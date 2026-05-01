from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
BACKEND_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(ROOT_ENV_FILE), str(BACKEND_ENV_FILE), ".env"),
        env_file_encoding="utf-8",
    extra="ignore",
    )

    app_name: str = "Meridian Electronics AI Assistant"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    mcp_server_url: str = "https://order-mcp-74afyau24q-uc.a.run.app/mcp"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    default_customer_email: str = "demo.customer1@example.com"

    allowed_origins: str = "http://localhost:3000"

settings = Settings()
