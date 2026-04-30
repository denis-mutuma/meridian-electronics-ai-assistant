from fastapi import APIRouter, Depends, Header, HTTPException, Request

from app.models import ChatRequest, ChatResponse
from app.services.auth_service import decode_access_token
from app.services.chat_engine import ChatEngine

router = APIRouter(prefix="/chat", tags=["chat"])


def get_current_email(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = authorization.split(" ", 1)[1]
    try:
        return decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc


def get_chat_engine(request: Request) -> ChatEngine:
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
    try:
        reply = await chat_engine.respond(email, payload.message)
    except Exception:
        raise HTTPException(status_code=502, detail="Unable to process request")

    return ChatResponse(reply=reply)
