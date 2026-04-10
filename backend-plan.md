# BACKEND DEVELOPMENT PLAN
## Smart Business Document Generator
### 8-Week Implementation Guide

---

# DEVELOPER PROFILE

| Attribute | Details |
|-----------|---------|
| **Role** | Backend Developer (Solo) |
| **Responsibilities** | APIs, Database, OCR, AI Integration, Deployment |
| **Time Commitment** | 4-8 hours/week |
| **Experience Level** | Less experience with OCR (learning curve factored in) |

---

# TECHNOLOGY STACK

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Framework** | Python 3.11 + FastAPI | REST API development |
| **Database** | MySQL 8.0 | Data storage |
| **ORM** | SQLAlchemy | Database operations |
| **OCR** | Google Cloud Vision API | Handwritten English text extraction |
| **AI/LLM** | NVIDIA NIMs + Llama 3.1 | Meeting notes summarization |
| **PDF** | WeasyPrint + Jinja2 | Document generation |
| **Storage** | AWS S3 / Cloudinary | Images & PDFs |
| **Auth** | JWT + bcrypt | Authentication |
| **Deployment** | Railway | Cloud hosting |

---

# WEEK-BY-WEEK PLAN

---

## 📅 WEEK 1: Project Setup & Database Design
**Hours Required:** 6-8 hours

### Tasks

| # | Task | Hours | Priority |
|---|------|-------|----------|
| 1 | Create GitHub repository with .gitignore | 0.5 | High |
| 2 | Setup Python virtual environment | 0.5 | High |
| 3 | Initialize FastAPI project structure | 1 | High |
| 4 | Install dependencies (requirements.txt) | 0.5 | High |
| 5 | Setup MySQL database locally | 1 | High |
| 6 | Configure SQLAlchemy connection | 1 | High |
| 7 | Design complete database schema | 1.5 | High |
| 8 | Create initial migration (Users, Documents, AuditLogs) | 1.5 | High |

### Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry
│   ├── config.py               # Environment configuration
│   ├── database.py             # Database connection
│   │
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── document.py
│   │   ├── quotation.py
│   │   ├── mom.py
│   │   └── work_order.py
│   │
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── quotation.py
│   │   ├── mom.py
│   │   └── work_order.py
│   │
│   ├── routers/                # API routes
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── documents.py
│   │   ├── quotations.py
│   │   ├── moms.py
│   │   ├── work_orders.py
│   │   └── ocr.py
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── ocr_service.py
│   │   ├── ai_service.py
│   │   ├── pdf_service.py
│   │   ├── gst_calculator.py
│   │   └── audit_service.py
│   │
│   ├── utils/                  # Utilities
│   │   ├── __init__.py
│   │   ├── auth.py             # JWT utilities
│   │   ├── file_upload.py
│   │   └── helpers.py
│   │
│   └── templates/              # PDF templates
│       ├── quotation.html
│       ├── mom.html
│       └── work_order.html
│
├── tests/
│   └── ...
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

### Requirements.txt
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pymysql==1.1.0
python-dotenv==1.0.0
pydantic==2.5.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
google-cloud-vision==3.5.0
opencv-python==4.8.1.78
Pillow==10.1.0
weasyprint==60.1
Jinja2==3.1.2
boto3==1.33.6
requests==2.31.0
```

### Database Schema (Week 1 Tables)

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

-- Documents Table (Base)
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

### Deliverables
- [ ] GitHub repository with proper structure
- [ ] FastAPI app running on localhost:8000
- [ ] MySQL database with initial tables
- [ ] `/docs` endpoint showing Swagger UI

---

## 📅 WEEK 2: Authentication System
**Hours Required:** 6-8 hours

### Tasks

| # | Task | Hours | Priority |
|---|------|-------|----------|
| 1 | Create User Pydantic schemas | 0.5 | High |
| 2 | Implement password hashing (bcrypt) | 0.5 | High |
| 3 | Build registration endpoint | 1.5 | High |
| 4 | Build login endpoint with JWT | 1.5 | High |
| 5 | Create JWT middleware for protected routes | 1 | High |
| 6 | Build user profile GET/PUT endpoints | 1.5 | High |
| 7 | Implement audit logging utility | 1 | Medium |
| 8 | Create admin user seeder | 0.5 | Medium |

### API Endpoints

```python
# Auth Router - /api/auth

POST /api/auth/register
- Request: { email, password, full_name, company_name?, phone? }
- Response: { user_id, message }
- Validation: Email unique, password min 8 chars

POST /api/auth/login
- Request: { email, password }
- Response: { access_token, token_type, user: {...} }
- Creates: Audit log entry

GET /api/auth/profile (Protected)
- Response: { id, email, full_name, company_name, ... }

PUT /api/auth/profile (Protected)
- Request: { full_name?, company_name?, phone?, address?, gst_number?, company_logo_url? }
- Response: { updated user object }
- Creates: Audit log entry
```

### Code: JWT Authentication

```python
# app/utils/auth.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    token = credentials.credentials
    payload = decode_token(token)
    return payload
```

### Code: Audit Logging

```python
# app/services/audit_service.py
from app.models.audit_log import AuditLog
from app.database import get_db
import uuid

