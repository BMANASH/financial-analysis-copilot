import streamlit as st
import json
import re
from google import genai


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Financial Analysis Copilot",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# PAGE STYLING
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 38px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .sub-title {
        font-size: 17px;
        color: #777;
        margin-bottom: 30px;
    }

    .metric-card {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.25);
        background-color: rgba(128,128,128,0.06);
        margin-bottom: 10px;
    }

    .metric-label {
        font-size: 15px;
        color: #777;
        margin-bottom: 5px;
    }

    .metric-value {
        font-size: 28px;
        font-weight: 700;
    }

    .metric-growth {
        font-size: 14px;
        margin-top: 5px;
    }

    .section-box {
        padding: 18px;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.20);
        margin-bottom: 20px;
    }

    .positive {
        color: #16a34a;
        font-weight: 600;
    }

    .negative {
        color: #dc2626;
        font-weight: 600;
    }

    .info-box {
        padding: 15px;
        border-radius: 10px;
        background-color: rgba(59,130,246,0.08);
        border: 1px solid rgba(59,130,246,0.20);
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

if "gemini_file" not in st.session_state:
    st.session_state.gemini_file = None

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "selected_model" not in st.session_state:
    st.session_state.selected_model = None

if "model_errors" not in st.session_state:
    st.session_state.model_errors = []


# ============================================================
# GEMINI CLIENT
# ============================================================

def get_gemini_client():

    try:

        api_key = st.secrets["GEMINI_API_KEY"]

    except Exception:

        st.error(
            "GEMINI_API_KEY was not found in Streamlit Secrets."
        )

        st.stop()

    try:

        client = genai.Client(api_key=api_key)

        return client

    except Exception as e:

        st.error(
            f"Could not connect to Gemini API: {e}"
        )

        st.stop()


client = get_gemini_client()


# ============================================================
# AUTOMATIC MODEL DISCOVERY
# ============================================================

def get_available_models():

    """
    Ask Gemini API which models are currently available
    for this API key.

    We do NOT assume that an old model still exists.
    """

    available = []

    try:

        models = client.models.list()

        for model in models:

            name = getattr(model, "name", "")

            supported_actions = getattr(
                model,
                "supported_actions",
                []
            )

            if not name:
                continue

            # Remove "models/" prefix if present
            clean_name = name.replace("models/", "")

            # We only need models capable of generateContent
            if (
                "generateContent" in supported_actions
                or not supported_actions
            ):

                if "gemini" in clean_name.lower():

                    available.append(clean_name)

    except Exception as e:

        st.session_state.model_errors.append(
            f"Model discovery failed: {e}"
        )

    return available


# ============================================================
# MODEL PRIORITY
# ============================================================

MODEL_PRIORITY = [

    # Newer / stronger models first
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",

    # Lower-cost fallback
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",

    # Older fallback if the API key still supports them
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",

]


def choose_best_model():

    """
    Select the best model that is actually available
    to the current API key.
    """

    available = get_available_models()

    if not available:

        return None, []

    # Convert to lowercase for safer comparison
    available_lower = {
        model.lower(): model
        for model in available
    }

    # First follow our preferred order
    for preferred in MODEL_PRIORITY:

        if preferred.lower() in available_lower:

            return (
                available_lower[preferred.lower()],
                available
            )

    # If none of the preferred models exists,
    # use another Gemini Flash model.
    flash_models = [

        model for model in available
        if "flash" in model.lower()
        and "image" not in model.lower()
        and "live" not in model.lower()
        and "tts" not in model.lower()

    ]

    if flash_models:

        return flash_models[0], available

    # Last fallback
    return available[0], available


# ============================================================
# GENERATE CONTENT WITH AUTOMATIC FALLBACK
# ============================================================

def generate_with_fallback(contents, max_output_tokens=8000):

    """
    Try several available models.

    If one model returns 404 / unavailable / quota /
    temporary errors, try another model automatically.
    """

    available = get_available_models()

    if not available:

        raise Exception(
            "No Gemini models are currently available "
            "for this API key."
        )

    available_lower = {
        model.lower(): model
        for model in available
    }

    # Build model order
    models_to_try = []

    for preferred in MODEL_PRIORITY:

        if preferred.lower() in available_lower:

            actual_model = available_lower[
                preferred.lower()
            ]

            if actual_model not in models_to_try:

                models_to_try.append(actual_model)

    # Add remaining Flash models
    for model in available:

        lower = model.lower()

        if (
            "flash" in lower
            and "image" not in lower
            and "live" not in lower
            and "tts" not in lower
        ):

            if model not in models_to_try:

                models_to_try.append(model)

    errors = []

    # --------------------------------------------------------
    # Try each model
    # --------------------------------------------------------

    for model_name in models_to_try:

        try:

            response = client.models.generate_content(

                model=model_name,

                contents=contents,

                config={
                    "max_output_tokens": max_output_tokens
                }

            )

            text = getattr(response, "text", None)

            if text:

                st.session_state.selected_model = model_name

                return text

            errors.append(
                f"{model_name}: empty response"
            )

        except Exception as e:

            error_text = str(e)

            errors.append(
                f"{model_name}: {error_text}"
            )

            # Try next model automatically
            continue

    raise Exception(
        "All available Gemini models failed.\n\n"
        + "\n\n".join(errors)
    )


# ============================================================
# CLEAN JSON RESPONSE
# ============================================================

def extract_json(text):

    """
    Gemini may sometimes put JSON inside ```json ... ```
    or add a little text around it.

    This function extracts the JSON safely.
    """

    if not text:
        return None

    text = text.strip()

    # Remove markdown code fence
    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    # Find first { and last }
    first = text.find("{")
    last = text.rfind("}")

    if first == -1 or last == -1:

        return None

    json_text = text[first:last + 1]

    try:

        return json.loads(json_text)

    except Exception:

        return None


# ============================================================
# ANALYSIS PROMPT
# ============================================================

ANALYSIS_PROMPT = """

You are a professional financial analyst.

Analyze the uploaded annual report carefully.

IMPORTANT:

The user is NOT an expert financial analyst.

Therefore:

- Use simple professional English.
- Avoid unnecessary technical jargon.
- Explain important financial terms briefly.
- Do not make the response unnecessarily long.
- Do not invent information.
- Use ONLY information available in the uploaded PDF.
- If something is not available in the PDF, write "Not available in the report".
- Clearly separate FACTS from ANALYST INTERPRETATION.
- Do not present assumptions as facts.

The final answer must be returned as VALID JSON ONLY.

Do not use markdown.
Do not use ```json.
Do not add any text before or after the JSON.

Use exactly this structure:

{
  "company_overview": {
    "company_name": "",
    "industry": "",
    "business_type": "",
    "reporting_period": ""
  },

  "key_metrics": [
    {
      "metric": "",
      "current": "",
      "previous": "",
      "growth": "",
      "unit": "",
      "basis": ""
    }
  ],

  "business_performance": [
    {
      "title": "",
      "what_happened": "",
      "why_it_matters": ""
    }
  ],

  "management_commentary": [
    {
      "topic": "",
      "summary": ""
    }
  ],

  "risks": [
    {
      "risk": "",
      "what_it_means": "",
      "why_it_matters": ""
    }
  ],

  "analyst_takeaway": {
    "improving": [],
    "weakening": [],
    "growth_drivers": [],
    "investor_watch": []
  }
}

KEY METRICS:

Include the most important financial and operating metrics.

Prefer metrics such as:

- Total Income
- Profit After Tax
- EPS
- Net Worth
- Debt / Borrowings
- Cash
- AUM
- Loan disbursements
- Payment volume
- Deposits
- NPA
- Capital Adequacy
- Other important industry-specific measures

Do not overload the dashboard.

Use around 8-15 important metrics.

BUSINESS PERFORMANCE:

Explain the important developments.

Each item should have:

"what_happened" = simple factual explanation.

"why_it_matters" = simple analyst interpretation.

MANAGEMENT COMMENTARY:

Summarize what management said.

Do not turn management statements into guaranteed future outcomes.

RISKS:

Explain each risk in simple language.

ANALYST TAKEAWAY:

"improving" = things getting better.

"weakening" = areas under pressure.

"growth_drivers" = factors that could support future growth according to the report.

"investor_watch" = things an investor should monitor.

IMPORTANT:

Do not give a direct BUY / SELL / HOLD recommendation.

If the report does not provide future numerical guidance, do not invent a forecast.

"""


# ============================================================
# DISPLAY COMPANY OVERVIEW
# ============================================================

def display_company_overview(data):

    overview = data.get(
        "company_overview",
        {}
    )

    st.header("Company Overview")

    st.subheader(
        overview.get(
            "company_name",
            "Company"
        )
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Industry / Sector</div>
                <div style="font-size:20px;font-weight:600;">
                    {overview.get("industry", "N/A")}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Business Type</div>
                <div style="font-size:18px;font-weight:600;">
                    {overview.get("business_type", "N/A")}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Reporting Period</div>
                <div style="font-size:20px;font-weight:600;">
                    {overview.get("reporting_period", "N/A")}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# DISPLAY KEY METRICS
# ============================================================

def display_key_metrics(data):

    st.header("Key Financial Metrics")

    metrics = data.get(
        "key_metrics",
        []
    )

    # Show first 3 major metrics as cards
    major_metrics = metrics[:3]

    if major_metrics:

        columns = st.columns(
            len(major_metrics)
        )

        for col, metric in zip(
            columns,
            major_metrics
        ):

            with col:

                growth = str(
                    metric.get(
                        "growth",
                        ""
                    )
                )

                positive = (
                    not growth.startswith("-")
                    and growth not in ["0", "0%"]
                )

                growth_class = (
                    "positive"
                    if positive
                    else "negative"
                )

                st.markdown(
                    f"""
                    <div class="metric-card">

                        <div class="metric-label">
                            {metric.get("metric", "Metric")}
                        </div>

                        <div class="metric-value">
                            {metric.get("current", "N/A")}
                        </div>

                        <div class="metric-growth {growth_class}">
                            {growth}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # --------------------------------------------------------
    # Detailed table
    # --------------------------------------------------------

    st.subheader("Detailed Financial Metrics")

    if metrics:

        table_data = []

        for metric in metrics:

            table_data.append({

                "Metric":
                    metric.get(
                        "metric",
                        ""
                    ),

                "Current":
                    metric.get(
                        "current",
                        ""
                    ),

                "Previous":
                    metric.get(
                        "previous",
                        ""
                    ),

                "YoY Growth":
                    metric.get(
                        "growth",
                        ""
                    ),

                "Unit":
                    metric.get(
                        "unit",
                        ""
                    ),

                "Basis":
                    metric.get(
                        "basis",
                        ""
                    )

            })

        st.dataframe(
            table_data,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# DISPLAY BUSINESS PERFORMANCE
# ============================================================

def display_business_performance(data):

    st.header("Business Performance")

    items = data.get(
        "business_performance",
        []
    )

    for item in items:

        with st.container(border=True):

            st.subheader(
                item.get(
                    "title",
                    "Business Development"
                )
            )

            st.write(
                item.get(
                    "what_happened",
                    ""
                )
            )

            st.markdown(
                "**Why it matters:** "
                + item.get(
                    "why_it_matters",
                    ""
                )
            )


# ============================================================
# MANAGEMENT COMMENTARY
# ============================================================

def display_management_commentary(data):

    st.header("Management Commentary")

    items = data.get(
        "management_commentary",
        []
    )

    for item in items:

        with st.container(border=True):

            st.markdown(
                f"### {item.get('topic', 'Management View')}"
            )

            st.write(
                item.get(
                    "summary",
                    ""
                )
            )


# ============================================================
# RISKS
# ============================================================

def display_risks(data):

    st.header("Risk & Headwind Assessment")

    risks = data.get(
        "risks",
        []
    )

    for risk in risks:

        with st.container(border=True):

            st.subheader(
                risk.get(
                    "risk",
                    "Risk"
                )
            )

            st.markdown(
                "**What does it mean?**"
            )

            st.write(
                risk.get(
                    "what_it_means",
                    ""
                )
            )

            st.markdown(
                "**Why does it matter?**"
            )

            st.write(
                risk.get(
                    "why_it_matters",
                    ""
                )
            )


# ============================================================
# ANALYST TAKEAWAY
# ============================================================

def display_analyst_takeaway(data):

    st.header("Analyst Takeaway")

    takeaway = data.get(
        "analyst_takeaway",
        {}
    )

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "What is Improving?"
        )

        for item in takeaway.get(
            "improving",
            []
        ):

            st.markdown(
                f"- {item}"
            )

    with col2:

        st.subheader(
            "What is Weakening?"
        )

        for item in takeaway.get(
            "weakening",
            []
        ):

            st.markdown(
                f"- {item}"
            )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "Main Growth Drivers"
        )

        for item in takeaway.get(
            "growth_drivers",
            []
        ):

            st.markdown(
                f"- {item}"
            )

    with col2:

        st.subheader(
            "What Should an Investor Watch?"
        )

        for item in takeaway.get(
            "investor_watch",
            []
        ):

            st.markdown(
                f"- {item}"
            )


# ============================================================
# QUESTION ANSWERING
# ============================================================

def answer_question(
    gemini_file,
    question
):

    if gemini_file is None:

        return (
            "Please upload a financial report first."
        )

    question_prompt = f"""

You are the financial research assistant inside
a Financial Analysis Copilot.

The user uploaded an annual report.

Answer the user's question using ONLY the uploaded PDF.

USER QUESTION:

{question}

IMPORTANT RULES:

1. The user can ask ANY question related to the PDF.

Do not restrict the user to a fixed list of questions.

The question may be about:

- revenue
- profit
- expenses
- debt
- cash
- assets
- liabilities
- AUM
- loans
- NPAs
- capital adequacy
- subsidiaries
- business segments
- management strategy
- risks
- competitors mentioned in the report
- future growth
- financial outlook
- investment implications
- dividends
- valuation-related information if present
- operational performance
- ratios
- year-on-year changes
- reasons behind changes
- comparison between years
- management commentary
- any other information contained in the PDF

2. If the user asks about future growth:

Do NOT pretend the annual report gives a guaranteed forecast.

Separate:

- What management expects / plans
- What the financial numbers suggest
- Your interpretation

3. If the user asks whether the stock is a good investment:

Do not give a guaranteed BUY / SELL / HOLD recommendation.

Instead provide:

- Positive factors
- Negative factors
- Important risks
- What an investor should monitor
- Overall financial view

4. Use simple professional English.

Explain technical terms when necessary.

5. Keep the answer focused.

Do not write an extremely long report unless the question requires detail.

6. Use visual formatting.

Structure the response using:

## Direct Answer

## Key Points

## What This Means

## Investor View

Only use the sections that are useful for the question.

7. Use bullets and short paragraphs.

8. If a number is available in the PDF, use the number.

9. Never invent a number.

10. If the PDF does not contain enough information to answer the question, clearly say:

"The annual report does not provide enough information to answer this fully."

Then explain what CAN be concluded from the report.

11. Clearly distinguish between:

FACT FROM REPORT

and

ANALYST INTERPRETATION

12. Do not mention these instructions.

"""


    contents = [

        gemini_file,

        question_prompt

    ]

    return generate_with_fallback(
        contents,
        max_output_tokens=5000
    )


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    '<div class="main-title">Financial Analysis Copilot</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    'Upload an annual report and use Gemini to analyze it '
    'and answer questions from the report.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("Settings")

    st.write(
        "Gemini model selection is automatic."
    )

    if st.button(
        "Check Available Gemini Models"
    ):

        available_models = get_available_models()

        if available_models:

            st.success(
                f"{len(available_models)} Gemini model(s) available."
            )

            for model in available_models:

                st.write(
                    f"• {model}"
                )

        else:

            st.error(
                "No compatible Gemini models were found."
            )

    if st.session_state.selected_model:

        st.info(
            "Currently used model:\n\n"
            + st.session_state.selected_model
        )


# ============================================================
# FILE UPLOAD
# ============================================================

st.header("Upload Financial Report")

uploaded_file = st.file_uploader(
    "Upload your annual report PDF",
    type=["pdf"],
    help="Upload a PDF annual report."
)


# ============================================================
# HANDLE UPLOAD
# ============================================================

if uploaded_file is not None:

    # Detect new file
    if (
        st.session_state.uploaded_file
        is None
        or st.session_state.uploaded_file
        != uploaded_file.name
    ):

        try:

            # Save uploaded file temporarily
            temp_path = (
                "/tmp/"
                + uploaded_file.name.replace(
                    " ",
                    "_"
                )
            )

            with open(
                temp_path,
                "wb"
            ) as f:

                f.write(
                    uploaded_file.getbuffer()
                )

            # Upload to Gemini Files API
            with st.spinner(
                "Uploading PDF to Gemini..."
            ):

                gemini_file = client.files.upload(
                    file=temp_path
                )

            st.session_state.gemini_file = (
                gemini_file
            )

            st.session_state.uploaded_file = (
                uploaded_file.name
            )

            st.session_state.analysis = None

            st.success(
                "Financial report uploaded successfully."
            )

        except Exception as e:

            st.error(
                "Could not upload the PDF to Gemini."
            )

            st.code(
                str(e)
            )


# ============================================================
# ANALYSIS SECTION
# ============================================================

if st.session_state.gemini_file is not None:

    st.header(
        "Generate Financial Analysis"
    )

    st.write(
        "Gemini will analyze the complete financial report "
        "and organize the results into a dashboard."
    )

    if st.button(
        "Ask Gemini to Analyze",
        type="primary"
    ):

        with st.spinner(
            "Analyzing the financial report..."
        ):

            try:

                contents = [

                    st.session_state.gemini_file,

                    ANALYSIS_PROMPT

                ]

                raw_response = (
                    generate_with_fallback(
                        contents,
                        max_output_tokens=12000
                    )
                )

                parsed = extract_json(
                    raw_response
                )

                if parsed is None:

                    st.error(
                        "Gemini returned an unexpected "
                        "format. Showing the raw response."
                    )

                    st.markdown(
                        raw_response
                    )

                else:

                    st.session_state.analysis = (
                        parsed
                    )

                    st.success(
                        "Financial analysis generated successfully."
                    )

            except Exception as e:

                st.error(
                    "Gemini could not analyze the report."
                )

                st.code(
                    str(e)
                )


# ============================================================
# DISPLAY ANALYSIS
# ============================================================

if st.session_state.analysis:

    data = st.session_state.analysis

    st.divider()

    display_company_overview(
        data
    )

    st.divider()

    display_key_metrics(
        data
    )

    st.divider()

    display_business_performance(
        data
    )

    st.divider()

    display_management_commentary(
        data
    )

    st.divider()

    display_risks(
        data
    )

    st.divider()

    display_analyst_takeaway(
        data
    )


# ============================================================
# Q&A SECTION
# ============================================================

if st.session_state.gemini_file is not None:

    st.divider()

    st.header(
        "Ask Questions About This Financial Report"
    )

    st.write(
        "Ask Gemini any question related to the uploaded "
        "financial report."
    )

    question = st.text_input(
        "Your question:",
        placeholder=(
            "Example: What are the main factors that "
            "could drive the company's future growth?"
        )
    )

    if st.button(
        "Ask Gemini",
        key="question_button"
    ):

        if not question.strip():

            st.warning(
                "Please enter a question."
            )

        else:

            with st.spinner(
                "Reading the report and preparing the answer..."
            ):

                try:

                    answer = answer_question(
                        st.session_state.gemini_file,
                        question
                    )

                    st.subheader(
                        "Gemini's Answer"
                    )

                    st.markdown(
                        answer
                    )

                    if st.session_state.selected_model:

                        st.caption(
                            "Model used: "
                            + st.session_state.selected_model
                        )

                except Exception as e:

                    st.error(
                        "Gemini could not answer the question."
                    )

                    st.code(
                        str(e)
                    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Financial Analysis Copilot • "
    "AI-generated analysis is for research and educational "
    "purposes and should not be treated as financial advice."
)
