from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.chat import router as chat_router
from app.routes.health import router as health_router
from app.services.chat_engine import ChatEngine
from app.services.mcp_client import MCPClient, ToolCache


app = FastAPI(title=settings.app_name)

app.state.chat_engine = ChatEngine(
    MCPClient(settings.mcp_server_url),
    ToolCache(),
)

# Allow requests from configured browser origins. Hosted CloudFront calls use
# same-origin /api requests, so CORS mainly supports local/direct API access.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.allowed_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(chat_router)
app.include_router(health_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
