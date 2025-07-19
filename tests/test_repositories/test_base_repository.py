"""
基础仓储类测试
"""

import uuid
import uuid
import pytest
from src.repositories.base_repository import BaseRepository
from src.models.project import Project

class TestBaseRepository:
    """基础仓储类测试"""
    
    def test_create(self, session):
        """测试创建记录"""
        repo = BaseRepository(Project, session)
        
        project = repo.create(
            project_name="Test Project",
            project_code="TEST_PROJ"
        )
        
        assert project is not None
        assert project.id is not None
        assert project.project_name == "Test Project"
        assert project.project_code == "TEST_PROJ"
    
    def test_get_by_id(self, session):
        """测试根据ID获取记录"""
        repo = BaseRepository(Project, session)
        
        # 创建记录
        project = repo.create(
            project_name="Test Project",
            project_code="TEST_PROJ"
        )
        session.commit()
        
        # 获取记录
        retrieved = repo.get_by_id(project.id)
        
        assert retrieved is not None
        assert retrieved.id == project.id
        assert retrieved.project_name == "Test Project"
    
    def test_get_by_id_not_found(self, session):
        """测试根据ID获取不存在的记录"""
        repo = BaseRepository(Project, session)
        
        # 使用有效的UUID格式
        non_existent_id = str(uuid.uuid4())
        result = repo.get_by_id(non_existent_id)
        
        assert result is None
    
    def test_get_all(self, session):
        """测试获取所有记录"""
        repo = BaseRepository(Project, session)
        
        # 创建多个记录
        repo.create(project_name="Project 1", project_code="PROJ1")
        repo.create(project_name="Project 2", project_code="PROJ2")
        repo.create(project_name="Project 3", project_code="PROJ3")
        session.commit()
        
        # 获取所有记录
        projects = repo.get_all()
        
        assert len(projects) == 3
        assert all(isinstance(p, Project) for p in projects)
    
    def test_get_all_with_limit(self, session):
        """测试获取所有记录（带限制）"""
        repo = BaseRepository(Project, session)
        
        # 创建多个记录
        repo.create(project_name="Project 1", project_code="PROJ1")
        repo.create(project_name="Project 2", project_code="PROJ2")
        repo.create(project_name="Project 3", project_code="PROJ3")
        session.commit()
        
        # 获取前2个记录
        projects = repo.get_all(limit=2)
        
        assert len(projects) == 2
    
    def test_update(self, session):
        """测试更新记录"""
        repo = BaseRepository(Project, session)
        
        # 创建记录
        project = repo.create(
            project_name="Test Project",
            project_code="TEST_PROJ"
        )
        session.commit()
        
        # 更新记录
        updated = repo.update(
            project.id,
            project_name="Updated Project",
            project_code="UPDATED_PROJ"
        )
        
        assert updated is not None
        assert updated.project_name == "Updated Project"
        assert updated.project_code == "UPDATED_PROJ"
    
    def test_update_not_found(self, session):
        """测试更新不存在的记录"""
        repo = BaseRepository(Project, session)
        
        # 使用有效的UUID格式
        non_existent_id = str(uuid.uuid4())
        result = repo.update(non_existent_id, project_name="Updated")
        
        assert result is None
    
    def test_delete(self, session):
        """测试删除记录"""
        repo = BaseRepository(Project, session)
        
        # 创建记录
        project = repo.create(
            project_name="Test Project",
            project_code="TEST_PROJ"
        )
        session.commit()
        
        # 删除记录
        result = repo.delete(project.id)
        
        assert result is True
        
        # 验证记录已被删除
        retrieved = repo.get_by_id(project.id)
        assert retrieved is None
    
    def test_delete_not_found(self, session):
        """测试删除不存在的记录"""
        repo = BaseRepository(Project, session)
        
        # 使用有效的UUID格式
        non_existent_id = str(uuid.uuid4())
        result = repo.delete(non_existent_id)
        
        assert result is False
    
    def test_count(self, session):
        """测试计数"""
        repo = BaseRepository(Project, session)
        
        # 创建多个记录
        repo.create(project_name="Project 1", project_code="PROJ1")
        repo.create(project_name="Project 2", project_code="PROJ2")
        session.commit()
        
        count = repo.count()
        
        assert count == 2
    
    def test_exists(self, session):
        """测试记录存在性检查"""
        repo = BaseRepository(Project, session)
        
        # 创建记录
        project = repo.create(
            project_name="Test Project",
            project_code="TEST_PROJ"
        )
        session.commit()
        
        # 检查存在
        assert repo.exists(project.id) is True
        
        # 使用有效的UUID格式
        non_existent_id = str(uuid.uuid4())
        assert repo.exists(non_existent_id) is False
    
    def test_find_by(self, session):
        """测试根据条件查找"""
        repo = BaseRepository(Project, session)
        
        # 创建记录
        repo.create(project_name="Test Project", project_code="TEST_PROJ")
        repo.create(project_name="Another Project", project_code="ANOTHER_PROJ")
        session.commit()
        
        # 查找
        projects = repo.find_by(project_name="Test Project")
        
        assert len(projects) == 1
        assert projects[0].project_name == "Test Project"
    
    def test_find_one_by(self, session):
        """测试根据条件查找单条记录"""
        repo = BaseRepository(Project, session)
        
        # 创建记录
        project = repo.create(project_name="Test Project", project_code="TEST_PROJ")
        session.commit()
        
        # 查找
        result = repo.find_one_by(project_name="Test Project")
        
        assert result is not None
        assert result.id == project.id
    
    def test_find_one_by_not_found(self, session):
        """测试根据条件查找不存在的记录"""
        repo = BaseRepository(Project, session)
        
        result = repo.find_one_by(project_name="Non-existent")
        
        assert result is None
    
    def test_bulk_create(self, session):
        """测试批量创建"""
        repo = BaseRepository(Project, session)
        
        instances_data = [
            {"project_name": "Project 1", "project_code": "PROJ1"},
            {"project_name": "Project 2", "project_code": "PROJ2"},
            {"project_name": "Project 3", "project_code": "PROJ3"}
        ]
        
        created = repo.bulk_create(instances_data)
        
        assert len(created) == 3
        assert all(isinstance(p, Project) for p in created)
        assert all(p.id is not None for p in created)
    
    def test_bulk_update(self, session):
        """测试批量更新"""
        repo = BaseRepository(Project, session)
        
        # 创建记录
        p1 = repo.create(project_name="Project 1", project_code="PROJ1")
        p2 = repo.create(project_name="Project 2", project_code="PROJ2")
        session.commit()
        
        # 批量更新
        updates = [
            {"id": p1.id, "project_name": "Updated 1"},
            {"id": p2.id, "project_name": "Updated 2"}
        ]
        
        updated = repo.bulk_update(updates)
        
        assert len(updated) == 2
        assert updated[0].project_name == "Updated 1"
        assert updated[1].project_name == "Updated 2"
    
    def test_bulk_delete(self, session):
        """测试批量删除"""
        repo = BaseRepository(Project, session)
        
        # 创建记录
        p1 = repo.create(project_name="Project 1", project_code="PROJ1")
        p2 = repo.create(project_name="Project 2", project_code="PROJ2")
        session.commit()
        
        # 使用有效的UUID格式
        non_existent_id = str(uuid.uuid4())
        deleted_count = repo.bulk_delete([p1.id, p2.id, non_existent_id])
        
        assert deleted_count == 2
        
        # 验证记录已被删除
        assert repo.get_by_id(p1.id) is None
        assert repo.get_by_id(p2.id) is None 