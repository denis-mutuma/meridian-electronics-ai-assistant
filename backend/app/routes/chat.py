"""
routes/chat.py — Chat endpoint.

POST /chat — accepts a user message and returns the assistant reply after
running the agentic tool loop. Customer context uses default_customer_email
from configuration (no JWT).
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from app.config import settings
from app.models import ChatRequest, ChatResponse
from app.services.chat_engine import ChatEngine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


def get_chat_engine(request: Request) -> ChatEngine:
    """
    Dependency: retrieve the ChatEngine instance from app.state.

    The engine is attached during startup (see main.py lifespan).
    Raises 503 if startup failed to initialise it.
    """
    chat_engine = getattr(request.app.state, "chat_engine", None)
    if chat_engine is None:
        raise HTTPException(status_code=503, detail="Chat engine unavailable")
    return chat_engine


@router.post("", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    chat_engine: ChatEngine = Depends(get_chat_engine),
) -> ChatResponse:
    """Send a message to the AI assistant."""
    try:
        reply = await chat_engine.respond(settings.default_customer_email, payload.message)
    except Exception as exc:
        logger.exception("Chat engine error: %s", exc)
        raise HTTPException(status_code=502, detail="Unable to process request")

    return ChatResponse(reply=reply)
