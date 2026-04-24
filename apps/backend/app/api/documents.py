from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from app.db.session import get_db
from app.utils.auth import get_current_user
from app.models.user import User
from app.models.document import Document, DocumentType, DocumentStatus
import math

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("")
def search_documents(
    q: Optional[str] = Query(None, description="Search by document number or title"),
    type: Optional[str] = Query(None, description="quotation | mom | work_order"),
    status: Optional[str] = Query(None, description="draft | processing | review | finalized"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Search all documents across modules with optional filters.

    - **q**: full-text search on document_number and title
    - **type**: filter to a single document type
    - **status**: filter by document status
    """
    query = db.query(Document).filter(Document.user_id == current_user.id)

    if q:
        query = query.filter(
            or_(
                Document.document_number.ilike(f"%{q}%"),
                Document.title.ilike(f"%{q}%"),
            )
        )

    if type:
        try:
            query = query.filter(Document.document_type == DocumentType(type))
        except ValueError:
            pass  # ignore unknown type values

    if status:
        try:
            query = query.filter(Document.status == DocumentStatus(status))
        except ValueError:
            pass

    total = query.count()
    docs = (
        query.order_by(Document.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 1,
        "items": [
            {
                "id": d.id,
                "document_type": d.document_type.value,
                "document_number": d.document_number,
                "title": d.title,
                "status": d.status.value,
                "has_pdf": bool(d.final_pdf_url),
                "created_at": d.created_at.isoformat() if d.created_at else None,
                "updated_at": d.updated_at.isoformat() if d.updated_at else None,
            }
            for d in docs
        ],
    }


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a document and its underlying entity (quotation / MOM / work order).
    Ownership is verified before deletion.
    """
    document = db.query(Document).filter(
        Document.id == doc_id,
        Document.user_id == current_user.id,
    ).first()

    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Delete the underlying entity first (cascades to child rows)
    if document.document_type == DocumentType.QUOTATION:
        from app.models.quotation import Quotation
        entity = db.query(Quotation).filter(Quotation.document_id == doc_id).first()
    elif document.document_type == DocumentType.MOM:
        from app.models.mom import MOM
        entity = db.query(MOM).filter(MOM.document_id == doc_id).first()
    elif document.document_type == DocumentType.WORK_ORDER:
        from app.models.work_order import WorkOrder
        entity = db.query(WorkOrder).filter(WorkOrder.document_id == doc_id).first()
    else:
        entity = None

    if entity:
        db.delete(entity)

    db.delete(document)
    db.commit()
    return None
