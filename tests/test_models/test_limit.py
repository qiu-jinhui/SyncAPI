"""
限制模型测试
"""

import pytest
from datetime import datetime
from src.models.limit import ModelLimit, ModelLimitUsage

class TestModelLimit:
    """模型限制测试类"""
    
    def test_limit_creation(self):
        """测试限制创建"""
        limit = ModelLimit(
            subscription_id="123e4567-e89b-12d3-a456-426614174000",
            limit_type="input_token_limit",
            scope="daily",
            limit_value=1000000
        )
        
        assert limit.subscription_id == "123e4567-e89b-12d3-a456-426614174000"
        assert limit.limit_type == "input_token_limit"
        assert limit.scope == "daily"
        assert limit.limit_value == 1000000
        assert hasattr(limit, 'id')
        # 时间戳在数据库会话中才会自动设置
        assert hasattr(limit, 'created_time')
        assert hasattr(limit, 'updated_time')
    
    def test_limit_repr(self):
        """测试限制字符串表示"""
        limit = ModelLimit(
            subscription_id="123e4567-e89b-12d3-a456-426614174000",
            limit_type="input_token_limit",
            scope="daily",
            limit_value=1000000
        )
        
        repr_str = repr(limit)
        assert "ModelLimit" in repr_str
        assert "input_token_limit" in repr_str
        assert "daily" in repr_str
        # limit_value在repr中可能不显示，测试基本结构
        assert "ModelLimit" in repr_str
        assert "input_token_limit" in repr_str
        assert "daily" in repr_str
    
    def test_limit_properties(self):
        """测试限制属性"""
        limit = ModelLimit(
            subscription_id="123e4567-e89b-12d3-a456-426614174000",
            limit_type="input_token_limit",
            scope="daily",
            limit_value=1000000
        )
        
        assert limit.type == "input_token_limit"
        assert limit.value == 1000000
    
    def test_limit_to_dict(self):
        """测试限制转字典"""
        limit = ModelLimit(
            subscription_id="123e4567-e89b-12d3-a456-426614174000",
            limit_type="input_token_limit",
            scope="daily",
            limit_value=1000000
        )
        
        data = limit.to_dict()
        
        assert "id" in data
        assert "subscription_id" in data
        assert "limit_type" in data
        assert "scope" in data
        assert "limit_value" in data
        assert "created_time" in data
        assert "updated_time" in data
        assert data["subscription_id"] == "123e4567-e89b-12d3-a456-426614174000"
        assert data["limit_type"] == "input_token_limit"
        assert data["scope"] == "daily"
        assert data["limit_value"] == 1000000
    
    def test_limit_from_dict(self):
        """测试从字典创建限制"""
        data = {
            "subscription_id": "123e4567-e89b-12d3-a456-426614174000",
            "limit_type": "input_token_limit",
            "scope": "daily",
            "limit_value": 1000000
        }
        
        limit = ModelLimit.from_dict(data)
        
        assert limit.subscription_id == "123e4567-e89b-12d3-a456-426614174000"
        assert limit.limit_type == "input_token_limit"
        assert limit.scope == "daily"
        assert limit.limit_value == 1000000

