"""
同步API路由测试 - 更新版本
测试修复后的同步路由实现
"""

import pytest
from unittest.mock import patch, Mock, AsyncMock, MagicMock
from fastapi import HTTPException
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from src.schemas.sync_request import SyncRequest
from src.schemas.sync_response import SyncResponse


class TestSyncRouter:
    """同步路由测试类 - 更新版本"""
    
    @pytest.fixture
    def mock_sync_service(self):
        """模拟同步服务"""
        mock_service = AsyncMock()
        
        # 模拟sync_all方法返回结果
        mock_service.sync_all.return_value = {
            "success": True,
            "start_time": "2025-07-20T10:00:00Z",
            "end_time": "2025-07-20T10:05:00Z",
            "duration_seconds": 300,
            "totals": {
                "created": 10,
                "updated": 5,
                "errors": 0
            },
            "details": {
                "projects": {
                    "data": [
                        {
                            "id": "proj-001",
                            "project_name": "Test Project",
                            "project_code": "TEST",
                            "created_time": "2025-07-20T10:00:00Z",
                            "updated_time": "2025-07-20T10:00:00Z"
                        }
                    ],
                    "created": 1,
                    "updated": 0,
                    "errors": 0
                },
                "use_cases": {
                    "data": [
                        {
                            "id": "uc-001",
                            "project_id": "proj-001",
                            "use_case_name": "test_case",
                            "ad_group": "test_group",
                            "is_active": True,
                            "created_time": "2025-07-20T10:00:00Z",
                            "updated_time": "2025-07-20T10:00:00Z"
                        }
                    ],
                    "created": 1,
                    "updated": 0,
                    "errors": 0
                },
                "budgets": {"data": [], "created": 0, "updated": 0, "errors": 0},
                "models": {"data": [], "created": 0, "updated": 0, "errors": 0},
                "deployments": {"data": [], "created": 0, "updated": 0, "errors": 0},
                "pricing": {"data": [], "created": 0, "updated": 0, "errors": 0},
                "subscriptions": {"data": [], "created": 0, "updated": 0, "errors": 0},
                "limits": {"data": [], "created": 0, "updated": 0, "errors": 0}
            }
        }
        
        # 模拟Redis服务
        mock_redis = AsyncMock()
        mock_redis.get_latest_sync_result.return_value = {
            "end_time": "2025-07-20T10:05:00Z",
            "totals": {"created": 10, "updated": 5, "errors": 0}
        }
        mock_redis.is_sync_in_progress.return_value = False
        mock_service.redis_service = mock_redis
        
        return mock_service
    
    @pytest.fixture
    def mock_db_session(self):
        """模拟数据库会话"""
        mock_session = Mock(spec=Session)
        return mock_session
    
    def test_sync_all_success_without_request_body(
        self, 
        client_with_mocked_dependencies,
        mock_sync_service,
        mock_db_session
    ):
        """测试不带请求体的全量同步成功"""
        
        # 重写依赖注入
        with patch('src.api.dependencies.get_sync_service', return_value=mock_sync_service), \
             patch('src.api.dependencies.get_db_session', return_value=mock_db_session):
            
            response = client_with_mocked_dependencies.post("/api/v1/model-garden/sync/all")
            
            assert response.status_code == 200
            data = response.json()
            
            # 验证响应结构
            assert "projects" in data
            assert "use_cases" in data
            assert "budgets" in data
            assert "models" in data
            assert "model_deployments" in data
            assert "pricing" in data
            assert "use_case_llm_models" in data
            assert "limits" in data
            
            # 验证数据内容
            assert len(data["projects"]) == 1
            assert data["projects"][0]["id"] == "proj-001"
            assert len(data["use_cases"]) == 1
            assert data["use_cases"][0]["id"] == "uc-001"
            
            # 验证SyncService被正确调用
            mock_sync_service.sync_all.assert_called_once_with(
                updated_since=None,
                session=mock_db_session
            )
    
    def test_sync_all_success_with_request_body(
        self,
        client_with_mocked_dependencies,
        mock_sync_service,
        mock_db_session
    ):
        """测试带请求体的全量同步成功"""
        
        # 准备测试数据
        request_data = {
            "updated_since": "2025-07-01T00:00:00Z"
        }
        
        with patch('src.api.dependencies.get_sync_service', return_value=mock_sync_service), \
             patch('src.api.dependencies.get_db_session', return_value=mock_db_session):
            
            response = client_with_mocked_dependencies.post(
                "/api/v1/model-garden/sync/all",
                json=request_data
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # 验证响应结构
            assert "projects" in data
            assert "use_cases" in data
            
            # 验证SyncService被正确调用，包含updated_since参数
            call_args = mock_sync_service.sync_all.call_args
            assert call_args[1]["session"] == mock_db_session
            assert call_args[1]["updated_since"] is not None
            assert call_args[1]["updated_since"].year == 2025
    
    def test_sync_all_sync_service_failure(
        self,
        client_with_mocked_dependencies,
        mock_sync_service,
        mock_db_session
    ):
        """测试SyncService失败的情况"""
        
        # 模拟同步服务失败
        mock_sync_service.sync_all.side_effect = Exception("同步服务失败")
        
        with patch('src.api.dependencies.get_sync_service', return_value=mock_sync_service), \
             patch('src.api.dependencies.get_db_session', return_value=mock_db_session):
            
            response = client_with_mocked_dependencies.post("/api/v1/model-garden/sync/all")
            
            assert response.status_code == 500
            data = response.json()
            assert "同步失败" in data["detail"]
            assert "同步服务失败" in data["detail"]
    
    def test_sync_all_empty_sync_result(
        self,
        client_with_mocked_dependencies,
        mock_sync_service,
        mock_db_session
    ):
        """测试空的同步结果"""
        
        # 模拟空的同步结果
        mock_sync_service.sync_all.return_value = {
            "success": True,
            "details": {}
        }
        
        with patch('src.api.dependencies.get_sync_service', return_value=mock_sync_service), \
             patch('src.api.dependencies.get_db_session', return_value=mock_db_session):
            
            response = client_with_mocked_dependencies.post("/api/v1/model-garden/sync/all")
            
            assert response.status_code == 200
            data = response.json()
            
            # 验证空数据结构
            assert data["projects"] == []
            assert data["use_cases"] == []
            assert data["budgets"] == []
            assert data["models"] == []
            assert data["model_deployments"] == []
            assert data["pricing"] == []
            assert data["use_case_llm_models"] == []
            assert data["limits"] == []
    
    def test_sync_all_malformed_sync_result(
        self,
        client_with_mocked_dependencies,
        mock_sync_service,
        mock_db_session
    ):
        """测试格式错误的同步结果"""
        
        # 模拟格式错误的同步结果
        mock_sync_service.sync_all.return_value = {
            "success": True,
            "details": {
                "projects": {"data": []},  # 空数据而不是缺少字段
                # 缺少其他实体，应该被安全处理
            }
        }
        
        with patch('src.api.dependencies.get_sync_service', return_value=mock_sync_service), \
             patch('src.api.dependencies.get_db_session', return_value=mock_db_session):
            
            response = client_with_mocked_dependencies.post("/api/v1/model-garden/sync/all")
            
            assert response.status_code == 200
            data = response.json()
            
            # 验证容错处理
            assert data["projects"] == []  # 空数据
            assert data["use_cases"] == []  # 缺少字段转为空列表
            assert data["budgets"] == []  # 缺少字段转为空列表
    
    def test_sync_all_with_invalid_datetime_format(
        self,
        client_with_mocked_dependencies,
        mock_sync_service,
        mock_db_session
    ):
        """测试无效的日期时间格式"""
        
        request_data = {
            "updated_since": "invalid-datetime"
        }
        
        with patch('src.api.dependencies.get_sync_service', return_value=mock_sync_service), \
             patch('src.api.dependencies.get_db_session', return_value=mock_db_session):
            
            response = client_with_mocked_dependencies.post(
                "/api/v1/model-garden/sync/all",
                json=request_data
            )
            
            # FastAPI的Pydantic验证会拒绝无效格式
            assert response.status_code == 422
    
    def test_get_sync_status_success(
        self,
        client_with_mocked_dependencies,
        mock_sync_service
    ):
        """测试获取同步状态成功"""
        
        # 确保没有 connection_failed 属性以避免异常
        if hasattr(mock_sync_service.redis_service, 'connection_failed'):
            delattr(mock_sync_service.redis_service, 'connection_failed')
        
        with patch('src.api.dependencies.get_sync_service', return_value=mock_sync_service):
            
            response = client_with_mocked_dependencies.get("/api/v1/model-garden/sync/status")
            
            assert response.status_code == 200
            data = response.json()
            
            # 验证响应结构
            assert data["status"] == "healthy"
            assert data["service"] == "synchronize-api"
            assert data["version"] == "1.0.0"
            assert "last_sync" in data
            assert "sync_in_progress" in data
            assert "last_sync_totals" in data
            
            # 验证数据内容
            assert data["last_sync"] == "2025-07-20T10:05:00Z"
            assert data["sync_in_progress"] is False
            assert data["last_sync_totals"]["created"] == 10
    
    def test_get_sync_status_redis_service_failure(
        self,
        client_with_mocked_dependencies,
        mock_sync_service
    ):
        """测试Redis服务失败的情况"""
        
        # 确保没有 connection_failed 属性以避免初始异常
        if hasattr(mock_sync_service.redis_service, 'connection_failed'):
            delattr(mock_sync_service.redis_service, 'connection_failed')
        
        # 模拟Redis服务异常
        mock_sync_service.redis_service.get_latest_sync_result.side_effect = Exception("Redis连接失败")
        
        with patch('src.api.dependencies.get_sync_service', return_value=mock_sync_service):
            
            response = client_with_mocked_dependencies.get("/api/v1/model-garden/sync/status")
            
            assert response.status_code == 500
            data = response.json()
            assert "获取状态失败" in data["detail"]
            assert "Redis连接失败" in data["detail"]
    
    def test_get_sync_status_missing_redis_methods(
        self,
        client_with_mocked_dependencies,
        mock_sync_service
    ):
        """测试Redis服务方法不存在的情况"""
        
        # 模拟Redis服务方法不存在
        delattr(mock_sync_service.redis_service, 'get_latest_sync_result')
        delattr(mock_sync_service.redis_service, 'is_sync_in_progress')
        # 确保没有 connection_failed 属性
        if hasattr(mock_sync_service.redis_service, 'connection_failed'):
            delattr(mock_sync_service.redis_service, 'connection_failed')
        
        with patch('src.api.dependencies.get_sync_service', return_value=mock_sync_service):
            
            response = client_with_mocked_dependencies.get("/api/v1/model-garden/sync/status")
            
            assert response.status_code == 200
            data = response.json()
            
            # 验证默认值
            assert data["status"] == "healthy"
            assert data["last_sync"] is None
            assert data["sync_in_progress"] is False
            assert data["last_sync_totals"] is None
    
    def test_get_sync_status_redis_connection_failed_attribute(
        self,
        client_with_mocked_dependencies,
        mock_sync_service
    ):
        """测试Redis连接失败属性存在的情况"""
        
        # 模拟Redis连接失败属性（设置为异常实例）
        connection_exception = Exception("Redis连接失败")
        mock_sync_service.redis_service.connection_failed = connection_exception
        
        with patch('src.api.dependencies.get_sync_service', return_value=mock_sync_service):
            
            response = client_with_mocked_dependencies.get("/api/v1/model-garden/sync/status")
            
            assert response.status_code == 500
            data = response.json()
            assert "获取状态失败" in data["detail"]
            assert "Redis连接失败" in data["detail"]
    
    def test_sync_all_with_large_dataset(
        self,
        client_with_mocked_dependencies,
        mock_sync_service,
        mock_db_session
    ):
        """测试大数据集同步"""
        
        # 模拟大数据集
        large_projects = [
            {
                "id": f"proj-{i:03d}",
                "project_name": f"Project {i}",
                "project_code": f"PROJ_{i}",
                "created_time": "2025-07-20T10:00:00Z",
                "updated_time": "2025-07-20T10:00:00Z"
            }
            for i in range(100)
        ]
        
        mock_sync_service.sync_all.return_value = {
            "success": True,
            "totals": {"created": 100, "updated": 0, "errors": 0},
            "details": {
                "projects": {"data": large_projects},
                "use_cases": {"data": []},
                "budgets": {"data": []},
                "models": {"data": []},
                "deployments": {"data": []},
                "pricing": {"data": []},
                "subscriptions": {"data": []},
                "limits": {"data": []}
            }
        }
        
        with patch('src.api.dependencies.get_sync_service', return_value=mock_sync_service), \
             patch('src.api.dependencies.get_db_session', return_value=mock_db_session):
            
            response = client_with_mocked_dependencies.post("/api/v1/model-garden/sync/all")
            
            assert response.status_code == 200
            data = response.json()
            
            # 验证大数据集处理
            assert len(data["projects"]) == 100
            assert data["projects"][0]["id"] == "proj-000"
            assert data["projects"][99]["id"] == "proj-099"
    
    def test_sync_all_performance_logging(
        self,
        client_with_mocked_dependencies,
        mock_sync_service,
        mock_db_session
    ):
        """测试性能日志记录"""
        
        # 模拟包含性能统计的同步结果
        mock_sync_service.sync_all.return_value = {
            "success": True,
            "duration_seconds": 123.45,
            "totals": {"created": 5, "updated": 3, "errors": 1},
            "details": {
                "projects": {
                    "data": [{
                        "id": "proj-001",
                        "project_name": "Test Project",
                        "project_code": "TEST",
                        "created_time": "2025-07-20T10:00:00Z",
                        "updated_time": "2025-07-20T10:00:00Z"
                    }]
                },
                "use_cases": {"data": []},
                "budgets": {"data": []},
                "models": {"data": []},
                "deployments": {"data": []},
                "pricing": {"data": []},
                "subscriptions": {"data": []},
                "limits": {"data": []}
            }
        }
        
        with patch('src.api.dependencies.get_sync_service', return_value=mock_sync_service), \
             patch('src.api.dependencies.get_db_session', return_value=mock_db_session), \
             patch('src.api.v1.sync_router.logger') as mock_logger:
            
            response = client_with_mocked_dependencies.post("/api/v1/model-garden/sync/all")
            
            assert response.status_code == 200
            
            # 验证性能日志被记录
            assert mock_logger.info.call_count >= 2  # 开始和完成日志
            
            # 查找完成日志
            completion_log_found = False
            for call in mock_logger.info.call_args_list:
                if "同步完成" in str(call):
                    completion_log_found = True
                    break
            
            assert completion_log_found, "未找到同步完成日志"
    
    def test_sync_all_none_request_with_details(
        self,
        client_with_mocked_dependencies,
        mock_sync_service,
        mock_db_session
    ):
        """测试None请求体但有details的情况"""
        
        mock_sync_service.sync_all.return_value = {
            "success": True,
            "details": {
                "projects": {
                    "data": [{
                        "id": "proj-001",
                        "project_name": "Test Project",
                        "project_code": "TEST",
                        "created_time": "2025-07-20T10:00:00Z",
                        "updated_time": "2025-07-20T10:00:00Z"
                    }]
                },
                "use_cases": {"data": []},
                "budgets": {"data": []},
                "models": {"data": []},
                "deployments": {"data": []},
                "pricing": {"data": []},
                "subscriptions": {"data": []},
                "limits": {"data": []}
            }
        }
        
        with patch('src.api.dependencies.get_sync_service', return_value=mock_sync_service), \
             patch('src.api.dependencies.get_db_session', return_value=mock_db_session):
            
            response = client_with_mocked_dependencies.post("/api/v1/model-garden/sync/all")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["projects"]) == 1
            assert data["projects"][0]["id"] == "proj-001"
    
    def test_sync_all_missing_totals(
        self,
        client_with_mocked_dependencies,
        mock_sync_service,
        mock_db_session
    ):
        """测试缺少totals的同步结果"""
        
        mock_sync_service.sync_all.return_value = {
            "success": True,
            "duration_seconds": 100,
            "details": {
                "projects": {"data": []},
                "use_cases": {"data": []},
                "budgets": {"data": []},
                "models": {"data": []},
                "deployments": {"data": []},
                "pricing": {"data": []},
                "subscriptions": {"data": []},
                "limits": {"data": []}
            }
        }
        
        with patch('src.api.dependencies.get_sync_service', return_value=mock_sync_service), \
             patch('src.api.dependencies.get_db_session', return_value=mock_db_session):
            
            response = client_with_mocked_dependencies.post("/api/v1/model-garden/sync/all")
            
            assert response.status_code == 200
            # 应该能处理缺少的totals字段
            data = response.json()
            assert all(data[key] == [] for key in ["projects", "use_cases", "budgets", "models", "model_deployments", "pricing", "use_case_llm_models", "limits"]) 