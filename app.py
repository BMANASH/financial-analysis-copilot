import streamlit as st
import json
import re
import tempfile
import os
import time
from google import genai
from google.genai import types


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Financial Analysis Copilot",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #0e1117;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    .hero {
        padding: 28px 32px;
        border-radius: 18px;
        background: linear-gradient(
            135deg,
            #151a24 0%,
            #1d2635 100%
        );
        border: 1px solid #2d3748;
        margin-bottom: 25px;
    }

    .hero-title {
        font-size: 38px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        color: #aab4c3;
        font-size: 17px;
    }

    .section-title {
        font-size: 27px;
        font-weight: 650;
        margin-top: 28px;
        margin-bottom: 16px;
    }

    .company-card {
        padding: 20px;
        border-radius: 14px;
        background: #151a24;
        border: 1px solid #2d3748;
        height: 100%;
    }

    .company-label {
        font-size: 13px;
        color: #8f9aaa;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 5px;
    }

    .company-value {
        font-size: 18px;
        font-weight: 600;
    }

    .insight-card {
        padding: 20px;
        border-radius: 14px;
        background: #151a24;
        border: 1px solid #2d3748;
        margin-bottom: 12px;
    }

    .insight-title {
        font-size: 17px;
        font-weight: 650;
        margin-bottom: 8px;
    }

    .insight-text {
        color: #b8c1ce;
        line-height: 1.65;
        font-size: 15px;
    }

    .risk-card {
        padding: 20px;
        border-radius: 14px;
        background: #17171b;
        border: 1px solid #3a3030;
        margin-bottom: 14px;
    }

    .risk-title {
        font-size: 17px;
        font-weight: 650;
        margin-bottom: 8px;
    }

    .risk-text {
        color: #b8c1ce;
        line-height: 1.6;
    }

    .watch-card {
        padding: 18px;
        border-radius: 14px;
        background: #151a24;
        border: 1px solid #2d3748;
        margin-bottom: 10px;
        line-height: 1.55;
    }

    .small-note {
        color: #8f9aaa;
        font-size: 13px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "gemini_file" not in st.session_state:
    st.session_state.gemini_file = None

if "uploaded_name" not in st.session_state:
    st.session_state.uploaded_name = None

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "selected_model" not in st.session_state:
    st.session_state.selected_model = None


# ============================================================
# API KEY
# ============================================================

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    API_KEY = None


if not API_KEY:
    st.error(
        "Gemini API key was not found. "
        "Please add GEMINI_API_KEY to Streamlit Secrets."
    )
    st.stop()


# ============================================================
# GEMINI CLIENT
# ============================================================

@st.cache_resource
def create_client(api_key):
    return genai.Client(api_key=api_key)


client = create_client(API_KEY)


# ============================================================
# AUTOMATIC MODEL DETECTION
# ============================================================

def get_available_models():
    """
    Find Gemini models that support generateContent.

    We do not permanently depend on one model version.
    """

    try:
        models = []

        for model in client.models.list():

            name = getattr(model, "name", "")

            if not name:
                continue

            clean_name = name.replace("models/", "")

            supported_actions = getattr(
                model,
                "supported_actions",
                []
            ) or []

            if "generateContent" in supported_actions:
                if "gemini" in clean_name.lower():
                    models.append(clean_name)

        return models

    except Exception:
        return []


def choose_best_model():
    """
    Select the best currently available Gemini model.

    Preference:
    1. Newer Flash models
    2. Other Flash models
    3. Other Gemini models
    """

    available = get_available_models()

    if not available:
        return None

    preferred_keywords = [
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-3-flash",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "flash"
    ]

    for keyword in preferred_keywords:

        for model in available:

            if keyword in model.lower():

                return model

    return available[0]


def get_model():
    """
    Get a usable Gemini model.
    """

    if st.session_state.selected_model:
        return st.session_state.selected_model

    model = choose_best_model()

    if model:
        st.session_state.selected_model = model

    return model


# ============================================================
# SAFE JSON EXTRACTION
# ============================================================

def clean_json_response(text):
    """
    Gemini normally returns JSON, but this function also handles
    cases where Gemini puts JSON inside ```json ... ``` blocks.
    """

    if not text:
        return {}

    text = text.strip()

    # Remove markdown code fences
    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"^```\s*",
        "",
        text
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    text = text.strip()

    try:
        return json.loads(text)

    except Exception:

        # Try to find the first JSON object
        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end != -1 and end > start:

            possible_json = text[start:end + 1]

            try:
                return json.loads(possible_json)
            except Exception:
                pass

    return {}


# ============================================================
# GEMINI CALL WITH AUTOMATIC MODEL FALLBACK
# ============================================================

def generate_with_fallback(contents, json_mode=False):
    """
    Try the selected model first.

    If it fails, automatically try other available Gemini models.
    """

    available_models = get_available_models()

    selected = get_model()

    ordered_models = []

    if selected:
        ordered_models.append(selected)

    for model in available_models:

        if model not in ordered_models:
            ordered_models.append(model)

    if not ordered_models:

        # Last-resort model names.
        ordered_models = [
            "gemini-3.7-flash",
            "gemini-3.6-flash",
            "gemini-2.5-flash",
            "gemini-2.0-flash"
        ]

    last_error = None

    for model in ordered_models:

        try:

            if json_mode:

                config = types.GenerateContentConfig(
                    response_mime_type="application/json"
                )

                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config
                )

            else:

                response = client.models.generate_content(
                    model=model,
                    contents=contents
                )

            st.session_state.selected_model = model

            return response

        except Exception as error:

            last_error = error
            continue

    raise Exception(
        f"Gemini could not find a working model. "
        f"Last error: {last_error}"
    )


