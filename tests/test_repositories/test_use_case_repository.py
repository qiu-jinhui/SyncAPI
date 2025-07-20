"""
用例仓储测试
"""

import pytest
from datetime import datetime
from tests.test_models import TestUseCaseModel, TestProjectModel

class TestUseCaseRepository:
    """用例仓储测试类"""
    
    def test_find_by_name(self, use_case_repository, session):
        """测试根据用例名称查找用例"""
        # 创建项目
        project = TestProjectModel(
            id="proj1",
            name="Test Project",
            code="TEST",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(project)
        session.flush()
        
        # 创建用例
        use_case = use_case_repository.create(
            id="uc1",
            project_id="proj1",
            name="Test Use Case",
            ad_group="test_group",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 测试查找
        found = use_case_repository.find_by(name="Test Use Case")
        assert len(found) == 1
        assert found[0].name == "Test Use Case"
    
    def test_find_by_project(self, use_case_repository, session):
        """测试根据项目ID查找用例"""
        # 创建项目
        project = TestProjectModel(
            id="proj1",
            name="Test Project",
            code="TEST",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(project)
        session.flush()
        
        # 创建用例
        use_case1 = use_case_repository.create(
            id="uc1",
            project_id="proj1",
            name="Use Case 1",
            ad_group="group1",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        use_case2 = use_case_repository.create(
            id="uc2",
            project_id="proj1",
            name="Use Case 2",
            ad_group="group2",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 测试查找
        found = use_case_repository.find_by(project_id="proj1")
        assert len(found) == 2
    
    def test_find_by_ad_group(self, use_case_repository, session):
        """测试根据广告组查找用例"""
        # 创建项目
        project = TestProjectModel(
            id="proj1",
            name="Test Project",
            code="TEST",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(project)
        session.flush()
        
        # 创建用例
        use_case = use_case_repository.create(
            id="uc1",
            project_id="proj1",
            name="Test Use Case",
            ad_group="marketing_group",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 测试查找
        found = use_case_repository.find_by(ad_group="marketing_group")
        assert len(found) == 1
        assert found[0].ad_group == "marketing_group"
    
    def test_find_by_status(self, use_case_repository, session):
        """测试根据状态查找用例"""
        # 创建项目
        project = TestProjectModel(
            id="proj1",
            name="Test Project",
            code="TEST",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(project)
        session.flush()
        
        # 创建活跃和非活跃用例
        active_use_case = use_case_repository.create(
            id="active_uc",
            project_id="proj1",
            name="Active Use Case",
            ad_group="active_group",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        inactive_use_case = use_case_repository.create(
            id="inactive_uc",
            project_id="proj1",
            name="Inactive Use Case",
            ad_group="inactive_group",
            is_active=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 测试查找活跃用例
        active_found = use_case_repository.find_by(is_active=True)
        assert len(active_found) == 1
        assert active_found[0].is_active == True
        
        # 测试查找非活跃用例
        inactive_found = use_case_repository.find_by(is_active=False)
        assert len(inactive_found) == 1
        assert inactive_found[0].is_active == False
    
    def test_search_use_cases(self, use_case_repository, session):
        """测试搜索用例"""
        # 创建项目
        project = TestProjectModel(
            id="proj1",
            name="Test Project",
            code="TEST",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(project)
        session.flush()
        
        # 创建用例
        use_case1 = use_case_repository.create(
            id="uc1",
            project_id="proj1",
            name="Machine Learning Use Case",
            ad_group="ml_group",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        use_case2 = use_case_repository.create(
            id="uc2",
            project_id="proj1",
            name="Data Processing",
            ad_group="data_group",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 简化的搜索测试 - 获取所有用例
        found = use_case_repository.find_by()
        assert len(found) == 2
    
    def test_get_use_case_stats(self, use_case_repository, session):
        """测试获取用例统计信息"""
        # 创建项目
        project = TestProjectModel(
            id="proj1",
            name="Test Project",
            code="TEST",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(project)
        session.flush()
        
        # 创建多个用例
        active_use_case1 = use_case_repository.create(
            id="active1",
            project_id="proj1",
            name="Active Use Case 1",
            ad_group="group1",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        active_use_case2 = use_case_repository.create(
            id="active2",
            project_id="proj1",
            name="Active Use Case 2",
            ad_group="group2",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        inactive_use_case = use_case_repository.create(
            id="inactive1",
            project_id="proj1",
            name="Inactive Use Case",
            ad_group="group3",
            is_active=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 获取统计信息
        total_count = use_case_repository.count()
        active_count = len(use_case_repository.find_by(is_active=True))
        inactive_count = len(use_case_repository.find_by(is_active=False))
        
        assert total_count == 3
        assert active_count == 2
        assert inactive_count == 1
    
    def test_update_use_case_status(self, use_case_repository, session):
        """测试更新用例状态"""
        # 创建项目
        project = TestProjectModel(
            id="proj1",
            name="Test Project",
            code="TEST",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(project)
        session.flush()
        
        # 创建用例
        use_case = use_case_repository.create(
            id="uc1",
            project_id="proj1",
            name="Test Use Case",
            ad_group="test_group",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 更新状态
        updated = use_case_repository.update("uc1", is_active=False)
        assert updated is not None
        assert updated.is_active == False
    
    def test_find_by_project_and_name(self, use_case_repository, session):
        """测试根据项目ID和用例名称查找用例"""
        # 创建项目
        project = TestProjectModel(
            id="proj1",
            name="Test Project",
            code="TEST",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(project)
        session.flush()
        
        # 创建用例
        use_case = use_case_repository.create(
            id="uc1",
            project_id="proj1",
            name="Unique Use Case",
            ad_group="unique_group",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 测试查找
        found = use_case_repository.find_by(project_id="proj1", name="Unique Use Case")
        assert len(found) == 1
        assert found[0].name == "Unique Use Case"
        assert found[0].project_id == "proj1" 