"""
models.py — Pydantic request/response schemas used across all routes.

These act as both the API contract (OpenAPI schema) and input validators.
"""

from pydantic import BaseModel, EmailStr, Field


# ── Auth ─────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    """Credentials submitted to POST /auth/login."""
    email: EmailStr               # Normalised and validated by Pydantic.
    pin: str = Field(min_length=4, max_length=4)  # Exactly 4 characters.


class LoginResponse(BaseModel):
    """Returned on successful login — contains the JWT bearer token."""
    access_token: str
    token_type: str = "bearer"    # Always "bearer" for this API.


# ── Chat ─────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    """Single user message submitted to POST /chat."""
    message: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    """Assistant reply returned from POST /chat."""
    reply: str
