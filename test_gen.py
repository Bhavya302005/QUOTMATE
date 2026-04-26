from weasyprint import HTML
import json

html_content = ""
with open("apps/backend/app/templates/quotation.html", "r") as f:
    html_content = f.read()

HTML(string=html_content).write_pdf("test_weasy.pdf")
print("Saved test_weasy.pdf")
