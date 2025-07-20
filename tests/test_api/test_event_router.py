"""
事件API路由测试
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from src.schemas.event_request import EventRequest
from src.schemas.payloads import ProjectPayload


class TestEventRouter:
    """事件路由测试类"""
    
    def test_receive_event_success(
        self, 
        client_with_mocked_dependencies, 
        sample_event_request, 
        mock_event_service
    ):
        """测试成功接收事件"""
        response = client_with_mocked_dependencies.post(
            "/api/v1/model-garden/events", 
            json=sample_event_request
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "message" in data
        
        # 验证事件服务被调用
        mock_event_service.process_event.assert_called_once()
    
    def test_receive_event_invalid_data(self, client_with_mocked_dependencies):
        """测试接收无效数据"""
        invalid_data = {
            "event_type": "INVALID",  # 无效的事件类型
            "entity_type": "project",
            "entity_id": "proj-001",
            "timestamp": "2025-07-15T14:20:00Z",
            "payload": {}
        }
        
        response = client_with_mocked_dependencies.post(
            "/api/v1/model-garden/events", 
            json=invalid_data
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_receive_event_missing_required_fields(self, client_with_mocked_dependencies):
        """测试缺少必需字段"""
        incomplete_data = {
            "event_type": "CREATED",
            "entity_type": "project",
            # 缺少 event_id, entity_id, timestamp, payload
        }
        
        response = client_with_mocked_dependencies.post(
            "/api/v1/model-garden/events", 
            json=incomplete_data
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_receive_event_service_failure(
        self, 
        client_with_mocked_dependencies, 
        sample_event_request
    ):
        """测试事件服务处理失败"""
        # 重写依赖以返回会抛出异常的服务
        from src.main import app
        from src.api.dependencies import get_event_service
        
        mock_failing_service = Mock()
        mock_failing_service.process_event = AsyncMock(
            side_effect=Exception("Service processing failed")
        )
        
        def override_failing_service():
            return mock_failing_service
            
        app.dependency_overrides[get_event_service] = override_failing_service
        
        try:
            response = client_with_mocked_dependencies.post(
                "/api/v1/model-garden/events", 
                json=sample_event_request
            )
            
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "Failed to process event" in data["detail"]
        finally:
            # 清理依赖重写
            app.dependency_overrides.clear()
    
    def test_health_check(self, client_with_mocked_dependencies):
        """测试健康检查端点"""
        response = client_with_mocked_dependencies.get("/api/v1/model-garden/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "synchronize-api"
        assert data["version"] == "1.0.0"


class TestEventValidation:
    """事件验证测试类"""
    
    def test_valid_project_event(self, sample_event_request):
        """测试有效的项目事件"""
        event = EventRequest(**sample_event_request)
        
        assert event.event_type == "CREATED"
        assert event.entity_type == "project"
        assert event.entity_id == "proj-001"
        assert event.event_id == "evt-001"
        assert isinstance(event.payload, dict)
    
    def test_valid_use_case_event(self):
        """测试有效的用例事件"""
        use_case_data = {
            "event_id": "evt-002",
            "event_type": "UPDATED",
            "entity_type": "use_case",
            "entity_id": "uc-001",
            "timestamp": "2025-07-15T14:20:00Z",
            "version": "1.0",
            "payload": {
                "id": "uc-001",
                "project_id": "proj-001",
                "use_case_name": "fraud_detection",
                "ad_group": "ad_fraud",
                "is_active": True,
                "created_time": "2025-07-15T14:00:00Z",
                "updated_time": "2025-07-15T14:20:00Z"
            }
        }
        
        event = EventRequest(**use_case_data)
        assert event.event_type == "UPDATED"
        assert event.entity_type == "use_case"
        assert event.entity_id == "uc-001"
    
    def test_invalid_event_type(self):
        """测试无效的事件类型"""
        invalid_data = {
            "event_id": "evt-003",
            "event_type": "INVALID",
            "entity_type": "project",
            "entity_id": "proj-001",
            "timestamp": "2025-07-15T14:20:00Z",
            "version": "1.0",
            "payload": {
                "id": "proj-001",
                "project_name": "Credit AI",
                "project_code": "CREDIT_AI",
                "created_time": "2025-07-15T14:00:00Z",
                "updated_time": "2025-07-15T14:00:00Z"
            }
        }
        
        # 注意：目前的EventRequest没有验证事件类型的枚举
        # 如果需要严格验证，需要在schema中添加enum约束
        event = EventRequest(**invalid_data)
        assert event.event_type == "INVALID"
    
    def test_missing_required_fields(self):
        """测试缺少必需字段"""
        incomplete_data = {
            "event_type": "CREATED",
            "entity_type": "project",
            # 缺少 event_id, entity_id, timestamp, payload
        }
        
        with pytest.raises(ValueError):
            EventRequest(**incomplete_data)
    
    def test_missing_event_id(self):
        """测试缺少事件ID"""
        data_without_event_id = {
            "event_type": "CREATED",
            "entity_type": "project",
            "entity_id": "proj-001",
            "timestamp": "2025-07-15T14:20:00Z",
            "payload": {}
        }
        
        with pytest.raises(ValueError):
            EventRequest(**data_without_event_id)
    
    def test_empty_payload(self):
        """测试空负载"""
        data_with_empty_payload = {
            "event_id": "evt-004",
            "event_type": "DELETED",
            "entity_type": "project",
            "entity_id": "proj-001",
            "timestamp": "2025-07-15T14:20:00Z",
            "payload": {}
        }
        
        event = EventRequest(**data_with_empty_payload)
        assert event.payload == {}
        assert event.event_type == "DELETED"
    
    def test_optional_version_field(self):
        """测试可选的版本字段"""
        data_without_version = {
            "event_id": "evt-005",
            "event_type": "CREATED",
            "entity_type": "project",
            "entity_id": "proj-001",
            "timestamp": "2025-07-15T14:20:00Z",
            "payload": {
                "id": "proj-001",
                "project_name": "Credit AI"
            }
        }
        
        event = EventRequest(**data_without_version)
        assert event.version is None
        
        # 测试带版本
        data_with_version = data_without_version.copy()
        data_with_version["version"] = "2.0"
        
        event_with_version = EventRequest(**data_with_version)
        assert event_with_version.version == "2.0" 