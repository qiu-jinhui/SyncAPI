"""
模型定价模型
对应llm_model_pricing表
"""

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.models.base import BaseModel

class ModelPricing(BaseModel):
    """模型定价模型"""
    
    __tablename__ = "llm_model_pricing"
    
    # 字段定义
    model_id = Column(UUID(as_uuid=True), ForeignKey("models.id"), nullable=False, index=True)
    input_token_price_cpm = Column(Integer, nullable=False)  # 每千个输入令牌价格（分）
    output_token_price_cpm = Column(Integer, nullable=False)  # 每千个输出令牌价格（分）
    currency = Column(String(10), default="USD", nullable=False)
    
    # 关系定义
    model = relationship("Model", back_populates="pricing")
    
    def __repr__(self) -> str:
        return f"<ModelPricing(id={self.id}, model_id={self.model_id}, input_cpm={self.input_token_price_cpm}, output_cpm={self.output_token_price_cpm})>"
    
    @property
    def input_price_per_token(self) -> float:
        """每个输入令牌价格（元）"""
        return self.input_token_price_cpm / 1000.0 / 100.0
    
    @property
    def output_price_per_token(self) -> float:
        """每个输出令牌价格（元）"""
        return self.output_token_price_cpm / 1000.0 / 100.0
    
    @property
    def input_price_per_1k_tokens(self) -> float:
        """每千个输入令牌价格（元）"""
        return self.input_token_price_cpm / 100.0
    
    @property
    def output_price_per_1k_tokens(self) -> float:
        """每千个输出令牌价格（元）"""
        return self.output_token_price_cpm / 100.0
    
    def calculate_input_cost(self, token_count: int) -> float:
        """计算输入令牌成本"""
        return token_count * self.input_price_per_token
    
    def calculate_output_cost(self, token_count: int) -> float:
        """计算输出令牌成本"""
        return token_count * self.output_price_per_token
    
    def calculate_total_cost(self, input_tokens: int, output_tokens: int) -> float:
        """计算总成本"""
        return self.calculate_input_cost(input_tokens) + self.calculate_output_cost(output_tokens) 