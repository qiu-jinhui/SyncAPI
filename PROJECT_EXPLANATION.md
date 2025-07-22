# 🔄 Synchronize API 项目详解

## 📋 项目概述

**Synchronize API** 是一个基于 FastAPI 的高性能同步系统，用于同步 Model Garden 的模型配置信息到 Gateway 数据库。项目采用现代的微服务架构，支持全量同步和实时事件处理。

### 🎯 核心功能
1. **全量同步**: 定时从 Model Garden 拉取所有配置数据
2. **事件同步**: 实时处理 Model Garden 的 CUD (创建/更新/删除) 事件
3. **数据管理**: 管理 8 种核心实体的数据同步

## 🏗️ 项目结构详解

```
SyncAPI/
├── 📁 src/                          # 主要源代码目录
│   ├── 📁 api/                      # API接口层
│   │   ├── dependencies.py         # 依赖注入配置
│   │   └── 📁 v1/                   # API v1版本
│   │       ├── event_router.py     # 事件接收路由
│   │       └── sync_router.py      # 同步操作路由
│   ├── 📁 config/                   # 配置管理
│   │   ├── database.py             # 数据库连接配置
│   │   └── settings.py             # 应用设置
│   ├── 📁 models/                   # 数据模型定义 (SQLAlchemy ORM)
│   │   ├── base.py                 # 基础模型类
│   │   ├── project.py              # 项目模型
│   │   ├── use_case.py             # 用例模型
│   │   ├── budget.py               # 预算模型
│   │   ├── model.py                # LLM模型
│   │   ├── deployment.py           # 部署模型
│   │   ├── pricing.py              # 定价模型
│   │   ├── subscription.py         # 订阅模型
│   │   └── limit.py                # 限制模型
│   ├── 📁 repositories/             # 数据访问层 (Repository模式)
│   │   ├── base_repository.py      # 基础仓储类
│   │   ├── project_repository.py   # 项目数据访问
│   │   ├── use_case_repository.py  # 用例数据访问
│   │   ├── budget_repository.py    # 预算数据访问
│   │   ├── model_repository.py     # 模型数据访问
│   │   ├── deployment_repository.py# 部署数据访问
│   │   ├── pricing_repository.py   # 定价数据访问
│   │   ├── subscription_repository.py # 订阅数据访问
│   │   └── limit_repository.py     # 限制数据访问
│   ├── 📁 schemas/                  # API数据模式 (Pydantic)
│   │   ├── event_request.py        # 事件请求模式
│   │   ├── event_response.py       # 事件响应模式
│   │   ├── sync_request.py         # 同步请求模式
│   │   ├── sync_response.py        # 同步响应模式
│   │   └── payloads.py             # 负载数据模式
│   ├── 📁 services/                 # 业务逻辑层
│   │   ├── event_service.py        # 事件处理服务
│   │   ├── sync_service.py         # 同步业务逻辑
│   │   ├── model_garden_client.py  # Model Garden API客户端
│   │   └── redis_service.py        # Redis缓存服务
│   ├── 📁 tasks/                    # 定时任务
│   │   └── sync_scheduler.py       # 同步调度器
│   ├── 📁 utils/                    # 工具模块
│   │   └── logger.py               # 日志配置
│   └── main.py                     # FastAPI应用入口
├── 📁 tests/                        # 测试代码
│   ├── conftest.py                 # 测试配置和fixtures
│   ├── 📁 test_api/                # API层测试
│   │   ├── test_dependencies.py   # 依赖注入测试
│   │   ├── test_event_router.py   # 事件路由测试
│   │   └── test_sync_router.py    # 同步路由测试
│   ├── 📁 test_services/           # 服务层测试
│   │   ├── test_event_service.py  # 事件服务测试
│   │   ├── test_sync_service.py   # 同步服务测试
│   │   ├── test_model_garden_client.py # 客户端测试
│   │   └── test_redis_service.py  # Redis服务测试
│   ├── 📁 test_repositories/       # 仓储层测试
│   │   └── test_*.py              # 各仓储类测试
│   └── 📁 test_models/             # 模型层测试
├── 📁 synchronize_api/              # 参考项目结构 (Poetry配置)
├── 📁 venv/                         # Python虚拟环境
├── 📄 swagger_docs.html            # Swagger文档 (生成)
├── 📄 swagger_openapi.json         # OpenAPI规范 (生成)
├── 📄 SWAGGER_DOCS_README.md       # 文档说明 (生成)
└── 📄 sync-api-design.md           # 设计文档
```

