"""
同步API请求数据模式
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class SyncRequest(BaseModel):
    """
    全量同步请求模式
    """
    updated_since: Optional[datetime] = Field(
        None,
        description="增量同步起始时间，如果不提供则进行全量同步",
        example="2025-07-01T00:00:00Z"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "updated_since": "2025-07-01T00:00:00Z"
            }
        } 