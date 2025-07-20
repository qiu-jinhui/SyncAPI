"""
基础仓储测试
"""

import pytest
from datetime import datetime
from tests.test_models import TestProjectModel

class TestBaseRepository:
    """基础仓储测试类"""
    
    def test_create(self, base_repository, session):
        """测试创建记录"""
        project = base_repository.create(
            id="test1",
            name="Test Project",
            code="TEST",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert project.id == "test1"
        assert project.name == "Test Project"
    
    def test_get_by_id(self, base_repository, session):
        """测试根据ID获取记录"""
        # 创建记录
        project = base_repository.create(
            id="test1",
            name="Test Project",
            code="TEST",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 获取记录
        found = base_repository.get_by_id("test1")
        assert found is not None
        assert found.id == "test1"
    
    def test_get_by_id_not_found(self, base_repository, session):
        """测试获取不存在的记录"""
        found = base_repository.get_by_id("nonexistent")
        assert found is None
    
    def test_get_all(self, base_repository, session):
        """测试获取所有记录"""
        # 创建多个记录
        base_repository.create(
            id="test1",
            name="Project 1",
            code="TEST1",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        base_repository.create(
            id="test2",
            name="Project 2",
            code="TEST2",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 获取所有记录
        all_projects = base_repository.get_all()
        assert len(all_projects) == 2
    
    def test_get_all_with_limit(self, base_repository, session):
        """测试带限制的获取所有记录"""
        # 创建多个记录
        for i in range(5):
            base_repository.create(
                id=f"test{i}",
                name=f"Project {i}",
                code=f"TEST{i}",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        session.commit()
        
        # 带限制获取
        limited = base_repository.get_all(limit=3)
        assert len(limited) == 3
    
    def test_update(self, base_repository, session):
        """测试更新记录"""
        # 创建记录
        project = base_repository.create(
            id="test1",
            name="Original Name",
            code="TEST",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 更新记录
        updated = base_repository.update("test1", name="Updated Name")
        assert updated is not None
        assert updated.name == "Updated Name"
    
    def test_update_not_found(self, base_repository, session):
        """测试更新不存在的记录"""
        updated = base_repository.update("nonexistent", name="New Name")
        assert updated is None
    
    def test_delete(self, base_repository, session):
        """测试删除记录"""
        # 创建记录
        base_repository.create(
            id="test1",
            name="Test Project",
            code="TEST",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 删除记录
        deleted = base_repository.delete("test1")
        assert deleted is True
        
        # 验证删除
        found = base_repository.get_by_id("test1")
        assert found is None
    
    def test_delete_not_found(self, base_repository, session):
        """测试删除不存在的记录"""
        deleted = base_repository.delete("nonexistent")
        assert deleted is False
    
    def test_count(self, base_repository, session):
        """测试计数"""
        # 创建记录
        base_repository.create(
            id="test1",
            name="Project 1",
            code="TEST1",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        base_repository.create(
            id="test2",
            name="Project 2",
            code="TEST2",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        count = base_repository.count()
        assert count == 2
    
    def test_exists(self, base_repository, session):
        """测试检查存在"""
        # 创建记录
        base_repository.create(
            id="test1",
            name="Test Project",
            code="TEST",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 检查存在
        exists = base_repository.exists("test1")
        assert exists is True
        
        # 检查不存在
        not_exists = base_repository.exists("nonexistent")
        assert not_exists is False
    
    def test_find_by(self, base_repository, session):
        """测试条件查找"""
        # 创建记录
        base_repository.create(
            id="test1",
            name="Test Project",
            code="TEST",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        base_repository.create(
            id="test2",
            name="Another Project",
            code="OTHER",
            is_active=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 条件查找
        active_projects = base_repository.find_by(is_active=True)
        assert len(active_projects) == 1
        assert active_projects[0].is_active is True
    
    def test_find_one_by(self, base_repository, session):
        """测试查找单个记录"""
        # 创建记录
        base_repository.create(
            id="test1",
            name="Unique Project",
            code="UNIQUE",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 查找单个
        found = base_repository.find_one_by(code="UNIQUE")
        assert found is not None
        assert found.code == "UNIQUE"
    
    def test_find_one_by_not_found(self, base_repository, session):
        """测试查找不存在的记录"""
        found = base_repository.find_one_by(code="NONEXISTENT")
        assert found is None
    
    def test_bulk_create(self, base_repository, session):
        """测试批量创建"""
        data = [
            {
                "id": "bulk1",
                "name": "Bulk Project 1",
                "code": "BULK1",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": "bulk2",
                "name": "Bulk Project 2",
                "code": "BULK2",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]
        
        created = base_repository.bulk_create(data)
        assert len(created) == 2
        assert created[0].name == "Bulk Project 1"
        assert created[1].name == "Bulk Project 2"
    
    def test_bulk_update(self, base_repository, session):
        """测试批量更新"""
        # 先创建记录
        base_repository.create(
            id="test1",
            name="Original 1",
            code="TEST1",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        base_repository.create(
            id="test2",
            name="Original 2",
            code="TEST2",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 批量更新
        updates = [
            {"id": "test1", "name": "Updated 1"},
            {"id": "test2", "name": "Updated 2"}
        ]
        
        updated = base_repository.bulk_update(updates)
        assert len(updated) == 2
        assert updated[0].name == "Updated 1"
        assert updated[1].name == "Updated 2"
    
    def test_bulk_delete(self, base_repository, session):
        """测试批量删除"""
        # 先创建记录
        base_repository.create(
            id="test1",
            name="To Delete 1",
            code="DEL1",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        base_repository.create(
            id="test2",
            name="To Delete 2",
            code="DEL2",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.commit()
        
        # 批量删除
        deleted_count = base_repository.bulk_delete(["test1", "test2"])
        assert deleted_count == 2
        
        # 验证删除
        assert base_repository.get_by_id("test1") is None
        assert base_repository.get_by_id("test2") is None 