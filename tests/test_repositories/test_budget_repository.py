"""
预算仓储测试
"""

import pytest
from datetime import datetime, timezone
from src.models.budget import UseCaseBudget, UseCaseBudgetUsage
from src.models.use_case import UseCase
from src.models.project import Project

class TestBudgetRepository:
    """预算仓储测试类"""
    
    def test_find_by_use_case(self, budget_repository, session):
        """测试根据用例查找预算"""
        # 创建项目、用例和预算
        project = Project(project_name="Test Project", project_code="TEST_PROJ")
        use_case = UseCase(use_case_name="Test Use Case", ad_group="test", project_id=project.id)
        session.add_all([project, use_case])
        session.flush()
        
        budget = budget_repository.create(
            use_case_id=use_case.id,
            amount=1000.0,
            currency="USD",
            period="monthly"
        )
        session.commit()
        
        # 查找
        results = budget_repository.find_by_use_case(use_case.id)
        
        assert len(results) == 1
        assert results[0].use_case_id == use_case.id
    
    def test_find_by_currency(self, budget_repository, session):
        """测试根据货币查找预算"""
        # 创建项目、用例和预算
        project = Project(project_name="Test Project", project_code="TEST_PROJ")
        use_case = UseCase(use_case_name="Test Use Case", ad_group="test", project_id=project.id)
        session.add_all([project, use_case])
        session.flush()
        
        budget = budget_repository.create(
            use_case_id=use_case.id,
            amount=1000.0,
            currency="USD",
            period="monthly"
        )
        session.commit()
        
        # 查找
        results = budget_repository.find_by_currency("USD")
        
        assert len(results) == 1
        assert results[0].currency == "USD"
    
    def test_find_by_project(self, budget_repository, session):
        """测试根据项目查找预算"""
        # 创建项目、用例和预算
        project1 = Project(project_name="Project 1", project_code="PROJ1")
        project2 = Project(project_name="Project 2", project_code="PROJ2")
        use_case1 = UseCase(use_case_name="Use Case 1", ad_group="test1", project_id=project1.id)
        use_case2 = UseCase(use_case_name="Use Case 2", ad_group="test2", project_id=project2.id)
        session.add_all([project1, project2, use_case1, use_case2])
        session.flush()
        
        budget = budget_repository.create(
            use_case_id=use_case1.id,
            amount=1000.0,
            currency="USD",
            period="monthly"
        )
        session.commit()
        
        # 查找
        results = budget_repository.find_by_project(project1.id)
        
        assert len(results) == 1
        assert results[0].use_case.project_id == project1.id
    
    def test_find_by_date_range(self, budget_repository, session):
        """测试根据日期范围查找预算"""
        # 创建项目、用例和预算
        project = Project(project_name="Test Project", project_code="TEST_PROJ")
        use_case = UseCase(use_case_name="Test Use Case", ad_group="test", project_id=project.id)
        session.add_all([project, use_case])
        session.flush()
        
        budget = budget_repository.create(
            use_case_id=use_case.id,
            amount=1000.0,
            currency="USD",
            period="monthly",
            start_date=datetime.now(timezone.utc)
        )
        session.commit()
        
        # 查找
        start_date = datetime.now(timezone.utc)
        end_date = datetime.now(timezone.utc)
        results = budget_repository.find_by_date_range(start_date, end_date)
        
        assert len(results) >= 1

class TestBudgetUsageRepository:
    """预算使用仓储测试类"""
    
    def test_find_by_use_case(self, budget_usage_repository, session):
        """测试根据用例查找预算使用"""
        # 创建项目、用例和预算使用
        project = Project(project_name="Test Project", project_code="TEST_PROJ")
        use_case = UseCase(use_case_name="Test Use Case", ad_group="test", project_id=project.id)
        session.add_all([project, use_case])
        session.flush()
        
        usage = budget_usage_repository.create(
            use_case_id=use_case.id,
            amount_used=100.0,
            currency="USD",
            usage_date=datetime.now(timezone.utc)
        )
        session.commit()
        
        # 查找
        results = budget_usage_repository.find_by_use_case(use_case.id)
        
        assert len(results) == 1
        assert results[0].use_case_id == use_case.id
    
    def test_find_by_date_range(self, budget_usage_repository, session):
        """测试根据日期范围查找预算使用"""
        # 创建项目、用例和预算使用
        project = Project(project_name="Test Project", project_code="TEST_PROJ")
        use_case = UseCase(use_case_name="Test Use Case", ad_group="test", project_id=project.id)
        session.add_all([project, use_case])
        session.flush()
        
        usage = budget_usage_repository.create(
            use_case_id=use_case.id,
            amount_used=100.0,
            currency="USD",
            usage_date=datetime.now(timezone.utc)
        )
        session.commit()
        
        # 查找
        start_date = datetime.now(timezone.utc)
        end_date = datetime.now(timezone.utc)
        results = budget_usage_repository.find_by_date_range(start_date, end_date)
        
        assert len(results) >= 1
    
    def test_get_usage_stats(self, budget_usage_repository, session):
        """测试获取使用统计信息"""
        # 创建项目、用例和预算使用
        project = Project(project_name="Test Project", project_code="TEST_PROJ")
        use_case = UseCase(use_case_name="Test Use Case", ad_group="test", project_id=project.id)
        session.add_all([project, use_case])
        session.flush()
        
        budget_usage_repository.create(
            use_case_id=use_case.id,
            amount_used=100.0,
            currency="USD",
            usage_date=datetime.now(timezone.utc)
        )
        budget_usage_repository.create(
            use_case_id=use_case.id,
            amount_used=200.0,
            currency="USD",
            usage_date=datetime.now(timezone.utc)
        )
        session.commit()
        
        # 获取统计信息
        stats = budget_usage_repository.get_usage_stats()
        
        assert stats['total_usage'] == 2
        assert stats['total_amount_used'] == 300.0 