def log_audit(
    db,
    user_id: str,
    action: str,
    entity_type: str = None,
    entity_id: str = None,
    old_value: dict = None,
    new_value: dict = None,
    ip_address: str = None
):
    audit = AuditLog(
        id=str(uuid.uuid4()),
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_value=old_value,
        new_value=new_value,
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()
```

### Deliverables
- [ ] User registration working
- [ ] User login returning JWT
- [ ] Protected routes requiring valid token
- [ ] Profile CRUD operations
- [ ] Audit logs being created
- [ ] Admin user created

---

## 📅 WEEK 3: OCR Integration (CRITICAL)
**Hours Required:** 8 hours (Push extra this week)

### Tasks

| # | Task | Hours | Priority |
|---|------|-------|----------|
| 1 | Setup Google Cloud Vision API credentials | 1 | High |
| 2 | Create image upload endpoint (Cloudinary/S3) | 1.5 | High |
| 3 | Implement image preprocessing (OpenCV) | 2 | High |
| 4 | Build OCR extraction function | 2 | High |
| 5 | Implement confidence score calculation | 0.5 | High |
| 6 | Create OCR API endpoint | 0.5 | High |
| 7 | Test with sample handwritten images | 0.5 | High |

### Google Cloud Vision Setup

```bash
# 1. Create Google Cloud Project
# 2. Enable Cloud Vision API
# 3. Create Service Account
# 4. Download JSON key file
# 5. Set environment variable:
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

### Code: Complete OCR Service

```python
# app/services/ocr_service.py
from google.cloud import vision
import cv2
import numpy as np
from PIL import Image
import io

class OCRService:
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()
    
    def preprocess_image(self, image_bytes: bytes) -> bytes:
        """
        Enhance image for better OCR accuracy on handwritten text
        """
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Invalid image data")
        
        # Resize if too large (max 4MB for Vision API)
        height, width = img.shape[:2]
        max_dimension = 2048
        if max(height, width) > max_dimension:
            scale = max_dimension / max(height, width)
            img = cv2.resize(img, None, fx=scale, fy=scale)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding for handwritten text
        thresh = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
        
        # Slight dilation to connect broken strokes
        kernel = np.ones((1, 1), np.uint8)
        dilated = cv2.dilate(denoised, kernel, iterations=1)
        
        # Encode back to bytes
        _, buffer = cv2.imencode('.png', dilated)
        return buffer.tobytes()
    
    def extract_text(self, image_bytes: bytes, preprocess: bool = True) -> dict:
        """
        Extract handwritten text using Google Cloud Vision
        """
        try:
            # Preprocess image
            if preprocess:
                processed_bytes = self.preprocess_image(image_bytes)
            else:
                processed_bytes = image_bytes
            
            # Create Vision API image object
            image = vision.Image(content=processed_bytes)
            
            # Use DOCUMENT_TEXT_DETECTION for better handwriting recognition
            response = self.client.document_text_detection(image=image)
            
            if response.error.message:
                raise Exception(f"Vision API Error: {response.error.message}")
            
            # Extract full text
            full_text = ""
            if response.full_text_annotation:
                full_text = response.full_text_annotation.text
            
            # Calculate confidence
            confidence = self._calculate_confidence(response)
            
            # Extract word-level details for debugging
            words = self._extract_words(response)
            
            return {
                "success": True,
                "text": full_text.strip(),
                "confidence": round(confidence, 2),
                "word_count": len(full_text.split()),
                "words": words[:50]  # First 50 words with positions
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": 0
            }
    
    def _calculate_confidence(self, response) -> float:
        """Calculate average confidence from Vision API response"""
        confidences = []
        
        if not response.full_text_annotation:
            return 0.0
        
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                if hasattr(block, 'confidence'):
                    confidences.append(block.confidence)
        
        if not confidences:
            return 75.0  # Default if no confidence reported
        
        return (sum(confidences) / len(confidences)) * 100
    
    def _extract_words(self, response) -> list:
        """Extract individual words with their confidence"""
        words = []
        
        if not response.full_text_annotation:
            return words
        
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    for word in paragraph.words:
                        word_text = ''.join([
                            symbol.text for symbol in word.symbols
                        ])
                        words.append({
                            "text": word_text,
                            "confidence": round(word.confidence * 100, 1) if hasattr(word, 'confidence') else None
                        })
        
        return words


# Singleton instance
ocr_service = OCRService()
```

### Code: Upload Endpoint

```python
# app/routers/ocr.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.services.ocr_service import ocr_service
from app.utils.auth import get_current_user
from app.utils.file_upload import upload_to_cloudinary
import io

router = APIRouter(prefix="/api/ocr", tags=["OCR"])

ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/extract")
async def extract_text_from_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    # Validate file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Invalid file type. Use JPEG, PNG, or WEBP.")
    
    # Read file
    contents = await file.read()
    
    # Validate file size
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large. Maximum 10MB allowed.")
    
    # Upload original to cloud storage
    image_url = upload_to_cloudinary(contents, file.filename)
    
    # Extract text
    result = ocr_service.extract_text(contents)
    
    if not result["success"]:
        raise HTTPException(500, f"OCR failed: {result['error']}")
    
    return {
        "image_url": image_url,
        "extracted_text": result["text"],
        "confidence": result["confidence"],
        "word_count": result["word_count"],
        "needs_review": result["confidence"] < 75
    }
```

### Deliverables
- [ ] Google Cloud Vision API working
- [ ] Image upload to cloud storage working
- [ ] OCR extracts handwritten English text
- [ ] Preprocessing improves accuracy
- [ ] Confidence score returned
- [ ] Tested with 5+ sample images

---

## 📅 WEEK 4: Quotation Module - Part 1
**Hours Required:** 6-8 hours

### Tasks

| # | Task | Hours | Priority |
|---|------|-------|----------|
| 1 | Create Quotation & Items database tables | 1 | High |
| 2 | Create Products/Inventory table | 0.5 | High |
| 3 | Build Quotation Pydantic schemas | 0.5 | High |
| 4 | Implement GST calculation service | 1.5 | High |
| 5 | Create Quotation POST endpoint | 1.5 | High |
| 6 | Create Products CRUD endpoints | 1 | Medium |
| 7 | Build OCR-to-Quotation field mapper | 1.5 | High |

### Database Schema (Quotation)

```sql
-- Products/Inventory Table
CREATE TABLE products (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    unit VARCHAR(20) DEFAULT 'nos',
    default_price DECIMAL(12,2),
    gst_rate DECIMAL(5,2) DEFAULT 18.00,
    is_active BOOLEAN DEFAULT TRUE,
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
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
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
    FOREIGN KEY (quotation_id) REFERENCES quotations(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

### Code: GST Calculator

```python
# app/services/gst_calculator.py
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict

class GSTCalculator:
    """
    GST Calculator for Indian taxation
    Supports: CGST+SGST (intra-state) and IGST (inter-state)
    """
    
    @staticmethod
    def calculate(
        items: List[Dict],
        is_igst: bool = False,
        discount_percent: float = 0
    ) -> Dict:
        """
        Calculate GST for quotation items
        
        Args:
            items: List of dicts with {quantity, unit_price, gst_rate}
            is_igst: True for inter-state (IGST only)
            discount_percent: Discount on subtotal
        
        Returns:
            Complete calculation breakdown
        """
        subtotal = Decimal('0')
        calculated_items = []
        
        for idx, item in enumerate(items):
            qty = Decimal(str(item['quantity']))
            price = Decimal(str(item['unit_price']))
            gst_rate = Decimal(str(item.get('gst_rate', 18)))
            
            item_subtotal = qty * price
            item_gst = (item_subtotal * gst_rate / 100).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            item_total = item_subtotal + item_gst
            
            subtotal += item_subtotal
            
            calculated_items.append({
                **item,
                'item_order': idx + 1,
                'item_subtotal': float(item_subtotal),
                'gst_amount': float(item_gst),
                'total': float(item_total)
            })
        
        # Apply discount on subtotal
        discount_dec = Decimal(str(discount_percent))
        discount_amount = (subtotal * discount_dec / 100).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        taxable_amount = subtotal - discount_amount
        
        # Calculate total GST (using weighted average rate)
        total_item_gst = sum(Decimal(str(i['gst_amount'])) for i in calculated_items)
        if subtotal > 0:
            effective_gst_rate = (total_item_gst / subtotal * 100)
        else:
            effective_gst_rate = Decimal('18')
        
        # GST on taxable amount
        total_gst = (taxable_amount * effective_gst_rate / 100).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        # Split GST
        if is_igst:
            cgst = Decimal('0')
            sgst = Decimal('0')
            igst = total_gst
        else:
            cgst = (total_gst / 2).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            sgst = total_gst - cgst  # Remaining to avoid rounding issues
            igst = Decimal('0')
        
        grand_total = (taxable_amount + total_gst).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        return {
            'items': calculated_items,
            'subtotal': float(subtotal),
            'discount_percent': float(discount_percent),
            'discount_amount': float(discount_amount),
            'taxable_amount': float(taxable_amount),
            'cgst_rate': float(effective_gst_rate / 2) if not is_igst else 0,
            'cgst_amount': float(cgst),
            'sgst_rate': float(effective_gst_rate / 2) if not is_igst else 0,
            'sgst_amount': float(sgst),
            'igst_rate': float(effective_gst_rate) if is_igst else 0,
            'igst_amount': float(igst),
            'total_gst': float(total_gst),
            'grand_total': float(grand_total),
            'is_igst': is_igst
        }


# Usage example
gst_calculator = GSTCalculator()
```

### Code: OCR to Quotation Mapper

```python
# app/services/quotation_mapper.py
import re
from typing import Dict, List

class QuotationMapper:
    """
    Maps OCR extracted text to quotation fields
    Uses pattern matching for common handwritten formats
    """
    
    # Indian phone patterns
    PHONE_PATTERNS = [
        r'(?:phone|mobile|contact|mob|ph)?[:\s]*([6-9]\d{9})',
        r'(?:phone|mobile|contact|mob|ph)?[:\s]*\+91[\s-]?([6-9]\d{9})',
    ]
    
    # Customer name patterns
    NAME_PATTERNS = [
        r'(?:customer|client|to|bill\s*to|name|party)[:\s]+([A-Za-z\s]+?)(?:\n|phone|mobile|address|$)',
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})$',
    ]
    
    # Item patterns (description, quantity, price)
    ITEM_PATTERNS = [
        # "Product name - 5 nos @ Rs.100"
        r'([A-Za-z][A-Za-z\s]+?)[\s\-]+(\d+(?:\.\d+)?)\s*(?:nos|pcs|units?|kg|ltr)?\s*[@x]\s*(?:Rs\.?|₹|INR)?\s*(\d+(?:\.\d+)?)',
        # "Product name    5    100"
        r'([A-Za-z][A-Za-z\s]{2,30}?)\s{2,}(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)',
        # "5 x Product @ 100"
        r'(\d+(?:\.\d+)?)\s*[x×]\s*([A-Za-z][A-Za-z\s]+?)\s*[@]\s*(?:Rs\.?|₹)?\s*(\d+(?:\.\d+)?)',
    ]
    
    # GST number pattern
    GST_PATTERN = r'(?:GST(?:IN)?|GSTIN)[:\s]*([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})'
    
    def map_text_to_quotation(self, ocr_text: str) -> Dict:
        """
        Extract quotation fields from OCR text
        
        Returns dict with extracted fields and confidence flags
        """
        result = {
            'customer_name': None,
            'customer_phone': None,
            'customer_address': None,
            'customer_gst': None,
            'items': [],
            'confidence_flags': [],  # Fields that need review
            'raw_text': ocr_text
        }
        
        text = ocr_text.strip()
        
        # Extract customer name
        for pattern in self.NAME_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                name = match.group(1).strip()
                if len(name) >= 3 and len(name) <= 100:
                    result['customer_name'] = name
                    break
        
        if not result['customer_name']:
            result['confidence_flags'].append('customer_name')
        
        # Extract phone
        for pattern in self.PHONE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result['customer_phone'] = match.group(1)
                break
        
        if not result['customer_phone']:
            result['confidence_flags'].append('customer_phone')
        
        # Extract GST number
        gst_match = re.search(self.GST_PATTERN, text, re.IGNORECASE)
        if gst_match:
            result['customer_gst'] = gst_match.group(1).upper()
        
        # Extract items
        for pattern in self.ITEM_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                try:
                    if len(match) >= 3:
                        # Handle different pattern formats
                        if match[0].replace('.', '').isdigit():
                            # Pattern: qty x product @ price
                            qty, desc, price = match[0], match[1], match[2]
                        else:
                            # Pattern: product qty price
                            desc, qty, price = match[0], match[1], match[2]
                        
                        item = {
                            'description': desc.strip(),
                            'quantity': float(qty),
                            'unit_price': float(price),
                            'unit': 'nos',
                            'gst_rate': 18.0,
                            'is_free_text': True
                        }
                        
                        # Avoid duplicates
                        if not any(i['description'].lower() == item['description'].lower() 
                                   for i in result['items']):
                            result['items'].append(item)
                except (ValueError, IndexError):
                    continue
        
        if len(result['items']) == 0:
            result['confidence_flags'].append('items')
        
        return result


