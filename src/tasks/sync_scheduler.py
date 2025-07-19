"""
定时同步调度器
定时调用Model Garden的同步API，获取所有数据并更新到本地数据库
"""

import asyncio
import structlog
from datetime import datetime, timedelta
from typing import Optional

from src.services.sync_service import SyncService
from src.services.model_garden_client import ModelGardenClient
from src.config.settings import get_settings
from src.utils.logger import setup_logging

# 设置日志
setup_logging()
logger = structlog.get_logger()

class SyncScheduler:
    """同步调度器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.sync_service = SyncService()
        self.model_garden_client = ModelGardenClient()
        self.is_running = False
        self.last_sync_time: Optional[datetime] = None
        
    async def start(self):
        """启动调度器"""
        if self.is_running:
            logger.warning("调度器已在运行中")
            return
            
        self.is_running = True
        logger.info("同步调度器已启动")
        
        try:
            while self.is_running:
                await self._run_sync()
                await self._wait_for_next_sync()
        except Exception as e:
            logger.error("同步调度器运行出错", error=str(e), exc_info=True)
            self.is_running = False
        finally:
            logger.info("同步调度器已停止")
    
    async def stop(self):
        """停止调度器"""
        self.is_running = False
        logger.info("正在停止同步调度器...")
    
    async def _run_sync(self):
        """执行同步任务"""
        try:
            logger.info("开始执行全量同步任务")
            
            # 计算增量同步的时间范围
            updated_since = None
            if self.last_sync_time:
                updated_since = self.last_sync_time.isoformat()
            
            # 调用Model Garden的同步API
            sync_data = await self.model_garden_client.sync_all(updated_since)
            
            # 处理同步数据
            await self.sync_service.process_sync_data(sync_data)
            
            # 更新最后同步时间
            self.last_sync_time = datetime.utcnow()
            
            logger.info("全量同步任务完成", 
                       last_sync_time=self.last_sync_time.isoformat())
            
        except Exception as e:
            logger.error("同步任务执行失败", error=str(e), exc_info=True)
            # 这里可以添加告警通知逻辑
    
    async def _wait_for_next_sync(self):
        """等待下次同步"""
        sync_interval = self.settings.SYNC_INTERVAL_MINUTES
        logger.info(f"等待下次同步，间隔: {sync_interval} 分钟")
        await asyncio.sleep(sync_interval * 60)
    
    async def manual_sync(self, updated_since: Optional[str] = None):
        """手动触发同步"""
        try:
            logger.info("手动触发同步任务", updated_since=updated_since)
            
            # 调用Model Garden的同步API
            sync_data = await self.model_garden_client.sync_all(updated_since)
            
            # 处理同步数据
            await self.sync_service.process_sync_data(sync_data)
            
            # 更新最后同步时间
            self.last_sync_time = datetime.utcnow()
            
            logger.info("手动同步任务完成")
            return True
            
        except Exception as e:
            logger.error("手动同步任务失败", error=str(e), exc_info=True)
            return False

# 全局调度器实例
scheduler = SyncScheduler()

async def start_scheduler():
    """启动调度器（用于Celery任务）"""
    await scheduler.start()

async def stop_scheduler():
    """停止调度器"""
    await scheduler.stop()

async def manual_sync_task(updated_since: Optional[str] = None):
    """手动同步任务（用于Celery）"""
    return await scheduler.manual_sync(updated_since)

# 如果直接运行此文件，启动调度器
if __name__ == "__main__":
    try:
        asyncio.run(scheduler.start())
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在停止调度器...")
        asyncio.run(scheduler.stop()) 