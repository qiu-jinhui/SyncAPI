"""
同步服务
负责全量同步和增量同步逻辑
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
import structlog

from src.services.model_garden_client import ModelGardenClient
from src.services.redis_service import RedisService
from src.repositories.project_repository import ProjectRepository
from src.repositories.use_case_repository import UseCaseRepository
from src.repositories.budget_repository import BudgetRepository
from src.repositories.model_repository import ModelRepository
from src.repositories.deployment_repository import DeploymentRepository
from src.repositories.pricing_repository import PricingRepository
from src.repositories.subscription_repository import SubscriptionRepository
from src.repositories.limit_repository import LimitRepository
from src.config.settings import get_settings
from src.utils.logger import get_logger

logger = get_logger()


class SyncService:
    """同步服务类"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.settings = get_settings()
        self.model_garden_client = ModelGardenClient()
        self.redis_service = RedisService()
        self.db_session = db_session
        
        # 初始化仓储（如果有session则使用，否则延迟初始化）
        if db_session:
            self._init_repositories(db_session)
        else:
            self._repositories_initialized = False
    
    def _init_repositories(self, session: Session):
        """初始化仓储"""
        self.project_repo = ProjectRepository(session)
        self.use_case_repo = UseCaseRepository(session)
        self.budget_repo = BudgetRepository(session)
        self.model_repo = ModelRepository(session)
        self.deployment_repo = DeploymentRepository(session)
        self.pricing_repo = PricingRepository(session)
        self.subscription_repo = SubscriptionRepository(session)
        self.limit_repo = LimitRepository(session)
        self._repositories_initialized = True
    
    async def sync_all(self, updated_since: Optional[datetime] = None, 
                      session: Optional[Session] = None) -> Dict[str, Any]:
        """
        执行全量同步
        
        Args:
            updated_since: 可选的增量同步时间
            session: 数据库会话
            
        Returns:
            同步结果字典
        """
        if session and not self._repositories_initialized:
            self._init_repositories(session)
        
        start_time = datetime.now(timezone.utc)
        
        logger.info(
            "开始执行全量同步",
            updated_since=updated_since.isoformat() if updated_since else None
        )
        
        try:
            # 调用Model Garden API获取数据
            sync_data = await self.model_garden_client.sync_all(updated_since)
            
            # 同步各种实体
            results = {}
            
            # 1. 同步项目
            results["projects"] = await self._sync_projects(sync_data.get("projects", []))
            
            # 2. 同步用例
            results["use_cases"] = await self._sync_use_cases(sync_data.get("use_cases", []))
            
            # 3. 同步预算
            results["budgets"] = await self._sync_budgets(sync_data.get("budgets", []))
            
            # 4. 同步模型
            results["models"] = await self._sync_models(sync_data.get("models", []))
            
            # 5. 同步部署
            results["deployments"] = await self._sync_deployments(sync_data.get("model_deployments", []))
            
            # 6. 同步定价
            results["pricing"] = await self._sync_pricing(sync_data.get("pricing", []))
            
            # 7. 同步订阅
            results["subscriptions"] = await self._sync_subscriptions(sync_data.get("use_case_llm_models", []))
            
            # 8. 同步限制
            results["limits"] = await self._sync_limits(sync_data.get("limits", []))
            
            # 计算总计
            total_created = sum(r.get("created", 0) for r in results.values())
            total_updated = sum(r.get("updated", 0) for r in results.values())
            total_errors = sum(r.get("errors", 0) for r in results.values())
            
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            result = {
                "success": True,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "totals": {
                    "created": total_created,
                    "updated": total_updated,
                    "errors": total_errors
                },
                "details": results
            }
            
            # 缓存同步结果
            cache_key = f"sync:result:{start_time.strftime('%Y%m%d_%H%M%S')}"
            await self.redis_service.set_cache(cache_key, result, expire=86400)  # 24小时
            
            # 发布同步完成事件
            await self.redis_service.publish_event("sync_events", {
                "event_type": "sync_completed",
                "sync_type": "incremental" if updated_since else "full",
                "totals": result["totals"],
                "duration_seconds": duration
            })
            
            logger.info(
                "全量同步完成",
                duration_seconds=duration,
                created=total_created,
                updated=total_updated,
                errors=total_errors
            )
            
            return result
            
        except Exception as e:
            logger.error("全量同步失败", error=str(e), exc_info=True)
            
            # 发布同步失败事件
            await self.redis_service.publish_event("sync_events", {
                "event_type": "sync_failed",
                "sync_type": "incremental" if updated_since else "full",
                "error": str(e)
            })
            
            return {
                "success": False,
                "error": str(e),
                "start_time": start_time.isoformat(),
                "end_time": datetime.now(timezone.utc).isoformat()
            }
    
    async def _sync_projects(self, projects_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """同步项目数据"""
        created = 0
        updated = 0
        errors = 0
        
        for project_data in projects_data:
            try:
                existing = self.project_repo.get_by_project_code(project_data.get("project_code"))
                
                if existing:
                    # 更新现有项目
                    updated_project = self.project_repo.update(
                        str(existing.id),
                        project_name=project_data.get("project_name"),
                        project_code=project_data.get("project_code")
                    )
                    if updated_project:
                        updated += 1
                        logger.debug("更新项目", project_id=existing.id, project_code=project_data.get("project_code"))
                else:
                    # 创建新项目
                    new_project = self.project_repo.create(
                        project_name=project_data.get("project_name"),
                        project_code=project_data.get("project_code")
                    )
                    if new_project:
                        created += 1
                        logger.debug("创建项目", project_id=new_project.id, project_code=project_data.get("project_code"))
                        
            except Exception as e:
                errors += 1
                logger.error("同步项目失败", project_data=project_data, error=str(e))
        
        return {"created": created, "updated": updated, "errors": errors}
    
    async def _sync_use_cases(self, use_cases_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """同步用例数据"""
        created = 0
        updated = 0
        errors = 0
        
        for use_case_data in use_cases_data:
            try:
                existing = self.use_case_repo.get_by_project_and_name(
                    use_case_data.get("project_id"),
                    use_case_data.get("use_case_name")
                )
                
                if existing:
                    # 更新现有用例
                    updated_use_case = self.use_case_repo.update(
                        str(existing.id),
                        **use_case_data
                    )
                    if updated_use_case:
                        updated += 1
                        logger.debug("更新用例", use_case_id=existing.id)
                else:
                    # 创建新用例
                    new_use_case = self.use_case_repo.create(**use_case_data)
                    if new_use_case:
                        created += 1
                        logger.debug("创建用例", use_case_id=new_use_case.id)
                        
            except Exception as e:
                errors += 1
                logger.error("同步用例失败", use_case_data=use_case_data, error=str(e))
        
        return {"created": created, "updated": updated, "errors": errors}
    
    async def _sync_budgets(self, budgets_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """同步预算数据"""
        created = 0
        updated = 0
        errors = 0
        
        for budget_data in budgets_data:
            try:
                # 分离预算和使用情况数据
                if budget_data.get("type") == "budget":
                    existing = self.budget_repo.get_by_use_case_id(budget_data.get("use_case_id"))
                    
                    if existing:
                        updated_budget = self.budget_repo.update(str(existing.id), **budget_data)
                        if updated_budget:
                            updated += 1
                    else:
                        new_budget = self.budget_repo.create(**budget_data)
                        if new_budget:
                            created += 1
                
                elif budget_data.get("type") == "usage":
                    existing_usage = self.budget_repo.get_usage_by_use_case_and_period(
                        budget_data.get("use_case_id"),
                        budget_data.get("usage_period"),
                        budget_data.get("scope")
                    )
                    
                    if existing_usage:
                        updated_usage = self.budget_repo.update_usage(str(existing_usage.id), **budget_data)
                        if updated_usage:
                            updated += 1
                    else:
                        new_usage = self.budget_repo.create_usage(**budget_data)
                        if new_usage:
                            created += 1
                            
            except Exception as e:
                errors += 1
                logger.error("同步预算失败", budget_data=budget_data, error=str(e))
        
        return {"created": created, "updated": updated, "errors": errors}
    
    async def _sync_models(self, models_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """同步模型数据"""
        created = 0
        updated = 0
        errors = 0
        
        for model_data in models_data:
            try:
                existing = self.model_repo.get_by_name(model_data.get("model_name"))
                
                if existing:
                    updated_model = self.model_repo.update(str(existing.id), **model_data)
                    if updated_model:
                        updated += 1
                else:
                    new_model = self.model_repo.create(**model_data)
                    if new_model:
                        created += 1
                        
            except Exception as e:
                errors += 1
                logger.error("同步模型失败", model_data=model_data, error=str(e))
        
        return {"created": created, "updated": updated, "errors": errors}
    
    async def _sync_deployments(self, deployments_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """同步部署数据"""
        created = 0
        updated = 0
        errors = 0
        
        for deployment_data in deployments_data:
            try:
                existing = self.deployment_repo.get_by_model_and_name(
                    deployment_data.get("model_id"),
                    deployment_data.get("deployment_name")
                )
                
                if existing:
                    updated_deployment = self.deployment_repo.update(str(existing.id), **deployment_data)
                    if updated_deployment:
                        updated += 1
                else:
                    new_deployment = self.deployment_repo.create(**deployment_data)
                    if new_deployment:
                        created += 1
                        
            except Exception as e:
                errors += 1
                logger.error("同步部署失败", deployment_data=deployment_data, error=str(e))
        
        return {"created": created, "updated": updated, "errors": errors}
    
    async def _sync_pricing(self, pricing_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """同步定价数据"""
        created = 0
        updated = 0
        errors = 0
        
        for price_data in pricing_data:
            try:
                existing = self.pricing_repo.get_by_model_and_type(
                    price_data.get("model_id"),
                    price_data.get("pricing_type")
                )
                
                if existing:
                    updated_pricing = self.pricing_repo.update(str(existing.id), **price_data)
                    if updated_pricing:
                        updated += 1
                else:
                    new_pricing = self.pricing_repo.create(**price_data)
                    if new_pricing:
                        created += 1
                        
            except Exception as e:
                errors += 1
                logger.error("同步定价失败", price_data=price_data, error=str(e))
        
        return {"created": created, "updated": updated, "errors": errors}
    
    async def _sync_subscriptions(self, subscriptions_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """同步订阅数据"""
        created = 0
        updated = 0
        errors = 0
        
        for subscription_data in subscriptions_data:
            try:
                existing = self.subscription_repo.get_by_use_case_and_model(
                    subscription_data.get("use_case_id"),
                    subscription_data.get("model_id")
                )
                
                if existing:
                    updated_subscription = self.subscription_repo.update(str(existing.id), **subscription_data)
                    if updated_subscription:
                        updated += 1
                else:
                    new_subscription = self.subscription_repo.create(**subscription_data)
                    if new_subscription:
                        created += 1
                        
            except Exception as e:
                errors += 1
                logger.error("同步订阅失败", subscription_data=subscription_data, error=str(e))
        
        return {"created": created, "updated": updated, "errors": errors}
    
    async def _sync_limits(self, limits_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """同步限制数据"""
        created = 0
        updated = 0
        errors = 0
        
        for limit_data in limits_data:
            try:
                # 分离限制和使用情况数据
                if limit_data.get("type") == "limit":
                    existing = self.limit_repo.get_by_use_case_and_model(
                        limit_data.get("use_case_id"),
                        limit_data.get("model_id")
                    )
                    
                    if existing:
                        updated_limit = self.limit_repo.update(str(existing.id), **limit_data)
                        if updated_limit:
                            updated += 1
                    else:
                        new_limit = self.limit_repo.create(**limit_data)
                        if new_limit:
                            created += 1
                
                elif limit_data.get("type") == "usage":
                    existing_usage = self.limit_repo.get_usage_by_limit_and_period(
                        limit_data.get("limit_id"),
                        limit_data.get("usage_period"),
                        limit_data.get("scope")
                    )
                    
                    if existing_usage:
                        updated_usage = self.limit_repo.update_usage(str(existing_usage.id), **limit_data)
                        if updated_usage:
                            updated += 1
                    else:
                        new_usage = self.limit_repo.create_usage(**limit_data)
                        if new_usage:
                            created += 1
                            
            except Exception as e:
                errors += 1
                logger.error("同步限制失败", limit_data=limit_data, error=str(e))
        
        return {"created": created, "updated": updated, "errors": errors} 