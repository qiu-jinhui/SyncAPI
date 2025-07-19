"""
模型定义
对应models表
"""

from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from src.models.base import BaseModel

class Model(BaseModel):
    """模型定义"""
    
    __tablename__ = "models"
    
    # 字段定义
    model_name = Column(String(255), nullable=False, index=True)
    model_type = Column(String(100), nullable=False, index=True)  # chat, completion, embedding等
    provider = Column(String(100), nullable=True, index=True)  # openai, anthropic, google等
    model_input = Column(String(100), nullable=True)  # text, image, audio等
    model_output = Column(String(100), nullable=True)  # text, image, audio等
    max_content_length = Column(Integer, nullable=True)
    
    # 关系定义
    deployments = relationship("ModelDeployment", back_populates="model", cascade="all, delete-orphan")
    pricing = relationship("ModelPricing", back_populates="model", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="model", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Model(id={self.id}, name='{self.model_name}', type='{self.model_type}', provider='{self.provider}')>"
    
    @property
    def name(self) -> str:
        """模型名称别名"""
        return self.model_name
    
    @property
    def type(self) -> str:
        """模型类型别名"""
        return self.model_type
    
    @property
    def max_length(self) -> int:
        """最大内容长度别名"""
        return self.max_content_length or 0 