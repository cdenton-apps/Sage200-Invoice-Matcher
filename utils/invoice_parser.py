# === utils/invoice_parser.py ===
import pdfplumber
import re

def extract_invoice_data(pdf_path):
    data = {
        "invoice_number": "Unknown",
        "po_number": None,
        "supplier_name": None,
        "total_amount": None,
        "line_items": []
    }

    # Open and extract all text from each page
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(
            page.extract_text() for page in pdf.pages if page.extract_text()
        )

    # -------------------------
    # 1) Extract “Invoice Number” exactly
    #    Expect lines like:
    #      Invoice Number: INV-1001
    #      or Invoice No: INV-1001
    #
    #    Regex breakdown:
    #    - ^\s*Invoice\s+(Number|No)    → look for “Invoice Number” or “Invoice No” at line start
    #    - \s*[:#]\s*                   → then a colon or pound sign (":" or "#"), optional whitespace
    #    - ([A-Za-z0-9\-/]+)            → capture invoice ID (alphanumeric, dashes, slashes)
    #
    invoice_match = re.search(
        r"^\s*Invoice\s+(?:Number|No)\s*[:#]\s*([A-Za-z0-9\-/]+)",
        text,
        re.IGNORECASE | re.MULTILINE
    )

    # -------------------------
    # 2) Extract “PO Number” exactly
    #    Expect lines like:
    #      PO Number: PO-1001
    #      or PO No: PO-1001
    po_match = re.search(
        r"^\s*PO\s+(?:Number|No)\s*[:#]\s*([A-Za-z0-9\-/]+)",
        text,
        re.IGNORECASE | re.MULTILINE
    )

    # -------------------------
    # 3) Extract “Supplier” (From:)
    #    Look for a line “From: ACME Supplies Ltd”
    supplier_match = re.search(
        r"^\s*From\s*[:]\s*(.+)$",
        text,
        re.IGNORECASE | re.MULTILINE
    )

    # -------------------------
    # 4) Extract “Total” (grand total)
    #    Look for “Total: £123.45” or “Total £123.45”
    total_match = re.search(
        r"^\s*Total\s*[:£]?\s*([\d\.,]+)",
        text,
        re.IGNORECASE | re.MULTILINE
    )

    # Assign extracted values (or leave as defaults)
    if invoice_match:
        data["invoice_number"] = invoice_match.group(1).strip()
    if po_match:
        data["po_number"] = po_match.group(1).strip()
    if supplier_match:
        data["supplier_name"] = supplier_match.group(1).strip()
    if total_match:
        try:
            data["total_amount"] = float(total_match.group(1).replace(",", ""))
        except ValueError:
            data["total_amount"] = None

    # -------------------------
    # 5) Extract line items
    #    Expect each item line in the PDF to look roughly like:
    #      Description……<spaces>Qty<spaces>£UnitPrice<spaces>£LineTotal
    #
    #    We’ll capture:
    #      1) description: “Printer Paper A4”
    #      2) quantity   : “10”
    #      3) unit_price : “2.50”  (after £)
    #      4) line_total : “25.00” (after £)
    #
    #    Regex (using MULTILINE so ^ matches start-of-line):
    #      ^\s*(.+?)\s+              → capture description (any chars), then whitespace
    #      (\d+)\s+                  → capture integer quantity, then whitespace
    #      £?(\d+\.\d{2})\s+         → capture unit price (with or without leading "£"), then whitespace
    #      £?(\d+\.\d{2})            → capture line total (with or without leading "£")
    #
    line_pattern = re.compile(
        r"^\s*(.+?)\s+(\d+)\s+£?(\d+\.\d{2})\s+£?(\d+\.\d{2})",
        re.IGNORECASE | re.MULTILINE
    )
    lines = line_pattern.findall(text)
    for desc, qty, unit_price, total in lines:
        try:
            data["line_items"].append({
                "description": desc.strip(),
                "quantity": int(qty),
                "unit_price": float(unit_price),
                "line_total": float(total)
            })
        except (ValueError, TypeError):
            continue

    return data