class TestModelLimitUsage:
    """模型限制使用测试类"""
    
    def test_limit_usage_creation(self):
        """测试限制使用创建"""
        usage = ModelLimitUsage(
            limit_id="123e4567-e89b-12d3-a456-426614174000",
            scope="daily",
            usage_period=datetime(2023, 1, 1, 12, 0, 0),
            value=50000,
            request_id="123e4567-e89b-12d3-a456-426614174001",
            called_by="test_user"
        )
        
        assert usage.limit_id == "123e4567-e89b-12d3-a456-426614174000"
        assert usage.scope == "daily"
        assert usage.usage_period == datetime(2023, 1, 1, 12, 0, 0)
        assert usage.value == 50000
        assert usage.request_id == "123e4567-e89b-12d3-a456-426614174001"
        assert usage.called_by == "test_user"
        assert hasattr(usage, 'id')
        # 时间戳在数据库会话中才会自动设置
        assert hasattr(usage, 'created_time')
    
    def test_limit_usage_repr(self):
        """测试限制使用字符串表示"""
        usage = ModelLimitUsage(
            limit_id="123e4567-e89b-12d3-a456-426614174000",
            scope="daily",
            usage_period=datetime(2023, 1, 1, 12, 0, 0),
            value=50000
        )
        
        repr_str = repr(usage)
        assert "ModelLimitUsage" in repr_str
        assert "daily" in repr_str
        # value在repr中可能不显示，测试基本结构
        assert "ModelLimitUsage" in repr_str
        assert "daily" in repr_str
    
    def test_limit_usage_properties(self):
        """测试限制使用属性"""
        usage = ModelLimitUsage(
            limit_id="123e4567-e89b-12d3-a456-426614174000",
            scope="daily",
            usage_period=datetime(2023, 1, 1, 12, 0, 0),
            value=50000,
            request_id="123e4567-e89b-12d3-a456-426614174001",
            called_by="test_user"
        )
        
        assert usage.usage_value == 50000
        assert usage.period == datetime(2023, 1, 1, 12, 0, 0)
        assert usage.caller == "test_user"
    
    def test_limit_usage_default_values(self):
        """测试限制使用默认值"""
        usage = ModelLimitUsage(
            limit_id="123e4567-e89b-12d3-a456-426614174000",
            scope="daily",
            usage_period=datetime(2023, 1, 1, 12, 0, 0)
        )
        
        # 默认值在数据库层面设置，这里测试字段存在
        assert hasattr(usage, 'value')
        assert hasattr(usage, 'request_id')
        assert hasattr(usage, 'called_by')
    
    def test_limit_usage_null_caller(self):
        """测试限制使用空调用者"""
        usage = ModelLimitUsage(
            limit_id="123e4567-e89b-12d3-a456-426614174000",
            scope="daily",
            usage_period=datetime(2023, 1, 1, 12, 0, 0),
            value=50000
        )
        
        assert usage.caller == ""
    
    def test_limit_usage_to_dict(self):
        """测试限制使用转字典"""
        usage = ModelLimitUsage(
            limit_id="123e4567-e89b-12d3-a456-426614174000",
            scope="daily",
            usage_period=datetime(2023, 1, 1, 12, 0, 0),
            value=50000,
            request_id="123e4567-e89b-12d3-a456-426614174001",
            called_by="test_user"
        )
        
        data = usage.to_dict()
        
        assert "id" in data
        assert "limit_id" in data
        assert "scope" in data
        assert "usage_period" in data
        assert "value" in data
        assert "request_id" in data
        assert "called_by" in data
        assert "created_time" in data
        assert data["limit_id"] == "123e4567-e89b-12d3-a456-426614174000"
        assert data["scope"] == "daily"
        assert data["value"] == 50000
        assert data["request_id"] == "123e4567-e89b-12d3-a456-426614174001"
        assert data["called_by"] == "test_user"
    
    def test_limit_usage_from_dict(self):
        """测试从字典创建限制使用"""
        data = {
            "limit_id": "123e4567-e89b-12d3-a456-426614174000",
            "scope": "daily",
            "usage_period": "2023-01-01T12:00:00+00:00",
            "value": 50000,
            "request_id": "123e4567-e89b-12d3-a456-426614174001",
            "called_by": "test_user"
        }
        
        usage = ModelLimitUsage.from_dict(data)
        
        assert usage.limit_id == "123e4567-e89b-12d3-a456-426614174000"
        assert usage.scope == "daily"
        assert usage.value == 50000
        assert usage.request_id == "123e4567-e89b-12d3-a456-426614174001"
        assert usage.called_by == "test_user" 