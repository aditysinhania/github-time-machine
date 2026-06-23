from typing import List, Optional
from pydantic import BaseModel


class AISummaryResponse(BaseModel):
    repository_id: int
    summary: str
    purpose: str
    risks: List[str]
    strengths: List[str]
    recommendations: List[str]


class ChatMessage(BaseModel):
    role: str     # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    repository_id: int
    answer: str
    history: List[ChatMessage]
