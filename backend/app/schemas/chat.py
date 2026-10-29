from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)


class ChatMessageResponse(BaseModel):
    reply: str
    sender: str = "assistant"
    timestamp: str
    suggested_prompts: List[str] = []
    context_data: Optional[Dict[str, Any]] = None
