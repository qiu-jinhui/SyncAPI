"""
模型仓储类
提供模型相关的数据访问操作
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from .base_repository import BaseRepository
from src.models.model import Model

class ModelRepository(BaseRepository[Model]):
    """模型仓储类"""
    
    def __init__(self, session: Session):
        super().__init__(Model, session)
    
    def find_by_name(self, model_name: str) -> Optional[Model]:
        """根据模型名称查找模型"""
        return self.find_one_by(model_name=model_name)
    
    def find_by_type(self, model_type: str) -> List[Model]:
        """根据模型类型查找模型"""
        return self.find_by(model_type=model_type)
    
    def find_by_provider(self, provider: str) -> List[Model]:
        """根据提供商查找模型"""
        return self.find_by(provider=provider)
    
    def find_by_input_type(self, model_input: str) -> List[Model]:
        """根据输入类型查找模型"""
        return self.find_by(model_input=model_input)
    
    def find_by_output_type(self, model_output: str) -> List[Model]:
        """根据输出类型查找模型"""
        return self.find_by(model_output=model_output)
    
    def search_models(self, search_term: str, limit: Optional[int] = None) -> List[Model]:
        """搜索模型"""
        query = self.session.query(self.model).filter(
            or_(
                self.model.model_name.ilike(f"%{search_term}%"),
                self.model.provider.ilike(f"%{search_term}%")
            )
        )
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_models_by_provider_and_type(self, provider: str, model_type: str) -> List[Model]:
        """根据提供商和类型获取模型"""
        return self.session.query(self.model).filter(
            and_(
                self.model.provider == provider,
                self.model.model_type == model_type
            )
        ).all()
    
    def get_models_with_deployments(self) -> List[Model]:
        """获取包含部署的模型"""
        return self.session.query(self.model).join(
            self.model.deployments
        ).distinct().all()
    
    def get_models_with_pricing(self) -> List[Model]:
        """获取包含定价的模型"""
        return self.session.query(self.model).join(
            self.model.pricing
        ).distinct().all()
    
    def get_model_stats(self) -> dict:
        """获取模型统计信息"""
        total_models = self.count()
        
        provider_stats = self.session.query(
            self.model.provider,
            func.count(self.model.id).label('count')
        ).group_by(self.model.provider).all()
        
        type_stats = self.session.query(
            self.model.model_type,
            func.count(self.model.id).label('count')
        ).group_by(self.model.model_type).all()
        
        return {
            'total_models': total_models,
            'provider_stats': {provider: count for provider, count in provider_stats},
            'type_stats': {model_type: count for model_type, count in type_stats}
        } 