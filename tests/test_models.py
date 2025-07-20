"""
测试专用模型定义
在测试环境中使用String类型的ID以支持SQLite数据库
"""

import os
from datetime import date, datetime
from sqlalchemy import String, Integer, Float, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List, Optional

# 确保在测试环境中
os.environ['TESTING'] = 'true'

class TestBase(DeclarativeBase):
    """测试基础模型"""
    pass

class TestProjectModel(TestBase):
    """测试项目模型"""
    __tablename__ = 'test_projects'
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    code: Mapped[str] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(String(100))
    updated_by: Mapped[Optional[str]] = mapped_column(String(100))
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # 关系
    use_cases: Mapped[List["TestUseCaseModel"]] = relationship("TestUseCaseModel", back_populates="project")
    subscriptions: Mapped[List["TestSubscriptionModel"]] = relationship("TestSubscriptionModel", back_populates="project")

class TestUseCaseModel(TestBase):
    """测试用例模型"""
    __tablename__ = 'test_use_cases'
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(50), ForeignKey('test_projects.id'))
    name: Mapped[str] = mapped_column(String(100))
    ad_group: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(String(100))
    updated_by: Mapped[Optional[str]] = mapped_column(String(100))
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # 关系
    project: Mapped["TestProjectModel"] = relationship("TestProjectModel", back_populates="use_cases")
    budgets: Mapped[List["TestBudgetModel"]] = relationship("TestBudgetModel", back_populates="use_case")
    subscriptions: Mapped[List["TestSubscriptionModel"]] = relationship("TestSubscriptionModel", back_populates="use_case")

class TestBudgetModel(TestBase):
    """测试预算模型"""
    __tablename__ = 'test_budgets'
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    use_case_id: Mapped[str] = mapped_column(String(50), ForeignKey('test_use_cases.id'))
    currency: Mapped[str] = mapped_column(String(10))
    amount: Mapped[float] = mapped_column(Float)
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(String(100))
    updated_by: Mapped[Optional[str]] = mapped_column(String(100))
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # 关系
    use_case: Mapped["TestUseCaseModel"] = relationship("TestUseCaseModel", back_populates="budgets")

class TestBudgetUsageModel(TestBase):
    """测试预算使用模型"""
    __tablename__ = 'test_budget_usage'
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    use_case_id: Mapped[str] = mapped_column(String(50), ForeignKey('test_use_cases.id'))
    usage_period: Mapped[date] = mapped_column(Date)
    amount: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(String(100))
    updated_by: Mapped[Optional[str]] = mapped_column(String(100))
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

class TestModelModel(TestBase):
    """测试模型模型"""
    __tablename__ = 'test_models'
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[str] = mapped_column(String(50))
    provider: Mapped[str] = mapped_column(String(50))
    input: Mapped[str] = mapped_column(String(50))
    output: Mapped[str] = mapped_column(String(50))
    context_length: Mapped[Optional[int]] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(String(100))
    updated_by: Mapped[Optional[str]] = mapped_column(String(100))
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # 关系
    deployments: Mapped[List["TestDeploymentModel"]] = relationship("TestDeploymentModel", back_populates="model")
    pricing: Mapped[List["TestPricingModel"]] = relationship("TestPricingModel", back_populates="model")
    subscriptions: Mapped[List["TestSubscriptionModel"]] = relationship("TestSubscriptionModel", back_populates="model")

class TestDeploymentModel(TestBase):
    """测试部署模型"""
    __tablename__ = 'test_deployments'
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    model_id: Mapped[str] = mapped_column(String(50), ForeignKey('test_models.id'))
    name: Mapped[str] = mapped_column(String(100))
    endpoint: Mapped[str] = mapped_column(String(255))
    region: Mapped[str] = mapped_column(String(50))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(String(100))
    updated_by: Mapped[Optional[str]] = mapped_column(String(100))
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # 关系
    model: Mapped["TestModelModel"] = relationship("TestModelModel", back_populates="deployments")

class TestPricingModel(TestBase):
    """测试定价模型"""
    __tablename__ = 'test_pricing'
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    model_id: Mapped[str] = mapped_column(String(50), ForeignKey('test_models.id'))
    currency: Mapped[str] = mapped_column(String(10))
    input_token_price_cpm: Mapped[int] = mapped_column(Integer)
    output_token_price_cpm: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(String(100))
    updated_by: Mapped[Optional[str]] = mapped_column(String(100))
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # 关系
    model: Mapped["TestModelModel"] = relationship("TestModelModel", back_populates="pricing")

class TestSubscriptionModel(TestBase):
    """测试订阅模型"""
    __tablename__ = 'test_subscriptions'
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(50), ForeignKey('test_projects.id'))
    use_case_id: Mapped[str] = mapped_column(String(50), ForeignKey('test_use_cases.id'))
    model_id: Mapped[str] = mapped_column(String(50), ForeignKey('test_models.id'))
    subscription_key: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(String(100))
    updated_by: Mapped[Optional[str]] = mapped_column(String(100))
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # 关系
    project: Mapped["TestProjectModel"] = relationship("TestProjectModel", back_populates="subscriptions")
    use_case: Mapped["TestUseCaseModel"] = relationship("TestUseCaseModel", back_populates="subscriptions")
    model: Mapped["TestModelModel"] = relationship("TestModelModel", back_populates="subscriptions")
    limits: Mapped[List["TestLimitModel"]] = relationship("TestLimitModel", back_populates="subscription")

class TestLimitModel(TestBase):
    """测试限制模型"""
    __tablename__ = 'test_limits'
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    subscription_id: Mapped[str] = mapped_column(String(50), ForeignKey('test_subscriptions.id'))
    type: Mapped[str] = mapped_column(String(50))
    scope: Mapped[str] = mapped_column(String(50))
    value: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(String(100))
    updated_by: Mapped[Optional[str]] = mapped_column(String(100))
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # 关系
    subscription: Mapped["TestSubscriptionModel"] = relationship("TestSubscriptionModel", back_populates="limits")

class TestLimitUsageModel(TestBase):
    """测试限制使用模型"""
    __tablename__ = 'test_limit_usage'
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    limit_id: Mapped[str] = mapped_column(String(50), ForeignKey('test_limits.id'))
    scope: Mapped[str] = mapped_column(String(50))
    usage_period: Mapped[datetime] = mapped_column(DateTime)
    value: Mapped[int] = mapped_column(Integer)
    request_id: Mapped[str] = mapped_column(String(100))
    called_by: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)
    created_by: Mapped[Optional[str]] = mapped_column(String(100))
    updated_by: Mapped[Optional[str]] = mapped_column(String(100))
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False) 