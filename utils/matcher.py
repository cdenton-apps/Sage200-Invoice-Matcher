# === utils/matcher.py ===
from fuzzywuzzy import fuzz

def match_invoice_to_po(invoice_data, po_df):
    results = {
        "Invoice No": invoice_data.get("invoice_number", "Unknown"),
        "PO Match": "Not Found",
        "Status": "No Match",
        "Issue": "No matching PO",
    }

    # Attempt to pick the correct PO column name:
    if "PO_Number" in po_df.columns:
        po_col = "PO_Number"
    elif "PO Number" in po_df.columns:
        po_col = "PO Number"
    else:
        results["Issue"] = "PO_Number column not found"
        return results

    matched_rows = po_df[po_df[po_col] == invoice_data.get("po_number")]

    if matched_rows.empty:
        results["Issue"] = "PO number not found in PO data"
        return results

    for _, row in matched_rows.iterrows():
        # Supplier check remains the same
        supplier_score = fuzz.partial_ratio(
            invoice_data.get("supplier_name", "").lower(),
            row["Supplier_Name"].lower()
        )
        if supplier_score < 80:
            results["PO Match"] = row[po_col]
            results["Status"] = "Mismatch"
            results["Issue"] = "Supplier name mismatch"
            continue

        # Now find the correct item/quantity/price columns:
        # (Assume your CSV might have "Item Description" instead of "Item_Description", etc.)
        # Example fallback for item description:
        if "Item_Description" in po_df.columns:
            desc_col = "Item_Description"
        elif "Item Description" in po_df.columns:
            desc_col = "Item Description"
        else:
            results["Issue"] = "Item_Description column not found"
            return results

        if "Quantity_Ordered" in po_df.columns:
            qty_col = "Quantity_Ordered"
        elif "Quantity Ordered" in po_df.columns:
            qty_col = "Quantity Ordered"
        else:
            results["Issue"] = "Quantity_Ordered column not found"
            return results

        if "Unit_Price" in po_df.columns:
            price_col = "Unit_Price"
        elif "Unit Price" in po_df.columns:
            price_col = "Unit Price"
        else:
            results["Issue"] = "Unit_Price column not found"
            return results

        # Line‐by‐line validation (fuzzy on description)
        invoice_lines = invoice_data.get("line_items", [])
        mismatches = []
        for line in invoice_lines:
            item_match = (
                fuzz.partial_ratio(
                    row[desc_col].lower(),
                    line["description"].lower()
                ) > 80
                and int(row[qty_col]) == line["quantity"]
                and abs(float(row[price_col]) - line["unit_price"]) < 0.01
            )
            if not item_match:
                mismatches.append(line)

        if not mismatches:
            results["PO Match"] = row[po_col]
            results["Status"] = "Match"
            results["Issue"] = "-"
            return results
        else:
            results["PO Match"] = row[po_col]
            results["Status"] = "Mismatch"
            results["Issue"] = f"{len(mismatches)} line item(s) did not match"
            return results

    return results
