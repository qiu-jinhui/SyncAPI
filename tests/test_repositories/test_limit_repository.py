"""
限制仓储测试
"""

import pytest
from datetime import datetime
from sqlalchemy import func
from tests.test_models import (
    TestLimitModel, TestLimitUsageModel, TestProjectModel, 
    TestUseCaseModel, TestModelModel, TestSubscriptionModel
)

class TestLimitRepository:
    """限制仓储测试类"""
    
    def test_find_by_subscription(self, limit_repository, session):
        """测试根据订阅查找限制"""
        # 创建完整的依赖链
        project = TestProjectModel(project_name="Test Project", project_code="TEST_PROJ")
        session.add(project)
        session.flush()
        
        use_case = TestUseCaseModel(name="Test Use Case", ad_group="test", project_id=project.id)
        session.add(use_case)
        session.flush()
        
        model = TestModelModel(name="Test Model", type="llm", provider="openai")
        session.add(model)
        session.flush()
        
        subscription = TestSubscriptionModel(
            project_id=project.id,
            use_case_id=use_case.id,
            model_id=model.id,
            provider="openai"
        )
        session.add(subscription)
        session.flush()
        
        limit = limit_repository.create(
            subscription_id=subscription.id,
            type="requests",
            value=1000
        )
        session.commit()
        
        # 查找
        results = limit_repository.find_by_subscription(subscription.id)
        
        assert len(results) == 1
        assert results[0].subscription_id == subscription.id
    
    def test_find_by_type(self, limit_repository, session):
        """测试根据类型查找限制"""
        # 创建完整的依赖链
        project = TestProjectModel(project_name="Test Project", project_code="TEST_PROJ")
        session.add(project)
        session.flush()
        
        use_case = TestUseCaseModel(name="Test Use Case", ad_group="test", project_id=project.id)
        session.add(use_case)
        session.flush()
        
        model = TestModelModel(name="Test Model", type="llm", provider="openai")
        session.add(model)
        session.flush()
        
        subscription = TestSubscriptionModel(
            project_id=project.id,
            use_case_id=use_case.id,
            model_id=model.id,
            provider="openai"
        )
        session.add(subscription)
        session.flush()
        
        limit1 = limit_repository.create(
            subscription_id=subscription.id,
            type="requests",
            value=1000
        )
        limit2 = limit_repository.create(
            subscription_id=subscription.id,
            type="tokens",
            value=50000
        )
        session.commit()
        
        # 查找
        results = limit_repository.find_by_type("requests")
        
        assert len(results) == 1
        assert results[0].type == "requests"
    
    def test_find_by_scope(self, limit_repository, session):
        """测试根据范围查找限制"""
        # 创建完整的依赖链
        project = TestProjectModel(project_name="Test Project", project_code="TEST_PROJ")
        session.add(project)
        session.flush()
        
        use_case = TestUseCaseModel(name="Test Use Case", ad_group="test", project_id=project.id)
        session.add(use_case)
        session.flush()
        
        model = TestModelModel(name="Test Model", type="llm", provider="openai")
        session.add(model)
        session.flush()
        
        subscription = TestSubscriptionModel(
            project_id=project.id,
            use_case_id=use_case.id,
            model_id=model.id,
            provider="openai"
        )
        session.add(subscription)
        session.flush()
        
        limit = limit_repository.create(
            subscription_id=subscription.id,
            type="requests",
            scope="daily",
            value=1000
        )
        session.commit()
        
        # 查找
        results = limit_repository.find_by_scope("daily")
        
        assert len(results) == 1
        assert results[0].scope == "daily"
    
    def test_find_by_date_range(self, limit_repository, session):
        """测试根据日期范围查找限制"""
        # 创建完整的依赖链
        project = TestProjectModel(project_name="Test Project", project_code="TEST_PROJ")
        session.add(project)
        session.flush()
        
        use_case = TestUseCaseModel(name="Test Use Case", ad_group="test", project_id=project.id)
        session.add(use_case)
        session.flush()
        
        model = TestModelModel(name="Test Model", type="llm", provider="openai")
        session.add(model)
        session.flush()
        
        subscription = TestSubscriptionModel(
            project_id=project.id,
            use_case_id=use_case.id,
            model_id=model.id,
            provider="openai"
        )
        session.add(subscription)
        session.flush()
        
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 12, 31)
        
        limit = limit_repository.create(
            subscription_id=subscription.id,
            type="requests",
            value=1000,
            start_date=start_date,
            end_date=end_date
        )
        session.commit()
        
        # 查找
        results = limit_repository.find_by_date_range(
            datetime(2023, 1, 1),
            datetime(2023, 12, 31)
        )
        
        assert len(results) == 1
        assert results[0].start_date >= start_date
    
    def test_get_limit_stats(self, limit_repository, session):
        """测试获取限制统计信息"""
        # 创建完整的依赖链
        project = TestProjectModel(project_name="Test Project", project_code="TEST_PROJ")
        session.add(project)
        session.flush()
        
        use_case = TestUseCaseModel(name="Test Use Case", ad_group="test", project_id=project.id)
        session.add(use_case)
        session.flush()
        
        model = TestModelModel(name="Test Model", type="llm", provider="openai")
        session.add(model)
        session.flush()
        
        subscription = TestSubscriptionModel(
            project_id=project.id,
            use_case_id=use_case.id,
            model_id=model.id,
            provider="openai"
        )
        session.add(subscription)
        session.flush()
        
        limit_repository.create(
            subscription_id=subscription.id,
            type="requests",
            value=1000
        )
        limit_repository.create(
            subscription_id=subscription.id,
            type="tokens",
            value=50000
        )
        limit_repository.create(
            subscription_id=subscription.id,
            type="cost",
            value=100
        )
        session.commit()
        
        # 获取统计信息
        stats = limit_repository.get_limit_stats()
        
        assert stats['total_limits'] == 3
        assert stats['types'] == 3