## 🔧 代码架构详解

### 1. 分层架构 (Layered Architecture)

项目采用经典的分层架构模式：

```
┌─────────────────────────────────────┐
│          API Layer (FastAPI)        │  ← HTTP接口层
├─────────────────────────────────────┤
│       Service Layer (Business)      │  ← 业务逻辑层
├─────────────────────────────────────┤
│     Repository Layer (Data Access)  │  ← 数据访问层
├─────────────────────────────────────┤
│      Model Layer (SQLAlchemy)       │  ← 数据模型层
└─────────────────────────────────────┘
```

### 2. 核心模块说明

#### 🌐 API层 (`src/api/`)
- **FastAPI路由**: 定义HTTP端点和请求处理
- **依赖注入**: 管理服务实例的创建和生命周期
- **数据验证**: 使用Pydantic进行请求/响应验证

```python
# 示例: 同步路由
@router.post("/api/v1/model-garden/sync/all")
async def sync_all(
    request: Optional[SyncRequest] = Body(None),
    sync_service: SyncService = Depends(get_sync_service)
) -> SyncResponse:
    # 业务逻辑委托给服务层
    return await sync_service.sync_all(request.updated_since)
```

#### 🎯 服务层 (`src/services/`)
- **事件服务**: 处理CUD事件的业务逻辑
- **同步服务**: 实现全量/增量同步算法
- **外部客户端**: 封装Model Garden API调用
- **缓存服务**: Redis操作和Stream事件

```python
# 示例: 同步服务核心逻辑
class SyncService:
    async def sync_all(self, updated_since: Optional[datetime]) -> Dict:
        # 1. 调用Model Garden API
        data = await self.model_garden_client.sync_all(updated_since)
        # 2. 批量更新数据库
        results = await self._sync_entities(data)
        # 3. 发布Redis事件
        await self.redis_service.publish_event("sync_completed", results)
        return results
```

#### 🗄️ 仓储层 (`src/repositories/`)
- **Repository模式**: 封装数据访问逻辑
- **基础仓储**: 提供通用CRUD操作
- **专用仓储**: 实现特定实体的查询逻辑

```python
# 示例: 项目仓储
class ProjectRepository(BaseRepository[Project]):
    def find_by_code(self, project_code: str) -> Optional[Project]:
        return self.session.query(Project).filter(
            Project.project_code == project_code
        ).first()
```

#### 📊 模型层 (`src/models/`)
- **SQLAlchemy ORM**: 数据库表映射
- **关系定义**: 实体间的外键和关联关系
- **数据约束**: 字段验证和索引定义

```python
# 示例: 项目模型
class Project(BaseModel):
    __tablename__ = "projects"
    
    project_name = Column(String(255), nullable=False)
    project_code = Column(String(100), nullable=False, unique=True)
    
    # 关联关系
    use_cases = relationship("UseCase", back_populates="project")
```

### 3. 设计模式应用

- **Repository模式**: 数据访问抽象
- **依赖注入**: 控制反转和松耦合
- **工厂模式**: 服务实例创建
- **观察者模式**: Redis事件发布订阅

## 🚀 启动指南

### 1. 环境准备

```bash
# 1. 激活虚拟环境
source venv/bin/activate

# 2. 安装依赖 (如果还没安装)
pip install -i https://mirrors.aliyun.com/pypi/simple/ \
    fastapi uvicorn sqlalchemy redis pydantic python-dotenv structlog httpx

# 3. 检查Python版本 (需要 3.9+)
python --version
```

### 2. 配置环境变量

```bash
# 创建环境配置文件 (可选)
cp synchronize_api/env.example .env

# 编辑配置
# vim .env  
# 配置数据库连接、Redis地址等
```

### 3. 启动应用

#### 开发模式启动
```bash
# 方式1: 直接启动 (推荐)
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload

# 方式2: Python模块启动
python -m uvicorn src.main:app --reload

# 方式3: 通过main.py启动
python src/main.py
```

#### 生产模式启动
```bash
# 多进程启动
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4

# 使用Gunicorn (推荐生产环境)
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 4. 验证启动

```bash
# 健康检查
curl http://127.0.0.1:8000/health

# API文档
# 浏览器访问: http://127.0.0.1:8000/docs
```

## 🧪 测试运行指南

### 1. 测试环境配置

```bash
# 激活虚拟环境
source venv/bin/activate