quotation_mapper = QuotationMapper()
```

### API Endpoints (Week 4)

```python
# Quotation endpoints
POST /api/quotations
- Create new quotation with items
- Auto-calculates GST

GET /api/quotations
- List user's quotations
- Supports pagination, search

GET /api/quotations/{id}
- Get quotation details with items

POST /api/quotations/from-ocr
- Create quotation from OCR text
- Returns mapped fields for review

POST /api/quotations/calculate
- Calculate GST without saving
- For preview purposes

# Product endpoints
POST /api/products
GET /api/products
PUT /api/products/{id}
DELETE /api/products/{id}
```

### Deliverables
- [ ] Quotation tables created
- [ ] Products/Inventory CRUD working
- [ ] GST calculation accurate
- [ ] OCR text maps to quotation fields
- [ ] Create quotation API working

---

## 📅 WEEK 5: Quotation Module - Part 2
**Hours Required:** 6-8 hours

### Tasks

| # | Task | Hours | Priority |
|---|------|-------|----------|
| 1 | Design quotation PDF template (HTML) | 2 | High |
| 2 | Implement PDF generation with WeasyPrint | 1.5 | High |
| 3 | Build quotation update/delete APIs | 1 | High |
| 4 | Build quotation list with search API | 1 | Medium |
| 5 | Create finalize quotation endpoint | 1 | High |
| 6 | Test complete quotation flow | 0.5 | High |

### Code: PDF Generation Service

```python
# app/services/pdf_service.py
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime

