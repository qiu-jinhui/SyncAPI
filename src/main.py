"""
同步API主应用
提供Model Garden事件接收服务
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import structlog

from src.api.v1.event_router import router as event_router
from src.config.settings import get_settings
from src.utils.logger import setup_logging

# 设置日志
setup_logging()
logger = structlog.get_logger()

# 获取配置
settings = get_settings()

# 创建FastAPI应用
app = FastAPI(
    title="Synchronize API",
    description="同步API系统，用于接收Model Garden的CUD事件",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # 记录请求信息
    logger.info(
        "Incoming request",
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host if request.client else None
    )
    
    response = await call_next(request)
    
    # 记录响应信息
    process_time = time.time() - start_time
    logger.info(
        "Request completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=f"{process_time:.3f}s"
    )
    
    return response

# 异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception",
        method=request.method,
        url=str(request.url),
        error=str(exc),
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )

# 注册路由
app.include_router(event_router, tags=["events"])

@app.get("/", summary="根路径")
async def root():
    """根路径，返回API信息"""
    return {
        "message": "Synchronize API",
        "version": "1.0.0",
        "description": "同步API系统，用于接收Model Garden的CUD事件"
    }

@app.get("/health", summary="健康检查")
async def health():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "synchronize-api",
        "version": "1.0.0",
        "timestamp": time.time()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    ) 