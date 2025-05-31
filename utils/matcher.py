# === utils/matcher.py ===
from fuzzywuzzy import fuzz


def match_invoice_to_po(invoice_data, po_df):
    results = {
        "Invoice No": invoice_data.get("invoice_number", "Unknown"),
        "PO Match": "Not Found",
        "Status": "No Match",
        "Issue": "No matching PO",
    }

    matched_rows = po_df[po_df["PO_Number"] == invoice_data.get("po_number")]

    if matched_rows.empty:
        results["Issue"] = "PO number not found in PO data"
        return results

    for _, row in matched_rows.iterrows():
        supplier_score = fuzz.partial_ratio(
            invoice_data.get("supplier_name", "").lower(),
            row["Supplier_Name"].lower()
        )

        if supplier_score < 80:
            results["PO Match"] = row["PO_Number"]
            results["Status"] = "Mismatch"
            results["Issue"] = "Supplier name mismatch"
            continue

        # Line-by-line validation
        invoice_lines = invoice_data.get("line_items", [])
        mismatches = []

        for line in invoice_lines:
            match = (
                row["Item_Description"].lower() == line["description"].lower() and
                int(row["Quantity_Ordered"]) == line["quantity"] and
                abs(float(row["Unit_Price"]) - line["unit_price"]) < 0.01
            )
            if not match:
                mismatches.append(line)

        if not mismatches:
            results["PO Match"] = row["PO_Number"]
            results["Status"] = "Match"
            results["Issue"] = "-"
            return results
        else:
            results["PO Match"] = row["PO_Number"]
            results["Status"] = "Mismatch"
            results["Issue"] = f"{len(mismatches)} line item(s) did not match"
            return results

    return results
