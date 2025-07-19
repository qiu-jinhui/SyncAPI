"""
事件响应模式
定义事件处理的响应数据结构
"""

from pydantic import BaseModel, Field

class EventResponse(BaseModel):
    """事件响应模式"""
    
    status: str = Field(..., description="处理状态")
    message: str = Field(..., description="响应消息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok",
                "message": "Event processed successfully"
            }
        } 