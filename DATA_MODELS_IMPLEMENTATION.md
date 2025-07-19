# 数据模型实现总结

## 概述

已成功实现所有数据模型，完全按照数据库schema文档设计。所有模型都继承自`BaseModel`，提供了统一的字段和方法。

## 实现的模型

### 1. 基础模型 (`src/models/base.py`)
- **BaseModel**: 所有模型的基类
- **功能**:
  - 自动生成UUID主键
  - 自动管理创建时间和更新时间
  - 提供`to_dict()`和`from_dict()`方法
  - 提供`update_from_dict()`方法
  - 自动生成表名

### 2. 项目模型 (`src/models/project.py`)
- **Project**: 项目表
- **字段**:
  - `project_name`: 项目名称 (VARCHAR, 索引)
  - `project_code`: 项目代码 (VARCHAR, 唯一索引)
- **关系**: 一对多用例、一对多订阅

### 3. 用例模型 (`src/models/use_case.py`)
- **UseCase**: 用例表
- **字段**:
  - `project_id`: 项目ID (UUID, 外键, 索引)
  - `use_case_name`: 用例名称 (VARCHAR, 索引)
  - `ad_group`: AD组 (VARCHAR)
  - `is_active`: 是否激活 (BOOLEAN, 默认TRUE, 索引)
- **关系**: 多对一项目、一对多预算、一对多订阅

### 4. 预算模型 (`src/models/budget.py`)
- **UseCaseBudget**: 用例预算表
  - `use_case_id`: 用例ID (UUID, 外键, 索引)
  - `budget_cents`: 预算金额分 (BIGINT)
  - `currency`: 货币类型 (VARCHAR, 默认USD)
  - 提供`budget_amount`属性（元）

- **UseCaseBudgetUsage**: 用例预算使用表
  - `use_case_id`: 用例ID (UUID, 外键, 索引)
  - `usage_period`: 使用期间 (DATE)
  - `scope`: 作用域 (VARCHAR) - daily, monthly, yearly
  - `used_cents`: 已使用金额分 (BIGINT, 默认0)
  - `currency`: 货币类型 (VARCHAR, 默认USD)
  - 唯一约束: (use_case_id, usage_period, scope)
  - 提供`used_amount`属性（元）

### 5. 模型定义 (`src/models/model.py`)
- **Model**: 模型表
- **字段**:
  - `model_name`: 模型名称 (VARCHAR, 索引)
  - `model_type`: 模型类型 (VARCHAR, 索引) - chat, completion, embedding等
  - `provider`: 提供商 (VARCHAR, 索引) - openai, anthropic, google等
  - `model_input`: 模型输入 (VARCHAR) - text, image, audio等
  - `model_output`: 模型输出 (VARCHAR) - text, image, audio等
  - `max_content_length`: 最大内容长度 (INT)
- **关系**: 一对多部署、一对多定价、一对多订阅

### 6. 部署模型 (`src/models/deployment.py`)
- **ModelDeployment**: 模型部署表
- **字段**:
  - `model_id`: 模型ID (UUID, 外键, 索引)
  - `deployment_name`: 部署名称 (VARCHAR, 索引)
  - `endpoint`: 端点URL (TEXT)
  - `auth_secret_manager_path`: 认证密钥路径 (TEXT)
  - `region`: 区域 (VARCHAR, 索引)
  - `request_per_min`: 每分钟请求数 (INT)
  - `token_per_min`: 每分钟令牌数 (INT)
  - `is_default`: 是否默认 (BOOLEAN, 默认FALSE, 索引)
- **唯一约束**: (model_id, deployment_name)
- **关系**: 多对一模型

### 7. 定价模型 (`src/models/pricing.py`)
- **ModelPricing**: 模型定价表
- **字段**:
  - `model_id`: 模型ID (UUID, 外键, 索引)
  - `input_token_price_cpm`: 输入令牌价格/千个 (INT, 分)
  - `output_token_price_cpm`: 输出令牌价格/千个 (INT, 分)
  - `currency`: 货币类型 (VARCHAR, 默认USD)
