# COMPLETE PROJECT STRUCTURE
## Smart Business Document Generator
### Full-Stack Application (Backend + Frontend)

---

# 📁 ROOT DIRECTORY STRUCTURE

```
smart-doc-generator/
│
├── 📁 backend/                    # Python FastAPI Backend
├── 📁 frontend/                   # React Frontend
├── 📁 docs/                       # Documentation
├── 📁 scripts/                    # Utility scripts
├── .gitignore                     # Git ignore rules
├── README.md                      # Project overview
├── docker-compose.yml             # Docker setup (optional)
└── Makefile                       # Common commands
```

---

# 📁 BACKEND STRUCTURE (Python + FastAPI)

```
backend/
│
├── 📁 app/
│   │
│   ├── __init__.py
│   ├── main.py                           # FastAPI application entry point
│   ├── config.py                         # Configuration & environment variables
│   ├── database.py                       # Database connection & session
│   │
│   ├── 📁 models/                        # SQLAlchemy ORM Models
│   │   ├── __init__.py
│   │   ├── base.py                       # Base model class
│   │   ├── user.py                       # User model
│   │   ├── document.py                   # Document base model
│   │   ├── quotation.py                  # Quotation & QuotationItem models
│   │   ├── product.py                    # Product/Inventory model
│   │   ├── mom.py                        # MOM & ActionItem models
│   │   ├── work_order.py                 # WorkOrder & WorkOrderMaterial models
│   │   └── audit_log.py                  # AuditLog model
│   │
│   ├── 📁 schemas/                       # Pydantic Schemas (Request/Response)
│   │   ├── __init__.py
│   │   ├── user.py                       # User schemas
│   │   │   ├── UserCreate
│   │   │   ├── UserLogin
│   │   │   ├── UserResponse
│   │   │   └── UserUpdate
│   │   ├── document.py                   # Document schemas
│   │   ├── quotation.py                  # Quotation schemas
│   │   │   ├── QuotationCreate
│   │   │   ├── QuotationUpdate
│   │   │   ├── QuotationResponse
│   │   │   ├── QuotationItemCreate
│   │   │   └── GSTCalculationRequest
│   │   ├── product.py                    # Product schemas
│   │   ├── mom.py                        # MOM schemas
│   │   │   ├── MOMCreate
│   │   │   ├── MOMResponse
│   │   │   ├── ActionItemCreate
│   │   │   ├── ActionItemUpdate
│   │   │   └── AISummarizeRequest
│   │   ├── work_order.py                 # WorkOrder schemas
│   │   │   ├── WorkOrderCreate
│   │   │   ├── WorkOrderUpdate
│   │   │   ├── WorkOrderResponse
│   │   │   └── MaterialCreate
│   │   ├── ocr.py                        # OCR schemas
│   │   │   ├── OCRExtractResponse
│   │   │   └── OCRMapRequest
│   │   └── dashboard.py                  # Dashboard schemas
│   │
│   ├── 📁 routers/                       # API Route Handlers
│   │   ├── __init__.py
│   │   ├── auth.py                       # /api/auth/*
│   │   │   ├── POST /register
│   │   │   ├── POST /login
│   │   │   ├── GET  /profile
│   │   │   └── PUT  /profile
│   │   ├── ocr.py                        # /api/ocr/*
│   │   │   └── POST /extract
│   │   ├── quotations.py                 # /api/quotations/*
│   │   │   ├── POST   /
│   │   │   ├── GET    /
│   │   │   ├── GET    /{id}
│   │   │   ├── PUT    /{id}
│   │   │   ├── DELETE /{id}
│   │   │   ├── POST   /from-ocr
│   │   │   ├── POST   /calculate
│   │   │   ├── POST   /{id}/finalize
│   │   │   └── GET    /{id}/download
│   │   ├── products.py                   # /api/products/*
│   │   │   ├── POST   /
│   │   │   ├── GET    /
│   │   │   ├── PUT    /{id}
│   │   │   └── DELETE /{id}
│   │   ├── moms.py                       # /api/moms/*
│   │   │   ├── POST   /
│   │   │   ├── GET    /
│   │   │   ├── GET    /{id}
│   │   │   ├── PUT    /{id}
│   │   │   ├── DELETE /{id}
│   │   │   ├── POST   /summarize
│   │   │   ├── PUT    /{id}/actions/{action_id}
│   │   │   ├── POST   /{id}/finalize
│   │   │   └── GET    /{id}/download
│   │   ├── work_orders.py                # /api/work-orders/*
│   │   │   ├── POST   /
│   │   │   ├── GET    /
│   │   │   ├── GET    /{id}
│   │   │   ├── PUT    /{id}
│   │   │   ├── DELETE /{id}
│   │   │   ├── POST   /{id}/photos
│   │   │   ├── POST   /{id}/signature
│   │   │   ├── POST   /{id}/finalize
│   │   │   └── GET    /{id}/download
│   │   ├── dashboard.py                  # /api/dashboard/*
│   │   │   ├── GET /stats
│   │   │   └── GET /search
│   │   └── uploads.py                    # /api/uploads/*
│   │       └── POST /image
│   │
│   ├── 📁 services/                      # Business Logic Services
│   │   ├── __init__.py
│   │   ├── auth_service.py               # Authentication logic
│   │   │   ├── create_user()
│   │   │   ├── authenticate_user()
│   │   │   └── get_current_user()
│   │   ├── ocr_service.py                # OCR Processing
│   │   │   ├── preprocess_image()
│   │   │   ├── extract_text_google_vision()
│   │   │   └── calculate_confidence()
│   │   ├── ai_service.py                 # NVIDIA NIMs AI Integration
│   │   │   ├── summarize_meeting_notes()
│   │   │   ├── _build_mom_prompt()
│   │   │   └── _parse_ai_response()
│   │   ├── gst_calculator.py             # GST Calculation
│   │   │   └── calculate_gst()
│   │   ├── quotation_mapper.py           # OCR to Quotation Field Mapping
│   │   │   └── map_text_to_quotation()
│   │   ├── pdf_service.py                # PDF Generation
│   │   │   ├── generate_quotation_pdf()
│   │   │   ├── generate_mom_pdf()
│   │   │   └── generate_work_order_pdf()
│   │   ├── file_service.py               # File Upload/Download
│   │   │   ├── upload_to_s3()
│   │   │   ├── upload_to_cloudinary()
│   │   │   └── delete_file()
│   │   ├── work_order_service.py         # Work Order Business Logic
│   │   │   └── calculate_costs()
│   │   └── audit_service.py              # Audit Logging
│   │       └── log_audit()
│   │
│   ├── 📁 utils/                         # Utility Functions
│   │   ├── __init__.py
│   │   ├── auth.py                       # JWT utilities
│   │   │   ├── hash_password()
│   │   │   ├── verify_password()
│   │   │   ├── create_access_token()
│   │   │   ├── decode_token()
│   │   │   └── get_current_user()  (dependency)
│   │   ├── helpers.py                    # General helpers
│   │   │   ├── generate_uuid()
│   │   │   ├── generate_document_number()
│   │   │   └── format_currency()
│   │   ├── validators.py                 # Input validators
│   │   │   ├── validate_email()
│   │   │   ├── validate_phone()
│   │   │   └── validate_gst_number()
│   │   └── exceptions.py                 # Custom exceptions
│   │       ├── NotFoundException
│   │       ├── UnauthorizedException
│   │       └── ValidationException
│   │
│   └── 📁 templates/                     # PDF HTML Templates (Jinja2)
│       ├── base.html                     # Base template
│       ├── quotation.html                # Quotation PDF template
│       ├── mom.html                      # MOM PDF template
│       └── work_order.html               # Work Order PDF template
│
├── 📁 migrations/                        # Database Migrations (Alembic)
│   ├── env.py
│   ├── script.py.mako
│   └── 📁 versions/
│       ├── 001_create_users_table.py
│       ├── 002_create_documents_table.py
│       ├── 003_create_quotations_tables.py
│       ├── 004_create_products_table.py
│       ├── 005_create_moms_tables.py
│       ├── 006_create_work_orders_tables.py
│       └── 007_create_audit_logs_table.py
│
├── 📁 tests/                             # Test Files
│   ├── __init__.py
│   ├── conftest.py                       # Pytest fixtures
│   ├── 📁 test_routers/
│   │   ├── test_auth.py
│   │   ├── test_quotations.py
│   │   ├── test_moms.py
│   │   └── test_work_orders.py
│   ├── 📁 test_services/
│   │   ├── test_ocr_service.py
│   │   ├── test_ai_service.py
│   │   ├── test_gst_calculator.py
│   │   └── test_pdf_service.py
│   └── 📁 test_data/
│       ├── sample_handwritten_1.jpg
│       ├── sample_handwritten_2.jpg
│       └── sample_meeting_notes.txt
│
├── 📁 scripts/                           # Utility Scripts
│   ├── create_admin.py                   # Create admin user
│   ├── seed_products.py                  # Seed sample products
│   └── test_ocr.py                       # Test OCR with sample images
│
├── .env.example                          # Environment variables template
├── .gitignore                            # Git ignore
├── requirements.txt                      # Python dependencies
├── Dockerfile                            # Docker configuration
├── alembic.ini                           # Alembic configuration
└── README.md                             # Backend documentation
```

