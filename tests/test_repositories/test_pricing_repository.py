"""
定价仓储测试
"""

import pytest
from src.models.pricing import ModelPricing
from src.models.model import Model

class TestPricingRepository:
    """定价仓储测试类"""
    
    def test_find_by_model(self, pricing_repository, session):
        """测试根据模型查找定价"""
        # 创建模型和定价
        model = Model(model_name="Test Model", model_type="llm", provider="openai")
        session.add(model)
        session.flush()
        
        pricing = pricing_repository.create(
            model_id=model.id,
            input_price=0.001,
            output_price=0.002,
            currency="USD"
        )
        session.commit()
        
        # 查找
        results = pricing_repository.find_by_model(model.id)
        
        assert len(results) == 1
        assert results[0].model_id == model.id
    
    def test_find_by_currency(self, pricing_repository, session):
        """测试根据货币查找定价"""
        # 创建模型和定价
        model = Model(model_name="Test Model", model_type="llm", provider="openai")
        session.add(model)
        session.flush()
        
        pricing = pricing_repository.create(
            model_id=model.id,
            input_price=0.001,
            output_price=0.002,
            currency="USD"
        )
        session.commit()
        
        # 查找
        results = pricing_repository.find_by_currency("USD")
        
        assert len(results) == 1
        assert results[0].currency == "USD"
    
    def test_find_by_price_range(self, pricing_repository, session):
        """测试根据价格范围查找定价"""
        # 创建模型和定价
        model = Model(model_name="Test Model", model_type="llm", provider="openai")
        session.add(model)
        session.flush()
        
        pricing = pricing_repository.create(
            model_id=model.id,
            input_price=0.001,
            output_price=0.002,
            currency="USD"
        )
        session.commit()
        
        # 查找
        results = pricing_repository.find_by_price_range(0.0005, 0.003)
        
        assert len(results) == 1
        assert results[0].input_price == 0.001
    
    def test_find_by_provider(self, pricing_repository, session):
        """测试根据提供商查找定价"""
        # 创建模型和定价
        model1 = Model(model_name="OpenAI Model", model_type="llm", provider="openai")
        model2 = Model(model_name="Anthropic Model", model_type="llm", provider="anthropic")
        session.add_all([model1, model2])
        session.flush()
        
        pricing = pricing_repository.create(
            model_id=model1.id,
            input_price=0.001,
            output_price=0.002,
            currency="USD"
        )
        session.commit()
        
        # 查找
        results = pricing_repository.find_by_provider("openai")
        
        assert len(results) == 1
        assert results[0].model.provider == "openai"
    
    def test_get_pricing_stats(self, pricing_repository, session):
        """测试获取定价统计信息"""
        # 创建模型和定价
        model1 = Model(model_name="Model 1", model_type="llm", provider="openai")
        model2 = Model(model_name="Model 2", model_type="llm", provider="anthropic")
        session.add_all([model1, model2])
        session.flush()
        
        pricing_repository.create(
            model_id=model1.id,
            input_price=0.001,
            output_price=0.002,
            currency="USD"
        )
        pricing_repository.create(
            model_id=model2.id,
            input_price=0.002,
            output_price=0.004,
            currency="USD"
        )
        session.commit()
        
        # 获取统计信息
        stats = pricing_repository.get_pricing_stats()
        
        assert stats['total_pricing'] == 2
        assert stats['avg_input_price'] == 0.0015
        assert stats['avg_output_price'] == 0.003 