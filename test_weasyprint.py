import sys
import traceback
from weasyprint import HTML
html_content = "<h1>Test</h1>"
try:
    HTML(string=html_content).write_pdf("test.pdf")
    print("PDF GENERATED SUCCESSFULLY")
except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()