---

# 📁 FRONTEND STRUCTURE (React + Tailwind)

```
frontend/
│
├── 📁 public/
│   ├── index.html
│   ├── favicon.ico
│   ├── logo192.png
│   ├── logo512.png
│   ├── manifest.json
│   └── robots.txt
│
├── 📁 src/
│   │
│   ├── 📁 assets/                        # Static Assets
│   │   ├── 📁 images/
│   │   │   ├── logo.svg
│   │   │   ├── empty-state.svg
│   │   │   └── auth-bg.jpg
│   │   └── 📁 icons/
│   │       └── (custom icons if any)
│   │
│   ├── 📁 components/                    # Reusable Components
│   │   │
│   │   ├── 📁 common/                    # Generic UI Components
│   │   │   ├── Button.jsx
│   │   │   ├── Input.jsx
│   │   │   ├── TextArea.jsx
│   │   │   ├── Select.jsx
│   │   │   ├── Card.jsx
│   │   │   ├── Modal.jsx
│   │   │   ├── Drawer.jsx
│   │   │   ├── LoadingSpinner.jsx
│   │   │   ├── LoadingOverlay.jsx
│   │   │   ├── ErrorMessage.jsx
│   │   │   ├── EmptyState.jsx
│   │   │   ├── ConfirmDialog.jsx
│   │   │   ├── Badge.jsx
│   │   │   ├── Avatar.jsx
│   │   │   ├── Tabs.jsx
│   │   │   ├── Pagination.jsx
│   │   │   └── index.js                  # Export all common components
│   │   │
│   │   ├── 📁 layout/                    # Layout Components
│   │   │   ├── AppLayout.jsx             # Main app layout wrapper
│   │   │   ├── AuthLayout.jsx            # Auth pages layout
│   │   │   ├── Header.jsx                # Top header bar
│   │   │   ├── BottomTabBar.jsx          # Mobile bottom navigation
│   │   │   ├── Sidebar.jsx               # Desktop sidebar (if needed)
│   │   │   ├── PageHeader.jsx            # Page title & back button
│   │   │   └── index.js
│   │   │
│   │   ├── 📁 auth/                      # Authentication Components
│   │   │   ├── LoginForm.jsx
│   │   │   ├── RegisterForm.jsx
│   │   │   ├── ForgotPasswordForm.jsx
│   │   │   ├── ProtectedRoute.jsx
│   │   │   └── index.js
│   │   │
│   │   ├── 📁 ocr/                       # OCR Related Components
│   │   │   ├── ImageUpload.jsx           # Camera/Gallery picker
│   │   │   ├── ImagePreview.jsx          # Preview before upload
│   │   │   ├── OCRResult.jsx             # Display extracted text
│   │   │   ├── ConfidenceIndicator.jsx   # Confidence score display
│   │   │   ├── FieldMapper.jsx           # Map OCR to form fields
│   │   │   └── index.js
│   │   │
│   │   ├── 📁 quotation/                 # Quotation Module Components
│   │   │   ├── QuotationForm.jsx         # Main quotation form
│   │   │   ├── QuotationList.jsx         # List all quotations
│   │   │   ├── QuotationCard.jsx         # Single quotation card
│   │   │   ├── QuotationPreview.jsx      # Preview before finalize
│   │   │   ├── QuotationDetail.jsx       # View quotation details
│   │   │   ├── CustomerDetails.jsx       # Customer info section
│   │   │   ├── LineItems.jsx             # Dynamic line items
│   │   │   ├── LineItemRow.jsx           # Single line item
│   │   │   ├── ProductSelector.jsx       # Select from inventory
│   │   │   ├── GSTSummary.jsx            # GST calculation display
│   │   │   ├── DiscountInput.jsx         # Discount controls
│   │   │   └── index.js
│   │   │
│   │   ├── 📁 mom/                       # MOM Module Components
│   │   │   ├── MOMForm.jsx               # Main MOM form
│   │   │   ├── MOMList.jsx               # List all MOMs
│   │   │   ├── MOMCard.jsx               # Single MOM card
│   │   │   ├── MOMPreview.jsx            # Preview before finalize
│   │   │   ├── MOMDetail.jsx             # View MOM details
│   │   │   ├── MeetingDetails.jsx        # Meeting info section
│   │   │   ├── AttendeesList.jsx         # Manage attendees
│   │   │   ├── MeetingNotes.jsx          # Notes textarea
│   │   │   ├── AISummarizeButton.jsx     # AI summarization trigger
│   │   │   ├── AISummaryDisplay.jsx      # Display AI summary
│   │   │   ├── DiscussionPoints.jsx      # Discussion points list
│   │   │   ├── DecisionsList.jsx         # Decisions list
│   │   │   ├── ActionItems.jsx           # Action items management
│   │   │   ├── ActionItemRow.jsx         # Single action item
│   │   │   ├── ActionItemStatus.jsx      # Status badge/selector
│   │   │   └── index.js
│   │   │
│   │   ├── 📁 work-order/                # Work Order Module Components
│   │   │   ├── WorkOrderForm.jsx         # Main work order form
│   │   │   ├── WorkOrderList.jsx         # List all work orders
│   │   │   ├── WorkOrderCard.jsx         # Single work order card
│   │   │   ├── WorkOrderPreview.jsx      # Preview before finalize
│   │   │   ├── WorkOrderDetail.jsx       # View work order details
│   │   │   ├── ClientDetails.jsx         # Client info section
│   │   │   ├── WorkDescription.jsx       # Work description
│   │   │   ├── MaterialsList.jsx         # Materials management
│   │   │   ├── MaterialRow.jsx           # Single material row
│   │   │   ├── LaborCost.jsx             # Labor hours & cost
│   │   │   ├── PhotoUpload.jsx           # Before/After photos
│   │   │   ├── PhotoPreview.jsx          # Photo preview
│   │   │   ├── SignaturePad.jsx          # Digital signature
│   │   │   ├── StatusSelector.jsx        # Work order status
│   │   │   ├── QuotationLinker.jsx       # Link to quotation
│   │   │   └── index.js
│   │   │
│   │   ├── 📁 product/                   # Product/Inventory Components
│   │   │   ├── ProductList.jsx
│   │   │   ├── ProductForm.jsx
│   │   │   ├── ProductCard.jsx
│   │   │   └── index.js
│   │   │
│   │   ├── 📁 dashboard/                 # Dashboard Components
│   │   │   ├── StatsCards.jsx            # Statistics cards
│   │   │   ├── QuickActions.jsx          # Quick action buttons
│   │   │   ├── RecentDocuments.jsx       # Recent documents list
│   │   │   ├── PendingActions.jsx        # Pending action items
│   │   │   └── index.js
│   │   │
│   │   └── 📁 profile/                   # Profile Components
│   │       ├── ProfileForm.jsx
│   │       ├── CompanyDetails.jsx
│   │       ├── LogoUpload.jsx
│   │       └── index.js
│   │
│   ├── 📁 pages/                         # Page Components (Routes)
│   │   ├── 📁 auth/
│   │   │   ├── LoginPage.jsx
│   │   │   ├── RegisterPage.jsx
│   │   │   └── ForgotPasswordPage.jsx
│   │   ├── 📁 dashboard/
│   │   │   └── DashboardPage.jsx
│   │   ├── 📁 quotation/
│   │   │   ├── QuotationsPage.jsx        # List page
│   │   │   ├── NewQuotationPage.jsx      # Create new
│   │   │   ├── QuotationDetailPage.jsx   # View/Edit
│   │   │   └── QuotationPreviewPage.jsx  # Preview & finalize
│   │   ├── 📁 mom/
│   │   │   ├── MOMsPage.jsx              # List page
│   │   │   ├── NewMOMPage.jsx            # Create new
│   │   │   ├── MOMDetailPage.jsx         # View/Edit
│   │   │   └── MOMPreviewPage.jsx        # Preview & finalize
│   │   ├── 📁 work-order/
│   │   │   ├── WorkOrdersPage.jsx        # List page
│   │   │   ├── NewWorkOrderPage.jsx      # Create new
│   │   │   ├── WorkOrderDetailPage.jsx   # View/Edit
│   │   │   └── WorkOrderPreviewPage.jsx  # Preview & finalize
│   │   ├── 📁 product/
│   │   │   └── ProductsPage.jsx          # Inventory management
│   │   ├── 📁 profile/
│   │   │   └── ProfilePage.jsx
│   │   ├── 📁 settings/
│   │   │   └── SettingsPage.jsx
│   │   └── NotFoundPage.jsx              # 404 page
│   │
│   ├── 📁 context/                       # React Context
│   │   ├── AuthContext.jsx               # Authentication state
│   │   ├── ThemeContext.jsx              # Theme (if needed)
│   │   └── index.js
│   │
│   ├── 📁 hooks/                         # Custom React Hooks
│   │   ├── useAuth.js                    # Auth hook
│   │   ├── useApi.js                     # API call hook
│   │   ├── useDebounce.js                # Debounce hook
│   │   ├── useLocalStorage.js            # Local storage hook
│   │   ├── useCamera.js                  # Camera access hook
│   │   ├── useGeolocation.js             # Location hook (if needed)
│   │   └── index.js
│   │
│   ├── 📁 services/                      # API Services
│   │   ├── api.js                        # Axios instance & interceptors
│   │   ├── authService.js                # Auth API calls
│   │   ├── quotationService.js           # Quotation API calls
│   │   ├── momService.js                 # MOM API calls
│   │   ├── workOrderService.js           # Work Order API calls
│   │   ├── ocrService.js                 # OCR API calls
│   │   ├── productService.js             # Product API calls
│   │   ├── dashboardService.js           # Dashboard API calls
│   │   └── index.js
│   │
│   ├── 📁 utils/                         # Utility Functions
│   │   ├── formatters.js                 # Date, currency formatters
│   │   │   ├── formatDate()
│   │   │   ├── formatCurrency()
│   │   │   ├── formatTime()
│   │   │   └── formatFileSize()
│   │   ├── validators.js                 # Form validation
│   │   │   ├── validateEmail()
│   │   │   ├── validatePhone()
│   │   │   ├── validateGST()
│   │   │   └── validateRequired()
│   │   ├── helpers.js                    # General helpers
│   │   │   ├── classNames()
│   │   │   ├── truncate()
│   │   │   ├── downloadBlob()
│   │   │   └── generateId()
│   │   ├── constants.js                  # App constants
│   │   │   ├── GST_RATES
│   │   │   ├── UNITS
│   │   │   ├── PRIORITIES
│   │   │   └── STATUSES
│   │   └── index.js
│   │
│   ├── 📁 styles/                        # Global Styles
│   │   ├── index.css                     # Main CSS with Tailwind
│   │   └── custom.css                    # Custom overrides
│   │
│   ├── 📁 routes/                        # Route Configuration
│   │   ├── AppRoutes.jsx                 # Main router
│   │   ├── PrivateRoutes.jsx             # Protected routes
│   │   └── PublicRoutes.jsx              # Public routes
│   │
│   ├── App.jsx                           # Main App component
│   ├── main.jsx                          # React entry point
│   └── index.css                         # Tailwind imports
│
├── .env.example                          # Environment template
├── .env.local                            # Local environment (git ignored)
├── .gitignore                            # Git ignore
├── .eslintrc.cjs                         # ESLint config
├── .prettierrc                           # Prettier config
├── index.html                            # HTML entry
├── package.json                          # NPM dependencies
├── postcss.config.js                     # PostCSS config
├── tailwind.config.js                    # Tailwind config
├── vite.config.js                        # Vite config
└── README.md                             # Frontend documentation
```

