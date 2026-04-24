from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.session import get_db
from app.models.user import User
from app.models.document import Document, DocumentType, DocumentStatus
from app.models.quotation import Quotation, QuotationItem
from app.schemas.quotation import (
    QuotationCreate,
    QuotationUpdate,
    QuotationResponse,
    QuotationListResponse,
    QuotationItemResponse,
    GSTCalculationRequest,
    GSTCalculationResponse,
    OCRToQuotationRequest,
    OCRToQuotationResponse
)
from app.utils.auth import get_current_user
from app.services.audit_service import log_audit
from app.services.gst_calculator import gst_calculator
from app.services.quotation_mapper import quotation_mapper
from typing import Optional
from datetime import datetime
from pathlib import Path
import uuid
import math

router = APIRouter(prefix="/api/quotations", tags=["Quotations"])


@router.post("/calculate", response_model=GSTCalculationResponse)
async def calculate_gst(
    calculation_data: GSTCalculationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Calculate GST for given items without saving
    
    Useful for previewing totals before creating quotation
    
    - **items**: List of items with quantity, unit_price, gst_rate
    - **discount_percent**: Discount percentage on subtotal
    - **is_igst**: Use IGST (inter-state) instead of CGST+SGST
    """
    # Convert Pydantic models to dicts for calculator
    items_data = [item.model_dump() for item in calculation_data.items]
    
    # Calculate
    result = gst_calculator.calculate(
        items=items_data,
        is_igst=calculation_data.is_igst,
        discount_percent=float(calculation_data.discount_percent),
        is_gst_on=calculation_data.is_gst_on,
        manual_total_amount=float(calculation_data.manual_total_amount) if calculation_data.manual_total_amount is not None else None
    )
    
    return GSTCalculationResponse(**result)


@router.post("/from-ocr", response_model=OCRToQuotationResponse)
async def map_ocr_to_quotation(
    ocr_data: OCRToQuotationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Map OCR extracted text to quotation fields
    
    Returns suggested fields with confidence flags for fields that need review
    
    - **ocr_text**: Raw text from OCR extraction
    - **document_id**: Document ID to associate with quotation (optional, will auto-create)
    """
    # Auto-create document if not provided
    document = None
    if ocr_data.document_id:
        # Verify document exists and belongs to user
        document = db.query(Document).filter(
            Document.id == ocr_data.document_id,
            Document.user_id == current_user.id
        ).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
    else:
        # Create a new document
        document = Document(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            document_type=DocumentType.QUOTATION,
            status=DocumentStatus.DRAFT,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(document)
        db.commit()
        db.refresh(document)
    
    # Map OCR text to quotation fields
    mapped_data = quotation_mapper.map_text_to_quotation(ocr_data.ocr_text)
    
    # Create suggested quotation if we have minimum data
    suggested_quotation = None
    if mapped_data['customer_name'] and len(mapped_data['items']) > 0:
        try:
            suggested_quotation = QuotationCreate(
                document_id=document.id,
                customer_name=mapped_data['customer_name'],
                customer_email=mapped_data.get('customer_email'),
                customer_phone=mapped_data.get('customer_phone'),
                customer_address=mapped_data.get('customer_address'),
                customer_gst=mapped_data.get('customer_gst'),
                discount_percent=mapped_data.get('discount_percent', 0),
                items=mapped_data['items'],
                is_igst=False,
                is_gst_on=True
            )
        except Exception:
            pass
    
    return OCRToQuotationResponse(
        **mapped_data,
        document_id=document.id,
        suggested_quotation=suggested_quotation
    )


@router.post("", response_model=QuotationResponse, status_code=status.HTTP_201_CREATED)
async def create_quotation(
    quotation_data: QuotationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new quotation with line items
    
    - **document_id**: Associated document ID (optional - will auto-create if not provided)
    - **customer_name**: Customer name (required)
    - **items**: List of line items (at least 1 required)
    - **is_igst**: Whether to use IGST (inter-state) tax
    - **discount_percent**: Discount on subtotal
    
    Automatically calculates GST and totals
    """
    # Verify or create document
    if quotation_data.document_id:
        # Verify document exists and belongs to user
        document = db.query(Document).filter(
            Document.id == quotation_data.document_id,
            Document.user_id == current_user.id
        ).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
    else:
        # Auto-create document for this quotation
        document_id = str(uuid.uuid4())
        
        # Generate document number (e.g., QUOT-0001)
        # Count existing quotation documents for this user
        existing_count = db.query(Document).filter(
            Document.user_id == current_user.id,
            Document.document_type == DocumentType.QUOTATION
        ).count()
        
        document_number = f"QUOT-{existing_count + 1:04d}"
        
        document = Document(
            id=document_id,
            user_id=current_user.id,
            document_type=DocumentType.QUOTATION,
            document_number=document_number,
            title=f"Quotation for {quotation_data.customer_name}",
            status=DocumentStatus.DRAFT
        )
        db.add(document)
        quotation_data.document_id = document_id
    
    # Calculate GST
    items_data = [item.model_dump() for item in quotation_data.items]
    calculation = gst_calculator.calculate(
        items=items_data,
        is_igst=quotation_data.is_igst,
        discount_percent=float(quotation_data.discount_percent),
        is_gst_on=quotation_data.is_gst_on,
        manual_total_amount=float(quotation_data.manual_total_amount) if quotation_data.manual_total_amount is not None else None
    )
    
    # Create quotation
    quotation_id = str(uuid.uuid4())
    quotation = Quotation(
        id=quotation_id,
        document_id=quotation_data.document_id,
        customer_name=quotation_data.customer_name,
        customer_email=quotation_data.customer_email,
        customer_phone=quotation_data.customer_phone,
        customer_address=quotation_data.customer_address,
        customer_gst=quotation_data.customer_gst,
        subtotal=calculation['subtotal'],
        cgst_amount=calculation['cgst_amount'],
        sgst_amount=calculation['sgst_amount'],
        igst_amount=calculation['igst_amount'],
        discount_percent=calculation['discount_percent'],
        discount_amount=calculation['discount_amount'],
        is_gst_on=quotation_data.is_gst_on,
        manual_total_amount=quotation_data.manual_total_amount,
        grand_total=calculation['grand_total'],
        valid_until=quotation_data.valid_until,
        terms_conditions=quotation_data.terms_conditions,
        notes=quotation_data.notes
    )
    
    db.add(quotation)
    
    # Create line items
    for calc_item in calculation['items']:
        item = QuotationItem(
            id=str(uuid.uuid4()),
            quotation_id=quotation_id,
            product_id=calc_item.get('product_id'),
            item_order=calc_item['item_order'],
            description=calc_item['description'],
            quantity=calc_item['quantity'],
            unit=calc_item['unit'],
            unit_price=calc_item['unit_price'],
            gst_rate=calc_item['gst_rate'],
            gst_amount=calc_item['gst_amount'],
            total=calc_item['total'],
            is_free_text=calc_item.get('is_free_text', False)
        )
        db.add(item)
    
    # Update document status
    document.status = DocumentStatus.REVIEW
    
    db.commit()
    db.refresh(quotation)
    
    # Load items for response
    quotation.items = db.query(QuotationItem).filter(
        QuotationItem.quotation_id == quotation_id
    ).order_by(QuotationItem.item_order).all()
    
    # Load document info (status and quotation_number)
    quotation.status = document.status.value  # Convert enum to string
    quotation.quotation_number = document.document_number
    
    # Audit log
    log_audit(
        db=db,
        user_id=current_user.id,
        action="quotation.created",
        entity_type="quotation",
        entity_id=quotation.id,
        new_value={
            "customer": quotation.customer_name,
            "grand_total": float(quotation.grand_total),
            "items_count": len(quotation.items)
        }
    )
    
    return quotation


@router.get("", response_model=QuotationListResponse)
async def list_quotations(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(default=None, description="Search in customer name"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all quotations for the current user with pagination
    
    - **page**: Page number (starts from 1)
    - **page_size**: Number of items per page (max 100)
    - **search**: Search query for customer name
    """
    # Build query with join to documents
    query = db.query(Quotation).join(
        Document, Quotation.document_id == Document.id
    ).filter(Document.user_id == current_user.id)
    
    # Apply search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(Quotation.customer_name.like(search_pattern))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    quotations = query.order_by(Quotation.created_at.desc()).offset(offset).limit(page_size).all()
    
    # Load items and document info for each quotation
    for quotation in quotations:
        quotation.items = db.query(QuotationItem).filter(
            QuotationItem.quotation_id == quotation.id
        ).order_by(QuotationItem.item_order).all()
        
        # Load document info (status and quotation_number)
        document = db.query(Document).filter(Document.id == quotation.document_id).first()
        if document:
            quotation.status = document.status.value  # Convert enum to string
            quotation.quotation_number = document.document_number
    
    # Calculate total pages
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    
    return QuotationListResponse(
        quotations=quotations,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{quotation_id}", response_model=QuotationResponse)
async def get_quotation(
    quotation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific quotation by ID with all line items"""
    # Query with join to verify ownership
    quotation = db.query(Quotation).join(
        Document, Quotation.document_id == Document.id
    ).filter(
        Quotation.id == quotation_id,
        Document.user_id == current_user.id
    ).first()
    
    if not quotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quotation not found"
        )
    
    # Load items
    quotation.items = db.query(QuotationItem).filter(
        QuotationItem.quotation_id == quotation_id
    ).order_by(QuotationItem.item_order).all()
    
    # Load document info (status and quotation_number)
    document = db.query(Document).filter(Document.id == quotation.document_id).first()
    if document:
        quotation.status = document.status.value  # Convert enum to string
        quotation.quotation_number = document.document_number
    
    return quotation


@router.put("/{quotation_id}", response_model=QuotationResponse)
async def update_quotation(
    quotation_id: str,
    quotation_data: QuotationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing quotation
    
    If items are provided, recalculates GST and totals
    """
    # Find quotation with ownership check
    quotation = db.query(Quotation).join(
        Document, Quotation.document_id == Document.id
    ).filter(
        Quotation.id == quotation_id,
        Document.user_id == current_user.id
    ).first()
    
    if not quotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quotation not found"
        )
    
    # Store old values for audit
    old_values = {
        "customer": quotation.customer_name,
        "grand_total": float(quotation.grand_total)
    }
    
    # If items are updated, recalculate
    if quotation_data.items is not None:
        items_data = [item.model_dump() for item in quotation_data.items]
        is_igst = quotation_data.is_igst if quotation_data.is_igst is not None else (quotation.igst_amount > 0)
        discount = float(quotation_data.discount_percent) if quotation_data.discount_percent is not None else float(quotation.discount_percent)
        is_gst_on = quotation_data.is_gst_on if quotation_data.is_gst_on is not None else quotation.is_gst_on
        
        # Only override manual_total_amount if explicitly passed, otherwise use existing
        manual_total_amount = float(quotation_data.manual_total_amount) if quotation_data.manual_total_amount is not None else (float(quotation.manual_total_amount) if quotation.manual_total_amount is not None else None)
        
        calculation = gst_calculator.calculate(
            items=items_data,
            is_igst=is_igst,
            discount_percent=discount,
            is_gst_on=is_gst_on,
            manual_total_amount=manual_total_amount
        )
        
        # Delete old items
        db.query(QuotationItem).filter(QuotationItem.quotation_id == quotation_id).delete()
        
        # Create new items
        for calc_item in calculation['items']:
            item = QuotationItem(
                id=str(uuid.uuid4()),
                quotation_id=quotation_id,
                product_id=calc_item.get('product_id'),
                item_order=calc_item['item_order'],
                description=calc_item['description'],
                quantity=calc_item['quantity'],
                unit=calc_item['unit'],
                unit_price=calc_item['unit_price'],
                gst_rate=calc_item['gst_rate'],
                gst_amount=calc_item['gst_amount'],
                total=calc_item['total'],
                is_free_text=calc_item.get('is_free_text', False)
            )
            db.add(item)
        
        # Update totals
        quotation.subtotal = calculation['subtotal']
        quotation.cgst_amount = calculation['cgst_amount']
        quotation.sgst_amount = calculation['sgst_amount']
        quotation.igst_amount = calculation['igst_amount']
        quotation.discount_percent = calculation['discount_percent']
        quotation.discount_amount = calculation['discount_amount']
        quotation.is_gst_on = is_gst_on
        if quotation_data.manual_total_amount is not None:
            quotation.manual_total_amount = quotation_data.manual_total_amount
        quotation.grand_total = calculation['grand_total']
    
    # Update other fields
    update_data = quotation_data.model_dump(exclude={'items', 'is_igst', 'is_gst_on', 'manual_total_amount'}, exclude_unset=True)
    for field, value in update_data.items():
        setattr(quotation, field, value)
    
    db.commit()
    db.refresh(quotation)
    
    # Load items
    quotation.items = db.query(QuotationItem).filter(
        QuotationItem.quotation_id == quotation_id
    ).order_by(QuotationItem.item_order).all()
    
    # Load document info (status and quotation_number)
    document = db.query(Document).filter(Document.id == quotation.document_id).first()
    if document:
        quotation.status = document.status.value  # Convert enum to string
        quotation.quotation_number = document.document_number
    
    # Audit log
    new_values = {
        "customer": quotation.customer_name,
        "grand_total": float(quotation.grand_total)
    }
    log_audit(
        db=db,
        user_id=current_user.id,
        action="quotation.updated",
        entity_type="quotation",
        entity_id=quotation.id,
        old_value=old_values,
        new_value=new_values
    )
    
    return quotation


@router.delete("/{quotation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quotation(
    quotation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a quotation and all its line items"""
    # Find quotation with ownership check
    quotation = db.query(Quotation).join(
        Document, Quotation.document_id == Document.id
    ).filter(
        Quotation.id == quotation_id,
        Document.user_id == current_user.id
    ).first()
    
    if not quotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quotation not found"
        )
    
    # Audit log
    log_audit(
        db=db,
        user_id=current_user.id,
        action="quotation.deleted",
        entity_type="quotation",
        entity_id=quotation.id,
        old_value={"customer": quotation.customer_name, "grand_total": float(quotation.grand_total)}
    )
    
    # Delete quotation (items will be cascade deleted)
    db.delete(quotation)
    db.commit()
    
    return None


@router.post("/{quotation_id}/finalize", response_model=QuotationResponse)
async def finalize_quotation(
    quotation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Finalize a quotation - generates PDF and updates document status
    
    - Changes document status to 'finalized'
    - Generates PDF and saves URL to document
    - Returns updated quotation
    """
    from app.services.pdf_service import pdf_service
    from app.utils.file_upload import file_upload_service
    import uuid as uuid_lib
    
    # Find quotation with ownership check
    quotation = db.query(Quotation).join(
        Document, Quotation.document_id == Document.id
    ).filter(
        Quotation.id == quotation_id,
        Document.user_id == current_user.id
    ).first()
    
    if not quotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quotation not found"
        )
    
    # Get document
    document = db.query(Document).filter(Document.id == quotation.document_id).first()
    
    # Load items
    items = db.query(QuotationItem).filter(
        QuotationItem.quotation_id == quotation_id
    ).order_by(QuotationItem.item_order).all()
    
    if len(items) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot finalize quotation without items"
        )
    
    # Prepare data for PDF generation
    quotation_dict = {
        'document_number': document.document_number,
        'customer_name': quotation.customer_name,
        'customer_email': quotation.customer_email,
        'customer_phone': quotation.customer_phone,
        'customer_address': quotation.customer_address,
        'customer_gst': quotation.customer_gst,
        'subtotal': quotation.subtotal,
        'cgst_amount': quotation.cgst_amount,
        'sgst_amount': quotation.sgst_amount,
        'igst_amount': quotation.igst_amount,
        'discount_percent': quotation.discount_percent,
        'discount_amount': quotation.discount_amount,
        'is_gst_on': quotation.is_gst_on,
        'manual_total_amount': quotation.manual_total_amount,
        'grand_total': quotation.grand_total,
        'valid_until': quotation.valid_until,
        'terms_conditions': quotation.terms_conditions,
        'notes': quotation.notes
    }
    
    user_dict = {
        'full_name': current_user.full_name,
        'company_name': current_user.company_name,
        'email': current_user.email,
        'phone': current_user.phone,
        'address': current_user.address,
        'gst_number': current_user.gst_number,
        'company_logo_url': current_user.company_logo_url
    }
    
    items_list = [
        {
            'description': item.description,
            'quantity': float(item.quantity),
            'unit': item.unit,
            'unit_price': float(item.unit_price),
            'gst_rate': float(item.gst_rate),
            'gst_amount': float(item.gst_amount),
            'total': float(item.total)
        }
        for item in items
    ]
    
    # Generate PDF
    try:
        pdf_bytes = pdf_service.generate_quotation_pdf(
            quotation_data=quotation_dict,
            user_data=user_dict,
            items=items_list
        )
        
        # Save PDF to local storage
        pdf_filename = f"quotation_{document.document_number}_{uuid_lib.uuid4().hex[:8]}.pdf"
        pdf_dir = Path("uploads/documents")
        pdf_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = pdf_dir / pdf_filename
        
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        
        # Update document with PDF URL
        pdf_url = f"/uploads/documents/{pdf_filename}"
        document.final_pdf_url = pdf_url
        document.status = DocumentStatus.FINALIZED
        
        db.commit()
        db.refresh(quotation)
        
        # Load items for response
        quotation.items = items
        
        # Audit log
        log_audit(
            db=db,
            user_id=current_user.id,
            action="quotation.finalized",
            entity_type="quotation",
            entity_id=quotation.id,
            new_value={"pdf_url": pdf_url, "status": "finalized"}
        )
        
        return quotation
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF: {str(e)}"
        )


@router.post("/{quotation_id}/revert-finalize", response_model=QuotationResponse)
async def revert_quotation_finalization(
    quotation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revert a finalized quotation back to review state so it can be edited again."""
    quotation = db.query(Quotation).join(
        Document, Quotation.document_id == Document.id
    ).filter(
        Quotation.id == quotation_id,
        Document.user_id == current_user.id
    ).first()

    if not quotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quotation not found"
        )

    document = db.query(Document).filter(Document.id == quotation.document_id).first()
    if document.status != DocumentStatus.FINALIZED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quotation is not finalized"
        )

    document.status = DocumentStatus.REVIEW
    document.final_pdf_url = None
    db.commit()

    quotation.items = db.query(QuotationItem).filter(
        QuotationItem.quotation_id == quotation_id
    ).order_by(QuotationItem.item_order).all()

    log_audit(
        db=db,
        user_id=current_user.id,
        action="quotation.finalization_reverted",
        entity_type="quotation",
        entity_id=quotation.id,
        new_value={"status": "review"}
    )

    return quotation


@router.get("/{quotation_id}/download")
async def download_quotation_pdf(
    quotation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download quotation PDF generated from the latest template.
    """
    from fastapi.responses import Response
    from app.services.pdf_service import pdf_service
    from pathlib import Path
    
    # Find quotation with ownership check
    quotation = db.query(Quotation).join(
        Document, Quotation.document_id == Document.id
    ).filter(
        Quotation.id == quotation_id,
        Document.user_id == current_user.id
    ).first()
    
    if not quotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quotation not found"
        )
    
    # Get document
    document = db.query(Document).filter(Document.id == quotation.document_id).first()
    
    backend_root = Path(__file__).resolve().parents[2]

    # Always generate from latest template so downloaded PDF matches preview theme.
    items = db.query(QuotationItem).filter(
        QuotationItem.quotation_id == quotation_id
    ).order_by(QuotationItem.item_order).all()

    if len(items) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot generate PDF for quotation without items"
        )

    quotation_dict = {
        'document_number': document.document_number,
        'customer_name': quotation.customer_name,
        'customer_email': quotation.customer_email,
        'customer_phone': quotation.customer_phone,
        'customer_address': quotation.customer_address,
        'customer_gst': quotation.customer_gst,
        'subtotal': quotation.subtotal,
        'cgst_amount': quotation.cgst_amount,
        'sgst_amount': quotation.sgst_amount,
        'igst_amount': quotation.igst_amount,
        'discount_percent': quotation.discount_percent,
        'discount_amount': quotation.discount_amount,
        'is_gst_on': quotation.is_gst_on,
        'manual_total_amount': quotation.manual_total_amount,
        'grand_total': quotation.grand_total,
        'valid_until': quotation.valid_until,
        'terms_conditions': quotation.terms_conditions,
        'notes': quotation.notes,
        'status': document.status.value if document.status else 'draft',
    }

    user_dict = {
        'full_name': current_user.full_name,
        'company_name': current_user.company_name,
        'email': current_user.email,
        'phone': current_user.phone,
        'address': current_user.address,
        'gst_number': current_user.gst_number,
        'company_logo_url': current_user.company_logo_url,
    }

    items_list = [
        {
            'description': item.description,
            'quantity': float(item.quantity),
            'unit': item.unit,
            'unit_price': float(item.unit_price),
            'gst_rate': float(item.gst_rate),
            'gst_amount': float(item.gst_amount),
            'total': float(item.total),
        }
        for item in items
    ]

    try:
        pdf_bytes = pdf_service.generate_quotation_pdf(
            quotation_data=quotation_dict,
            user_data=user_dict,
            items=items_list,
        )

        # Update stored file too, so future finalized references keep same visual style.
        if document.final_pdf_url and document.final_pdf_url.startswith('/uploads/'):
            rewrite_path = backend_root / document.final_pdf_url.lstrip('/')
            rewrite_path.parent.mkdir(parents=True, exist_ok=True)
            with open(rewrite_path, 'wb') as f:
                f.write(pdf_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF: {str(e)}"
        )
    
    # Return PDF
    filename = f"quotation_{document.document_number or quotation_id}.pdf"
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
