"""
模型关系测试
"""

import pytest
from src.models import (
    Project, UseCase, UseCaseBudget, Model, ModelDeployment, 
    ModelPricing, Subscription, ModelLimit
)

class TestModelRelationships:
    """模型关系测试类"""
    
    def test_project_use_case_relationship(self):
        """测试项目和用例关系"""
        # 创建项目
        project = Project(
            project_name="Test Project",
            project_code="TEST_PROJ"
        )
        
        # 创建用例
        use_case = UseCase(
            project_id=project.id,
            use_case_name="Test Use Case",
            ad_group="test_group",
            is_active=True
        )
        
        # 测试关系
        assert use_case.project_id == project.id
        assert use_case.project is None  # 需要数据库会话才能加载关系
    
    def test_use_case_budget_relationship(self):
        """测试用例和预算关系"""
        # 创建用例
        use_case = UseCase(
            project_id="123e4567-e89b-12d3-a456-426614174000",
            use_case_name="Test Use Case",
            ad_group="test_group"
        )
        
        # 创建预算
        budget = UseCaseBudget(
            use_case_id=use_case.id,
            budget_cents=1000000,  # 10000元
            currency="USD"
        )
        
        # 测试关系
        assert budget.use_case_id == use_case.id
        assert budget.budget_amount == 10000.0
    
    def test_model_deployment_relationship(self):
        """测试模型和部署关系"""
        # 创建模型
        model = Model(
            model_name="gpt-4",
            model_type="chat",
            provider="openai"
        )
        
        # 创建部署
        deployment = ModelDeployment(
            model_id=model.id,
            deployment_name="gpt4-prod",
            endpoint="https://api.openai.com/v1/chat/completions",
            auth_secret_manager_path="projects/demo/secrets/openai-key",
            region="us-central1",
            request_per_min=600,
            token_per_min=60000,
            is_default=True
        )
        
        # 测试关系
        assert deployment.model_id == model.id
        assert deployment.name == "gpt4-prod"
        assert deployment.default is True
        assert deployment.rpm == 600
        assert deployment.tpm == 60000
    
    def test_model_pricing_relationship(self):
        """测试模型和定价关系"""
        # 创建模型
        model = Model(
            model_name="gpt-4",
            model_type="chat",
            provider="openai"
        )
        
        # 创建定价
        pricing = ModelPricing(
            model_id=model.id,
            input_token_price_cpm=15,
            output_token_price_cpm=30,
            currency="USD"
        )
        
        # 测试关系
        assert pricing.model_id == model.id
        assert pricing.input_price_per_1k_tokens == 0.15
        assert pricing.output_price_per_1k_tokens == 0.30
    
    def test_subscription_relationships(self):
        """测试订阅关系"""
        # 创建订阅
        subscription = Subscription(
            project_id="123e4567-e89b-12d3-a456-426614174000",
            use_case_id="123e4567-e89b-12d3-a456-426614174001",
            model_id="123e4567-e89b-12d3-a456-426614174002"
        )
        
        # 测试订阅键
        expected_key = "123e4567-e89b-12d3-a456-426614174000:123e4567-e89b-12d3-a456-426614174001:123e4567-e89b-12d3-a456-426614174002"
        assert subscription.subscription_key == expected_key
    
    def test_model_limit_relationship(self):
        """测试模型限制关系"""
        # 创建限制
        limit = ModelLimit(
            subscription_id="123e4567-e89b-12d3-a456-426614174000",
            limit_type="input_token_limit",
            scope="daily",
            limit_value=1000000
        )
        
        # 测试关系
        assert limit.subscription_id == "123e4567-e89b-12d3-a456-426614174000"
        assert limit.type == "input_token_limit"
        assert limit.scope == "daily"
        assert limit.value == 1000000 