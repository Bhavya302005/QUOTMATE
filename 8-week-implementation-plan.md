# SMART BUSINESS DOCUMENT GENERATOR
## 8-Week Implementation Plan
### SGP Project - Comprehensive Development Guide

---

# PROJECT OVERVIEW

## Team Structure
| Role | Responsibilities | Hours/Week |
|------|------------------|------------|
| **Developer 1 (You)** | Backend, Database, OCR, AI Integration, Deployment | 4-8 hrs |
| **Developer 2** | Frontend (React), UI/UX, Mobile Responsiveness | 4-8 hrs |

**Total Available Hours:** 64-128 hours over 8 weeks (per person)

## Technology Stack (Finalized)

| Layer | Technology |
|-------|------------|
| **Frontend** | React.js + Tailwind CSS (Mobile-First) |
| **Backend** | Python + FastAPI |
| **Database** | MySQL |
| **OCR** | Google Cloud Vision API (Handwritten English) |
| **AI** | NVIDIA NIMs + Llama 3.1 (Latest) |
| **PDF** | WeasyPrint |
| **Storage** | AWS S3 / Cloudinary |
| **Deployment** | Railway (Backend) + Vercel (Frontend) |

## Priority Order (Based on Requirements)
```
🥇 Priority 1: Quotation Module (CRITICAL - Must Have)
🥈 Priority 2: Authentication + User Management
🥉 Priority 3: MOM Module with AI Summarization
4️⃣ Priority 4: Work Order Module
5️⃣ Priority 5: Dashboard & Document Management
```

---

# WEEK-BY-WEEK IMPLEMENTATION PLAN

---

## 📅 WEEK 1: Foundation & Setup
**Theme:** "Get the foundation rock solid"

### Your Tasks (Backend - 6-8 hrs)

| Day | Task | Hours | Deliverable |
|-----|------|-------|-------------|
| Day 1-2 | Project setup, GitHub repo, folder structure | 2 | Repository ready |
| Day 2-3 | FastAPI project initialization | 1.5 | Basic API running |
| Day 3-4 | MySQL database setup + SQLAlchemy config | 2 | DB connected |
| Day 4-5 | Design & create database schema (Users, Documents, Quotations) | 2.5 | Tables created |

### Frontend Tasks (Partner - 6-8 hrs)

| Day | Task | Hours | Deliverable |
|-----|------|-------|-------------|
| Day 1-2 | React project setup with Tailwind | 2 | Project initialized |
| Day 2-3 | Mobile-first layout structure | 2 | Base layout ready |
| Day 3-4 | Login/Register UI screens | 2 | Auth pages ready |
| Day 4-5 | Dashboard UI skeleton | 2 | Dashboard shell |

### Database Schema (Week 1)

```sql
-- Users Table
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    company_name VARCHAR(200),
    company_logo_url VARCHAR(500),
    phone VARCHAR(20),
    address TEXT,
    gst_number VARCHAR(20),
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Audit Logs Table
CREATE TABLE audit_logs (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36),
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50),
    entity_id VARCHAR(36),
    old_value JSON,
    new_value JSON,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Documents Table (Base for all document types)
CREATE TABLE documents (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    document_type ENUM('quotation', 'mom', 'work_order') NOT NULL,
    document_number VARCHAR(50) UNIQUE,
    title VARCHAR(200),
    status ENUM('draft', 'processing', 'review', 'finalized') DEFAULT 'draft',
    original_image_url VARCHAR(500),
    ocr_raw_text TEXT,
    ocr_confidence DECIMAL(5,2),
    final_pdf_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Week 1 Checklist
- [ ] GitHub repository created with proper .gitignore
- [ ] Backend folder structure set up
- [ ] Frontend folder structure set up
- [ ] MySQL database running
- [ ] Basic tables created (users, audit_logs, documents)
- [ ] FastAPI returns "Hello World"
- [ ] React app runs on localhost
- [ ] Login/Register UI designed (mobile-first)

### Week 1 Submission
- Repository link with initial code
- Database schema document
- Screenshot of running frontend/backend

---

## 📅 WEEK 2: Authentication & Core APIs
**Theme:** "Secure the gates"

### Your Tasks (Backend - 6-8 hrs)

| Task | Hours | Deliverable |
|------|-------|-------------|
| User Registration API with validation | 2 | POST /api/auth/register |
| User Login API with JWT | 2 | POST /api/auth/login |
| Password hashing (bcrypt) | 0.5 | Secure passwords |
| JWT middleware for protected routes | 1 | Auth middleware |
| User profile GET/PUT APIs | 1.5 | Profile endpoints |
| Audit logging utility function | 1 | log_audit() function |

### Frontend Tasks (Partner - 6-8 hrs)

| Task | Hours | Deliverable |
|------|-------|-------------|
| Login form with validation | 2 | Working login |
| Register form with validation | 2 | Working register |
| JWT storage & auth context | 2 | Auth state management |
| Protected route wrapper | 1 | Route protection |
| Profile page UI | 1 | Profile screen |

### API Specifications

```python
# Registration
POST /api/auth/register
Request: { "email", "password", "full_name", "company_name", "phone" }
Response: { "user_id", "message": "Registration successful" }

