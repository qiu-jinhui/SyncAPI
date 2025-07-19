"""
用例模型
对应use_cases表
"""

from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.models.base import BaseModel

class UseCase(BaseModel):
    """用例模型"""
    
    __tablename__ = "use_cases"
    
    # 字段定义
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    use_case_name = Column(String(255), nullable=False, index=True)
    ad_group = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # 关系定义
    project = relationship("Project", back_populates="use_cases")
    budget = relationship("UseCaseBudget", back_populates="use_case", uselist=False, cascade="all, delete-orphan")
    budget_usage = relationship("UseCaseBudgetUsage", back_populates="use_case", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="use_case", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<UseCase(id={self.id}, name='{self.use_case_name}', project_id={self.project_id})>"
    
    @property
    def name(self) -> str:
        """用例名称别名"""
        return self.use_case_name
    
    @property
    def active(self) -> bool:
        """是否激活别名"""
        return self.is_active 