---

# 📁 DOCS FOLDER STRUCTURE

```
docs/
│
├── 📁 api/
│   ├── api-reference.md                  # Complete API documentation
│   ├── postman-collection.json           # Postman collection
│   └── openapi.yaml                      # OpenAPI/Swagger spec
│
├── 📁 database/
│   ├── schema.md                         # Database schema documentation
│   ├── er-diagram.png                    # ER Diagram
│   └── migrations.md                     # Migration guide
│
├── 📁 guides/
│   ├── setup-guide.md                    # Development setup
│   ├── deployment-guide.md               # Deployment instructions
│   ├── google-vision-setup.md            # Google Cloud Vision setup
│   ├── nvidia-nims-setup.md              # NVIDIA NIMs setup
│   └── testing-guide.md                  # Testing instructions
│
├── 📁 wireframes/
│   ├── login.png
│   ├── dashboard.png
│   ├── quotation-form.png
│   ├── mom-form.png
│   └── work-order-form.png
│
├── 📁 architecture/
│   ├── system-architecture.md
│   ├── flow-diagrams.md
│   └── data-flow.md
│
├── requirements.md                       # Project requirements
├── tech-stack.md                         # Technology decisions
└── changelog.md                          # Version history
```

---

# 📁 SCRIPTS FOLDER

