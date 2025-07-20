# 📚 Synchronize API - Swagger 文档

## 🎯 概述

Synchronize API 是一个用于同步 Model Garden 模型信息到 GatewayDB 的系统。该 API 提供两个主要功能：

1. **全量同步API** - 定时调用，同步所有数据
2. **事件同步API** - 实时调用，处理CUD事件

## 📖 文档访问方式

### 1. 在线文档 (推荐)
启动API服务器后，可通过以下地址访问：

```bash
# 启动服务器
source venv/bin/activate
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

然后访问：
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **OpenAPI JSON**: http://127.0.0.1:8000/openapi.json

### 2. 离线文档
项目根目录提供了以下离线文档：

- **`swagger_docs.html`** - 完整的Swagger UI页面，双击打开即可
- **`swagger_openapi.json`** - OpenAPI 3.1.0 规范的JSON文件

## 🔧 主要API端点

### 全量同步
- **POST** `/api/v1/model-garden/sync/all`
- **描述**: 从Model Garden同步所有配置数据到本地数据库
- **请求体**: 可选的`SyncRequest`，包含`updated_since`参数用于增量同步
- **响应**: `SyncResponse`包含所有同步的实体数据

### 事件接收
- **POST** `/api/v1/model-garden/events`
- **描述**: 接收并处理来自Model Garden的CUD事件
- **请求体**: `EventRequest`包含事件类型、实体信息和负载数据
- **响应**: `EventResponse`包含处理状态

### 同步状态查询
- **GET** `/api/v1/model-garden/sync/status`
- **描述**: 获取最近的同步任务状态信息
- **响应**: 包含服务状态、版本等信息

### 健康检查
- **GET** `/api/v1/model-garden/health`
- **描述**: 检查API服务状态
- **响应**: 服务健康状态信息

## 📊 数据模型

API支持以下数据实体：

- **ProjectPayload** - 项目数据
- **UseCasePayload** - 用例数据  
- **UseCaseBudgetPayload** - 预算数据
- **ModelPayload** - 模型数据
- **ModelDeploymentPayload** - 部署数据
- **ModelPricingPayload** - 定价数据
- **SubscriptionPayload** - 订阅数据
- **ModelLimitPayload** - 限制数据

## 🚀 快速测试

### 1. 健康检查
```bash
curl http://127.0.0.1:8000/health
```

### 2. 全量同步（无参数）
```bash
curl -X POST http://127.0.0.1:8000/api/v1/model-garden/sync/all \
  -H "Content-Type: application/json"
```

### 3. 增量同步
```bash
curl -X POST http://127.0.0.1:8000/api/v1/model-garden/sync/all \
  -H "Content-Type: application/json" \
  -d '{"updated_since": "2025-07-01T00:00:00Z"}'
```

### 4. 发送事件
```bash
curl -X POST http://127.0.0.1:8000/api/v1/model-garden/events \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "evt-001",
    "event_type": "CREATED",
    "entity_type": "project", 
    "entity_id": "proj-001",
    "timestamp": "2025-07-15T14:20:00Z",
    "version": "1.0",
    "payload": {
      "id": "proj-001",
      "project_name": "Test Project",
      "project_code": "TEST",
      "created_time": "2025-07-15T14:00:00Z",
      "updated_time": "2025-07-15T14:00:00Z"
    }
  }'
```

## 📋 API规范信息

- **OpenAPI版本**: 3.1.0
- **API版本**: 1.0.0
- **支持的数据格式**: JSON
- **字符编码**: UTF-8
- **时间格式**: ISO 8601 (YYYY-MM-DDTHH:mm:ssZ)

## 🛠️ 开发工具

### 导入Postman
1. 下载 `swagger_openapi.json` 文件
2. 在Postman中选择 Import > Upload Files
3. 选择JSON文件即可导入所有API

### 代码生成
可以使用OpenAPI Generator基于`swagger_openapi.json`生成各种语言的客户端代码：

```bash
# 安装OpenAPI Generator
npm install -g @openapitools/openapi-generator-cli

# 生成Python客户端
openapi-generator-cli generate -i swagger_openapi.json -g python -o ./python-client

# 生成JavaScript客户端  
openapi-generator-cli generate -i swagger_openapi.json -g javascript -o ./js-client
```

## 📞 支持

如有问题或建议，请联系开发团队或查看项目文档。

---

**最后更新**: 2025-07-20  
**API版本**: 1.0.0 