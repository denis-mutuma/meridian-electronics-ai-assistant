"""
routes/auth.py — Authentication endpoints.

POST /auth/login  — validates email + PIN against the demo user store,
                    returns a signed JWT on success.

This is an MVP demo flow; a production system would query a real user
database and hash passwords instead of plain PINs.
"""

from fastapi import APIRouter, HTTPException

from app.models import LoginRequest, LoginResponse
from app.services.auth_service import create_access_token
from app.services.demo_users import DEMO_USERS

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    """
    Authenticate a demo customer by email + PIN.

    Returns a JWT bearer token valid for `jwt_expires_minutes` minutes.
    Raises 401 if the credentials are not in the demo store.
    """
    # Normalise email to lowercase so comparisons are case-insensitive.
    email = payload.email.lower()

    expected_pin = DEMO_USERS.get(email)

    # Both conditions (unknown email and wrong PIN) return the same error
    # to avoid leaking which emails are registered.
    if expected_pin is None or payload.pin != expected_pin:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(email)
    return LoginResponse(access_token=token)
