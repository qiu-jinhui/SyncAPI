"""
API依赖注入测试
测试依赖注入函数的正确性
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.api.dependencies import (
    get_db, 
    get_redis_service, 
    get_event_service, 
    get_sync_service
)
from src.services.event_service import EventService
from src.services.sync_service import SyncService
from src.services.redis_service import RedisService


class TestDependencies:
    """依赖注入测试类"""
    
    def test_get_db(self):
        """测试获取数据库会话"""
        with patch('src.api.dependencies.SessionLocal') as mock_session_local:
            mock_session = Mock()
            mock_session_local.return_value = mock_session
            
            # 获取数据库会话生成器
            db_generator = get_db()
            
            # 获取会话
            session = next(db_generator)
            assert session == mock_session
            
            # 验证会话创建
            mock_session_local.assert_called_once()
            
            # 模拟生成器结束，应该调用close()
            try:
                next(db_generator)
            except StopIteration:
                pass
                
            mock_session.close.assert_called_once()
    
    def test_get_db_exception_handling(self):
        """测试数据库会话异常处理"""
        with patch('src.api.dependencies.SessionLocal') as mock_session_local:
            mock_session = Mock()
            mock_session_local.return_value = mock_session
            
            db_generator = get_db()
            session = next(db_generator)
            
            # 模拟异常情况
            try:
                raise Exception("Database error")
            except:
                # 即使发生异常，也应该关闭会话
                try:
                    db_generator.close()
                except:
                    pass
            
            # 验证会话最终被关闭
            mock_session.close.assert_called_once()
    
    def test_get_redis_service(self):
        """测试获取Redis服务"""
        redis_service = get_redis_service()
        
        assert isinstance(redis_service, RedisService)
    
    def test_get_redis_service_returns_new_instance(self):
        """测试每次调用都返回新的Redis服务实例"""
        service1 = get_redis_service()
        service2 = get_redis_service()
        
        # 每次调用都应该返回新实例
        assert service1 is not service2
        assert isinstance(service1, RedisService)
        assert isinstance(service2, RedisService)
    
    def test_get_event_service(self):
        """测试获取事件服务"""
        mock_db = Mock()
        mock_redis = Mock()
        
        event_service = get_event_service(mock_db, mock_redis)
        
        assert isinstance(event_service, EventService)
        # 验证依赖注入正确
        assert event_service.db_session == mock_db
    
    def test_get_event_service_dependency_injection(self):
        """测试事件服务的依赖注入"""
        with patch('src.api.dependencies.EventService') as mock_event_service_class:
            mock_db = Mock()
            mock_redis = Mock()
            mock_service_instance = Mock()
            mock_event_service_class.return_value = mock_service_instance
            
            result = get_event_service(mock_db, mock_redis)
            
            # 验证EventService被正确实例化
            mock_event_service_class.assert_called_once_with(db_session=mock_db)
            assert result == mock_service_instance
    
    def test_get_sync_service(self):
        """测试获取同步服务"""
        mock_db = Mock()
        mock_redis = Mock()
        
        sync_service = get_sync_service(mock_db, mock_redis)
        
        assert isinstance(sync_service, SyncService)
        # 验证依赖注入正确
        assert sync_service.db_session == mock_db
    
    def test_get_sync_service_dependency_injection(self):
        """测试同步服务的依赖注入"""
        with patch('src.api.dependencies.SyncService') as mock_sync_service_class:
            mock_db = Mock()
            mock_redis = Mock()
            mock_service_instance = Mock()
            mock_sync_service_class.return_value = mock_service_instance
            
            result = get_sync_service(mock_db, mock_redis)
            
            # 验证SyncService被正确实例化
            mock_sync_service_class.assert_called_once_with(db_session=mock_db)
            assert result == mock_service_instance
    
    def test_all_dependencies_integration(self):
        """测试所有依赖的集成"""
        with patch('src.api.dependencies.SessionLocal') as mock_session_local:
            mock_session = Mock()
            mock_session_local.return_value = mock_session
            
            # 获取所有依赖
            db_generator = get_db()
            db_session = next(db_generator)
            redis_service = get_redis_service()
            event_service = get_event_service(db_session, redis_service)
            sync_service = get_sync_service(db_session, redis_service)
            
            # 验证所有服务都正确创建
            assert db_session == mock_session
            assert isinstance(redis_service, RedisService)
            assert isinstance(event_service, EventService)
            assert isinstance(sync_service, SyncService)
            
            # 验证依赖关系
            assert event_service.db_session == db_session
            assert sync_service.db_session == db_session
            
            # 清理
            try:
                next(db_generator)
            except StopIteration:
                pass 