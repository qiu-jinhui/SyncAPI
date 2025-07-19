"""
事件API路由
处理Model Garden发送的CUD事件
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from src.schemas.event_request import EventRequest
from src.schemas.event_response import EventResponse
from src.services.event_service import EventService
from src.api.dependencies import get_event_service
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.post(
    "/api/v1/model-garden/events",
    response_model=EventResponse,
    summary="接收Model Garden的CUD事件",
    description="处理来自Model Garden的创建、更新、删除事件"
)
async def receive_event(
    event: EventRequest,
    event_service: EventService = Depends(get_event_service)
) -> EventResponse:
    """
    接收并处理来自Model Garden的CUD事件
    
    Args:
        event: 事件请求数据
        event_service: 事件服务实例
        
    Returns:
        EventResponse: 事件处理结果
        
    Raises:
        HTTPException: 当事件处理失败时
    """
    try:
        logger.info(f"接收到事件: {event.event_type} - {event.entity_type} - {event.entity_id}")
        
        # 处理事件
        result = await event_service.process_event(event)
        
        logger.info(f"事件处理成功: {event.entity_id}")
        return EventResponse(status="ok", message="Event processed successfully")
        
    except Exception as e:
        logger.error(f"事件处理失败: {event.entity_id}, 错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process event: {str(e)}"
        )

@router.get(
    "/api/v1/model-garden/health",
    summary="健康检查",
    description="检查API服务状态"
)
async def health_check() -> Dict[str, Any]:
    """
    健康检查端点
    
    Returns:
        Dict[str, Any]: 服务状态信息
    """
    return {
        "status": "healthy",
        "service": "synchronize-api",
        "version": "1.0.0"
    } 