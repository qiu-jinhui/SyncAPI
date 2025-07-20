"""
数据库配置和连接管理
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator

from src.config.settings import get_settings

# 获取配置
settings = get_settings()

# 创建数据库引擎
if settings.TESTING:
    # 测试环境使用SQLite
    DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(
        DATABASE_URL,
        echo=settings.DEBUG,
        connect_args={"check_same_thread": False},  # SQLite特有配置
    )
else:
    # 生产环境使用PostgreSQL
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=QueuePool,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_pre_ping=True,  # 连接前检查有效性
        echo=settings.DEBUG,
    )

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话
    
    Yields:
        数据库会话实例
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """创建所有表"""
    from src.models.base import Base
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """删除所有表（仅用于测试）"""
    from src.models.base import Base
    Base.metadata.drop_all(bind=engine) 