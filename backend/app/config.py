"""
config.py — Application settings loaded from environment variables.

Priority order (highest first):
  1. Real process environment (e.g. AWS ECS runtime env)
  2. <repo_root>/.env         — primary local dev file (gitignored)
  3. <backend_dir>/.env       — optional backend-scoped overrides
  4. .env in the working directory (fallback)

All settings have safe defaults so the app starts without any .env file.
Only OPENAI_API_KEY is required for live AI responses.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env paths relative to this file so they work regardless of
# which directory uvicorn / pytest is invoked from.
ROOT_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
BACKEND_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Pydantic-settings merges all listed files; later entries take precedence.
        env_file=(str(ROOT_ENV_FILE), str(BACKEND_ENV_FILE), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",  # Silently ignore unknown env vars.
    )

    # ── App identity ─────────────────────────────────────────────────────────
    app_name: str = "Meridian Electronics AI Assistant"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # ── MCP tool server ──────────────────────────────────────────────────────
    # Streamable HTTP endpoint exposing order/product tools via JSON-RPC 2.0.
    mcp_server_url: str = "https://order-mcp-74afyau24q-uc.a.run.app/mcp"

    # ── OpenAI ───────────────────────────────────────────────────────────────
    # Leave empty locally to get placeholder responses without consuming API quota.
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # ── Chat context ─────────────────────────────────────────────────────────
    # Injected into the LLM/MCP context as the customer email (no login flow).
    default_customer_email: str = "demo.customer1@example.com"

    # ── CORS ─────────────────────────────────────────────────────────────────
    # Comma-separated list of allowed origins for the CORS middleware.
    allowed_origins: str = "http://localhost:3000"


# Module-level singleton — import this everywhere instead of re-instantiating.
settings = Settings()
