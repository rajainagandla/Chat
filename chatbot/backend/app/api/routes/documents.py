"""Document upload, listing, and deletion endpoints."""
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ...config import settings
from ...db.models import Document
from ...db.session import get_db
from ...models.schemas import DocumentOut
from ...services.ingestion import ingest_document
from ...services.vector_store import get_vector_store

router = APIRouter(prefix="/api/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB


def _validate_file(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")
    return ext


@router.post("", response_model=DocumentOut, status_code=201)
def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    ext = _validate_file(file.filename or "")

    # Read content with size limit
    content = file.file.read(MAX_FILE_SIZE + 1)
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 25 MB)")

    # Save file
    doc_id = str(uuid.uuid4())
    save_name = f"{doc_id}{ext}"
    save_path = settings.upload_path / save_name
    save_path.write_bytes(content)

    doc = Document(
        id=doc_id,
        filename=file.filename,
        filepath=str(save_path),
        filetype=ext.lstrip("."),
        status="processing",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Ingest (parse + embed + index)
    try:
        chunk_count = ingest_document(doc_id, file.filename, str(save_path))
        doc.status = "ready"
        doc.chunk_count = chunk_count
    except Exception as exc:  # noqa: BLE001
        doc.status = "failed"
        doc.error = str(exc)
    finally:
        db.commit()
        db.refresh(doc)

    return doc


@router.get("", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db)):
    return db.query(Document).order_by(Document.created_at.desc()).all()


@router.delete("/{doc_id}", status_code=204)
def delete_document(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Remove from vector store
    try:
        get_vector_store().delete_document(doc_id)
    except Exception:  # noqa: BLE001
        pass

    # Remove file
    try:
        Path(doc.filepath).unlink(missing_ok=True)
    except Exception:  # noqa: BLE001
        pass

    db.delete(doc)
    db.commit()
