"""
事件服务
负责处理Model Garden发送的CUD事件
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
import structlog

from src.services.redis_service import RedisService
from src.repositories.project_repository import ProjectRepository
from src.repositories.use_case_repository import UseCaseRepository
from src.repositories.budget_repository import BudgetRepository
from src.repositories.model_repository import ModelRepository
from src.repositories.deployment_repository import DeploymentRepository
from src.repositories.pricing_repository import PricingRepository
from src.repositories.subscription_repository import SubscriptionRepository
from src.repositories.limit_repository import LimitRepository
from src.schemas.event_request import EventRequest
from src.config.settings import get_settings
from src.utils.logger import get_logger

logger = get_logger()


class EventService:
    """事件服务类"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.settings = get_settings()
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
    
    async def process_event(self, event_request: EventRequest, 
                           session: Optional[Session] = None) -> Dict[str, Any]:
        """
        处理CUD事件
        
        Args:
            event_request: 事件请求对象
            session: 数据库会话
            
        Returns:
            处理结果字典
        """
        if session and not self._repositories_initialized:
            self._init_repositories(session)
        
        start_time = datetime.now(timezone.utc)
        
        logger.info(
            "开始处理事件",
            event_id=event_request.event_id,
            event_type=event_request.event_type,
            entity_type=event_request.entity_type,
            entity_id=event_request.entity_id
        )
        
        try:
            # 检查事件是否已处理（幂等性）
            cache_key = f"event:processed:{event_request.event_id}"
            if await self.redis_service.get_cache(cache_key):
                logger.info("事件已处理，跳过", event_id=event_request.event_id)
                return {
                    "success": True,
                    "status": "already_processed",
                    "event_id": event_request.event_id
                }
            
            # 根据实体类型和事件类型分发处理
            result = await self._dispatch_event(event_request)
            
            # 标记事件已处理
            await self.redis_service.set_cache(cache_key, {
                "processed_at": start_time.isoformat(),
                "result": result
            }, expire=86400)  # 24小时
            
            # 发布事件处理完成到Redis Stream
            await self.redis_service.publish_event("event_processed", {
                "event_id": event_request.event_id,
                "event_type": event_request.event_type,
                "entity_type": event_request.entity_type,
                "entity_id": event_request.entity_id,
                "status": "success",
                "processing_time": (datetime.now(timezone.utc) - start_time).total_seconds()
            })
            
            logger.info(
                "事件处理完成",
                event_id=event_request.event_id,
                status=result.get("status"),
                processing_time=(datetime.now(timezone.utc) - start_time).total_seconds()
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "事件处理失败",
                event_id=event_request.event_id,
                error=str(e),
                exc_info=True
            )
            
            # 发布事件处理失败到Redis Stream
            await self.redis_service.publish_event("event_processed", {
                "event_id": event_request.event_id,
                "event_type": event_request.event_type,
                "entity_type": event_request.entity_type,
                "entity_id": event_request.entity_id,
                "status": "failed",
                "error": str(e),
                "processing_time": (datetime.now(timezone.utc) - start_time).total_seconds()
            })
            
            return {
                "success": False,
                "error": str(e),
                "event_id": event_request.event_id
            }
    
    async def _dispatch_event(self, event_request: EventRequest) -> Dict[str, Any]:
        """
        根据实体类型分发事件处理
        
        Args:
            event_request: 事件请求对象
            
        Returns:
            处理结果字典
        """
        entity_type = event_request.entity_type.lower()
        event_type = event_request.event_type.upper()
        
        # 实体类型处理映射
        handlers = {
            "project": self._handle_project_event,
            "usecase": self._handle_use_case_event,
            "budget": self._handle_budget_event,
            "model": self._handle_model_event,
            "deployment": self._handle_deployment_event,
            "pricing": self._handle_pricing_event,
            "subscription": self._handle_subscription_event,
            "limit": self._handle_limit_event,
        }
        
        handler = handlers.get(entity_type)
        if not handler:
            raise ValueError(f"不支持的实体类型: {entity_type}")
        
        return await handler(event_type, event_request)
    
    async def _handle_project_event(self, event_type: str, event_request: EventRequest) -> Dict[str, Any]:
        """处理项目事件"""
        if event_type == "CREATE":
            project = self.project_repo.create(**event_request.payload)
            return {
                "success": True,
                "status": "created",
                "entity_id": str(project.id) if project else None
            }
        
        elif event_type == "UPDATE":
            project = self.project_repo.update(event_request.entity_id, **event_request.payload)
            return {
                "success": True,
                "status": "updated" if project else "not_found",
                "entity_id": event_request.entity_id
            }
        
        elif event_type == "DELETE":
            success = self.project_repo.delete(event_request.entity_id)
            return {
                "success": True,
                "status": "deleted" if success else "not_found",
                "entity_id": event_request.entity_id
            }
        
        else:
            raise ValueError(f"不支持的事件类型: {event_type}")
    
    async def _handle_use_case_event(self, event_type: str, event_request: EventRequest) -> Dict[str, Any]:
        """处理用例事件"""
        if event_type == "CREATE":
            use_case = self.use_case_repo.create(**event_request.payload)
            return {
                "success": True,
                "status": "created",
                "entity_id": str(use_case.id) if use_case else None
            }
        
        elif event_type == "UPDATE":
            use_case = self.use_case_repo.update(event_request.entity_id, **event_request.payload)
            return {
                "success": True,
                "status": "updated" if use_case else "not_found",
                "entity_id": event_request.entity_id
            }
        
        elif event_type == "DELETE":
            success = self.use_case_repo.delete(event_request.entity_id)
            return {
                "success": True,
                "status": "deleted" if success else "not_found",
                "entity_id": event_request.entity_id
            }
        
        else:
            raise ValueError(f"不支持的事件类型: {event_type}")
    
    async def _handle_budget_event(self, event_type: str, event_request: EventRequest) -> Dict[str, Any]:
        """处理预算事件"""
        payload = event_request.payload
        budget_type = payload.get("type", "budget")  # budget 或 usage
        
        if event_type == "CREATE":
            if budget_type == "budget":
                budget = self.budget_repo.create(**payload)
                entity_id = str(budget.id) if budget else None
            else:
                usage = self.budget_repo.create_usage(**payload)
                entity_id = str(usage.id) if usage else None
            
            return {
                "success": True,
                "status": "created",
                "entity_id": entity_id
            }
        
        elif event_type == "UPDATE":
            if budget_type == "budget":
                result = self.budget_repo.update(event_request.entity_id, **payload)
            else:
                result = self.budget_repo.update_usage(event_request.entity_id, **payload)
            
            return {
                "success": True,
                "status": "updated" if result else "not_found",
                "entity_id": event_request.entity_id
            }
        
        elif event_type == "DELETE":
            if budget_type == "budget":
                success = self.budget_repo.delete(event_request.entity_id)
            else:
                success = self.budget_repo.delete_usage(event_request.entity_id)
            
            return {
                "success": True,
                "status": "deleted" if success else "not_found",
                "entity_id": event_request.entity_id
            }
        
        else:
            raise ValueError(f"不支持的事件类型: {event_type}")
    
    async def _handle_model_event(self, event_type: str, event_request: EventRequest) -> Dict[str, Any]:
        """处理模型事件"""
        if event_type == "CREATE":
            model = self.model_repo.create(**event_request.payload)
            return {
                "success": True,
                "status": "created",
                "entity_id": str(model.id) if model else None
            }
        
        elif event_type == "UPDATE":
            model = self.model_repo.update(event_request.entity_id, **event_request.payload)
            return {
                "success": True,
                "status": "updated" if model else "not_found",
                "entity_id": event_request.entity_id
            }
        
        elif event_type == "DELETE":
            success = self.model_repo.delete(event_request.entity_id)
            return {
                "success": True,
                "status": "deleted" if success else "not_found",
                "entity_id": event_request.entity_id
            }
        
        else:
            raise ValueError(f"不支持的事件类型: {event_type}")
    
    async def _handle_deployment_event(self, event_type: str, event_request: EventRequest) -> Dict[str, Any]:
        """处理部署事件"""
        if event_type == "CREATE":
            deployment = self.deployment_repo.create(**event_request.payload)
            return {
                "success": True,
                "status": "created",
                "entity_id": str(deployment.id) if deployment else None
            }
        
        elif event_type == "UPDATE":
            deployment = self.deployment_repo.update(event_request.entity_id, **event_request.payload)
            return {
                "success": True,
                "status": "updated" if deployment else "not_found",
                "entity_id": event_request.entity_id
            }
        
        elif event_type == "DELETE":
            success = self.deployment_repo.delete(event_request.entity_id)
            return {
                "success": True,
                "status": "deleted" if success else "not_found",
                "entity_id": event_request.entity_id
            }
        
        else:
            raise ValueError(f"不支持的事件类型: {event_type}")
    
    async def _handle_pricing_event(self, event_type: str, event_request: EventRequest) -> Dict[str, Any]:
        """处理定价事件"""
        if event_type == "CREATE":
            pricing = self.pricing_repo.create(**event_request.payload)
            return {
                "success": True,
                "status": "created",
                "entity_id": str(pricing.id) if pricing else None
            }
        
        elif event_type == "UPDATE":
            pricing = self.pricing_repo.update(event_request.entity_id, **event_request.payload)
            return {
                "success": True,
                "status": "updated" if pricing else "not_found",
                "entity_id": event_request.entity_id
            }
        
        elif event_type == "DELETE":
            success = self.pricing_repo.delete(event_request.entity_id)
            return {
                "success": True,
                "status": "deleted" if success else "not_found",
                "entity_id": event_request.entity_id
            }
        
        else:
            raise ValueError(f"不支持的事件类型: {event_type}")
    
    async def _handle_subscription_event(self, event_type: str, event_request: EventRequest) -> Dict[str, Any]:
        """处理订阅事件"""
        if event_type == "CREATE":
            subscription = self.subscription_repo.create(**event_request.payload)
            return {
                "success": True,
                "status": "created",
                "entity_id": str(subscription.id) if subscription else None
            }
        
        elif event_type == "UPDATE":
            subscription = self.subscription_repo.update(event_request.entity_id, **event_request.payload)
            return {
                "success": True,
                "status": "updated" if subscription else "not_found",
                "entity_id": event_request.entity_id
            }
        
        elif event_type == "DELETE":
            success = self.subscription_repo.delete(event_request.entity_id)
            return {
                "success": True,
                "status": "deleted" if success else "not_found",
                "entity_id": event_request.entity_id
            }
        
        else:
            raise ValueError(f"不支持的事件类型: {event_type}")
    
    async def _handle_limit_event(self, event_type: str, event_request: EventRequest) -> Dict[str, Any]:
        """处理限制事件"""
        payload = event_request.payload
        limit_type = payload.get("type", "limit")  # limit 或 usage
        
        if event_type == "CREATE":
            if limit_type == "limit":
                limit = self.limit_repo.create(**payload)
                entity_id = str(limit.id) if limit else None
            else:
                usage = self.limit_repo.create_usage(**payload)
                entity_id = str(usage.id) if usage else None
            
            return {
                "success": True,
                "status": "created",
                "entity_id": entity_id
            }
        
        elif event_type == "UPDATE":
            if limit_type == "limit":
                result = self.limit_repo.update(event_request.entity_id, **payload)
            else:
                result = self.limit_repo.update_usage(event_request.entity_id, **payload)
            
            return {
                "success": True,
                "status": "updated" if result else "not_found",
                "entity_id": event_request.entity_id
            }
        
        elif event_type == "DELETE":
            if limit_type == "limit":
                success = self.limit_repo.delete(event_request.entity_id)
            else:
                success = self.limit_repo.delete_usage(event_request.entity_id)
            
            return {
                "success": True,
                "status": "deleted" if success else "not_found",
                "entity_id": event_request.entity_id
            }
        
        else:
            raise ValueError(f"不支持的事件类型: {event_type}") 