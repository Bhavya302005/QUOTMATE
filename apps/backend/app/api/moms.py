from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.document import Document, DocumentType, DocumentStatus
from app.models.mom import MOM, ActionItem, ActionItemStatus, ActionItemPriority
from app.schemas.mom import (
    MOMCreate,
    MOMUpdate,
    MOMResponse,
    MOMListResponse,
    ActionItemCreate,
    ActionItemUpdate,
    ActionItemResponse,
    SummarizeRequest,
    SummarizeResponse
)
from app.utils.auth import get_current_user
from app.services.audit_service import log_audit
from app.services.nvidia_nims_service import nvidia_nims_service
from typing import Optional
from datetime import datetime, date
from pathlib import Path
from sqlalchemy.exc import SQLAlchemyError
import uuid
import json
import math

router = APIRouter(prefix="/api/moms", tags=["MOMs"])


def _generate_unique_mom_number(db: Session) -> str:
    """
    Generate globally unique MOM number matching documents.document_number unique constraint.
    """
    next_index = db.query(Document).filter(
        Document.document_type == DocumentType.MOM
    ).count() + 1

    while True:
        candidate = f"MOM-{next_index:04d}"
        exists = db.query(Document).filter(Document.document_number == candidate).first()
        if not exists:
            return candidate
        next_index += 1


def _normalize_priority(priority_value: Optional[str]) -> ActionItemPriority:
    priority_map = {
        "low": ActionItemPriority.LOW,
        "medium": ActionItemPriority.MEDIUM,
        "high": ActionItemPriority.HIGH,
        "critical": ActionItemPriority.CRITICAL
    }
    return priority_map.get(str(priority_value or "medium").lower(), ActionItemPriority.MEDIUM)


def _parse_due_date(due_date_value: Optional[str]) -> Optional[date]:
    if not due_date_value:
        return None
    if isinstance(due_date_value, date):
        return due_date_value
    try:
        return datetime.strptime(str(due_date_value), "%Y-%m-%d").date()
    except ValueError:
        return None


def _clean_action_title(raw_title: Optional[str]) -> Optional[str]:
    title = str(raw_title or "").strip()
    if not title:
        return None

    while title and title[0] in "-*+•\t ":
        title = title[1:].strip()

    if len(title) < 3:
        return None

    return title[:500]


