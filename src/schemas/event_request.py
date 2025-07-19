"""
事件请求模式
定义Model Garden发送的CUD事件数据结构
"""

from datetime import datetime
from typing import Union, Optional
from pydantic import BaseModel, Field

from src.schemas.payloads import (
    ProjectPayload,
    UseCasePayload,
    UseCaseBudgetPayload,
    ModelPayload,
    ModelDeploymentPayload,
    ModelPricingPayload,
    SubscriptionPayload,
    ModelLimitPayload
)

class EventRequest(BaseModel):
    """事件请求模式"""
    
    event_type: str = Field(..., description="事件类型", enum=["CREATED", "UPDATED", "DELETED"])
    entity_type: str = Field(..., description="实体类型")
    entity_id: str = Field(..., description="实体ID")
    timestamp: datetime = Field(..., description="事件时间戳")
    version: Optional[str] = Field(None, description="事件版本")
    payload: Union[
        ProjectPayload,
        UseCasePayload,
        UseCaseBudgetPayload,
        ModelPayload,
        ModelDeploymentPayload,
        ModelPricingPayload,
        SubscriptionPayload,
        ModelLimitPayload
    ] = Field(..., description="事件负载数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "CREATED",
                "entity_type": "project",
                "entity_id": "proj-001",
                "timestamp": "2025-07-15T14:20:00Z",
                "version": "1.0",
                "payload": {
                    "id": "proj-001",
                    "project_name": "Credit AI",
                    "project_code": "CREDIT_AI",
                    "created_time": "2025-07-15T14:00:00Z",
                    "updated_time": "2025-07-15T14:00:00Z"
                }
            }
        } 