"""
Redis服务
负责缓存和事件流管理
"""

import json
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import redis.asyncio as redis
import structlog

from src.config.settings import get_settings
from src.utils.logger import get_logger

logger = get_logger()


class RedisService:
    """Redis服务类"""
    
    def __init__(self):
        self.settings = get_settings()
        self.redis_url = self.settings.REDIS_URL
        self.pool_size = self.settings.REDIS_POOL_SIZE
        self._pool: Optional[redis.ConnectionPool] = None
        self._client: Optional[redis.Redis] = None
    
    async def get_client(self) -> redis.Redis:
        """
        获取Redis客户端
        
        Returns:
            Redis客户端实例
        """
        if self._client is None:
            if self._pool is None:
                self._pool = redis.ConnectionPool.from_url(
                    self.redis_url,
                    max_connections=self.pool_size
                )
            self._client = redis.Redis(connection_pool=self._pool)
        
        return self._client
    
    async def close(self):
        """关闭Redis连接"""
        if self._client:
            await self._client.close()
            self._client = None
        if self._pool:
            await self._pool.disconnect()
            self._pool = None
    
    async def set_cache(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """
        设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            expire: 过期时间（秒）
            
        Returns:
            是否设置成功
        """
        try:
            client = await self.get_client()
            
            # 序列化值
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            
            result = await client.set(key, value, ex=expire)
            
            logger.debug(
                "设置缓存",
                key=key,
                expire=expire,
                success=bool(result)
            )
            
            return bool(result)
            
        except Exception as e:
            logger.error("设置缓存失败", key=key, error=str(e))
            return False
    
    async def get_cache(self, key: str) -> Optional[Any]:
        """
        获取缓存
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，不存在返回None
        """
        try:
            client = await self.get_client()
            value = await client.get(key)
            
            if value is None:
                return None
            
            # 尝试反序列化JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value.decode('utf-8')
                
        except Exception as e:
            logger.error("获取缓存失败", key=key, error=str(e))
            return None
    
    async def delete_cache(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            是否删除成功
        """
        try:
            client = await self.get_client()
            result = await client.delete(key)
            
            logger.debug(
                "删除缓存",
                key=key,
                success=bool(result)
            )
            
            return bool(result)
            
        except Exception as e:
            logger.error("删除缓存失败", key=key, error=str(e))
            return False
    
    async def publish_event(self, stream_name: str, event_data: Dict[str, Any]) -> Optional[str]:
        """
        发布事件到Redis Stream
        
        Args:
            stream_name: 流名称
            event_data: 事件数据
            
        Returns:
            事件ID，失败返回None
        """
        try:
            client = await self.get_client()
            
            # 添加时间戳
            event_data = {
                **event_data,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "synchronize_api"
            }
            
            # 发布到Stream
            event_id = await client.xadd(stream_name, event_data)
            
            logger.info(
                "发布事件到Redis Stream",
                stream_name=stream_name,
                event_id=event_id,
                event_type=event_data.get("event_type"),
                entity_type=event_data.get("entity_type"),
                entity_id=event_data.get("entity_id")
            )
            
            return event_id
            
        except Exception as e:
            logger.error(
                "发布事件失败",
                stream_name=stream_name,
                error=str(e),
                event_data=event_data
            )
            return None
    
    async def read_events(self, stream_name: str, consumer_group: str, 
                         consumer_name: str, count: int = 10) -> List[Dict[str, Any]]:
        """
        从Redis Stream读取事件
        
        Args:
            stream_name: 流名称
            consumer_group: 消费者组
            consumer_name: 消费者名称
            count: 读取数量
            
        Returns:
            事件列表
        """
        try:
            client = await self.get_client()
            
            # 确保消费者组存在
            try:
                await client.xgroup_create(stream_name, consumer_group, id='0', mkstream=True)
            except redis.RedisError:
                # 消费者组可能已存在
                pass
            
            # 读取事件
            messages = await client.xreadgroup(
                consumer_group,
                consumer_name,
                {stream_name: '>'},
                count=count,
                block=1000  # 阻塞1秒
            )
            
            events = []
            for stream, msgs in messages:
                for msg_id, fields in msgs:
                    event = {
                        "id": msg_id,
                        "stream": stream,
                        **fields
                    }
                    events.append(event)
            
            logger.debug(
                "从Redis Stream读取事件",
                stream_name=stream_name,
                consumer_group=consumer_group,
                consumer_name=consumer_name,
                events_count=len(events)
            )
            
            return events
            
        except Exception as e:
            logger.error(
                "读取事件失败",
                stream_name=stream_name,
                consumer_group=consumer_group,
                consumer_name=consumer_name,
                error=str(e)
            )
            return []
    
    async def ack_event(self, stream_name: str, consumer_group: str, event_id: str) -> bool:
        """
        确认事件处理完成
        
        Args:
            stream_name: 流名称
            consumer_group: 消费者组
            event_id: 事件ID
            
        Returns:
            是否确认成功
        """
        try:
            client = await self.get_client()
            result = await client.xack(stream_name, consumer_group, event_id)
            
            logger.debug(
                "确认事件处理",
                stream_name=stream_name,
                consumer_group=consumer_group,
                event_id=event_id,
                success=bool(result)
            )
            
            return bool(result)
            
        except Exception as e:
            logger.error(
                "确认事件失败",
                stream_name=stream_name,
                consumer_group=consumer_group,
                event_id=event_id,
                error=str(e)
            )
            return False
    
    async def health_check(self) -> bool:
        """
        Redis健康检查
        
        Returns:
            是否健康
        """
        try:
            client = await self.get_client()
            await client.ping()
            logger.debug("Redis健康检查通过")
            return True
        except Exception as e:
            logger.warning("Redis健康检查失败", error=str(e))
            return False 