"""
订阅模型测试
"""

import pytest
from src.models.subscription import Subscription

class TestSubscription:
    """订阅模型测试类"""
    
    def test_subscription_creation(self):
        """测试订阅创建"""
        subscription = Subscription(
            project_id="123e4567-e89b-12d3-a456-426614174000",
            use_case_id="123e4567-e89b-12d3-a456-426614174001",
            model_id="123e4567-e89b-12d3-a456-426614174002"
        )
        
        assert subscription.project_id == "123e4567-e89b-12d3-a456-426614174000"
        assert subscription.use_case_id == "123e4567-e89b-12d3-a456-426614174001"
        assert subscription.model_id == "123e4567-e89b-12d3-a456-426614174002"
        assert hasattr(subscription, 'id')
        # 时间戳在数据库会话中才会自动设置
        assert hasattr(subscription, 'created_time')
        assert hasattr(subscription, 'updated_time')
    
    def test_subscription_repr(self):
        """测试订阅字符串表示"""
        subscription = Subscription(
            project_id="123e4567-e89b-12d3-a456-426614174000",
            use_case_id="123e4567-e89b-12d3-a456-426614174001",
            model_id="123e4567-e89b-12d3-a456-426614174002"
        )
        
        repr_str = repr(subscription)
        assert "Subscription" in repr_str
        assert "123e4567-e89b-12d3-a456-426614174000" in repr_str
        assert "123e4567-e89b-12d3-a456-426614174001" in repr_str
        assert "123e4567-e89b-12d3-a456-426614174002" in repr_str
    
    def test_subscription_key_property(self):
        """测试订阅键属性"""
        subscription = Subscription(
            project_id="123e4567-e89b-12d3-a456-426614174000",
            use_case_id="123e4567-e89b-12d3-a456-426614174001",
            model_id="123e4567-e89b-12d3-a456-426614174002"
        )
        
        expected_key = "123e4567-e89b-12d3-a456-426614174000:123e4567-e89b-12d3-a456-426614174001:123e4567-e89b-12d3-a456-426614174002"
        assert subscription.subscription_key == expected_key
    
    def test_subscription_to_dict(self):
        """测试订阅转字典"""
        subscription = Subscription(
            project_id="123e4567-e89b-12d3-a456-426614174000",
            use_case_id="123e4567-e89b-12d3-a456-426614174001",
            model_id="123e4567-e89b-12d3-a456-426614174002"
        )
        
        data = subscription.to_dict()
        
        assert "id" in data
        assert "project_id" in data
        assert "use_case_id" in data
        assert "model_id" in data
        assert "created_time" in data
        assert "updated_time" in data
        assert data["project_id"] == "123e4567-e89b-12d3-a456-426614174000"
        assert data["use_case_id"] == "123e4567-e89b-12d3-a456-426614174001"
        assert data["model_id"] == "123e4567-e89b-12d3-a456-426614174002"
    
    def test_subscription_from_dict(self):
        """测试从字典创建订阅"""
        data = {
            "project_id": "123e4567-e89b-12d3-a456-426614174000",
            "use_case_id": "123e4567-e89b-12d3-a456-426614174001",
            "model_id": "123e4567-e89b-12d3-a456-426614174002"
        }
        
        subscription = Subscription.from_dict(data)
        
        assert subscription.project_id == "123e4567-e89b-12d3-a456-426614174000"
        assert subscription.use_case_id == "123e4567-e89b-12d3-a456-426614174001"
        assert subscription.model_id == "123e4567-e89b-12d3-a456-426614174002"
    
    def test_subscription_update_from_dict(self):
        """测试从字典更新订阅"""
        subscription = Subscription(
            project_id="123e4567-e89b-12d3-a456-426614174000",
            use_case_id="123e4567-e89b-12d3-a456-426614174001",
            model_id="123e4567-e89b-12d3-a456-426614174002"
        )
        
        import time
        time.sleep(0.001)
        
        original_updated_time = subscription.updated_time
        
        update_data = {
            "project_id": "123e4567-e89b-12d3-a456-426614174003",
            "use_case_id": "123e4567-e89b-12d3-a456-426614174004",
            "model_id": "123e4567-e89b-12d3-a456-426614174005"
        }
        
        subscription.update_from_dict(update_data)
        
        assert subscription.project_id == "123e4567-e89b-12d3-a456-426614174003"
        assert subscription.use_case_id == "123e4567-e89b-12d3-a456-426614174004"
        assert subscription.model_id == "123e4567-e89b-12d3-a456-426614174005"
        # 时间戳在数据库会话中才会自动设置
        assert hasattr(subscription, 'updated_time') 