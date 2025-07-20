"""
全局测试配置文件
提供API测试的fixtures和mock配置
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from datetime import datetime

from src.main import app
from src.api.dependencies import get_db, get_event_service, get_sync_service
from src.services.event_service import EventService
from src.services.sync_service import SyncService
from src.services.model_garden_client import ModelGardenClient
from src.services.redis_service import RedisService


@pytest.fixture
def test_client():
    """测试客户端fixture"""
    return TestClient(app)


@pytest.fixture
def mock_db_session():
    """模拟数据库会话"""
    mock_session = Mock()
    mock_session.commit = Mock()
    mock_session.rollback = Mock()
    mock_session.close = Mock()
    return mock_session


@pytest.fixture
def mock_redis_service():
    """模拟Redis服务"""
    mock_redis = Mock(spec=RedisService)
    mock_redis.publish_event = AsyncMock()
    mock_redis.set_cache = AsyncMock()
    mock_redis.get_cache = AsyncMock()
    return mock_redis


@pytest.fixture
def mock_event_service(mock_db_session):
    """模拟事件服务"""
    mock_service = Mock(spec=EventService)
    mock_service.process_event = AsyncMock(return_value=True)
    return mock_service


@pytest.fixture
def mock_sync_service(mock_db_session):
    """模拟同步服务"""
    mock_service = Mock(spec=SyncService)
    mock_service.sync_all = AsyncMock(return_value={
        "success": True,
        "start_time": "2025-07-20T10:00:00Z",
        "end_time": "2025-07-20T10:05:00Z",
        "duration_seconds": 300,
        "totals": {
            "created": 5,
            "updated": 3,
            "errors": 0
        }
    })
    mock_service.redis_service = Mock()
    return mock_service


@pytest.fixture
def mock_model_garden_client():
    """模拟Model Garden客户端"""
    mock_client = Mock(spec=ModelGardenClient)
    mock_client.sync_all = AsyncMock(return_value={
        "projects": [
            {
                "id": "proj-001",
                "project_name": "Credit AI",
                "project_code": "CREDIT_AI",
                "created_time": "2025-01-01T00:00:00Z",
                "updated_time": "2025-07-10T10:00:00Z"
            }
        ],
        "use_cases": [
            {
                "id": "uc-001",
                "project_id": "proj-001",
                "use_case_name": "fraud_detection",
                "ad_group": "ad_fraud",
                "is_active": True,
                "created_time": "2025-01-05T00:00:00Z",
                "updated_time": "2025-07-10T12:00:00Z"
            }
        ],
        "budgets": [],
        "models": [],
        "model_deployments": [],
        "pricing": [],
        "use_case_llm_models": [],
        "limits": []
    })
    return mock_client


@pytest.fixture
def sample_event_request():
    """示例事件请求数据"""
    return {
        "event_id": "evt-001",
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


@pytest.fixture
def sample_sync_request():
    """示例同步请求数据"""
    return {
        "updated_since": "2025-07-01T00:00:00Z"
    }


@pytest.fixture
def client_with_mocked_dependencies(
    test_client, 
    mock_db_session, 
    mock_event_service, 
    mock_sync_service
):
    """带有模拟依赖的测试客户端"""
    
    def override_get_db():
        return mock_db_session
    
    def override_get_event_service():
        return mock_event_service
    
    def override_get_sync_service():
        return mock_sync_service
    
    # 重写依赖注入
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_event_service] = override_get_event_service
    app.dependency_overrides[get_sync_service] = override_get_sync_service
    
    yield test_client
    
    # 清理依赖重写
    app.dependency_overrides.clear()


@pytest.fixture
def mock_asyncio_create_task():
    """模拟asyncio.create_task"""
    with patch('asyncio.create_task') as mock_task:
        mock_task.return_value = Mock()
        yield mock_task 