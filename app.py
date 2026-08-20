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
You are a Senior Financial Analyst.

Analyze the uploaded financial report and create an Executive
Financial Snapshot.

IMPORTANT:
- Use only information found in the uploaded report.
- Do not invent or assume financial figures.
- If a metric is not available, write "Not available".
- Clearly distinguish between Consolidated and Standalone figures.
- Use the latest financial period available in the report.
- Compare with the previous year whenever the information is available.

Provide the analysis in the following structure:

1. COMPANY OVERVIEW
- Company name
- Reporting period
- Type of report

2. KEY FINANCIAL METRICS
Create a table with:
- Revenue / Total Income
- EBITDA / Operating Profit / PPOP (use the most relevant metric for the company)
- Profit Before Tax
- Net Profit / PAT
- EPS

For each metric provide:
- Current period
- Previous period
- YoY growth

3. BUSINESS PERFORMANCE
Identify the 3 to 5 most important business developments
mentioned in the report.

4. MANAGEMENT COMMENTARY
Summarize important management statements about:
- Growth
- Future plans
- Capital expenditure
- New products or businesses
- Future outlook

5. KEY RISKS
Identify the 3 to 5 most important risks or headwinds
mentioned or clearly indicated in the report.

6. ANALYST TAKEAWAY
Give a short conclusion covering:
- What is improving?
- What is weakening?
- What should an investor watch?

Remember:
This is financial analysis, so accuracy is more important than
length.

Financial report:

{text}
"""

        response = client.models.generate_content(
            model="gemini-3.7-flash",
            contents=prompt
        )

        st.subheader("Gemini Financial Analysis")

        st.write(response.text)