```
scripts/
│
├── setup.sh                              # Initial project setup
├── dev.sh                                # Start development servers
├── test.sh                               # Run all tests
├── deploy.sh                             # Deployment script
├── db-migrate.sh                         # Run database migrations
├── db-seed.sh                            # Seed database
└── backup.sh                             # Backup script
```

---

# 📄 ROOT FILES

## .gitignore
```gitignore
# Dependencies
node_modules/
__pycache__/
*.pyc
.venv/
venv/

# Environment
.env
.env.local
.env.*.local

# Build
dist/
build/
*.egg-info/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Testing
.coverage
htmlcov/
.pytest_cache/

# Secrets
*.pem
*.key
service-account*.json
```

## docker-compose.yml
```yaml
version: '3.8'

services:
  # Backend API
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql://user:password@db:3306/docgen
      - JWT_SECRET=${JWT_SECRET}
      - NVIDIA_API_KEY=${NVIDIA_API_KEY}
    depends_on:
      - db
    volumes:
      - ./backend:/app

  # Frontend
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000/api
    volumes:
      - ./frontend:/app

  # MySQL Database
  db:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=rootpassword
      - MYSQL_DATABASE=docgen
      - MYSQL_USER=user
      - MYSQL_PASSWORD=password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

## Makefile
```makefile
.PHONY: setup dev test deploy

