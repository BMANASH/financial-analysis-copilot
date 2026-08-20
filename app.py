import streamlit as st
from pypdf import PdfReader
from google import genai
import json

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

Analyze the uploaded financial report.

Your first task is to understand the company and its business.

Determine:

1. Company name
2. Reporting period
3. Industry / sector
4. Business type
5. Type of report

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

Examples:

For Banks, NBFCs and Financial Services:
- Total Income
- NII
- NIM
- PPOP
- AUM
- GNPA
- NNPA
- Credit Cost
- PAT
- ROA
- ROE
- Capital Adequacy Ratio

For Manufacturing and Automobile:
- Revenue
- Revenue Growth
- EBITDA
- EBITDA Margin
- EBIT
- PAT
- Net Debt
- Capex
- Free Cash Flow
- ROCE

For IT and Technology:
- Revenue
- Revenue Growth
- EBIT
- EBIT Margin
- PAT
- Deal Wins
- Order Book
- Utilization
- Employee Count
- Attrition

For FMCG and Consumer:
- Revenue
- Revenue Growth
- Volume Growth
- EBITDA
- EBITDA Margin
- PAT
- Gross Margin
- Market Share
- Distribution

For Insurance:
- Gross Written Premium
- APE
- VNB
- VNB Margin
- Claims Ratio
- Solvency Ratio
- PAT

Do not force irrelevant metrics into the analysis.

IMPORTANT ACCURACY RULES:

- Use only information found in the uploaded report.
- Do not invent financial figures.
- Do not guess missing information.
- If a metric is not available, use "Not available".
- Clearly distinguish Consolidated and Standalone figures.
- Use the latest financial period available.
- Compare with the previous year whenever available.
- Keep financial figures as reported.
- Mention the unit used in the report.

VERY IMPORTANT:

Return your answer ONLY as valid JSON.

Do not use Markdown.

Do not use ```json.

Do not add any explanation before or after the JSON.

Use exactly this structure:

{{
    "company_overview": {{
        "company_name": "",
        "reporting_period": "",
        "industry": "",
        "business_type": "",
        "category": "",
        "report_type": ""
    }},

    "key_metrics": [
        {{
            "metric": "",
            "current_period": "",
            "previous_period": "",
            "yoy_growth": "",
            "unit": "",
            "basis": ""
        }}
    ],

    "business_performance": [
        ""
    ],

    "management_commentary": [
        ""
    ],

    "risks": [
        ""
    ],

    "analyst_takeaway": {{
        "improving": [
            ""
        ],
        "weakening": [
            ""
        ],
        "growth_drivers": [
            ""
        ],
        "investor_watch": [
            ""
        ]
    }}
}}

The "key_metrics" section should contain only the most relevant
metrics for the company.

The "basis" field must say either:
"Consolidated"
or
"Standalone"
or
"Not specified"

If a value is unavailable, write:
"Not available"

Do not provide Buy, Sell or Hold recommendations.

Financial report:

{text}
"""

        response = client.models.generate_content(
            model="gemini-3.7-flash",
            contents=prompt
        )

        st.subheader("Gemini Financial Analysis")

        raw_response = response.text

        try:
            analysis = json.loads(raw_response)

            st.success("Financial analysis successfully structured.")

            st.write(analysis)

        except json.JSONDecodeError:

            st.error("Gemini returned an invalid JSON response.")

            st.write(raw_response)
