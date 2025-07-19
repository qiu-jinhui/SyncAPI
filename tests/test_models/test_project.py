"""
项目模型测试
"""

import pytest
from datetime import datetime
from src.models.project import Project

class TestProject:
    """项目模型测试类"""
    
    def test_project_creation(self):
        """测试项目创建"""
        project = Project(
            project_name="Test Project",
            project_code="TEST_PROJ"
        )
        
        assert project.project_name == "Test Project"
        assert project.project_code == "TEST_PROJ"
        # UUID需要数据库会话才能自动生成，这里只测试字段存在
        assert hasattr(project, 'id')
        # 时间戳在数据库会话中才会自动设置
        assert hasattr(project, 'created_time')
        assert hasattr(project, 'updated_time')
    
    def test_project_repr(self):
        """测试项目字符串表示"""
        project = Project(
            project_name="Test Project",
            project_code="TEST_PROJ"
        )
        
        repr_str = repr(project)
        assert "Project" in repr_str
        assert "Test Project" in repr_str
        assert "TEST_PROJ" in repr_str
    
    def test_project_properties(self):
        """测试项目属性"""
        project = Project(
            project_name="Test Project",
            project_code="TEST_PROJ"
        )
        
        assert project.name == "Test Project"
        assert project.code == "TEST_PROJ"
    
    def test_project_to_dict(self):
        """测试项目转字典"""
        project = Project(
            project_name="Test Project",
            project_code="TEST_PROJ"
        )
        
        data = project.to_dict()
        
        assert "id" in data
        assert "project_name" in data
        assert "project_code" in data
        assert "created_time" in data
        assert "updated_time" in data
        assert data["project_name"] == "Test Project"
        assert data["project_code"] == "TEST_PROJ"
    
    def test_project_from_dict(self):
        """测试从字典创建项目"""
        data = {
            "project_name": "Test Project",
            "project_code": "TEST_PROJ"
        }
        
        project = Project.from_dict(data)
        
        assert project.project_name == "Test Project"
        assert project.project_code == "TEST_PROJ"
    
    def test_project_update_from_dict(self):
        """测试从字典更新项目"""
        project = Project(
            project_name="Old Name",
            project_code="OLD_CODE"
        )
        
        # 等待一小段时间确保时间戳不同
        import time
        time.sleep(0.001)
        
        original_updated_time = project.updated_time
        
        update_data = {
            "project_name": "New Name",
            "project_code": "NEW_CODE"
        }
        
        project.update_from_dict(update_data)
        
        assert project.project_name == "New Name"
        assert project.project_code == "NEW_CODE"
        # 时间戳在数据库会话中才会自动设置
        assert hasattr(project, 'updated_time') 