from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

from core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(key: str = Security(api_key_header)) -> str:
    """
    Optional API key guard — only active in production.
    In development, all requests pass through freely.
    """
    if not settings.is_production:
        return "dev"

    if not key or key != settings.SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key. Pass it in the X-API-Key header.",
        )
    return key
