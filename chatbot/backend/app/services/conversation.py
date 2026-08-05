"""Conversation & message persistence helpers."""

from sqlalchemy.orm import Session

from ..db.models import Conversation, Message


def get_or_create_conversation(db: Session, conversation_id: str | None) -> Conversation:
    if conversation_id:
        conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conv:
            return conv
    conv = Conversation()
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


def get_history(db: Session, conversation_id: str, limit: int = 10) -> list[dict]:
    msgs = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .limit(limit)
        .all()
    )
    return [{"role": m.role, "content": m.content} for m in msgs]


def add_message(db: Session, conversation_id: str, role: str, content: str) -> None:
    msg = Message(conversation_id=conversation_id, role=role, content=content)
    db.add(msg)
    db.commit()
