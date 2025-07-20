"""
同步API响应数据模式
"""

from typing import List
from pydantic import BaseModel, Field

from src.schemas.payloads import (
    ProjectPayload,
    UseCasePayload,
    UseCaseBudgetPayload,
    ModelPayload,
    ModelDeploymentPayload,
    ModelPricingPayload,
    SubscriptionPayload,
    ModelLimitPayload
)


class SyncResponse(BaseModel):
    """
    全量同步响应模式
    包含所有同步的实体数据
    """
    projects: List[ProjectPayload] = Field(
        default_factory=list,
        description="项目列表"
    )
    use_cases: List[UseCasePayload] = Field(
        default_factory=list,
        description="用例列表"
    )
    budgets: List[UseCaseBudgetPayload] = Field(
        default_factory=list,
        description="预算列表"
    )
    models: List[ModelPayload] = Field(
        default_factory=list,
        description="模型列表"
    )
    model_deployments: List[ModelDeploymentPayload] = Field(
        default_factory=list,
        description="模型部署列表"
    )
    pricing: List[ModelPricingPayload] = Field(
        default_factory=list,
        description="模型定价列表"
    )
    use_case_llm_models: List[SubscriptionPayload] = Field(
        default_factory=list,
        description="用例LLM模型订阅列表"
    )
    limits: List[ModelLimitPayload] = Field(
        default_factory=list,
        description="模型限制列表"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "projects": [
                    {
                        "id": "proj-001",
                        "project_name": "Credit AI",
                        "project_code": "CREDIT_AI",
                        "created_time": "2025-01-01T00:00:00Z",
                        "updated_time": "2025-07-10T10:00:00Z"
                    }
                ],
                "use_cases": [
                    {
                        "id": "uc-001",
                        "project_id": "proj-001",
                        "use_case_name": "fraud_detection",
                        "ad_group": "ad_fraud",
                        "is_active": True,
                        "created_time": "2025-01-05T00:00:00Z",
                        "updated_time": "2025-07-10T12:00:00Z"
                    }
                ]
            }
        } 