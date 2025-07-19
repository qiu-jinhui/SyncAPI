"""
限制仓储类
提供限制相关的数据访问操作
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from .base_repository import BaseRepository
from src.models.limit import ModelLimit, ModelLimitUsage

class LimitRepository(BaseRepository[ModelLimit]):
    """限制仓储类"""
    
    def __init__(self, session: Session):
        super().__init__(ModelLimit, session)
    
    def find_by_subscription_id(self, subscription_id: str) -> List[ModelLimit]:
        """根据订阅ID查找限制"""
        return self.find_by(subscription_id=subscription_id)
    
    def find_by_type(self, limit_type: str) -> List[ModelLimit]:
        """根据限制类型查找限制"""
        return self.find_by(limit_type=limit_type)
    
    def find_by_scope(self, scope: str) -> List[ModelLimit]:
        """根据范围查找限制"""
        return self.find_by(scope=scope)
    
    def find_by_subscription_and_type(self, subscription_id: str, limit_type: str) -> Optional[ModelLimit]:
        """根据订阅ID和类型查找限制"""
        return self.session.query(self.model).filter(
            and_(
                self.model.subscription_id == subscription_id,
                self.model.limit_type == limit_type
            )
        ).first()
    
    def get_limits_by_project(self, project_id: str) -> List[ModelLimit]:
        """根据项目ID获取限制"""
        return self.session.query(self.model).join(
            self.model.subscription
        ).filter(
            self.model.subscription.has(project_id=project_id)
        ).all()
    
    def get_limit_stats(self) -> dict:
        """获取限制统计信息"""
        total_limits = self.count()
        
        type_stats = self.session.query(
            self.model.limit_type,
            func.count(self.model.id).label('count')
        ).group_by(self.model.limit_type).all()
        
        scope_stats = self.session.query(
            self.model.scope,
            func.count(self.model.id).label('count')
        ).group_by(self.model.scope).all()
        
        return {
            'total_limits': total_limits,
            'type_stats': {limit_type: count for limit_type, count in type_stats},
            'scope_stats': {scope: count for scope, count in scope_stats}
        }

class LimitUsageRepository(BaseRepository[ModelLimitUsage]):
    """限制使用仓储类"""
    
    def __init__(self, session: Session):
        super().__init__(ModelLimitUsage, session)
    
    def find_by_limit_id(self, limit_id: str) -> List[ModelLimitUsage]:
        """根据限制ID查找使用记录"""
        return self.find_by(limit_id=limit_id)
    
    def find_by_scope(self, scope: str) -> List[ModelLimitUsage]:
        """根据范围查找使用记录"""
        return self.find_by(scope=scope)
    
    def find_by_period(self, usage_period: datetime) -> List[ModelLimitUsage]:
        """根据使用期间查找使用记录"""
        return self.find_by(usage_period=usage_period)
    
    def find_by_request_id(self, request_id: str) -> Optional[ModelLimitUsage]:
        """根据请求ID查找使用记录"""
        return self.find_one_by(request_id=request_id)
    
    def find_by_caller(self, called_by: str) -> List[ModelLimitUsage]:
        """根据调用者查找使用记录"""
        return self.find_by(called_by=called_by)
    
    def get_usage_by_date_range(self, start_date: datetime, end_date: datetime) -> List[ModelLimitUsage]:
        """根据日期范围获取使用记录"""
        return self.session.query(self.model).filter(
            and_(
                self.model.usage_period >= start_date,
                self.model.usage_period <= end_date
            )
        ).all()
    
    def get_usage_by_limit_and_period(self, limit_id: str, usage_period: datetime) -> List[ModelLimitUsage]:
        """根据限制ID和期间获取使用记录"""
        return self.session.query(self.model).filter(
            and_(
                self.model.limit_id == limit_id,
                self.model.usage_period == usage_period
            )
        ).all()
    
    def get_total_usage_by_limit(self, limit_id: str) -> int:
        """获取限制的总使用量"""
        result = self.session.query(
            func.sum(self.model.value)
        ).filter(
            self.model.limit_id == limit_id
        ).scalar()
        
        return result or 0
    
    def get_usage_stats(self, limit_id: Optional[str] = None) -> dict:
        """获取使用统计信息"""
        query = self.session.query(self.model)
        if limit_id:
            query = query.filter(self.model.limit_id == limit_id)
        
        total_usage = query.count()
        total_value = query.with_entities(
            func.sum(self.model.value)
        ).scalar() or 0
        
        return {
            'total_usage_records': total_usage,
            'total_usage_value': total_value
        } 