"""
订阅模型
对应subscriptions表
"""

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.models.base import BaseModel

class Subscription(BaseModel):
    """订阅模型"""
    
    __tablename__ = "subscriptions"
    
    # 字段定义
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    use_case_id = Column(UUID(as_uuid=True), ForeignKey("use_cases.id"), nullable=False, index=True)
    model_id = Column(UUID(as_uuid=True), ForeignKey("models.id"), nullable=False, index=True)
    
    # 关系定义
    project = relationship("Project", back_populates="subscriptions")
    use_case = relationship("UseCase", back_populates="subscriptions")
    model = relationship("Model", back_populates="subscriptions")
    limits = relationship("ModelLimit", back_populates="subscription", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, project_id={self.project_id}, use_case_id={self.use_case_id}, model_id={self.model_id})>"
    
    @property
    def subscription_key(self) -> str:
        """订阅键（用于缓存）"""
        return f"{self.project_id}:{self.use_case_id}:{self.model_id}" 