import streamlit as st

st.title("Financial Analysis Copilot")

st.write("Upload a financial report to begin analysis.")

uploaded_file = st.file_uploader(
    "Choose a financial report",
    type=["pdf"]
)

if uploaded_file is not None:
    st.success("Financial report uploaded successfully!")
    st.write("File name:", uploaded_file.name)
