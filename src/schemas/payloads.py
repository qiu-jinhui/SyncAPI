"""
负载数据模式
定义各种实体类型的数据结构
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class ProjectPayload(BaseModel):
    """项目负载数据"""
    id: str = Field(..., description="项目ID")
    project_name: str = Field(..., description="项目名称")
    project_code: str = Field(..., description="项目代码")
    created_time: datetime = Field(..., description="创建时间")
    updated_time: datetime = Field(..., description="更新时间")

class UseCasePayload(BaseModel):
    """用例负载数据"""
    id: str = Field(..., description="用例ID")
    project_id: str = Field(..., description="项目ID")
    use_case_name: str = Field(..., description="用例名称")
    ad_group: str = Field(..., description="AD组")
    is_active: bool = Field(..., description="是否激活")
    created_time: datetime = Field(..., description="创建时间")
    updated_time: datetime = Field(..., description="更新时间")

class UseCaseBudgetPayload(BaseModel):
    """用例预算负载数据"""
    id: str = Field(..., description="预算ID")
    use_case_id: str = Field(..., description="用例ID")
    budget_cents: int = Field(..., description="预算金额（分）")
    currency: str = Field(..., description="货币类型")
    created_time: datetime = Field(..., description="创建时间")
    updated_time: datetime = Field(..., description="更新时间")

class ModelPayload(BaseModel):
    """模型负载数据"""
    id: str = Field(..., description="模型ID")
    model_name: str = Field(..., description="模型名称")
    model_type: str = Field(..., description="模型类型")
    provider: str = Field(..., description="提供商")
    model_input: str = Field(..., description="模型输入")
    model_output: str = Field(..., description="模型输出")
    max_content_length: int = Field(..., description="最大内容长度")
    created_time: datetime = Field(..., description="创建时间")
    updated_time: datetime = Field(..., description="更新时间")

class ModelDeploymentPayload(BaseModel):
    """模型部署负载数据"""
    id: str = Field(..., description="部署ID")
    model_id: str = Field(..., description="模型ID")
    deployment_name: str = Field(..., description="部署名称")
    endpoint: str = Field(..., description="端点URL")
    auth_secret_manager_path: str = Field(..., description="认证密钥管理器路径")
    region: str = Field(..., description="区域")
    request_per_min: int = Field(..., description="每分钟请求数")
    token_per_min: int = Field(..., description="每分钟令牌数")
    is_default: bool = Field(..., description="是否默认")
    created_time: datetime = Field(..., description="创建时间")
    updated_time: datetime = Field(..., description="更新时间")

class ModelPricingPayload(BaseModel):
    """模型定价负载数据"""
    id: str = Field(..., description="定价ID")
    model_id: str = Field(..., description="模型ID")
    input_token_price_cpm: int = Field(..., description="输入令牌价格（每千个）")
    output_token_price_cpm: int = Field(..., description="输出令牌价格（每千个）")
    currency: str = Field(..., description="货币类型")
    created_time: datetime = Field(..., description="创建时间")
    updated_time: datetime = Field(..., description="更新时间")

class SubscriptionPayload(BaseModel):
    """订阅负载数据"""
    id: str = Field(..., description="订阅ID")
    project_id: str = Field(..., description="项目ID")
    use_case_id: str = Field(..., description="用例ID")
    model_id: str = Field(..., description="模型ID")
    alias: str = Field(..., description="别名")
    created_time: datetime = Field(..., description="创建时间")
    updated_time: datetime = Field(..., description="更新时间")

class ModelLimitPayload(BaseModel):
    """模型限制负载数据"""
    id: str = Field(..., description="限制ID")
    subscription_id: str = Field(..., description="订阅ID")
    limit_type: str = Field(..., description="限制类型")
    scope: str = Field(..., description="作用域")
    limit_value: int = Field(..., description="限制值")
    created_time: datetime = Field(..., description="创建时间")
    updated_time: datetime = Field(..., description="更新时间") 