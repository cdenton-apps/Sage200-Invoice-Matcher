import pdfplumber
import re

def extract_invoice_data(pdf_path):
    data = {
        "invoice_number": None,
        "po_number": None,
        "supplier_name": None,
        "total_amount": None
    }
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

    invoice_match = re.search(r"Invoice\s*No[:\s]*([A-Z0-9\-]+)", text, re.IGNORECASE)
    po_match = re.search(r"PO\s*No[:\s]*([A-Z0-9\-]+)", text, re.IGNORECASE)
    total_match = re.search(r"Total[:\s]*£?\s?([\d\.,]+)", text, re.IGNORECASE)
    supplier_match = re.search(r"From[:\s]*(.+)", text)

    if invoice_match:
        data["invoice_number"] = invoice_match.group(1).strip()
    if po_match:
        data["po_number"] = po_match.group(1).strip()
    if total_match:
        data["total_amount"] = float(total_match.group(1).replace(",", ""))
    if supplier_match:
        data["supplier_name"] = supplier_match.group(1).strip()

    return data
