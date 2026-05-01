import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.chat import router as chat_router
from app.routes.health import router as health_router
from app.services.chat_engine import ChatEngine
from app.services.llm_service import LLMService
from app.services.mcp_client import MCPClient, ToolCache
from app.services.testdata_contract import validate_testdata_contract

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    mcp_client = MCPClient(settings.mcp_server_url)
    tool_cache = ToolCache()
    llm_service = LLMService()

    try:
        credentials = validate_testdata_contract()
        logger.info("Demo credential contract validated: %d rows.", len(credentials))
    except FileNotFoundError:
        logger.warning("testdata.md not found; skipping local demo credential validation.")
    except ValueError as exc:
        logger.warning("testdata.md contract validation failed: %s", exc)

    try:
        await mcp_client.initialize()
        discovered_tools = await mcp_client.list_tools()
        await tool_cache.set_tools(discovered_tools)
        logger.info("MCP tool discovery succeeded: %d tools loaded.", len(discovered_tools))
    except Exception as exc:
        logger.warning("MCP tool discovery failed at startup: %s", exc)
        await tool_cache.set_tools([])

    app.state.chat_engine = ChatEngine(mcp_client, tool_cache, llm_service)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.allowed_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(chat_router)
