"""Tools exposed to agents as AIFunctions.

Agent Framework auto-discovers Python-annotated functions and turns them
into tool calls. Each tool is one capability the LLM can decide to use.
"""
from datetime import datetime, timedelta
from typing import Annotated
from pydantic import Field


def draft_neutral_absence_email(
    recipient: Annotated[str, Field(description="Manager name or email")],
    date: Annotated[str, Field(description="ISO date of the absence, e.g. 2026-06-20")],
    duration_hours: Annotated[int, Field(description="How long the absence lasts")] = 4,
) -> str:
    """Draft an absence email that mentions a medical appointment without revealing its nature."""
    return (
        f"Subject: Medical appointment on {date}\n\n"
        f"Hi {recipient},\n\n"
        f"I have a scheduled medical appointment on {date} that will require "
        f"me to be absent for approximately {duration_hours} hours. I'll ensure "
        f"my deliverables are covered and remain reachable for urgent matters.\n\n"
        f"Thank you for your understanding."
    )


def schedule_reminder(
    title: Annotated[str, Field(description="Short reminder title")],
    when_iso: Annotated[str, Field(description="ISO datetime of the reminder")],
) -> dict:
    """Schedule a reminder in the user's personal Bloom calendar (not employer-visible)."""
    return {"status": "scheduled", "title": title, "when": when_iso}


def find_specialist(
    specialty: Annotated[str, Field(description="e.g. gynecologist, endometriosis specialist")],
    postal_code: Annotated[str, Field(description="User's postal code")],
    max_distance_km: Annotated[int, Field(description="Search radius")] = 20,
) -> list[dict]:
    """Find healthcare specialists near the user. Calls the per-country directory."""
    return [
        {
            "name": "Dr. Example",
            "specialty": specialty,
            "distance_km": 3,
            "next_available": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "phone": "+33 1 23 45 67 89",
        }
    ]


def calculate_screening_due_date(
    age: Annotated[int, Field(description="User age")],
    family_history_breast_cancer: Annotated[bool, Field(description="First-degree relative")] = False,
    country: Annotated[str, Field(description="ISO country code")] = "FR",
) -> dict:
    """Calculate when the next mammogram is due based on age, risk, and country guidelines."""
    base_age = 40 if family_history_breast_cancer else 50
    next_screening = (
        datetime.utcnow() + timedelta(days=365 * 2)
        if age >= base_age
        else datetime.utcnow().replace(year=datetime.utcnow().year + (base_age - age))
    )
    return {
        "next_screening_date": next_screening.date().isoformat(),
        "rationale": f"Based on {country} guidelines and your risk profile.",
        "country_guideline": "HAS" if country == "FR" else "USPSTF",
    }
