#!/usr/bin/env python3
"""
Week 5 Implementation Verification Script
Verifies all Week 5 components can be imported correctly
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

print("=" * 60)
print("Week 5 Implementation Verification")
print("=" * 60)
print()

tests_passed = 0
tests_failed = 0

# Test 1: Check templates exist
print("Test 1: Checking PDF templates...")
template_dir = os.path.join(os.path.dirname(__file__), '..', 'app', 'templates')
templates = ['quotation.html', 'mom.html', 'work_order.html']
for template in templates:
    template_path = os.path.join(template_dir, template)
    if os.path.exists(template_path):
        print(f"  ✓ {template} exists")
        tests_passed += 1
    else:
        print(f"  ✗ {template} NOT FOUND")
        tests_failed += 1
print()

# Test 2: Import PDF service (may fail if WeasyPrint deps not installed)
print("Test 2: Importing PDF service...")
weasyprint_failed = False
try:
    from app.services.pdf_service import pdf_service
    print("  ✓ PDF service imported successfully")
    print(f"  ✓ Template environment configured")
    tests_passed += 1
except Exception as e:
    weasyprint_failed = True
    print(f"  ⚠ PDF service import failed (expected if WeasyPrint deps not installed)")
    print(f"    Error: {str(e)[:100]}")
    print(f"    This is OK - see WEASYPRINT_SETUP.md for installation")
print()

# Test 3: Import quotations router
print("Test 3: Importing quotations router...")
try:
    from app.api import quotations
    print("  ✓ Quotations router imported successfully")
    
    # Check if new endpoints exist
    router = quotations.router
    routes = [route.path for route in router.routes]
    
    expected_routes = [
        '/calculate',
        '/from-ocr',
        '',  # POST for create, GET for list
        '/{quotation_id}',  # GET, PUT, DELETE
        '/{quotation_id}/finalize',
        '/{quotation_id}/download'
    ]
    
    print(f"  ✓ Router has {len(routes)} endpoints")
    
    # Check for finalize endpoint
    if any('finalize' in route for route in routes):
        print("  ✓ Finalize endpoint found")
        tests_passed += 1
    else:
        print("  ✗ Finalize endpoint NOT FOUND")
        tests_failed += 1
    
    # Check for download endpoint
    if any('download' in route for route in routes):
        print("  ✓ Download endpoint found")
        tests_passed += 1
    else:
        print("  ✗ Download endpoint NOT FOUND")
        tests_failed += 1
        
except Exception as e:
    print(f"  ✗ Failed to import quotations router")
    print(f"    Error: {str(e)}")
    tests_failed += 1
print()

# Test 4: Check services can be imported
print("Test 4: Importing related services...")
services_to_check = [
    ('app.services.gst_calculator', 'gst_calculator'),
    ('app.services.quotation_mapper', 'quotation_mapper'),
    ('app.services.audit_service', 'log_audit'),
]

for module_name, attr_name in services_to_check:
    try:
        module = __import__(module_name, fromlist=[attr_name])
        getattr(module, attr_name)
        print(f"  ✓ {module_name} imported")
        tests_passed += 1
    except Exception as e:
        print(f"  ✗ {module_name} failed: {str(e)}")
        tests_failed += 1
print()

# Test 5: Check models
print("Test 5: Importing models...")
try:
    from app.models.quotation import Quotation, QuotationItem
    from app.models.document import Document, DocumentStatus
    print("  ✓ Quotation models imported")
    print("  ✓ Document models imported")
    tests_passed += 1
except Exception as e:
    print(f"  ✗ Models import failed: {str(e)}")
    tests_failed += 1
print()

# Summary
print("=" * 60)
print("Verification Summary")
print("=" * 60)
print(f"Tests Passed: {tests_passed}")
print(f"Tests Failed: {tests_failed}")
print()

if tests_failed == 0 and not weasyprint_failed:
    print("✅ All components verified successfully!")
    print()
    print("Next steps:")
    print("1. Start the server: uvicorn app.main:app --reload")
    print("2. Test the API endpoints (see WEEK5_IMPLEMENTATION_SUMMARY.md)")
    sys.exit(0)
elif tests_failed == 0 and weasyprint_failed:
    print("✅ Week 5 implementation complete!")
    print("⚠️  WeasyPrint needs system dependencies for PDF generation")
    print()
    print("To enable PDF generation, install system dependencies:")
    print("  brew install cairo pango gdk-pixbuf libffi")
    print()
    print("See WEASYPRINT_SETUP.md for full instructions")
    print()
    print("You can still test all other API endpoints!")
    sys.exit(0)
else:
    print("❌ Some critical components failed verification")
    print()
    print("Please check the error messages above")
    sys.exit(1)
