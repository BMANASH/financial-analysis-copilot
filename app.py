import streamlit as st
import os
from pypdf import PdfReader
from google import genai


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Financial Analysis Copilot",
    page_icon="📊",
    layout="wide"
)


# =========================================================
# GEMINI API SETUP
# =========================================================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error(
        "Gemini API key is not configured. "
        "Please check your Streamlit secrets."
    )
    st.stop()

client = genai.Client(api_key=api_key)


# =========================================================
# GEMINI MODEL HANDLER
# =========================================================

def ask_gemini(prompt):
    """
    Sends the prompt to Gemini.

    The application tries the newer model first.
    If that model is unavailable, it automatically
    tries the backup models.
    """

    models_to_try = [
        "gemini-3.6-flash",
        "gemini-2.5-flash",
        "gemini-2.0-flash"
    ]

    last_error = None

    for model_name in models_to_try:

        try:

            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )

            return response.text

        except Exception as error:

            last_error = error

            continue

    raise Exception(
        "None of the configured Gemini models are currently "
        "available for this API key.\n\n"
        f"Last error: {last_error}"
    )


# =========================================================
# TITLE
# =========================================================

st.title("Financial Analysis Copilot")

st.write(
    "Upload a company's financial report and get a "
    "professional financial analysis powered by Gemini."
)


# =========================================================
# PDF UPLOAD
# =========================================================

uploaded_file = st.file_uploader(
    "Upload a financial report (PDF)",
    type=["pdf"]
)


# =========================================================
# PDF TEXT EXTRACTION
# =========================================================

extracted_text = ""

if uploaded_file is not None:

    try:

        reader = PdfReader(uploaded_file)

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                extracted_text += page_text + "\n"

        if extracted_text.strip():

            st.success(
                "Financial report uploaded successfully."
            )

        else:

            st.warning(
                "The PDF was uploaded, but no readable text "
                "could be extracted."
            )

    except Exception as error:

        st.error(
            f"Could not read the PDF: {error}"
        )

        st.stop()


# =========================================================
# FINANCIAL ANALYSIS
# =========================================================

if uploaded_file is not None and extracted_text.strip():

    st.subheader("Generate Financial Analysis")

    if st.button("Ask Gemini to Analyze"):

        with st.spinner(
            "Gemini is analyzing the financial report..."
        ):

            analysis_prompt = f"""
You are a professional financial analyst.

Analyze the uploaded financial report and create a clear,
professional financial analysis.

IMPORTANT INSTRUCTIONS:

1. Identify the company name directly from the report.

2. Identify the reporting period directly from the report.

3. Do not assume the report belongs to a particular company.

4. Analyze whichever company is present in the uploaded PDF.

5. Use ONLY information available in the uploaded report.

6. Do not invent financial figures, management statements,
   guidance, risks, or business information.

7. If a particular metric is not available, clearly say:
   "Not available in the report."

8. Use simple language while remaining professional.

9. Avoid unnecessary technical jargon.

10. Explain important numbers in a way that a finance student
    or beginner can understand.

11. When discussing growth or decline, explain why it happened
    based on information available in the report.

12. Do not confuse consolidated and standalone figures.

13. Clearly mention the reporting period for important figures.

STRUCTURE THE ANALYSIS AS FOLLOWS:

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
- Consolidated or Standalone basis where relevant

Do not force metrics that are not relevant to the company.

3. BUSINESS PERFORMANCE

Explain:

- Major business developments
- Segment performance
- Major growth areas
- Important changes in the business
- Major operational achievements

4. MANAGEMENT COMMENTARY

Summarize important management statements regarding:

- Growth
- Future plans
- Capital expenditure
- New products
- Expansion
- Margins
- Industry outlook
- Management guidance

Clearly distinguish management commentary from
your own analytical interpretation.

5. RISK AND HEADWIND ASSESSMENT

Identify important risks mentioned or supported by the report.

For each major risk explain:

WHAT IS THE RISK?

WHY DOES IT MATTER?

6. ANALYST TAKEAWAY

Explain:

WHAT IS IMPROVING?

WHAT IS WEAKENING?

WHAT ARE THE MAIN GROWTH DRIVERS?

WHAT SHOULD AN INVESTOR WATCH?

Keep this section practical and easy to understand.

The final answer should be professional, structured,
simple, and readable.

UPLOADED FINANCIAL REPORT:

{extracted_text}
"""

            try:

                analysis_result = ask_gemini(
                    analysis_prompt
                )

                st.session_state[
                    "financial_analysis"
                ] = analysis_result

            except Exception as error:

                st.error(
                    f"Gemini analysis failed: {error}"
                )


# =========================================================
# DISPLAY FINANCIAL ANALYSIS
# =========================================================

if "financial_analysis" in st.session_state:

    st.markdown("---")

    st.header("Financial Analysis")

    st.markdown(
        st.session_state["financial_analysis"]
    )


# =========================================================
# INTERACTIVE Q&A
# =========================================================

if uploaded_file is not None and extracted_text.strip():

    st.markdown("---")

    st.header(
        "Ask Questions About This Financial Report"
    )

    st.write(
        "Ask Gemini any question related to the "
        "uploaded financial report."
    )

    user_question = st.text_input(
        "Your question:",
        placeholder=(
            "Example: Why did the company's profit decline?"
        )
    )

    if st.button(
        "Ask Gemini",
        key="ask_question_button"
    ):

        if not user_question.strip():

            st.warning(
                "Please enter a question first."
            )

        else:

            with st.spinner(
                "Gemini is finding the answer..."
            ):

                qa_prompt = f"""
You are a professional financial analysis assistant.

The user has uploaded a financial report and is asking
a question about that document.

The user may ask ANY reasonable question related to
the uploaded financial report.

The question is NOT limited to predefined questions.

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
- Any specific number, statement, section,
  or topic contained in the financial report

IMPORTANT RULES:

1. Answer the user's actual question directly.

2. Do not restrict the user to predefined questions.

3. Use ONLY information available in the uploaded
   financial report.

4. Do NOT invent or assume information that is not
   present in the report.

5. If the answer cannot be found in the uploaded report,
   clearly say:

   "This information is not available in the uploaded report."

6. If the user asks for information outside the report,
   such as today's share price, current market price,
   live news, or information from another source,
   clearly explain that the uploaded report does not
   contain that information.

7. Use simple language while remaining professional.

8. Avoid unnecessary technical jargon.

9. When giving financial figures, mention the relevant
   period and unit where possible.

10. When useful, explain WHY the information matters.

11. If the user asks for a comparison, clearly compare
    the relevant periods or business segments.

12. If the user asks for an opinion about whether
    performance is improving or weakening, base the
    interpretation only on evidence from the report.

13. Clearly separate facts from analytical interpretation.

14. Do not present an analytical interpretation as a
    statement made by management.

15. Do not invent management guidance.

16. If the report does not provide future guidance,
    clearly say so.

17. If the user asks whether the company is a good
    investment, explain the positive and negative
    factors from the report rather than giving a
    blind BUY or SELL recommendation.

USER QUESTION:

{user_question}

UPLOADED FINANCIAL REPORT:

{extracted_text}
"""

                try:

                    answer = ask_gemini(
                        qa_prompt
                    )

                    st.subheader(
                        "Gemini's Answer"
                    )

                    st.markdown(answer)

                except Exception as error:

                    st.error(
                        f"Gemini could not answer "
                        f"the question: {error}"
                    )
