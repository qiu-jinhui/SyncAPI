"""
事件服务测试
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from src.services.event_service import EventService
from src.schemas.event_request import EventRequest


class TestEventService:
    """事件服务测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.mock_session = Mock(spec=Session)
        self.service = EventService(self.mock_session)
    
    def test_init_with_session(self):
        """测试带数据库会话初始化"""
        service = EventService(self.mock_session)
        assert service.db_session == self.mock_session
        assert service._repositories_initialized is True
    
    def test_init_without_session(self):
        """测试不带数据库会话初始化"""
        service = EventService()
        assert service.db_session is None
        assert service._repositories_initialized is False
    
    @pytest.mark.asyncio
    async def test_process_event_success(self):
        """测试成功处理事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="CREATE",
            entity_type="project",
            entity_id="proj123",
            payload={"project_name": "Test Project", "project_code": "TEST"},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        with patch.object(self.service.redis_service, 'get_cache') as mock_get_cache, \
             patch.object(self.service, '_dispatch_event') as mock_dispatch, \
             patch.object(self.service.redis_service, 'set_cache') as mock_set_cache, \
             patch.object(self.service.redis_service, 'publish_event') as mock_publish:
            
            mock_get_cache.return_value = None  # 事件未处理过
            mock_dispatch.return_value = {"success": True, "status": "created", "entity_id": "proj123"}
            
            result = await self.service.process_event(event_request)
            
            assert result["success"] is True
            assert result["status"] == "created"
            
            # 验证缓存和事件发布
            mock_set_cache.assert_called_once()
            mock_publish.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_event_already_processed(self):
        """测试处理已处理过的事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="CREATE",
            entity_type="project",
            entity_id="proj123",
            payload={"project_name": "Test Project"},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        with patch.object(self.service.redis_service, 'get_cache') as mock_get_cache:
            mock_get_cache.return_value = {"processed_at": "2023-01-01T00:00:00Z"}
            
            result = await self.service.process_event(event_request)
            
            assert result["success"] is True
            assert result["status"] == "already_processed"
            assert result["event_id"] == "evt123"
    
    @pytest.mark.asyncio
    async def test_process_event_failure(self):
        """测试处理事件失败"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="CREATE",
            entity_type="invalid",
            entity_id="proj123",
            payload={"project_name": "Test Project"},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        with patch.object(self.service.redis_service, 'get_cache') as mock_get_cache, \
             patch.object(self.service, '_dispatch_event') as mock_dispatch, \
             patch.object(self.service.redis_service, 'publish_event') as mock_publish:
            
            mock_get_cache.return_value = None
            mock_dispatch.side_effect = ValueError("不支持的实体类型: invalid")
            
            result = await self.service.process_event(event_request)
            
            assert result["success"] is False
            assert "error" in result
            
            # 验证发布失败事件
            call_args = mock_publish.call_args[0][1]
            assert call_args["status"] == "failed"
    
    @pytest.mark.asyncio
    async def test_dispatch_event_project(self):
        """测试分发项目事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="CREATE",
            entity_type="project",
            entity_id="proj123",
            payload={"project_name": "Test Project", "project_code": "TEST"},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        with patch.object(self.service, '_handle_project_event') as mock_handle:
            mock_handle.return_value = {"success": True, "status": "created"}
            
            result = await self.service._dispatch_event(event_request)
            
            assert result["success"] is True
            mock_handle.assert_called_once_with("CREATE", event_request)
    
    @pytest.mark.asyncio
    async def test_dispatch_event_unsupported_entity(self):
        """测试不支持的实体类型"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="CREATE",
            entity_type="unsupported",
            entity_id="123",
            payload={},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        with pytest.raises(ValueError, match="不支持的实体类型: unsupported"):
            await self.service._dispatch_event(event_request)
    
    @pytest.mark.asyncio
    async def test_handle_project_event_create(self):
        """测试处理项目创建事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="CREATE",
            entity_type="project",
            entity_id="proj123",
            payload={"project_name": "Test Project", "project_code": "TEST"},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        # 模拟项目仓储
        self.service.project_repo = Mock()
        mock_project = Mock()
        mock_project.id = "new-project-id"
        self.service.project_repo.create.return_value = mock_project
        
        result = await self.service._handle_project_event("CREATE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "created"
        assert result["entity_id"] == "new-project-id"
        
        self.service.project_repo.create.assert_called_once_with(**event_request.payload)
    
    @pytest.mark.asyncio
    async def test_handle_project_event_update(self):
        """测试处理项目更新事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="UPDATE",
            entity_type="project",
            entity_id="proj123",
            payload={"project_name": "Updated Project"},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        # 模拟项目仓储
        self.service.project_repo = Mock()
        mock_project = Mock()
        self.service.project_repo.update.return_value = mock_project
        
        result = await self.service._handle_project_event("UPDATE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "updated"
        assert result["entity_id"] == "proj123"
        
        self.service.project_repo.update.assert_called_once_with("proj123", **event_request.payload)
    
    @pytest.mark.asyncio
    async def test_handle_project_event_update_not_found(self):
        """测试更新不存在的项目"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="UPDATE",
            entity_type="project",
            entity_id="nonexistent",
            payload={"project_name": "Updated Project"},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        # 模拟项目不存在
        self.service.project_repo = Mock()
        self.service.project_repo.update.return_value = None
        
        result = await self.service._handle_project_event("UPDATE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "not_found"
        assert result["entity_id"] == "nonexistent"
    
    @pytest.mark.asyncio
    async def test_handle_project_event_delete(self):
        """测试处理项目删除事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="DELETE",
            entity_type="project",
            entity_id="proj123",
            payload={},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        # 模拟项目仓储
        self.service.project_repo = Mock()
        self.service.project_repo.delete.return_value = True
        
        result = await self.service._handle_project_event("DELETE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "deleted"
        assert result["entity_id"] == "proj123"
        
        self.service.project_repo.delete.assert_called_once_with("proj123")
    
    @pytest.mark.asyncio
    async def test_handle_project_event_unsupported_action(self):
        """测试不支持的项目事件类型"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="UNSUPPORTED",
            entity_type="project",
            entity_id="proj123",
            payload={},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        with pytest.raises(ValueError, match="不支持的事件类型: UNSUPPORTED"):
            await self.service._handle_project_event("UNSUPPORTED", event_request)
    
    @pytest.mark.asyncio
    async def test_handle_use_case_event_create(self):
        """测试处理用例创建事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="CREATE",
            entity_type="usecase",
            entity_id="uc123",
            payload={"use_case_name": "Test Use Case", "project_id": "proj123"},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        # 模拟用例仓储
        self.service.use_case_repo = Mock()
        mock_use_case = Mock()
        mock_use_case.id = "new-use-case-id"
        self.service.use_case_repo.create.return_value = mock_use_case
        
        result = await self.service._handle_use_case_event("CREATE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "created"
        assert result["entity_id"] == "new-use-case-id"
    
    @pytest.mark.asyncio
    async def test_handle_use_case_event_update(self):
        """测试处理用例更新事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="UPDATE",
            entity_type="usecase",
            entity_id="uc123",
            payload={"use_case_name": "Updated Use Case"},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.service.use_case_repo = Mock()
        mock_use_case = Mock()
        self.service.use_case_repo.update.return_value = mock_use_case
        
        result = await self.service._handle_use_case_event("UPDATE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "updated"
    
    @pytest.mark.asyncio
    async def test_handle_use_case_event_delete(self):
        """测试处理用例删除事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="DELETE",
            entity_type="usecase",
            entity_id="uc123",
            payload={},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.service.use_case_repo = Mock()
        self.service.use_case_repo.delete.return_value = True
        
        result = await self.service._handle_use_case_event("DELETE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "deleted"
    
    @pytest.mark.asyncio
    async def test_handle_budget_event_create_budget(self):
        """测试处理预算创建事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="CREATE",
            entity_type="budget",
            entity_id="budget123",
            payload={
                "type": "budget",
                "use_case_id": "uc123",
                "budget_cents": 10000,
                "currency": "USD"
            },
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        # 模拟预算仓储
        self.service.budget_repo = Mock()
        mock_budget = Mock()
        mock_budget.id = "new-budget-id"
        self.service.budget_repo.create.return_value = mock_budget
        
        result = await self.service._handle_budget_event("CREATE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "created"
        assert result["entity_id"] == "new-budget-id"
        
        self.service.budget_repo.create.assert_called_once_with(**event_request.payload)
    
    @pytest.mark.asyncio
    async def test_handle_budget_event_create_usage(self):
        """测试处理预算使用情况创建事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="CREATE",
            entity_type="budget",
            entity_id="usage123",
            payload={
                "type": "usage",
                "use_case_id": "uc123",
                "usage_period": "2023-01-01",
                "scope": "daily",
                "used_cents": 5000
            },
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        # 模拟预算仓储
        self.service.budget_repo = Mock()
        mock_usage = Mock()
        mock_usage.id = "new-usage-id"
        self.service.budget_repo.create_usage.return_value = mock_usage
        
        result = await self.service._handle_budget_event("CREATE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "created"
        assert result["entity_id"] == "new-usage-id"
        
        self.service.budget_repo.create_usage.assert_called_once_with(**event_request.payload)
    
    @pytest.mark.asyncio
    async def test_handle_budget_event_update_budget(self):
        """测试处理预算更新事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="UPDATE",
            entity_type="budget",
            entity_id="budget123",
            payload={
                "type": "budget",
                "budget_cents": 20000
            },
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.service.budget_repo = Mock()
        mock_budget = Mock()
        self.service.budget_repo.update.return_value = mock_budget
        
        result = await self.service._handle_budget_event("UPDATE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "updated"
    
    @pytest.mark.asyncio
    async def test_handle_budget_event_update_usage(self):
        """测试处理预算使用情况更新事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="UPDATE",
            entity_type="budget",
            entity_id="usage123",
            payload={
                "type": "usage",
                "used_cents": 6000
            },
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.service.budget_repo = Mock()
        mock_usage = Mock()
        self.service.budget_repo.update_usage.return_value = mock_usage
        
        result = await self.service._handle_budget_event("UPDATE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "updated"
    
    @pytest.mark.asyncio
    async def test_handle_budget_event_delete_budget(self):
        """测试处理预算删除事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="DELETE",
            entity_type="budget",
            entity_id="budget123",
            payload={"type": "budget"},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.service.budget_repo = Mock()
        self.service.budget_repo.delete.return_value = True
        
        result = await self.service._handle_budget_event("DELETE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "deleted"
    
    @pytest.mark.asyncio
    async def test_handle_budget_event_delete_usage(self):
        """测试处理预算使用情况删除事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="DELETE",
            entity_type="budget",
            entity_id="usage123",
            payload={"type": "usage"},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.service.budget_repo = Mock()
        self.service.budget_repo.delete_usage.return_value = True
        
        result = await self.service._handle_budget_event("DELETE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "deleted"
    
    @pytest.mark.asyncio
    async def test_handle_model_event_create(self):
        """测试处理模型创建事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="CREATE",
            entity_type="model",
            entity_id="model123",
            payload={
                "model_name": "gpt-4",
                "model_provider": "openai"
            },
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        # 模拟模型仓储
        self.service.model_repo = Mock()
        mock_model = Mock()
        mock_model.id = "new-model-id"
        self.service.model_repo.create.return_value = mock_model
        
        result = await self.service._handle_model_event("CREATE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "created"
        assert result["entity_id"] == "new-model-id"
    
    @pytest.mark.asyncio
    async def test_handle_model_event_update(self):
        """测试处理模型更新事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="UPDATE",
            entity_type="model",
            entity_id="model123",
            payload={"model_name": "gpt-4-turbo"},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.service.model_repo = Mock()
        mock_model = Mock()
        self.service.model_repo.update.return_value = mock_model
        
        result = await self.service._handle_model_event("UPDATE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "updated"
    
    @pytest.mark.asyncio
    async def test_handle_model_event_delete(self):
        """测试处理模型删除事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="DELETE",
            entity_type="model",
            entity_id="model123",
            payload={},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.service.model_repo = Mock()
        self.service.model_repo.delete.return_value = True
        
        result = await self.service._handle_model_event("DELETE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "deleted"
    
    @pytest.mark.asyncio
    async def test_handle_deployment_event_create(self):
        """测试处理部署创建事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="CREATE",
            entity_type="deployment",
            entity_id="deploy123",
            payload={
                "model_id": "model123",
                "deployment_name": "prod-deployment",
                "endpoint": "https://api.example.com"
            },
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        # 模拟部署仓储
        self.service.deployment_repo = Mock()
        mock_deployment = Mock()
        mock_deployment.id = "new-deployment-id"
        self.service.deployment_repo.create.return_value = mock_deployment
        
        result = await self.service._handle_deployment_event("CREATE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "created"
        assert result["entity_id"] == "new-deployment-id"
    
    @pytest.mark.asyncio
    async def test_handle_deployment_event_update(self):
        """测试处理部署更新事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="UPDATE",
            entity_type="deployment",
            entity_id="deploy123",
            payload={"endpoint": "https://api-v2.example.com"},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.service.deployment_repo = Mock()
        mock_deployment = Mock()
        self.service.deployment_repo.update.return_value = mock_deployment
        
        result = await self.service._handle_deployment_event("UPDATE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "updated"
    
    @pytest.mark.asyncio
    async def test_handle_deployment_event_delete(self):
        """测试处理部署删除事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="DELETE",
            entity_type="deployment",
            entity_id="deploy123",
            payload={},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.service.deployment_repo = Mock()
        self.service.deployment_repo.delete.return_value = True
        
        result = await self.service._handle_deployment_event("DELETE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "deleted"
    
    @pytest.mark.asyncio
    async def test_handle_pricing_event_create(self):
        """测试处理定价创建事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="CREATE",
            entity_type="pricing",
            entity_id="price123",
            payload={
                "model_id": "model123",
                "pricing_type": "input",
                "price_per_unit": 0.001
            },
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        # 模拟定价仓储
        self.service.pricing_repo = Mock()
        mock_pricing = Mock()
        mock_pricing.id = "new-pricing-id"
        self.service.pricing_repo.create.return_value = mock_pricing
        
        result = await self.service._handle_pricing_event("CREATE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "created"
        assert result["entity_id"] == "new-pricing-id"
    
    @pytest.mark.asyncio
    async def test_handle_pricing_event_update(self):
        """测试处理定价更新事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="UPDATE",
            entity_type="pricing",
            entity_id="price123",
            payload={"price_per_unit": 0.002},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.service.pricing_repo = Mock()
        mock_pricing = Mock()
        self.service.pricing_repo.update.return_value = mock_pricing
        
        result = await self.service._handle_pricing_event("UPDATE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "updated"
    
    @pytest.mark.asyncio
    async def test_handle_pricing_event_delete(self):
        """测试处理定价删除事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="DELETE",
            entity_type="pricing",
            entity_id="price123",
            payload={},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.service.pricing_repo = Mock()
        self.service.pricing_repo.delete.return_value = True
        
        result = await self.service._handle_pricing_event("DELETE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "deleted"
    
    @pytest.mark.asyncio
    async def test_handle_subscription_event_create(self):
        """测试处理订阅创建事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="CREATE",
            entity_type="subscription",
            entity_id="sub123",
            payload={
                "use_case_id": "uc123",
                "model_id": "model123"
            },
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        # 模拟订阅仓储
        self.service.subscription_repo = Mock()
        mock_subscription = Mock()
        mock_subscription.id = "new-subscription-id"
        self.service.subscription_repo.create.return_value = mock_subscription
        
        result = await self.service._handle_subscription_event("CREATE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "created"
        assert result["entity_id"] == "new-subscription-id"
    
    @pytest.mark.asyncio
    async def test_handle_subscription_event_update(self):
        """测试处理订阅更新事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="UPDATE",
            entity_type="subscription",
            entity_id="sub123",
            payload={"alias": "updated-alias"},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.service.subscription_repo = Mock()
        mock_subscription = Mock()
        self.service.subscription_repo.update.return_value = mock_subscription
        
        result = await self.service._handle_subscription_event("UPDATE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "updated"
    
    @pytest.mark.asyncio
    async def test_handle_subscription_event_delete(self):
        """测试处理订阅删除事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="DELETE",
            entity_type="subscription",
            entity_id="sub123",
            payload={},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.service.subscription_repo = Mock()
        self.service.subscription_repo.delete.return_value = True
        
        result = await self.service._handle_subscription_event("DELETE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "deleted"
    
    @pytest.mark.asyncio
    async def test_handle_limit_event_create_limit(self):
        """测试处理限制创建事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="CREATE",
            entity_type="limit",
            entity_id="limit123",
            payload={
                "type": "limit",
                "use_case_id": "uc123",
                "model_id": "model123",
                "limit_type": "request_per_minute",
                "limit_value": 100
            },
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        # 模拟限制仓储
        self.service.limit_repo = Mock()
        mock_limit = Mock()
        mock_limit.id = "new-limit-id"
        self.service.limit_repo.create.return_value = mock_limit
        
        result = await self.service._handle_limit_event("CREATE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "created"
        assert result["entity_id"] == "new-limit-id"
    
    @pytest.mark.asyncio
    async def test_handle_limit_event_create_usage(self):
        """测试处理限制使用情况创建事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="CREATE",
            entity_type="limit",
            entity_id="usage123",
            payload={
                "type": "usage",
                "limit_id": "limit123",
                "usage_period": "2023-01-01",
                "scope": "daily",
                "used_value": 50
            },
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        # 模拟限制仓储
        self.service.limit_repo = Mock()
        mock_usage = Mock()
        mock_usage.id = "new-usage-id"
        self.service.limit_repo.create_usage.return_value = mock_usage
        
        result = await self.service._handle_limit_event("CREATE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "created"
        assert result["entity_id"] == "new-usage-id"
    
    @pytest.mark.asyncio
    async def test_handle_limit_event_update_limit(self):
        """测试处理限制更新事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="UPDATE",
            entity_type="limit",
            entity_id="limit123",
            payload={
                "type": "limit",
                "limit_value": 200
            },
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.service.limit_repo = Mock()
        mock_limit = Mock()
        self.service.limit_repo.update.return_value = mock_limit
        
        result = await self.service._handle_limit_event("UPDATE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "updated"
    
    @pytest.mark.asyncio
    async def test_handle_limit_event_update_usage(self):
        """测试处理限制使用情况更新事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="UPDATE",
            entity_type="limit",
            entity_id="usage123",
            payload={
                "type": "usage",
                "used_value": 75
            },
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.service.limit_repo = Mock()
        mock_usage = Mock()
        self.service.limit_repo.update_usage.return_value = mock_usage
        
        result = await self.service._handle_limit_event("UPDATE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "updated"
    
    @pytest.mark.asyncio
    async def test_handle_limit_event_delete_limit(self):
        """测试处理限制删除事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="DELETE",
            entity_type="limit",
            entity_id="limit123",
            payload={"type": "limit"},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.service.limit_repo = Mock()
        self.service.limit_repo.delete.return_value = True
        
        result = await self.service._handle_limit_event("DELETE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "deleted"
    
    @pytest.mark.asyncio
    async def test_handle_limit_event_delete_usage(self):
        """测试处理限制使用情况删除事件"""
        event_request = EventRequest(
            event_id="evt123",
            event_type="DELETE",
            entity_type="limit",
            entity_id="usage123",
            payload={"type": "usage"},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.service.limit_repo = Mock()
        self.service.limit_repo.delete_usage.return_value = True
        
        result = await self.service._handle_limit_event("DELETE", event_request)
        
        assert result["success"] is True
        assert result["status"] == "deleted" 
    
    @pytest.mark.asyncio
    async def test_process_event_with_session_parameter(self):
        """测试带session参数处理事件"""
        mock_session = Mock()
        service = EventService()  # 不带session初始化
        
        event_request = EventRequest(
            event_id="evt123",
            event_type="CREATE",
            entity_type="project",
            entity_id="proj123",
            payload={"project_name": "Test Project"},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        with patch.object(service, '_init_repositories') as mock_init, \
             patch.object(service.redis_service, 'get_cache') as mock_get_cache, \
             patch.object(service, '_dispatch_event') as mock_dispatch, \
             patch.object(service.redis_service, 'set_cache'), \
             patch.object(service.redis_service, 'publish_event'):
            
            mock_get_cache.return_value = None
            mock_dispatch.return_value = {"success": True, "status": "created"}
            
            await service.process_event(event_request, session=mock_session)
            
            mock_init.assert_called_once_with(mock_session)
    
    @pytest.mark.asyncio
    async def test_handle_unsupported_event_types(self):
        """测试处理不支持的事件类型"""
        event_types = ["use_case", "model", "deployment", "pricing", "subscription", "limit"]
        
        for entity_type in event_types:
            event_request = EventRequest(
                event_id="evt123",
                event_type="UNSUPPORTED_ACTION",
                entity_type=entity_type,
                entity_id="123",
                payload={},
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
            with pytest.raises(ValueError, match="不支持的事件类型: UNSUPPORTED_ACTION"):
                if entity_type == "use_case":
                    await self.service._handle_use_case_event("UNSUPPORTED_ACTION", event_request)
                elif entity_type == "model":
                    await self.service._handle_model_event("UNSUPPORTED_ACTION", event_request)
                elif entity_type == "deployment":
                    await self.service._handle_deployment_event("UNSUPPORTED_ACTION", event_request)
                elif entity_type == "pricing":
                    await self.service._handle_pricing_event("UNSUPPORTED_ACTION", event_request)
                elif entity_type == "subscription":
                    await self.service._handle_subscription_event("UNSUPPORTED_ACTION", event_request)
                elif entity_type == "limit":
                    await self.service._handle_limit_event("UNSUPPORTED_ACTION", event_request) 