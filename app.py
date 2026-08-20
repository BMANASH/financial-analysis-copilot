import streamlit as st
from pypdf import PdfReader
from google import genai

st.title("Financial Analysis Copilot")

st.write("Upload a financial report to begin analysis.")

uploaded_file = st.file_uploader(
    "Choose a financial report",
    type=["pdf"]
)

if uploaded_file is not None:

    reader = PdfReader(uploaded_file)

    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    st.success("Financial report uploaded and read successfully!")

    if st.button("Ask Gemini to Analyze"):

        client = genai.Client(
            api_key=st.secrets["GEMINI_API_KEY"]
        )

        prompt = f"""
You are a financial analyst.

Read the following financial report and provide a short summary
of the company's financial performance.

Focus on:
1. Revenue
2. EBITDA
3. Net Profit
4. Revenue growth
5. Profit growth
6. Major business highlights
7. Major risks

Financial report:

{text}
"""

        response = client.models.generate_content(
            model="gemini-3.7-flash",
            contents=prompt
        )

        st.subheader("Gemini Financial Analysis")

        st.write(response.text)
