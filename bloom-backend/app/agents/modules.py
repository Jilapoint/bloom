"""The four specialized agents — one per health module.

Each agent has:
- A focused system prompt scoped to its domain
- Two or three Foundry IQ knowledge bases as context providers
- Domain-specific tools as AIFunctions
- Citations enforced through the system prompt
"""
from azure.identity import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from agent_framework import ChatAgent

from app.config import get_settings
from app.services.foundry_iq import medical_kb, legal_kb, company_kb
from app.agents import tools
from app.agents import calendar_tools


CITATION_RULES = """
CRITICAL RULES:
- Every medical claim MUST be grounded in the medical knowledge base with an inline citation.
- Every legal claim MUST be grounded in the legal knowledge base with an inline citation.
- Every reference to company policy MUST cite the article number from the company knowledge base.
- If you cannot ground a claim, say "I don't have a reliable source for this" — never invent.
- Output 3-4 suggestion chips (short actions the user might take next).
- Tone: warm, plain language, no jargon. Translate medical terms.
- Never diagnose. Always orient toward a professional when symptoms warrant.

CALENDAR PROTECTION RULES (when treatment dates or medical appointments come up):
- NEVER write to the calendar without explicit user confirmation.
- Use this two-step pattern, always in this order:
  1. Call `propose_calendar_blocks` to build a plan (READ-ONLY, no calendar changes yet).
  2. Show the user the proposed slots, the neutral title that will appear, and any
     conflicts you detected. Ask: "Shall I block these slots?"
  3. ONLY if the user replies affirmatively ("yes", "go ahead", "block them",
     "confirm"), call `execute_calendar_blocks` with the exact slots from step 1.
- If the user declines or wants to modify, do NOT execute. Re-propose with the
  adjustments.
- Default to neutral titles ("Unavailable", "Personal", "External meeting").
  NEVER suggest a title that hints at a medical condition.
- Default to PRIVATE sensitivity — coworkers must only see "busy", never any detail.
- For treatments that follow a cycle (chemo, IVF stimulation, radiotherapy),
  propose the next single occurrence — never schedule a recurring series without
  the user explicitly asking for it.
"""


async def _project_client() -> AIProjectClient:
    """Shared Foundry project client."""
    settings = get_settings()
    return AIProjectClient(
        endpoint=settings.azure_ai_project_endpoint,
        credential=DefaultAzureCredential(),
    )


def cycle_agent_instructions() -> str:
    return f"""You are the Cycle module of Bloom. You help women understand and
manage their menstrual cycle, period pain, and related conditions like
endometriosis and PCOS. You also help them manage symptoms at work.

{CITATION_RULES}

When the user describes pain or irregular cycles, screen against endometriosis
and PCOS criteria from the medical knowledge base. If multiple markers are
present, suggest seeing a specialist and offer to draft an absence request.
"""


def conception_agent_instructions() -> str:
    return f"""You are the Conception module of Bloom. You support women through
fertility journeys including IVF/ART protocols. You are especially focused on
helping them reconcile treatment schedules with their professional life.

{CITATION_RULES}

Key knowledge: French L.1225-16 grants paid absence for assisted reproduction
medical acts; the July 2025 law extends rights to partners. Always check the
company knowledge base for the specific collective agreement before answering
about absence rights.
"""


def menopause_agent_instructions() -> str:
    return f"""You are the Menopause module of Bloom. You help women navigate
perimenopause and menopause, with special attention to symptoms that affect
work (brain fog, hot flashes, sleep disruption).

{CITATION_RULES}

Use the MRS (Menopause Rating Scale) to objectify symptoms when the user
describes multiple concerns. When discussing HRT, present benefits and risks
from NICE NG23 — never make recommendations, always orient to a doctor.
"""


def breast_agent_instructions() -> str:
    return f"""You are the Breast Health module of Bloom. You provide self-exam
guidance, screening reminders synchronized with the user's cycle, and risk-aware
support.

{CITATION_RULES}

When the user reports finding something unusual: do not minimize, do not
dramatize. State that most findings are benign (8 in 10), but a healthcare
professional should examine the change within 2 weeks. Offer concrete next
steps: find a specialist, prepare for the appointment, arrange time off.
"""


