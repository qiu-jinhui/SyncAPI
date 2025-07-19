"""
项目仓储测试
"""

import pytest
from src.models.project import Project
from src.models.use_case import UseCase

class TestProjectRepository:
    """项目仓储测试类"""
    
    def test_find_by_name(self, project_repository, session):
        """测试根据名称查找项目"""
        # 创建项目
        project = project_repository.create(
            project_name="Test Project",
            project_code="TEST_PROJ"
        )
        session.commit()
        
        # 查找
        result = project_repository.find_by_name("Test Project")
        
        assert result is not None
        assert result.id == project.id
        assert result.project_name == "Test Project"
    
    def test_find_by_code(self, project_repository, session):
        """测试根据代码查找项目"""
        # 创建项目
        project = project_repository.create(
            project_name="Test Project",
            project_code="TEST_PROJ"
        )
        session.commit()
        
        # 查找
        result = project_repository.find_by_code("TEST_PROJ")
        
        assert result is not None
        assert result.id == project.id
        assert result.project_code == "TEST_PROJ"
    
    def test_find_by_name_or_code(self, project_repository, session):
        """测试根据名称或代码查找项目"""
        # 创建项目
        project = project_repository.create(
            project_name="Test Project",
            project_code="TEST_PROJ"
        )
        session.commit()
        
        # 用名称查找
        result1 = project_repository.find_by_name_or_code("Test Project")
        assert result1 is not None
        assert result1.id == project.id
        
        # 用代码查找
        result2 = project_repository.find_by_name_or_code("TEST_PROJ")
        assert result2 is not None
        assert result2.id == project.id
    
    def test_search_projects(self, project_repository, session):
        """测试搜索项目"""
        # 创建项目
        project_repository.create(project_name="Test Project", project_code="TEST_PROJ")
        project_repository.create(project_name="Another Project", project_code="ANOTHER_PROJ")
        project_repository.create(project_name="Different Name", project_code="DIFF_CODE")
        session.commit()
        
        # 搜索
        results = project_repository.search_projects("Test")
        
        assert len(results) == 1
        assert results[0].project_name == "Test Project"
    
    def test_search_projects_with_limit(self, project_repository, session):
        """测试搜索项目（带限制）"""
        # 创建项目
        project_repository.create(project_name="Test Project 1", project_code="TEST1")
        project_repository.create(project_name="Test Project 2", project_code="TEST2")
        project_repository.create(project_name="Test Project 3", project_code="TEST3")
        session.commit()
        
        # 搜索（限制2个）
        results = project_repository.search_projects("Test", limit=2)
        
        assert len(results) == 2
    
    def test_get_active_projects(self, project_repository, session):
        """测试获取活跃项目"""
        # 创建项目
        project_repository.create(project_name="Active Project", project_code="ACTIVE", is_active=True)
        project_repository.create(project_name="Inactive Project", project_code="INACTIVE", is_active=False)
        session.commit()
        
        # 获取活跃项目
        results = project_repository.get_active_projects()
        
        assert len(results) == 1
        assert results[0].project_name == "Active Project"
    
    def test_get_projects_by_status(self, project_repository, session):
        """测试根据状态获取项目"""
        # 创建项目
        project_repository.create(project_name="Active Project", project_code="ACTIVE", is_active=True)
        project_repository.create(project_name="Inactive Project", project_code="INACTIVE", is_active=False)
        session.commit()
        
        # 获取活跃项目
        active_results = project_repository.get_projects_by_status(True)
        assert len(active_results) == 1
        assert active_results[0].project_name == "Active Project"
        
        # 获取非活跃项目
        inactive_results = project_repository.get_projects_by_status(False)
        assert len(inactive_results) == 1
        assert inactive_results[0].project_name == "Inactive Project"
    
    def test_update_project_status(self, project_repository, session):
        """测试更新项目状态"""
        # 创建项目
        project = project_repository.create(
            project_name="Test Project",
            project_code="TEST_PROJ",
            is_active=True
        )
        session.commit()
        
        # 更新状态
        updated = project_repository.update_project_status(project.id, False)
        
        assert updated is not None
        assert updated.is_active is False
    
    def test_get_projects_with_use_cases(self, project_repository, session):
        """测试获取包含用例的项目"""
        # 创建项目和用例
        project = project_repository.create(project_name="Test Project", project_code="TEST_PROJ")
        use_case = UseCase(project_id=project.id, use_case_name="Test Use Case", ad_group="test")
        session.add(use_case)
        session.commit()
        
        # 获取包含用例的项目
        results = project_repository.get_projects_with_use_cases()
        
        assert len(results) == 1
        assert results[0].id == project.id
    
    def test_get_project_stats(self, project_repository, session):
        """测试获取项目统计信息"""
        # 创建项目
        project_repository.create(project_name="Active Project", project_code="ACTIVE", is_active=True)
        project_repository.create(project_name="Inactive Project", project_code="INACTIVE", is_active=False)
        project_repository.create(project_name="Another Active", project_code="ACTIVE2", is_active=True)
        session.commit()
        
        # 获取统计信息
        stats = project_repository.get_project_stats()
        
        assert stats['total_projects'] == 3
        assert stats['active_projects'] == 2
        assert stats['inactive_projects'] == 1 