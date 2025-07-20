"""
Model Garden客户端测试
"""

import pytest
import httpx
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timezone

from src.services.model_garden_client import ModelGardenClient


class TestModelGardenClient:
    """Model Garden客户端测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.client = ModelGardenClient()
    
    @pytest.mark.asyncio
    async def test_init(self):
        """测试初始化"""
        assert self.client.base_url == "http://localhost:8080"
        assert self.client.api_key == "your_api_key_here"
        assert self.client.timeout == 30
        assert "Authorization" in self.client.client_config["headers"]
        assert "Content-Type" in self.client.client_config["headers"]
    
    @pytest.mark.asyncio
    async def test_sync_all_success(self):
        """测试成功的全量同步"""
        mock_response_data = {
            "projects": [
                {"id": "proj1", "project_name": "Test Project", "project_code": "TEST"}
            ],
            "use_cases": [
                {"id": "uc1", "use_case_name": "Test Use Case", "project_id": "proj1"}
            ],
            "budgets": [],
            "models": [],
            "model_deployments": [],
            "pricing": [],
            "use_case_llm_models": [],
            "limits": []
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_client.post.return_value = mock_response
            
            result = await self.client.sync_all()
            
            assert result == mock_response_data
            mock_client.post.assert_called_once()
            mock_response.raise_for_status.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_sync_all_with_updated_since(self):
        """测试带更新时间的增量同步"""
        updated_since = datetime(2023, 1, 1, tzinfo=timezone.utc)
        mock_response_data = {"projects": [], "use_cases": []}
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_client.post.return_value = mock_response
            
            result = await self.client.sync_all(updated_since)
            
            assert result == mock_response_data
            # 验证请求参数包含updated_since
            call_args = mock_client.post.call_args
            assert "json" in call_args.kwargs
            assert "updated_since" in call_args.kwargs["json"]
    
    @pytest.mark.asyncio
    async def test_sync_all_http_error(self):
        """测试HTTP错误"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_client.post.return_value = mock_response
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Server error", request=Mock(), response=mock_response
            )
            
            with pytest.raises(httpx.HTTPStatusError):
                await self.client.sync_all()
    
    @pytest.mark.asyncio
    async def test_sync_all_request_error(self):
        """测试请求错误"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_client.post.side_effect = httpx.RequestError("Connection error")
            
            with pytest.raises(httpx.RequestError):
                await self.client.sync_all()
    
    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """测试健康检查成功"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_client.get.return_value = mock_response
            
            result = await self.client.health_check()
            
            assert result is True
            mock_client.get.assert_called_once_with("http://localhost:8080/health")
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """测试健康检查失败"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_client.get.side_effect = httpx.RequestError("Connection error")
            
            result = await self.client.health_check()
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff_success_first_try(self):
        """测试第一次尝试就成功"""
        async def mock_func():
            return "success"
        
        result = await self.client.retry_with_backoff(mock_func)
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff_success_after_retry(self):
        """测试重试后成功"""
        call_count = 0
        
        async def mock_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary error")
            return "success"
        
        with patch('asyncio.sleep') as mock_sleep:
            result = await self.client.retry_with_backoff(mock_func)
            
            assert result == "success"
            assert call_count == 3
            assert mock_sleep.call_count == 2  # 两次重试
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff_max_retries_exceeded(self):
        """测试超过最大重试次数"""
        async def mock_func():
            raise Exception("Permanent error")
        
        with patch('asyncio.sleep'):
            with pytest.raises(Exception, match="Permanent error"):
                await self.client.retry_with_backoff(mock_func, max_retries=2)
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff_custom_params(self):
        """测试自定义重试参数"""
        call_count = 0
        
        async def mock_func():
            nonlocal call_count
            call_count += 1
            raise Exception("Error")
        
        with patch('asyncio.sleep') as mock_sleep:
            with pytest.raises(Exception):
                await self.client.retry_with_backoff(
                    mock_func, max_retries=1, base_delay=0.5
                )
            
            assert call_count == 2  # 原始调用 + 1次重试
            mock_sleep.assert_called_once_with(0.5)  # base_delay * 2^0 