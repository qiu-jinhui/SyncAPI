"""
订阅仓储测试
"""

import pytest
from src.models.subscription import Subscription
from src.models.project import Project
from src.models.use_case import UseCase
from src.models.model import Model

class TestSubscriptionRepository:
    """订阅仓储测试类"""
    
    def test_find_by_subscription_key(self, subscription_repository, session):
        """测试根据订阅密钥查找订阅"""
        # 创建项目、用例、模型和订阅
        project = Project(project_name="Test Project", project_code="TEST_PROJ")
        use_case = UseCase(use_case_name="Test Use Case", ad_group="test", project_id=project.id)
        model = Model(model_name="Test Model", model_type="llm", provider="openai")
        session.add_all([project, use_case, model])
        session.flush()
        
        subscription = subscription_repository.create(
            subscription_key="test-key-123",
            project_id=project.id,
            use_case_id=use_case.id,
            model_id=model.id
        )
        session.commit()
        
        # 查找
        result = subscription_repository.find_by_subscription_key("test-key-123")
        
        assert result is not None
        assert result.id == subscription.id
        assert result.subscription_key == "test-key-123"
    
    def test_find_by_project(self, subscription_repository, session):
        """测试根据项目查找订阅"""
        # 创建项目、用例、模型和订阅
        project1 = Project(project_name="Project 1", project_code="PROJ1")
        project2 = Project(project_name="Project 2", project_code="PROJ2")
        use_case1 = UseCase(use_case_name="Use Case 1", ad_group="test1", project_id=project1.id)
        use_case2 = UseCase(use_case_name="Use Case 2", ad_group="test2", project_id=project2.id)
        model = Model(model_name="Test Model", model_type="llm", provider="openai")
        session.add_all([project1, project2, use_case1, use_case2, model])
        session.flush()
        
        subscription1 = subscription_repository.create(
            subscription_key="key1",
            project_id=project1.id,
            use_case_id=use_case1.id,
            model_id=model.id
        )
        subscription2 = subscription_repository.create(
            subscription_key="key2",
            project_id=project1.id,
            use_case_id=use_case1.id,
            model_id=model.id
        )
        session.commit()
        
        # 查找项目1的订阅
        results = subscription_repository.find_by_project(project1.id)
        
        assert len(results) == 2
        assert all(s.project_id == project1.id for s in results)
    
    def test_find_by_use_case(self, subscription_repository, session):
        """测试根据用例查找订阅"""
        # 创建项目、用例、模型和订阅
        project = Project(project_name="Test Project", project_code="TEST_PROJ")
        use_case = UseCase(use_case_name="Test Use Case", ad_group="test", project_id=project.id)
        model = Model(model_name="Test Model", model_type="llm", provider="openai")
        session.add_all([project, use_case, model])
        session.flush()
        
        subscription = subscription_repository.create(
            subscription_key="test-key",
            project_id=project.id,
            use_case_id=use_case.id,
            model_id=model.id
        )
        session.commit()
        
        # 查找
        results = subscription_repository.find_by_use_case(use_case.id)
        
        assert len(results) == 1
        assert results[0].use_case_id == use_case.id
    
    def test_find_by_model(self, subscription_repository, session):
        """测试根据模型查找订阅"""
        # 创建项目、用例、模型和订阅
        project = Project(project_name="Test Project", project_code="TEST_PROJ")
        use_case = UseCase(use_case_name="Test Use Case", ad_group="test", project_id=project.id)
        model1 = Model(model_name="Model 1", model_type="llm", provider="openai")
        model2 = Model(model_name="Model 2", model_type="llm", provider="anthropic")
        session.add_all([project, use_case, model1, model2])
        session.flush()
        
        subscription = subscription_repository.create(
            subscription_key="test-key",
            project_id=project.id,
            use_case_id=use_case.id,
            model_id=model1.id
        )
        session.commit()
        
        # 查找
        results = subscription_repository.find_by_model(model1.id)
        
        assert len(results) == 1
        assert results[0].model_id == model1.id
    
    def test_find_by_provider(self, subscription_repository, session):
        """测试根据提供商查找订阅"""
        # 创建项目、用例、模型和订阅
        project = Project(project_name="Test Project", project_code="TEST_PROJ")
        use_case = UseCase(use_case_name="Test Use Case", ad_group="test", project_id=project.id)
        model1 = Model(model_name="OpenAI Model", model_type="llm", provider="openai")
        model2 = Model(model_name="Anthropic Model", model_type="llm", provider="anthropic")
        session.add_all([project, use_case, model1, model2])
        session.flush()
        
        subscription = subscription_repository.create(
            subscription_key="test-key",
            project_id=project.id,
            use_case_id=use_case.id,
            model_id=model1.id
        )
        session.commit()
        
        # 查找
        results = subscription_repository.find_by_provider("openai")
        
        assert len(results) == 1
        assert results[0].model.provider == "openai"
    
    def test_get_subscription_stats(self, subscription_repository, session):
        """测试获取订阅统计信息"""
        # 创建项目、用例、模型和订阅
        project = Project(project_name="Test Project", project_code="TEST_PROJ")
        use_case = UseCase(use_case_name="Test Use Case", ad_group="test", project_id=project.id)
        model = Model(model_name="Test Model", model_type="llm", provider="openai")
        session.add_all([project, use_case, model])
        session.flush()
        
        subscription_repository.create(
            subscription_key="key1",
            project_id=project.id,
            use_case_id=use_case.id,
            model_id=model.id,
            status="active"
        )
        subscription_repository.create(
            subscription_key="key2",
            project_id=project.id,
            use_case_id=use_case.id,
            model_id=model.id,
            status="active"
        )
        subscription_repository.create(
            subscription_key="key3",
            project_id=project.id,
            use_case_id=use_case.id,
            model_id=model.id,
            status="inactive"
        )
        session.commit()
        
        # 获取统计信息
        stats = subscription_repository.get_subscription_stats()
        
        assert stats['total_subscriptions'] == 3
        assert stats['active_subscriptions'] == 2
        assert stats['inactive_subscriptions'] == 1 