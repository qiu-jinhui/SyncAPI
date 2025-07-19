"""
项目模型
对应projects表
"""

from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from src.models.base import BaseModel

class Project(BaseModel):
    """项目模型"""
    
    __tablename__ = "projects"
    
    # 字段定义
    project_name = Column(String(255), nullable=False, index=True)
    project_code = Column(String(100), nullable=False, unique=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # 关系定义
    use_cases = relationship("UseCase", back_populates="project", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.project_name}', code='{self.project_code}')>"
    
    @property
    def name(self) -> str:
        """项目名称别名"""
        return self.project_name
    
    @property
    def code(self) -> str:
        """项目代码别名"""
        return self.project_code 