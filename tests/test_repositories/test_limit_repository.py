"""
限制仓储测试
"""

import pytest
from datetime import datetime, timezone
from src.models.limit import ModelLimit, ModelLimitUsage
from src.models.subscription import Subscription
from src.models.project import Project
from src.models.use_case import UseCase
from src.models.model import Model

class TestLimitRepository:
    """限制仓储测试类"""
    
    def test_find_by_subscription(self, limit_repository, session):
        """测试根据订阅查找限制"""
        # 创建项目、用例、模型、订阅和限制
        project = Project(project_name="Test Project", project_code="TEST_PROJ")
        use_case = UseCase(use_case_name="Test Use Case", ad_group="test", project_id=project.id)
        model = Model(model_name="Test Model", model_type="llm", provider="openai")
        subscription = Subscription(
            project_id=project.id,
            use_case_id=use_case.id,
            model_id=model.id
        )
        session.add_all([project, use_case, model, subscription])
        session.flush()
        
        limit = limit_repository.create(
            subscription_id=subscription.id,
            limit_type="rate",
            limit_value=1000,
            scope="per_minute"
        )
        session.commit()
        
        # 查找
        results = limit_repository.find_by_subscription(subscription.id)
        
        assert len(results) == 1
        assert results[0].subscription_id == subscription.id
    
    def test_find_by_type(self, limit_repository, session):
        """测试根据类型查找限制"""
        # 创建项目、用例、模型、订阅和限制
        project = Project(project_name="Test Project", project_code="TEST_PROJ")
        use_case = UseCase(use_case_name="Test Use Case", ad_group="test", project_id=project.id)
        model = Model(model_name="Test Model", model_type="llm", provider="openai")
        subscription = Subscription(
            project_id=project.id,
            use_case_id=use_case.id,
            model_id=model.id
        )
        session.add_all([project, use_case, model, subscription])
        session.flush()
        
        limit = limit_repository.create(
            subscription_id=subscription.id,
            limit_type="rate",
            limit_value=1000,
            scope="per_minute"
        )
        session.commit()
        
        # 查找
        results = limit_repository.find_by_type("rate")
        
        assert len(results) == 1
        assert results[0].limit_type == "rate"
    
    def test_find_by_scope(self, limit_repository, session):
        """测试根据范围查找限制"""
        # 创建项目、用例、模型、订阅和限制
        project = Project(project_name="Test Project", project_code="TEST_PROJ")
        use_case = UseCase(use_case_name="Test Use Case", ad_group="test", project_id=project.id)
        model = Model(model_name="Test Model", model_type="llm", provider="openai")
        subscription = Subscription(
            project_id=project.id,
            use_case_id=use_case.id,
            model_id=model.id
        )
        session.add_all([project, use_case, model, subscription])
        session.flush()
        
        limit = limit_repository.create(
            subscription_id=subscription.id,
            limit_type="rate",
            limit_value=1000,
            scope="per_minute"
        )
        session.commit()
        
        # 查找
        results = limit_repository.find_by_scope("per_minute")
        
        assert len(results) == 1
        assert results[0].scope == "per_minute"
    
    def test_find_by_date_range(self, limit_repository, session):
        """测试根据日期范围查找限制"""
        # 创建项目、用例、模型、订阅和限制
        project = Project(project_name="Test Project", project_code="TEST_PROJ")
        use_case = UseCase(use_case_name="Test Use Case", ad_group="test", project_id=project.id)
        model = Model(model_name="Test Model", model_type="llm", provider="openai")
        subscription = Subscription(
            project_id=project.id,
            use_case_id=use_case.id,
            model_id=model.id
        )
        session.add_all([project, use_case, model, subscription])
        session.flush()
        
        limit = limit_repository.create(
            subscription_id=subscription.id,
            limit_type="rate",
            limit_value=1000,
            scope="per_minute",
            start_date=datetime.now(timezone.utc)
        )
        session.commit()
        
        # 查找
        start_date = datetime.now(timezone.utc)
        end_date = datetime.now(timezone.utc)
        results = limit_repository.find_by_date_range(start_date, end_date)
        
        assert len(results) >= 1
    
    def test_get_limit_stats(self, limit_repository, session):
        """测试获取限制统计信息"""
        # 创建项目、用例、模型、订阅和限制
        project = Project(project_name="Test Project", project_code="TEST_PROJ")
        use_case = UseCase(use_case_name="Test Use Case", ad_group="test", project_id=project.id)
        model = Model(model_name="Test Model", model_type="llm", provider="openai")
        subscription = Subscription(
            project_id=project.id,
            use_case_id=use_case.id,
            model_id=model.id
        )
        session.add_all([project, use_case, model, subscription])
        session.flush()
        
        limit_repository.create(
            subscription_id=subscription.id,
            limit_type="rate",
            limit_value=1000,
            scope="per_minute"
        )
        limit_repository.create(
            subscription_id=subscription.id,
            limit_type="quota",
            limit_value=10000,
            scope="per_day"
        )
        session.commit()
        
        # 获取统计信息
        stats = limit_repository.get_limit_stats()
        
        assert stats['total_limits'] == 2
        assert stats['rate_limits'] == 1
        assert stats['quota_limits'] == 1

