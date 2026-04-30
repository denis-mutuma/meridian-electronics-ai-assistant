"""
main.py — FastAPI application entry point.

Startup sequence (lifespan):
  1. Connect to the MCP tool server and discover available tools.
  2. Cache the tool list so every request reuses it without re-fetching.
  3. Wire together the ChatEngine and attach it to app.state.

If MCP discovery fails (e.g. network issue at boot), the service still
starts and will answer with an LLM-only response (no tool calls).
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.auth import router as auth_router
from app.routes.chat import router as chat_router
from app.routes.health import router as health_router
from app.services.chat_engine import ChatEngine
from app.services.llm_service import LLMService
from app.services.mcp_client import MCPClient, ToolCache

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan: initialise shared services before first request."""
    mcp_client = MCPClient(settings.mcp_server_url)
    tool_cache = ToolCache()
    llm_service = LLMService()

    try:
        # Perform MCP handshake and populate the tool cache.
        await mcp_client.initialize()
        discovered_tools = await mcp_client.list_tools()
        await tool_cache.set_tools(discovered_tools)
        logger.info("MCP tool discovery succeeded: %d tools loaded.", len(discovered_tools))
    except Exception as exc:
        # Non-fatal — the API will still work; tool calls will be skipped.
        logger.warning("MCP tool discovery failed at startup: %s", exc)
        await tool_cache.set_tools([])

    # Attach the chat engine to app.state so route handlers can access it.
    app.state.chat_engine = ChatEngine(mcp_client, tool_cache, llm_service)
    yield  # Application runs here.


app = FastAPI(title=settings.app_name, lifespan=lifespan)

# Allow cross-origin requests from the configured frontend origin(s).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.allowed_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route groups.
app.include_router(health_router)   # GET /health
app.include_router(auth_router)     # POST /auth/login
app.include_router(chat_router)     # POST /chat
