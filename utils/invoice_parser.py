# === utils/invoice_parser.py ===
import pdfplumber
import re


def extract_invoice_data(pdf_path):
    data = {
        "invoice_number": None,
        "po_number": None,
        "supplier_name": None,
        "total_amount": None,
        "line_items": []
    }

    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(
            page.extract_text() for page in pdf.pages if page.extract_text())

    # Extract general fields
    invoice_match = re.search(r"Invoice\s*(Number|No)?[:#\s]*([A-Z0-9\-]+)", text, re.IGNORECASE)
    po_match = re.search(r"PO\s*(Number|No)?[:#\s]*([A-Z0-9\-]+)", text, re.IGNORECASE)
    total_match = re.search(r"Total\s*[:£]?\s*([\d\.,]+)", text, re.IGNORECASE)
    supplier_match = re.search(r"From[:\s]*(.+)", text)

    if invoice_match:
        data["invoice_number"] = invoice_match.group(2).strip()
    if po_match:
        data["po_number"] = po_match.group(2).strip()
    if total_match:
        try:
            data["total_amount"] = float(total_match.group(1).replace(",", ""))
        except ValueError:
            data["total_amount"] = None
    if supplier_match:
        data["supplier_name"] = supplier_match.group(1).strip()

    # Extract line items from text (naive implementation)
    line_pattern = re.compile(r"(.+?)\s+(\d+)\s+\£?(\d+\.\d{2})\s+\£?(\d+\.\d{2})")
    lines = line_pattern.findall(text)
    for desc, qty, unit_price, total in lines:
        try:
            data["line_items"].append({
                "description": desc.strip(),
                "quantity": int(qty),
                "unit_price": float(unit_price),
                "line_total": float(total)
            })
        except ValueError:
            continue

    return data
