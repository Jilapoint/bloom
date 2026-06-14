"""Authentication via Microsoft Entra ID (formerly Azure AD).

Teams passes an SSO token; we validate it and extract the user identity.
For the hackathon, a stub user can be returned when AUTH_DISABLED=true.
"""
import os
from dataclasses import dataclass
from fastapi import Header, HTTPException


@dataclass
class CurrentUser:
    id: str
    email: str
    company_id: str
    role: str  # "employee" or "hr"


async def get_current_user(authorization: str | None = Header(default=None)) -> CurrentUser:
    if os.getenv("AUTH_DISABLED") == "true":
        return CurrentUser(
            id="demo-user-1",
            email="demo@bloom.local",
            company_id="demo-co",
            role="employee",
        )

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    # In production: validate the JWT against Entra ID's JWKS,
    # check audience and issuer, then map claims to CurrentUser.
    raise HTTPException(status_code=501, detail="Production auth not configured")
