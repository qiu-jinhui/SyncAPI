"""
模型仓储测试
"""

import pytest
from src.models.model import Model

class TestModelRepository:
    """模型仓储测试类"""
    
    def test_find_by_name(self, model_repository, session):
        """测试根据名称查找模型"""
        # 创建模型
        model = model_repository.create(
            model_name="Test Model",
            model_type="llm",
            provider="openai"
        )
        session.commit()
        
        # 查找
        result = model_repository.find_by_name("Test Model")
        
        assert result is not None
        assert result.id == model.id
        assert result.model_name == "Test Model"
    
    def test_find_by_type(self, model_repository, session):
        """测试根据类型查找模型"""
        # 创建模型
        model1 = model_repository.create(
            model_name="LLM Model",
            model_type="llm",
            provider="openai"
        )
        model2 = model_repository.create(
            model_name="Embedding Model",
            model_type="embedding",
            provider="openai"
        )
        session.commit()
        
        # 查找LLM模型
        results = model_repository.find_by_type("llm")
        
        assert len(results) == 1
        assert results[0].model_type == "llm"
    
    def test_find_by_provider(self, model_repository, session):
        """测试根据提供商查找模型"""
        # 创建模型
        model1 = model_repository.create(
            model_name="OpenAI Model",
            model_type="llm",
            provider="openai"
        )
        model2 = model_repository.create(
            model_name="Anthropic Model",
            model_type="llm",
            provider="anthropic"
        )
        session.commit()
        
        # 查找OpenAI模型
        results = model_repository.find_by_provider("openai")
        
        assert len(results) == 1
        assert results[0].provider == "openai"
    
    def test_find_by_input_type(self, model_repository, session):
        """测试根据输入类型查找模型"""
        # 创建模型
        model = model_repository.create(
            model_name="Text Model",
            model_type="llm",
            provider="openai",
            input_type="text"
        )
        session.commit()
        
        # 查找
        results = model_repository.find_by_input_type("text")
        
        assert len(results) == 1
        assert results[0].input_type == "text"
    
    def test_find_by_output_type(self, model_repository, session):
        """测试根据输出类型查找模型"""
        # 创建模型
        model = model_repository.create(
            model_name="Text Model",
            model_type="llm",
            provider="openai",
            output_type="text"
        )
        session.commit()
        
        # 查找
        results = model_repository.find_by_output_type("text")
        
        assert len(results) == 1
        assert results[0].output_type == "text"
    
    def test_search_models(self, model_repository, session):
        """测试搜索模型"""
        # 创建模型
        model_repository.create(
            model_name="GPT-4 Model",
            model_type="llm",
            provider="openai"
        )
        model_repository.create(
            model_name="Claude Model",
            model_type="llm",
            provider="anthropic"
        )
        session.commit()
        
        # 搜索
        results = model_repository.search_models("GPT")
        
        assert len(results) == 1
        assert "GPT" in results[0].model_name
    
    def test_get_model_stats(self, model_repository, session):
        """测试获取模型统计信息"""
        # 创建模型
        model_repository.create(
            model_name="LLM Model 1",
            model_type="llm",
            provider="openai"
        )
        model_repository.create(
            model_name="LLM Model 2",
            model_type="llm",
            provider="anthropic"
        )
        model_repository.create(
            model_name="Embedding Model",
            model_type="embedding",
            provider="openai"
        )
        session.commit()
        
        # 获取统计信息
        stats = model_repository.get_model_stats()
        
        assert stats['total_models'] == 3
        assert stats['llm_models'] == 2
        assert stats['embedding_models'] == 1 