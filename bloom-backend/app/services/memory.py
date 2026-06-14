"""Longitudinal memory backed by Cosmos DB.

The employee memory and HR aggregates are stored in SEPARATE containers
with SEPARATE access policies — this is the confidentiality wall enforced
at the data layer.
"""
from datetime import datetime, timezone
from azure.cosmos.aio import CosmosClient
from azure.identity import DefaultAzureCredential

from app.config import get_settings


class MemoryStore:
    """Append-only conversation + symptom log, encrypted at rest, per-user partitioned."""

    def __init__(self):
        settings = get_settings()
        self._client = CosmosClient(
            url=settings.cosmos_endpoint,
            credential=DefaultAzureCredential(),
        )
        self._db = self._client.get_database_client(settings.cosmos_database)
        self._employee = self._db.get_container_client(settings.cosmos_container_employee)

    async def append(self, user_id: str, module: str, payload: dict) -> None:
        """Save one turn / event to the employee's private memory."""
        doc = {
            "id": f"{user_id}:{datetime.now(timezone.utc).isoformat()}",
            "userId": user_id,  # partition key
            "module": module,
            "payload": payload,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await self._employee.create_item(doc)

    async def fetch_recent(self, user_id: str, limit: int = 50) -> list[dict]:
        """Read recent context for the orchestrator to reason over."""
        query = (
            "SELECT TOP @limit * FROM c WHERE c.userId = @uid "
            "ORDER BY c.timestamp DESC"
        )
        params = [{"name": "@uid", "value": user_id}, {"name": "@limit", "value": limit}]
        items = []
        async for item in self._employee.query_items(query=query, parameters=params):
            items.append(item)
        return items


class HRAggregateStore:
    """Anonymized, k-anonymized aggregates — the ONLY data crossing the wall."""

    K_THRESHOLD = 20

    def __init__(self):
        settings = get_settings()
        self._client = CosmosClient(
            url=settings.cosmos_endpoint,
            credential=DefaultAzureCredential(),
        )
        self._db = self._client.get_database_client(settings.cosmos_database)
        self._hr = self._db.get_container_client(settings.cosmos_container_hr)

    async def fetch_insights(self, company_id: str, period: str) -> list[dict]:
        """Return only metrics that meet the k-anonymity threshold."""
        query = (
            "SELECT * FROM c WHERE c.companyId = @cid AND c.period = @p "
            "AND c.contributorCount >= @k"
        )
        params = [
            {"name": "@cid", "value": company_id},
            {"name": "@p", "value": period},
            {"name": "@k", "value": self.K_THRESHOLD},
        ]
        items = []
        async for item in self._hr.query_items(query=query, parameters=params):
            items.append(item)
        return items
