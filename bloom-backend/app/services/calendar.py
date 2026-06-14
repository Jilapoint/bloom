"""Calendar integration via Microsoft Graph.

Important: every call here runs under the USER's delegated permissions
(scope: Calendars.ReadWrite). Bloom never accesses calendars under a
service identity — this means the employer cannot claim Bloom has any
visibility into employees' calendars. Each event is created by the
user themselves, with the user's own credentials.

Privacy guarantees enforced at this layer:
- Event titles are neutral by default ("Unavailable") — never anything
  that reveals a medical reason.
- sensitivity="private" — coworkers see "busy" but never event details.
- showAs="busy" — does not differentiate from any other busy slot.
"""
from datetime import datetime, timedelta
from typing import Annotated, Literal
import httpx
from pydantic import Field

from app.services.auth_context import get_user_access_token


GRAPH_BASE = "https://graph.microsoft.com/v1.0"


async def list_events_in_range(
    user_id: str,
    start: datetime,
    end: datetime,
) -> list[dict]:
    """Read the user's events in a date range — used to detect conflicts.

    Only metadata is read (subject, start, end, isAllDay). The agent never
    sees other people's events, only the current user's own calendar.
    """
    token = await get_user_access_token(user_id, scope="Calendars.Read")
    params = {
        "startDateTime": start.isoformat(),
        "endDateTime": end.isoformat(),
        "$select": "id,subject,start,end,isAllDay,sensitivity,showAs",
        "$orderby": "start/dateTime",
        "$top": "50",
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            f"{GRAPH_BASE}/me/calendarView",
            params=params,
            headers={"Authorization": f"Bearer {token}"},
        )
        r.raise_for_status()
        return r.json().get("value", [])


async def create_blocked_slot(
    user_id: str,
    start: datetime,
    end: datetime,
    title: str = "Unavailable",
    body: str = "",
) -> dict:
    """Create a private, neutral-titled busy block on the user's calendar.

    All Bloom-created events are tagged with a hidden category so the user
    can later list and delete them. The category does NOT appear in shared
    views — only the user sees it.
    """
    token = await get_user_access_token(user_id, scope="Calendars.ReadWrite")
    event = {
        "subject": title,
        "body": {"contentType": "text", "content": body},
        "start": {"dateTime": start.isoformat(), "timeZone": "Europe/Paris"},
        "end": {"dateTime": end.isoformat(), "timeZone": "Europe/Paris"},
        "sensitivity": "private",
        "showAs": "busy",
        "isReminderOn": True,
        "reminderMinutesBeforeStart": 60,
        "categories": ["Bloom"],  # private tag, user-only visibility
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(
            f"{GRAPH_BASE}/me/events",
            json=event,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )
        r.raise_for_status()
        return r.json()


async def list_bloom_events(user_id: str) -> list[dict]:
    """List events Bloom has created for the user — for review/deletion."""
    token = await get_user_access_token(user_id, scope="Calendars.Read")
    params = {
        "$filter": "categories/any(c:c eq 'Bloom')",
        "$select": "id,subject,start,end",
        "$orderby": "start/dateTime",
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            f"{GRAPH_BASE}/me/events",
            params=params,
            headers={"Authorization": f"Bearer {token}"},
        )
        r.raise_for_status()
        return r.json().get("value", [])


async def delete_event(user_id: str, event_id: str) -> None:
    token = await get_user_access_token(user_id, scope="Calendars.ReadWrite")
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.delete(
            f"{GRAPH_BASE}/me/events/{event_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        r.raise_for_status()
