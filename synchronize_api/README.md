# 同步API项目

## 项目概述

这是一个同步API系统，用于同步Model Garden的模型信息到GatewayDB。该系统包含两个主要功能：

1. **全量同步API** (`/api/v1/model-garden/sync/all`) - 定时调用，同步所有数据
2. **事件同步API** (`/api/v1/model-garden/events`) - 实时调用，处理CUD事件

## 技术栈

- **框架**: FastAPI
- **包管理**: Poetry
- **数据库**: PostgreSQL + SQLAlchemy
- **缓存**: Redis (包含Redis Stream)
- **测试**: pytest (覆盖率目标95%)
- **部署**: Docker
- **服务器**: uvicorn

## 项目结构

```
synchronize_api/
├── src/                          # 源代码目录
│   ├── main.py                   # FastAPI应用入口
│   ├── config/                   # 配置管理
│   │   ├── settings.py           # 应用配置
│   │   └── database.py           # 数据库配置
│   ├── models/                   # 数据模型
│   │   ├── base.py               # 基础模型
│   │   ├── project.py            # 项目模型
│   │   ├── use_case.py           # 用例模型
│   │   ├── budget.py             # 预算模型
│   │   ├── model.py              # 模型定义
│   │   ├── deployment.py         # 部署模型
│   │   ├── pricing.py            # 定价模型
│   │   ├── subscription.py       # 订阅模型
│   │   └── limit.py              # 限制模型
│   ├── schemas/                  # API模式定义
│   │   ├── sync_request.py       # 同步请求模式
│   │   ├── sync_response.py      # 同步响应模式
│   │   ├── event_request.py      # 事件请求模式
│   │   └── event_response.py     # 事件响应模式
│   ├── repositories/             # 数据访问层
│   │   ├── base.py               # 基础仓储
│   │   ├── project_repository.py # 项目仓储
│   │   ├── use_case_repository.py # 用例仓储
│   │   ├── budget_repository.py  # 预算仓储
│   │   ├── model_repository.py   # 模型仓储
│   │   ├── deployment_repository.py # 部署仓储
│   │   ├── pricing_repository.py # 定价仓储
│   │   ├── subscription_repository.py # 订阅仓储
│   │   └── limit_repository.py   # 限制仓储
│   ├── services/                 # 业务逻辑层
│   │   ├── sync_service.py       # 同步服务
│   │   ├── event_service.py      # 事件服务
│   │   ├── model_garden_client.py # Model Garden客户端
│   │   └── redis_service.py      # Redis服务
│   ├── api/                      # API层
│   │   ├── dependencies.py       # 依赖注入
│   │   └── v1/                   # API版本1
│   │       ├── sync_router.py    # 同步路由
│   │       └── event_router.py   # 事件路由
│   ├── utils/                    # 工具模块
│   │   ├── logger.py             # 日志工具
│   │   ├── validators.py         # 验证工具
│   │   └── helpers.py            # 辅助工具
│   └── tasks/                    # 定时任务
│       └── sync_scheduler.py     # 同步调度器
├── tests/                        # 测试目录
│   ├── conftest.py               # 测试配置
│   ├── test_main.py              # 主应用测试
│   ├── test_database.py          # 数据库测试
│   ├── run_tests.py              # 测试运行脚本
│   ├── test_models/              # 模型测试
│   ├── test_repositories/        # 仓储测试
│   ├── test_services/            # 服务测试
│   └── test_api/                 # API测试
├── alembic/                      # 数据库迁移
│   ├── versions/                 # 迁移版本
│   ├── env.py                    # 迁移环境
│   ├── script.py.mako            # 迁移模板
│   └── alembic.ini               # Alembic配置
├── docker/                       # Docker配置
│   ├── Dockerfile                # 应用Dockerfile
│   ├── docker-compose.yml        # 开发环境
│   └── docker-compose.prod.yml   # 生产环境
├── scripts/                      # 脚本文件
│   ├── setup.sh                  # 环境设置脚本
│   ├── migrate.sh                # 数据库迁移脚本
│   └── deploy.sh                 # 部署脚本
├── .env                          # 环境变量
├── .env.example                  # 环境变量示例
├── .gitignore                    # Git忽略文件
├── pyproject.toml                # Poetry配置
├── requirements.txt              # 依赖列表
└── docker-compose.yml            # 本地开发环境
```

## 快速开始

### 1. 环境准备

```bash
# 进入项目目录
cd synchronize_api

# 安装Poetry (如果未安装)
curl -sSL https://install.python-poetry.org | python3 -

# 安装依赖
poetry install
```

### 2. 环境配置

```bash
# 复制环境变量文件
cp .env.example .env

# 编辑环境变量
vim .env
```

### 3. 数据库设置

```bash
# 运行数据库迁移
poetry run alembic upgrade head
```

### 4. 启动应用

```bash
# 开发环境启动
poetry run uvicorn src.main:app --reload

# 或者使用Docker
docker-compose up
```

## API文档

启动应用后，可以访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 测试

```bash
# 运行所有测试
poetry run pytest

# 运行测试并生成覆盖率报告
poetry run pytest --cov=src --cov-report=html

# 运行特定测试
poetry run pytest tests/test_models/
```

## 部署

```bash
# 构建Docker镜像
docker build -f docker/Dockerfile -t synchronize-api .

# 运行生产环境
docker-compose -f docker/docker-compose.prod.yml up -d
```

## 开发指南

详细的开发指南请参考 `Synchronize_API_implemetation.txt` 文件。

## 许可证

MIT License
