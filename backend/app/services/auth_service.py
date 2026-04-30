"""
services/auth_service.py — JWT creation and validation helpers.

Tokens are signed with HS256 using `settings.jwt_secret`.
The only claim stored is "sub" (the customer's email address).
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.config import settings

# HS256 is sufficient for a symmetric secret shared only by this service.
ALGORITHM = "HS256"


def create_access_token(email: str) -> str:
    """
    Mint a new JWT for the given customer email.

    The token expires after `settings.jwt_expires_minutes` minutes.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expires_minutes)
    payload = {"sub": email, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def decode_access_token(token: str) -> str:
    """
    Validate and decode a JWT, returning the customer email.

    Raises ValueError for any invalid or expired token so callers
    can convert it to an HTTP 401 without leaking JWT internals.
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise ValueError("Invalid token") from exc

    subject = payload.get("sub")
    if not subject:
        raise ValueError("Invalid token")
    return str(subject)
