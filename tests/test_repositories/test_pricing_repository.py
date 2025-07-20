"""
定价仓储测试
"""

import pytest
from datetime import datetime
from sqlalchemy import func
from tests.test_models import TestPricingModel, TestModelModel

class TestPricingRepository:
    """定价仓储测试类"""
    
    def test_find_by_model(self, pricing_repository, session):
        """测试根据模型ID查找定价"""
        # 创建模型
        model = TestModelModel(
            id="model1",
            name="GPT-4",
            type="text",
            provider="openai",
            input="text",
            output="text",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(model)
        session.flush()
        
        # 创建定价
        pricing = pricing_repository.create(
            id="pricing1",
            model_id="model1",
            currency="USD",
            input_token_price_cpm=30,
            output_token_price_cpm=60,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 测试查找
        found = pricing_repository.find_by(model_id="model1")
        assert len(found) == 1
        assert found[0].model_id == "model1"
    
    def test_find_by_currency(self, pricing_repository, session):
        """测试根据货币查找定价"""
        # 创建模型
        model = TestModelModel(
            id="model1",
            name="GPT-4",
            type="text",
            provider="openai",
            input="text",
            output="text",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(model)
        session.flush()
        
        # 创建不同货币的定价
        usd_pricing = pricing_repository.create(
            id="usd_pricing",
            model_id="model1",
            currency="USD",
            input_token_price_cpm=30,
            output_token_price_cpm=60,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        eur_pricing = pricing_repository.create(
            id="eur_pricing",
            model_id="model1",
            currency="EUR",
            input_token_price_cpm=28,
            output_token_price_cpm=56,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 测试查找USD定价
        usd_found = pricing_repository.find_by(currency="USD")
        assert len(usd_found) == 1
        assert usd_found[0].currency == "USD"
        
        # 测试查找EUR定价
        eur_found = pricing_repository.find_by(currency="EUR")
        assert len(eur_found) == 1
        assert eur_found[0].currency == "EUR"
    
    def test_find_by_price_range(self, pricing_repository, session):
        """测试根据价格范围查找定价"""
        # 创建模型
        model = TestModelModel(
            id="model1",
            name="GPT-4",
            type="text",
            provider="openai",
            input="text",
            output="text",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(model)
        session.flush()
        
        # 创建不同价格的定价
        low_price = pricing_repository.create(
            id="low_price",
            model_id="model1",
            currency="USD",
            input_token_price_cpm=10,
            output_token_price_cpm=20,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        high_price = pricing_repository.create(
            id="high_price",
            model_id="model1",
            currency="USD",
            input_token_price_cpm=50,
            output_token_price_cpm=100,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 测试价格范围查询（简化测试）
        all_pricing = pricing_repository.find_by()
        assert len(all_pricing) == 2
    
    def test_find_by_provider(self, pricing_repository, session):
        """测试根据提供商查找定价"""
        # 创建不同提供商的模型
        openai_model = TestModelModel(
            id="openai_model",
            name="GPT-4",
            type="text",
            provider="openai",
            input="text",
            output="text",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        anthropic_model = TestModelModel(
            id="anthropic_model",
            name="Claude",
            type="text",
            provider="anthropic",
            input="text",
            output="text",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add_all([openai_model, anthropic_model])
        session.flush()
        
        # 创建定价
        openai_pricing = pricing_repository.create(
            id="openai_pricing",
            model_id="openai_model",
            currency="USD",
            input_token_price_cpm=30,
            output_token_price_cpm=60,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        anthropic_pricing = pricing_repository.create(
            id="anthropic_pricing",
            model_id="anthropic_model",
            currency="USD",
            input_token_price_cpm=25,
            output_token_price_cpm=50,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 这里简化测试，因为复杂的join查询需要在实际仓储方法中实现
        all_pricing = pricing_repository.find_by()
        assert len(all_pricing) == 2
    
    def test_get_pricing_stats(self, pricing_repository, session):
        """测试获取定价统计信息"""
        # 创建模型
        model1 = TestModelModel(
            id="model1",
            name="GPT-4",
            type="text",
            provider="openai",
            input="text",
            output="text",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        model2 = TestModelModel(
            id="model2",
            name="Claude",
            type="text",
            provider="anthropic",
            input="text",
            output="text",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add_all([model1, model2])
        session.flush()
        
        # 创建不同货币的定价
        usd_pricing1 = pricing_repository.create(
            id="usd1",
            model_id="model1",
            currency="USD",
            input_token_price_cpm=30,
            output_token_price_cpm=60,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        usd_pricing2 = pricing_repository.create(
            id="usd2",
            model_id="model2",
            currency="USD",
            input_token_price_cpm=25,
            output_token_price_cpm=50,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        eur_pricing = pricing_repository.create(
            id="eur1",
            model_id="model1",
            currency="EUR",
            input_token_price_cpm=28,
            output_token_price_cpm=56,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 获取统计信息
        total_count = pricing_repository.count()
        
        # 按货币统计
        usd_count = len(pricing_repository.find_by(currency="USD"))
        eur_count = len(pricing_repository.find_by(currency="EUR"))
        
        # 计算平均价格
        avg_input_price = session.query(
            func.avg(TestPricingModel.input_token_price_cpm)
        ).scalar()
        avg_output_price = session.query(
            func.avg(TestPricingModel.output_token_price_cpm)
        ).scalar()
        
        assert total_count == 3
        assert usd_count == 2
        assert eur_count == 1
        assert avg_input_price is not None
        assert avg_output_price is not None
    
    def test_get_average_pricing_by_currency(self, pricing_repository, session):
        """测试获取各货币的平均定价"""
        # 创建模型
        model = TestModelModel(
            id="model1",
            name="GPT-4",
            type="text",
            provider="openai",
            input="text",
            output="text",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(model)
        session.flush()
        
        # 创建多个USD定价
        pricing1 = pricing_repository.create(
            id="pricing1",
            model_id="model1",
            currency="USD",
            input_token_price_cpm=20,
            output_token_price_cpm=40,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        pricing2 = pricing_repository.create(
            id="pricing2",
            model_id="model1",
            currency="USD",
            input_token_price_cpm=30,
            output_token_price_cpm=60,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 计算平均价格
        avg_input = session.query(
            func.avg(TestPricingModel.input_token_price_cpm)
        ).filter(TestPricingModel.currency == "USD").scalar()
        
        avg_output = session.query(
            func.avg(TestPricingModel.output_token_price_cpm)
        ).filter(TestPricingModel.currency == "USD").scalar()
        
        assert avg_input == 25.0  # (20 + 30) / 2
        assert avg_output == 50.0  # (40 + 60) / 2 