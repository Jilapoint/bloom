"""HR policy generation agent.

Runs in a SEPARATE Foundry project from the employee agents. Has access to
the legal and company KBs, plus a benchmark KB if available — but NOT to any
individual employee memory.
"""
from azure.identity import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from agent_framework import ChatAgent

from app.config import get_settings
from app.services.foundry_iq import legal_kb, company_kb, medical_kb


POLICY_INSTRUCTIONS = """You are Bloom's HR Policy Agent. You help HR teams
write fair, legally-sound, and medically-informed policies on women's health
at work.

For every policy you draft:
1. Identify the applicable laws from the legal knowledge base (cite article numbers).
2. Check the company's existing agreements in the company knowledge base.
3. Reference medical best practices (NICE, WHO, etc.) for any recommended accommodations.
4. Cross-reference all three knowledge bases — do not produce a generic template.
5. Output in clean markdown with a clear structure: Scope, Rights, Process, Resources, Sources.
6. Cite every claim inline. No claim without a citation.

You DO NOT have access to individual employee data. Suggestions are based on
anonymized organizational insights only.
"""


async def build_policy_agent() -> ChatAgent:
    settings = get_settings()
    client = AIProjectClient(
        endpoint=settings.azure_ai_project_endpoint,
        credential=DefaultAzureCredential(),
    )
    return ChatAgent(
        name="hr-policy",
        chat_client=client.inference.get_chat_completions_client(),
        model=settings.azure_openai_model,
        instructions=POLICY_INSTRUCTIONS,
        context_providers=[legal_kb(), company_kb(), medical_kb()],
    )
