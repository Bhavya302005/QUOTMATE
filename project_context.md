# QuotMate - Project Context & Architecture

## Overview
**QuotMate** is an AI-powered SaaS application designed to streamline the creation, management, and export of business documents. It primarily focuses on three types of documents:
1. **Quotations** (Estimates/Invoices) with Indian GST calculation support.
2. **Minutes of Meeting (MOM)** with AI-powered summarization and action-item extraction.
3. **Work Orders** (Project execution blueprints).

The platform heavily leverages AI (NVIDIA NIMs / LLaMA vision models) to parse handwritten notes or images and automatically draft structured digital documents. Users can then edit these documents in a sophisticated React frontend and export them to professional PDFs.

---

## Tech Stack

### Backend (`/backend`)
- **Framework:** FastAPI (Python 3.12+)
- **Database:** PostgreSQL (hosted on Aiven)
- **ORM:** SQLAlchemy with Alembic for migrations
- **Authentication:** JWT (JSON Web Tokens) with `python-jose` and `passlib`
- **AI/LLM Integration:** NVIDIA NIMs API (using `llama-3.2-11b-vision-instruct` and `llama-3.3-70b-instruct`) for OCR and document understanding.
- **PDF Generation:** WeasyPrint with Jinja2 HTML templates.
- **Image Processing:** OpenCV (`cv2`) for image deskewing and perspective correction before sending to the OCR pipeline.

### Frontend (`/frontend`)
- **Framework:** React 18 (Vite)
- **Styling:** Tailwind CSS (Modern, soft UI design - recently transitioned from a brutalist theme)
- **State Management/Rendering:** React Hooks, React Router DOM
- **Forms:** React Hook Form (`react-hook-form`)
- **Icons:** Lucide React

---

## Core Features & Workflows

### 1. Authentication & Users
- Standard Email/Password login and registration flow.
- Users have profiles containing company details (name, GST number, logo, address) which are automatically injected into generated PDFs.

### 2. AI Document Generation (The "Magic" Flow)
- Users upload an image (e.g., a photo of a handwritten quotation or meeting notes).
- **Image Preprocessing:** The backend (`image_preprocessing.py`) uses OpenCV to deskew and correct the perspective of the image.
- **OCR Pipeline:** The image is sent to NVIDIA NIMs Vision API to extract raw text and structural metadata. A secondary LLM pass cleans up hallucinated text and formats it into a strict JSON schema.
- **Drafting:** The corresponding document (Quotation or MOM) is created in a `DRAFT` state and populated with the parsed data.

### 3. Quotation Management
- Complex line-item management with dynamic Indian GST calculations (CGST, SGST, IGST).
- **Features:** 
  - Dynamic GST toggling (ability to completely remove tax from a document).
  - Manual Total Overrides (ability to bypass calculations and supply a flat "Estimated Cost", automatically zeroing out item prices).
  - Discount applications.

### 4. Minutes of Meeting (MOM)
- **AI Processing:** Uses LLMs to take raw meeting transcripts or notes and summarize them into Key Points, Decisions, and Assignable Action Items.

### 5. PDF Export
- Backend `pdf_service.py` takes the SQLAlchemy models, passes them into Jinja2 HTML templates (`quotation.html`, `mom.html`), applies CSS, and uses WeasyPrint to generate a downloadable PDF.
- The PDF engine respects layout rules like hiding tax columns if GST is toggled off, or replacing item prices with a unified "Estimated Cost" if a manual override is applied.

---

## Directory Structure Overview

### Backend
```text
backend/
├── alembic.ini             # Database migration configuration
├── requirements.txt        # Python dependencies
├── start.sh                # Server startup script
├── app/
│   ├── main.py             # FastAPI application entry point
│   ├── database.py         # SQLAlchemy engine and session setup
│   ├── config.py           # Environment variables (Pydantic Settings)
│   ├── models/             # SQLAlchemy DB Models (document.py, quotation.py, user.py)
│   ├── schemas/            # Pydantic Schemas for API validation
│   ├── routers/            # API Endpoints (auth.py, ocr.py, quotations.py, mom.py)
│   ├── services/           # Core business logic
│   │   ├── ocr_service.py          # Orchestrates image prep and LLM parsing
│   │   ├── nvidia_nims_service.py  # Handles API calls to NVIDIA LLaMA models
│   │   ├── image_preprocessing.py  # OpenCV image correction
│   │   ├── gst_calculator.py       # Tax calculation logic
│   │   └── pdf_service.py          # WeasyPrint PDF generation
│   ├── templates/          # Jinja2 HTML templates for PDF rendering
│   └── utils/              # Helper functions (auth_utils.py, file_upload.py)
└── migrations/             # Alembic migration versions
```

### Frontend
```text
frontend/
├── index.html              # Vite entry point
├── package.json            # Node dependencies
├── tailwind.config.js      # Tailwind theme configuration
├── vite.config.js          # Vite configuration
├── src/
│   ├── App.jsx             # Main React component and Route definitions
│   ├── index.css           # Global CSS and Tailwind directives
│   ├── api/                # Axios API client setups (client.js, services)
│   ├── components/         # Reusable React components
│   │   ├── layout/         # Sidebar, Header, PageWrappers
│   │   ├── quotation/      # QuotationForm, LineItems, GSTSummary, QuotationPreview
│   │   ├── mom/            # MOM Form, ActionItems, AI Summary display
│   │   └── common/         # Buttons, Inputs, EmptyStates
│   ├── pages/              # Top-level route pages (Dashboard, LoginPage, QuotationCreate)
│   └── utils/              # Frontend helpers (cn.js for class merging)
```

## Key Architectural Decisions & Nuances
1. **Document Abstraction:** There is a base `Document` model that handles generic states (Draft, Review, Finalized) and ownership. Specific types (like `Quotation` or `MOM`) have their own tables and link back to a parent `Document` via `document_id`.
2. **Stateless OCR:** The OCR endpoints (`/api/ocr/*`) are mostly stateless. They take an image, process it, and return the structured JSON data. The frontend is responsible for taking that JSON and POSTing it to the create document endpoints (`/api/quotations`, etc.).
3. **Database Migrations:** Alembic is strictly used. When modifying SQLAlchemy models, `alembic revision --autogenerate -m "..."` and `alembic upgrade head` are required.
4. **Soft Deletes:** Documents aren't generally soft-deleted right now, standard `DELETE` cascades down to line items.
