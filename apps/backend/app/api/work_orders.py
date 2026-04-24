from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.session import get_db
from datetime import datetime as dt
from app.models.user import User
from app.models.document import Document, DocumentType, DocumentStatus
from app.models.work_order import WorkOrder, WorkOrderMaterial, WorkOrderStatus
from app.models.quotation import Quotation
from app.schemas.work_order import (
    WorkOrderCreate,
    WorkOrderUpdate,
    WorkOrderResponse,
    WorkOrderListResponse,
    WorkOrderListItem,
    MaterialCreate,
    MaterialUpdate,
    MaterialResponse,
    LaborCalculateRequest,
    LaborCalculateResponse,
    OCRToWorkOrderRequest,
    OCRToWorkOrderResponse,
    OCRWorkOrderSuggestion,
    OCRMaterialSuggestion,
)
from app.utils.auth import get_current_user
from app.utils.file_upload import FileUploadService
from app.services.audit_service import log_audit
from typing import Optional
from decimal import Decimal
from pathlib import Path
from sqlalchemy.exc import SQLAlchemyError
import uuid
import math

router = APIRouter(prefix="/api/work-orders", tags=["Work Orders"])

file_upload_service = FileUploadService()


def _build_wo_pdf_data(work_order: WorkOrder, document: Document, materials: list, current_user) -> dict:
    """Build dict for work_order.html template rendering."""
    def _fmt_date(d):
        return d.strftime('%d-%m-%Y') if d else '—'

    return {
        "work_order_number": document.document_number or work_order.work_order_number or '—',
        "generated_date": dt.utcnow().strftime('%d-%m-%Y'),
        "client_name": work_order.client_name,
        "client_phone": work_order.client_phone or '',
        "client_email": work_order.client_email or '',
        "service_location": work_order.service_location or '',
        "work_description": work_order.work_description or '',
        "assigned_to": work_order.assigned_to or '',
        "start_date": _fmt_date(work_order.start_date),
        "end_date": _fmt_date(work_order.end_date),
        "status": work_order.status.value if hasattr(work_order.status, 'value') else str(work_order.status),
        "labor_hours": float(work_order.labor_hours or 0),
        "labor_rate": float(work_order.labor_rate or 0),
        "labor_cost": float(work_order.labor_cost or 0),
        "material_cost": float(work_order.material_cost or 0),
        "total_cost": float(work_order.total_cost or 0),
        "materials": [
            {
                "material_name": m.material_name,
                "quantity": float(m.quantity or 0),
                "unit": m.unit or '',
                "unit_cost": float(m.unit_cost or 0),
                "total_cost": float(m.total_cost or 0),
            }
            for m in materials
        ],
        "remarks": work_order.remarks or '',
        "company_name": current_user.company_name or current_user.full_name,
        "company_email": current_user.email or '',
        "company_phone": current_user.phone or '',
    }


# ─── Helpers ────────────────────────────────────────────────────────────────────

def _generate_unique_wo_number(db: Session) -> str:
    next_index = db.query(Document).filter(
        Document.document_type == DocumentType.WORK_ORDER
    ).count() + 1
    while True:
        candidate = f"WO-{next_index:04d}"
        exists = db.query(Document).filter(Document.document_number == candidate).first()
        if not exists:
            return candidate
        next_index += 1


def _calc_costs(work_order: WorkOrder, materials: list) -> None:
    """Recalculate labor_cost, material_cost, total_cost on the work_order in place."""
    labor_hours = Decimal(str(work_order.labor_hours or 0))
    labor_rate = Decimal(str(work_order.labor_rate or 0))
    work_order.labor_cost = labor_hours * labor_rate

    mat_total = Decimal("0")
    for m in materials:
        qty = Decimal(str(m.quantity or 0))
        uc = Decimal(str(m.unit_cost or 0))
        computed = qty * uc
        m.total_cost = computed if not m.total_cost else m.total_cost
        mat_total += Decimal(str(m.total_cost or 0))

    work_order.material_cost = mat_total
    work_order.total_cost = work_order.labor_cost + mat_total


