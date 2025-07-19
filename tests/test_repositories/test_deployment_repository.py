"""
部署仓储测试
"""

import pytest
from src.models.deployment import ModelDeployment
from src.models.model import Model

class TestDeploymentRepository:
    """部署仓储测试类"""
    
    def test_find_by_name(self, deployment_repository, session):
        """测试根据名称查找部署"""
        # 创建模型和部署
        model = Model(model_name="Test Model", model_type="llm", provider="openai")
        session.add(model)
        session.flush()
        
        deployment = deployment_repository.create(
            deployment_name="Test Deployment",
            model_id=model.id,
            region="us-east-1"
        )
        session.commit()
        
        # 查找
        result = deployment_repository.find_by_name("Test Deployment")
        
        assert result is not None
        assert result.id == deployment.id
        assert result.deployment_name == "Test Deployment"
    
    def test_find_by_model(self, deployment_repository, session):
        """测试根据模型查找部署"""
        # 创建模型和部署
        model1 = Model(model_name="Model 1", model_type="llm", provider="openai")
        model2 = Model(model_name="Model 2", model_type="llm", provider="anthropic")
        session.add_all([model1, model2])
        session.flush()
        
        deployment1 = deployment_repository.create(
            deployment_name="Deployment 1",
            model_id=model1.id,
            region="us-east-1"
        )
        deployment2 = deployment_repository.create(
            deployment_name="Deployment 2",
            model_id=model1.id,
            region="us-west-1"
        )
        session.commit()
        
        # 查找模型1的部署
        results = deployment_repository.find_by_model(model1.id)
        
        assert len(results) == 2
        assert all(d.model_id == model1.id for d in results)
    
    def test_find_by_region(self, deployment_repository, session):
        """测试根据区域查找部署"""
        # 创建模型和部署
        model = Model(model_name="Test Model", model_type="llm", provider="openai")
        session.add(model)
        session.flush()
        
        deployment = deployment_repository.create(
            deployment_name="Test Deployment",
            model_id=model.id,
            region="us-east-1"
        )
        session.commit()
        
        # 查找
        results = deployment_repository.find_by_region("us-east-1")
        
        assert len(results) == 1
        assert results[0].region == "us-east-1"
    
    def test_find_default_deployment(self, deployment_repository, session):
        """测试查找默认部署"""
        # 创建模型和部署
        model = Model(model_name="Test Model", model_type="llm", provider="openai")
        session.add(model)
        session.flush()
        
        deployment = deployment_repository.create(
            deployment_name="Default Deployment",
            model_id=model.id,
            region="us-east-1",
            is_default=True
        )
        session.commit()
        
        # 查找默认部署
        result = deployment_repository.find_default_deployment(model.id)
        
        assert result is not None
        assert result.is_default is True
    
    def test_find_by_provider(self, deployment_repository, session):
        """测试根据提供商查找部署"""
        # 创建模型和部署
        model1 = Model(model_name="OpenAI Model", model_type="llm", provider="openai")
        model2 = Model(model_name="Anthropic Model", model_type="llm", provider="anthropic")
        session.add_all([model1, model2])
        session.flush()
        
        deployment1 = deployment_repository.create(
            deployment_name="OpenAI Deployment",
            model_id=model1.id,
            region="us-east-1"
        )
        deployment2 = deployment_repository.create(
            deployment_name="Anthropic Deployment",
            model_id=model2.id,
            region="us-west-1"
        )
        session.commit()
        
        # 查找OpenAI部署
        results = deployment_repository.find_by_provider("openai")
        
        assert len(results) == 1
        assert results[0].model.provider == "openai"
    
    def test_get_active_deployments(self, deployment_repository, session):
        """测试获取活跃部署"""
        # 创建模型和部署
        model = Model(model_name="Test Model", model_type="llm", provider="openai")
        session.add(model)
        session.flush()
        
        deployment1 = deployment_repository.create(
            deployment_name="Active Deployment",
            model_id=model.id,
            region="us-east-1",
            is_active=True
        )
        deployment2 = deployment_repository.create(
            deployment_name="Inactive Deployment",
            model_id=model.id,
            region="us-west-1",
            is_active=False
        )
        session.commit()
        
        # 获取活跃部署
        results = deployment_repository.get_active_deployments()
        
        assert len(results) == 1
        assert results[0].is_active is True
    
    def test_update_default_deployment(self, deployment_repository, session):
        """测试更新默认部署"""
        # 创建模型和部署
        model = Model(model_name="Test Model", model_type="llm", provider="openai")
        session.add(model)
        session.flush()
        
        deployment1 = deployment_repository.create(
            deployment_name="Deployment 1",
            model_id=model.id,
            region="us-east-1",
            is_default=True
        )
        deployment2 = deployment_repository.create(
            deployment_name="Deployment 2",
            model_id=model.id,
            region="us-west-1",
            is_default=False
        )
        session.commit()
        
        # 更新默认部署
        result = deployment_repository.update_default_deployment(model.id, deployment2.id)
        
        assert result is True
        
        # 验证默认部署已更新
        updated_deployment1 = deployment_repository.get_by_id(deployment1.id)
        updated_deployment2 = deployment_repository.get_by_id(deployment2.id)
        
        assert updated_deployment1.is_default is False
        assert updated_deployment2.is_default is True 