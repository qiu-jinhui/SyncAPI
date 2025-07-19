"""
模型部署模型
对应model_deployments表
"""

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.models.base import BaseModel

class ModelDeployment(BaseModel):
    """模型部署模型"""
    
    __tablename__ = "model_deployments"
    
    # 字段定义
    model_id = Column(UUID(as_uuid=True), ForeignKey("models.id"), nullable=False, index=True)
    deployment_name = Column(String(255), nullable=False, index=True)
    endpoint = Column(Text, nullable=False)
    auth_secret_manager_path = Column(Text, nullable=True)
    region = Column(String(100), nullable=True, index=True)
    request_per_min = Column(Integer, nullable=True)
    token_per_min = Column(Integer, nullable=True)
    is_default = Column(Boolean, default=False, nullable=False, index=True)
    
    # 唯一约束
    __table_args__ = (
        UniqueConstraint('model_id', 'deployment_name', name='uq_model_deployment'),
    )
    
    # 关系定义
    model = relationship("Model", back_populates="deployments")
    
    def __repr__(self) -> str:
        return f"<ModelDeployment(id={self.id}, name='{self.deployment_name}', model_id={self.model_id})>"
    
    @property
    def name(self) -> str:
        """部署名称别名"""
        return self.deployment_name
    
    @property
    def default(self) -> bool:
        """是否默认别名"""
        return self.is_default
    
    @property
    def auth_path(self) -> str:
        """认证路径别名"""
        return self.auth_secret_manager_path or ""
    
    @property
    def rpm(self) -> int:
        """每分钟请求数别名"""
        return self.request_per_min or 0
    
    @property
    def tpm(self) -> int:
        """每分钟令牌数别名"""
        return self.token_per_min or 0 