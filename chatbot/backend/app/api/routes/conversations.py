"""Conversation listing and message retrieval endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...db.models import Conversation, Message
from ...db.session import get_db
from ...models.schemas import ConversationOut, MessageOut

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.get("", response_model=list[ConversationOut])
def list_conversations(db: Session = Depends(get_db)):
    return db.query(Conversation).order_by(Conversation.updated_at.desc()).all()


@router.get("/{conv_id}/messages", response_model=list[MessageOut])
def get_messages(conv_id: str, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return (
        db.query(Message)
        .filter(Message.conversation_id == conv_id)
        .order_by(Message.created_at.asc())
        .all()
    )
