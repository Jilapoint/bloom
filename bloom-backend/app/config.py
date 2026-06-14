"""Configuration loaded from environment variables and Azure Key Vault."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Azure / Foundry
    azure_ai_project_endpoint: str  # https://<project>.services.ai.azure.com/api/projects/<name>
    azure_openai_model: str = "gpt-4o"
    azure_subscription_id: str
    azure_tenant_id: str

    # Foundry IQ — knowledge bases
    foundry_iq_search_endpoint: str  # https://<service>.search.windows.net
    kb_medical_name: str = "bloom-kb-medical"
    kb_legal_fr_name: str = "bloom-kb-legal-fr"
    kb_company_name: str = "bloom-kb-company"

    # Data layer
    cosmos_endpoint: str  # https://<account>.documents.azure.com:443/
    cosmos_database: str = "bloom"
    cosmos_container_employee: str = "employee-memory"
    cosmos_container_hr: str = "hr-aggregates"

    # Observability
    applicationinsights_connection_string: str | None = None

    # App
    environment: str = "development"
    cors_origins: str = "http://localhost:5173,https://teams.microsoft.com"


@lru_cache
def get_settings() -> Settings:
    return Settings()
