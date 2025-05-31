from fuzzywuzzy import fuzz

def match_invoice_to_po(invoice_data, po_df):
    best_match = None
    best_issue = "No matching PO"
    best_status = "No Match"

    for _, row in po_df.iterrows():
        if invoice_data["po_number"] == row["PO_Number"]:
            supplier_score = fuzz.partial_ratio(
                invoice_data["supplier_name"].lower(),
                row["Supplier_Name"].lower()
            )
            amount_match = abs(invoice_data["total_amount"] - row["Total_Amount"]) < 1.0

            if supplier_score >= 80 and amount_match:
                return {
                    "Invoice No": invoice_data["invoice_number"],
                    "PO Match": row["PO_Number"],
                    "Status": "Match",
                    "Issue": "-",
                }

            else:
                best_match = row["PO_Number"]
                best_issue = "Mismatch in supplier or amount"
                best_status = "Mismatch"

    return {
        "Invoice No": invoice_data["invoice_number"],
        "PO Match": best_match if best_match else "Not Found",
        "Status": best_status,
        "Issue": best_issue,
    }