# Setup project
setup:
	cd backend && python -m venv venv && pip install -r requirements.txt
	cd frontend && npm install

# Start development
dev:
	cd backend && uvicorn app.main:app --reload &
	cd frontend && npm run dev

# Run tests
test:
	cd backend && pytest
	cd frontend && npm test

# Database migrations
migrate:
	cd backend && alembic upgrade head

# Deploy
deploy:
	cd backend && railway up
	cd frontend && vercel --prod

# Clean
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name node_modules -exec rm -rf {} +
```

## README.md (Root)
```markdown
# Smart Business Document Generator

AI-powered application for creating business documents from handwritten notes.

## Features
- 📝 Quotation generation with GST calculation
- 📋 Minutes of Meeting with AI summarization
- 🔧 Work Order management
- 📷 OCR for handwritten text extraction
- 📱 Mobile-first responsive design

## Tech Stack
- **Backend:** Python, FastAPI, MySQL
- **Frontend:** React, Tailwind CSS
- **AI:** NVIDIA NIMs (Llama 3.1)
- **OCR:** Google Cloud Vision

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- MySQL 8.0
- Google Cloud account
- NVIDIA NGC account

### Setup
```bash
# Clone repository
git clone https://github.com/yourusername/smart-doc-generator.git
cd smart-doc-generator

# Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials

# Setup frontend
cd ../frontend
npm install
cp .env.example .env.local
# Edit .env.local with API URL

# Start development
make dev
```

## Documentation
See `/docs` folder for detailed documentation.

## Team
- Backend Developer: [Your Name]
- Frontend Developer: [Partner Name]

## License
MIT
```

---

# FILE COUNT SUMMARY

| Category | Files | Folders |
|----------|-------|---------|
| Backend | ~45 | ~12 |
| Frontend | ~85 | ~20 |
| Docs | ~15 | ~5 |
| Root | ~8 | ~4 |
| **Total** | **~153** | **~41** |

---

**Document Version:** 1.0  
**Last Updated:** January 2025






Admin User
Email: admin@quotmate.com
Password: Admin123
User ID: cda6a884-8bf7-4009-8867-e8c737aa14b0
Full Name: Admin User
Company: QuotMate Pro
Phone: 1234567890
Address: 123 Tech Street
GST Number: 22AAAAA0000A1Z5
Is Admin: true

Test User
Email: test@example.com
Password: Test1234
User ID: 770fb0be-7db2-4a5d-9450-1e2fa2bfc2fd
Full Name: Test User
Company: Test Company
Phone: 9876543210
Is Admin: false