# Login
POST /api/auth/login
Request: { "email", "password" }
Response: { "access_token", "token_type": "bearer", "user": {...} }

# Profile
GET /api/auth/profile (Protected)
Response: { "id", "email", "full_name", "company_name", ... }

PUT /api/auth/profile (Protected)
Request: { "full_name", "company_name", "phone", "address", "gst_number" }
```

### Week 2 Checklist
- [ ] User can register with email/password
- [ ] User can login and receive JWT
- [ ] Protected routes require valid JWT
- [ ] User can view and update profile
- [ ] Audit logs capture login/register events
- [ ] Mobile-responsive auth pages
- [ ] Form validation working

### Week 2 Submission
- Working authentication demo
- API documentation (Postman collection)
- Screenshots of mobile UI

---

## 📅 WEEK 3: OCR Integration (CRITICAL WEEK)
**Theme:** "Teach the system to read"

### Your Tasks (Backend - 8 hrs - Push Extra This Week)

| Task | Hours | Deliverable |
|------|-------|-------------|
| Google Cloud Vision API setup | 1 | API credentials ready |
| Image upload endpoint (S3/Cloudinary) | 2 | POST /api/upload |
| OCR processing function | 2.5 | extract_text_from_image() |
| Image preprocessing (OpenCV) | 1.5 | preprocess_image() |
| OCR confidence calculation | 0.5 | Confidence score |
| Testing with sample handwritten images | 0.5 | Test results |

### Frontend Tasks (Partner - 6-8 hrs)

| Task | Hours | Deliverable |
|------|-------|-------------|
| Camera/Gallery image picker (mobile) | 2 | Image capture |
| Image preview before upload | 1 | Preview component |
| Upload progress indicator | 1 | Loading state |
| OCR result display component | 2 | Text display |
| Error handling UI | 1 | Error messages |

### OCR Implementation Code

```python
# ocr_service.py
from google.cloud import vision
import cv2
import numpy as np

def preprocess_image(image_bytes):
    """Enhance image for better OCR accuracy"""
    # Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
    
    # Encode back to bytes
    _, buffer = cv2.imencode('.png', denoised)
    return buffer.tobytes()

def extract_text_google_vision(image_bytes):
    """Extract handwritten text using Google Cloud Vision"""
    client = vision.ImageAnnotatorClient()
    
    # Preprocess image
    processed_image = preprocess_image(image_bytes)
    
    image = vision.Image(content=processed_image)
    
    # Use DOCUMENT_TEXT_DETECTION for handwriting
    response = client.document_text_detection(image=image)
    
    if response.error.message:
        raise Exception(f"Vision API Error: {response.error.message}")
    
    full_text = response.full_text_annotation.text
    confidence = calculate_confidence(response)
    
    return {
        "text": full_text,
        "confidence": confidence,
        "word_count": len(full_text.split())
    }

def calculate_confidence(response):
    """Calculate average confidence from Vision API response"""
    confidences = []
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            confidences.append(block.confidence)
    
    return sum(confidences) / len(confidences) * 100 if confidences else 0
