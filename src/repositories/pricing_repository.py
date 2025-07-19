"""
定价仓储类
提供定价相关的数据访问操作
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from .base_repository import BaseRepository
from src.models.pricing import ModelPricing

class PricingRepository(BaseRepository[ModelPricing]):
    """定价仓储类"""
    
    def __init__(self, session: Session):
        super().__init__(ModelPricing, session)
    
    def find_by_model_id(self, model_id: str) -> List[ModelPricing]:
        """根据模型ID查找定价"""
        return self.find_by(model_id=model_id)
    
    def find_by_currency(self, currency: str) -> List[ModelPricing]:
        """根据货币查找定价"""
        return self.find_by(currency=currency)
    
    def find_by_price_range(self, min_input_price: Optional[int] = None, max_input_price: Optional[int] = None) -> List[ModelPricing]:
        """根据价格范围查找定价"""
        query = self.session.query(self.model)
        
        if min_input_price is not None:
            query = query.filter(self.model.input_token_price_cpm >= min_input_price)
        
        if max_input_price is not None:
            query = query.filter(self.model.input_token_price_cpm <= max_input_price)
        
        return query.all()
    
    def get_pricing_by_provider(self, provider: str) -> List[ModelPricing]:
        """根据提供商获取定价"""
        return self.session.query(self.model).join(
            self.model.model
        ).filter(
            self.model.model.has(provider=provider)
        ).all()
    
    def get_average_pricing_by_currency(self) -> dict:
        """获取各货币的平均定价"""
        result = self.session.query(
            self.model.currency,
            func.avg(self.model.input_token_price_cpm).label('avg_input'),
            func.avg(self.model.output_token_price_cpm).label('avg_output')
        ).group_by(self.model.currency).all()
        
        return {
            currency: {
                'avg_input_price': float(avg_input) if avg_input else 0,
                'avg_output_price': float(avg_output) if avg_output else 0
            }
            for currency, avg_input, avg_output in result
        }
    
    def get_pricing_stats(self) -> dict:
        """获取定价统计信息"""
        total_pricing = self.count()
        
        currency_stats = self.session.query(
            self.model.currency,
            func.count(self.model.id).label('count'),
            func.avg(self.model.input_token_price_cpm).label('avg_input'),
            func.avg(self.model.output_token_price_cpm).label('avg_output')
        ).group_by(self.model.currency).all()
        
        return {
            'total_pricing': total_pricing,
            'currency_stats': {
                currency: {
                    'count': count,
                    'avg_input_price': float(avg_input) if avg_input else 0,
                    'avg_output_price': float(avg_output) if avg_output else 0
                }
                for currency, count, avg_input, avg_output in currency_stats
            }
        } 