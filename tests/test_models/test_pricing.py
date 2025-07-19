"""
定价模型测试
"""

import pytest
from src.models.pricing import ModelPricing

class TestModelPricing:
    """定价模型测试类"""
    
    def test_pricing_creation(self):
        """测试定价创建"""
        pricing = ModelPricing(
            model_id="123e4567-e89b-12d3-a456-426614174000",
            input_token_price_cpm=15,  # 15分/千个令牌
            output_token_price_cpm=30,  # 30分/千个令牌
            currency="USD"
        )
        
        assert pricing.model_id == "123e4567-e89b-12d3-a456-426614174000"
        assert pricing.input_token_price_cpm == 15
        assert pricing.output_token_price_cpm == 30
        assert pricing.currency == "USD"
    
    def test_pricing_repr(self):
        """测试定价字符串表示"""
        pricing = ModelPricing(
            model_id="123e4567-e89b-12d3-a456-426614174000",
            input_token_price_cpm=15,
            output_token_price_cpm=30
        )
        
        repr_str = repr(pricing)
        assert "ModelPricing" in repr_str
        assert "15" in repr_str
        assert "30" in repr_str
    
    def test_pricing_properties(self):
        """测试定价属性"""
        pricing = ModelPricing(
            model_id="123e4567-e89b-12d3-a456-426614174000",
            input_token_price_cpm=15,
            output_token_price_cpm=30
        )
        
        # 测试每个令牌价格
        assert pricing.input_price_per_token == 0.00015  # 15分/1000令牌/100分
        assert pricing.output_price_per_token == 0.0003  # 30分/1000令牌/100分
        
        # 测试每千个令牌价格
        assert pricing.input_price_per_1k_tokens == 0.15  # 15分/100分
        assert pricing.output_price_per_1k_tokens == 0.30  # 30分/100分
    
    def test_pricing_cost_calculation(self):
        """测试成本计算"""
        pricing = ModelPricing(
            model_id="123e4567-e89b-12d3-a456-426614174000",
            input_token_price_cpm=15,
            output_token_price_cpm=30
        )
        
        # 测试输入令牌成本
        input_cost = pricing.calculate_input_cost(1000)
        assert input_cost == 0.15  # 1000 * 0.00015
        
        # 测试输出令牌成本
        output_cost = pricing.calculate_output_cost(500)
        assert output_cost == 0.15  # 500 * 0.0003
        
        # 测试总成本
        total_cost = pricing.calculate_total_cost(1000, 500)
        assert total_cost == 0.30  # 0.15 + 0.15
    
    def test_pricing_default_currency(self):
        """测试默认货币"""
        pricing = ModelPricing(
            model_id="123e4567-e89b-12d3-a456-426614174000",
            input_token_price_cpm=15,
            output_token_price_cpm=30
        )
        
        # 默认值在数据库层面设置，这里测试字段存在
        assert hasattr(pricing, 'currency') 