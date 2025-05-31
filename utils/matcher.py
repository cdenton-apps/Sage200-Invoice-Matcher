import pandas as pd
from fuzzywuzzy import fuzz

def match_invoice_to_po(invoice_data, po_df):
    results = {
        "Invoice No": invoice_data["invoice_number"],
        "PO Match": "Not Found",
        "Status": "❌",
        "Issue": "No matching PO"
    }

    for _, row in po_df.iterrows():
        if invoice_data["po_number"] == row.get("PO_Number") or invoice_data["po_number"] == row.get("PO Number"):
            supplier_csv_key = "Supplier_Name" if "Supplier_Name" in row else "Supplier"
            score = fuzz.partial_ratio(invoice_data["supplier_name"].lower(), row[supplier_csv_key].lower())
            amount_match = abs(invoice_data["total_amount"] - row["Total_Amount"]) < 1.0

            if score >= 80 and amount_match:
                results["PO Match"] = row["PO_Number"]
                results["Status"] = "✅"
                results["Issue"] = "-"
                break
            else:
                results["PO Match"] = row["PO_Number"]
                results["Status"] = "⚠️"
                results["Issue"] = "Mismatch in supplier or amount"
                break

    return results
