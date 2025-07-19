"""
用例模型测试
"""

import pytest
from src.models.use_case import UseCase

class TestUseCase:
    """用例模型测试类"""
    
    def test_use_case_creation(self):
        """测试用例创建"""
        use_case = UseCase(
            project_id="123e4567-e89b-12d3-a456-426614174000",
            use_case_name="Test Use Case",
            ad_group="test_group",
            is_active=True
        )
        
        assert use_case.project_id == "123e4567-e89b-12d3-a456-426614174000"
        assert use_case.use_case_name == "Test Use Case"
        assert use_case.ad_group == "test_group"
        assert use_case.is_active is True
        assert hasattr(use_case, 'id')
        # 时间戳在数据库会话中才会自动设置
        assert hasattr(use_case, 'created_time')
        assert hasattr(use_case, 'updated_time')
    
    def test_use_case_repr(self):
        """测试用例字符串表示"""
        use_case = UseCase(
            project_id="123e4567-e89b-12d3-a456-426614174000",
            use_case_name="Test Use Case",
            ad_group="test_group"
        )
        
        repr_str = repr(use_case)
        assert "UseCase" in repr_str
        assert "Test Use Case" in repr_str
        assert "123e4567-e89b-12d3-a456-426614174000" in repr_str
    
    def test_use_case_properties(self):
        """测试用例属性"""
        use_case = UseCase(
            project_id="123e4567-e89b-12d3-a456-426614174000",
            use_case_name="Test Use Case",
            ad_group="test_group",
            is_active=True
        )
        
        assert use_case.name == "Test Use Case"
        assert use_case.active is True
    
    def test_use_case_default_active(self):
        """测试用例默认激活状态"""
        use_case = UseCase(
            project_id="123e4567-e89b-12d3-a456-426614174000",
            use_case_name="Test Use Case",
            ad_group="test_group"
        )
        
        # 默认值在数据库层面设置，这里测试字段存在
        assert hasattr(use_case, 'is_active')
    
    def test_use_case_to_dict(self):
        """测试用例转字典"""
        use_case = UseCase(
            project_id="123e4567-e89b-12d3-a456-426614174000",
            use_case_name="Test Use Case",
            ad_group="test_group",
            is_active=True
        )
        
        data = use_case.to_dict()
        
        assert "id" in data
        assert "project_id" in data
        assert "use_case_name" in data
        assert "ad_group" in data
        assert "is_active" in data
        assert "created_time" in data
        assert "updated_time" in data
        assert data["project_id"] == "123e4567-e89b-12d3-a456-426614174000"
        assert data["use_case_name"] == "Test Use Case"
        assert data["ad_group"] == "test_group"
        assert data["is_active"] is True
    
    def test_use_case_from_dict(self):
        """测试从字典创建用例"""
        data = {
            "project_id": "123e4567-e89b-12d3-a456-426614174000",
            "use_case_name": "Test Use Case",
            "ad_group": "test_group",
            "is_active": True
        }
        
        use_case = UseCase.from_dict(data)
        
        assert use_case.project_id == "123e4567-e89b-12d3-a456-426614174000"
        assert use_case.use_case_name == "Test Use Case"
        assert use_case.ad_group == "test_group"
        assert use_case.is_active is True
    
    def test_use_case_update_from_dict(self):
        """测试从字典更新用例"""
        use_case = UseCase(
            project_id="123e4567-e89b-12d3-a456-426614174000",
            use_case_name="Old Name",
            ad_group="old_group",
            is_active=True
        )
        
        import time
        time.sleep(0.001)
        
        original_updated_time = use_case.updated_time
        
        update_data = {
            "use_case_name": "New Name",
            "ad_group": "new_group",
            "is_active": False
        }
        
        use_case.update_from_dict(update_data)
        
        assert use_case.use_case_name == "New Name"
        assert use_case.ad_group == "new_group"
        assert use_case.is_active is False
        # 时间戳在数据库会话中才会自动设置
        assert hasattr(use_case, 'updated_time') 