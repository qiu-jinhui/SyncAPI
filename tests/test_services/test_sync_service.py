"""
同步服务测试
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from src.services.sync_service import SyncService


class TestSyncService:
    """同步服务测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.mock_session = Mock(spec=Session)
        self.service = SyncService(self.mock_session)
    
    def test_init_with_session(self):
        """测试带数据库会话初始化"""
        service = SyncService(self.mock_session)
        assert service.db_session == self.mock_session
        assert service._repositories_initialized is True
    
    def test_init_without_session(self):
        """测试不带数据库会话初始化"""
        service = SyncService()
        assert service.db_session is None
        assert service._repositories_initialized is False
    
    @pytest.mark.asyncio
    async def test_sync_all_success(self):
        """测试成功的全量同步"""
        # 模拟Model Garden API返回的数据
        mock_sync_data = {
            "projects": [
                {"project_name": "Test Project", "project_code": "TEST"}
            ],
            "use_cases": [
                {"use_case_name": "Test Use Case", "project_id": "proj1"}
            ],
            "budgets": [],
            "models": [],
            "model_deployments": [],
            "pricing": [],
            "use_case_llm_models": [],
            "limits": []
        }
        
        # 模拟各个同步方法的返回结果
        mock_sync_results = {
            "projects": {"created": 1, "updated": 0, "errors": 0},
            "use_cases": {"created": 1, "updated": 0, "errors": 0},
            "budgets": {"created": 0, "updated": 0, "errors": 0},
            "models": {"created": 0, "updated": 0, "errors": 0},
            "deployments": {"created": 0, "updated": 0, "errors": 0},
            "pricing": {"created": 0, "updated": 0, "errors": 0},
            "subscriptions": {"created": 0, "updated": 0, "errors": 0},
            "limits": {"created": 0, "updated": 0, "errors": 0}
        }
        
        with patch.object(self.service.model_garden_client, 'sync_all') as mock_sync_all, \
             patch.object(self.service, '_sync_projects') as mock_sync_projects, \
             patch.object(self.service, '_sync_use_cases') as mock_sync_use_cases, \
             patch.object(self.service, '_sync_budgets') as mock_sync_budgets, \
             patch.object(self.service, '_sync_models') as mock_sync_models, \
             patch.object(self.service, '_sync_deployments') as mock_sync_deployments, \
             patch.object(self.service, '_sync_pricing') as mock_sync_pricing, \
             patch.object(self.service, '_sync_subscriptions') as mock_sync_subscriptions, \
             patch.object(self.service, '_sync_limits') as mock_sync_limits, \
             patch.object(self.service.redis_service, 'set_cache') as mock_set_cache, \
             patch.object(self.service.redis_service, 'publish_event') as mock_publish_event:
            
            mock_sync_all.return_value = mock_sync_data
            mock_sync_projects.return_value = mock_sync_results["projects"]
            mock_sync_use_cases.return_value = mock_sync_results["use_cases"]
            mock_sync_budgets.return_value = mock_sync_results["budgets"]
            mock_sync_models.return_value = mock_sync_results["models"]
            mock_sync_deployments.return_value = mock_sync_results["deployments"]
            mock_sync_pricing.return_value = mock_sync_results["pricing"]
            mock_sync_subscriptions.return_value = mock_sync_results["subscriptions"]
            mock_sync_limits.return_value = mock_sync_results["limits"]
            
            result = await self.service.sync_all()
            
            assert result["success"] is True
            assert result["totals"]["created"] == 2
            assert result["totals"]["updated"] == 0
            assert result["totals"]["errors"] == 0
            assert "duration_seconds" in result
            
            # 验证缓存和事件发布
            mock_set_cache.assert_called_once()
            mock_publish_event.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_sync_all_with_updated_since(self):
        """测试增量同步"""
        updated_since = datetime(2023, 1, 1, tzinfo=timezone.utc)
        mock_sync_data = {"projects": [], "use_cases": []}
        
        with patch.object(self.service.model_garden_client, 'sync_all') as mock_sync_all, \
             patch.object(self.service, '_sync_projects') as mock_sync_projects, \
             patch.object(self.service, '_sync_use_cases') as mock_sync_use_cases, \
             patch.object(self.service, '_sync_budgets') as mock_sync_budgets, \
             patch.object(self.service, '_sync_models') as mock_sync_models, \
             patch.object(self.service, '_sync_deployments') as mock_sync_deployments, \
             patch.object(self.service, '_sync_pricing') as mock_sync_pricing, \
             patch.object(self.service, '_sync_subscriptions') as mock_sync_subscriptions, \
             patch.object(self.service, '_sync_limits') as mock_sync_limits, \
             patch.object(self.service.redis_service, 'set_cache'), \
             patch.object(self.service.redis_service, 'publish_event') as mock_publish_event:
            
            mock_sync_all.return_value = mock_sync_data
            # 设置所有同步方法返回空结果
            for mock_method in [mock_sync_projects, mock_sync_use_cases, mock_sync_budgets,
                               mock_sync_models, mock_sync_deployments, mock_sync_pricing,
                               mock_sync_subscriptions, mock_sync_limits]:
                mock_method.return_value = {"created": 0, "updated": 0, "errors": 0}
            
            result = await self.service.sync_all(updated_since)
            
            assert result["success"] is True
            mock_sync_all.assert_called_once_with(updated_since)
            
            # 验证发布的事件类型为增量同步
            call_args = mock_publish_event.call_args[0][1]
            assert call_args["sync_type"] == "incremental"
    
    @pytest.mark.asyncio
    async def test_sync_all_failure(self):
        """测试同步失败"""
        with patch.object(self.service.model_garden_client, 'sync_all') as mock_sync_all, \
             patch.object(self.service.redis_service, 'publish_event') as mock_publish_event:
            
            mock_sync_all.side_effect = Exception("API error")
            
            result = await self.service.sync_all()
            
            assert result["success"] is False
            assert "error" in result
            assert result["error"] == "API error"
            
            # 验证发布同步失败事件
            call_args = mock_publish_event.call_args[0][1]
            assert call_args["event_type"] == "sync_failed"
    
    @pytest.mark.asyncio
    async def test_sync_projects_create_new(self):
        """测试创建新项目"""
        projects_data = [
            {"project_name": "New Project", "project_code": "NEW"}
        ]
        
        # 模拟项目不存在
        self.service.project_repo = Mock()
        self.service.project_repo.get_by_project_code.return_value = None
        mock_project = Mock()
        mock_project.id = "new-project-id"
        self.service.project_repo.create.return_value = mock_project
        
        result = await self.service._sync_projects(projects_data)
        
        assert result["created"] == 1
        assert result["updated"] == 0
        assert result["errors"] == 0
        
        self.service.project_repo.get_by_project_code.assert_called_once_with("NEW")
        self.service.project_repo.create.assert_called_once_with(
            project_name="New Project",
            project_code="NEW"
        )
    
    @pytest.mark.asyncio
    async def test_sync_projects_update_existing(self):
        """测试更新现有项目"""
        projects_data = [
            {"project_name": "Updated Project", "project_code": "EXISTING"}
        ]
        
        # 模拟项目已存在
        self.service.project_repo = Mock()
        existing_project = Mock()
        existing_project.id = "existing-project-id"
        self.service.project_repo.get_by_project_code.return_value = existing_project
        self.service.project_repo.update.return_value = existing_project
        
        result = await self.service._sync_projects(projects_data)
        
        assert result["created"] == 0
        assert result["updated"] == 1
        assert result["errors"] == 0
        
        self.service.project_repo.update.assert_called_once_with(
            "existing-project-id",
            project_name="Updated Project",
            project_code="EXISTING"
        )
    
    @pytest.mark.asyncio
    async def test_sync_projects_error(self):
        """测试项目同步出错"""
        projects_data = [
            {"project_name": "Error Project", "project_code": "ERROR"}
        ]
        
        # 模拟仓储操作出错
        self.service.project_repo = Mock()
        self.service.project_repo.get_by_project_code.side_effect = Exception("DB error")
        
        result = await self.service._sync_projects(projects_data)
        
        assert result["created"] == 0
        assert result["updated"] == 0
        assert result["errors"] == 1
    
    @pytest.mark.asyncio
    async def test_sync_use_cases_create_new(self):
        """测试创建新用例"""
        use_cases_data = [
            {
                "project_id": "proj1",
                "use_case_name": "New Use Case",
                "ad_group": "test_group"
            }
        ]
        
        # 模拟用例不存在
        self.service.use_case_repo = Mock()
        self.service.use_case_repo.get_by_project_and_name.return_value = None
        mock_use_case = Mock()
        mock_use_case.id = "new-use-case-id"
        self.service.use_case_repo.create.return_value = mock_use_case
        
        result = await self.service._sync_use_cases(use_cases_data)
        
        assert result["created"] == 1
        assert result["updated"] == 0
        assert result["errors"] == 0
        
        self.service.use_case_repo.get_by_project_and_name.assert_called_once_with(
            "proj1", "New Use Case"
        )
        self.service.use_case_repo.create.assert_called_once_with(**use_cases_data[0])
    
    @pytest.mark.asyncio
    async def test_sync_budgets_create_budget(self):
        """测试创建预算"""
        budgets_data = [
            {
                "type": "budget",
                "use_case_id": "uc1",
                "budget_cents": 10000,
                "currency": "USD"
            }
        ]
        
        # 模拟预算不存在
        self.service.budget_repo = Mock()
        self.service.budget_repo.get_by_use_case_id.return_value = None
        mock_budget = Mock()
        mock_budget.id = "new-budget-id"
        self.service.budget_repo.create.return_value = mock_budget
        
        result = await self.service._sync_budgets(budgets_data)
        
        assert result["created"] == 1
        assert result["updated"] == 0
        assert result["errors"] == 0
        
        self.service.budget_repo.create.assert_called_once_with(**budgets_data[0])
    
    @pytest.mark.asyncio
    async def test_sync_budgets_create_usage(self):
        """测试创建预算使用情况"""
        budgets_data = [
            {
                "type": "usage",
                "use_case_id": "uc1",
                "usage_period": "2023-01-01",
                "scope": "daily",
                "used_cents": 5000
            }
        ]
        
        # 模拟使用情况不存在
        self.service.budget_repo = Mock()
        self.service.budget_repo.get_usage_by_use_case_and_period.return_value = None
        mock_usage = Mock()
        mock_usage.id = "new-usage-id"
        self.service.budget_repo.create_usage.return_value = mock_usage
        
        result = await self.service._sync_budgets(budgets_data)
        
        assert result["created"] == 1
        assert result["updated"] == 0
        assert result["errors"] == 0
        
        self.service.budget_repo.create_usage.assert_called_once_with(**budgets_data[0])
    
    @pytest.mark.asyncio
    async def test_sync_models_create_new(self):
        """测试创建新模型"""
        models_data = [
            {
                "model_name": "gpt-4",
                "model_provider": "openai"
            }
        ]
        
        # 模拟模型不存在
        self.service.model_repo = Mock()
        self.service.model_repo.get_by_name.return_value = None
        mock_model = Mock()
        mock_model.id = "new-model-id"
        self.service.model_repo.create.return_value = mock_model
        
        result = await self.service._sync_models(models_data)
        
        assert result["created"] == 1
        assert result["updated"] == 0
        assert result["errors"] == 0
        
        self.service.model_repo.get_by_name.assert_called_once_with("gpt-4")
        self.service.model_repo.create.assert_called_once_with(**models_data[0])
    
    @pytest.mark.asyncio
    async def test_sync_deployments_create_new(self):
        """测试创建新部署"""
        deployments_data = [
            {
                "model_id": "model1",
                "deployment_name": "prod-deployment",
                "endpoint": "https://api.example.com"
            }
        ]
        
        # 模拟部署不存在
        self.service.deployment_repo = Mock()
        self.service.deployment_repo.get_by_model_and_name.return_value = None
        mock_deployment = Mock()
        mock_deployment.id = "new-deployment-id"
        self.service.deployment_repo.create.return_value = mock_deployment
        
        result = await self.service._sync_deployments(deployments_data)
        
        assert result["created"] == 1
        assert result["updated"] == 0
        assert result["errors"] == 0
        
        self.service.deployment_repo.get_by_model_and_name.assert_called_once_with(
            "model1", "prod-deployment"
        )
        self.service.deployment_repo.create.assert_called_once_with(**deployments_data[0])
    
    @pytest.mark.asyncio
    async def test_sync_pricing_create_new(self):
        """测试创建新定价"""
        pricing_data = [
            {
                "model_id": "model1",
                "pricing_type": "input",
                "price_per_unit": 0.001
            }
        ]
        
        # 模拟定价不存在
        self.service.pricing_repo = Mock()
        self.service.pricing_repo.get_by_model_and_type.return_value = None
        mock_pricing = Mock()
        mock_pricing.id = "new-pricing-id"
        self.service.pricing_repo.create.return_value = mock_pricing
        
        result = await self.service._sync_pricing(pricing_data)
        
        assert result["created"] == 1
        assert result["updated"] == 0
        assert result["errors"] == 0
        
        self.service.pricing_repo.get_by_model_and_type.assert_called_once_with(
            "model1", "input"
        )
        self.service.pricing_repo.create.assert_called_once_with(**pricing_data[0])
    
    @pytest.mark.asyncio
    async def test_sync_subscriptions_create_new(self):
        """测试创建新订阅"""
        subscriptions_data = [
            {
                "use_case_id": "uc1",
                "model_id": "model1"
            }
        ]
        
        # 模拟订阅不存在
        self.service.subscription_repo = Mock()
        self.service.subscription_repo.get_by_use_case_and_model.return_value = None
        mock_subscription = Mock()
        mock_subscription.id = "new-subscription-id"
        self.service.subscription_repo.create.return_value = mock_subscription
        
        result = await self.service._sync_subscriptions(subscriptions_data)
        
        assert result["created"] == 1
        assert result["updated"] == 0
        assert result["errors"] == 0
        
        self.service.subscription_repo.get_by_use_case_and_model.assert_called_once_with(
            "uc1", "model1"
        )
        self.service.subscription_repo.create.assert_called_once_with(**subscriptions_data[0])
    
    @pytest.mark.asyncio
    async def test_sync_limits_create_limit(self):
        """测试创建限制"""
        limits_data = [
            {
                "type": "limit",
                "use_case_id": "uc1",
                "model_id": "model1",
                "limit_type": "request_per_minute",
                "limit_value": 100
            }
        ]
        
        # 模拟限制不存在
        self.service.limit_repo = Mock()
        self.service.limit_repo.get_by_use_case_and_model.return_value = None
        mock_limit = Mock()
        mock_limit.id = "new-limit-id"
        self.service.limit_repo.create.return_value = mock_limit
        
        result = await self.service._sync_limits(limits_data)
        
        assert result["created"] == 1
        assert result["updated"] == 0
        assert result["errors"] == 0
        
        self.service.limit_repo.create.assert_called_once_with(**limits_data[0])
    
    @pytest.mark.asyncio
    async def test_sync_limits_create_usage(self):
        """测试创建限制使用情况"""
        limits_data = [
            {
                "type": "usage",
                "limit_id": "limit1",
                "usage_period": "2023-01-01",
                "scope": "daily",
                "used_value": 50
            }
        ]
        
        # 模拟使用情况不存在
        self.service.limit_repo = Mock()
        self.service.limit_repo.get_usage_by_limit_and_period.return_value = None
        mock_usage = Mock()
        mock_usage.id = "new-usage-id"
        self.service.limit_repo.create_usage.return_value = mock_usage
        
        result = await self.service._sync_limits(limits_data)
        
        assert result["created"] == 1
        assert result["updated"] == 0
        assert result["errors"] == 0
        
        self.service.limit_repo.create_usage.assert_called_once_with(**limits_data[0]) 
    
    @pytest.mark.asyncio
    async def test_sync_projects_update_existing_no_changes(self):
        """测试更新现有项目但返回None"""
        projects_data = [
            {"project_name": "Updated Project", "project_code": "EXISTING"}
        ]
        
        # 模拟项目已存在但更新失败
        self.service.project_repo = Mock()
        existing_project = Mock()
        existing_project.id = "existing-project-id"
        self.service.project_repo.get_by_project_code.return_value = existing_project
        self.service.project_repo.update.return_value = None
        
        result = await self.service._sync_projects(projects_data)
        
        assert result["created"] == 0
        assert result["updated"] == 0
        assert result["errors"] == 0
    
    @pytest.mark.asyncio
    async def test_sync_projects_create_failed(self):
        """测试创建项目失败"""
        projects_data = [
            {"project_name": "New Project", "project_code": "NEW"}
        ]
        
        # 模拟项目不存在但创建失败
        self.service.project_repo = Mock()
        self.service.project_repo.get_by_project_code.return_value = None
        self.service.project_repo.create.return_value = None
        
        result = await self.service._sync_projects(projects_data)
        
        assert result["created"] == 0
        assert result["updated"] == 0
        assert result["errors"] == 0
    
    @pytest.mark.asyncio
    async def test_sync_use_cases_update_existing(self):
        """测试更新现有用例"""
        use_cases_data = [
            {
                "project_id": "proj1",
                "use_case_name": "Existing Use Case",
                "ad_group": "updated_group"
            }
        ]
        
        # 模拟用例已存在
        self.service.use_case_repo = Mock()
        existing_use_case = Mock()
        existing_use_case.id = "existing-use-case-id"
        self.service.use_case_repo.get_by_project_and_name.return_value = existing_use_case
        self.service.use_case_repo.update.return_value = existing_use_case
        
        result = await self.service._sync_use_cases(use_cases_data)
        
        assert result["created"] == 0
        assert result["updated"] == 1
        assert result["errors"] == 0
        
        self.service.use_case_repo.update.assert_called_once_with(
            "existing-use-case-id", **use_cases_data[0]
        )
    
    @pytest.mark.asyncio
    async def test_sync_budgets_update_existing_budget(self):
        """测试更新现有预算"""
        budgets_data = [
            {
                "type": "budget",
                "use_case_id": "uc1",
                "budget_cents": 20000,
                "currency": "USD"
            }
        ]
        
        # 模拟预算已存在
        self.service.budget_repo = Mock()
        existing_budget = Mock()
        existing_budget.id = "existing-budget-id"
        self.service.budget_repo.get_by_use_case_id.return_value = existing_budget
        self.service.budget_repo.update.return_value = existing_budget
        
        result = await self.service._sync_budgets(budgets_data)
        
        assert result["created"] == 0
        assert result["updated"] == 1
        assert result["errors"] == 0
        
        self.service.budget_repo.update.assert_called_once_with(
            "existing-budget-id", **budgets_data[0]
        )
    
    @pytest.mark.asyncio
    async def test_sync_budgets_update_existing_usage(self):
        """测试更新现有预算使用情况"""
        budgets_data = [
            {
                "type": "usage",
                "use_case_id": "uc1",
                "usage_period": "2023-01-01",
                "scope": "daily",
                "used_cents": 6000
            }
        ]
        
        # 模拟使用情况已存在
        self.service.budget_repo = Mock()
        existing_usage = Mock()
        existing_usage.id = "existing-usage-id"
        self.service.budget_repo.get_usage_by_use_case_and_period.return_value = existing_usage
        self.service.budget_repo.update_usage.return_value = existing_usage
        
        result = await self.service._sync_budgets(budgets_data)
        
        assert result["created"] == 0
        assert result["updated"] == 1
        assert result["errors"] == 0
        
        self.service.budget_repo.update_usage.assert_called_once_with(
            "existing-usage-id", **budgets_data[0]
        )
    
    @pytest.mark.asyncio
    async def test_sync_models_update_existing(self):
        """测试更新现有模型"""
        models_data = [
            {
                "model_name": "gpt-4",
                "model_provider": "openai"
            }
        ]
        
        # 模拟模型已存在
        self.service.model_repo = Mock()
        existing_model = Mock()
        existing_model.id = "existing-model-id"
        self.service.model_repo.get_by_name.return_value = existing_model
        self.service.model_repo.update.return_value = existing_model
        
        result = await self.service._sync_models(models_data)
        
        assert result["created"] == 0
        assert result["updated"] == 1
        assert result["errors"] == 0
        
        self.service.model_repo.update.assert_called_once_with(
            "existing-model-id", **models_data[0]
        )
    
    @pytest.mark.asyncio
    async def test_sync_deployments_update_existing(self):
        """测试更新现有部署"""
        deployments_data = [
            {
                "model_id": "model1",
                "deployment_name": "prod-deployment",
                "endpoint": "https://api-v2.example.com"
            }
        ]
        
        # 模拟部署已存在
        self.service.deployment_repo = Mock()
        existing_deployment = Mock()
        existing_deployment.id = "existing-deployment-id"
        self.service.deployment_repo.get_by_model_and_name.return_value = existing_deployment
        self.service.deployment_repo.update.return_value = existing_deployment
        
        result = await self.service._sync_deployments(deployments_data)
        
        assert result["created"] == 0
        assert result["updated"] == 1
        assert result["errors"] == 0
        
        self.service.deployment_repo.update.assert_called_once_with(
            "existing-deployment-id", **deployments_data[0]
        )
    
    @pytest.mark.asyncio
    async def test_sync_pricing_update_existing(self):
        """测试更新现有定价"""
        pricing_data = [
            {
                "model_id": "model1",
                "pricing_type": "input",
                "price_per_unit": 0.002
            }
        ]
        
        # 模拟定价已存在
        self.service.pricing_repo = Mock()
        existing_pricing = Mock()
        existing_pricing.id = "existing-pricing-id"
        self.service.pricing_repo.get_by_model_and_type.return_value = existing_pricing
        self.service.pricing_repo.update.return_value = existing_pricing
        
        result = await self.service._sync_pricing(pricing_data)
        
        assert result["created"] == 0
        assert result["updated"] == 1
        assert result["errors"] == 0
        
        self.service.pricing_repo.update.assert_called_once_with(
            "existing-pricing-id", **pricing_data[0]
        )
    
    @pytest.mark.asyncio
    async def test_sync_subscriptions_update_existing(self):
        """测试更新现有订阅"""
        subscriptions_data = [
            {
                "use_case_id": "uc1",
                "model_id": "model1"
            }
        ]
        
        # 模拟订阅已存在
        self.service.subscription_repo = Mock()
        existing_subscription = Mock()
        existing_subscription.id = "existing-subscription-id"
        self.service.subscription_repo.get_by_use_case_and_model.return_value = existing_subscription
        self.service.subscription_repo.update.return_value = existing_subscription
        
        result = await self.service._sync_subscriptions(subscriptions_data)
        
        assert result["created"] == 0
        assert result["updated"] == 1
        assert result["errors"] == 0
        
        self.service.subscription_repo.update.assert_called_once_with(
            "existing-subscription-id", **subscriptions_data[0]
        )
    
    @pytest.mark.asyncio
    async def test_sync_limits_update_existing_limit(self):
        """测试更新现有限制"""
        limits_data = [
            {
                "type": "limit",
                "use_case_id": "uc1",
                "model_id": "model1",
                "limit_type": "request_per_minute",
                "limit_value": 200
            }
        ]
        
        # 模拟限制已存在
        self.service.limit_repo = Mock()
        existing_limit = Mock()
        existing_limit.id = "existing-limit-id"
        self.service.limit_repo.get_by_use_case_and_model.return_value = existing_limit
        self.service.limit_repo.update.return_value = existing_limit
        
        result = await self.service._sync_limits(limits_data)
        
        assert result["created"] == 0
        assert result["updated"] == 1
        assert result["errors"] == 0
        
        self.service.limit_repo.update.assert_called_once_with(
            "existing-limit-id", **limits_data[0]
        )
    
    @pytest.mark.asyncio
    async def test_sync_limits_update_existing_usage(self):
        """测试更新现有限制使用情况"""
        limits_data = [
            {
                "type": "usage",
                "limit_id": "limit1",
                "usage_period": "2023-01-01",
                "scope": "daily",
                "used_value": 75
            }
        ]
        
        # 模拟使用情况已存在
        self.service.limit_repo = Mock()
        existing_usage = Mock()
        existing_usage.id = "existing-usage-id"
        self.service.limit_repo.get_usage_by_limit_and_period.return_value = existing_usage
        self.service.limit_repo.update_usage.return_value = existing_usage
        
        result = await self.service._sync_limits(limits_data)
        
        assert result["created"] == 0
        assert result["updated"] == 1
        assert result["errors"] == 0
        
        self.service.limit_repo.update_usage.assert_called_once_with(
            "existing-usage-id", **limits_data[0]
        ) 
    
    @pytest.mark.asyncio
    async def test_sync_all_with_session_parameter(self):
        """测试带session参数的同步"""
        mock_session = Mock()
        service = SyncService()  # 不带session初始化
        
        # 模拟初始化repositories时的调用
        with patch.object(service, '_init_repositories') as mock_init:
            await service.sync_all(session=mock_session)
            mock_init.assert_called_once_with(mock_session)
    
    @pytest.mark.asyncio
    async def test_sync_projects_multiple_items(self):
        """测试同步多个项目的混合场景"""
        projects_data = [
            {"project_name": "New Project", "project_code": "NEW"},
            {"project_name": "Updated Project", "project_code": "EXISTING"},
            {"project_name": "Error Project", "project_code": "ERROR"}
        ]
        
        self.service.project_repo = Mock()
        
        # 第一个项目：新建成功
        self.service.project_repo.get_by_project_code.side_effect = [
            None,  # 第一个项目不存在
            Mock(id="existing-id"),  # 第二个项目存在
            Exception("Database error")  # 第三个项目查询出错
        ]
        
        new_project = Mock()
        new_project.id = "new-id"
        self.service.project_repo.create.return_value = new_project
        
        updated_project = Mock()
        self.service.project_repo.update.return_value = updated_project
        
        result = await self.service._sync_projects(projects_data)
        
        assert result["created"] == 1
        assert result["updated"] == 1  
        assert result["errors"] == 1
    
    @pytest.mark.asyncio
    async def test_sync_budgets_unknown_type(self):
        """测试处理未知类型的预算数据"""
        budgets_data = [
            {
                "type": "unknown_type",
                "use_case_id": "uc1"
            }
        ]
        
        self.service.budget_repo = Mock()
        
        # 由于type不是budget或usage，应该不会调用任何仓储方法
        result = await self.service._sync_budgets(budgets_data)
        
        assert result["created"] == 0
        assert result["updated"] == 0
        assert result["errors"] == 0
    
    @pytest.mark.asyncio
    async def test_sync_limits_unknown_type(self):
        """测试处理未知类型的限制数据"""
        limits_data = [
            {
                "type": "unknown_type",
                "use_case_id": "uc1",
                "model_id": "model1"
            }
        ]
        
        self.service.limit_repo = Mock()
        
        # 由于type不是limit或usage，应该不会调用任何仓储方法
        result = await self.service._sync_limits(limits_data)
        
        assert result["created"] == 0
        assert result["updated"] == 0
        assert result["errors"] == 0 