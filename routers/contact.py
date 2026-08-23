from fastapi import APIRouter, Request, HTTPException, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from schemas.contact import ContactSchema, ContactResponse
from services.turnstile import verify_turnstile_token
from services.email import send_contact_email

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/api", tags=["Contact"])


@router.post("/contact", response_model=ContactResponse)
@limiter.limit("5/minute")
async def process_contact_form(request: Request, body: ContactSchema):
    """
    Processes contact form submission:
    1. Applies rate limit (5 requests per minute per IP).
    2. Validates schema using Pydantic.
    3. Verifies Cloudflare Turnstile token.
    4. Sends notification email via Resend.
    """
    client_ip = request.client.host if request.client else "unknown"

    # Turnstile verification
    is_human = await verify_turnstile_token(token=body.turnstile_token, client_ip=client_ip)
    if not is_human:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bot verification failed. Please refresh and retry."
        )

    # Email dispatch
    try:
        await send_contact_email(contact_data=body)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server email service misconfiguration."
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not send your message at this time. Please try again later."
        )

    return ContactResponse(ok=True, message="Message sent successfully. We will reply within 24 hours.")
