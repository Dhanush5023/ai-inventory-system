from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    """Chatbot request schema"""
    question: str = Field(..., description="The business question for the AI")

class ChatResponse(BaseModel):
    """Chatbot response schema"""
    answer: str
    status: str = "success"
    error: Optional[str] = None
