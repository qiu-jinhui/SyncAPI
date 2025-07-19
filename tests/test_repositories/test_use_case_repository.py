"""
用例仓储测试
"""

import pytest
from src.models.use_case import UseCase
from src.models.project import Project

class TestUseCaseRepository:
    """用例仓储测试类"""
    
    def test_find_by_name(self, use_case_repository, session):
        """测试根据名称查找用例"""
        # 创建项目和用例
        project = Project(project_name="Test Project", project_code="TEST_PROJ")
        session.add(project)
        session.flush()
        
        use_case = use_case_repository.create(
            use_case_name="Test Use Case",
            ad_group="test_group",
            project_id=project.id
        )
        session.commit()
        
        # 查找
        result = use_case_repository.find_by_name("Test Use Case")
        
        assert result is not None
        assert result.id == use_case.id
        assert result.use_case_name == "Test Use Case"
    
    def test_find_by_project(self, use_case_repository, session):
        """测试根据项目查找用例"""
        # 创建项目和用例
        project1 = Project(project_name="Project 1", project_code="PROJ1")
        project2 = Project(project_name="Project 2", project_code="PROJ2")
        session.add_all([project1, project2])
        session.flush()
        
        use_case1 = use_case_repository.create(
            use_case_name="Use Case 1",
            ad_group="group1",
            project_id=project1.id
        )
        use_case2 = use_case_repository.create(
            use_case_name="Use Case 2",
            ad_group="group2",
            project_id=project1.id
        )
        use_case3 = use_case_repository.create(
            use_case_name="Use Case 3",
            ad_group="group3",
            project_id=project2.id
        )
        session.commit()
        
        # 查找项目1的用例
        results = use_case_repository.find_by_project(project1.id)
        
        assert len(results) == 2
        assert all(uc.project_id == project1.id for uc in results)
    
    def test_find_by_ad_group(self, use_case_repository, session):
        """测试根据广告组查找用例"""
        # 创建项目和用例
        project = Project(project_name="Test Project", project_code="TEST_PROJ")
        session.add(project)
        session.flush()
        
        use_case = use_case_repository.create(
            use_case_name="Test Use Case",
            ad_group="test_group",
            project_id=project.id
        )
        session.commit()
        
        # 查找
        results = use_case_repository.find_by_ad_group("test_group")
        
        assert len(results) == 1
        assert results[0].id == use_case.id
        assert results[0].ad_group == "test_group"
    
    def test_find_by_status(self, use_case_repository, session):
        """测试根据状态查找用例"""
        # 创建项目和用例
        project = Project(project_name="Test Project", project_code="TEST_PROJ")
        session.add(project)
        session.flush()
        
        use_case1 = use_case_repository.create(
            use_case_name="Active Use Case",
            ad_group="group1",
            project_id=project.id,
            status="active"
        )
        use_case2 = use_case_repository.create(
            use_case_name="Inactive Use Case",
            ad_group="group2",
            project_id=project.id,
            status="inactive"
        )
        session.commit()
        
        # 查找活跃用例
        active_results = use_case_repository.find_by_status("active")
        assert len(active_results) == 1
        assert active_results[0].status == "active"
        
        # 查找非活跃用例
        inactive_results = use_case_repository.find_by_status("inactive")
        assert len(inactive_results) == 1
        assert inactive_results[0].status == "inactive"
    
    def test_search_use_cases(self, use_case_repository, session):
        """测试搜索用例"""
        # 创建项目和用例
        project = Project(project_name="Test Project", project_code="TEST_PROJ")
        session.add(project)
        session.flush()
        
        use_case_repository.create(
            use_case_name="Test Use Case",
            ad_group="test_group",
            project_id=project.id
        )
        use_case_repository.create(
            use_case_name="Another Use Case",
            ad_group="another_group",
            project_id=project.id
        )
        session.commit()
        
        # 搜索
        results = use_case_repository.search_use_cases("Test")
        
        assert len(results) == 1
        assert results[0].use_case_name == "Test Use Case"
    
    def test_get_use_case_stats(self, use_case_repository, session):
        """测试获取用例统计信息"""
        # 创建项目和用例
        project = Project(project_name="Test Project", project_code="TEST_PROJ")
        session.add(project)
        session.flush()
        
        use_case_repository.create(
            use_case_name="Use Case 1",
            ad_group="group1",
            project_id=project.id,
            status="active"
        )
        use_case_repository.create(
            use_case_name="Use Case 2",
            ad_group="group2",
            project_id=project.id,
            status="active"
        )
        use_case_repository.create(
            use_case_name="Use Case 3",
            ad_group="group3",
            project_id=project.id,
            status="inactive"
        )
        session.commit()
        
        # 获取统计信息
        stats = use_case_repository.get_use_case_stats()
        
        assert stats['total_use_cases'] == 3
        assert stats['active_use_cases'] == 2
        assert stats['inactive_use_cases'] == 1 