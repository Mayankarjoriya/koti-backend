from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

from config import settings
from routers.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/api/agents", tags=["AI Agents"])

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    agent_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest, current_user: User = Depends(get_current_user)):
    """
    Placeholder endpoint for AI Agent integration.
    In the future, this will connect to OpenRouter or HuggingFace API using `settings.OPENROUTER_API_KEY`.
    """
    
    if not settings.OPENROUTER_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED, 
            detail="AI integration is not configured. Missing OPENROUTER_API_KEY."
        )

    # Note: In a real implementation, you would use `httpx` or an OpenAI-compatible 
    # client to stream responses back from the LLM provider.
    
    user_message = request.messages[-1].content if request.messages else ""
    
    # Mock Response
    reply = f"Hello {current_user.email}. This is the Signal AI Agent. You said: '{user_message}'"
    
    return ChatResponse(reply=reply)