# ============================================================
# PDF UPLOAD
# ============================================================

st.sidebar.title("Financial Analysis Copilot")

st.sidebar.write(
    "Upload an annual report or financial PDF "
    "and let Gemini analyse it."
)

uploaded_file = st.sidebar.file_uploader(
    "Upload Financial Report",
    type=["pdf"]
)


if uploaded_file:

    if (
        st.session_state.uploaded_name
        != uploaded_file.name
    ):

        with st.spinner(
            "Uploading financial report to Gemini..."
        ):

            try:

                # Create temporary PDF file
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf"
                ) as temp_file:

                    temp_file.write(
                        uploaded_file.getbuffer()
                    )

                    temp_path = temp_file.name

                # Upload PDF to Gemini
                gemini_file = client.files.upload(
                    file=temp_path
                )

                # Wait for processing if necessary
                for _ in range(20):

                    state = getattr(
                        gemini_file,
                        "state",
                        None
                    )

                    state_name = getattr(
                        state,
                        "name",
                        ""
                    )

                    if not state_name:
                        break

                    if state_name == "ACTIVE":
                        break

                    if state_name == "FAILED":
                        raise Exception(
                            "Gemini failed to process the PDF."
                        )

                    time.sleep(1)

                    gemini_file = client.files.get(
                        name=gemini_file.name
                    )

                st.session_state.gemini_file = gemini_file
                st.session_state.uploaded_name = uploaded_file.name
                st.session_state.analysis = None
                st.session_state.chat_history = []

                # Delete local temporary file
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

                st.success(
                    "Financial report uploaded successfully."
                )

            except Exception as error:

                st.error(
                    f"Could not upload the PDF: {error}"
                )


# ============================================================
# HERO SECTION
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">
            Financial Analysis Copilot
        </div>

        <div class="hero-subtitle">
            AI-powered financial analysis from annual reports
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# NO PDF MESSAGE
# ============================================================

if not st.session_state.gemini_file:

    st.info(
        "Upload a financial report from the sidebar to begin."
    )

    st.stop()


# ============================================================
# GENERATE ANALYSIS
# ============================================================

st.markdown(
    '<div class="section-title">Generate Financial Analysis</div>',
    unsafe_allow_html=True
)

st.write(
    "Gemini will read the uploaded report and create a "
    "structured financial dashboard."
)


