import logging
from typing import Optional
import httpx
from config import settings

logger = logging.getLogger(__name__)

TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


async def verify_turnstile_token(token: str, client_ip: Optional[str] = None) -> bool:
    """
    Verifies a Cloudflare Turnstile token server-to-server.
    """
    secret = settings.TURNSTILE_SECRET_KEY
    if not secret:
        logger.error("[turnstile] TURNSTILE_SECRET_KEY is not configured in backend settings")
        return False

    payload = {
        "secret": secret,
        "response": token,
    }
    if client_ip and client_ip != "unknown":
        payload["remoteip"] = client_ip

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(TURNSTILE_VERIFY_URL, json=payload)
            data = response.json()
            success = data.get("success", False)
            if not success:
                logger.warning(f"[turnstile] Verification failed: {data.get('error-codes', [])}")
            return success
    except Exception as exc:
        logger.error(f"[turnstile] HTTP error verifying token: {exc}")
        return False
