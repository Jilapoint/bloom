"""HR-side endpoints. Returns ONLY k-anonymized aggregates.

Uses a SEPARATE Foundry project (different agent instance, different KB
permissions) — this is the confidentiality wall enforced at the service layer.
"""
from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import (
    PolicyRequest,
    PolicyResponse,
    HRInsightsResponse,
    HRInsight,
    Citation,
)
from app.routers.auth import get_current_user
from app.services.memory import HRAggregateStore
from app.agents.policy import build_policy_agent

router = APIRouter(prefix="/api/v1/hr", tags=["hr"])


def _require_hr(user) -> None:
    if user.role != "hr":
        raise HTTPException(status_code=403, detail="HR role required")


@router.get("/insights", response_model=HRInsightsResponse)
async def insights(period: str = "last_6_months", user=Depends(get_current_user)):
    _require_hr(user)
    store = HRAggregateStore()
    raw = await store.fetch_insights(company_id=user.company_id, period=period)
    return HRInsightsResponse(
        insights=[
            HRInsight(
                metric_id=r["metricId"],
                value=r["value"],
                label=r["label"],
                threshold_met=True,
            )
            for r in raw
        ],
        k_threshold=HRAggregateStore.K_THRESHOLD,
        period=period,
    )


@router.post("/policy", response_model=PolicyResponse)
async def generate_policy(req: PolicyRequest, user=Depends(get_current_user)):
    """Generate a tailored HR policy grounded in legal + medical + company KBs."""
    _require_hr(user)
    agent = await build_policy_agent()
    prompt = (
        f"Generate a {req.policy_type} for a company with this context: "
        f"{req.company_context}. Jurisdiction: {req.locale}. Output in markdown. "
        f"Cite every legal article and medical guideline used."
    )
    result = await agent.run(message=prompt)
    return PolicyResponse(
        document=result.text,
        citations=[
            Citation(title=c.title, source=c.source, url=c.url)
            for c in (result.citations or [])
        ],
    )