class TestLimitUsageRepository:
    """限制使用仓储测试类"""
    
    def test_find_by_subscription(self, limit_usage_repository, session):
        """测试根据订阅查找限制使用"""
        # 创建项目、用例、模型、订阅和限制使用
        project = Project(project_name="Test Project", project_code="TEST_PROJ")
        use_case = UseCase(use_case_name="Test Use Case", ad_group="test", project_id=project.id)
        model = Model(model_name="Test Model", model_type="llm", provider="openai")
        subscription = Subscription(
            project_id=project.id,
            use_case_id=use_case.id,
            model_id=model.id
        )
        session.add_all([project, use_case, model, subscription])
        session.flush()
        
        usage = limit_usage_repository.create(
            subscription_id=subscription.id,
            limit_type="rate",
            usage_value=50,
            usage_date=datetime.now(timezone.utc)
        )
        session.commit()
        
        # 查找
        results = limit_usage_repository.find_by_subscription(subscription.id)
        
        assert len(results) == 1
        assert results[0].subscription_id == subscription.id
    
    def test_find_by_type(self, limit_usage_repository, session):
        """测试根据类型查找限制使用"""
        # 创建项目、用例、模型、订阅和限制使用
        project = Project(project_name="Test Project", project_code="TEST_PROJ")
        use_case = UseCase(use_case_name="Test Use Case", ad_group="test", project_id=project.id)
        model = Model(model_name="Test Model", model_type="llm", provider="openai")
        subscription = Subscription(
            project_id=project.id,
            use_case_id=use_case.id,
            model_id=model.id
        )
        session.add_all([project, use_case, model, subscription])
        session.flush()
        
        usage = limit_usage_repository.create(
            subscription_id=subscription.id,
            limit_type="rate",
            usage_value=50,
            usage_date=datetime.now(timezone.utc)
        )
        session.commit()
        
        # 查找
        results = limit_usage_repository.find_by_type("rate")
        
        assert len(results) == 1
        assert results[0].limit_type == "rate"
    
    def test_find_by_date_range(self, limit_usage_repository, session):
        """测试根据日期范围查找限制使用"""
        # 创建项目、用例、模型、订阅和限制使用
        project = Project(project_name="Test Project", project_code="TEST_PROJ")
        use_case = UseCase(use_case_name="Test Use Case", ad_group="test", project_id=project.id)
        model = Model(model_name="Test Model", model_type="llm", provider="openai")
        subscription = Subscription(
            project_id=project.id,
            use_case_id=use_case.id,
            model_id=model.id
        )
        session.add_all([project, use_case, model, subscription])
        session.flush()
        
        usage = limit_usage_repository.create(
            subscription_id=subscription.id,
            limit_type="rate",
            usage_value=50,
            usage_date=datetime.now(timezone.utc)
        )
        session.commit()
        
        # 查找
        start_date = datetime.now(timezone.utc)
        end_date = datetime.now(timezone.utc)
        results = limit_usage_repository.find_by_date_range(start_date, end_date)
        
        assert len(results) >= 1
    
    def test_get_usage_stats(self, limit_usage_repository, session):
        """测试获取使用统计信息"""
        # 创建项目、用例、模型、订阅和限制使用
        project = Project(project_name="Test Project", project_code="TEST_PROJ")
        use_case = UseCase(use_case_name="Test Use Case", ad_group="test", project_id=project.id)
        model = Model(model_name="Test Model", model_type="llm", provider="openai")
        subscription = Subscription(
            project_id=project.id,
            use_case_id=use_case.id,
            model_id=model.id
        )
        session.add_all([project, use_case, model, subscription])
        session.flush()
        
        limit_usage_repository.create(
            subscription_id=subscription.id,
            limit_type="rate",
            usage_value=50,
            usage_date=datetime.now(timezone.utc)
        )
        limit_usage_repository.create(
            subscription_id=subscription.id,
            limit_type="rate",
            usage_value=75,
            usage_date=datetime.now(timezone.utc)
        )
        session.commit()
        
        # 获取统计信息
        stats = limit_usage_repository.get_usage_stats()
        
        assert stats['total_usage'] == 2
        assert stats['total_usage_value'] == 125 