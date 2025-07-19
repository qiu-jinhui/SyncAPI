"""
仓储层测试配置
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from src.models.base import Base
from src.repositories import (
    ProjectRepository, UseCaseRepository, BudgetRepository, BudgetUsageRepository,
    ModelRepository, DeploymentRepository, PricingRepository, SubscriptionRepository,
    LimitRepository, LimitUsageRepository
)

@pytest.fixture(scope="function")
def engine():
    """创建内存数据库引擎"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return engine

@pytest.fixture(scope="function")
def session(engine):
    """创建数据库会话"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 创建会话
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    yield session
    
    # 清理
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def project_repository(session):
    """项目仓储实例"""
    return ProjectRepository(session)

@pytest.fixture
def use_case_repository(session):
    """用例仓储实例"""
    return UseCaseRepository(session)

@pytest.fixture
def budget_repository(session):
    """预算仓储实例"""
    return BudgetRepository(session)

@pytest.fixture
def budget_usage_repository(session):
    """预算使用仓储实例"""
    return BudgetUsageRepository(session)

@pytest.fixture
def model_repository(session):
    """模型仓储实例"""
    return ModelRepository(session)

@pytest.fixture
def deployment_repository(session):
    """部署仓储实例"""
    return DeploymentRepository(session)

@pytest.fixture
def pricing_repository(session):
    """定价仓储实例"""
    return PricingRepository(session)

@pytest.fixture
def subscription_repository(session):
    """订阅仓储实例"""
    return SubscriptionRepository(session)

@pytest.fixture
def limit_repository(session):
    """限制仓储实例"""
    return LimitRepository(session)

@pytest.fixture
def limit_usage_repository(session):
    """限制使用仓储实例"""
    return LimitUsageRepository(session) 