"""
Redis服务测试
"""

import pytest
import json
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

from src.services.redis_service import RedisService


class TestRedisService:
    """Redis服务测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.service = RedisService()
    
    @pytest.mark.asyncio
    async def test_init(self):
        """测试初始化"""
        assert self.service.redis_url == "redis://localhost:6379/0"
        assert self.service.pool_size == 10
        assert self.service._pool is None
        assert self.service._client is None
    
    @pytest.mark.asyncio
    async def test_get_client_creates_pool_and_client(self):
        """测试获取客户端时创建连接池和客户端"""
        with patch('redis.asyncio.ConnectionPool') as mock_pool_class, \
             patch('redis.asyncio.Redis') as mock_redis_class:
            
            mock_pool = Mock()
            mock_pool_class.from_url.return_value = mock_pool
            mock_client = Mock()
            mock_redis_class.return_value = mock_client
            
            client = await self.service.get_client()
            
            assert client == mock_client
            assert self.service._pool == mock_pool
            assert self.service._client == mock_client
            mock_pool_class.from_url.assert_called_once_with(
                "redis://localhost:6379/0", max_connections=10
            )
    
    @pytest.mark.asyncio
    async def test_get_client_reuses_existing(self):
        """测试重用已存在的客户端"""
        mock_client = Mock()
        self.service._client = mock_client
        
        client = await self.service.get_client()
        
        assert client == mock_client
    
    @pytest.mark.asyncio
    async def test_close(self):
        """测试关闭连接"""
        mock_client = AsyncMock()
        mock_pool = AsyncMock()
        
        self.service._client = mock_client
        self.service._pool = mock_pool
        
        await self.service.close()
        
        mock_client.close.assert_called_once()
        mock_pool.disconnect.assert_called_once()
        assert self.service._client is None
        assert self.service._pool is None
    
    @pytest.mark.asyncio
    async def test_set_cache_simple_value(self):
        """测试设置简单缓存值"""
        with patch.object(self.service, 'get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.set.return_value = True
            mock_get_client.return_value = mock_client
            
            result = await self.service.set_cache("test_key", "test_value", 3600)
            
            assert result is True
            mock_client.set.assert_called_once_with("test_key", "test_value", ex=3600)
    
    @pytest.mark.asyncio
    async def test_set_cache_dict_value(self):
        """测试设置字典缓存值"""
        with patch.object(self.service, 'get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.set.return_value = True
            mock_get_client.return_value = mock_client
            
            test_dict = {"key": "value", "number": 123}
            result = await self.service.set_cache("test_key", test_dict)
            
            assert result is True
            expected_json = json.dumps(test_dict, ensure_ascii=False)
            mock_client.set.assert_called_once_with("test_key", expected_json, ex=None)
    
    @pytest.mark.asyncio
    async def test_set_cache_error(self):
        """测试设置缓存出错"""
        with patch.object(self.service, 'get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.set.side_effect = Exception("Redis error")
            mock_get_client.return_value = mock_client
            
            result = await self.service.set_cache("test_key", "test_value")
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_get_cache_string_value(self):
        """测试获取字符串缓存值"""
        with patch.object(self.service, 'get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get.return_value = b"test_value"
            mock_get_client.return_value = mock_client
            
            result = await self.service.get_cache("test_key")
            
            assert result == "test_value"
    
    @pytest.mark.asyncio
    async def test_get_cache_json_value(self):
        """测试获取JSON缓存值"""
        with patch.object(self.service, 'get_client') as mock_get_client:
            mock_client = AsyncMock()
            test_dict = {"key": "value", "number": 123}
            mock_client.get.return_value = json.dumps(test_dict).encode()
            mock_get_client.return_value = mock_client
            
            result = await self.service.get_cache("test_key")
            
            assert result == test_dict
    
    @pytest.mark.asyncio
    async def test_get_cache_not_found(self):
        """测试获取不存在的缓存"""
        with patch.object(self.service, 'get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get.return_value = None
            mock_get_client.return_value = mock_client
            
            result = await self.service.get_cache("nonexistent_key")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_cache_error(self):
        """测试获取缓存出错"""
        with patch.object(self.service, 'get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get.side_effect = Exception("Redis error")
            mock_get_client.return_value = mock_client
            
            result = await self.service.get_cache("test_key")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_cache_success(self):
        """测试删除缓存成功"""
        with patch.object(self.service, 'get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.delete.return_value = 1
            mock_get_client.return_value = mock_client
            
            result = await self.service.delete_cache("test_key")
            
            assert result is True
            mock_client.delete.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_delete_cache_not_found(self):
        """测试删除不存在的缓存"""
        with patch.object(self.service, 'get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.delete.return_value = 0
            mock_get_client.return_value = mock_client
            
            result = await self.service.delete_cache("nonexistent_key")
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_publish_event_success(self):
        """测试发布事件成功"""
        with patch.object(self.service, 'get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.xadd.return_value = "1234567890-0"
            mock_get_client.return_value = mock_client
            
            event_data = {
                "event_type": "CREATE",
                "entity_type": "project",
                "entity_id": "proj123"
            }
            
            result = await self.service.publish_event("test_stream", event_data)
            
            assert result == "1234567890-0"
            mock_client.xadd.assert_called_once()
            
            # 验证事件数据包含时间戳和来源
            call_args = mock_client.xadd.call_args
            assert call_args[0][0] == "test_stream"  # stream_name
            event_with_metadata = call_args[0][1]
            assert "timestamp" in event_with_metadata
            assert "source" in event_with_metadata
            assert event_with_metadata["source"] == "synchronize_api"
    
    @pytest.mark.asyncio
    async def test_publish_event_error(self):
        """测试发布事件出错"""
        with patch.object(self.service, 'get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.xadd.side_effect = Exception("Redis error")
            mock_get_client.return_value = mock_client
            
            event_data = {"event_type": "CREATE"}
            result = await self.service.publish_event("test_stream", event_data)
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_read_events_success(self):
        """测试读取事件成功"""
        with patch.object(self.service, 'get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.xgroup_create.return_value = True
            mock_client.xreadgroup.return_value = [
                ("test_stream", [
                    ("1234567890-0", {"event_type": "CREATE", "entity_id": "123"}),
                    ("1234567890-1", {"event_type": "UPDATE", "entity_id": "456"})
                ])
            ]
            mock_get_client.return_value = mock_client
            
            result = await self.service.read_events(
                "test_stream", "test_group", "test_consumer", 10
            )
            
            assert len(result) == 2
            assert result[0]["id"] == "1234567890-0"
            assert result[0]["event_type"] == "CREATE"
            assert result[1]["id"] == "1234567890-1"
            assert result[1]["event_type"] == "UPDATE"
    
    @pytest.mark.asyncio
    async def test_read_events_consumer_group_exists(self):
        """测试消费者组已存在的情况"""
        with patch.object(self.service, 'get_client') as mock_get_client:
            mock_client = AsyncMock()
            # 模拟消费者组已存在的异常
            import redis.asyncio as redis
            mock_client.xgroup_create.side_effect = redis.RedisError("Group exists")
            mock_client.xreadgroup.return_value = []
            mock_get_client.return_value = mock_client
            
            result = await self.service.read_events(
                "test_stream", "test_group", "test_consumer"
            )
            
            assert result == []
    
    @pytest.mark.asyncio
    async def test_read_events_error(self):
        """测试读取事件出错"""
        with patch.object(self.service, 'get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.xreadgroup.side_effect = Exception("Redis error")
            mock_get_client.return_value = mock_client
            
            result = await self.service.read_events(
                "test_stream", "test_group", "test_consumer"
            )
            
            assert result == []
    
    @pytest.mark.asyncio
    async def test_ack_event_success(self):
        """测试确认事件成功"""
        with patch.object(self.service, 'get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.xack.return_value = 1
            mock_get_client.return_value = mock_client
            
            result = await self.service.ack_event(
                "test_stream", "test_group", "1234567890-0"
            )
            
            assert result is True
            mock_client.xack.assert_called_once_with(
                "test_stream", "test_group", "1234567890-0"
            )
    
    @pytest.mark.asyncio
    async def test_ack_event_failure(self):
        """测试确认事件失败"""
        with patch.object(self.service, 'get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.xack.return_value = 0
            mock_get_client.return_value = mock_client
            
            result = await self.service.ack_event(
                "test_stream", "test_group", "1234567890-0"
            )
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_ack_event_error(self):
        """测试确认事件出错"""
        with patch.object(self.service, 'get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.xack.side_effect = Exception("Redis error")
            mock_get_client.return_value = mock_client
            
            result = await self.service.ack_event(
                "test_stream", "test_group", "1234567890-0"
            )
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """测试健康检查成功"""
        with patch.object(self.service, 'get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.ping.return_value = True
            mock_get_client.return_value = mock_client
            
            result = await self.service.health_check()
            
            assert result is True
            mock_client.ping.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """测试健康检查失败"""
        with patch.object(self.service, 'get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.ping.side_effect = Exception("Redis error")
            mock_get_client.return_value = mock_client
            
            result = await self.service.health_check()
            
            assert result is False 