```

### Week 3 Checklist
- [ ] Google Cloud Vision API configured
- [ ] Image upload working (phone camera)
- [ ] OCR extracts text from handwritten images
- [ ] Preprocessing improves accuracy
- [ ] Confidence score displayed
- [ ] Mobile camera integration working
- [ ] At least 70% accuracy on test images

### Week 3 Submission
- OCR demo video (handwritten → text)
- Accuracy test results
- API response samples

---

## 📅 WEEK 4: Quotation Module - Part 1 (CRITICAL)
**Theme:** "Build the money maker"

### Your Tasks (Backend - 6-8 hrs)

| Task | Hours | Deliverable |
|------|-------|-------------|
| Quotation & QuotationItems tables | 1 | DB tables |
| Inventory/Products table | 1 | Product catalog |
| Create quotation API | 2 | POST /api/quotations |
| GST calculation logic | 1.5 | calculate_gst() |
| Field mapping from OCR text | 1.5 | map_ocr_to_quotation() |

### Frontend Tasks (Partner - 6-8 hrs)

| Task | Hours | Deliverable |
|------|-------|-------------|
| Quotation form UI (mobile-first) | 3 | Form component |
| Customer details section | 1 | Customer input |
| Dynamic line items (add/remove) | 2 | Line items |
| Auto-calculation display | 1 | Totals display |

### Database Schema (Quotation)

```sql
-- Inventory/Products Table
CREATE TABLE products (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    unit VARCHAR(20) DEFAULT 'nos',
    default_price DECIMAL(12,2),
    gst_rate DECIMAL(5,2) DEFAULT 18.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Quotations Table
CREATE TABLE quotations (
    id VARCHAR(36) PRIMARY KEY,
    document_id VARCHAR(36) NOT NULL,
    customer_name VARCHAR(200) NOT NULL,
    customer_email VARCHAR(255),
    customer_phone VARCHAR(20),
    customer_address TEXT,
    customer_gst VARCHAR(20),
    subtotal DECIMAL(12,2) DEFAULT 0,
    cgst_amount DECIMAL(12,2) DEFAULT 0,
    sgst_amount DECIMAL(12,2) DEFAULT 0,
    igst_amount DECIMAL(12,2) DEFAULT 0,
    discount_percent DECIMAL(5,2) DEFAULT 0,
    discount_amount DECIMAL(12,2) DEFAULT 0,
    grand_total DECIMAL(12,2) DEFAULT 0,
    valid_until DATE,
    terms_conditions TEXT,
    notes TEXT,
    FOREIGN KEY (document_id) REFERENCES documents(id)
);

-- Quotation Line Items
CREATE TABLE quotation_items (
    id VARCHAR(36) PRIMARY KEY,
    quotation_id VARCHAR(36) NOT NULL,
    product_id VARCHAR(36),
    item_order INT,
    description VARCHAR(500) NOT NULL,
    quantity DECIMAL(10,2) NOT NULL,
    unit VARCHAR(20) DEFAULT 'nos',
    unit_price DECIMAL(12,2) NOT NULL,
    gst_rate DECIMAL(5,2) DEFAULT 18.00,
    gst_amount DECIMAL(12,2),
    total DECIMAL(12,2),
    is_free_text BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (quotation_id) REFERENCES quotations(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

### GST Calculation Logic

```python
# gst_calculator.py
from decimal import Decimal

def calculate_gst(items, is_igst=False, discount_percent=0):
    """
    Calculate GST for quotation items
    
    Args:
        items: List of {quantity, unit_price, gst_rate}
        is_igst: True for inter-state (IGST), False for intra-state (CGST+SGST)
        discount_percent: Discount percentage on subtotal
    
    Returns:
        Dictionary with all calculated values
    """
    subtotal = Decimal('0')
    total_gst = Decimal('0')
    
    calculated_items = []
    
    for item in items:
        qty = Decimal(str(item['quantity']))
        price = Decimal(str(item['unit_price']))
        gst_rate = Decimal(str(item.get('gst_rate', 18)))
        
        item_subtotal = qty * price
        item_gst = item_subtotal * (gst_rate / 100)
        item_total = item_subtotal + item_gst
        
        subtotal += item_subtotal
        total_gst += item_gst
        
        calculated_items.append({
            **item,
            'item_subtotal': float(item_subtotal),
            'gst_amount': float(item_gst),
            'total': float(item_total)
        })
    
    # Apply discount
    discount_amount = subtotal * (Decimal(str(discount_percent)) / 100)
    taxable_amount = subtotal - discount_amount
    
    # Recalculate GST on discounted amount
    # (Simplified: using average GST rate)
    avg_gst_rate = (total_gst / subtotal * 100) if subtotal > 0 else Decimal('18')
    final_gst = taxable_amount * (avg_gst_rate / 100)
    
    if is_igst:
        cgst = Decimal('0')
        sgst = Decimal('0')
        igst = final_gst
    else:
        cgst = final_gst / 2
        sgst = final_gst / 2
        igst = Decimal('0')
    
    grand_total = taxable_amount + final_gst
    
    return {
        'items': calculated_items,
        'subtotal': float(subtotal),
        'discount_percent': float(discount_percent),
        'discount_amount': float(discount_amount),
        'taxable_amount': float(taxable_amount),
        'cgst_amount': float(cgst),
        'sgst_amount': float(sgst),
        'igst_amount': float(igst),
        'total_gst': float(final_gst),
        'grand_total': float(grand_total)
    }
```

### Week 4 Checklist
- [ ] Quotation database tables created
- [ ] Products/inventory table created
- [ ] Create quotation API working
- [ ] GST calculation accurate
- [ ] Quotation form UI complete (mobile)
- [ ] Dynamic line items working
- [ ] Can add products from inventory OR free text

### Week 4 Submission
- Quotation creation demo
- GST calculation examples
- Mobile UI screenshots

---

## 📅 WEEK 5: Quotation Module - Part 2 (Complete)
**Theme:** "Polish the crown jewel"

### Your Tasks (Backend - 6-8 hrs)

| Task | Hours | Deliverable |
|------|-------|-------------|
| OCR → Quotation field mapping | 2 | Smart extraction |
| Quotation PDF template (HTML) | 2 | PDF template |
| PDF generation with WeasyPrint | 1.5 | generate_quotation_pdf() |
| Quotation CRUD APIs (Update, Delete, List) | 1.5 | Complete APIs |

### Frontend Tasks (Partner - 6-8 hrs)

| Task | Hours | Deliverable |
|------|-------|-------------|
| OCR review & edit screen | 2 | Review component |
| Quotation preview screen | 2 | Preview before finalize |
| PDF download button | 1 | Download feature |
| Quotation list view | 1.5 | List/history |
| Search & filter | 0.5 | Search feature |

### OCR to Quotation Mapping

```python
# quotation_mapper.py
import re

def map_ocr_to_quotation(ocr_text):
    """
    Extract quotation fields from OCR text
    Uses pattern matching for common formats
    """
    result = {
        'customer_name': None,
        'customer_phone': None,
        'items': [],
        'confidence_flags': []
    }
    
    lines = ocr_text.strip().split('\n')
    
    # Pattern: Customer/Client name
    name_patterns = [
        r'(?:customer|client|to|bill to|name)[:\s]+([a-zA-Z\s]+)',
        r'^([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)$'  # Capitalized names
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, ocr_text, re.IGNORECASE | re.MULTILINE)
        if match:
            result['customer_name'] = match.group(1).strip()
            break
    
    # Pattern: Phone number (Indian)
    phone_pattern = r'(?:phone|mobile|contact|ph)?[:\s]*([6-9]\d{9})'
    phone_match = re.search(phone_pattern, ocr_text)
    if phone_match:
        result['customer_phone'] = phone_match.group(1)
    
    # Pattern: Items with quantity and price
    # Matches: "Item name - 5 nos @ 100" or "Item name x 5 = 500"
    item_patterns = [
        r'([a-zA-Z\s]+)[\s\-]+(\d+)\s*(?:nos|pcs|units?)?\s*[@x]\s*(?:Rs\.?|₹)?\s*(\d+(?:\.\d{2})?)',
        r'([a-zA-Z\s]+)\s+(\d+)\s+(\d+(?:\.\d{2})?)',  # Simple: name qty price
    ]
    
    for pattern in item_patterns:
        matches = re.findall(pattern, ocr_text, re.IGNORECASE)
        for match in matches:
            if len(match) >= 3:
                result['items'].append({
                    'description': match[0].strip(),
                    'quantity': float(match[1]),
                    'unit_price': float(match[2]),
                    'is_free_text': True
                })
    
    # Flag low confidence extractions
    if not result['customer_name']:
        result['confidence_flags'].append('customer_name')
    if len(result['items']) == 0:
        result['confidence_flags'].append('items')
    
    return result
```

### PDF Template (HTML for WeasyPrint)

```html
<!-- quotation_template.html -->
<!DOCTYPE html>
<html>
<head>
    <style>
        @page { size: A4; margin: 1cm; }
        body { font-family: Arial, sans-serif; font-size: 12px; }
        .header { display: flex; justify-content: space-between; border-bottom: 2px solid #333; padding-bottom: 10px; }
        .company-logo { max-height: 60px; }
        .company-info { text-align: right; }
        .title { text-align: center; font-size: 18px; font-weight: bold; margin: 20px 0; }
        .customer-box { background: #f5f5f5; padding: 10px; margin: 10px 0; }
        .items-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        .items-table th, .items-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .items-table th { background: #333; color: white; }
        .totals { width: 300px; margin-left: auto; }
        .totals td { padding: 5px; }
        .grand-total { font-size: 16px; font-weight: bold; background: #f0f0f0; }
        .footer { margin-top: 30px; font-size: 10px; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            {% if company_logo %}<img src="{{ company_logo }}" class="company-logo">{% endif %}
            <h2>{{ company_name }}</h2>
        </div>
        <div class="company-info">
            <p>{{ company_address }}</p>
            <p>Phone: {{ company_phone }}</p>
            <p>GSTIN: {{ company_gst }}</p>
        </div>
    </div>
    
    <div class="title">QUOTATION</div>
    <p><strong>Quotation No:</strong> {{ quotation_number }} | <strong>Date:</strong> {{ date }}</p>
    
    <div class="customer-box">
        <strong>To:</strong><br>
        {{ customer_name }}<br>
        {{ customer_address }}<br>
        Phone: {{ customer_phone }}<br>
        {% if customer_gst %}GSTIN: {{ customer_gst }}{% endif %}
    </div>
    
    <table class="items-table">
        <thead>
            <tr>
                <th>#</th>
                <th>Description</th>
                <th>Qty</th>
                <th>Unit</th>
                <th>Rate (₹)</th>
                <th>GST %</th>
                <th>Amount (₹)</th>
            </tr>
        </thead>
        <tbody>
            {% for item in items %}
            <tr>
                <td>{{ loop.index }}</td>
                <td>{{ item.description }}</td>
                <td>{{ item.quantity }}</td>
                <td>{{ item.unit }}</td>
                <td>{{ "%.2f"|format(item.unit_price) }}</td>
                <td>{{ item.gst_rate }}%</td>
                <td>{{ "%.2f"|format(item.total) }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    <table class="totals">
        <tr><td>Subtotal:</td><td>₹ {{ "%.2f"|format(subtotal) }}</td></tr>
        {% if discount_amount > 0 %}
        <tr><td>Discount ({{ discount_percent }}%):</td><td>- ₹ {{ "%.2f"|format(discount_amount) }}</td></tr>
        {% endif %}
        <tr><td>CGST:</td><td>₹ {{ "%.2f"|format(cgst_amount) }}</td></tr>
        <tr><td>SGST:</td><td>₹ {{ "%.2f"|format(sgst_amount) }}</td></tr>
        <tr class="grand-total"><td>Grand Total:</td><td>₹ {{ "%.2f"|format(grand_total) }}</td></tr>
    </table>
    
    <div class="footer">
        <p><strong>Terms & Conditions:</strong></p>
        <p>{{ terms_conditions }}</p>
        <p>Valid until: {{ valid_until }}</p>
    </div>
</body>
</html>
```

### Week 5 Checklist
- [ ] OCR text maps to quotation fields
- [ ] User can review & edit OCR extractions
- [ ] PDF generation working
- [ ] PDF has company branding
- [ ] Quotation list with search
- [ ] Full quotation workflow: Image → OCR → Edit → Preview → PDF

### Week 5 Submission
- End-to-end quotation demo (handwritten to PDF)
- Sample generated PDFs
- Video walkthrough

---

## 📅 WEEK 6: MOM Module with NVIDIA NIMs
**Theme:** "Bring in the AI"

### Your Tasks (Backend - 8 hrs - Critical AI Week)

| Task | Hours | Deliverable |
|------|-------|-------------|
| NVIDIA NIMs API setup & authentication | 1.5 | API working |
| MOM database tables | 1 | Tables created |
| AI summarization function | 2.5 | summarize_meeting_notes() |
| Prompt engineering for MOM | 1.5 | Optimized prompts |
| MOM CRUD APIs | 1.5 | Complete APIs |

### Frontend Tasks (Partner - 6-8 hrs)

| Task | Hours | Deliverable |
|------|-------|-------------|
| MOM form UI | 2 | Form component |
| Meeting notes input (large text area) | 1 | Notes input |
| AI summarize button with loading | 1 | Trigger summarization |
| Editable summary display | 2 | Edit AI output |
| Action items management UI | 2 | Action items CRUD |

### NVIDIA NIMs Integration

```python
# nvidia_nims_service.py
import requests
import os

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_NIM_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

def summarize_meeting_notes(raw_notes: str) -> dict:
    """
    Summarize meeting notes using NVIDIA NIMs Llama 3.1
    
    Returns structured MOM data
    """
    
    prompt = f"""You are a professional meeting assistant. Analyze the following meeting notes and extract structured information.

MEETING NOTES:
{raw_notes}

Provide your response in the following JSON format only, no other text:
{{
    "meeting_title": "Brief title for the meeting",
    "summary": "2-3 sentence summary of the meeting",
    "key_discussion_points": [
        "Point 1",
        "Point 2",
        "Point 3"
    ],
    "decisions_made": [
        "Decision 1",
        "Decision 2"
    ],
    "action_items": [
        {{
            "task": "Task description",
            "assigned_to": "Person name or 'Unassigned'",
            "deadline": "Date if mentioned or 'TBD'",
            "priority": "high/medium/low"
        }}
    ],
    "next_meeting": "Date/time if mentioned or null"
}}

Extract only what is explicitly mentioned or can be clearly inferred. Be concise."""

    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "meta/llama-3.1-70b-instruct",  # Or latest available
        "messages": [
            {
                "role": "system",
                "content": "You are a professional meeting minutes assistant. Always respond with valid JSON only."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "temperature": 0.3,  # Lower for more consistent output
        "max_tokens": 1024,
        "top_p": 0.9
    }
    
    try:
        response = requests.post(
            NVIDIA_NIM_URL,
            headers=headers,
            json=payload,
            timeout=30  # 30 second timeout
        )
        response.raise_for_status()
        
        result = response.json()
        ai_response = result['choices'][0]['message']['content']
        
        # Parse JSON from response
        import json
        # Clean up response if needed (remove markdown code blocks)
        ai_response = ai_response.strip()
        if ai_response.startswith("```"):
            ai_response = ai_response.split("```")[1]
            if ai_response.startswith("json"):
                ai_response = ai_response[4:]
        
        parsed_data = json.loads(ai_response)
        
        return {
            "success": True,
            "data": parsed_data,
            "processing_time": response.elapsed.total_seconds()
        }
        
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "AI service timeout. Please try again.",
            "fallback": True
        }
    except json.JSONDecodeError:
        return {
            "success": False,
            "error": "Failed to parse AI response",
            "raw_response": ai_response
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_available_models():
    """Get list of available models from NVIDIA NIMs"""
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        "https://integrate.api.nvidia.com/v1/models",
        headers=headers
    )
    return response.json()
```

### MOM Database Schema

```sql
-- Minutes of Meeting Table
CREATE TABLE moms (
    id VARCHAR(36) PRIMARY KEY,
    document_id VARCHAR(36) NOT NULL,
    meeting_title VARCHAR(200),
    meeting_date DATE,
    meeting_time TIME,
    location VARCHAR(200),
    attendees JSON,
    agenda TEXT,
    raw_notes TEXT,
    ai_summary TEXT,
    discussion_points JSON,
    decisions JSON,
    next_meeting_date DATETIME,
    FOREIGN KEY (document_id) REFERENCES documents(id)
);

-- Action Items Table
CREATE TABLE action_items (
    id VARCHAR(36) PRIMARY KEY,
    mom_id VARCHAR(36) NOT NULL,
    task_description TEXT NOT NULL,
    assigned_to VARCHAR(100),
    deadline DATE,
    priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
    status ENUM('pending', 'in_progress', 'completed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (mom_id) REFERENCES moms(id)
);
```

### Week 6 Checklist
- [ ] NVIDIA NIMs API authenticated
- [ ] Llama model responding correctly
- [ ] Meeting notes summarization working
- [ ] Response time < 7 seconds
- [ ] Action items extracted with status
- [ ] MOM form complete (mobile)
- [ ] Can edit AI-generated summary

### Week 6 Submission
- AI summarization demo
- Sample input/output examples
- API response time measurements

---

## 📅 WEEK 7: Work Order Module + Integration
**Theme:** "Complete the trilogy"

### Your Tasks (Backend - 6-8 hrs)

| Task | Hours | Deliverable |
|------|-------|-------------|
| Work Order database tables | 1 | Tables created |
| Work Order CRUD APIs | 2 | Complete APIs |
| Photo upload (before/after) | 1.5 | Photo endpoints |
| Labor cost calculation | 1 | Cost calculator |
| Link quotation to work order | 1 | Linking logic |
| MOM PDF generation | 0.5 | MOM PDF |

### Frontend Tasks (Partner - 6-8 hrs)

| Task | Hours | Deliverable |
|------|-------|-------------|
| Work Order form UI | 2.5 | Form component |
| Materials list management | 1.5 | Materials CRUD |
| Before/After photo capture | 1.5 | Photo component |
| Digital signature pad | 1 | Signature capture |
| Work Order PDF preview | 1 | Preview screen |

### Work Order Database Schema

```sql
-- Work Orders Table
CREATE TABLE work_orders (
    id VARCHAR(36) PRIMARY KEY,
    document_id VARCHAR(36) NOT NULL,
    linked_quotation_id VARCHAR(36),
    work_order_number VARCHAR(50) UNIQUE,
    client_name VARCHAR(200) NOT NULL,
    client_phone VARCHAR(20),
    client_email VARCHAR(255),
    service_location TEXT,
    work_description TEXT,
    assigned_to VARCHAR(100),
    start_date DATE,
    end_date DATE,
    labor_hours DECIMAL(6,2),
    labor_rate DECIMAL(10,2),
    labor_cost DECIMAL(12,2),
    material_cost DECIMAL(12,2),
    total_cost DECIMAL(12,2),
    status ENUM('pending', 'in_progress', 'completed', 'cancelled') DEFAULT 'pending',
    before_photo_url VARCHAR(500),
    after_photo_url VARCHAR(500),
    customer_signature_url VARCHAR(500),
    remarks TEXT,
    FOREIGN KEY (document_id) REFERENCES documents(id),
    FOREIGN KEY (linked_quotation_id) REFERENCES quotations(id)
);

-- Work Order Materials
CREATE TABLE work_order_materials (
    id VARCHAR(36) PRIMARY KEY,
    work_order_id VARCHAR(36) NOT NULL,
    material_name VARCHAR(200) NOT NULL,
    quantity DECIMAL(10,2),
    unit VARCHAR(20),
    unit_cost DECIMAL(12,2),
    total_cost DECIMAL(12,2),
    FOREIGN KEY (work_order_id) REFERENCES work_orders(id)
);
```

### Week 7 Checklist
- [ ] Work Order CRUD complete
- [ ] Materials tracking working
- [ ] Before/After photos uploadable
- [ ] Digital signature capture
- [ ] Labor cost calculated
- [ ] Quotation → Work Order linking
- [ ] All three module PDFs generating

### Week 7 Submission
- Work Order demo
- All modules working together
- Integration test results

---

## 📅 WEEK 8: Dashboard, Testing & Deployment
**Theme:** "Ship it!"

### Your Tasks (Backend - 8 hrs)

| Task | Hours | Deliverable |
|------|-------|-------------|
| Dashboard stats API | 1 | Stats endpoint |
| Document search API | 1 | Search endpoint |
| Bug fixes & optimization | 2 | Stable backend |
| Railway deployment | 2 | Live backend |
| Environment configuration | 1 | Production config |
| Final testing | 1 | Test report |

### Frontend Tasks (Partner - 8 hrs)

| Task | Hours | Deliverable |
|------|-------|-------------|
| Dashboard with stats | 2 | Dashboard page |
| Document list with filters | 1.5 | List view |
| Final UI polish | 2 | Polished UI |
| Vercel deployment | 1.5 | Live frontend |
| Bug fixes | 1 | Stable frontend |

### Deployment Checklist

```bash
# Backend (Railway)
1. Create Railway account
2. Connect GitHub repository
3. Set environment variables:
   - DATABASE_URL
   - NVIDIA_API_KEY
   - GOOGLE_CLOUD_CREDENTIALS
   - JWT_SECRET
   - AWS_ACCESS_KEY (for S3)
4. Deploy and test

# Frontend (Vercel)
1. Create Vercel account
2. Connect GitHub repository
3. Set environment variables:
   - REACT_APP_API_URL
4. Deploy and test

# Database (PlanetScale or Railway MySQL)
1. Create production database
2. Run migrations
3. Create admin user
```

### Week 8 Checklist
- [ ] Dashboard shows document stats
- [ ] Search & filter working
- [ ] All bugs fixed
- [ ] Backend deployed on Railway
- [ ] Frontend deployed on Vercel
- [ ] Mobile responsive verified
- [ ] End-to-end testing passed
- [ ] Demo video recorded

### Week 8 Submission
- Live application URL
- Demo video
- Source code (GitHub)
- Final documentation

---

# SUMMARY: 8-WEEK MILESTONE TRACKER

| Week | Milestone | Your Focus | Partner Focus | Deliverable |
|------|-----------|------------|---------------|-------------|
| 1 | Foundation | Backend setup, DB schema | Frontend setup, Auth UI | Repos + DB ready |
| 2 | Auth Complete | Auth APIs, JWT | Auth pages, routing | Working login |
| 3 | OCR Working | Google Vision, preprocessing | Camera upload UI | Handwriting → Text |
| 4 | Quotation P1 | APIs, GST calc, mapping | Form UI, line items | Create quotation |
| 5 | Quotation P2 | PDF generation, OCR mapping | Preview, download | Full quotation flow |
| 6 | MOM + AI | NVIDIA NIMs, summarization | MOM form, action items | AI summarization |
| 7 | Work Order | APIs, photos, linking | Form, signature | All 3 modules done |
| 8 | Deploy | Railway, optimization | Vercel, polish | LIVE APPLICATION |

---

# RISK MITIGATION

| Risk | Probability | Mitigation |
|------|-------------|------------|
| OCR accuracy low | Medium | Use Google Vision (best for handwriting), good preprocessing |
| NVIDIA NIM slow/down | Low | Cache responses, have fallback manual mode |
| Time overrun | Medium | Quotation is MVP - others can be simplified |
| Partner unavailable | Low | Document everything, modular code |

---

# BUDGET ESTIMATE

| Service | Free Tier | Estimated Cost |
|---------|-----------|----------------|
| Google Cloud Vision | 1000 units/month free | $0 (within free tier) |
| NVIDIA NIMs | $0 trial credits | $0-10/month |
| Railway | $5 free credits | $0-5/month |
| Vercel | Free for hobby | $0 |
| Cloudinary | 25GB free | $0 |
| **Total** | | **$0-15/month** |

---

**Document Version:** 1.0  
**Created:** January 2025  
**Project Duration:** 8 Weeks  
**Team Size:** 2 Members