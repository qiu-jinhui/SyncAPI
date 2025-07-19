"""
订阅仓储类
提供订阅相关的数据访问操作
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from .base_repository import BaseRepository
from src.models.subscription import Subscription

class SubscriptionRepository(BaseRepository[Subscription]):
    """订阅仓储类"""
    
    def __init__(self, session: Session):
        super().__init__(Subscription, session)
    
    def find_by_project_id(self, project_id: str) -> List[Subscription]:
        """根据项目ID查找订阅"""
        return self.find_by(project_id=project_id)
    
    def find_by_use_case_id(self, use_case_id: str) -> List[Subscription]:
        """根据用例ID查找订阅"""
        return self.find_by(use_case_id=use_case_id)
    
    def find_by_model_id(self, model_id: str) -> List[Subscription]:
        """根据模型ID查找订阅"""
        return self.find_by(model_id=model_id)
    
    def find_by_subscription_key(self, subscription_key: str) -> Optional[Subscription]:
        """根据订阅键查找订阅"""
        project_id, use_case_id, model_id = subscription_key.split(':', 2)
        return self.session.query(self.model).filter(
            and_(
                self.model.project_id == project_id,
                self.model.use_case_id == use_case_id,
                self.model.model_id == model_id
            )
        ).first()
    
    def find_by_project_and_use_case(self, project_id: str, use_case_id: str) -> List[Subscription]:
        """根据项目ID和用例ID查找订阅"""
        return self.session.query(self.model).filter(
            and_(
                self.model.project_id == project_id,
                self.model.use_case_id == use_case_id
            )
        ).all()
    
    def find_by_project_and_model(self, project_id: str, model_id: str) -> List[Subscription]:
        """根据项目ID和模型ID查找订阅"""
        return self.session.query(self.model).filter(
            and_(
                self.model.project_id == project_id,
                self.model.model_id == model_id
            )
        ).all()
    
    def get_subscriptions_by_provider(self, provider: str) -> List[Subscription]:
        """根据提供商获取订阅"""
        return self.session.query(self.model).join(
            self.model.model
        ).filter(
            self.model.model.has(provider=provider)
        ).all()
    
    def get_subscription_stats(self, project_id: Optional[str] = None) -> dict:
        """获取订阅统计信息"""
        query = self.session.query(self.model)
        if project_id:
            query = query.filter(self.model.project_id == project_id)
        
        total_subscriptions = query.count()
        
        # 按模型统计
        model_stats = query.join(
            self.model.model
        ).with_entities(
            self.model.model_id,
            func.count(self.model.id).label('count')
        ).group_by(self.model.model_id).all()
        
        return {
            'total_subscriptions': total_subscriptions,
            'model_stats': {model_id: count for model_id, count in model_stats}
        } 