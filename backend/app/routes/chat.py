import logging
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from app.services.chat_engine import ChatEngine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


class ChatHistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    # customer_email is collected in the frontend UI and sent with every request.
    # There is no session or JWT — identity is per-request.
    customer_email: str = Field(min_length=1, max_length=254)
    message: str = Field(min_length=1, max_length=2000)
    history: list[ChatHistoryMessage] = Field(default_factory=list, max_length=16)


class ChatResponse(BaseModel):
    reply: str


def get_chat_engine(request: Request) -> ChatEngine:
    # The chat engine is attached to app.state in main.py.
    # Return 503 if startup failed so the client gets a clear error.
    chat_engine = getattr(request.app.state, "chat_engine", None)
    if chat_engine is None:
        raise HTTPException(status_code=503, detail="Chat engine unavailable")
    return chat_engine


@router.post("", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    chat_engine: ChatEngine = Depends(get_chat_engine),
) -> ChatResponse:
    try:
        reply = await chat_engine.respond(
            payload.customer_email,
            payload.message,
            history=[message.model_dump() for message in payload.history],
        )
    except Exception as exc:
        logger.exception("Chat engine error: %s", exc)
        raise HTTPException(status_code=502, detail="Unable to process request")

    return ChatResponse(reply=reply)
