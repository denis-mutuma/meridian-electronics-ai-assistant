from fastapi import APIRouter, Depends, Header, HTTPException

from app.models import ChatRequest, ChatResponse
from app.services.auth_service import decode_access_token

router = APIRouter(prefix="/chat", tags=["chat"])


def get_current_email(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = authorization.split(" ", 1)[1]
    try:
        return decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest, email: str = Depends(get_current_email)) -> ChatResponse:
    return ChatResponse(reply=f"Hello {email}, I received: {payload.message}")
