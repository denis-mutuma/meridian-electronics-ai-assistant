"""
routes/health.py — Liveness probe endpoint.

GET /health  — returns {"status": "ok"} with HTTP 200.
Used by AWS App Runner to determine whether the container is healthy.
No authentication required.
"""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """Simple liveness check — always returns ok if the process is running."""
    return {"status": "ok"}
