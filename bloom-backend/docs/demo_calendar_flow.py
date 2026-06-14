"""Demo script — the calendar two-step flow.

Shows the exact conversation a user has with Bloom when scheduling
post-treatment recovery blocks. This is the script for the demo video.

Run: python docs/demo_calendar_flow.py
"""
import asyncio
import json
from datetime import datetime, timedelta


# ───── Turn 1: User mentions an upcoming treatment ────────────────────────

USER_TURN_1 = (
    "I have my next chemo session next Tuesday at 9am. Last time I needed about "
    "2 days to recover before I could focus again."
)

# Bloom's expected behavior:
# 1. Recognize this is a treatment-related message → orchestrator routes to "treatment"
# 2. Treatment agent calls `propose_calendar_blocks` (READ-ONLY)
# 3. Agent shows the user the plan + asks for confirmation

BLOOM_TURN_1_EXPECTED = """
Thank you for letting me know — I want to make sure that recovery time is
protected for you.

Based on what you said, I'd suggest blocking these slots on your calendar:

  Tuesday Jun 23, 9:00–18:00   (treatment day)
  Wednesday Jun 24, 9:00–18:00 (recovery day 1)
  Thursday Jun 25, 9:00–18:00  (recovery day 2)

Each one would appear as **"Unavailable"** with **private** sensitivity — your
colleagues will see you're busy, but never the reason. Only you can see the
details.

I noticed one conflict: you have a 1:1 with Marc on Wednesday at 10am.
I can help you reschedule it after you confirm.

**Shall I block these slots?**
"""

# Tool call expected from the agent at this turn:
PROPOSE_CALL = {
    "tool": "propose_calendar_blocks",
    "args": {
        "user_id": "demo-user-1",
        "treatment_date_iso": "2026-06-23T09:00:00",
        "recovery_days": 2,
        "block_style": "full_day",
        "title_preset": "default",
    },
}


# ───── Turn 2: User confirms ──────────────────────────────────────────────

USER_TURN_2 = "Yes, go ahead. And please draft a quick neutral message for Marc."

# Bloom's expected behavior:
# 1. Recognize affirmative confirmation
# 2. Call `execute_calendar_blocks` with the EXACT slots from the proposal
# 3. Call `draft_neutral_absence_email` for Marc's reschedule
# 4. Confirm both actions are done

BLOOM_TURN_2_EXPECTED = """
Done. I've added the three blocks to your calendar with the neutral title and
private sensitivity. Here's a quick message you can send Marc — feel free to
edit before sending:

  Subject: 1:1 reschedule
  Hi Marc, I have a medical appointment that morning, would Friday at the
  same time work for our 1:1? Sorry for the short notice. — [you]

After your session on Tuesday, I'll check in to ask how the recovery actually
went — that helps me get better at suggesting the right amount of time for
the next cycle.

One last thing, and this is entirely up to you: occupational health can put
formal accommodations in place for the duration of your treatment, without
your manager ever knowing the reason. Would you like to learn more about
how that works?
"""

# Tool calls expected from the agent at this turn:
EXECUTE_CALLS = [
    {
        "tool": "execute_calendar_blocks",
        "args": {
            "user_id": "demo-user-1",
            "slots": [
                {"start": "2026-06-23T09:00:00", "end": "2026-06-23T18:00:00"},
                {"start": "2026-06-24T09:00:00", "end": "2026-06-24T18:00:00"},
                {"start": "2026-06-25T09:00:00", "end": "2026-06-25T18:00:00"},
            ],
            "title_preset": "default",
        },
    },
    {
        "tool": "draft_neutral_absence_email",
        "args": {"recipient": "Marc", "date": "2026-06-24", "duration_hours": 1},
    },
]


def print_flow():
    print("=" * 70)
    print("BLOOM — CALENDAR PROTECTION FLOW")
    print("=" * 70)
    print()
    print(">>> TURN 1 — User")
    print(USER_TURN_1)
    print()
    print("    [internal] orchestrator routes → treatment module")
    print("    [internal] tool call: propose_calendar_blocks (READ-ONLY)")
    print(f"    {json.dumps(PROPOSE_CALL['args'], indent=6)}")
    print()
    print(">>> TURN 1 — Bloom")
    print(BLOOM_TURN_1_EXPECTED)
    print()
    print("-" * 70)
    print()
    print(">>> TURN 2 — User")
    print(USER_TURN_2)
    print()
    print("    [internal] confirmation detected — execute now allowed")
    print("    [internal] tool calls:")
    for c in EXECUTE_CALLS:
        print(f"       - {c['tool']}")
    print()
    print(">>> TURN 2 — Bloom")
    print(BLOOM_TURN_2_EXPECTED)
    print()


if __name__ == "__main__":
    print_flow()
