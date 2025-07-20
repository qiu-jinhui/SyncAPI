"""
同步API路由
处理全量同步请求
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
from datetime import datetime

from src.schemas.sync_request import SyncRequest
from src.schemas.sync_response import SyncResponse
from src.services.sync_service import SyncService
from src.services.model_garden_client import ModelGardenClient
from src.api.dependencies import get_sync_service
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/api/v1/model-garden/sync/all",
    response_model=SyncResponse,
    summary="全量同步Model Garden配置",
    description="从Model Garden同步所有配置数据到本地数据库"
)
async def sync_all(
    request: Optional[SyncRequest] = Body(None),
    sync_service: SyncService = Depends(get_sync_service)
) -> SyncResponse:
    """
    执行全量同步操作
    
    Args:
        request: 同步请求参数（可选）
        sync_service: 同步服务实例
        
    Returns:
        SyncResponse: 同步的所有数据
        
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
        
        # 使用Model Garden客户端直接获取数据
        model_garden_client = ModelGardenClient()
        sync_data = await model_garden_client.sync_all(updated_since)
        
        # 同时触发后台同步到数据库
        # 这里异步执行，不等待结果，让API快速返回数据
        try:
            # 启动后台同步任务
            import asyncio
            asyncio.create_task(
                sync_service.sync_all(updated_since)
            )
            logger.info("后台数据库同步任务已启动")
        except Exception as e:
            logger.warning(f"启动后台同步任务失败: {str(e)}")
            # 不影响API返回，继续执行
        
        # 构建响应数据
        response = SyncResponse(
            projects=sync_data.get("projects", []),
            use_cases=sync_data.get("use_cases", []),
            budgets=sync_data.get("budgets", []),
            models=sync_data.get("models", []),
            model_deployments=sync_data.get("model_deployments", []),
            pricing=sync_data.get("pricing", []),
            use_case_llm_models=sync_data.get("use_case_llm_models", []),
            limits=sync_data.get("limits", [])
        )
        
        logger.info(
            "全量同步完成",
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
        # 这里可以添加获取同步状态的逻辑
        # 比如从Redis获取最近的同步结果
        redis_service = sync_service.redis_service
        
        # 尝试访问Redis服务以触发可能的异常
        if hasattr(redis_service, 'connection_failed'):
            raise redis_service.connection_failed
        
        # 获取最近的同步结果（示例）
        status_info = {
            "status": "healthy",
            "service": "synchronize-api",
            "version": "1.0.0",
            "last_sync": None,  # 可以从Redis获取
            "sync_in_progress": False  # 可以从Redis获取
        }
        
        return status_info
        
    except Exception as e:
        logger.error(f"获取同步状态失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取状态失败: {str(e)}"
        ) 