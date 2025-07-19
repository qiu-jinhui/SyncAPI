"""
预算模型测试
"""

import pytest
from datetime import date
from src.models.budget import UseCaseBudget, UseCaseBudgetUsage

class TestUseCaseBudget:
    """用例预算模型测试类"""
    
    def test_budget_creation(self):
        """测试预算创建"""
        budget = UseCaseBudget(
            use_case_id="123e4567-e89b-12d3-a456-426614174000",
            budget_cents=1000000,  # 10000元
            currency="USD"
        )
        
        assert budget.use_case_id == "123e4567-e89b-12d3-a456-426614174000"
        assert budget.budget_cents == 1000000
        assert budget.currency == "USD"
        assert hasattr(budget, 'id')
    
    def test_budget_repr(self):
        """测试预算字符串表示"""
        budget = UseCaseBudget(
            use_case_id="123e4567-e89b-12d3-a456-426614174000",
            budget_cents=1000000
        )
        
        repr_str = repr(budget)
        assert "UseCaseBudget" in repr_str
        assert "1000000" in repr_str
    
    def test_budget_amount_property(self):
        """测试预算金额属性"""
        budget = UseCaseBudget(
            use_case_id="123e4567-e89b-12d3-a456-426614174000",
            budget_cents=1000000
        )
        
        assert budget.budget_amount == 10000.0
        
        # 测试设置金额
        budget.budget_amount = 5000.0
        assert budget.budget_cents == 500000
    
    def test_budget_default_currency(self):
        """测试预算默认货币"""
        budget = UseCaseBudget(
            use_case_id="123e4567-e89b-12d3-a456-426614174000",
            budget_cents=1000000
        )
        
        # 默认值在数据库层面设置，这里测试字段存在
        assert hasattr(budget, 'currency')
    
    def test_budget_to_dict(self):
        """测试预算转字典"""
        budget = UseCaseBudget(
            use_case_id="123e4567-e89b-12d3-a456-426614174000",
            budget_cents=1000000,
            currency="USD"
        )
        
        data = budget.to_dict()
        
        assert "id" in data
        assert "use_case_id" in data
        assert "budget_cents" in data
        assert "currency" in data
        assert data["use_case_id"] == "123e4567-e89b-12d3-a456-426614174000"
        assert data["budget_cents"] == 1000000
        assert data["currency"] == "USD"

class TestUseCaseBudgetUsage:
    """用例预算使用模型测试类"""
    
    def test_budget_usage_creation(self):
        """测试预算使用创建"""
        usage = UseCaseBudgetUsage(
            use_case_id="123e4567-e89b-12d3-a456-426614174000",
            usage_period=date(2023, 1, 1),
            scope="daily",
            used_cents=50000,  # 500元
            currency="USD"
        )
        
        assert usage.use_case_id == "123e4567-e89b-12d3-a456-426614174000"
        assert usage.usage_period == date(2023, 1, 1)
        assert usage.scope == "daily"
        assert usage.used_cents == 50000
        assert usage.currency == "USD"
        assert hasattr(usage, 'id')
    
    def test_budget_usage_repr(self):
        """测试预算使用字符串表示"""
        usage = UseCaseBudgetUsage(
            use_case_id="123e4567-e89b-12d3-a456-426614174000",
            usage_period=date(2023, 1, 1),
            scope="daily",
            used_cents=50000
        )
        
        repr_str = repr(usage)
        assert "UseCaseBudgetUsage" in repr_str
        assert "daily" in repr_str
    
    def test_budget_usage_amount_property(self):
        """测试预算使用金额属性"""
        usage = UseCaseBudgetUsage(
            use_case_id="123e4567-e89b-12d3-a456-426614174000",
            usage_period=date(2023, 1, 1),
            scope="daily",
            used_cents=50000
        )
        
        assert usage.used_amount == 500.0
        
        # 测试设置金额
        usage.used_amount = 1000.0
        assert usage.used_cents == 100000
    
    def test_budget_usage_period_property(self):
        """测试预算使用期间属性"""
        usage = UseCaseBudgetUsage(
            use_case_id="123e4567-e89b-12d3-a456-426614174000",
            usage_period=date(2023, 1, 1),
            scope="daily",
            used_cents=50000
        )
        
        assert usage.usage_period_date == date(2023, 1, 1)
    
    def test_budget_usage_default_values(self):
        """测试预算使用默认值"""
        usage = UseCaseBudgetUsage(
            use_case_id="123e4567-e89b-12d3-a456-426614174000",
            usage_period=date(2023, 1, 1),
            scope="daily"
        )
        
        # 默认值在数据库层面设置，这里测试字段存在
        assert hasattr(usage, 'used_cents')
        assert hasattr(usage, 'currency')
    
    def test_budget_usage_to_dict(self):
        """测试预算使用转字典"""
        usage = UseCaseBudgetUsage(
            use_case_id="123e4567-e89b-12d3-a456-426614174000",
            usage_period=date(2023, 1, 1),
            scope="daily",
            used_cents=50000,
            currency="USD"
        )
        
        data = usage.to_dict()
        
        assert "id" in data
        assert "use_case_id" in data
        assert "usage_period" in data
        assert "scope" in data
        assert "used_cents" in data
        assert "currency" in data
        assert data["use_case_id"] == "123e4567-e89b-12d3-a456-426614174000"
        # 日期在to_dict中会被转换为字符串
        assert "2023-01-01" in str(data["usage_period"])
        assert data["scope"] == "daily"
        assert data["used_cents"] == 50000
        assert data["currency"] == "USD" 