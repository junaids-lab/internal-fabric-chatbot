from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "local"
    allowed_origins_raw: str = Field(default="http://localhost:3000,http://localhost:5173", alias="ALLOWED_ORIGINS")

    azure_search_endpoint: str = ""
    azure_search_api_key: str = ""
    azure_search_index_name: str = "rdcci-internal-chatbot-kb"
    azure_search_knowledge_base_name: str = "rdcci-internal-fabric-kb"
    azure_search_api_version: str = "2025-11-01-preview"

    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_api_version: str = "2024-10-21"
    azure_openai_embedding_deployment: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    azure_ai_foundry_project_endpoint: str = ""
    azure_ai_foundry_agent_name: str = ""
    azure_ai_foundry_model_deployment: str = "gpt-4.1-mini"
    azure_ai_foundry_api_key: str = ""
    azure_ai_foundry_use_agent: bool = False

    entra_tenant_id: str = ""
    entra_frontend_client_id: str = ""
    powerbi_delegated_scopes_raw: str = Field(
        default="https://analysis.windows.net/powerbi/api/Dataset.Read.All",
        alias="POWERBI_DELEGATED_SCOPES",
    )

    fabric_workspace_id: str = ""
    subscription_semantic_model_id: str = ""
    manual_stamp_semantic_model_id: str = ""
    electronic_stamp_semantic_model_id: str = ""
    permit_semantic_model_id: str = ""

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins_raw.split(",") if origin.strip()]

    @property
    def powerbi_delegated_scopes(self) -> list[str]:
        return [scope.strip() for scope in self.powerbi_delegated_scopes_raw.split(",") if scope.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
