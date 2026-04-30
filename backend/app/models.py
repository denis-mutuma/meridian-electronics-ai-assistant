"""
models.py — Pydantic request/response schemas used across all routes.

These act as both the API contract (OpenAPI schema) and input validators.
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Single user message submitted to POST /chat."""
    message: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    """Assistant reply returned from POST /chat."""
    reply: str
