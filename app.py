import streamlit as st
import pandas as pd
import os
import io
from utils.invoice_parser import extract_invoice_data
from utils.matcher import match_invoice_to_po

st.title("📄 Supplier Invoice Line-by-Line Matcher for Sage 200")

# Upload PO export CSV
po_file = st.file_uploader("Upload Sage PO Export (CSV)", type=["csv"])
if po_file:
    po_df = pd.read_csv(po_file)
    st.success("✅ PO data loaded successfully!")
    st.write("📋 PO Columns:", po_df.columns.tolist())

# Upload invoice PDFs
invoice_files = st.file_uploader("Upload Supplier Invoices (PDFs)", type=["pdf"], accept_multiple_files=True)

if invoice_files and po_file:
    match_results = []

    for invoice_file in invoice_files:
        temp_path = f"temp_{invoice_file.name}"
        with open(temp_path, "wb") as f:
            f.write(invoice_file.read())

        invoice_data = extract_invoice_data(temp_path)
        st.write(f"🔍 Extracted Data from {invoice_file.name}:", invoice_data)

        result = match_invoice_to_po(invoice_data, po_df)
        result["File Name"] = invoice_file.name
        match_results.append(result)

        os.remove(temp_path)

    result_df = pd.DataFrame(match_results)
    st.subheader("📊 Match Results")
    st.dataframe(result_df)

    csv_buffer = io.StringIO()
    result_df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="📥 Download Match Report as CSV",
        data=csv_buffer.getvalue(),
        file_name="match_report.csv",
        mime="text/csv"
    )