if st.button(
    "Generate Financial Analysis",
    type="primary"
):

    model = get_model()

    if not model:

        st.error(
            "No usable Gemini model was found for this API key."
        )

    else:

        analysis_prompt = """
You are a professional financial analyst.

Analyze ONLY the uploaded financial report.

The uploaded PDF may belong to ANY company.
Do NOT assume the company is Jio Financial Services.
Identify the actual company name, reporting period,
industry and business type from the document.

Your task is to create a structured financial analysis.

IMPORTANT:

1. Use ONLY information available in the uploaded PDF.
2. Do not invent financial numbers.
3. Do not assume missing information.
4. If a figure is not available, say "Not available".
5. Keep explanations professional but easy to understand.
6. Avoid unnecessary technical financial jargon.
7. Explain what important numbers mean in practical business terms.
8. Keep the analysis concise enough for a dashboard.
9. Do not return HTML.
10. Return ONLY valid JSON.

Return exactly this structure:

{
  "company_overview": {
    "company_name": "",
    "industry": "",
    "business_type": "",
    "reporting_period": "",
    "report_type": ""
  },

  "key_metrics": [
    {
      "metric": "",
      "current_period": "",
      "previous_period": "",
      "yoy_growth": "",
      "unit": "",
      "basis": ""
    }
  ],

  "business_performance": [
    {
      "title": "",
      "summary": "",
      "why_it_matters": ""
    }
  ],

  "management_commentary": [
    {
      "title": "",
      "summary": ""
    }
  ],

  "risks": [
    {
      "title": "",
      "what_is_the_risk": "",
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

For key_metrics:
Include the most important financial and operating metrics.
Prefer around 10 to 18 useful metrics rather than dozens.

For business_performance:
Give 5 to 8 major developments.

For management_commentary:
Give 4 to 6 important management points.

For risks:
Give 4 to 6 major risks.

For analyst_takeaway:
Use short, professional sentences.
The language should be understandable to a student or general investor.

Do NOT provide an investment recommendation such as
"Buy", "Sell", or "Hold".
Instead explain what an investor should monitor.
"""

        with st.spinner(
            "Gemini is analysing the financial report..."
        ):

            try:

                response = generate_with_fallback(
                    contents=[
                        analysis_prompt,
                        st.session_state.gemini_file
                    ],
                    json_mode=True
                )

                data = clean_json_response(
                    response.text
                )

                if not data:

                    st.error(
                        "Gemini returned an unexpected response. "
                        "Please try generating the analysis again."
                    )

                else:

                    st.session_state.analysis = data

                    st.success(
                        "Financial analysis generated successfully."
                    )

            except Exception as error:

                st.error(
                    f"Gemini could not complete the analysis: {error}"
                )


# ============================================================
# DASHBOARD DISPLAY
# ============================================================

data = st.session_state.analysis