class TestLimitUsageRepository:
    """限制使用仓储测试类"""
    
    def test_find_by_subscription(self, limit_usage_repository, session):
        """测试根据订阅查找限制使用"""
        # 创建完整的依赖链
        project = TestProjectModel(project_name="Test Project", project_code="TEST_PROJ")
        session.add(project)
        session.flush()
        
        use_case = TestUseCaseModel(name="Test Use Case", ad_group="test", project_id=project.id)
        session.add(use_case)
        session.flush()
        
        model = TestModelModel(name="Test Model", type="llm", provider="openai")
        session.add(model)
        session.flush()
        
        subscription = TestSubscriptionModel(
            project_id=project.id,
            use_case_id=use_case.id,
            model_id=model.id,
            provider="openai"
        )
        session.add(subscription)
        session.flush()
        
        limit = TestLimitModel(
            subscription_id=subscription.id,
            type="requests",
            value=1000
        )
        session.add(limit)
        session.flush()
        
        usage = limit_usage_repository.create(
            limit_id=limit.id,
            type="requests",
            value_used=100,
            usage_date=datetime.now()
        )
        session.commit()
        
        # 查找
        results = limit_usage_repository.find_by_subscription(subscription.id)
        
        assert len(results) == 1
        assert results[0].limit_id == limit.id
    
    def test_find_by_type(self, limit_usage_repository, session):
        """测试根据类型查找限制使用"""
        # 创建完整的依赖链
        project = TestProjectModel(project_name="Test Project", project_code="TEST_PROJ")
        session.add(project)
        session.flush()
        
        use_case = TestUseCaseModel(name="Test Use Case", ad_group="test", project_id=project.id)
        session.add(use_case)
        session.flush()
        
        model = TestModelModel(name="Test Model", type="llm", provider="openai")
        session.add(model)
        session.flush()
        
        subscription = TestSubscriptionModel(
            project_id=project.id,
            use_case_id=use_case.id,
            model_id=model.id,
            provider="openai"
        )
        session.add(subscription)
        session.flush()
        
        limit = TestLimitModel(
            subscription_id=subscription.id,
            type="requests",
            value=1000
        )
        session.add(limit)
        session.flush()
        
        usage = limit_usage_repository.create(
            limit_id=limit.id,
            type="requests",
            value_used=100,
            usage_date=datetime.now()
        )
        session.commit()
        
        # 查找
        results = limit_usage_repository.find_by_type("requests")
        
        assert len(results) == 1
        assert results[0].type == "requests"
    
    def test_find_by_date_range(self, limit_usage_repository, session):
        """测试根据日期范围查找限制使用"""
        # 创建完整的依赖链
        project = TestProjectModel(project_name="Test Project", project_code="TEST_PROJ")
        session.add(project)
        session.flush()
        
        use_case = TestUseCaseModel(name="Test Use Case", ad_group="test", project_id=project.id)
        session.add(use_case)
        session.flush()
        
        model = TestModelModel(name="Test Model", type="llm", provider="openai")
        session.add(model)
        session.flush()
        
        subscription = TestSubscriptionModel(
            project_id=project.id,
            use_case_id=use_case.id,
            model_id=model.id,
            provider="openai"
        )
        session.add(subscription)
        session.flush()
        
        limit = TestLimitModel(
            subscription_id=subscription.id,
            type="requests",
            value=1000
        )
        session.add(limit)
        session.flush()
        
        usage_date = datetime(2023, 6, 15)
        usage = limit_usage_repository.create(
            limit_id=limit.id,
            type="requests",
            value_used=100,
            usage_date=usage_date
        )
        session.commit()
        
        # 查找
        results = limit_usage_repository.find_by_date_range(
            datetime(2023, 1, 1),
            datetime(2023, 12, 31)
        )
        
        assert len(results) == 1
        assert results[0].usage_date >= datetime(2023, 1, 1)
    
    def test_get_usage_stats(self, limit_usage_repository, session):
        """测试获取使用统计信息"""
        # 创建完整的依赖链
        project = TestProjectModel(project_name="Test Project", project_code="TEST_PROJ")
        session.add(project)
        session.flush()
        
        use_case = TestUseCaseModel(name="Test Use Case", ad_group="test", project_id=project.id)
        session.add(use_case)
        session.flush()
        
        model = TestModelModel(name="Test Model", type="llm", provider="openai")
        session.add(model)
        session.flush()
        
        subscription = TestSubscriptionModel(
            project_id=project.id,
            use_case_id=use_case.id,
            model_id=model.id,
            provider="openai"
        )
        session.add(subscription)
        session.flush()
        
        limit = TestLimitModel(
            subscription_id=subscription.id,
            type="requests",
            value=1000
        )
        session.add(limit)
        session.flush()
        
        limit_usage_repository.create(
            limit_id=limit.id,
            type="requests",
            value_used=100,
            usage_date=datetime.now()
        )
        limit_usage_repository.create(
            limit_id=limit.id,
            type="requests",
            value_used=150,
            usage_date=datetime.now()
        )
        session.commit()
        
        # 获取统计信息
        stats = limit_usage_repository.get_usage_stats()
        
        assert stats['total_usage'] == 250
        assert stats['usage_count'] == 2 