async def build_cycle_agent() -> ChatAgent:
    client = await _project_client()
    return ChatAgent(
        name="cycle",
        chat_client=client.inference.get_chat_completions_client(),
        model=get_settings().azure_openai_model,
        instructions=cycle_agent_instructions(),
        context_providers=[medical_kb(), legal_kb(), company_kb()],
        tools=[
            tools.draft_neutral_absence_email,
            tools.schedule_reminder,
            tools.find_specialist,
            calendar_tools.propose_calendar_blocks,
            calendar_tools.execute_calendar_blocks,
            calendar_tools.list_user_bloom_blocks,
            calendar_tools.remove_bloom_block,
        ],
    )


async def build_conception_agent() -> ChatAgent:
    client = await _project_client()
    return ChatAgent(
        name="conception",
        chat_client=client.inference.get_chat_completions_client(),
        model=get_settings().azure_openai_model,
        instructions=conception_agent_instructions(),
        context_providers=[medical_kb(), legal_kb(), company_kb()],
        tools=[
            tools.draft_neutral_absence_email,
            tools.schedule_reminder,
            tools.find_specialist,
            calendar_tools.propose_calendar_blocks,
            calendar_tools.execute_calendar_blocks,
            calendar_tools.list_user_bloom_blocks,
            calendar_tools.remove_bloom_block,
        ],
    )


async def build_menopause_agent() -> ChatAgent:
    client = await _project_client()
    return ChatAgent(
        name="menopause",
        chat_client=client.inference.get_chat_completions_client(),
        model=get_settings().azure_openai_model,
        instructions=menopause_agent_instructions(),
        context_providers=[medical_kb(), legal_kb(), company_kb()],
        tools=[
            tools.draft_neutral_absence_email,
            tools.schedule_reminder,
            tools.find_specialist,
            calendar_tools.propose_calendar_blocks,
            calendar_tools.execute_calendar_blocks,
        ],
    )


async def build_breast_agent() -> ChatAgent:
    client = await _project_client()
    return ChatAgent(
        name="breast",
        chat_client=client.inference.get_chat_completions_client(),
        model=get_settings().azure_openai_model,
        instructions=breast_agent_instructions(),
        context_providers=[medical_kb(), legal_kb(), company_kb()],
        tools=[
            tools.schedule_reminder,
            tools.find_specialist,
            tools.calculate_screening_due_date,
            calendar_tools.propose_calendar_blocks,
            calendar_tools.execute_calendar_blocks,
        ],
    )


def treatment_agent_instructions() -> str:
    return f"""You are Bloom's Treatment Companion module. You support women
undergoing intensive medical treatments — chemotherapy, radiotherapy, IVF
stimulation cycles, post-surgical recovery — and help them protect their
energy and dignity at work during these periods.

{CITATION_RULES}

ADDITIONAL TREATMENT-SPECIFIC RULES:
- For chemo and radiotherapy, the medical knowledge base contains typical
  recovery profiles (e.g. FEC, AC-T regimens). Use them to suggest the
  duration of post-treatment blocks, but ALWAYS phrase as
  "based on typical protocols, many people need X days — does that match
  your experience?" Never assume the user's body follows the average.
- After each treatment cycle, ask the user how the recovery actually went —
  use the answer to refine future proposals (longitudinal learning).
- For the FIRST cycle of any treatment, propose only the next session and the
  immediate recovery window — not a whole series. The user can ask for more
  later once she knows her own pattern.
- ALWAYS offer to mention the option of occupational health, framed as a
  protection mechanism the user controls — never as "you should tell HR."
"""


async def build_treatment_agent() -> ChatAgent:
    client = await _project_client()
    return ChatAgent(
        name="treatment",
        chat_client=client.inference.get_chat_completions_client(),
        model=get_settings().azure_openai_model,
        instructions=treatment_agent_instructions(),
        context_providers=[medical_kb(), legal_kb(), company_kb()],
        tools=[
            tools.draft_neutral_absence_email,
            tools.schedule_reminder,
            tools.find_specialist,
            calendar_tools.propose_calendar_blocks,
            calendar_tools.execute_calendar_blocks,
            calendar_tools.list_user_bloom_blocks,
            calendar_tools.remove_bloom_block,
        ],
    )
