"""
部署模型测试
"""

import pytest
from src.models.deployment import ModelDeployment

class TestModelDeployment:
    """模型部署测试类"""
    
    def test_deployment_creation(self):
        """测试部署创建"""
        deployment = ModelDeployment(
            model_id="123e4567-e89b-12d3-a456-426614174000",
            deployment_name="gpt4-prod",
            endpoint="https://api.openai.com/v1/chat/completions",
            auth_secret_manager_path="projects/demo/secrets/openai-key",
            region="us-central1",
            request_per_min=600,
            token_per_min=60000,
            is_default=True
        )
        
        assert deployment.model_id == "123e4567-e89b-12d3-a456-426614174000"
        assert deployment.deployment_name == "gpt4-prod"
        assert deployment.endpoint == "https://api.openai.com/v1/chat/completions"
        assert deployment.auth_secret_manager_path == "projects/demo/secrets/openai-key"
        assert deployment.region == "us-central1"
        assert deployment.request_per_min == 600
        assert deployment.token_per_min == 60000
        assert deployment.is_default is True
        assert hasattr(deployment, 'id')
    
    def test_deployment_repr(self):
        """测试部署字符串表示"""
        deployment = ModelDeployment(
            model_id="123e4567-e89b-12d3-a456-426614174000",
            deployment_name="gpt4-prod",
            endpoint="https://api.openai.com/v1/chat/completions"
        )
        
        repr_str = repr(deployment)
        assert "ModelDeployment" in repr_str
        assert "gpt4-prod" in repr_str
        assert "123e4567-e89b-12d3-a456-426614174000" in repr_str
    
    def test_deployment_properties(self):
        """测试部署属性"""
        deployment = ModelDeployment(
            model_id="123e4567-e89b-12d3-a456-426614174000",
            deployment_name="gpt4-prod",
            endpoint="https://api.openai.com/v1/chat/completions",
            auth_secret_manager_path="projects/demo/secrets/openai-key",
            region="us-central1",
            request_per_min=600,
            token_per_min=60000,
            is_default=True
        )
        
        assert deployment.name == "gpt4-prod"
        assert deployment.default is True
        assert deployment.auth_path == "projects/demo/secrets/openai-key"
        assert deployment.rpm == 600
        assert deployment.tpm == 60000
    
    def test_deployment_default_values(self):
        """测试部署默认值"""
        deployment = ModelDeployment(
            model_id="123e4567-e89b-12d3-a456-426614174000",
            deployment_name="gpt4-prod",
            endpoint="https://api.openai.com/v1/chat/completions"
        )
        
        # 默认值在数据库层面设置，这里测试字段存在
        assert hasattr(deployment, 'is_default')
        assert hasattr(deployment, 'auth_secret_manager_path')
        assert hasattr(deployment, 'region')
        assert hasattr(deployment, 'request_per_min')
        assert hasattr(deployment, 'token_per_min')
    
    def test_deployment_null_values(self):
        """测试部署空值处理"""
        deployment = ModelDeployment(
            model_id="123e4567-e89b-12d3-a456-426614174000",
            deployment_name="gpt4-prod",
            endpoint="https://api.openai.com/v1/chat/completions"
        )
        
        assert deployment.auth_path == ""
        assert deployment.rpm == 0
        assert deployment.tpm == 0
    
    def test_deployment_to_dict(self):
        """测试部署转字典"""
        deployment = ModelDeployment(
            model_id="123e4567-e89b-12d3-a456-426614174000",
            deployment_name="gpt4-prod",
            endpoint="https://api.openai.com/v1/chat/completions",
            auth_secret_manager_path="projects/demo/secrets/openai-key",
            region="us-central1",
            request_per_min=600,
            token_per_min=60000,
            is_default=True
        )
        
        data = deployment.to_dict()
        
        assert "id" in data
        assert "model_id" in data
        assert "deployment_name" in data
        assert "endpoint" in data
        assert "auth_secret_manager_path" in data
        assert "region" in data
        assert "request_per_min" in data
        assert "token_per_min" in data
        assert "is_default" in data
        assert data["model_id"] == "123e4567-e89b-12d3-a456-426614174000"
        assert data["deployment_name"] == "gpt4-prod"
        assert data["endpoint"] == "https://api.openai.com/v1/chat/completions"
        assert data["auth_secret_manager_path"] == "projects/demo/secrets/openai-key"
        assert data["region"] == "us-central1"
        assert data["request_per_min"] == 600
        assert data["token_per_min"] == 60000
        assert data["is_default"] is True
    
    def test_deployment_from_dict(self):
        """测试从字典创建部署"""
        data = {
            "model_id": "123e4567-e89b-12d3-a456-426614174000",
            "deployment_name": "gpt4-prod",
            "endpoint": "https://api.openai.com/v1/chat/completions",
            "auth_secret_manager_path": "projects/demo/secrets/openai-key",
            "region": "us-central1",
            "request_per_min": 600,
            "token_per_min": 60000,
            "is_default": True
        }
        
        deployment = ModelDeployment.from_dict(data)
        
        assert deployment.model_id == "123e4567-e89b-12d3-a456-426614174000"
        assert deployment.deployment_name == "gpt4-prod"
        assert deployment.endpoint == "https://api.openai.com/v1/chat/completions"
        assert deployment.auth_secret_manager_path == "projects/demo/secrets/openai-key"
        assert deployment.region == "us-central1"
        assert deployment.request_per_min == 600
        assert deployment.token_per_min == 60000
        assert deployment.is_default is True 