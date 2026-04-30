from fastapi import APIRouter, HTTPException

from app.models import LoginRequest, LoginResponse
from app.services.auth_service import create_access_token
from app.services.demo_users import DEMO_USERS

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    # MVP demo authentication backed by provided test credentials.
    email = payload.email.lower()
    expected_pin = DEMO_USERS.get(email)
    if expected_pin is None or payload.pin != expected_pin:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(email)
    return LoginResponse(access_token=token)