def _build_mom_pdf_data(mom: MOM, document: Document, action_items: list, current_user: User) -> dict:
    return {
        "mom_number": document.document_number,
        "meeting_title": mom.meeting_title,
        "meeting_date": mom.meeting_date,
        "meeting_time": mom.meeting_time,
        "location": mom.location,
        "attendees": json.loads(mom.attendees) if mom.attendees else [],
        "raw_notes": mom.raw_notes,
        "summary": mom.ai_summary,
        "key_points": json.loads(mom.key_points) if mom.key_points else [],
        "decisions": json.loads(mom.decisions) if mom.decisions else [],
        "next_steps": json.loads(mom.next_steps) if mom.next_steps else [],
        "action_items": [
            {
                "title": item.title,
                "description": item.description,
                "assigned_to": item.assigned_to,
                "due_date": item.due_date,
                "priority": item.priority.value if hasattr(item.priority, "value") else str(item.priority),
                "status": item.status.value if hasattr(item.status, "value") else str(item.status)
            }
            for item in action_items
        ],
        "company_name": current_user.company_name or current_user.full_name,
        "company_email": current_user.email,
        "company_phone": current_user.phone,
        "user_data": {
            "full_name": current_user.full_name,
            "phone": current_user.phone,
            "email": current_user.email,
            "address": current_user.address,
            "company_name": current_user.company_name,
            "company_logo_url": current_user.company_logo_url
        }
    }


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_meeting_notes(
    request: SummarizeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    AI-powered meeting notes summarization
    
    Uses NVIDIA NIMs to extract:
    - Meeting summary
    - Key discussion points
    - Decisions made
    - Action items
    - Next steps
    """
    try:
        result = nvidia_nims_service.summarize_meeting_notes(
            raw_notes=request.raw_notes,
            meeting_context=request.meeting_context
        )
        
        return SummarizeResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI summarization failed: {str(e)}"
        )


@router.post("", response_model=MOMResponse, status_code=status.HTTP_201_CREATED)
async def create_mom(
    mom_data: MOMCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new Minutes of Meeting
    
    - Auto-creates Document if document_id not provided
    - Generates MOM-#### number
    - Stores meeting details and notes
    """
    try:
        # Resolve or create document
        if mom_data.document_id:
            document = db.query(Document).filter(
                Document.id == mom_data.document_id,
                Document.user_id == current_user.id
            ).first()

            if not document:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Document not found"
                )

            if document.document_type != DocumentType.MOM:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Provided document is not a MOM document"
                )

            existing_mom = db.query(MOM).filter(MOM.document_id == document.id).first()
            if existing_mom:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This document is already linked to a MOM"
                )
        else:
            document = Document(
                id=str(uuid.uuid4()),
                user_id=current_user.id,
                document_type=DocumentType.MOM,
                document_number=_generate_unique_mom_number(db),
                title=mom_data.meeting_title,
                status=DocumentStatus.DRAFT,
                original_image_url=mom_data.original_image_url,
                ocr_raw_text=mom_data.ocr_raw_text,
                ocr_confidence=mom_data.ocr_confidence,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(document)

        document.title = mom_data.meeting_title
        if mom_data.original_image_url:
            document.original_image_url = mom_data.original_image_url
        if mom_data.ocr_raw_text:
            document.ocr_raw_text = mom_data.ocr_raw_text
        if mom_data.ocr_confidence is not None:
            document.ocr_confidence = mom_data.ocr_confidence

        ai_result = None
        if mom_data.trigger_ai_summary:
            try:
                ai_result = nvidia_nims_service.summarize_meeting_notes(
                    raw_notes=mom_data.raw_notes,
                    meeting_context=mom_data.meeting_context
                )
            except Exception:
                # Graceful fallback: keep creating MOM with raw notes only
                ai_result = None

        mom_id = str(uuid.uuid4())
        mom = MOM(
            id=mom_id,
            document_id=document.id,
            meeting_title=mom_data.meeting_title,
            meeting_date=mom_data.meeting_date,
            meeting_time=mom_data.meeting_time,
            location=mom_data.location,
            attendees=json.dumps(mom_data.attendees) if mom_data.attendees else None,
            raw_notes=mom_data.raw_notes,
            ai_summary=ai_result.get("summary") if ai_result else None,
            key_points=json.dumps(ai_result.get("key_points", [])) if ai_result else None,
            decisions=json.dumps(ai_result.get("decisions", [])) if ai_result else None,
            next_steps=json.dumps(ai_result.get("next_steps", [])) if ai_result else None,
            ai_confidence=ai_result.get("confidence") if ai_result else None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(mom)
        db.flush()

        created_action_items = []
        should_create_ai_actions = bool(
            ai_result and ai_result.get("ai_model") not in {"fallback", None}
        )

        if should_create_ai_actions:
            ai_items = ai_result.get("action_items", [])
            seen_titles = set()
            if isinstance(ai_items, list):
                for index, item in enumerate(ai_items, start=1):
                    if not isinstance(item, dict):
                        continue

                    title = _clean_action_title(item.get("title") or item.get("task"))
                    if not title:
                        continue

                    normalized_title = title.lower()
                    if normalized_title in seen_titles:
                        continue
                    seen_titles.add(normalized_title)

                    action_item = ActionItem(
                        id=str(uuid.uuid4()),
                        mom_id=mom_id,
                        title=title,
                        description=str(item.get("description") or "").strip() or None,
                        assigned_to=str(item.get("assigned_to") or "").strip() or None,
                        due_date=_parse_due_date(item.get("due_date") or item.get("deadline")),
                        priority=_normalize_priority(item.get("priority")),
                        status=ActionItemStatus.PENDING,
                        order=index,
                        is_ai_generated=True,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    try:
                        with db.begin_nested():
                            db.add(action_item)
                            db.flush()
                        created_action_items.append(action_item)
                    except SQLAlchemyError:
                        continue

            document.status = DocumentStatus.REVIEW
        else:
            document.status = DocumentStatus.DRAFT

        db.commit()
        db.refresh(mom)
        db.refresh(document)

        # Query action items fresh from database after commit
        action_items_from_db = db.query(ActionItem).filter(
            ActionItem.mom_id == mom_id
        ).order_by(ActionItem.order).all()

        # Log audit
        log_audit(
            db=db,
            user_id=current_user.id,
            action="mom.created",
            entity_type="MOM",
            entity_id=mom_id
        )
        db.commit()  # Commit audit log

        return MOMResponse(
            id=mom.id,
            document_id=mom.document_id,
            meeting_title=mom.meeting_title,
            meeting_date=mom.meeting_date,
            meeting_time=mom.meeting_time,
            location=mom.location,
            attendees=json.loads(mom.attendees) if mom.attendees else [],
            raw_notes=mom.raw_notes,
            ai_summary=mom.ai_summary,
            key_points=json.loads(mom.key_points) if mom.key_points else [],
            decisions=json.loads(mom.decisions) if mom.decisions else [],
            next_steps=json.loads(mom.next_steps) if mom.next_steps else [],
            ai_confidence=mom.ai_confidence,
            action_items=[
                ActionItemResponse(
                    id=item.id,
                    mom_id=item.mom_id,
                    title=item.title,
                    description=item.description,
                    assigned_to=item.assigned_to,
                    due_date=item.due_date,
                    priority=item.priority,
                    status=item.status,
                    order=item.order,
                    is_ai_generated=item.is_ai_generated,
                    created_at=item.created_at,
                    updated_at=item.updated_at
                )
                for item in action_items_from_db
            ],
            mom_number=document.document_number,
            status=document.status.value,
            created_at=mom.created_at,
            updated_at=mom.updated_at
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create MOM: {str(e)}"
        )


@router.get("", response_model=MOMListResponse)
async def list_moms(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all MOMs with pagination and search
    
    - Supports search by meeting title or location
    - Includes action item counts
    - Ordered by meeting date (newest first)
    """
    # Build base query
    query = db.query(MOM).join(
        Document, MOM.document_id == Document.id
    ).filter(
        Document.user_id == current_user.id
    )
    
    # Apply search
    if search:
        query = query.filter(
            MOM.meeting_title.contains(search) |
            MOM.location.contains(search)
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering
    moms = query.order_by(
        MOM.meeting_date.desc(),
        MOM.created_at.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()
    
    # Prepare response
    items = []
    for mom in moms:
        document = db.query(Document).filter(Document.id == mom.document_id).first()
        action_items = db.query(ActionItem).filter(
            ActionItem.mom_id == mom.id
        ).order_by(ActionItem.order).all()
        
        items.append(MOMResponse(
            id=mom.id,
            document_id=mom.document_id,
            meeting_title=mom.meeting_title,
            meeting_date=mom.meeting_date,
            meeting_time=mom.meeting_time,
            location=mom.location,
            attendees=json.loads(mom.attendees) if mom.attendees else [],
            raw_notes=mom.raw_notes,
            ai_summary=mom.ai_summary,
            key_points=json.loads(mom.key_points) if mom.key_points else [],
            decisions=json.loads(mom.decisions) if mom.decisions else [],
            next_steps=json.loads(mom.next_steps) if mom.next_steps else [],
            ai_confidence=mom.ai_confidence,
            action_items=[
                ActionItemResponse(
                    id=item.id,
                    mom_id=item.mom_id,
                    title=item.title,
                    description=item.description,
                    assigned_to=item.assigned_to,
                    due_date=item.due_date,
                    priority=item.priority,
                    status=item.status,
                    order=item.order,
                    is_ai_generated=item.is_ai_generated,
                    created_at=item.created_at,
                    updated_at=item.updated_at
                ) for item in action_items
            ],
            mom_number=document.document_number,
            status=document.status.value,
            created_at=mom.created_at,
            updated_at=mom.updated_at
        ))
    
    return MOMListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 1
    )


@router.get("/{mom_id}", response_model=MOMResponse)
async def get_mom(
    mom_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single MOM by ID with all action items"""
    
    mom = db.query(MOM).join(
        Document, MOM.document_id == Document.id
    ).filter(
        MOM.id == mom_id,
        Document.user_id == current_user.id
    ).first()
    
    if not mom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MOM not found"
        )
    
    document = db.query(Document).filter(Document.id == mom.document_id).first()
    action_items = db.query(ActionItem).filter(
        ActionItem.mom_id == mom_id
    ).order_by(ActionItem.order).all()
    
    return MOMResponse(
        id=mom.id,
        document_id=mom.document_id,
        meeting_title=mom.meeting_title,
        meeting_date=mom.meeting_date,
        meeting_time=mom.meeting_time,
        location=mom.location,
        attendees=json.loads(mom.attendees) if mom.attendees else [],
        raw_notes=mom.raw_notes,
        ai_summary=mom.ai_summary,
        key_points=json.loads(mom.key_points) if mom.key_points else [],
        decisions=json.loads(mom.decisions) if mom.decisions else [],
        next_steps=json.loads(mom.next_steps) if mom.next_steps else [],
        ai_confidence=mom.ai_confidence,
        action_items=[
            ActionItemResponse(
                id=item.id,
                mom_id=item.mom_id,
                title=item.title,
                description=item.description,
                assigned_to=item.assigned_to,
                due_date=item.due_date,
                priority=item.priority,
                status=item.status,
                order=item.order,
                is_ai_generated=item.is_ai_generated,
                created_at=item.created_at,
                updated_at=item.updated_at
            ) for item in action_items
        ],
        mom_number=document.document_number,
        status=document.status.value,
        created_at=mom.created_at,
        updated_at=mom.updated_at
    )


@router.put("/{mom_id}", response_model=MOMResponse)
async def update_mom(
    mom_id: str,
    mom_data: MOMUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update MOM details"""
    
    mom = db.query(MOM).join(
        Document, MOM.document_id == Document.id
    ).filter(
        MOM.id == mom_id,
        Document.user_id == current_user.id
    ).first()
    
    if not mom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MOM not found"
        )
    
    # Update fields
    update_data = mom_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if field in ['attendees', 'key_points', 'decisions', 'next_steps'] and value is not None:
            setattr(mom, field, json.dumps(value))
        else:
            setattr(mom, field, value)
    
    mom.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(mom)
    
    # Log audit
    log_audit(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="MOM",
        entity_id=mom_id
    )
    
    # Return updated MOM
    return await get_mom(mom_id, current_user, db)


@router.delete("/{mom_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mom(
    mom_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete MOM and associated document"""
    
    mom = db.query(MOM).join(
        Document, MOM.document_id == Document.id
    ).filter(
        MOM.id == mom_id,
        Document.user_id == current_user.id
    ).first()
    
    if not mom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MOM not found"
        )
    
    document_id = mom.document_id
    
    # Log audit before deletion
    log_audit(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        entity_type="MOM",
        entity_id=mom_id
    )
    
    # Delete MOM (cascade will delete action items)
    db.delete(mom)
    
    # Delete document
    document = db.query(Document).filter(Document.id == document_id).first()
    if document:
        db.delete(document)
    
    db.commit()


# Action Item Endpoints

@router.post("/{mom_id}/action-items", response_model=ActionItemResponse, status_code=status.HTTP_201_CREATED)
async def create_action_item(
    mom_id: str,
    item_data: ActionItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add action item to MOM"""
    
    # Verify MOM exists and user owns it
    mom = db.query(MOM).join(
        Document, MOM.document_id == Document.id
    ).filter(
        MOM.id == mom_id,
        Document.user_id == current_user.id
    ).first()
    
    if not mom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MOM not found"
        )
    
    # Get next order number
    max_order = db.query(ActionItem).filter(
        ActionItem.mom_id == mom_id
    ).count()
    
    # Create action item
    item_id = str(uuid.uuid4())
    action_item = ActionItem(
        id=item_id,
        mom_id=mom_id,
        title=item_data.title,
        description=item_data.description,
        assigned_to=item_data.assigned_to,
        due_date=item_data.due_date,
        priority=item_data.priority,
        status=item_data.status,
        order=max_order + 1,
        is_ai_generated=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(action_item)
    db.commit()
    db.refresh(action_item)
    
    return ActionItemResponse(
        id=action_item.id,
        mom_id=action_item.mom_id,
        title=action_item.title,
        description=action_item.description,
        assigned_to=action_item.assigned_to,
        due_date=action_item.due_date,
        priority=action_item.priority,
        status=action_item.status,
        order=action_item.order,
        is_ai_generated=action_item.is_ai_generated,
        created_at=action_item.created_at,
        updated_at=action_item.updated_at
    )


@router.put("/{mom_id}/action-items/{item_id}", response_model=ActionItemResponse)
@router.put("/{mom_id}/actions/{item_id}", response_model=ActionItemResponse)
async def update_action_item(
    mom_id: str,
    item_id: str,
    item_data: ActionItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update action item"""
    
    # Verify ownership
    action_item = db.query(ActionItem).join(
        MOM, ActionItem.mom_id == MOM.id
    ).join(
        Document, MOM.document_id == Document.id
    ).filter(
        ActionItem.id == item_id,
        ActionItem.mom_id == mom_id,
        Document.user_id == current_user.id
    ).first()
    
    if not action_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action item not found"
        )
    
    # Update fields
    update_data = item_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(action_item, field, value)
    
    action_item.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(action_item)
    
    return ActionItemResponse(
        id=action_item.id,
        mom_id=action_item.mom_id,
        title=action_item.title,
        description=action_item.description,
        assigned_to=action_item.assigned_to,
        due_date=action_item.due_date,
        priority=action_item.priority,
        status=action_item.status,
        order=action_item.order,
        is_ai_generated=action_item.is_ai_generated,
        created_at=action_item.created_at,
        updated_at=action_item.updated_at
    )


@router.delete("/{mom_id}/action-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_action_item(
    mom_id: str,
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete action item"""
    
    # Verify ownership
    action_item = db.query(ActionItem).join(
        MOM, ActionItem.mom_id == MOM.id
    ).join(
        Document, MOM.document_id == Document.id
    ).filter(
        ActionItem.id == item_id,
        ActionItem.mom_id == mom_id,
        Document.user_id == current_user.id
    ).first()
    
    if not action_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action item not found"
        )
    
    db.delete(action_item)
    db.commit()


@router.post("/{mom_id}/finalize", response_model=MOMResponse)
async def finalize_mom(
    mom_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Finalize MOM: generate PDF and mark associated document as finalized.
    """
    from app.services.pdf_service import pdf_service

    mom = db.query(MOM).join(
        Document, MOM.document_id == Document.id
    ).filter(
        MOM.id == mom_id,
        Document.user_id == current_user.id
    ).first()

    if not mom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MOM not found"
        )

    document = db.query(Document).filter(Document.id == mom.document_id).first()
    action_items = db.query(ActionItem).filter(
        ActionItem.mom_id == mom_id
    ).order_by(ActionItem.order).all()

    mom_pdf_data = _build_mom_pdf_data(
        mom=mom,
        document=document,
        action_items=action_items,
        current_user=current_user
    )

    try:
        pdf_bytes = pdf_service.generate_mom_pdf(mom_pdf_data)

        filename = f"mom_{document.document_number}_{uuid.uuid4().hex[:8]}.pdf"
        backend_root = Path(__file__).resolve().parents[2]
        pdf_dir = backend_root / "uploads" / "documents"
        pdf_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = pdf_dir / filename

        with open(pdf_path, "wb") as pdf_file:
            pdf_file.write(pdf_bytes)

        document.final_pdf_url = f"/uploads/documents/{filename}"
        document.status = DocumentStatus.FINALIZED
        db.commit()

        log_audit(
            db=db,
            user_id=current_user.id,
            action="mom.finalized",
            entity_type="MOM",
            entity_id=mom_id,
            new_value={"pdf_url": document.final_pdf_url, "status": "finalized"}
        )

        return await get_mom(mom_id, current_user, db)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to finalize MOM: {str(e)}"
        )


@router.post("/{mom_id}/revert-finalize", response_model=MOMResponse)
async def revert_mom_finalization(
    mom_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revert a finalized MOM back to review state so it can be edited again."""
    mom = db.query(MOM).join(
        Document, MOM.document_id == Document.id
    ).filter(
        MOM.id == mom_id,
        Document.user_id == current_user.id
    ).first()

    if not mom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MOM not found"
        )

    document = db.query(Document).filter(Document.id == mom.document_id).first()
    if document.status != DocumentStatus.FINALIZED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MOM is not finalized"
        )

    document.status = DocumentStatus.REVIEW
    document.final_pdf_url = None
    db.commit()

    log_audit(
        db=db,
        user_id=current_user.id,
        action="mom.finalization_reverted",
        entity_type="MOM",
        entity_id=mom_id,
        new_value={"status": "review"}
    )

    return await get_mom(mom_id, current_user, db)


@router.get("/{mom_id}/download")
async def download_mom_pdf(
    mom_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download MOM PDF

    - If finalized PDF exists, returns it
    - Otherwise generates PDF on-the-fly
    """
    from fastapi.responses import Response
    from app.services.pdf_service import pdf_service

    mom = db.query(MOM).join(
        Document, MOM.document_id == Document.id
    ).filter(
        MOM.id == mom_id,
        Document.user_id == current_user.id
    ).first()

    if not mom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MOM not found"
        )

    document = db.query(Document).filter(Document.id == mom.document_id).first()
    pdf_bytes = None
    backend_root = Path(__file__).resolve().parents[2]

    if document.final_pdf_url and document.final_pdf_url.startswith("/uploads/"):
        existing_pdf_path = backend_root / document.final_pdf_url.lstrip("/")
        if existing_pdf_path.exists():
            if existing_pdf_path.stat().st_size >= 10 * 1024:
                with open(existing_pdf_path, "rb") as pdf_file:
                    pdf_bytes = pdf_file.read()

    if pdf_bytes is None:
        action_items = db.query(ActionItem).filter(
            ActionItem.mom_id == mom_id
        ).order_by(ActionItem.order).all()

        mom_pdf_data = _build_mom_pdf_data(
            mom=mom,
            document=document,
            action_items=action_items,
            current_user=current_user
        )

        try:
            pdf_bytes = pdf_service.generate_mom_pdf(mom_pdf_data)

            # Replace existing tiny/legacy PDF if a stored upload path exists.
            if document.final_pdf_url and document.final_pdf_url.startswith('/uploads/'):
                rewrite_path = backend_root / document.final_pdf_url.lstrip('/')
                rewrite_path.parent.mkdir(parents=True, exist_ok=True)
                with open(rewrite_path, 'wb') as pdf_file:
                    pdf_file.write(pdf_bytes)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate MOM PDF: {str(e)}"
            )

    filename = f"mom_{document.document_number or mom_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
