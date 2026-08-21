import streamlit as st
import os
import json
import re
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
        "Please check your Streamlit Secrets."
    )
    st.stop()

client = genai.Client(api_key=api_key)


# =========================================================
# GEMINI MODEL HANDLER
# =========================================================

def ask_gemini(prompt):
    """
    Sends a prompt to Gemini.

    The app tries the preferred model first.
    If it is unavailable, it automatically tries
    backup models.
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

            if response and response.text:
                return response.text

        except Exception as error:

            last_error = error
            continue

    raise Exception(
        "Gemini could not be reached using the available "
        "models.\n\n"
        f"Last error: {last_error}"
    )


# =========================================================
# CLEAN GEMINI OUTPUT
# =========================================================

def clean_gemini_output(text):
    """
    Removes unwanted HTML/code formatting if Gemini
    accidentally returns it.
    """

    if not text:
        return ""

    # Remove HTML code fences
    text = re.sub(
        r"```html\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"```\s*",
        "",
        text
    )

    # Remove common HTML tags
    text = re.sub(
        r"<div[^>]*>",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"</div>",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"<span[^>]*>",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"</span>",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"<p[^>]*>",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"</p>",
        "\n",
        text,
        flags=re.IGNORECASE
    )

    # Remove SVG tags if Gemini accidentally creates them
    text = re.sub(
        r"<svg.*?</svg>",
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    # Remove common CSS-style HTML attributes
    text = re.sub(
        r'class="[^"]*"',
        "",
        text,
        flags=re.IGNORECASE
    )

    return text.strip()


# =========================================================
# PDF TEXT EXTRACTION
# =========================================================

def extract_pdf_text(uploaded_file):

    reader = PdfReader(uploaded_file)

    pages_text = []

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            pages_text.append(page_text)

    return "\n\n".join(pages_text)


# =========================================================
# PDF UPLOAD
# =========================================================

st.title("Financial Analysis Copilot")

st.write(
    "Upload a company's financial report and generate "
    "a clear financial analysis using Gemini."
)

uploaded_file = st.file_uploader(
    "Upload a financial report (PDF)",
    type=["pdf"]
)


# =========================================================
# PROCESS PDF
# =========================================================

if uploaded_file is not None:

    try:

        extracted_text = extract_pdf_text(
            uploaded_file
        )

        if not extracted_text.strip():

            st.error(
                "The PDF was uploaded, but no readable text "
                "could be extracted from it."
            )

            st.stop()

        # Save report text in session
        st.session_state["report_text"] = extracted_text

        st.success(
            "Financial report uploaded successfully."
        )

    except Exception as error:

        st.error(
            f"Could not read the PDF: {error}"
        )

        st.stop()


# =========================================================
# FINANCIAL ANALYSIS
# =========================================================

if "report_text" in st.session_state:

    report_text = st.session_state["report_text"]

    st.markdown("---")

    st.header("Generate Financial Analysis")

    if st.button(
        "Ask Gemini to Analyze",
        key="generate_analysis"
    ):

        with st.spinner(
            "Gemini is analyzing the financial report..."
        ):

            analysis_prompt = f"""
You are a professional financial analyst.

Analyze the uploaded financial report.

The report may belong to ANY company.

You must identify the company directly from the
uploaded report.

Do NOT assume the company name.

==================================================
VERY IMPORTANT OUTPUT RULES
==================================================

Return ONLY clean Markdown.

DO NOT return HTML.

DO NOT return:

- <div>
- <span>
- <p>
- <table>
- <svg>
- CSS
- JavaScript
- HTML code blocks
- JSON
- Python code
- UI code
- CSS class names

DO NOT create your own HTML cards.

The application will create the visual cards itself.

Use normal Markdown headings, bullet points and
Markdown tables only.

==================================================
GENERAL RULES
==================================================

1. Use only information available in the uploaded report.

2. Do not invent numbers.

3. Do not assume missing information.

4. If a metric is unavailable, say:
   "Not available in the report."

5. Clearly distinguish consolidated and standalone
   figures.

6. Clearly mention the reporting period.

7. Use simple professional language.

8. Avoid unnecessary technical jargon.

9. Explain why important changes matter.

10. If the company is from a different industry,
    automatically adjust the metrics to that industry.

For example:

A bank may require:
- Net Interest Income
- NIM
- GNPA
- NNPA
- CASA
- Capital Adequacy

A manufacturing company may require:
- Revenue
- EBITDA
- EBITDA margin
- Capacity
- Utilisation
- Debt

A technology company may require:
- Revenue
- ARR
- Customers
- Margins
- Cash flow

Do not force irrelevant metrics.

==================================================
REQUIRED STRUCTURE
==================================================

# COMPANY OVERVIEW

Include:

