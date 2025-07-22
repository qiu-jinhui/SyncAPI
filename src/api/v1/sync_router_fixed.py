"""
同步API路由 - 修复版本
正确使用SyncService进行完整的同步流程
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
from datetime import datetime

from src.schemas.sync_request import SyncRequest
from src.schemas.sync_response import SyncResponse
from src.services.sync_service import SyncService
from src.api.dependencies import get_sync_service, get_db_session
from src.utils.logger import get_logger
from sqlalchemy.orm import Session

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/api/v1/model-garden/sync/all",
    response_model=SyncResponse,
    summary="全量同步Model Garden配置",
    description="从Model Garden同步所有配置数据到本地数据库，并发布同步事件"
)
async def sync_all(
    request: Optional[SyncRequest] = Body(None),
    sync_service: SyncService = Depends(get_sync_service),
    db_session: Session = Depends(get_db_session)
) -> SyncResponse:
    """
    执行完整的同步操作
    
    这是正确的实现：
    1. 调用Model Garden API获取数据
    2. 将数据同步到本地数据库
    3. 发布Redis同步事件
    4. 返回同步结果统计
    
    Args:
        request: 同步请求参数（可选）
        sync_service: 同步服务实例（依赖注入）
        db_session: 数据库会话（依赖注入）
        
    Returns:
        SyncResponse: 同步结果和统计信息
        
    Raises:
        HTTPException: 当同步失败时
    """
    try:
        # 提取updated_since参数
        updated_since = None
        if request and request.updated_since:
            updated_since = request.updated_since
            
        logger.info(
            "开始执行全量同步",
            updated_since=updated_since.isoformat() if updated_since else None
        )
        
        # ✅ 正确做法：调用SyncService执行完整同步流程
        # 这会包括：API调用 + 数据库同步 + Redis事件发布
        sync_result = await sync_service.sync_all(
            updated_since=updated_since,
            session=db_session
        )
        
        # 构建API响应（转换为SyncResponse格式）
        details = sync_result.get("details", {})
        response = SyncResponse(
            projects=details.get("projects", {}).get("data", []),
            use_cases=details.get("use_cases", {}).get("data", []),
            budgets=details.get("budgets", {}).get("data", []),
            models=details.get("models", {}).get("data", []),
            model_deployments=details.get("deployments", {}).get("data", []),
            pricing=details.get("pricing", {}).get("data", []),
            use_case_llm_models=details.get("subscriptions", {}).get("data", []),
            limits=details.get("limits", {}).get("data", [])
        )
        
        # 记录同步统计
        totals = sync_result.get("totals", {})
        logger.info(
            "同步完成",
            duration_seconds=sync_result.get("duration_seconds"),
            created=totals.get("created", 0),
            updated=totals.get("updated", 0), 
            errors=totals.get("errors", 0),
            projects_count=len(response.projects),
            use_cases_count=len(response.use_cases),
            budgets_count=len(response.budgets),
            models_count=len(response.models),
            deployments_count=len(response.model_deployments),
            pricing_count=len(response.pricing),
            subscriptions_count=len(response.use_case_llm_models),
            limits_count=len(response.limits)
        )
        
        return response
        
    except Exception as e:
        logger.error(f"全量同步失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"同步失败: {str(e)}"
        )


@router.get(
    "/api/v1/model-garden/sync/status",
    summary="获取同步状态",
    description="获取最近的同步任务状态信息"
)
async def get_sync_status(
    sync_service: SyncService = Depends(get_sync_service)
) -> dict:
    """
    获取同步状态信息
    
    Args:
        sync_service: 同步服务实例
        
    Returns:
        dict: 同步状态信息
    """
    try:
        # 获取最近的同步结果（从Redis缓存）
        latest_sync = await sync_service.redis_service.get_latest_sync_result()
        
        # 检查是否有正在进行的同步
        sync_in_progress = await sync_service.redis_service.is_sync_in_progress()
        
        status_info = {
            "status": "healthy",
            "service": "synchronize-api",
            "version": "1.0.0",
            "last_sync": latest_sync.get("end_time") if latest_sync else None,
            "sync_in_progress": sync_in_progress,
            "last_sync_totals": latest_sync.get("totals") if latest_sync else None
        }
        
        return status_info
        
    except Exception as e:
        logger.error(f"获取同步状态失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取状态失败: {str(e)}"
        ) 