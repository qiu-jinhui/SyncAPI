"""
同步API路由测试
测试全量同步和状态查询端点
"""

import pytest
from unittest.mock import patch, Mock, AsyncMock
from fastapi import HTTPException
from datetime import datetime

from src.schemas.sync_request import SyncRequest
from src.schemas.sync_response import SyncResponse
from src.services.model_garden_client import ModelGardenClient


class TestSyncRouter:
    """同步路由测试类"""
    
    def test_sync_all_success_without_request_body(
        self, 
        client_with_mocked_dependencies,
        mock_model_garden_client
    ):
        """测试不带请求体的全量同步成功"""
        with patch('src.api.v1.sync_router.ModelGardenClient', return_value=mock_model_garden_client):
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
            
            # 验证Model Garden客户端被调用
            mock_model_garden_client.sync_all.assert_called_once_with(None)
    
    def test_sync_all_success_with_request_body(
        self, 
        client_with_mocked_dependencies,
        mock_model_garden_client,
        sample_sync_request
    ):
        """测试带请求体的全量同步成功"""
        with patch('src.api.v1.sync_router.ModelGardenClient', return_value=mock_model_garden_client):
            response = client_with_mocked_dependencies.post(
                "/api/v1/model-garden/sync/all",
                json=sample_sync_request
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # 验证响应结构
            assert "projects" in data
            assert len(data["projects"]) == 1
            
            # 验证Model Garden客户端被调用时传入了updated_since参数
            mock_model_garden_client.sync_all.assert_called_once()
            call_args = mock_model_garden_client.sync_all.call_args[0]
            assert call_args[0] is not None  # updated_since参数不为None
    
    def test_sync_all_success_with_empty_request_body(
        self, 
        client_with_mocked_dependencies,
        mock_model_garden_client
    ):
        """测试空请求体的全量同步成功"""
        with patch('src.api.v1.sync_router.ModelGardenClient', return_value=mock_model_garden_client):
            response = client_with_mocked_dependencies.post(
                "/api/v1/model-garden/sync/all",
                json={}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "projects" in data
            
            # 验证Model Garden客户端被调用时updated_since为None
            mock_model_garden_client.sync_all.assert_called_once_with(None)
    
    def test_sync_all_with_background_task(
        self, 
        client_with_mocked_dependencies,
        mock_model_garden_client,
        mock_sync_service,
        mock_asyncio_create_task
    ):
        """测试后台同步任务启动"""
        with patch('src.api.v1.sync_router.ModelGardenClient', return_value=mock_model_garden_client):
            response = client_with_mocked_dependencies.post("/api/v1/model-garden/sync/all")
            
            assert response.status_code == 200
            
            # 验证后台任务被创建
            mock_asyncio_create_task.assert_called_once()
            
            # 验证同步服务的sync_all方法会被调用
            # (虽然是异步的，但在测试中我们可以验证task的创建)
    
    def test_sync_all_background_task_failure(
        self, 
        client_with_mocked_dependencies,
        mock_model_garden_client
    ):
        """测试后台任务启动失败"""
        with patch('src.api.v1.sync_router.ModelGardenClient', return_value=mock_model_garden_client), \
             patch('asyncio.create_task', side_effect=Exception("Task creation failed")):
            
            # 即使后台任务失败，API仍应成功返回
            response = client_with_mocked_dependencies.post("/api/v1/model-garden/sync/all")
            
            assert response.status_code == 200
            data = response.json()
            assert "projects" in data
    
    def test_sync_all_model_garden_client_failure(
        self, 
        client_with_mocked_dependencies
    ):
        """测试Model Garden客户端调用失败"""
        mock_client = Mock()
        mock_client.sync_all = AsyncMock(side_effect=Exception("API call failed"))
        
        with patch('src.api.v1.sync_router.ModelGardenClient', return_value=mock_client):
            response = client_with_mocked_dependencies.post("/api/v1/model-garden/sync/all")
            
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "同步失败" in data["detail"]
    
    def test_sync_all_http_exception(
        self, 
        client_with_mocked_dependencies
    ):
        """测试HTTP异常处理"""
        mock_client = Mock()
        mock_client.sync_all = AsyncMock(side_effect=HTTPException(
            status_code=503, 
            detail="Service unavailable"
        ))
        
        with patch('src.api.v1.sync_router.ModelGardenClient', return_value=mock_client):
            response = client_with_mocked_dependencies.post("/api/v1/model-garden/sync/all")
            
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
    
    def test_sync_all_invalid_request_data(self, client_with_mocked_dependencies):
        """测试无效的请求数据"""
        invalid_data = {
            "updated_since": "invalid-date-format"
        }
        
        response = client_with_mocked_dependencies.post(
            "/api/v1/model-garden/sync/all",
            json=invalid_data
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_get_sync_status_success(
        self, 
        client_with_mocked_dependencies,
        mock_sync_service
    ):
        """测试获取同步状态成功"""
        # 确保redis_service没有connection_failed属性
        mock_redis_service = Mock()
        # 明确删除可能存在的connection_failed属性
        if hasattr(mock_redis_service, 'connection_failed'):
            delattr(mock_redis_service, 'connection_failed')
        mock_sync_service.redis_service = mock_redis_service
        
        response = client_with_mocked_dependencies.get("/api/v1/model-garden/sync/status")
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证响应结构
        assert "status" in data
        assert "service" in data
        assert "version" in data
        assert "last_sync" in data
        assert "sync_in_progress" in data
        
        # 验证具体值
        assert data["status"] == "healthy"
        assert data["service"] == "synchronize-api"
        assert data["version"] == "1.0.0"
    
    def test_get_sync_status_service_failure(
        self, 
        client_with_mocked_dependencies,
        mock_sync_service
    ):
        """测试同步状态服务失败"""
        # 设置redis_service有connection_failed属性，触发异常
        mock_redis_service = Mock()
        mock_redis_service.connection_failed = Exception("Redis connection failed")
        mock_sync_service.redis_service = mock_redis_service
        
        response = client_with_mocked_dependencies.get("/api/v1/model-garden/sync/status")
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "获取状态失败" in data["detail"]
    
    def test_get_sync_status_non_exception_failure(
        self, 
        client_with_mocked_dependencies,
        mock_sync_service
    ):
        """测试同步状态服务有非异常类型的连接失败"""
        # 设置redis_service有connection_failed属性，但不是异常类型
        mock_redis_service = Mock()
        mock_redis_service.connection_failed = "not an exception"
        mock_sync_service.redis_service = mock_redis_service
        
        response = client_with_mocked_dependencies.get("/api/v1/model-garden/sync/status")
        
        # 应该抛出TypeError因为试图raise一个非异常对象
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "获取状态失败" in data["detail"]


class TestSyncValidation:
    """同步请求验证测试类"""
    
    def test_valid_sync_request(self):
        """测试有效的同步请求"""
        valid_data = {
            "updated_since": "2025-07-01T00:00:00Z"
        }
        
        request = SyncRequest(**valid_data)
        assert request.updated_since.year == 2025
        assert request.updated_since.month == 7
        assert request.updated_since.day == 1
    
    def test_sync_request_without_updated_since(self):
        """测试不带updated_since的同步请求"""
        empty_data = {}
        
        request = SyncRequest(**empty_data)
        assert request.updated_since is None
    
    def test_sync_request_none_updated_since(self):
        """测试updated_since为None的同步请求"""
        data = {"updated_since": None}
        
        request = SyncRequest(**data)
        assert request.updated_since is None
    
    def test_invalid_datetime_format(self):
        """测试无效的日期时间格式"""
        invalid_data = {
            "updated_since": "invalid-date"
        }
        
        with pytest.raises(ValueError):
            SyncRequest(**invalid_data)
    
    def test_sync_response_creation(self):
        """测试同步响应创建"""
        response_data = {
            "projects": [
                {
                    "id": "proj-001",
                    "project_name": "Test Project",
                    "project_code": "TEST",
                    "created_time": datetime.now(),
                    "updated_time": datetime.now()
                }
            ],
            "use_cases": [],
            "budgets": [],
            "models": [],
            "model_deployments": [],
            "pricing": [],
            "use_case_llm_models": [],
            "limits": []
        }
        
        response = SyncResponse(**response_data)
        assert len(response.projects) == 1
        assert response.projects[0].id == "proj-001"
        assert len(response.use_cases) == 0
    
    def test_sync_response_empty_lists(self):
        """测试空列表的同步响应"""
        response = SyncResponse()
        
        assert len(response.projects) == 0
        assert len(response.use_cases) == 0
        assert len(response.budgets) == 0
        assert len(response.models) == 0
        assert len(response.model_deployments) == 0
        assert len(response.pricing) == 0
        assert len(response.use_case_llm_models) == 0
        assert len(response.limits) == 0 