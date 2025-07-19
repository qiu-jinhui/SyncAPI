"""
事件API路由测试
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from src.main import app
from src.schemas.event_request import EventRequest
from src.schemas.payloads import ProjectPayload

client = TestClient(app)

@pytest.fixture
def mock_event_service():
    """模拟事件服务"""
    mock_service = Mock()
    mock_service.process_event = AsyncMock(return_value=True)
    return mock_service

@pytest.fixture
def sample_event_request():
    """示例事件请求数据"""
    return {
        "event_type": "CREATED",
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

class TestEventRouter:
    """事件路由测试类"""
    
    def test_receive_event_success(self, sample_event_request, mock_event_service):
        """测试成功接收事件"""
        # 这里需要模拟依赖注入
        # 在实际测试中，需要配置依赖注入来使用mock_event_service
        
        response = client.post("/api/v1/model-garden/events", json=sample_event_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "message" in data
    
    def test_receive_event_invalid_data(self):
        """测试接收无效数据"""
        invalid_data = {
            "event_type": "INVALID",
            "entity_type": "project",
            "entity_id": "proj-001",
            "timestamp": "2025-07-15T14:20:00Z",
            "payload": {}
        }
        
        response = client.post("/api/v1/model-garden/events", json=invalid_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_health_check(self):
        """测试健康检查端点"""
        response = client.get("/api/v1/model-garden/health")
        
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
        assert isinstance(event.payload, ProjectPayload)
    
    def test_invalid_event_type(self):
        """测试无效的事件类型"""
        invalid_data = {
            "event_type": "INVALID",
            "entity_type": "project",
            "entity_id": "proj-001",
            "timestamp": "2025-07-15T14:20:00Z",
            "payload": {
                "id": "proj-001",
                "project_name": "Credit AI",
                "project_code": "CREDIT_AI",
                "created_time": "2025-07-15T14:00:00Z",
                "updated_time": "2025-07-15T14:00:00Z"
            }
        }
        
        with pytest.raises(ValueError):
            EventRequest(**invalid_data)
    
    def test_missing_required_fields(self):
        """测试缺少必需字段"""
        incomplete_data = {
            "event_type": "CREATED",
            "entity_type": "project",
            # 缺少 entity_id, timestamp, payload
        }
        
        with pytest.raises(ValueError):
            EventRequest(**incomplete_data) 