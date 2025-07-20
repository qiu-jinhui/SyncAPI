"""
Model Garden客户端
负责调用Model Garden的API
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import httpx
import structlog

from src.config.settings import get_settings
from src.utils.logger import get_logger

logger = get_logger()


class ModelGardenClient:
    """Model Garden API客户端"""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.MODEL_GARDEN_BASE_URL
        self.api_key = self.settings.MODEL_GARDEN_API_KEY
        self.timeout = self.settings.MODEL_GARDEN_TIMEOUT
        
        # HTTP客户端配置
        self.client_config = {
            "timeout": httpx.Timeout(self.timeout),
            "headers": {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": f"SynchronizeAPI/{self.settings.APP_VERSION}"
            }
        }
    
    async def sync_all(self, updated_since: Optional[datetime] = None) -> Dict[str, Any]:
        """
        调用全量同步API
        
        Args:
            updated_since: 可选的更新时间，用于增量同步
            
        Returns:
            同步数据字典
            
        Raises:
            httpx.HTTPStatusError: HTTP错误
            httpx.RequestError: 请求错误
        """
        url = f"{self.base_url}/model-garden/sync/all"
        
        # 构建请求数据
        request_data = {}
        if updated_since:
            request_data["updated_since"] = updated_since.isoformat()
        
        logger.info(
            "开始调用Model Garden同步API",
            url=url,
            updated_since=updated_since.isoformat() if updated_since else None
        )
        
        async with httpx.AsyncClient(**self.client_config) as client:
            try:
                response = await client.post(url, json=request_data)
                response.raise_for_status()
                
                data = response.json()
                logger.info(
                    "成功获取同步数据",
                    projects_count=len(data.get("projects", [])),
                    use_cases_count=len(data.get("use_cases", [])),
                    budgets_count=len(data.get("budgets", [])),
                    models_count=len(data.get("models", [])),
                    deployments_count=len(data.get("model_deployments", [])),
                    pricing_count=len(data.get("pricing", [])),
                    subscriptions_count=len(data.get("use_case_llm_models", [])),
                    limits_count=len(data.get("limits", []))
                )
                
                return data
                
            except httpx.HTTPStatusError as e:
                logger.error(
                    "Model Garden API返回错误",
                    status_code=e.response.status_code,
                    response_text=e.response.text,
                    url=url
                )
                raise
            except httpx.RequestError as e:
                logger.error(
                    "调用Model Garden API失败",
                    error=str(e),
                    url=url
                )
                raise
    
    async def health_check(self) -> bool:
        """
        检查Model Garden API健康状态
        
        Returns:
            是否健康
        """
        url = f"{self.base_url}/health"
        
        try:
            async with httpx.AsyncClient(**self.client_config) as client:
                response = await client.get(url)
                response.raise_for_status()
                logger.debug("Model Garden健康检查通过")
                return True
        except Exception as e:
            logger.warning("Model Garden健康检查失败", error=str(e))
            return False
    
    async def retry_with_backoff(self, func, max_retries: int = 3, base_delay: float = 1.0):
        """
        带指数退避的重试机制
        
        Args:
            func: 要重试的函数
            max_retries: 最大重试次数
            base_delay: 基础延迟时间（秒）
            
        Returns:
            函数执行结果
            
        Raises:
            最后一次执行的异常
        """
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return await func()
            except Exception as e:
                last_exception = e
                
                if attempt == max_retries:
                    logger.error(
                        "重试次数用尽",
                        attempt=attempt,
                        max_retries=max_retries,
                        error=str(e)
                    )
                    raise e
                
                delay = base_delay * (2 ** attempt)
                logger.warning(
                    "操作失败，准备重试",
                    attempt=attempt + 1,
                    max_retries=max_retries,
                    delay=delay,
                    error=str(e)
                )
                await asyncio.sleep(delay)
        
        raise last_exception 