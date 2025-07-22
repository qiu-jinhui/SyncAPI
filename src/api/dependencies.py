"""
API依赖注入
提供数据库会话、服务实例等依赖
"""

from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session

from src.config.database import SessionLocal
from src.services.event_service import EventService
from src.services.sync_service import SyncService
from src.services.redis_service import RedisService
from src.utils.logger import get_logger

logger = get_logger(__name__)


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话
    
    Yields:
        Session: 数据库会话实例
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 别名，为了与sync_router.py保持一致
get_db_session = get_db


def get_redis_service() -> RedisService:
    """
    获取Redis服务实例
    
    Returns:
        RedisService: Redis服务实例
    """
    return RedisService()


def get_event_service(
    db: Session = Depends(get_db),
    redis_service: RedisService = Depends(get_redis_service)
) -> EventService:
    """
    获取事件服务实例
    
    Args:
        db: 数据库会话
        redis_service: Redis服务实例
        
    Returns:
        EventService: 事件服务实例
    """
    return EventService(db_session=db)


def get_sync_service(
    db: Session = Depends(get_db),
    redis_service: RedisService = Depends(get_redis_service)
) -> SyncService:
    """
    获取同步服务实例
    
    Args:
        db: 数据库会话
        redis_service: Redis服务实例
        
    Returns:
        SyncService: 同步服务实例
    """
    return SyncService(db_session=db) 