# 安装测试依赖
pip install -i https://mirrors.aliyun.com/pypi/simple/ \
    pytest pytest-cov pytest-asyncio pytest-mock
```

### 2. 运行所有测试

```bash
# 运行全部测试
python -m pytest tests/ -v

# 运行指定模块测试
python -m pytest tests/test_api/ -v
python -m pytest tests/test_services/ -v
python -m pytest tests/test_repositories/ -v
```

### 3. 覆盖率测试

```bash
# 生成覆盖率报告
python -m pytest tests/ --cov=src --cov-report=term-missing

# 生成HTML覆盖率报告
python -m pytest tests/ --cov=src --cov-report=html

# 查看HTML报告
open htmlcov/index.html
```

### 4. 特定层级测试

```bash
# API层测试 (100%覆盖率)
python -m pytest tests/test_api/ --cov=src/api --cov-report=term

# 服务层测试 (99%覆盖率)
python -m pytest tests/test_services/ --cov=src/services --cov-report=term

# 仓储层测试 (90%+覆盖率)
python -m pytest tests/test_repositories/ --cov=src/repositories --cov-report=term
```

### 5. 测试结果解读

```bash
# 测试统计示例
================================ test session starts ================================
tests/test_api/test_sync_router.py ✓✓✓✓✓✓✓✓✓✓          (17个测试通过)
tests/test_api/test_event_router.py ✓✓✓✓✓✓✓✓✓✓✓        (12个测试通过)
tests/test_api/test_dependencies.py ✓✓✓✓✓✓✓✓✓          (9个测试通过)

总计: 38个测试, 38个通过, 0个失败
覆盖率: src/api/ 100%
```

## 🔌 API使用示例

### 1. 健康检查
```bash
curl http://127.0.0.1:8000/health
# 响应: {"status":"healthy","service":"synchronize-api","version":"1.0.0"}
```

### 2. 全量同步
```bash
# 无参数全量同步
curl -X POST http://127.0.0.1:8000/api/v1/model-garden/sync/all \
  -H "Content-Type: application/json"

# 增量同步 (从指定时间开始)
curl -X POST http://127.0.0.1:8000/api/v1/model-garden/sync/all \
  -H "Content-Type: application/json" \
  -d '{"updated_since": "2025-07-01T00:00:00Z"}'
```

### 3. 事件接收
```bash
curl -X POST http://127.0.0.1:8000/api/v1/model-garden/events \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "evt-001",
    "event_type": "CREATED",
    "entity_type": "project",
    "entity_id": "proj-001",
    "timestamp": "2025-07-20T14:00:00Z",
    "version": "1.0",
    "payload": {
      "id": "proj-001",
      "project_name": "Test Project",
      "project_code": "TEST",
      "created_time": "2025-07-20T14:00:00Z",
      "updated_time": "2025-07-20T14:00:00Z"
    }
  }'
```

## 📊 监控和调试

### 1. 日志查看
```bash
# 应用日志 (结构化JSON格式)
tail -f logs/app.log

# 实时日志 (开发模式)
# 启动时添加 --log-level debug
```

### 2. 性能监控
```bash
# API响应时间统计
curl -w "@curl-format.txt" -s -o /dev/null http://127.0.0.1:8000/health

# 内存使用监控
ps aux | grep python | grep uvicorn
```

### 3. 数据库状态
```bash
# 连接数检查
# 需要配置数据库后查看
```

## ⚠️ 注意事项

### 1. 依赖要求
- **Python**: 3.9+ (推荐 3.11)
- **数据库**: PostgreSQL (生产) / SQLite (开发)
- **缓存**: Redis 6.0+
- **系统**: macOS/Linux (Windows需WSL)

### 2. 已知问题
- 部分测试需要修复 (16个失败测试)
- 数据库迁移未配置 (需要Alembic)
- 环境变量配置不完整

### 3. 开发建议
- 使用虚拟环境隔离依赖
- 遵循代码覆盖率 ≥95% 要求
- 提交前运行全部测试
- 保持API文档同步更新

## 📚 相关文档

- **API文档**: `swagger_docs.html` (交互式)
- **设计文档**: `sync-api-design.md`
- **API规范**: `sync-api.yml` / `sync-api-event.yml`
- **项目说明**: `README.md`

---

**最后更新**: 2025-07-20  
**项目版本**: 1.0.0  
**架构**: FastAPI + SQLAlchemy + Redis 