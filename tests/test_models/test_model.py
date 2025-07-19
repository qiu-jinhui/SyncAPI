"""
模型定义测试
"""

import pytest
from src.models.model import Model

class TestModel:
    """模型定义测试类"""
    
    def test_model_creation(self):
        """测试模型创建"""
        model = Model(
            model_name="gpt-4",
            model_type="chat",
            provider="openai",
            model_input="text",
            model_output="text",
            max_content_length=1000000
        )
        
        assert model.model_name == "gpt-4"
        assert model.model_type == "chat"
        assert model.provider == "openai"
        assert model.model_input == "text"
        assert model.model_output == "text"
        assert model.max_content_length == 1000000
        # UUID需要数据库会话才能自动生成，这里只测试字段存在
        assert hasattr(model, 'id')
    
    def test_model_repr(self):
        """测试模型字符串表示"""
        model = Model(
            model_name="gpt-4",
            model_type="chat",
            provider="openai"
        )
        
        repr_str = repr(model)
        assert "Model" in repr_str
        assert "gpt-4" in repr_str
        assert "chat" in repr_str
        assert "openai" in repr_str
    
    def test_model_properties(self):
        """测试模型属性"""
        model = Model(
            model_name="gpt-4",
            model_type="chat",
            provider="openai",
            max_content_length=1000000
        )
        
        assert model.name == "gpt-4"
        assert model.type == "chat"
        assert model.max_length == 1000000
    
    def test_model_max_length_default(self):
        """测试模型最大长度默认值"""
        model = Model(
            model_name="gpt-4",
            model_type="chat"
        )
        
        assert model.max_length == 0
    
    def test_model_to_dict(self):
        """测试模型转字典"""
        model = Model(
            model_name="gpt-4",
            model_type="chat",
            provider="openai"
        )
        
        data = model.to_dict()
        
        assert "id" in data
        assert "model_name" in data
        assert "model_type" in data
        assert "provider" in data
        assert data["model_name"] == "gpt-4"
        assert data["model_type"] == "chat"
        assert data["provider"] == "openai" 