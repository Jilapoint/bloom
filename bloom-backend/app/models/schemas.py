"""API request/response models."""
from typing import Literal
from pydantic import BaseModel, Field


ModuleId = Literal["cycle", "conception", "menopause", "breast"]


class ChatRequest(BaseModel):
    module: ModuleId
    message: str = Field(..., min_length=1, max_length=4000)
    conversation_id: str | None = None


class Citation(BaseModel):
    title: str
    source: str  # e.g. "WHO Endometriosis Fact Sheet" or "Code du travail L.1225-16"
    url: str | None = None


class ChatResponse(BaseModel):
    conversation_id: str
    text: str
    citations: list[Citation] = []
    chips: list[str] = []  # suggested next-step actions
    routed_to: ModuleId | None = None  # if orchestrator handed off


class PolicyRequest(BaseModel):
    policy_type: Literal["menstrual_charter", "menopause_action_plan", "fertility_policy"]
    company_context: dict  # size, sector, country, existing agreements
    locale: str = "fr-FR"


class PolicyResponse(BaseModel):
    document: str  # markdown
    citations: list[Citation]


class HRInsight(BaseModel):
    metric_id: str
    value: float | str
    label: str
    threshold_met: bool  # k-anonymity threshold


class HRInsightsResponse(BaseModel):
    insights: list[HRInsight]
    k_threshold: int = 20
    period: str