if data:

    company = data.get(
        "company_overview",
        {}
    )

    metrics = data.get(
        "key_metrics",
        []
    )

    performance = data.get(
        "business_performance",
        []
    )

    management = data.get(
        "management_commentary",
        []
    )

    risks = data.get(
        "risks",
        []
    )

    takeaway = data.get(
        "analyst_takeaway",
        {}
    )


    # ========================================================
    # COMPANY OVERVIEW
    # ========================================================

    st.markdown(
        '<div class="section-title">Company Overview</div>',
        unsafe_allow_html=True
    )

    overview_columns = st.columns(5)

    overview_items = [
        (
            "Company",
            company.get(
                "company_name",
                "Not available"
            )
        ),
        (
            "Industry",
            company.get(
                "industry",
                "Not available"
            )
        ),
        (
            "Business Type",
            company.get(
                "business_type",
                "Not available"
            )
        ),
        (
            "Reporting Period",
            company.get(
                "reporting_period",
                "Not available"
            )
        ),
        (
            "Report Type",
            company.get(
                "report_type",
                "Not available"
            )
        )
    ]

    for column, item in zip(
        overview_columns,
        overview_items
    ):

        with column:

            st.markdown(
                f"""
                <div class="company-card">
                    <div class="company-label">
                        {item[0]}
                    </div>

                    <div class="company-value">
                        {item[1]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


    # ========================================================
    # KEY METRICS
    # ========================================================

    st.markdown(
        '<div class="section-title">Key Financial Metrics</div>',
        unsafe_allow_html=True
    )

    # Pick important headline metrics
    headline_metrics = []

    preferred_metric_words = [
        "total income",
        "revenue",
        "profit after tax",
        "pat",
        "net profit",
        "assets under management",
        "aum"
    ]

    for metric in metrics:

        name = str(
            metric.get("metric", "")
        ).lower()

        if any(
            word in name
            for word in preferred_metric_words
        ):

            if metric not in headline_metrics:
                headline_metrics.append(metric)

    # Keep headline cards manageable
    headline_metrics = headline_metrics[:4]

    if not headline_metrics:
        headline_metrics = metrics[:4]


    metric_columns = st.columns(
        len(headline_metrics)
        if headline_metrics
        else 1
    )

    for column, metric in zip(
        metric_columns,
        headline_metrics
    ):

        with column:

            metric_name = metric.get(
                "metric",
                "Metric"
            )

            value = metric.get(
                "current_period",
                "N/A"
            )

            unit = metric.get(
                "unit",
                ""
            )

            growth = metric.get(
                "yoy_growth",
                ""
            )

            basis = metric.get(
                "basis",
                ""
            )

            if growth and growth not in [
                "N/A",
                "Not applicable",
                "Not available"
            ]:

                delta = str(growth)

            else:

                delta = None


            st.metric(
                label=metric_name,
                value=f"{value} {unit}".strip(),
                delta=delta,
                border=True
            )

            if basis:

                st.caption(
                    f"Basis: {basis}"
                )


    # ========================================================
    # TABS
    # ========================================================

    overview_tab, metrics_tab, business_tab, management_tab, risks_tab, investor_tab = st.tabs(
        [
            "Overview",
            "Financial Metrics",
            "Business Performance",
            "Management",
            "Risks",
            "Investor View"
        ]
    )


    # ========================================================
    # OVERVIEW TAB
    # ========================================================

    with overview_tab:

        st.subheader("Financial Snapshot")

        st.write(
            "The dashboard below summarizes the most important "
            "financial and operating information found in the report."
        )

        if performance:

            for item in performance[:4]:

                title = item.get(
                    "title",
                    "Business Development"
                )

                summary = item.get(
                    "summary",
                    ""
                )

                why = item.get(
                    "why_it_matters",
                    ""
                )

                st.markdown(
                    f"""
                    <div class="insight-card">

                        <div class="insight-title">
                            {title}
                        </div>

                        <div class="insight-text">
                            {summary}
                        </div>

                        <br>

                        <div class="small-note">
                            Why it matters
                        </div>

                        <div class="insight-text">
                            {why}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


    # ========================================================
    # FINANCIAL METRICS TAB
    # ========================================================

    with metrics_tab:

        st.subheader(
            "Detailed Financial & Operating Metrics"
        )

        if metrics:

            table_rows = []

            for metric in metrics:

                table_rows.append(
                    {
                        "Metric": metric.get(
                            "metric",
                            ""
                        ),
                        "Current Period": metric.get(
                            "current_period",
                            ""
                        ),
                        "Previous Period": metric.get(
                            "previous_period",
                            ""
                        ),
                        "YoY Growth": metric.get(
                            "yoy_growth",
                            ""
                        ),
                        "Unit": metric.get(
                            "unit",
                            ""
                        ),
                        "Basis": metric.get(
                            "basis",
                            ""
                        )
                    }
                )

            st.dataframe(
                table_rows,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No detailed metrics were returned."
            )


    # ========================================================
    # BUSINESS PERFORMANCE TAB
    # ========================================================

    with business_tab:

        st.subheader(
            "Business Performance"
        )

        if performance:

            for index, item in enumerate(
                performance,
                start=1
            ):

                title = item.get(
                    "title",
                    f"Development {index}"
                )

                summary = item.get(
                    "summary",
                    ""
                )

                why = item.get(
                    "why_it_matters",
                    ""
                )

                with st.expander(
                    f"{index}. {title}",
                    expanded=index <= 2
                ):

                    st.write(summary)

                    if why:

                        st.markdown(
                            "**Why it matters:**"
                        )

                        st.write(why)


    # ========================================================
    # MANAGEMENT TAB
    # ========================================================

    with management_tab:

        st.subheader(
            "Management Commentary"
        )

        if management:

            for item in management:

                title = item.get(
                    "title",
                    "Management View"
                )

                summary = item.get(
                    "summary",
                    ""
                )

                with st.expander(
                    title,
                    expanded=False
                ):

                    st.write(summary)

        else:

            st.info(
                "No management commentary was identified."
            )


    # ========================================================
    # RISKS TAB
    # ========================================================

    with risks_tab:

        st.subheader(
            "Risk & Headwind Assessment"
        )

        if risks:

            for risk in risks:

                title = risk.get(
                    "title",
                    "Risk"
                )

                risk_description = risk.get(
                    "what_is_the_risk",
                    ""
                )

                why = risk.get(
                    "why_it_matters",
                    ""
                )

                st.markdown(
                    f"""
                    <div class="risk-card">

                        <div class="risk-title">
                            {title}
                        </div>

                        <div class="small-note">
                            What is the risk?
                        </div>

                        <div class="risk-text">
                            {risk_description}
                        </div>

                        <br>

                        <div class="small-note">
                            Why it matters
                        </div>

                        <div class="risk-text">
                            {why}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


    # ========================================================
    # INVESTOR VIEW TAB
    # ========================================================

    with investor_tab:

        st.subheader(
            "Analyst Takeaway"
        )

        improving = takeaway.get(
            "improving",
            []
        )

        weakening = takeaway.get(
            "weakening",
            []
        )

        growth_drivers = takeaway.get(
            "growth_drivers",
            []
        )

        investor_watch = takeaway.get(
            "investor_watch",
            []
        )


        col1, col2 = st.columns(2)


        with col1:

            st.markdown(
                "### What is improving?"
            )

            for item in improving:

                st.markdown(
                    f"""
                    <div class="watch-card">
                        {item}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


        with col2:

            st.markdown(
                "### What is weakening?"
            )

            for item in weakening:

                st.markdown(
                    f"""
                    <div class="watch-card">
                        {item}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


        st.markdown(
            "### Main Growth Drivers"
        )

        for item in growth_drivers:

            st.markdown(
                f"""
                <div class="watch-card">
                    {item}
                </div>
                """,
                unsafe_allow_html=True
            )


        st.markdown(
            "### What Should an Investor Watch?"
        )

        for item in investor_watch:

            st.markdown(
                f"""
                <div class="watch-card">
                    {item}
                </div>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# ASK QUESTIONS
# ============================================================

st.divider()

st.markdown(
    '<div class="section-title">Ask Questions About This Financial Report</div>',
    unsafe_allow_html=True
)

st.write(
    "Ask Gemini any question related to the uploaded financial report."
)

question = st.text_input(
    "Your question",
    placeholder=(
        "Example: What are the biggest risks to the company's "
        "future growth?"
    )
)


if st.button(
    "Ask Gemini",
    key="ask_question"
):

    if not question.strip():

        st.warning(
            "Please enter a question first."
        )

    else:

        question_prompt = f"""
You are a professional financial analyst.

Answer the user's question using ONLY the uploaded
financial report.

USER QUESTION:
{question}

IMPORTANT RULES:

1. Answer the actual question directly.
2. Use information from the uploaded PDF.
3. Do not invent facts or financial numbers.
4. If the report does not contain enough information,
   clearly say so.
5. Use simple, professional language.
6. Avoid unnecessary technical jargon.
7. If numbers are relevant, include them.
8. Explain why the numbers matter.
9. You may make reasonable financial interpretations
   based on the report, but clearly distinguish
   interpretation from facts.
10. If the user asks about future growth, explain the
    growth drivers and risks found in the report.
11. If the user asks about investment potential,
    provide an analytical view but DO NOT give a direct
    Buy, Sell, or Hold recommendation.
12. The answer should be easy for a general investor
    or finance student to understand.
13. Do not answer questions unrelated to the uploaded report.

Format the answer clearly using:

## Direct Answer

## Key Points

## What the Report Suggests

## What to Watch

Only use sections that are actually useful.
"""

        with st.spinner(
            "Gemini is analysing your question..."
        ):

            try:

                response = generate_with_fallback(
                    contents=[
                        question_prompt,
                        st.session_state.gemini_file
                    ],
                    json_mode=False
                )

                st.markdown(
                    "### Gemini's Answer"
                )

                st.write(
                    response.text
                )

            except Exception as error:

                st.error(
                    f"Gemini could not answer the question: {error}"
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Financial Analysis Copilot • "
    "AI-generated analysis based on the uploaded financial report. "
    "For educational and research purposes only."
)
