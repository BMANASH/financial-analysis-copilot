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
You are a Senior Financial Analyst and Equity Research Analyst.

Your first task is to understand the company and its business
before analyzing its financial performance.

FIRST, determine:

1. Company name
2. Reporting period
3. Industry / sector
4. Business type

Classify the company into the most appropriate category:

- Banking / NBFC / Financial Services
- Manufacturing / Automobile
- IT / Technology
- FMCG / Consumer
- Pharmaceutical / Healthcare
- Energy / Oil & Gas
- Telecom
- Insurance
- Infrastructure / Construction
- Other

Then select the financial metrics that are most relevant
to that company and sector.

IMPORTANT:
Do not force irrelevant metrics into the analysis.

For Banks, NBFCs and Financial Services, consider:
- Revenue / Total Income
- Net Interest Income (NII)
- Net Interest Margin (NIM)
- Pre-Provision Operating Profit (PPOP)
- Assets Under Management (AUM)
- Gross NPA
- Net NPA
- Credit Cost
- Profit After Tax (PAT)
- Return on Assets (ROA)
- Return on Equity (ROE)
- Capital Adequacy Ratio

For Manufacturing and Automobile companies, consider:
- Revenue
- Revenue Growth
- EBITDA
- EBITDA Margin
- EBIT
- Profit After Tax (PAT)
- Net Debt
- Capital Expenditure (Capex)
- Free Cash Flow
- ROCE

For IT and Technology companies, consider:
- Revenue
- Revenue Growth
- EBIT
- EBIT Margin
- Profit After Tax
- Deal Wins
- Order Book
- Utilization
- Employee Count
- Attrition

For FMCG and Consumer companies, consider:
- Revenue
- Revenue Growth
- Volume Growth
- EBITDA
- EBITDA Margin
- Profit After Tax
- Gross Margin
- Market Share
- Distribution

For Insurance companies, consider:
- Gross Written Premium
- Annualized Premium Equivalent (APE)
- Value of New Business (VNB)
- VNB Margin
- Claims Ratio
- Solvency Ratio
- Profit After Tax

Use only metrics that are actually relevant and available
in the uploaded report.

IMPORTANT ACCURACY RULES:
- Use only information found in the uploaded report.
- Do not invent financial figures.
- Do not guess missing information.
- If a metric is not available, write "Not available".
- Clearly distinguish between Consolidated and Standalone figures.
- Use the latest financial period available in the report.
- Compare with the previous year whenever the information is available.
- Keep financial figures exactly as reported whenever possible.
- Mention the unit used in the report, such as ₹ crore, ₹ million,
  USD million, etc.

Now provide the analysis using the following structure:

1. COMPANY OVERVIEW

Provide:
- Company name
- Reporting period
- Industry / sector
- Business type
- Type of report

2. KEY FINANCIAL METRICS

Create a clear table containing the most relevant financial
metrics for this particular company.

For each metric provide:
- Current period
- Previous period
- YoY growth

Do not include irrelevant metrics simply to fill the table.

Clearly identify whether the figures are:
- Consolidated
- Standalone

3. BUSINESS PERFORMANCE

Identify the 3 to 5 most important business developments
mentioned in the report.

Focus on:
- Revenue drivers
- Segment performance
- New businesses
- Product launches
- Market expansion
- Customer growth
- Operational improvements

4. MANAGEMENT COMMENTARY

Summarize important management statements about:

- Growth
- Future plans
- Capital expenditure
- New products or businesses
- Expansion plans
- Strategic priorities
- Future outlook

Do not present your own assumptions as management commentary.

5. KEY RISKS AND HEADWINDS

Identify the 3 to 5 most important risks or challenges
mentioned in the report.

Consider:
- Demand slowdown
- Input cost pressure
- Interest rate risk
- Foreign exchange risk
- Credit risk
- Regulatory risk
- Competitive pressure
- Cybersecurity risk
- Execution risk

Only include risks that are relevant to the company.

6. ANALYST TAKEAWAY

Give a short analyst-style conclusion covering:

- What is improving?
- What is weakening?
- What are the major growth drivers?
- What should an investor watch?

Keep this section balanced.

Do not give a "Buy", "Sell" or "Hold" recommendation.

Financial report:

{text}
"""

        response = client.models.generate_content(
            model="gemini-3.7-flash",
            contents=prompt
        )

        st.subheader("Gemini Financial Analysis")

        st.write(response.text)