class PDFService:
    def __init__(self):
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        self.env = Environment(loader=FileSystemLoader(template_dir))
    
    def generate_quotation_pdf(self, quotation_data: dict) -> bytes:
        """
        Generate quotation PDF from data
        
        Args:
            quotation_data: Complete quotation with items and user info
        
        Returns:
            PDF as bytes
        """
        template = self.env.get_template('quotation.html')
        
        # Add formatting helpers
        quotation_data['generated_date'] = datetime.now().strftime('%d-%m-%Y')
        
        html_content = template.render(**quotation_data)
        
        # Generate PDF
        pdf_bytes = HTML(string=html_content).write_pdf()
        
        return pdf_bytes
    
    def generate_mom_pdf(self, mom_data: dict) -> bytes:
        """Generate MOM PDF"""
        template = self.env.get_template('mom.html')
        html_content = template.render(**mom_data)
        return HTML(string=html_content).write_pdf()
    
    def generate_work_order_pdf(self, work_order_data: dict) -> bytes:
        """Generate Work Order PDF"""
        template = self.env.get_template('work_order.html')
        html_content = template.render(**work_order_data)
        return HTML(string=html_content).write_pdf()


pdf_service = PDFService()
```

### Quotation PDF Template

```html
<!-- app/templates/quotation.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {
            size: A4;
            margin: 1.5cm;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Helvetica', 'Arial', sans-serif;
            font-size: 11px;
            line-height: 1.4;
            color: #333;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            padding-bottom: 15px;
            border-bottom: 2px solid #2c3e50;
            margin-bottom: 20px;
        }
        
        .company-info h1 {
            font-size: 20px;
            color: #2c3e50;
            margin-bottom: 5px;
        }
        
        .company-info p {
            font-size: 10px;
            color: #666;
        }
        
        .logo {
            max-height: 60px;
            max-width: 150px;
        }
        
        .document-title {
            text-align: center;
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            margin: 15px 0;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        .meta-info {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
        }
        
        .meta-box {
            width: 48%;
        }
        
        .meta-box.right {
            text-align: right;
        }
        
        .customer-box {
            background: #f8f9fa;
            padding: 12px;
            border-left: 3px solid #2c3e50;
            margin-bottom: 20px;
        }
        
        .customer-box h3 {
            font-size: 11px;
            color: #666;
            margin-bottom: 5px;
        }
        
        .items-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        
        .items-table th {
            background: #2c3e50;
            color: white;
            padding: 10px 8px;
            text-align: left;
            font-size: 10px;
            text-transform: uppercase;
        }
        
        .items-table td {
            padding: 10px 8px;
            border-bottom: 1px solid #ddd;
        }
        
        .items-table tr:nth-child(even) {
            background: #f8f9fa;
        }
        
        .items-table .number {
            text-align: right;
        }
        
        .totals-section {
            display: flex;
            justify-content: flex-end;
        }
        
        .totals-table {
            width: 280px;
        }
        
        .totals-table td {
            padding: 6px 10px;
        }
        
        .totals-table .label {
            text-align: right;
            color: #666;
        }
        
        .totals-table .value {
            text-align: right;
            font-weight: 500;
        }
        
        .totals-table .grand-total {
            background: #2c3e50;
            color: white;
            font-size: 13px;
            font-weight: bold;
        }
        
        .footer {
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid #ddd;
        }
        
        .terms h4 {
            font-size: 11px;
            margin-bottom: 5px;
        }
        
        .terms p {
            font-size: 9px;
            color: #666;
        }
        
        .signature-section {
            margin-top: 40px;
            display: flex;
            justify-content: space-between;
        }
        
        .signature-box {
            width: 200px;
            text-align: center;
        }
        
        .signature-line {
            border-top: 1px solid #333;
            margin-top: 40px;
            padding-top: 5px;
            font-size: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="company-info">
            {% if company_logo %}
            <img src="{{ company_logo }}" class="logo" alt="Logo">
            {% endif %}
            <h1>{{ company_name }}</h1>
            <p>{{ company_address }}</p>
            <p>Phone: {{ company_phone }}</p>
            {% if company_gst %}<p>GSTIN: {{ company_gst }}</p>{% endif %}
        </div>
    </div>
    
    <div class="document-title">Quotation</div>
    
    <div class="meta-info">
        <div class="meta-box">
            <strong>Quotation No:</strong> {{ quotation_number }}<br>
            <strong>Date:</strong> {{ generated_date }}
        </div>
        <div class="meta-box right">
            <strong>Valid Until:</strong> {{ valid_until }}<br>
        </div>
    </div>
    
    <div class="customer-box">
        <h3>BILL TO</h3>
        <strong>{{ customer_name }}</strong><br>
        {% if customer_address %}{{ customer_address }}<br>{% endif %}
        {% if customer_phone %}Phone: {{ customer_phone }}<br>{% endif %}
        {% if customer_gst %}GSTIN: {{ customer_gst }}{% endif %}
    </div>
    
    <table class="items-table">
        <thead>
            <tr>
                <th style="width: 5%">#</th>
                <th style="width: 40%">Description</th>
                <th style="width: 10%">Qty</th>
                <th style="width: 10%">Unit</th>
                <th style="width: 12%" class="number">Rate (₹)</th>
                <th style="width: 8%" class="number">GST %</th>
                <th style="width: 15%" class="number">Amount (₹)</th>
            </tr>
        </thead>
        <tbody>
            {% for item in items %}
            <tr>
                <td>{{ loop.index }}</td>
                <td>{{ item.description }}</td>
                <td>{{ item.quantity }}</td>
                <td>{{ item.unit }}</td>
                <td class="number">{{ "%.2f"|format(item.unit_price) }}</td>
                <td class="number">{{ item.gst_rate }}%</td>
                <td class="number">{{ "%.2f"|format(item.total) }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    <div class="totals-section">
        <table class="totals-table">
            <tr>
                <td class="label">Subtotal:</td>
                <td class="value">₹ {{ "%.2f"|format(subtotal) }}</td>
            </tr>
            {% if discount_amount > 0 %}
            <tr>
                <td class="label">Discount ({{ discount_percent }}%):</td>
                <td class="value">- ₹ {{ "%.2f"|format(discount_amount) }}</td>
            </tr>
            {% endif %}
            {% if cgst_amount > 0 %}
            <tr>
                <td class="label">CGST ({{ "%.1f"|format(cgst_rate) }}%):</td>
                <td class="value">₹ {{ "%.2f"|format(cgst_amount) }}</td>
            </tr>
            <tr>
                <td class="label">SGST ({{ "%.1f"|format(sgst_rate) }}%):</td>
                <td class="value">₹ {{ "%.2f"|format(sgst_amount) }}</td>
            </tr>
            {% endif %}
            {% if igst_amount > 0 %}
            <tr>
                <td class="label">IGST ({{ "%.1f"|format(igst_rate) }}%):</td>
                <td class="value">₹ {{ "%.2f"|format(igst_amount) }}</td>
            </tr>
            {% endif %}
            <tr class="grand-total">
                <td class="label">Grand Total:</td>
                <td class="value">₹ {{ "%.2f"|format(grand_total) }}</td>
            </tr>
        </table>
    </div>
    
    <div class="footer">
        <div class="terms">
            <h4>Terms & Conditions:</h4>
            <p>{{ terms_conditions or 'Standard terms and conditions apply.' }}</p>
        </div>
        
        <div class="signature-section">
            <div class="signature-box">
                <div class="signature-line">Customer Signature</div>
            </div>
            <div class="signature-box">
                <div class="signature-line">Authorized Signature</div>
            </div>
        </div>
    </div>
</body>
</html>
```

### Deliverables
- [ ] PDF template looks professional
- [ ] PDF generation working
- [ ] Quotation CRUD complete
- [ ] Search/filter working
- [ ] End-to-end flow: OCR → Edit → Preview → PDF

---

## 📅 WEEK 6: MOM Module with NVIDIA NIMs
**Hours Required:** 8 hours (Critical AI Integration)

### Tasks

| # | Task | Hours | Priority |
|---|------|-------|----------|
| 1 | Register for NVIDIA NGC and get API key | 0.5 | High |
| 2 | Create MOM & ActionItems database tables | 1 | High |
| 3 | Build NVIDIA NIMs API integration | 2 | High |
| 4 | Design and test AI prompts | 1.5 | High |
| 5 | Create MOM CRUD APIs | 1.5 | High |
| 6 | Handle AI errors gracefully | 1 | High |
| 7 | Test summarization quality | 0.5 | High |

### NVIDIA NIMs Setup

```bash
# 1. Go to https://build.nvidia.com
# 2. Sign up / Sign in
# 3. Navigate to Llama models
# 4. Get API Key from your profile
# 5. Add to .env:
NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxxxxxxxxx
```

### Code: NVIDIA NIMs AI Service

```python
# app/services/ai_service.py
import requests
import json
import os
from typing import Dict, Optional
import time

class NVIDIANIMsService:
    """
    NVIDIA NIMs integration for AI-powered features
    Using Llama 3.1 for meeting summarization
    """
    
    BASE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
    
    def __init__(self):
        self.api_key = os.getenv("NVIDIA_API_KEY")
        if not self.api_key:
            raise ValueError("NVIDIA_API_KEY not set in environment")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Model selection - use latest Llama available
        self.model = "meta/llama-3.1-70b-instruct"
    
    def summarize_meeting_notes(self, raw_notes: str) -> Dict:
        """
        Summarize meeting notes and extract structured information
        
        Args:
            raw_notes: Raw meeting notes text (typically ~500 words)
        
        Returns:
            Structured MOM data with summary, action items, decisions
        """
        
        prompt = self._build_mom_prompt(raw_notes)
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": """You are a professional meeting assistant. Your task is to analyze meeting notes and extract structured information. Always respond with valid JSON only, no markdown formatting or extra text."""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,  # Low for consistent, factual output
            "max_tokens": 1500,
            "top_p": 0.9
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(
                self.BASE_URL,
                headers=self.headers,
                json=payload,
                timeout=30  # 30 second timeout
            )
            response.raise_for_status()
            
            processing_time = time.time() - start_time
            
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            
            # Parse JSON from response
            parsed_data = self._parse_ai_response(ai_response)
            
            return {
                "success": True,
                "data": parsed_data,
                "processing_time": round(processing_time, 2),
                "model_used": self.model
            }
            
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "AI service timeout. Please try again.",
                "fallback": True
            }
        except requests.exceptions.HTTPError as e:
            return {
                "success": False,
                "error": f"API error: {str(e)}",
                "fallback": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback": True
            }
    
    def _build_mom_prompt(self, raw_notes: str) -> str:
        """Build the prompt for MOM summarization"""
        return f"""Analyze the following meeting notes and extract structured information.

MEETING NOTES:
---
{raw_notes}
---

Extract and return a JSON object with this exact structure:
{{
    "meeting_title": "A brief, descriptive title for this meeting (max 10 words)",
    "summary": "A 2-3 sentence executive summary of what was discussed",
    "key_discussion_points": [
        "First main topic discussed",
        "Second main topic discussed",
        "Third main topic discussed"
    ],
    "decisions_made": [
        "First decision that was made",
        "Second decision that was made"
    ],
    "action_items": [
        {{
            "task": "Clear description of what needs to be done",
            "assigned_to": "Person's name or 'Unassigned' if not mentioned",
            "deadline": "Date in YYYY-MM-DD format or 'TBD' if not mentioned",
            "priority": "high" or "medium" or "low"
        }}
    ],
    "next_meeting": "Date/time if mentioned, otherwise null",
    "attendees_mentioned": ["Name 1", "Name 2"]
}}

Rules:
1. Only include information that is explicitly stated or clearly implied
2. Keep discussion points concise (max 15 words each)
3. Action items must be specific and actionable
4. If no decisions were made, use an empty array
5. Respond with ONLY the JSON object, no other text"""

    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parse and validate AI response"""
        # Clean up response
        text = response_text.strip()
        
        # Remove markdown code blocks if present
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1])
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        
        text = text.strip()
        
        try:
            data = json.loads(text)
            
            # Validate required fields
            required_fields = ['meeting_title', 'summary', 'key_discussion_points', 
                             'decisions_made', 'action_items']
            for field in required_fields:
                if field not in data:
                    data[field] = [] if field in ['key_discussion_points', 
                                                   'decisions_made', 
                                                   'action_items'] else ""
            
            return data
            
        except json.JSONDecodeError as e:
            # Return partial data if parsing fails
            return {
                "meeting_title": "Meeting Summary",
                "summary": response_text[:500],
                "key_discussion_points": [],
                "decisions_made": [],
                "action_items": [],
                "parse_error": str(e)
            }
    
    def get_available_models(self) -> list:
        """Get list of available models from NVIDIA"""
        try:
            response = requests.get(
                "https://integrate.api.nvidia.com/v1/models",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            models = response.json()
            return [m['id'] for m in models.get('data', [])]
        except Exception:
            return [self.model]  # Return default


# Singleton instance
nvidia_ai_service = NVIDIANIMsService()
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
    attendees JSON,  -- ["Person 1", "Person 2"]
    agenda TEXT,
    raw_notes TEXT NOT NULL,
    ai_summary TEXT,
    discussion_points JSON,  -- ["Point 1", "Point 2"]
    decisions JSON,  -- ["Decision 1", "Decision 2"]
    next_meeting_date DATETIME,
    ai_processing_time DECIMAL(5,2),
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
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
    FOREIGN KEY (mom_id) REFERENCES moms(id) ON DELETE CASCADE
);

-- Index for faster queries
CREATE INDEX idx_action_items_status ON action_items(status);
CREATE INDEX idx_action_items_assigned ON action_items(assigned_to);
```

### MOM API Endpoints

```python
# MOM Endpoints

POST /api/moms
- Create MOM with raw notes
- Optionally trigger AI summarization

POST /api/moms/summarize
- Summarize raw notes without saving
- For preview before creating

GET /api/moms
- List user's MOMs

GET /api/moms/{id}
- Get MOM with action items

PUT /api/moms/{id}
- Update MOM details

PUT /api/moms/{id}/action-items/{item_id}
- Update action item status

POST /api/moms/{id}/finalize
- Finalize and generate PDF
```

### Deliverables
- [ ] NVIDIA NIMs API connected
- [ ] Llama model responding
- [ ] Meeting summarization working
- [ ] Response time < 7 seconds
- [ ] Action items extracted correctly
- [ ] MOM CRUD APIs complete

---

## 📅 WEEK 7: Work Order Module + Integration
**Hours Required:** 6-8 hours

### Tasks

| # | Task | Hours | Priority |
|---|------|-------|----------|
| 1 | Create Work Order database tables | 1 | High |
| 2 | Build Work Order CRUD APIs | 2 | High |
| 3 | Implement photo upload (before/after) | 1 | High |
| 4 | Build labor cost calculation | 0.5 | High |
| 5 | Link quotation to work order | 1 | Medium |
| 6 | Create Work Order PDF template | 1 | High |
| 7 | Generate MOM PDF template | 0.5 | Medium |

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
    labor_hours DECIMAL(6,2) DEFAULT 0,
    labor_rate DECIMAL(10,2) DEFAULT 0,
    labor_cost DECIMAL(12,2) DEFAULT 0,
    material_cost DECIMAL(12,2) DEFAULT 0,
    total_cost DECIMAL(12,2) DEFAULT 0,
    status ENUM('pending', 'in_progress', 'completed', 'cancelled') DEFAULT 'pending',
    before_photo_url VARCHAR(500),
    after_photo_url VARCHAR(500),
    customer_signature_url VARCHAR(500),
    remarks TEXT,
    completed_at TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (linked_quotation_id) REFERENCES quotations(id) ON SET NULL
);

-- Work Order Materials
CREATE TABLE work_order_materials (
    id VARCHAR(36) PRIMARY KEY,
    work_order_id VARCHAR(36) NOT NULL,
    material_name VARCHAR(200) NOT NULL,
    quantity DECIMAL(10,2) DEFAULT 1,
    unit VARCHAR(20) DEFAULT 'nos',
    unit_cost DECIMAL(12,2) DEFAULT 0,
    total_cost DECIMAL(12,2) DEFAULT 0,
    FOREIGN KEY (work_order_id) REFERENCES work_orders(id) ON DELETE CASCADE
);
```

### Code: Work Order Cost Calculator

```python
# app/services/work_order_service.py
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict

def calculate_work_order_costs(
    labor_hours: float,
    labor_rate: float,
    materials: List[Dict]
) -> Dict:
    """
    Calculate total work order costs
    
    Args:
        labor_hours: Total hours worked
        labor_rate: Rate per hour (INR)
        materials: List of {quantity, unit_cost}
    
    Returns:
        Cost breakdown
    """
    labor_hours = Decimal(str(labor_hours))
    labor_rate = Decimal(str(labor_rate))
    
    labor_cost = (labor_hours * labor_rate).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )
    
    material_cost = Decimal('0')
    calculated_materials = []
    
    for mat in materials:
        qty = Decimal(str(mat.get('quantity', 1)))
        unit_cost = Decimal(str(mat.get('unit_cost', 0)))
        mat_total = (qty * unit_cost).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        material_cost += mat_total
        
        calculated_materials.append({
            **mat,
            'total_cost': float(mat_total)
        })
    
    total_cost = labor_cost + material_cost
    
    return {
        'labor_hours': float(labor_hours),
        'labor_rate': float(labor_rate),
        'labor_cost': float(labor_cost),
        'materials': calculated_materials,
        'material_cost': float(material_cost),
        'total_cost': float(total_cost)
    }
```

### Deliverables
- [ ] Work Order CRUD complete
- [ ] Materials tracking working
- [ ] Photo upload working
- [ ] Labor cost calculation correct
- [ ] Quotation linking working
- [ ] All three PDFs generating

---

## 📅 WEEK 8: Dashboard, Testing & Deployment
**Hours Required:** 8 hours

### Tasks

| # | Task | Hours | Priority |
|---|------|-------|----------|
| 1 | Build dashboard stats API | 1 | High |
| 2 | Build document search API | 1 | Medium |
| 3 | Fix bugs and optimize queries | 1.5 | High |
| 4 | Setup Railway project | 1 | High |
| 5 | Configure environment variables | 0.5 | High |
| 6 | Deploy backend to Railway | 1.5 | High |
| 7 | Test deployed application | 1 | High |
| 8 | Create API documentation | 0.5 | Medium |

### Code: Dashboard Stats API

```python
# app/routers/dashboard.py
from fastapi import APIRouter, Depends
from sqlalchemy import func
from app.database import get_db
from app.models import Document, Quotation, MOM, WorkOrder
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats")
async def get_dashboard_stats(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    user_id = current_user['user_id']
    
    # Count documents by type
    quotation_count = db.query(func.count(Document.id)).filter(
        Document.user_id == user_id,
        Document.document_type == 'quotation'
    ).scalar()
    
    mom_count = db.query(func.count(Document.id)).filter(
        Document.user_id == user_id,
        Document.document_type == 'mom'
    ).scalar()
    
    work_order_count = db.query(func.count(Document.id)).filter(
        Document.user_id == user_id,
        Document.document_type == 'work_order'
    ).scalar()
    
    # Recent documents
    recent_docs = db.query(Document).filter(
        Document.user_id == user_id
    ).order_by(Document.created_at.desc()).limit(5).all()
    
    # Pending action items
    pending_actions = db.query(func.count(ActionItem.id)).join(
        MOM, ActionItem.mom_id == MOM.id
    ).join(
        Document, MOM.document_id == Document.id
    ).filter(
        Document.user_id == user_id,
        ActionItem.status == 'pending'
    ).scalar()
    
    return {
        "total_documents": quotation_count + mom_count + work_order_count,
        "quotations": quotation_count,
        "moms": mom_count,
        "work_orders": work_order_count,
        "pending_action_items": pending_actions,
        "recent_documents": [
            {
                "id": doc.id,
                "type": doc.document_type,
                "title": doc.title,
                "status": doc.status,
                "created_at": doc.created_at.isoformat()
            }
            for doc in recent_docs
        ]
    }
```

### Railway Deployment Steps

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login to Railway
railway login

# 3. Initialize project
railway init

# 4. Add MySQL database
railway add --database mysql

# 5. Set environment variables in Railway dashboard:
# - DATABASE_URL (auto-set by Railway)
# - JWT_SECRET
# - NVIDIA_API_KEY
# - GOOGLE_APPLICATION_CREDENTIALS (base64 encoded)
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
# - S3_BUCKET_NAME

# 6. Deploy
railway up

# 7. Get deployment URL
railway domain
```

### Environment Variables (.env.example)

```env
# Database
DATABASE_URL=mysql://user:password@localhost:3306/docgen

# Authentication
JWT_SECRET=your-super-secret-jwt-key-min-32-chars

# NVIDIA NIMs
NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxxxxxxxxxxxxx

# Google Cloud Vision
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# AWS S3 (or use Cloudinary)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=ap-south-1
S3_BUCKET_NAME=your-bucket-name

# Cloudinary (alternative to S3)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# App Settings
DEBUG=False
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
```

### Deliverables
- [ ] Dashboard API working
- [ ] Search working
- [ ] All bugs fixed
- [ ] Backend deployed on Railway
- [ ] Environment variables configured
- [ ] Production database running
- [ ] API accessible via public URL

---

# COMPLETE API REFERENCE

## Authentication APIs
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login, get JWT |
| GET | `/api/auth/profile` | Get user profile |
| PUT | `/api/auth/profile` | Update profile |

## OCR APIs
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ocr/extract` | Extract text from image |

## Quotation APIs
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/quotations` | Create quotation |
| GET | `/api/quotations` | List quotations |
| GET | `/api/quotations/{id}` | Get quotation |
| PUT | `/api/quotations/{id}` | Update quotation |
| DELETE | `/api/quotations/{id}` | Delete quotation |
| POST | `/api/quotations/from-ocr` | Create from OCR text |
| POST | `/api/quotations/calculate` | Calculate GST |
| POST | `/api/quotations/{id}/finalize` | Generate PDF |
| GET | `/api/quotations/{id}/download` | Download PDF |

## Product APIs
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/products` | Create product |
| GET | `/api/products` | List products |
| PUT | `/api/products/{id}` | Update product |
| DELETE | `/api/products/{id}` | Delete product |

## MOM APIs
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/moms` | Create MOM |
| GET | `/api/moms` | List MOMs |
| GET | `/api/moms/{id}` | Get MOM with actions |
| PUT | `/api/moms/{id}` | Update MOM |
| DELETE | `/api/moms/{id}` | Delete MOM |
| POST | `/api/moms/summarize` | AI summarize (preview) |
| PUT | `/api/moms/{id}/actions/{action_id}` | Update action status |
| POST | `/api/moms/{id}/finalize` | Generate PDF |

## Work Order APIs
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/work-orders` | Create work order |
| GET | `/api/work-orders` | List work orders |
| GET | `/api/work-orders/{id}` | Get work order |
| PUT | `/api/work-orders/{id}` | Update work order |
| DELETE | `/api/work-orders/{id}` | Delete work order |
| POST | `/api/work-orders/{id}/photos` | Upload photos |
| POST | `/api/work-orders/{id}/signature` | Save signature |
| POST | `/api/work-orders/{id}/finalize` | Generate PDF |

## Dashboard APIs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/stats` | Get dashboard stats |
| GET | `/api/documents/search` | Search documents |

---

# WEEKLY CHECKLIST SUMMARY

| Week | Focus | Key Deliverables | Hours |
|------|-------|------------------|-------|
| 1 | Setup | Repo, FastAPI, MySQL, Schema | 6-8 |
| 2 | Auth | Login, Register, JWT, Profile | 6-8 |
| 3 | OCR | Google Vision, Preprocessing | 8 |
| 4 | Quotation P1 | APIs, GST, Field Mapping | 6-8 |
| 5 | Quotation P2 | PDF, CRUD, Full Flow | 6-8 |
| 6 | MOM + AI | NVIDIA NIMs, Summarization | 8 |
| 7 | Work Order | APIs, Photos, Linking | 6-8 |
| 8 | Deploy | Railway, Testing, Docs | 8 |

**Total Backend Hours: 54-66 hours**

---

# RESOURCES & LINKS

- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Google Cloud Vision:** https://cloud.google.com/vision/docs
- **NVIDIA NIMs:** https://build.nvidia.com
- **WeasyPrint:** https://weasyprint.org
- **Railway:** https://railway.app/docs
- **SQLAlchemy:** https://docs.sqlalchemy.org

---

**Document Version:** 1.0  
**Last Updated:** January 2025  
**Developer:** Backend Lead