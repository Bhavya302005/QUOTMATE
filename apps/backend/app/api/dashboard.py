from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.utils.auth import get_current_user
from app.models.user import User
from app.models.document import Document, DocumentType, DocumentStatus
from app.models.quotation import Quotation
from app.models.work_order import WorkOrder, WorkOrderStatus
from app.models.mom import MOM
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _month_range(base_date: datetime, months_back: int):
    """Return (start, end) UTC datetimes for a month N months before base_date."""
    # Roll back months_back months
    month = base_date.month - months_back
    year = base_date.year
    while month <= 0:
        month += 12
        year -= 1
    start = base_date.replace(year=year, month=month, day=1,
                               hour=0, minute=0, second=0, microsecond=0)
    # End = first day of following month
    end_month = start.month % 12 + 1
    end_year = start.year + (1 if start.month == 12 else 0)
    end = start.replace(year=end_year, month=end_month, day=1)
    return start, end


@router.get("")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_id = current_user.id
    now = datetime.utcnow()

    # ── Document counts grouped by type + status ──────────────────────────────
    type_totals: dict = {}
    status_breakdown: dict = {}
    
    # We will adjust counts to exclude orphaned documents
    q_count = db.query(Document.status, func.count(Quotation.id)).join(Quotation, Document.id == Quotation.document_id).filter(Document.user_id == user_id).group_by(Document.status).all()
    m_count = db.query(Document.status, func.count(MOM.id)).join(MOM, Document.id == MOM.document_id).filter(Document.user_id == user_id).group_by(Document.status).all()
    w_count = db.query(Document.status, func.count(WorkOrder.id)).join(WorkOrder, Document.id == WorkOrder.document_id).filter(Document.user_id == user_id).group_by(Document.status).all()

    for status, cnt in q_count:
        type_totals[DocumentType.QUOTATION] = type_totals.get(DocumentType.QUOTATION, 0) + cnt
        status_breakdown[f"{DocumentType.QUOTATION.value}_{status.value}"] = cnt
        
    for status, cnt in m_count:
        type_totals[DocumentType.MOM] = type_totals.get(DocumentType.MOM, 0) + cnt
        status_breakdown[f"{DocumentType.MOM.value}_{status.value}"] = cnt
        
    for status, cnt in w_count:
        type_totals[DocumentType.WORK_ORDER] = type_totals.get(DocumentType.WORK_ORDER, 0) + cnt
        status_breakdown[f"{DocumentType.WORK_ORDER.value}_{status.value}"] = cnt

    # ── All-time revenue (finalized quotations) ───────────────────────────────
    total_revenue = float(
        db.query(func.sum(Quotation.grand_total))
        .join(Document, Document.id == Quotation.document_id)
        .filter(
            Document.user_id == user_id,
            Document.status == DocumentStatus.FINALIZED,
        )
        .scalar()
        or 0
    )

    # ── Current-month revenue ─────────────────────────────────────────────────
    month_start, _ = _month_range(now, 0)
    monthly_revenue = float(
        db.query(func.sum(Quotation.grand_total))
        .join(Document, Document.id == Quotation.document_id)
        .filter(
            Document.user_id == user_id,
            Document.status == DocumentStatus.FINALIZED,
            Quotation.created_at >= month_start,
        )
        .scalar()
        or 0
    )

    # ── Work-order status breakdown ───────────────────────────────────────────
    wo_rows = (
        db.query(WorkOrder.status, func.count(WorkOrder.id).label("cnt"))
        .join(Document, Document.id == WorkOrder.document_id)
        .filter(Document.user_id == user_id)
        .group_by(WorkOrder.status)
        .all()
    )
    wo_by_status = {s.value: c for s, c in wo_rows}

    # ── 6-month revenue trend ─────────────────────────────────────────────────
    monthly_trend = []
    for i in range(5, -1, -1):
        m_start, m_end = _month_range(now, i)
        # For the current month extend end to now
        if i == 0:
            m_end = now
        rev = float(
            db.query(func.sum(Quotation.grand_total))
            .join(Document, Document.id == Quotation.document_id)
            .filter(
                Document.user_id == user_id,
                Document.status == DocumentStatus.FINALIZED,
                Quotation.created_at >= m_start,
                Quotation.created_at < m_end,
            )
            .scalar()
            or 0
        )
        monthly_trend.append({"month": m_start.strftime("%b %y"), "revenue": rev})

    # ── Recent 8 documents ────────────────────────────────────────────────────
    recent_docs = (
        db.query(Document)
        .filter(Document.user_id == user_id)
        .order_by(Document.created_at.desc())
        .limit(20) # Fetch more to account for orphaned documents being skipped
        .all()
    )

    recent = []
    for d in recent_docs:
        entity_id = None
        if d.document_type == DocumentType.QUOTATION:
            q = db.query(Quotation.id).filter(Quotation.document_id == d.id).first()
            if q: entity_id = q.id
        elif d.document_type == DocumentType.MOM:
            m = db.query(MOM.id).filter(MOM.document_id == d.id).first()
            if m: entity_id = m.id
        elif d.document_type == DocumentType.WORK_ORDER:
            w = db.query(WorkOrder.id).filter(WorkOrder.document_id == d.id).first()
            if w: entity_id = w.id
            
        if entity_id: # Only include if not orphaned
            recent.append({
                "id": entity_id,
                "document_id": d.id,
                "document_type": d.document_type.value,
                "document_number": d.document_number,
                "title": d.title,
                "status": d.status.value,
                "created_at": d.created_at.isoformat() if d.created_at else None,
            })
            if len(recent) == 8:
                break

    # ── Assemble response ─────────────────────────────────────────────────────
    return {
        "stats": {
            "total_documents": sum(type_totals.values()),
            "total_quotations": type_totals.get(DocumentType.QUOTATION, 0),
            "total_moms": type_totals.get(DocumentType.MOM, 0),
            "total_work_orders": type_totals.get(DocumentType.WORK_ORDER, 0),
            "total_revenue": total_revenue,
            "monthly_revenue": monthly_revenue,
        },
        "quotation_status": {
            "draft": status_breakdown.get("quotation_draft", 0),
            "finalized": status_breakdown.get("quotation_finalized", 0),
        },
        "work_order_status": {
            "pending": wo_by_status.get("pending", 0),
            "in_progress": wo_by_status.get("in_progress", 0),
            "completed": wo_by_status.get("completed", 0),
            "cancelled": wo_by_status.get("cancelled", 0),
        },
        "monthly_trend": monthly_trend,
        "recent_documents": recent,
    }