- **功能**:
  - 提供价格计算属性
  - 提供成本计算方法
- **关系**: 多对一模型

### 8. 订阅模型 (`src/models/subscription.py`)
- **Subscription**: 订阅表
- **字段**:
  - `project_id`: 项目ID (UUID, 外键, 索引)
  - `use_case_id`: 用例ID (UUID, 外键, 索引)
  - `model_id`: 模型ID (UUID, 外键, 索引)
- **功能**:
  - 提供`subscription_key`属性用于缓存
- **关系**: 多对一项目、多对一用例、多对一模型、一对多限制

### 9. 限制模型 (`src/models/limit.py`)
- **ModelLimit**: 模型限制表
  - `subscription_id`: 订阅ID (UUID, 外键, 索引)
  - `limit_type`: 限制类型 (VARCHAR, 索引) - input_token_limit, output_token_limit, request_limit等
  - `scope`: 作用域 (VARCHAR, 索引) - daily, monthly, yearly
  - `limit_value`: 限制值 (BIGINT)

- **ModelLimitUsage**: 模型限制使用表
  - `limit_id`: 限制ID (UUID, 外键, 索引)
  - `scope`: 作用域 (VARCHAR, 索引)
  - `usage_period`: 使用期间 (TIMESTAMP, 索引)
  - `value`: 使用值 (BIGINT, 默认0)
  - `request_id`: 请求ID (UUID, 索引)
  - `called_by`: 调用者 (VARCHAR)

## 模型特性

### 1. 统一的基础功能
- 自动UUID主键生成
- 自动时间戳管理
- 字典转换方法
- 字符串表示方法

### 2. 关系映射
- 使用SQLAlchemy ORM关系映射
- 支持级联删除
- 双向关系定义

### 3. 属性别名
- 提供简化的属性访问
- 支持金额单位转换（分↔元）
- 支持价格计算

### 4. 约束和索引
- 外键约束
- 唯一约束
- 数据库索引
- 默认值设置

## 测试覆盖

### 已实现的测试
1. **test_project.py** - 项目模型测试
2. **test_model.py** - 模型定义测试
3. **test_pricing.py** - 定价模型测试
4. **test_relationships.py** - 模型关系测试

### 测试内容
- 模型创建和字段验证
- 字符串表示方法
- 属性访问
- 字典转换
- 关系验证
- 价格计算
- 约束验证

## 数据库表结构

所有模型都严格按照schema文档设计：

```sql
-- 主要表结构
projects (id, project_name, project_code, created_time, updated_time)
use_cases (id, project_id, use_case_name, ad_group, is_active, created_time, updated_time)
use_case_budget (id, use_case_id, budget_cents, currency, created_time, updated_time)
use_case_budget_usage (id, use_case_id, usage_period, scope, used_cents, currency, created_time, updated_time)
models (id, model_name, model_type, provider, model_input, model_output, max_content_length, created_time, updated_time)
model_deployments (id, model_id, deployment_name, endpoint, auth_secret_manager_path, region, request_per_min, token_per_min, is_default, created_time, updated_time)
llm_model_pricing (id, model_id, input_token_price_cpm, output_token_price_cpm, currency, created_time, updated_time)
subscriptions (id, project_id, use_case_id, model_id, created_time, updated_time)
llm_model_limits (id, subscription_id, limit_type, scope, limit_value, created_time, updated_time)
llm_model_limits_usage (id, limit_id, scope, usage_period, value, request_id, called_by, created_time)
```

## 下一步

1. **实现仓储层** - 为每个模型创建数据访问层
2. **实现服务层** - 业务逻辑处理
3. **实现API层** - 事件接收和处理
4. **数据库迁移** - 创建Alembic迁移文件
5. **集成测试** - 数据库集成测试

数据模型实现完成，所有表结构、关系、约束都已正确定义，可以开始实现仓储层了。 