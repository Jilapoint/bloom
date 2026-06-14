"""Employee-side chat endpoint."""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import ChatRequest, ChatResponse, Citation
from app.agents.orchestrator import build_orchestrator
from app.services.memory import MemoryStore
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/v1", tags=["employee"])


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, user=Depends(get_current_user)) -> ChatResponse:
    """Single conversational turn.

    Flow:
    1. Append the user's message to longitudinal memory.
    2. Pass message + module hint + recent memory to the orchestrator.
    3. Orchestrator routes to a module agent (handoff pattern).
    4. Module agent queries Foundry IQ knowledge bases, calls tools, returns text + citations.
    5. Append the response to memory.
    6. Return to client.
    """
    memory = MemoryStore()
    conv_id = req.conversation_id or str(uuid.uuid4())

    await memory.append(
        user_id=user.id,
        module=req.module,
        payload={"role": "user", "text": req.message, "conversation_id": conv_id},
    )

    recent = await memory.fetch_recent(user.id, limit=20)

    workflow = await build_orchestrator()
    result = await workflow.run(
        message=req.message,
        context={"module_hint": req.module, "memory": recent, "user_locale": "fr-FR"},
    )

    citations = [
        Citation(title=c.title, source=c.source, url=c.url)
        for c in (result.citations or [])
    ]

    response = ChatResponse(
        conversation_id=conv_id,
        text=result.text,
        citations=citations,
        chips=result.suggestions or [],
        routed_to=result.routed_agent,
    )

    await memory.append(
        user_id=user.id,
        module=req.module,
        payload={"role": "assistant", "response": response.model_dump()},
    )

    return response
