"""
routes/chat.py — Chat endpoint.

POST /chat  — accepts an authenticated user message and returns the
              assistant's reply after running the agentic tool loop.

Authentication is enforced via a JWT bearer token in the Authorization
header (issued by POST /auth/login).
"""

import logging

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from app.models import ChatRequest, ChatResponse
from app.services.auth_service import decode_access_token
from app.services.chat_engine import ChatEngine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


def get_current_email(authorization: str | None = Header(default=None)) -> str:
    """
    Dependency: extract and validate the JWT from the Authorization header.

    Returns the customer's email (stored as the JWT subject).
    Raises 401 if the header is missing or the token is invalid/expired.
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = authorization.split(" ", 1)[1]
    try:
        return decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc


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
    email: str = Depends(get_current_email),
    chat_engine: ChatEngine = Depends(get_chat_engine),
) -> ChatResponse:
    """
    Send a message to the AI assistant.

    The authenticated customer's email is passed to the chat engine so the
    assistant can personalise responses (e.g. look up orders for that account).
    """
    try:
        reply = await chat_engine.respond(email, payload.message)
    except Exception as exc:
        logger.exception("Chat engine error for %s: %s", email, exc)
        raise HTTPException(status_code=502, detail="Unable to process request")

    return ChatResponse(reply=reply)
