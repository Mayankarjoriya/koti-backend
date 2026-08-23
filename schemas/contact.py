from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field, AliasChoices


class ContactSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full name of the requester")
    email: EmailStr = Field(..., description="Valid contact email address")
    company: Optional[str] = Field(None, max_length=120, description="Optional company or project name")
    service: Literal["ai-agents", "cybersecurity", "web-dev", "app-dev", "other"] = Field(
        ..., description="Selected service category"
    )
    message: str = Field(..., min_length=10, max_length=2000, description="Message body details")
    turnstile_token: str = Field(
        ...,
        validation_alias=AliasChoices("turnstile_token", "turnstileToken"),
        min_length=1,
        description="Cloudflare Turnstile token for verification"
    )


class ContactResponse(BaseModel):
    ok: bool
    message: Optional[str] = "Message successfully submitted."