- Company Name
- Industry / Sector
- Business Type
- Reporting Period
- Type of Report

==================================================

# KEY FINANCIAL METRICS

Create a Markdown table.

Use these columns:

| Metric | Current Period | Previous Period | YoY Growth | Unit | Basis |
|---|---:|---:|---:|---|---|

Include the most important financial metrics available
in the report.

Possible metrics include:

- Revenue / Total Income
- Operating Profit
- EBITDA
- EBITDA Margin
- PBT
- PAT
- EPS
- Debt
- Cash
- Assets
- Net Worth
- Important industry-specific metrics

Only include metrics that are actually available
and relevant.

==================================================

# BUSINESS PERFORMANCE

Explain the major developments in simple professional
language.

Focus on:

- Revenue growth
- Profit growth
- Segment performance
- Business expansion
- New products
- Important operational developments
- Important changes from the previous period

==================================================

# MANAGEMENT COMMENTARY

Summarize important management statements.

Cover:

- Growth plans
- Strategy
- Expansion
- Capital expenditure
- New products
- Future plans
- Industry outlook
- Management guidance

Clearly identify these as management statements.

==================================================

# RISK AND HEADWIND ASSESSMENT

For each major risk use this format:

### Risk Name

**What is the risk?**

Explain it simply.

**Why does it matter?**

Explain the possible financial or business impact.

==================================================

# ANALYST TAKEAWAY

Use these four sections:

## What is improving?

List the strongest positive developments.

## What is weakening?

List the major negative developments.

## Main growth drivers

Explain what could support future growth based
on the report.

## What should an investor watch?

Explain the most important things an investor
should monitor.

==================================================
IMPORTANT INVESTMENT RULE
==================================================

If the user later asks whether the company is a good
investment, do NOT blindly say BUY or SELL.

Instead:

- Use evidence from the report.
- Explain positive factors.
- Explain negative factors.
- Explain risks.
- Explain what an investor should monitor.

Do not claim that the annual report can predict
the future stock price.

==================================================

UPLOADED FINANCIAL REPORT:

{report_text}
"""

            try:

                analysis_result = ask_gemini(
                    analysis_prompt
                )

                analysis_result = clean_gemini_output(
                    analysis_result
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
# ASK QUESTIONS ABOUT THE REPORT
# =========================================================

if "report_text" in st.session_state:

    report_text = st.session_state["report_text"]

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
            "Example: What are the main risks to "
            "the company's future growth?"
        ),
        key="financial_question"
    )

    if st.button(
        "Ask Gemini",
        key="ask_question"
    ):

        if not user_question.strip():

            st.warning(
                "Please enter a question first."
            )

        else:

            with st.spinner(
                "Gemini is analyzing your question..."
            ):

                qa_prompt = f"""
You are a professional financial analysis assistant.

A user has uploaded a financial report.

The user can ask ANY reasonable question related
to that report.

The question is NOT limited to a fixed list.

==================================================
IMPORTANT OUTPUT RULES
==================================================

Return ONLY clean Markdown.

DO NOT return HTML.

DO NOT return:

- <div>
- <span>
- <p>
- <table>
- <svg>
- CSS
- JavaScript
- HTML code
- Python code
- UI code

Use normal Markdown only.

==================================================
ANSWER RULES
==================================================

1. Answer the user's actual question directly.

2. Use information from the uploaded report.

3. Do not invent information.

4. If the report does not contain the answer, say:

"This information is not available in the uploaded report."

5. If the user asks about information that requires
current external data, clearly explain that the uploaded
report does not provide that information.

Examples:

- Current stock price
- Today's market price
- Live news
- Current analyst target price
- Current market capitalisation

6. Use simple professional language.

7. Avoid unnecessary technical terms.

8. If you use a financial number, mention its
relevant period and unit.

9. If comparing two periods, clearly show the change.

10. Explain WHY the number or change matters when useful.

11. Separate facts from your interpretation.

12. Do not present your interpretation as management's
statement.

13. Do not invent future management guidance.

14. If the report does not provide future guidance,
clearly say so.

==================================================
INVESTMENT QUESTIONS
==================================================

If the user asks:

"Is this a good investment?"

or

"Should I buy this stock?"

or similar questions:

Do NOT give a blind BUY or SELL recommendation.

Instead explain:

- Financial strengths
- Financial weaknesses
- Growth drivers
- Key risks
- Important investor watchpoints

Also clearly state that the report alone cannot
predict the future stock price.

==================================================
USER QUESTION
==================================================

{user_question}

==================================================
UPLOADED FINANCIAL REPORT
==================================================

{report_text}
"""

                try:

                    answer = ask_gemini(
                        qa_prompt
                    )

                    answer = clean_gemini_output(
                        answer
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
