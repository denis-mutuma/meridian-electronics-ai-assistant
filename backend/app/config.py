from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Support .env in both the repo root and the backend/ directory so the app
# works whether launched from the repo root or from within backend/.
ROOT_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
BACKEND_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(ROOT_ENV_FILE), str(BACKEND_ENV_FILE), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",  # ignore any extra env vars not declared here
    )

    app_name: str = "Meridian Electronics AI Assistant"

    # MCP server that holds all customer/order data
    mcp_server_url: str = "https://order-mcp-74afyau24q-uc.a.run.app/mcp"

    # In production, OPENAI_API_KEY is injected into Lambda by Terraform.
    # Locally, set it in .env.
    openai_api_key: str = ""
    openai_model: str = "gpt-5.4-nano"

    # Comma-separated list of allowed CORS origins.
    # Hosted CloudFront calls use same-origin /api requests; this mostly
    # supports local development or direct API Gateway browser access.
    allowed_origins: str = "http://localhost:3000"


settings = Settings()