def _get_wo_or_404(wo_id: str, db: Session, current_user: User) -> tuple:
    work_order = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")

    document = db.query(Document).filter(Document.id == work_order.document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Associated document not found")

    if document.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this work order")

    return work_order, document


def _build_response(work_order: WorkOrder, materials: list) -> dict:
    return {
        **{c.name: getattr(work_order, c.name) for c in work_order.__table__.columns},
        "materials": materials,
    }


# ─── CRUD Endpoints ─────────────────────────────────────────────────────────────

@router.post("", response_model=WorkOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_work_order(
    payload: WorkOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new work order. Optionally link to an existing quotation."""

    # Validate linked quotation if provided
    if payload.linked_quotation_id:
        linked_q = db.query(Quotation).filter(Quotation.id == payload.linked_quotation_id).first()
        if not linked_q:
            raise HTTPException(status_code=404, detail="Linked quotation not found")

    wo_number = _generate_unique_wo_number(db)

    try:
        # Create document record
        document = Document(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            document_type=DocumentType.WORK_ORDER,
            document_number=wo_number,
            title=f"Work Order – {payload.client_name}",
            status=DocumentStatus.DRAFT,
        )
        db.add(document)
        db.flush()

        # Create work order record
        work_order = WorkOrder(
            id=str(uuid.uuid4()),
            document_id=document.id,
            linked_quotation_id=payload.linked_quotation_id,
            work_order_number=wo_number,
            client_name=payload.client_name,
            client_phone=payload.client_phone,
            client_email=payload.client_email,
            service_location=payload.service_location,
            work_description=payload.work_description,
            assigned_to=payload.assigned_to,
            start_date=payload.start_date,
            end_date=payload.end_date,
            labor_hours=payload.labor_hours,
            labor_rate=payload.labor_rate,
            remarks=payload.remarks,
            status=WorkOrderStatus.PENDING,
        )
        db.add(work_order)
        db.flush()

        # Create materials
        materials_db = []
        for idx, mat in enumerate(payload.materials or []):
            qty = Decimal(str(mat.quantity or 0))
            uc = Decimal(str(mat.unit_cost or 0))
            computed_total = mat.total_cost if mat.total_cost is not None else (qty * uc)
            m = WorkOrderMaterial(
                id=str(uuid.uuid4()),
                work_order_id=work_order.id,
                material_name=mat.material_name,
                quantity=mat.quantity,
                unit=mat.unit,
                unit_cost=mat.unit_cost,
                total_cost=computed_total,
                order=idx,
            )
            db.add(m)
            materials_db.append(m)

        db.flush()
        _calc_costs(work_order, materials_db)

        db.commit()
        db.refresh(work_order)
        db.refresh(document)

        materials_from_db = (
            db.query(WorkOrderMaterial)
            .filter(WorkOrderMaterial.work_order_id == work_order.id)
            .order_by(WorkOrderMaterial.order)
            .all()
        )

        db.commit()

        log_audit(
            db=db,
            user_id=current_user.id,
            action="create",
            entity_type="work_order",
            entity_id=work_order.id,
            new_value={"work_order_number": wo_number, "client_name": payload.client_name},
        )

        return WorkOrderResponse(
            **{c.name: getattr(work_order, c.name) for c in work_order.__table__.columns},
            materials=[MaterialResponse.model_validate(m) for m in materials_from_db],
        )

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("", response_model=WorkOrderListResponse)
async def list_work_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List work orders with pagination."""

    # Base query – join on document to filter by user
    docs_query = db.query(Document.id).filter(
        Document.user_id == current_user.id,
        Document.document_type == DocumentType.WORK_ORDER,
    )
    doc_ids = [r[0] for r in docs_query.all()]

    query = db.query(WorkOrder).filter(WorkOrder.document_id.in_(doc_ids))

    if status:
        try:
            status_enum = WorkOrderStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
        query = query.filter(WorkOrder.status == status_enum)

    if search:
        query = query.filter(
            WorkOrder.client_name.ilike(f"%{search}%")
            | WorkOrder.work_order_number.ilike(f"%{search}%")
            | WorkOrder.assigned_to.ilike(f"%{search}%")
        )

    total = query.count()
    total_pages = max(1, math.ceil(total / page_size))
    items = query.order_by(WorkOrder.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return WorkOrderListResponse(
        items=[WorkOrderListItem.model_validate(wo) for wo in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{wo_id}", response_model=WorkOrderResponse)
async def get_work_order(
    wo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single work order by ID."""
    work_order, _ = _get_wo_or_404(wo_id, db, current_user)
    materials = (
        db.query(WorkOrderMaterial)
        .filter(WorkOrderMaterial.work_order_id == work_order.id)
        .order_by(WorkOrderMaterial.order)
        .all()
    )
    return WorkOrderResponse(
        **{c.name: getattr(work_order, c.name) for c in work_order.__table__.columns},
        materials=[MaterialResponse.model_validate(m) for m in materials],
    )


@router.put("/{wo_id}", response_model=WorkOrderResponse)
async def update_work_order(
    wo_id: str,
    payload: WorkOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a work order's fields."""
    work_order, document = _get_wo_or_404(wo_id, db, current_user)

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(work_order, field, value)

    materials = (
        db.query(WorkOrderMaterial)
        .filter(WorkOrderMaterial.work_order_id == work_order.id)
        .all()
    )
    _calc_costs(work_order, materials)

    db.commit()
    db.refresh(work_order)

    materials_from_db = (
        db.query(WorkOrderMaterial)
        .filter(WorkOrderMaterial.work_order_id == work_order.id)
        .order_by(WorkOrderMaterial.order)
        .all()
    )

    log_audit(
        db=db,
        user_id=current_user.id,
        action="update",
        entity_type="work_order",
        entity_id=work_order.id,
        new_value=update_data,
    )

    return WorkOrderResponse(
        **{c.name: getattr(work_order, c.name) for c in work_order.__table__.columns},
        materials=[MaterialResponse.model_validate(m) for m in materials_from_db],
    )


@router.delete("/{wo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_work_order(
    wo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a work order and its document."""
    work_order, document = _get_wo_or_404(wo_id, db, current_user)

    log_audit(
        db=db,
        user_id=current_user.id,
        action="delete",
        entity_type="work_order",
        entity_id=work_order.id,
        old_value={"work_order_number": work_order.work_order_number},
    )

    db.delete(document)  # cascades to work_order + materials
    db.commit()


# ─── Materials ───────────────────────────────────────────────────────────────────

@router.post("/{wo_id}/materials", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
async def add_material(
    wo_id: str,
    payload: MaterialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a material to a work order."""
    work_order, _ = _get_wo_or_404(wo_id, db, current_user)

    current_count = db.query(WorkOrderMaterial).filter(WorkOrderMaterial.work_order_id == work_order.id).count()

    qty = Decimal(str(payload.quantity or 0))
    uc = Decimal(str(payload.unit_cost or 0))
    computed_total = payload.total_cost if payload.total_cost is not None else (qty * uc)

    material = WorkOrderMaterial(
        id=str(uuid.uuid4()),
        work_order_id=work_order.id,
        material_name=payload.material_name,
        quantity=payload.quantity,
        unit=payload.unit,
        unit_cost=payload.unit_cost,
        total_cost=computed_total,
        order=current_count,
    )
    db.add(material)
    db.flush()

    all_materials = db.query(WorkOrderMaterial).filter(WorkOrderMaterial.work_order_id == work_order.id).all()
    _calc_costs(work_order, all_materials)
    db.commit()
    db.refresh(material)

    return MaterialResponse.model_validate(material)


@router.put("/{wo_id}/materials/{material_id}", response_model=MaterialResponse)
async def update_material(
    wo_id: str,
    material_id: str,
    payload: MaterialUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a material in a work order."""
    work_order, _ = _get_wo_or_404(wo_id, db, current_user)

    material = db.query(WorkOrderMaterial).filter(
        WorkOrderMaterial.id == material_id,
        WorkOrderMaterial.work_order_id == work_order.id,
    ).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(material, field, value)

    # Recompute total_cost if qty/unit_cost changed and total_cost not explicitly set
    if payload.total_cost is None and (payload.quantity is not None or payload.unit_cost is not None):
        qty = Decimal(str(material.quantity or 0))
        uc = Decimal(str(material.unit_cost or 0))
        material.total_cost = qty * uc

    all_materials = db.query(WorkOrderMaterial).filter(WorkOrderMaterial.work_order_id == work_order.id).all()
    _calc_costs(work_order, all_materials)

    db.commit()
    db.refresh(material)
    return MaterialResponse.model_validate(material)


@router.delete("/{wo_id}/materials/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_material(
    wo_id: str,
    material_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a material from a work order."""
    work_order, _ = _get_wo_or_404(wo_id, db, current_user)

    material = db.query(WorkOrderMaterial).filter(
        WorkOrderMaterial.id == material_id,
        WorkOrderMaterial.work_order_id == work_order.id,
    ).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    db.delete(material)
    db.flush()

    remaining = db.query(WorkOrderMaterial).filter(WorkOrderMaterial.work_order_id == work_order.id).all()
    _calc_costs(work_order, remaining)
    db.commit()


# ─── Photo Upload ────────────────────────────────────────────────────────────────

@router.post("/{wo_id}/upload-photo")
async def upload_photo(
    wo_id: str,
    photo_type: str = Query(..., description="'before' or 'after'"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a before or after photo for a work order."""
    if photo_type not in ("before", "after"):
        raise HTTPException(status_code=400, detail="photo_type must be 'before' or 'after'")

    work_order, _ = _get_wo_or_404(wo_id, db, current_user)

    is_valid, error_msg = FileUploadService.validate_image_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    upload_dir = Path("uploads/images/work_orders")
    upload_dir.mkdir(parents=True, exist_ok=True)

    unique_filename = FileUploadService.generate_unique_filename(file.filename)
    file_path = upload_dir / unique_filename

    import aiofiles
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    photo_url = f"/uploads/images/work_orders/{unique_filename}"

    if photo_type == "before":
        work_order.before_photo_url = photo_url
    else:
        work_order.after_photo_url = photo_url

    db.commit()

    return {
        "message": f"{photo_type.capitalize()} photo uploaded successfully",
        "photo_url": photo_url,
        "photo_type": photo_type,
    }


# ─── Signature Upload ────────────────────────────────────────────────────────────

@router.post("/{wo_id}/upload-signature")
async def upload_signature(
    wo_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload customer signature (PNG from canvas) for a work order."""
    work_order, _ = _get_wo_or_404(wo_id, db, current_user)

    upload_dir = Path("uploads/images/signatures")
    upload_dir.mkdir(parents=True, exist_ok=True)

    unique_filename = FileUploadService.generate_unique_filename(file.filename or "signature.png")
    file_path = upload_dir / unique_filename

    import aiofiles
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    sig_url = f"/uploads/images/signatures/{unique_filename}"
    work_order.customer_signature_url = sig_url
    db.commit()

    return {"message": "Signature uploaded successfully", "signature_url": sig_url}


# ─── OCR → Work Order ───────────────────────────────────────────────────────────

@router.post("/from-ocr", response_model=OCRToWorkOrderResponse)
async def map_ocr_to_work_order(
    ocr_data: OCRToWorkOrderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Map OCR extracted text to work order fields.

    - **ocr_text**: Raw text from OCR extraction
    - **document_id**: Optional document to link (auto-created if omitted)
    """
    from app.services.work_order_mapper import work_order_mapper

    # Auto-create document if not provided
    document = None
    if ocr_data.document_id:
        document = db.query(Document).filter(
            Document.id == ocr_data.document_id,
            Document.user_id == current_user.id
        ).first()
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    else:
        document = Document(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            document_type=DocumentType.WORK_ORDER,
            status=DocumentStatus.DRAFT,
            created_at=dt.utcnow(),
            updated_at=dt.utcnow(),
        )
        db.add(document)
        db.commit()
        db.refresh(document)

    mapped = work_order_mapper.map_text_to_work_order(ocr_data.ocr_text)

    # Build suggested work order
    suggested = None
    if mapped.get('client_name'):
        materials = [
            OCRMaterialSuggestion(
                material_name=m['material_name'],
                quantity=m.get('quantity'),
                unit=m.get('unit'),
                unit_cost=m.get('unit_cost'),
                total_cost=m.get('total_cost'),
            )
            for m in mapped.get('materials', [])
            if m.get('material_name')
        ]
        suggested = OCRWorkOrderSuggestion(
            client_name=mapped.get('client_name'),
            client_phone=mapped.get('client_phone'),
            client_email=mapped.get('client_email'),
            service_location=mapped.get('service_location'),
            work_description=mapped.get('work_description'),
            assigned_to=mapped.get('assigned_to'),
            remarks=mapped.get('remarks'),
            materials=materials,
        )

    return OCRToWorkOrderResponse(
        document_id=document.id,
        suggested_work_order=suggested,
        raw_text=mapped.get('raw_text', ocr_data.ocr_text),
        confidence_flags=mapped.get('confidence_flags', []),
        ai_confidence=mapped.get('ai_confidence'),
    )


# ─── Labor / Cost Calculation ────────────────────────────────────────────────────

@router.post("/calculate", response_model=LaborCalculateResponse)
async def calculate_costs(
    payload: LaborCalculateRequest,
    current_user: User = Depends(get_current_user),
):
    """Calculate labor and material costs without saving."""
    labor_cost = Decimal(str(payload.labor_hours)) * Decimal(str(payload.labor_rate))
    mat_total = Decimal("0")
    for mat in payload.materials or []:
        qty = Decimal(str(mat.quantity or 0))
        uc = Decimal(str(mat.unit_cost or 0))
        tc = mat.total_cost if mat.total_cost is not None else (qty * uc)
        mat_total += Decimal(str(tc))

    return LaborCalculateResponse(
        labor_cost=labor_cost,
        material_cost=mat_total,
        total_cost=labor_cost + mat_total,
    )


# ─── Finalize ────────────────────────────────────────────────────────────────────

@router.post("/{wo_id}/finalize", response_model=WorkOrderResponse)
async def finalize_work_order(
    wo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a work order as completed, generate PDF, and finalize the document."""
    from app.services.pdf_service import pdf_service

    work_order, document = _get_wo_or_404(wo_id, db, current_user)

    materials = (
        db.query(WorkOrderMaterial)
        .filter(WorkOrderMaterial.work_order_id == work_order.id)
        .order_by(WorkOrderMaterial.order)
        .all()
    )

    # Generate PDF
    try:
        wo_pdf_data = _build_wo_pdf_data(work_order, document, materials, current_user)
        pdf_bytes = pdf_service.generate_work_order_pdf(wo_pdf_data)
        filename = f"wo_{document.document_number}_{uuid.uuid4().hex[:8]}.pdf"
        backend_root = Path(__file__).resolve().parents[2]
        pdf_dir = backend_root / "uploads" / "documents"
        pdf_dir.mkdir(parents=True, exist_ok=True)
        (pdf_dir / filename).write_bytes(pdf_bytes)
        document.final_pdf_url = f"/uploads/documents/{filename}"
    except Exception:
        pass  # Don't block finalization if PDF generation fails

    work_order.status = WorkOrderStatus.COMPLETED
    document.status = DocumentStatus.FINALIZED

    db.commit()
    db.refresh(work_order)

    log_audit(
        db=db,
        user_id=current_user.id,
        action="finalize",
        entity_type="work_order",
        entity_id=work_order.id,
        new_value={"status": "completed"},
    )

    return WorkOrderResponse(
        **{c.name: getattr(work_order, c.name) for c in work_order.__table__.columns},
        materials=[MaterialResponse.model_validate(m) for m in materials],
    )


@router.post("/{wo_id}/revert-finalize", response_model=WorkOrderResponse)
async def revert_work_order_finalization(
    wo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Revert a finalized work order back to editable state."""
    work_order, document = _get_wo_or_404(wo_id, db, current_user)

    if document.status != DocumentStatus.FINALIZED:
        raise HTTPException(status_code=400, detail="Work order is not finalized")

    work_order.status = WorkOrderStatus.PENDING
    document.status = DocumentStatus.REVIEW
    document.final_pdf_url = None

    db.commit()
    db.refresh(work_order)

    materials = (
        db.query(WorkOrderMaterial)
        .filter(WorkOrderMaterial.work_order_id == work_order.id)
        .order_by(WorkOrderMaterial.order)
        .all()
    )

    log_audit(
        db=db,
        user_id=current_user.id,
        action="revert_finalize",
        entity_type="work_order",
        entity_id=work_order.id,
        new_value={"status": "pending", "document_status": "review"},
    )

    return WorkOrderResponse(
        **{c.name: getattr(work_order, c.name) for c in work_order.__table__.columns},
        materials=[MaterialResponse.model_validate(m) for m in materials],
    )


# ─── Download PDF ────────────────────────────────────────────────────────────────

@router.get("/{wo_id}/download")
async def download_work_order_pdf(
    wo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download Work Order PDF — returns stored PDF or generates on-the-fly."""
    from fastapi.responses import Response
    from app.services.pdf_service import pdf_service

    work_order, document = _get_wo_or_404(wo_id, db, current_user)

    pdf_bytes = None
    backend_root = Path(__file__).resolve().parents[2]

    if document.final_pdf_url and document.final_pdf_url.startswith("/uploads/"):
        existing = backend_root / document.final_pdf_url.lstrip("/")
        if existing.exists():
            if existing.stat().st_size >= 10 * 1024:
                pdf_bytes = existing.read_bytes()

    if pdf_bytes is None:
        materials = (
            db.query(WorkOrderMaterial)
            .filter(WorkOrderMaterial.work_order_id == work_order.id)
            .order_by(WorkOrderMaterial.order)
            .all()
        )
        wo_pdf_data = _build_wo_pdf_data(work_order, document, materials, current_user)
        try:
            pdf_bytes = pdf_service.generate_work_order_pdf(wo_pdf_data)

            # Replace existing tiny/legacy PDF if a stored upload path exists.
            if document.final_pdf_url and document.final_pdf_url.startswith('/uploads/'):
                rewrite_path = backend_root / document.final_pdf_url.lstrip('/')
                rewrite_path.parent.mkdir(parents=True, exist_ok=True)
                rewrite_path.write_bytes(pdf_bytes)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate PDF: {str(e)}",
            )

    filename = f"wo_{document.document_number or wo_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
