"""
预算仓储类
提供预算相关的数据访问操作
"""

from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from .base_repository import BaseRepository
from src.models.budget import UseCaseBudget, UseCaseBudgetUsage

class BudgetRepository(BaseRepository[UseCaseBudget]):
    """预算仓储类"""
    
    def __init__(self, session: Session):
        super().__init__(UseCaseBudget, session)
    
    def find_by_use_case_id(self, use_case_id: str) -> List[UseCaseBudget]:
        """根据用例ID查找预算"""
        return self.find_by(use_case_id=use_case_id)
    
    def find_by_currency(self, currency: str) -> List[UseCaseBudget]:
        """根据货币查找预算"""
        return self.find_by(currency=currency)
    
    def get_budgets_by_project(self, project_id: str) -> List[UseCaseBudget]:
        """根据项目ID获取预算"""
        return self.session.query(self.model).join(
            self.model.use_case
        ).filter(
            self.model.use_case.has(project_id=project_id)
        ).all()
    
    def find_by_date_range(self, start_date: date, end_date: date) -> List[UseCaseBudget]:
        """根据日期范围查找预算"""
        return self.session.query(self.model).filter(
            and_(
                self.model.start_date >= start_date,
                self.model.end_date <= end_date
            )
        ).all()

class BudgetUsageRepository(BaseRepository[UseCaseBudgetUsage]):
    """预算使用仓储类"""
    
    def __init__(self, session: Session):
        super().__init__(UseCaseBudgetUsage, session)
    
    def find_by_use_case_id(self, use_case_id: str) -> List[UseCaseBudgetUsage]:
        """根据用例ID查找预算使用记录"""
        return self.find_by(use_case_id=use_case_id)
    
    def find_by_period(self, usage_period: date) -> List[UseCaseBudgetUsage]:
        """根据使用期间查找预算使用记录"""
        return self.find_by(usage_period=usage_period)
    
    def get_usage_by_date_range(self, start_date: date, end_date: date) -> List[UseCaseBudgetUsage]:
        """根据日期范围获取使用记录"""
        return self.session.query(self.model).filter(
            and_(
                self.model.usage_period >= start_date,
                self.model.usage_period <= end_date
            )
        ).all()
    
    def get_usage_stats(self, use_case_id: Optional[str] = None) -> dict:
        """获取预算使用统计信息"""
        query = self.session.query(self.model)
        if use_case_id:
            query = query.filter(self.model.use_case_id == use_case_id)
        
        total_usage = query.count()
        total_amount = query.with_entities(
            func.sum(self.model.amount)
        ).scalar() or 0
        
        return {
            'total_usage_records': total_usage,
            'total_amount_used': float(total_amount)
        } 