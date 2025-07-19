# 项目结构说明

## 已创建的文件和目录

### 📁 目录结构
```
synchronize_api/
├── src/                          # 源代码目录 (75个Python文件)
│   ├── main.py                   # FastAPI应用入口
│   ├── config/                   # 配置管理
│   │   ├── __init__.py
│   │   ├── settings.py           # 应用配置
│   │   └── database.py           # 数据库配置
│   ├── models/                   # 数据模型 (9个文件)
│   │   ├── __init__.py
│   │   ├── base.py               # 基础模型
│   │   ├── project.py            # 项目模型
│   │   ├── use_case.py           # 用例模型
│   │   ├── budget.py             # 预算模型
│   │   ├── model.py              # 模型定义
│   │   ├── deployment.py         # 部署模型
│   │   ├── pricing.py            # 定价模型
│   │   ├── subscription.py       # 订阅模型
│   │   └── limit.py              # 限制模型
│   ├── schemas/                  # API模式定义 (3个文件)
│   │   ├── __init__.py
│   │   ├── event_request.py      # 事件请求模式
│   │   ├── event_response.py     # 事件响应模式
│   │   └── payloads.py           # 负载数据模式
│   ├── repositories/             # 数据访问层 (9个文件)
│   │   ├── __init__.py
│   │   ├── base.py               # 基础仓储
│   │   ├── project_repository.py # 项目仓储
│   │   ├── use_case_repository.py # 用例仓储
│   │   ├── budget_repository.py  # 预算仓储
│   │   ├── model_repository.py   # 模型仓储
│   │   ├── deployment_repository.py # 部署仓储
│   │   ├── pricing_repository.py # 定价仓储
│   │   ├── subscription_repository.py # 订阅仓储
│   │   └── limit_repository.py   # 限制仓储
│   ├── services/                 # 业务逻辑层 (4个文件)
│   │   ├── __init__.py
│   │   ├── sync_service.py       # 同步服务
│   │   ├── event_service.py      # 事件服务
│   │   ├── model_garden_client.py # Model Garden客户端
│   │   └── redis_service.py      # Redis服务
│   ├── api/                      # API层 (2个文件)
│   │   ├── __init__.py
│   │   ├── dependencies.py       # 依赖注入
│   │   └── v1/                   # API版本1
│   │       ├── __init__.py
│   │       └── event_router.py   # 事件路由
│   ├── utils/                    # 工具模块 (3个文件)
│   │   ├── __init__.py
│   │   ├── logger.py             # 日志工具
│   │   ├── validators.py         # 验证工具
│   │   └── helpers.py            # 辅助工具
│   └── tasks/                    # 定时任务 (1个文件)
│       ├── __init__.py
│       └── sync_scheduler.py     # 同步调度器
├── tests/                        # 测试目录 (24个Python文件)
│   ├── __init__.py
│   ├── conftest.py               # 测试配置
│   ├── test_main.py              # 主应用测试
│   ├── test_database.py          # 数据库测试
│   ├── run_tests.py              # 测试运行脚本
│   ├── test_models/              # 模型测试 (8个文件)
│   │   ├── __init__.py
│   │   ├── test_project.py
│   │   ├── test_use_case.py
│   │   ├── test_budget.py
│   │   ├── test_model.py
│   │   ├── test_deployment.py
│   │   ├── test_pricing.py
│   │   ├── test_subscription.py
│   │   └── test_limit.py
│   ├── test_repositories/        # 仓储测试 (8个文件)
│   │   ├── __init__.py
│   │   ├── test_project_repository.py
│   │   ├── test_use_case_repository.py
│   │   ├── test_budget_repository.py
│   │   ├── test_model_repository.py
│   │   ├── test_deployment_repository.py
│   │   ├── test_pricing_repository.py
│   │   ├── test_subscription_repository.py
│   │   └── test_limit_repository.py
│   ├── test_services/            # 服务测试 (4个文件)
│   │   ├── __init__.py
│   │   ├── test_sync_service.py
│   │   ├── test_event_service.py
│   │   ├── test_model_garden_client.py
│   │   └── test_redis_service.py
│   └── test_api/                 # API测试 (1个文件)
│       ├── __init__.py
│       └── test_event_router.py
├── alembic/                      # 数据库迁移 (3个文件)
│   ├── versions/                 # 迁移版本目录
│   ├── env.py                    # 迁移环境
│   ├── script.py.mako            # 迁移模板
│   └── alembic.ini               # Alembic配置
├── docker/                       # Docker配置 (3个文件)
│   ├── Dockerfile                # 应用Dockerfile
│   ├── docker-compose.yml        # 开发环境
│   └── docker-compose.prod.yml   # 生产环境
├── scripts/                      # 脚本文件 (3个文件)
│   ├── setup.sh                  # 环境设置脚本
│   ├── migrate.sh                # 数据库迁移脚本
│   └── deploy.sh                 # 部署脚本
├── .gitignore                    # Git忽略文件
├── env.example                   # 环境变量示例
├── pyproject.toml                # Poetry配置
├── requirements.txt              # 依赖列表
├── README.md                     # 项目说明
├── PROJECT_STRUCTURE.md          # 项目结构说明
└── docker-compose.yml            # 本地开发环境
```

