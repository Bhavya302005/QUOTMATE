"""PDF generation service with graceful fallback when WeasyPrint is unavailable."""

from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import io
from urllib.parse import urlparse

# Apple Silicon Mac compatibility fix for Homebrew installed libraries
import platform
import os
if platform.system() == "Darwin" and platform.machine() == "arm64":
    # Ensure WeasyPrint's cffi can find libraries in /opt/homebrew/lib
    fallback = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "")
    if "/opt/homebrew/lib" not in fallback:
        os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = f"/opt/homebrew/lib:{fallback}".strip(":")

try:
    from weasyprint import HTML, CSS
    _WEASYPRINT_AVAILABLE = True
    _WEASYPRINT_IMPORT_ERROR = None
except Exception as exc:  # pragma: no cover - depends on host system libs
    HTML = None
    CSS = None
    _WEASYPRINT_AVAILABLE = False
    _WEASYPRINT_IMPORT_ERROR = exc

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    _REPORTLAB_AVAILABLE = True
except Exception:
    canvas = None
    A4 = None
    _REPORTLAB_AVAILABLE = False


class PDFService:
    """Service for generating PDFs from HTML templates"""
    
    def __init__(self):
        """Initialize PDF service with template loader"""
        # Get the templates directory path
        template_dir = Path(__file__).parent.parent / 'templates'
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))
        
        # Optional: Custom CSS can be added here
        self.custom_css = (
            CSS(string='''
                @page {
                    size: A4;
                    margin: 1.5cm;
                }
            ''')
            if _WEASYPRINT_AVAILABLE
            else None
        )

    def _render_html_pdf(self, html_content: str) -> bytes:
        """Render HTML to PDF using WeasyPrint if available."""
        if not _WEASYPRINT_AVAILABLE:
            raise RuntimeError(f"WeasyPrint unavailable: {_WEASYPRINT_IMPORT_ERROR}")
        return HTML(string=html_content).write_pdf()

    def _resolve_public_asset_url(self, value: Optional[str]) -> Optional[str]:
        """Convert relative API asset paths into absolute URLs for template rendering."""
        if not value:
            return None
        if value.startswith('data:'):
            return value

        # If logo is stored as an absolute URL, extract uploads path when possible.
        if value.startswith('http://') or value.startswith('https://'):
            parsed = urlparse(value)
            if parsed.path.startswith('/uploads/'):
                value = parsed.path
            else:
                return value

        # Prefer local file URI for uploaded assets so PDF rendering does not depend on HTTP fetch.
        if value.startswith('/uploads/'):
            backend_root = Path(__file__).resolve().parents[2]
            local_path = backend_root / value.lstrip('/')
            if local_path.exists():
                return local_path.resolve().as_uri()

        base_url = os.getenv("BACKEND_PUBLIC_URL", "http://localhost:8000").rstrip('/')
        normalized = value if value.startswith('/') else f"/{value}"
        return f"{base_url}{normalized}"

    def _generate_fallback_pdf(self, title: str, lines: list[str]) -> bytes:
        """Generate a simple, readable PDF using ReportLab as fallback."""
        if not _REPORTLAB_AVAILABLE:
            raise RuntimeError(
                "PDF renderer unavailable. Install ReportLab or system libs required by WeasyPrint."
            )

        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        page_width, page_height = A4

        y = page_height - 40
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(40, y, title)
        y -= 24

        pdf.setFont("Helvetica", 10)
        for line in lines:
            text = (line or "").strip()
            if not text:
                y -= 8
                continue
            # Wrap long lines into chunks to avoid clipping.
            while len(text) > 110:
                chunk = text[:110]
                pdf.drawString(40, y, chunk)
                y -= 14
                text = text[110:]
                if y < 40:
                    pdf.showPage()
                    pdf.setFont("Helvetica", 10)
                    y = page_height - 40
            pdf.drawString(40, y, text)
            y -= 14
            if y < 40:
                pdf.showPage()
                pdf.setFont("Helvetica", 10)
                y = page_height - 40

        pdf.save()
        return buffer.getvalue()
    
    def generate_quotation_pdf(
        self, 
        quotation_data: Dict,
        user_data: Dict,
        items: list
    ) -> bytes:
        """
        Generate quotation PDF from data
        
        Args:
            quotation_data: Quotation details dict
            user_data: User/company details dict
            items: List of quotation items
        
        Returns:
            PDF as bytes
        """
        template = self.env.get_template('quotation.html')
        
        # Prepare template context
        context = {
            # Company/User Info
            'company_name': user_data.get('company_name') or user_data.get('full_name'),
            'company_address': user_data.get('address'),
            'company_phone': user_data.get('phone'),
            'company_email': user_data.get('email'),
            'company_gst': user_data.get('gst_number'),
            'company_logo': self._resolve_public_asset_url(user_data.get('company_logo_url')),
            'user_full_name': user_data.get('full_name'),
            
            # Quotation Info
            'quotation_number': quotation_data.get('document_number'),
            'quotation_status': quotation_data.get('status') or 'draft',
            'generated_date': datetime.now().strftime('%Y-%m-%d'),
            'valid_until': quotation_data.get('valid_until').strftime('%d-%m-%Y') if quotation_data.get('valid_until') else None,
            
            # Customer Info
            'customer_name': quotation_data.get('customer_name'),
            'customer_email': quotation_data.get('customer_email'),
            'customer_phone': quotation_data.get('customer_phone'),
            'customer_address': quotation_data.get('customer_address'),
            'customer_gst': quotation_data.get('customer_gst'),
            
            # Items
            'items': items,
            
            # Totals
            'subtotal': float(quotation_data.get('subtotal', 0)),
            'discount_percent': float(quotation_data.get('discount_percent', 0)),
            'discount_amount': float(quotation_data.get('discount_amount', 0)),
            'cgst_amount': float(quotation_data.get('cgst_amount', 0)),
            'sgst_amount': float(quotation_data.get('sgst_amount', 0)),
            'igst_amount': float(quotation_data.get('igst_amount', 0)),
            'grand_total': float(quotation_data.get('grand_total', 0)),
            
            # Calculate GST rates (reverse calculate from amounts)
            'cgst_rate': self._calculate_rate(
                quotation_data.get('cgst_amount', 0),
                quotation_data.get('subtotal', 0) - quotation_data.get('discount_amount', 0)
            ),
            'sgst_rate': self._calculate_rate(
                quotation_data.get('sgst_amount', 0),
                quotation_data.get('subtotal', 0) - quotation_data.get('discount_amount', 0)
            ),
            'igst_rate': self._calculate_rate(
                quotation_data.get('igst_amount', 0),
                quotation_data.get('subtotal', 0) - quotation_data.get('discount_amount', 0)
            ),
            
            # Additional Info
            'terms_conditions': quotation_data.get('terms_conditions'),
            'notes': quotation_data.get('notes'),
            
            # Feature Flags
            'is_gst_on': quotation_data.get('is_gst_on', True),
            'manual_total_amount': float(quotation_data.get('manual_total_amount')) if quotation_data.get('manual_total_amount') is not None else None,
        }
        
        # Render HTML
        html_content = template.render(**context)
        
        try:
            return self._render_html_pdf(html_content)
        except Exception as e:
            print(f"WeasyPrint failed to render quotation pdf: {str(e)}")
            import traceback
            traceback.print_exc()
            fallback_lines = [
                f"Quotation No: {context.get('quotation_number') or '-'}",
                f"Generated: {context.get('generated_date')}",
                f"Customer: {context.get('customer_name') or '-'}",
                f"Phone: {context.get('customer_phone') or '-'}",
                f"Email: {context.get('customer_email') or '-'}",
                "",
                "Items:",
            ]
            for idx, item in enumerate(items, start=1):
                fallback_lines.append(
                    f"{idx}. {item.get('description', '-')}: qty {item.get('quantity', 0)} x "
                    f"{item.get('unit_price', 0)} = {item.get('total', 0)}"
                )
            fallback_lines.extend(
                [
                    "",
                    f"Subtotal: {context.get('subtotal', 0)}",
                    f"Discount: {context.get('discount_amount', 0)}",
                    f"CGST: {context.get('cgst_amount', 0)}",
                    f"SGST: {context.get('sgst_amount', 0)}",
                    f"IGST: {context.get('igst_amount', 0)}",
                    f"Grand Total: {context.get('grand_total', 0)}",
                ]
            )
            return self._generate_fallback_pdf("Quotation", fallback_lines)
    
    def generate_mom_pdf(self, mom_data: Dict) -> bytes:
        """
        Generate Minutes of Meeting PDF
        
        Args:
            mom_data: MOM details dict
        
        Returns:
            PDF as bytes
        """
        template = self.env.get_template('mom.html')

        meeting_date = mom_data.get('meeting_date')
        meeting_time = mom_data.get('meeting_time')

        if hasattr(meeting_date, "strftime"):
            meeting_date = meeting_date.strftime('%d-%m-%Y')
        else:
            meeting_date = meeting_date or "-"

        if hasattr(meeting_time, "strftime"):
            meeting_time = meeting_time.strftime('%I:%M %p')
        else:
            meeting_time = meeting_time or "-"

        context = {
            "mom_number": mom_data.get('mom_number'),
            "generated_date": datetime.now().strftime('%d-%m-%Y'),
            "meeting_title": mom_data.get('meeting_title') or "Minutes of Meeting",
            "meeting_date": meeting_date,
            "meeting_time": meeting_time,
            "location": mom_data.get('location') or "-",
            "attendees": mom_data.get('attendees') or [],
            "summary": mom_data.get('summary') or "No summary available.",
            "key_points": mom_data.get('key_points') or [],
            "decisions": mom_data.get('decisions') or [],
            "next_steps": mom_data.get('next_steps') or [],
            "action_items": mom_data.get('action_items') or [],
            "raw_notes": mom_data.get('raw_notes') or "",
            "company_name": mom_data.get('company_name'),
            "company_email": mom_data.get('company_email'),
            "company_phone": mom_data.get('company_phone'),
        }

        html_content = template.render(**context)
        try:
            return self._render_html_pdf(html_content)
        except Exception:
            fallback_lines = [
                f"MOM No: {context.get('mom_number') or '-'}",
                f"Generated: {context.get('generated_date')}",
                f"Meeting: {context.get('meeting_title') or '-'}",
                f"Date: {context.get('meeting_date')}",
                f"Time: {context.get('meeting_time')}",
                f"Location: {context.get('location')}",
                "",
                "Summary:",
                context.get('summary') or '-',
                "",
                "Action Items:",
            ]
            for idx, item in enumerate(context.get('action_items') or [], start=1):
                fallback_lines.append(
                    f"{idx}. {item.get('task', '-')}, owner: {item.get('assigned_to', '-')}, due: {item.get('due_date', '-')}"
                )
            return self._generate_fallback_pdf("Minutes of Meeting", fallback_lines)
    
    def generate_work_order_pdf(self, work_order_data: Dict) -> bytes:
        """
        Generate Work Order PDF
        
        Args:
            work_order_data: Work order details dict
        
        Returns:
            PDF as bytes
        """
        # To be implemented in Week 7
        template = self.env.get_template('work_order.html')
        html_content = template.render(**work_order_data)
        try:
            return self._render_html_pdf(html_content)
        except Exception:
            fallback_lines = [
                f"Work Order: {work_order_data.get('work_order_number') or '-'}",
                f"Client: {work_order_data.get('client_name') or '-'}",
                f"Phone: {work_order_data.get('client_phone') or '-'}",
                f"Location: {work_order_data.get('service_location') or '-'}",
                f"Assigned To: {work_order_data.get('assigned_to') or '-'}",
                f"Start: {work_order_data.get('start_date') or '-'}",
                f"End: {work_order_data.get('end_date') or '-'}",
                "",
                "Work Description:",
                work_order_data.get('work_description') or '-',
                "",
                f"Labor Cost: {work_order_data.get('labor_cost') or 0}",
                f"Material Cost: {work_order_data.get('material_cost') or 0}",
                f"Total Cost: {work_order_data.get('total_cost') or 0}",
            ]
            return self._generate_fallback_pdf("Work Order", fallback_lines)
    
    def _calculate_rate(self, amount: float, base: float) -> float:
        """Calculate percentage rate from amount and base"""
        if base <= 0:
            return 0.0
        return round((float(amount) / float(base)) * 100, 2)
    
    def save_pdf_to_file(self, pdf_bytes: bytes, filepath: str) -> str:
        """
        Save PDF bytes to file
        
        Args:
            pdf_bytes: PDF content as bytes
            filepath: Path where to save the file
        
        Returns:
            Filepath where PDF was saved
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'wb') as f:
            f.write(pdf_bytes)
        
        return filepath


# Singleton instance
pdf_service = PDFService()
