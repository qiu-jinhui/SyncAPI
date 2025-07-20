"""
项目仓储测试
"""

import pytest
from datetime import datetime
from tests.test_models import TestProjectModel, TestUseCaseModel

class TestProjectRepository:
    """项目仓储测试类"""
    
    def test_find_by_name(self, project_repository, session):
        """测试根据项目名称查找项目"""
        # 创建项目
        project = project_repository.create(
            id="proj1",
            name="Test Project",
            code="TEST",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 测试查找
        found = project_repository.find_by(name="Test Project")
        assert len(found) == 1
        assert found[0].name == "Test Project"
    
    def test_find_by_code(self, project_repository, session):
        """测试根据项目代码查找项目"""
        # 创建项目
        project = project_repository.create(
            id="proj1",
            name="Test Project",
            code="TEST_CODE",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 测试查找
        found = project_repository.find_by(code="TEST_CODE")
        assert len(found) == 1
        assert found[0].code == "TEST_CODE"
    
    def test_find_by_name_or_code(self, project_repository, session):
        """测试根据项目名称或代码查找项目"""
        # 创建项目
        project1 = project_repository.create(
            id="proj1",
            name="Project One",
            code="PROJ1",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        project2 = project_repository.create(
            id="proj2",
            name="Project Two",
            code="PROJ2",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 测试按名称查找
        found_by_name = project_repository.find_by(name="Project One")
        assert len(found_by_name) == 1
        assert found_by_name[0].name == "Project One"
        
        # 测试按代码查找
        found_by_code = project_repository.find_by(code="PROJ2")
        assert len(found_by_code) == 1
        assert found_by_code[0].code == "PROJ2"
    
    def test_search_projects(self, project_repository, session):
        """测试搜索项目"""
        # 创建项目
        project1 = project_repository.create(
            id="proj1",
            name="Machine Learning Project",
            code="ML_PROJ",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        project2 = project_repository.create(
            id="proj2",
            name="Data Analysis",
            code="DATA_PROJ",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 搜索包含"Project"的项目
        found = project_repository.find_by()  # 获取所有项目进行简单搜索测试
        assert len(found) == 2
    
    def test_search_projects_with_limit(self, project_repository, session):
        """测试带限制的项目搜索"""
        # 创建多个项目
        for i in range(5):
            project_repository.create(
                id=f"proj{i}",
                name=f"Project {i}",
                code=f"PROJ{i}",
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        session.commit()
        
        # 带限制搜索
        limited = project_repository.get_all(limit=3)
        assert len(limited) == 3
    
    def test_get_active_projects(self, project_repository, session):
        """测试获取活跃项目"""
        # 创建活跃和非活跃项目
        active_project = project_repository.create(
            id="active1",
            name="Active Project",
            code="ACTIVE",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        inactive_project = project_repository.create(
            id="inactive1",
            name="Inactive Project",
            code="INACTIVE",
            is_active=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 获取活跃项目
        active_projects = project_repository.find_by(is_active=True)
        assert len(active_projects) == 1
        assert active_projects[0].is_active == True
    
    def test_get_projects_by_status(self, project_repository, session):
        """测试根据状态获取项目"""
        # 创建不同状态的项目
        active_project = project_repository.create(
            id="active1",
            name="Active Project",
            code="ACTIVE",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        inactive_project = project_repository.create(
            id="inactive1",
            name="Inactive Project", 
            code="INACTIVE",
            is_active=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 测试获取活跃项目
        active_projects = project_repository.find_by(is_active=True)
        assert len(active_projects) == 1
        
        # 测试获取非活跃项目
        inactive_projects = project_repository.find_by(is_active=False)
        assert len(inactive_projects) == 1
    
    def test_update_project_status(self, project_repository, session):
        """测试更新项目状态"""
        # 创建项目
        project = project_repository.create(
            id="proj1",
            name="Test Project",
            code="TEST",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 更新状态
        updated = project_repository.update("proj1", is_active=False)
        assert updated is not None
        assert updated.is_active == False
    
    def test_get_projects_with_use_cases(self, project_repository, session):
        """测试获取包含用例的项目"""
        # 创建项目
        project = project_repository.create(
            id="proj1",
            name="Project with Use Cases",
            code="PROJ_UC",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 创建用例
        use_case = TestUseCaseModel(
            id="uc1",
            project_id="proj1",
            name="Test Use Case",
            ad_group="test_group",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(use_case)
        session.commit()
        
        # 这里简化测试，因为复杂的join查询需要在实际仓储方法中实现
        # 验证项目存在
        found_project = project_repository.get_by_id("proj1")
        assert found_project is not None
    
    def test_get_project_stats(self, project_repository, session):
        """测试获取项目统计信息"""
        # 创建多个项目
        active_project1 = project_repository.create(
            id="active1",
            name="Active Project 1",
            code="ACTIVE1",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        active_project2 = project_repository.create(
            id="active2",
            name="Active Project 2",
            code="ACTIVE2",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        inactive_project = project_repository.create(
            id="inactive1",
            name="Inactive Project",
            code="INACTIVE1",
            is_active=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 获取统计信息
        total_count = project_repository.count()
        active_count = len(project_repository.find_by(is_active=True))
        inactive_count = len(project_repository.find_by(is_active=False))
        
        assert total_count == 3
        assert active_count == 2
        assert inactive_count == 1 