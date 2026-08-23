import logging
from config import settings
from schemas.contact import ContactSchema

logger = logging.getLogger(__name__)


async def send_contact_email(contact_data: ContactSchema) -> bool:
    """
    Dispatches a contact inquiry email via Resend integration.
    """
    resend_key = settings.RESEND_API_KEY
    to_email = settings.CONTACT_EMAIL_TO

    if not resend_key or not to_email:
        logger.error("[email] RESEND_API_KEY or CONTACT_EMAIL_TO is missing in backend configuration")
        raise ValueError("Server email integration misconfigured.")

    subject = f"New inquiry from {contact_data.name} — {contact_data.service}"
    
    text_lines = [
        f"Name: {contact_data.name}",
        f"Email: {contact_data.email}",
    ]
    if contact_data.company:
        text_lines.append(f"Company: {contact_data.company}")
    text_lines.extend([
        f"Service: {contact_data.service}",
        "",
        contact_data.message
    ])
    body_text = "\n".join(text_lines)

    try:
        import resend
        resend.api_key = resend_key
        params = {
            "from": settings.FROM_EMAIL,
            "to": [to_email],
            "reply_to": contact_data.email,
            "subject": subject,
            "text": body_text,
        }
        resend.Emails.send(params)
        logger.info(f"[email] Successfully sent email for {contact_data.email}")
        return True
    except ImportError:
        # Fallback to direct HTTP request using httpx if resend SDK is not installed
        import httpx
        headers = {
            "Authorization": f"Bearer {resend_key}",
            "Content-Type": "application/json",
        }
        json_data = {
            "from": settings.FROM_EMAIL,
            "to": [to_email],
            "reply_to": contact_data.email,
            "subject": subject,
            "text": body_text,
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post("https://api.resend.com/emails", json=json_data, headers=headers)
            resp.raise_for_status()
            logger.info(f"[email] Successfully sent email via HTTP for {contact_data.email}")
            return True
    except Exception as exc:
        logger.error(f"[email] Failed to send email via Resend: {exc}")
        raise RuntimeError("Failed to send notification email.") from exc
