"""Calendar tools for the agent.

CRITICAL DESIGN PATTERN — two-step confirmation:
1. `propose_calendar_blocks` — read-only. Returns a plan with conflict detection.
   The agent shows this to the user as a suggestion.
2. `execute_calendar_blocks` — writes. Only called AFTER the user has explicitly
   confirmed ("yes, block these slots"). The agent must not skip step 1.

The system prompt instructs the agent to always propose first, never block
without explicit user consent.
"""
from datetime import datetime, timedelta, time
from typing import Annotated, Literal
from pydantic import Field

from app.services.calendar import (
    list_events_in_range,
    create_blocked_slot,
    list_bloom_events,
    delete_event,
)


# Title presets — neutral, indistinguishable, never reveal medical context
NEUTRAL_TITLES: dict[str, str] = {
    "default": "Unavailable",
    "recovery": "Personal",
    "appointment": "External meeting",
    "focus": "Focus time",
}


async def propose_calendar_blocks(
    user_id: Annotated[str, Field(description="User identifier from session")],
    treatment_date_iso: Annotated[
        str,
        Field(description="ISO date of the medical event (e.g. chemo session, IVF retrieval)"),
    ],
    recovery_days: Annotated[
        int,
        Field(description="How many days of reduced availability after the event"),
    ] = 2,
    block_style: Annotated[
        Literal["full_day", "afternoon", "morning"],
        Field(description="How to block: full day, afternoon only, or morning only"),
    ] = "full_day",
    title_preset: Annotated[
        Literal["default", "recovery", "appointment", "focus"],
        Field(description="Which neutral title to use"),
    ] = "default",
) -> dict:
    """Build a proposed calendar plan WITHOUT writing anything yet.

    Returns the slots that would be created and flags any conflicts with
    existing meetings, so the user can review before confirming.
    """
    treatment_date = datetime.fromisoformat(treatment_date_iso)
    slots: list[dict] = []

    for day_offset in range(recovery_days + 1):  # day of + recovery days
        day = treatment_date.date() + timedelta(days=day_offset)
        if block_style == "full_day":
            start = datetime.combine(day, time(9, 0))
            end = datetime.combine(day, time(18, 0))
        elif block_style == "afternoon":
            start = datetime.combine(day, time(13, 0))
            end = datetime.combine(day, time(18, 0))
        else:  # morning
            start = datetime.combine(day, time(9, 0))
            end = datetime.combine(day, time(13, 0))
        slots.append({"start": start.isoformat(), "end": end.isoformat()})

    # Detect conflicts with existing events in the same window
    range_start = datetime.fromisoformat(slots[0]["start"])
    range_end = datetime.fromisoformat(slots[-1]["end"])
    existing = await list_events_in_range(user_id, range_start, range_end)
    conflicts = [
        {"subject": e["subject"], "start": e["start"]["dateTime"]}
        for e in existing
        if e.get("showAs") in ("busy", "tentative", "oof")
    ]

    return {
        "proposed_slots": slots,
        "title_that_will_appear": NEUTRAL_TITLES[title_preset],
        "privacy_level": "private (only you see the details)",
        "conflicts": conflicts,
        "requires_confirmation": True,
        "confirmation_hint": "Ask the user 'Shall I block these slots?' before calling execute_calendar_blocks.",
    }


async def execute_calendar_blocks(
    user_id: Annotated[str, Field(description="User identifier from session")],
    slots: Annotated[
        list[dict],
        Field(description="The exact slots returned by propose_calendar_blocks"),
    ],
    title_preset: Annotated[
        Literal["default", "recovery", "appointment", "focus"],
        Field(description="Must match the preset used in the proposal"),
    ] = "default",
) -> dict:
    """Write the previously-proposed blocks to the user's calendar.

    DO NOT call this without the user's explicit confirmation.
    The agent must have shown the proposal to the user and received
    an affirmative answer like "yes", "go ahead", "block them".
    """
    title = NEUTRAL_TITLES[title_preset]
    created: list[str] = []
    for slot in slots:
        event = await create_blocked_slot(
            user_id=user_id,
            start=datetime.fromisoformat(slot["start"]),
            end=datetime.fromisoformat(slot["end"]),
            title=title,
            body="",  # never store medical reason in the calendar entry
        )
        created.append(event["id"])
    return {
        "status": "blocked",
        "events_created": len(created),
        "event_ids": created,
        "note": (
            "Blocks added to your calendar with neutral title and private "
            "sensitivity. You can view or remove them anytime in Bloom."
        ),
    }


async def list_user_bloom_blocks(
    user_id: Annotated[str, Field(description="User identifier from session")],
) -> list[dict]:
    """List all blocks Bloom has previously created — for the user to review."""
    return await list_bloom_events(user_id)


async def remove_bloom_block(
    user_id: Annotated[str, Field(description="User identifier from session")],
    event_id: Annotated[str, Field(description="Calendar event id from list_user_bloom_blocks")],
) -> dict:
    """Remove a previously-blocked slot at the user's request."""
    await delete_event(user_id, event_id)
    return {"status": "removed", "event_id": event_id}
