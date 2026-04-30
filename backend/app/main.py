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


@asynccontextmanager
async def lifespan(app: FastAPI):
    mcp_client = MCPClient(settings.mcp_server_url)
    tool_cache = ToolCache()
    llm_service = LLMService()

    try:
        await mcp_client.initialize()
        discovered_tools = await mcp_client.list_tools()
        await tool_cache.set_tools(discovered_tools)
    except Exception:
        # Keep service up even if MCP discovery fails at startup.
        await tool_cache.set_tools([])

    app.state.chat_engine = ChatEngine(mcp_client, tool_cache, llm_service)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.allowed_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(chat_router)
