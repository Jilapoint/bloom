"""Foundry IQ integration via Azure AI Search Context Provider.

Each knowledge base is one knowledge_base_name in the same Azure AI Search service.
Foundry IQ handles indexing, agentic retrieval, query planning, and citation.
"""
from azure.identity import DefaultAzureCredential
from agent_framework_azure_ai import AzureAISearchContextProvider

from app.config import get_settings


def make_kb_provider(knowledge_base_name: str) -> AzureAISearchContextProvider:
    """Create a Foundry IQ context provider for one knowledge base.

    The agent will call this provider on every turn to retrieve grounded
    context with citations. Agentic mode lets Foundry IQ plan multi-hop
    queries (e.g., medical + legal cross-reference).
    """
    settings = get_settings()
    return AzureAISearchContextProvider(
        endpoint=settings.foundry_iq_search_endpoint,
        knowledge_base_name=knowledge_base_name,
        credential=DefaultAzureCredential(),
        mode="agentic",  # vs "fast" for single-source lookup
        include_citations=True,
    )


# Pre-built providers shared across agents
def medical_kb():
    return make_kb_provider(get_settings().kb_medical_name)


def legal_kb():
    return make_kb_provider(get_settings().kb_legal_fr_name)


def company_kb():
    return make_kb_provider(get_settings().kb_company_name)
