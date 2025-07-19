"""
部署仓储类
提供部署相关的数据访问操作
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from .base_repository import BaseRepository
from src.models.deployment import ModelDeployment

class DeploymentRepository(BaseRepository[ModelDeployment]):
    """部署仓储类"""
    
    def __init__(self, session: Session):
        super().__init__(ModelDeployment, session)
    
    def find_by_model_id(self, model_id: str) -> List[ModelDeployment]:
        """根据模型ID查找部署"""
        return self.find_by(model_id=model_id)
    
    def find_by_name(self, deployment_name: str) -> Optional[ModelDeployment]:
        """根据部署名称查找部署"""
        return self.find_one_by(deployment_name=deployment_name)
    
    def find_by_region(self, region: str) -> List[ModelDeployment]:
        """根据区域查找部署"""
        return self.find_by(region=region)
    
    def find_default_deployment(self, model_id: str) -> Optional[ModelDeployment]:
        """查找模型的默认部署"""
        return self.session.query(self.model).filter(
            and_(
                self.model.model_id == model_id,
                self.model.is_default == True
            )
        ).first()
    
    def get_deployments_by_provider(self, provider: str) -> List[ModelDeployment]:
        """根据提供商获取部署"""
        return self.session.query(self.model).join(
            self.model.model
        ).filter(
            self.model.model.has(provider=provider)
        ).all()
    
    def get_active_deployments(self) -> List[ModelDeployment]:
        """获取所有活跃部署"""
        return self.session.query(self.model).join(
            self.model.model
        ).filter(
            self.model.model.has(is_active=True)
        ).all()
    
    def search_deployments(self, search_term: str, limit: Optional[int] = None) -> List[ModelDeployment]:
        """搜索部署"""
        query = self.session.query(self.model).filter(
            or_(
                self.model.deployment_name.ilike(f"%{search_term}%"),
                self.model.endpoint.ilike(f"%{search_term}%")
            )
        )
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def update_default_deployment(self, model_id: str, deployment_id: str) -> bool:
        """更新默认部署"""
        # 先取消所有默认部署
        self.session.query(self.model).filter(
            and_(
                self.model.model_id == model_id,
                self.model.is_default == True
            )
        ).update({'is_default': False})
        
        # 设置新的默认部署
        result = self.session.query(self.model).filter(
            self.model.id == deployment_id
        ).update({'is_default': True})
        
        self.session.flush()
        return result > 0 