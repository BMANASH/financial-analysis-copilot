import streamlit as st
import os
import json
from pypdf import PdfReader
from google import genai


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="Financial Analysis Copilot",
    page_icon="📊",
    layout="wide"
)


# ---------------------------------------------------------
# GEMINI API SETUP
# ---------------------------------------------------------

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Gemini API key is not configured.")
    st.stop()

client = genai.Client(api_key=api_key)


# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------

st.title("Financial Analysis Copilot")

st.write(
    "Upload a company's financial report and get a simple, "
    "professional financial analysis powered by Gemini."
)


# ---------------------------------------------------------
# PDF UPLOAD
# ---------------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload a financial report (PDF)",
    type=["pdf"]
)


# ---------------------------------------------------------
# READ PDF
# ---------------------------------------------------------

extracted_text = ""

if uploaded_file is not None:

    try:
        reader = PdfReader(uploaded_file)

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                extracted_text += page_text + "\n"

        st.success("Financial report uploaded successfully.")

    except Exception as e:
        st.error(f"Could not read the PDF: {e}")
        st.stop()


# ---------------------------------------------------------
# FINANCIAL ANALYSIS
# ---------------------------------------------------------

if uploaded_file is not None and extracted_text:

    st.subheader("Generate Financial Analysis")

    if st.button("Ask Gemini to Analyze"):

        with st.spinner("Gemini is analyzing the financial report..."):

            analysis_prompt = f"""
You are a professional financial analyst.

Analyze the uploaded financial report and create a clear,
professional financial analysis.

IMPORTANT INSTRUCTIONS:

1. Identify the company name from the uploaded report.
2. Identify the reporting period.
3. Do not assume that the report belongs to a particular company.
4. Analyze whichever company is present in the uploaded PDF.
5. Use ONLY information available in the uploaded report.
6. Do not invent financial figures, management statements,
   guidance, risks, or business information.
7. If a particular metric is not available, clearly say
   "Not available in the report."
8. Use simple and professional language.
9. Avoid unnecessary technical jargon.
10. Explain important numbers in a way that a finance student
    or beginner can understand.
11. When discussing growth or decline, explain the likely reason
    based on the report.

Structure the answer using the following sections:

1. COMPANY OVERVIEW

Include:
- Company Name
- Industry / Sector
- Business Type
- Reporting Period
- Type of Report

2. KEY FINANCIAL METRICS

Create a clear table containing important metrics such as:
- Revenue / Total Income
- Operating Profit / EBITDA, where applicable
- EBITDA Margin, where applicable
- Profit Before Tax
- Profit After Tax
- EPS
- Debt / Borrowings
- Cash / Cash Equivalents
- Important industry-specific metrics

Show:
- Current period
- Previous period
- YoY or QoQ growth where available
- Units

Do not force metrics that are not relevant to the company.

3. BUSINESS PERFORMANCE

Explain the company's major business developments,
segment performance, important growth areas and changes
in the business.

4. MANAGEMENT COMMENTARY

Summarize important statements from management regarding:
- Growth
- Future plans
- Capital expenditure
- New products
- Expansion
- Margins
- Industry outlook
- Guidance

Clearly distinguish management commentary from
your own interpretation.

5. RISK AND HEADWIND ASSESSMENT

Identify important risks mentioned or supported by the report.

For each major risk explain:
- What is the risk?
- Why does it matter?

6. ANALYST TAKEAWAY

Explain:

WHAT IS IMPROVING?
WHAT IS WEAKENING?
WHAT ARE THE MAIN GROWTH DRIVERS?
WHAT SHOULD AN INVESTOR WATCH?

Keep this section practical and easy to understand.

The final response should be professional, structured,
and readable.

Financial Report:
{extracted_text}
"""

            try:

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=analysis_prompt
                )

                st.session_state["financial_analysis"] = response.text

            except Exception as e:
                st.error(f"Gemini analysis failed: {e}")


# ---------------------------------------------------------
# DISPLAY FINANCIAL ANALYSIS
# ---------------------------------------------------------

if "financial_analysis" in st.session_state:

    st.markdown("---")

    st.header("Financial Analysis")

    st.markdown(
        st.session_state["financial_analysis"]
    )


# ---------------------------------------------------------
# INTERACTIVE Q&A
# ---------------------------------------------------------

if uploaded_file is not None and extracted_text:

    st.markdown("---")

    st.header("Ask Questions About This Financial Report")

    st.write(
        "Ask Gemini any question related to the uploaded "
        "financial report."
    )

    user_question = st.text_input(
        "Your question:",
        placeholder="Example: Why did the company's profit decline?"
    )

    if st.button("Ask Gemini", key="ask_question_button"):

        if not user_question.strip():

            st.warning("Please enter a question first.")

        else:

            with st.spinner("Gemini is finding the answer..."):

                qa_prompt = f"""
You are a professional financial analysis assistant.

The user has uploaded a financial report and is asking a question
about that document.

The user may ask ANY reasonable question related to the uploaded
financial report.

The question may relate to:

- Revenue
- Profitability
- EBITDA
- Margins
- Balance sheet
- Cash flow
- Debt
- Borrowings
- Financial ratios
- Segment performance
- Business performance
- Management commentary
- Management guidance
- Future plans
- Capital expenditure
- Strategy
- Risks
- Headwinds
- Growth drivers
- Industry-specific metrics
- Year-on-year comparisons
- Quarter-on-quarter comparisons
- Any specific number, statement, section, or topic contained
  in the financial report

IMPORTANT RULES:

1. Answer the user's actual question directly.

2. Do NOT restrict the user to predefined questions.

3. Use ONLY information available in the uploaded financial report.

4. Do NOT invent or assume information that is not present
   in the report.

5. If the answer cannot be found in the uploaded report,
   clearly say:

   "This information is not available in the uploaded report."

6. If the question asks for information outside the report,
   such as today's share price, current market price, live news,
   or information from another source, clearly explain that
   the uploaded report does not contain that information.

7. Use simple language while remaining professional.

8. Avoid unnecessary technical jargon.

9. When giving financial figures, mention the relevant period
   and unit where possible.

10. When useful, explain WHY the information matters.

11. If the user asks for a comparison, clearly compare the
    relevant periods or business segments.

12. If the user asks for an opinion such as whether performance
    is improving or weakening, base the answer only on evidence
    from the report and clearly label it as an analytical
    interpretation.

13. Do not provide investment advice such as "buy", "sell",
    or "hold" unless the user specifically asks for an
    analytical view. Even then, explain that the response
    is based only on the uploaded document.

USER QUESTION:

{user_question}

UPLOADED FINANCIAL REPORT:

{extracted_text}
"""

                try:

                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=qa_prompt
                    )

                    st.subheader("Gemini's Answer")

                    st.markdown(response.text)

                except Exception as e:

                    st.error(
                        f"Gemini could not answer the question: {e}"
                    )
