"""Pydantic request/response schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ---------- Document ----------
class DocumentOut(BaseModel):
    id: str
    filename: str
    filetype: str
    status: str
    chunk_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------- Conversation ----------
class ConversationOut(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MessageOut(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------- Chat ----------
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User query")
    conversation_id: Optional[str] = Field(None, description="Existing conversation id")


class SourceRef(BaseModel):
    document: str
    score: float


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    sources: list[SourceRef] = []
