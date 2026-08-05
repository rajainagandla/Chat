"""Chat endpoints including SSE streaming."""

import json
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...models.schemas import ChatRequest, ChatResponse
from ...services.rag_pipeline import answer_query, stream_query

router = APIRouter(prefix="/api", tags=["chat"])

DbDep = Annotated[Session, Depends(get_db)]


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: DbDep):
    conv_id, answer, sources = answer_query(db, request.message, request.conversation_id)
    return ChatResponse(conversation_id=conv_id, answer=answer, sources=sources)


@router.post("/chat/stream")
def chat_stream(request: ChatRequest, db: DbDep):
    """Stream chat tokens as Server-Sent Events."""

    def event_stream():
        for event, data in stream_query(db, request.message, request.conversation_id):
            payload = {"event": event, "data": data}
            yield f"data: {json.dumps(payload)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
