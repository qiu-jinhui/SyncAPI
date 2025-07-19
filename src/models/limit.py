"""
模型限制相关模型
对应llm_model_limits和llm_model_limits_usage表
"""

from datetime import datetime
from sqlalchemy import Column, String, BigInteger, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.models.base import BaseModel

class ModelLimit(BaseModel):
    """模型限制模型"""
    
    __tablename__ = "llm_model_limits"
    
    # 字段定义
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=False, index=True)
    limit_type = Column(String(100), nullable=False, index=True)  # input_token_limit, output_token_limit, request_limit等
    scope = Column(String(50), nullable=False, index=True)  # daily, monthly, yearly
    limit_value = Column(BigInteger, nullable=False)
    
    # 关系定义
    subscription = relationship("Subscription", back_populates="limits")
    usage = relationship("ModelLimitUsage", back_populates="limit", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<ModelLimit(id={self.id}, subscription_id={self.subscription_id}, type='{self.limit_type}', scope='{self.scope}')>"
    
    @property
    def type(self) -> str:
        """限制类型别名"""
        return self.limit_type
    
    @property
    def value(self) -> int:
        """限制值别名"""
        return self.limit_value

class ModelLimitUsage(BaseModel):
    """模型限制使用模型"""
    
    __tablename__ = "llm_model_limits_usage"
    
    # 字段定义
    limit_id = Column(UUID(as_uuid=True), ForeignKey("llm_model_limits.id"), nullable=False, index=True)
    scope = Column(String(50), nullable=False, index=True)  # daily, monthly, yearly
    usage_period = Column(DateTime, nullable=False, index=True)
    value = Column(BigInteger, default=0, nullable=False)
    request_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    called_by = Column(String(255), nullable=True)
    
    # 关系定义
    limit = relationship("ModelLimit", back_populates="usage")
    
    def __repr__(self) -> str:
        return f"<ModelLimitUsage(id={self.id}, limit_id={self.limit_id}, scope='{self.scope}', period={self.usage_period})>"
    
    @property
    def usage_value(self) -> int:
        """使用值别名"""
        return self.value
    
    @property
    def period(self) -> datetime:
        """使用期间别名"""
        return self.usage_period
    
    @property
    def caller(self) -> str:
        """调用者别名"""
        return self.called_by or "" 