### 📊 文件统计
- **总文件数**: 92个文件
- **Python文件**: 75个
- **配置文件**: 17个
- **目录数**: 20个

### 🎯 核心功能模块

1. **数据模型层** (`src/models/`)
   - 8个数据模型，对应数据库表结构
   - 基础模型提供通用字段和方法

2. **API模式层** (`src/schemas/`)
   - 事件请求模式：接收Model Garden的CUD事件
   - 事件响应模式：返回处理结果
   - 负载数据模式：定义各种实体类型的数据结构

3. **数据访问层** (`src/repositories/`)
   - 8个仓储类，对应每个数据模型
   - 基础仓储提供通用CRUD操作

4. **业务逻辑层** (`src/services/`)
   - 同步服务：处理从Model Garden获取的数据
   - 事件服务：处理CUD事件
   - Model Garden客户端：调用外部API
   - Redis服务：缓存和事件发布

5. **API层** (`src/api/`)
   - 事件路由：`/api/v1/model-garden/events` (接收Model Garden事件)
   - 健康检查：`/api/v1/model-garden/health`
   - 依赖注入配置

6. **工具模块** (`src/utils/`)
   - 日志工具：结构化日志
   - 验证工具：数据验证
   - 辅助工具：通用功能

7. **定时任务** (`src/tasks/`)
   - 同步调度器：定时调用Model Garden的 `/model-garden/sync/all` API

### 🧪 测试结构

1. **模型测试** (`tests/test_models/`)
   - 8个模型测试文件
   - 数据验证和关系测试

2. **仓储测试** (`tests/test_repositories/`)
   - 8个仓储测试文件
   - CRUD操作和事务测试

3. **服务测试** (`tests/test_services/`)
   - 4个服务测试文件
   - 业务逻辑和外部API调用测试

4. **API测试** (`tests/test_api/`)
   - 1个API测试文件
   - 事件接收端点测试

### 🐳 部署配置

1. **Docker配置**
   - 多阶段构建的Dockerfile
   - 开发和生产环境的docker-compose文件

2. **脚本文件**
   - 环境设置脚本
   - 数据库迁移脚本
   - 部署脚本

### 📋 下一步开发计划

1. **实现数据模型** - 根据数据库schema定义所有模型
2. **实现API模式** - 完善事件请求响应模式
3. **实现仓储层** - 数据访问和CRUD操作
4. **实现服务层** - 业务逻辑和外部API调用
5. **实现API路由** - 完善事件接收端点
6. **实现测试** - 单元测试、集成测试、API测试
7. **配置部署** - Docker化和生产环境配置

### 🚀 快速开始

```bash
# 进入项目目录
cd synchronize_api

# 运行环境设置脚本
./scripts/setup.sh

# 配置环境变量
cp env.example .env
# 编辑 .env 文件

# 运行数据库迁移
./scripts/migrate.sh

# 启动应用
poetry run uvicorn src.main:app --reload
```

### 🔄 API调用关系

1. **Sync API → Model Garden**: 定时调用 `/model-garden/sync/all` 获取全量数据
2. **Model Garden → Sync API**: 实时调用 `/api/v1/model-garden/events` 发送CUD事件

项目结构已根据正确的API调用关系调整完成，所有必要的文件和目录都已就绪，可以开始具体的代码实现了。 