"""
预算相关模型
对应use_case_budget和use_case_budget_usage表
"""

from datetime import date
from sqlalchemy import Column, String, BigInteger, ForeignKey, Date, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.models.base import BaseModel

class UseCaseBudget(BaseModel):
    """用例预算模型"""
    
    __tablename__ = "use_case_budget"
    
    # 字段定义
    use_case_id = Column(UUID(as_uuid=True), ForeignKey("use_cases.id"), nullable=False, index=True)
    budget_cents = Column(BigInteger, nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    
    # 关系定义
    use_case = relationship("UseCase", back_populates="budget")
    
    def __repr__(self) -> str:
        return f"<UseCaseBudget(id={self.id}, use_case_id={self.use_case_id}, budget_cents={self.budget_cents})>"
    
    @property
    def budget_amount(self) -> float:
        """预算金额（元）"""
        return self.budget_cents / 100.0
    
    @budget_amount.setter
    def budget_amount(self, amount: float) -> None:
        """设置预算金额（元）"""
        self.budget_cents = int(amount * 100)

class UseCaseBudgetUsage(BaseModel):
    """用例预算使用模型"""
    
    __tablename__ = "use_case_budget_usage"
    
    # 字段定义
    use_case_id = Column(UUID(as_uuid=True), ForeignKey("use_cases.id"), nullable=False, index=True)
    usage_period = Column(Date, nullable=False)
    scope = Column(String(50), nullable=False)  # daily, monthly, yearly
    used_cents = Column(BigInteger, default=0, nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    
    # 唯一约束
    __table_args__ = (
        UniqueConstraint('use_case_id', 'usage_period', 'scope', name='uq_use_case_budget_usage'),
    )
    
    # 关系定义
    use_case = relationship("UseCase", back_populates="budget_usage")
    
    def __repr__(self) -> str:
        return f"<UseCaseBudgetUsage(id={self.id}, use_case_id={self.use_case_id}, period={self.usage_period}, scope={self.scope})>"
    
    @property
    def used_amount(self) -> float:
        """已使用金额（元）"""
        return self.used_cents / 100.0
    
    @used_amount.setter
    def used_amount(self, amount: float) -> None:
        """设置已使用金额（元）"""
        self.used_cents = int(amount * 100)
    
    @property
    def usage_period_date(self) -> date:
        """使用期间日期"""
        return self.usage_period 