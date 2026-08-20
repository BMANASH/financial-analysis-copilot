import streamlit as st
from pypdf import PdfReader

st.title("Financial Analysis Copilot")

st.write("Upload a financial report to begin analysis.")

uploaded_file = st.file_uploader(
    "Choose a financial report",
    type=["pdf"]
)

if uploaded_file is not None:
    st.success("Financial report uploaded successfully!")

    reader = PdfReader(uploaded_file)

    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    st.write("Number of pages:", len(reader.pages))

    st.write("PDF text extracted successfully.")

    with st.expander("View extracted text"):
        st.text(text[:5000])
