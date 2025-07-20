"""
应用配置
从环境变量加载配置
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用配置
    APP_NAME: str = "synchronize-api"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://username:password@localhost:5432/synchronize_api"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_POOL_SIZE: int = 10
    
    # Model Garden配置
    MODEL_GARDEN_BASE_URL: str = "http://localhost:8080"
    MODEL_GARDEN_API_KEY: str = "your_api_key_here"
    MODEL_GARDEN_TIMEOUT: int = 30
    
    # 同步配置
    SYNC_INTERVAL_MINUTES: int = 60
    SYNC_BATCH_SIZE: int = 1000
    
    # 安全配置
    SECRET_KEY: str = "your_secret_key_here"
    JWT_SECRET_KEY: str = "your_jwt_secret_key_here"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 测试配置
    TESTING: bool = False
    TEST_DATABASE_URL: Optional[str] = None
    TEST_REDIS_URL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
_settings = None


def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings 