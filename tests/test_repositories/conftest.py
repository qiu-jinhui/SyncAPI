"""
测试配置文件
设置测试环境和fixture
"""

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 确保在导入模型之前设置测试环境变量
os.environ['TESTING'] = 'true'

# 导入测试模型
from tests.test_models import (
    TestBase, TestProjectModel, TestUseCaseModel, TestBudgetModel, 
    TestBudgetUsageModel, TestModelModel, TestDeploymentModel, 
    TestPricingModel, TestSubscriptionModel, TestLimitModel, TestLimitUsageModel
)

# 导入仓储类
from src.repositories.base_repository import BaseRepository

# 创建测试专用的仓储类
class TestProjectRepository(BaseRepository[TestProjectModel]):
    def __init__(self, session):
        super().__init__(TestProjectModel, session)

class TestUseCaseRepository(BaseRepository[TestUseCaseModel]):
    def __init__(self, session):
        super().__init__(TestUseCaseModel, session)

class TestBudgetRepository(BaseRepository[TestBudgetModel]):
    def __init__(self, session):
        super().__init__(TestBudgetModel, session)

class TestBudgetUsageRepository(BaseRepository[TestBudgetUsageModel]):
    def __init__(self, session):
        super().__init__(TestBudgetUsageModel, session)

class TestModelRepository(BaseRepository[TestModelModel]):
    def __init__(self, session):
        super().__init__(TestModelModel, session)

class TestDeploymentRepository(BaseRepository[TestDeploymentModel]):
    def __init__(self, session):
        super().__init__(TestDeploymentModel, session)

class TestPricingRepository(BaseRepository[TestPricingModel]):
    def __init__(self, session):
        super().__init__(TestPricingModel, session)

class TestSubscriptionRepository(BaseRepository[TestSubscriptionModel]):
    def __init__(self, session):
        super().__init__(TestSubscriptionModel, session)

class TestLimitRepository(BaseRepository[TestLimitModel]):
    def __init__(self, session):
        super().__init__(TestLimitModel, session)

class TestLimitUsageRepository(BaseRepository[TestLimitUsageModel]):
    def __init__(self, session):
        super().__init__(TestLimitUsageModel, session)

@pytest.fixture
def engine():
    """创建内存SQLite引擎"""
    return create_engine("sqlite:///:memory:")

@pytest.fixture
def session(engine):
    """创建数据库会话"""
    TestBase.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def base_repository(session):
    """基础仓储实例"""
    return TestProjectRepository(session)

@pytest.fixture  
def project_repository(session):
    """项目仓储实例"""
    return TestProjectRepository(session)

@pytest.fixture
def use_case_repository(session):
    """用例仓储实例"""
    return TestUseCaseRepository(session)

@pytest.fixture
def budget_repository(session):
    """预算仓储实例"""
    return TestBudgetRepository(session)

@pytest.fixture
def budget_usage_repository(session):
    """预算使用仓储实例"""
    return TestBudgetUsageRepository(session)

@pytest.fixture
def model_repository(session):
    """模型仓储实例"""
    return TestModelRepository(session)

@pytest.fixture
def deployment_repository(session):
    """部署仓储实例"""
    return TestDeploymentRepository(session)

@pytest.fixture
def pricing_repository(session):
    """定价仓储实例"""
    return TestPricingRepository(session)

@pytest.fixture
def subscription_repository(session):
    """订阅仓储实例"""
    return TestSubscriptionRepository(session)

@pytest.fixture
def limit_repository(session):
    """限制仓储实例"""
    return TestLimitRepository(session)

@pytest.fixture
def limit_usage_repository(session):
    """限制使用仓储实例"""
    return TestLimitUsageRepository(session) 