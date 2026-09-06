import logging
from config import settings
from schemas.contact import ContactSchema

logger = logging.getLogger(__name__)


def _dispatch_email(resend_key: str, from_email: str, to_email: str, subject: str, body_text: str, reply_to: str = None):
    """Internal helper to dispatch email using Resend SDK or HTTP fallback."""
    try:
        import resend
        resend.api_key = resend_key
        params = {
            "from": from_email,
            "to": [to_email],
            "subject": subject,
            "text": body_text,
        }
        if reply_to:
            params["reply_to"] = reply_to
        resend.Emails.send(params)
    except ImportError:
        import httpx
        headers = {
            "Authorization": f"Bearer {resend_key}",
            "Content-Type": "application/json",
        }
        json_data = {
            "from": from_email,
            "to": [to_email],
            "subject": subject,
            "text": body_text,
        }
        if reply_to:
            json_data["reply_to"] = reply_to
        with httpx.Client(timeout=10.0) as client:
            resp = client.post("https://api.resend.com/emails", json=json_data, headers=headers)
            resp.raise_for_status()


async def send_contact_email(contact_data: ContactSchema) -> bool:
    """
    Dispatches:
    1. A contact inquiry email to the site admin.
    2. A confirmation auto-reply email to the submitting user.
    """
    resend_key = settings.RESEND_API_KEY
    admin_to_email = settings.CONTACT_EMAIL_TO

    if not resend_key or not admin_to_email:
        logger.error("[email] RESEND_API_KEY or CONTACT_EMAIL_TO is missing in backend configuration")
        raise ValueError("Server email integration misconfigured.")

    # 1. Send Admin Notification Email
    admin_subject = f"New inquiry from {contact_data.name} — {contact_data.service}"
    
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
    admin_body_text = "\n".join(text_lines)

    try:
        _dispatch_email(
            resend_key=resend_key,
            from_email=settings.FROM_EMAIL,
            to_email=admin_to_email,
            subject=admin_subject,
            body_text=admin_body_text,
            reply_to=contact_data.email
        )
        logger.info(f"[email] Successfully sent admin notification email for {contact_data.email}")
    except Exception as exc:
        logger.error(f"[email] Failed to send admin notification email via Resend: {exc}")
        raise RuntimeError("Failed to send notification email.") from exc

    # 2. Send User Confirmation Email (Auto-Reply)
    user_subject = "Thank you for contacting Signal — We've received your inquiry"
    user_body_text = (
        f"Hi {contact_data.name},\n\n"
        f"Thank you for reaching out to Signal regarding our '{contact_data.service}' services!\n\n"
        f"We have received your message and our team is currently reviewing your inquiry. "
        f"We will get back to you within 24 hours.\n\n"
        f"Here is a summary of your submission:\n"
        f"----------------------------------------\n"
        f"Service: {contact_data.service}\n"
        f"Message: {contact_data.message}\n"
        f"----------------------------------------\n\n"
        f"Best regards,\n"
        f"The Signal Team"
    )

    try:
        _dispatch_email(
            resend_key=resend_key,
            from_email=settings.FROM_EMAIL,
            to_email=contact_data.email,
            subject=user_subject,
            body_text=user_body_text,
            reply_to=None
        )
        logger.info(f"[email] Successfully sent confirmation email to {contact_data.email}")
    except Exception as exc:
        logger.warning(f"[email] Could not send confirmation email to {contact_data.email}: {exc}")

    return True
