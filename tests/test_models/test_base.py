"""
基础模型测试
"""

import pytest
from datetime import datetime, timezone
from src.models.base import BaseModel

class TestBaseModel:
    """基础模型测试类"""
    
    def test_base_model_creation(self):
        """测试基础模型创建"""
        # 创建一个简单的测试类
        class TestModel1(BaseModel):
            __abstract__ = False
            test_field = None
        
        model = TestModel1()
        
        assert hasattr(model, 'id')
        assert hasattr(model, 'created_time')
        assert hasattr(model, 'updated_time')
        # 时间戳在数据库会话中才会自动设置
        assert hasattr(model, 'created_time')
        assert hasattr(model, 'updated_time')
    
    def test_base_model_repr(self):
        """测试基础模型字符串表示"""
        class TestModel2(BaseModel):
            __abstract__ = False
            test_field = None
        
        model = TestModel2()
        repr_str = repr(model)
        
        assert "TestModel2" in repr_str
        assert "id=" in repr_str
    
    def test_base_model_to_dict(self):
        """测试基础模型转字典"""
        class TestModel3(BaseModel):
            __abstract__ = False
            test_field = "test_value"
        
        model = TestModel3()
        data = model.to_dict()
        
        # to_dict只包含SQLAlchemy Column字段
        assert "id" in data
        assert "created_time" in data
        assert "updated_time" in data
        
        # 测试时间格式
        assert isinstance(data["created_time"], str)
        assert isinstance(data["updated_time"], str)
    
    def test_base_model_from_dict(self):
        """测试从字典创建基础模型"""
        class TestModel4(BaseModel):
            __abstract__ = False
            test_field = None
        
        data = {
            "test_field": "test_value",
            "created_time": "2023-01-01T00:00:00+00:00"
        }
        
        model = TestModel4.from_dict(data)
        
        assert model.test_field == "test_value"
        assert hasattr(model, 'created_time')
    
    def test_base_model_from_dict_with_none(self):
        """测试从字典创建基础模型（包含None值）"""
        class TestModel5(BaseModel):
            __abstract__ = False
            test_field = None
        
        data = {
            "test_field": "test_value",
            "none_field": None
        }
        
        model = TestModel5.from_dict(data)
        
        assert model.test_field == "test_value"
        assert not hasattr(model, 'none_field')
    
    def test_base_model_update_from_dict(self):
        """测试从字典更新基础模型"""
        class TestModel6(BaseModel):
            __abstract__ = False
            test_field = "old_value"
        
        model = TestModel6()
        # 时间戳在数据库会话中才会自动设置，这里只测试字段存在
        assert hasattr(model, 'updated_time')
        
        update_data = {
            "test_field": "new_value",
            "none_field": None
        }
        
        model.update_from_dict(update_data)
        
        assert model.test_field == "new_value"
        assert hasattr(model, 'updated_time')
    
    def test_base_model_properties(self):
        """测试基础模型属性"""
        class TestModel7(BaseModel):
            __abstract__ = False
            test_field = None
        
        model = TestModel7()
        
        assert model.created_at == model.created_time
        assert model.updated_at == model.updated_time
    
    def test_base_model_tablename(self):
        """测试表名生成"""
        class TestModel8(BaseModel):
            __abstract__ = False
            test_field = None
        
        assert TestModel8.__tablename__ == "testmodel8" 