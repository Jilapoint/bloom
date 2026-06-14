"""Orchestrator agent — handoff pattern.

The orchestrator inspects the user's message + memory and either:
- Answers directly if the question spans multiple modules or is generic
- Hands off to one specialized module agent via the handoff pattern

In Agent Framework, handoff is expressed by letting an agent invoke other
agents as tools — the LLM decides when to delegate.
"""
from agent_framework import ChatAgent, HandoffBuilder
from azure.identity import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient

from app.config import get_settings
from app.agents.modules import (
    build_cycle_agent,
    build_conception_agent,
    build_menopause_agent,
    build_breast_agent,
    build_treatment_agent,
)


ORCHESTRATOR_INSTRUCTIONS = """You are Bloom's orchestrator. Your job is to
route each user message to the right specialized module agent, or to answer
directly if the question is generic or spans multiple modules.

Available modules:
- cycle: menstrual cycle, period pain, endometriosis, PCOS
- conception: fertility, IVF/ART, trying to conceive
- menopause: perimenopause, menopause, HRT, hot flashes, brain fog
- breast: breast self-exam, mammogram scheduling, family history risk
- treatment: intensive medical treatments (chemo, radiotherapy, post-surgical
  recovery, IVF stimulation cycles). Use this when the user mentions an
  ongoing or upcoming treatment that requires recovery time and impacts work.

ROUTING RULES:
- Match the user's explicit module choice when present in the request.
- For cross-module reasoning (e.g., "I'm 44 and my cycles are weird") — use
  the longitudinal memory to decide: long history of regular cycles + age 40+
  → likely perimenopause → hand off to menopause.
- If a user mentions chemo, radiotherapy, or any cyclical heavy treatment,
  hand off to the treatment module — even if the original question was about
  symptoms (treatment knows the protocols best).
- Never invent a routing — if unclear, ask one short clarifying question.

You have access to all module agents as tools. Call the one that fits.
"""


async def build_orchestrator() -> ChatAgent:
    settings = get_settings()
    client = AIProjectClient(
        endpoint=settings.azure_ai_project_endpoint,
        credential=DefaultAzureCredential(),
    )

    cycle = await build_cycle_agent()
    conception = await build_conception_agent()
    menopause = await build_menopause_agent()
    breast = await build_breast_agent()
    treatment = await build_treatment_agent()

    orchestrator = ChatAgent(
        name="orchestrator",
        chat_client=client.inference.get_chat_completions_client(),
        model=settings.azure_openai_model,
        instructions=ORCHESTRATOR_INSTRUCTIONS,
    )

    workflow = (
        HandoffBuilder()
        .set_coordinator(orchestrator)
        .add_handoff(orchestrator, [cycle, conception, menopause, breast, treatment])
        .build()
    )
    return workflow
