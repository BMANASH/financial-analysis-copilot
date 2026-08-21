import streamlit as st
from pypdf import PdfReader
from google import genai
import json

st.set_page_config(
    page_title="Financial Analysis Copilot",
    page_icon="📊",
    layout="wide"
)

st.title("Financial Analysis Copilot")

st.write(
    "Upload a corporate financial report and generate an AI-powered "
    "financial analysis."
)

uploaded_file = st.file_uploader(
    "Upload Financial Report (PDF)",
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

Your job is to turn the report into a clear, professional,
easy-to-understand financial analysis.

IMPORTANT COMMUNICATION STYLE:

- Use simple professional English.
- Write for a business student, investor, manager, or analyst.
- Avoid unnecessary technical jargon.
- Do not make the explanation childish or overly casual.
- Keep the financial meaning accurate.
- If an important technical financial term is necessary,
  explain it briefly in simple words.
- Prefer short and clear sentences.
- Avoid overly long paragraphs.
- Focus on what the number or event means for the business.
- Do not simply copy sentences from the report.
- Summarize and explain them.

For example:

Instead of:
"Interest rate volatility may affect fair value movements
in the treasury portfolio."

Prefer:
"Interest rate risk: Changes in interest rates can reduce
the value of the company's investments and affect earnings."

Instead of:
"Asset quality deterioration could increase ECL provisioning."

Prefer:
"Credit risk: If more borrowers struggle to repay their loans,
the company may need to set aside more money for possible losses."

Do NOT remove important financial terms completely.
Explain them when necessary.

--------------------------------------------------

COMPANY IDENTIFICATION

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

--------------------------------------------------

FINANCIAL METRICS

Select only the financial metrics that are relevant
to the company's industry.

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

--------------------------------------------------

IMPORTANT ACCURACY RULES

- Use only information found in the uploaded report.
- Do not invent financial figures.
- Do not guess missing information.
- If a metric is unavailable, write "Not available".
- Clearly distinguish Consolidated and Standalone figures.
- Use the latest financial period available.
- Compare with the previous year whenever available.
- Keep financial figures as reported.
- Mention the correct unit.
- Do not provide Buy, Sell or Hold recommendations.

--------------------------------------------------

BUSINESS PERFORMANCE

Explain the most important developments in the company.

Focus on:

- Revenue and profit performance
- Important business segments
- Major growth areas
- New products or services
- Expansion
- Major investments
- Capital allocation
- Important strategic developments

Write 5 to 8 clear points.

Each point should explain:
WHAT happened + WHY it matters.

--------------------------------------------------

MANAGEMENT COMMENTARY

Summarize important statements made by:

- Chairman
- CEO / MD
- CFO
- Other senior management

Focus on:

- Management's view of the business
- Growth plans
- Future strategy
- Capital allocation
- New businesses
- Industry outlook
- Guidance or expectations

Write 4 to 6 clear points.

Do not present management opinions as guaranteed future results.

--------------------------------------------------

RISK AND HEADWIND ASSESSMENT

Identify the most important risks mentioned or clearly supported
by the financial report.

Focus on:

- Demand slowdown
- Input cost pressure
- Interest rate risk
- Foreign exchange risk
- Credit risk
- Regulatory risk
- Competition
- Technology risk
- Cybersecurity
- Execution risk
- High debt or finance costs
- New business losses
- Supply chain problems
- Macroeconomic risks

Only include risks that are relevant to this company.

For each risk:

1. Give the risk a short name.
2. Explain the risk in simple professional language.
3. Explain why it matters to the company.

Write 4 to 6 risks.

--------------------------------------------------

ANALYST TAKEAWAY

Create four sections:

IMPROVING:
What is getting better?

WEAKENING:
What is getting worse?

GROWTH DRIVERS:
What could support future growth?

INVESTOR WATCH:
What important things should an investor monitor?

Use simple professional language.

Do not give investment recommendations.

--------------------------------------------------

VERY IMPORTANT OUTPUT RULE

Return ONLY valid JSON.

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
        {{
            "risk_name": "",
            "explanation": "",
            "why_it_matters": ""
        }}
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

The "basis" field must say:

"Consolidated"

or

"Standalone"

or

"Not specified"

If a value is unavailable, write:

"Not available"

Financial report:

{text}
"""

        response = client.models.generate_content(
            model="gemini-3.7-flash",
            contents=prompt
        )

        raw_response = response.text

        try:

            analysis = json.loads(raw_response)

            st.success("Financial analysis successfully structured.")

            overview = analysis["company_overview"]
            metrics = analysis["key_metrics"]

            # -----------------------------
            # COMPANY OVERVIEW
            # -----------------------------

            st.header("Company Overview")

            st.subheader(
                overview["company_name"]
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.write("**Industry / Sector**")
                st.write(overview["industry"])

            with col2:
                st.write("**Business Type**")
                st.write(overview["business_type"])

            with col3:
                st.write("**Reporting Period**")
                st.write(overview["reporting_period"])

            st.divider()

            # -----------------------------
            # KEY FINANCIAL METRICS
            # -----------------------------

            st.header("Key Financial Metrics")

            total_income = None
            pat = None
            aum = None

            for metric in metrics:

                metric_name = metric["metric"].lower()

                if (
                    total_income is None
                    and "total income" in metric_name
                ):
                    total_income = metric

                if (
                    pat is None
                    and (
                        "profit after tax" in metric_name
                        or metric_name == "pat"
                    )
                ):
                    pat = metric

                if (
                    aum is None
                    and "assets under management" in metric_name
                ):
                    aum = metric

            card1, card2, card3 = st.columns(3)

            with card1:

                if total_income:

                    st.metric(
                        "Total Income",
                        f'{total_income["current_period"]} {total_income["unit"]}',
                        total_income["yoy_growth"]
                    )

                else:

                    st.metric(
                        "Total Income",
                        "Not available"
                    )

            with card2:

                if pat:

                    st.metric(
                        "Profit After Tax",
                        f'{pat["current_period"]} {pat["unit"]}',
                        pat["yoy_growth"]
                    )

                else:

                    st.metric(
                        "Profit After Tax",
                        "Not available"
                    )

            with card3:

                if aum:

                    st.metric(
                        "Assets Under Management",
                        f'{aum["current_period"]} {aum["unit"]}',
                        aum["yoy_growth"]
                    )

                else:

                    st.metric(
                        "Assets Under Management",
                        "Not available"
                    )

            st.divider()

            # -----------------------------
            # DETAILED FINANCIAL METRICS
            # -----------------------------

            st.subheader("Detailed Financial Metrics")

            table_data = []

            for metric in metrics:

                table_data.append(
                    {
                        "Metric": metric["metric"],
                        "Current Period": metric["current_period"],
                        "Previous Period": metric["previous_period"],
                        "YoY Growth": metric["yoy_growth"],
                        "Unit": metric["unit"],
                        "Basis": metric["basis"]
                    }
                )

            st.dataframe(
                table_data,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            # -----------------------------
            # BUSINESS PERFORMANCE
            # -----------------------------

            st.header("Business Performance")

            business_performance = analysis.get(
                "business_performance",
                []
            )

            if business_performance:

                for item in business_performance:

                    st.markdown(
                        f"- {item}"
                    )

            else:

                st.info(
                    "Business performance information was not available."
                )

            st.divider()

            # -----------------------------
            # MANAGEMENT COMMENTARY
            # -----------------------------

            st.header("Management Commentary")

            management_commentary = analysis.get(
                "management_commentary",
                []
            )

            if management_commentary:

                for item in management_commentary:

                    st.markdown(
                        f"- {item}"
                    )

            else:

                st.info(
                    "Management commentary was not available."
                )

            st.divider()

            # -----------------------------
            # RISK & HEADWIND ASSESSMENT
            # -----------------------------

            st.header("Risk & Headwind Assessment")

            risks = analysis.get(
                "risks",
                []
            )

            if risks:

                for risk in risks:

                    with st.expander(
                        risk.get(
                            "risk_name",
                            "Risk"
                        )
                    ):

                        st.write(
                            "**What is the risk?**"
                        )

                        st.write(
                            risk.get(
                                "explanation",
                                "Not available"
                            )
                        )

                        st.write(
                            "**Why does it matter?**"
                        )

                        st.write(
                            risk.get(
                                "why_it_matters",
                                "Not available"
                            )
                        )

            else:

                st.info(
                    "Risk information was not available."
                )

            st.divider()

            # -----------------------------
            # ANALYST TAKEAWAY
            # -----------------------------

            st.header("Analyst Takeaway")

            takeaway = analysis.get(
                "analyst_takeaway",
                {}
            )

            col1, col2 = st.columns(2)

            with col1:

                st.subheader("What is Improving?")

                for item in takeaway.get(
                    "improving",
                    []
                ):

                    st.markdown(
                        f"- {item}"
                    )

            with col2:

                st.subheader("What is Weakening?")

                for item in takeaway.get(
                    "weakening",
                    []
                ):

                    st.markdown(
                        f"- {item}"
                    )

            st.subheader("Growth Drivers")

            for item in takeaway.get(
                "growth_drivers",
                []
            ):

                st.markdown(
                    f"- {item}"
                )

            st.subheader("What Should an Investor Watch?")

            for item in takeaway.get(
                "investor_watch",
                []
            ):

                st.markdown(
                    f"- {item}"
                )

        except json.JSONDecodeError:

            st.error(
                "Gemini returned an invalid JSON response."
            )

            st.write(raw_response)
