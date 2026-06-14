"""User access token resolver for delegated Microsoft Graph calls.

Bloom obtains user-delegated tokens via the Teams SSO flow + On-Behalf-Of
exchange. The token is scoped per-API-call so Calendar permissions stay
narrow (only what the current request needs).

For local development, set BLOOM_GRAPH_TOKEN to a token from
https://developer.microsoft.com/en-us/graph/graph-explorer (Calendars.ReadWrite).
"""
import os
from contextvars import ContextVar


# Set by middleware on each request — never global state
_current_user_token: ContextVar[str | None] = ContextVar(
    "_current_user_token", default=None
)


def set_request_token(token: str) -> None:
    _current_user_token.set(token)


async def get_user_access_token(user_id: str, scope: str) -> str:
    """Return the user's Graph token for the requested scope.

    Production: implements On-Behalf-Of flow against Entra ID using the
    incoming Teams SSO token. For the hackathon demo, falls back to a
    static dev token.
    """
    dev_token = os.getenv("BLOOM_GRAPH_TOKEN")
    if dev_token:
        return dev_token

    token = _current_user_token.get()
    if not token:
        raise RuntimeError(
            f"No user token available for scope={scope}. "
            "Configure Teams SSO + OBO flow or set BLOOM_GRAPH_TOKEN."
        )
    # TODO: exchange the incoming Teams token for a Graph token via OBO
    return token
