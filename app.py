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
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ---------- MAIN APP ---------- */

    .stApp {
        background: #0e1117;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }


    /* ---------- HERO ---------- */

    .hero {
        background: linear-gradient(
            135deg,
            #18202d 0%,
            #111722 100%
        );

        border: 1px solid #2d3748;
        border-radius: 18px;

        padding: 30px 34px;

        margin-bottom: 30px;
    }

    .hero-title {
        font-size: 40px;
        font-weight: 750;
        color: #ffffff;
        line-height: 1.15;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        font-size: 17px;
        color: #aeb8c7;
        line-height: 1.5;
    }


    /* ---------- SECTION HEADINGS ---------- */

    .section-title {
        font-size: 28px;
        font-weight: 700;
        color: #ffffff;
        margin-top: 30px;
        margin-bottom: 6px;
    }

    .section-description {
        color: #9ca7b6;
        font-size: 15px;
        margin-bottom: 20px;
    }


    /* ---------- COMPANY CARDS ---------- */

    .company-card {
        background: #151a24;
        border: 1px solid #2c3543;
        border-radius: 14px;

        padding: 18px;

        min-height: 115px;

        margin-bottom: 10px;
    }

    .company-label {
        color: #8f9aaa;
        font-size: 12px;

        text-transform: uppercase;
        letter-spacing: 0.7px;

        margin-bottom: 7px;
    }

    .company-value {
        color: #ffffff;
        font-size: 17px;
        font-weight: 600;
        line-height: 1.4;
    }


    /* ---------- INSIGHT CARDS ---------- */

    .insight-card {
        background: #151a24;
        border: 1px solid #2d3748;
        border-radius: 14px;

        padding: 20px;

        margin-bottom: 14px;
    }

    .insight-title {
        color: #ffffff;
        font-size: 17px;
        font-weight: 650;

        margin-bottom: 8px;
    }

    .insight-text {
        color: #b8c1ce;
        font-size: 15px;
        line-height: 1.65;
    }

    .why-label {
        color: #8f9aaa;
        font-size: 12px;

        text-transform: uppercase;
        letter-spacing: 0.5px;

        margin-top: 15px;
        margin-bottom: 5px;
    }


    /* ---------- RISK CARDS ---------- */

    .risk-card {
        background: #18171b;
        border: 1px solid #49383b;
        border-radius: 14px;

        padding: 20px;

        margin-bottom: 14px;
    }

    .risk-title {
        color: #ffffff;
        font-size: 17px;
        font-weight: 650;

        margin-bottom: 12px;
    }

    .risk-label {
        color: #a88f94;
        font-size: 12px;

        text-transform: uppercase;
        letter-spacing: 0.5px;

        margin-top: 10px;
        margin-bottom: 5px;
    }

    .risk-text {
        color: #c1c5cc;
        font-size: 15px;
        line-height: 1.6;
    }


    /* ---------- TAKEAWAY CARDS ---------- */

    .takeaway-card {
        background: #151a24;
        border: 1px solid #2d3748;
        border-radius: 14px;

        padding: 17px 18px;

        margin-bottom: 10px;

        color: #c3cbd6;
        line-height: 1.55;
        font-size: 14px;
    }


    /* ---------- SMALL TEXT ---------- */

    .small-note {
        color: #8f9aaa;
        font-size: 13px;
    }


    /* ---------- STATUS ---------- */

    .status-card {
        background: #131923;
        border: 1px solid #273244;
        border-radius: 12px;

        padding: 14px 18px;

        margin-top: 10px;
        margin-bottom: 20px;

        color: #aeb8c7;
        font-size: 14px;
    }


    /* ---------- ASK GEMINI ---------- */

    .question-box {
        background: #151a24;
        border: 1px solid #2d3748;
        border-radius: 16px;

        padding: 22px;

        margin-top: 10px;
        margin-bottom: 15px;
    }


    /* ---------- FOOTER ---------- */

    .footer {
        color: #707b8c;
        font-size: 12px;
        text-align: center;

        padding-top: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "gemini_file": None,
    "uploaded_name": None,
    "analysis": None,
    "selected_model": None,
    "chat_history": []
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


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

    return genai.Client(
        api_key=api_key
    )


client = create_client(API_KEY)


# ============================================================
# MODEL DISCOVERY
# ============================================================

def get_available_models():

    try:

        available = []

        for model in client.models.list():

            name = getattr(
                model,
                "name",
                ""
            )

            if not name:
                continue

            clean_name = name.replace(
                "models/",
                ""
            )

            supported_actions = getattr(
                model,
                "supported_actions",
                []
            ) or []

            # Only use models that can generate content
            if (
                "generateContent"
                in supported_actions
                and "gemini"
                in clean_name.lower()
            ):

                available.append(
                    clean_name
                )

        return available

    except Exception:

        return []


# ============================================================
# MODEL RANKING
# ============================================================

def model_score(model_name):

    name = model_name.lower()

    score = 0

    # Prefer Flash models because they are generally
    # faster and more suitable for this application.
    if "flash" in name:
        score += 100

    if "pro" in name:
        score += 40

    # Prefer newer-looking model generations.
    if "3.7" in name:
        score += 37

    elif "3.6" in name:
        score += 36

    elif "3.5" in name:
        score += 35

    elif "3.0" in name:
        score += 30

    elif "2.5" in name:
        score += 25

    elif "2.0" in name:
        score += 20

    return score


def get_ranked_models():

    models = get_available_models()

    if not models:
        return []

    # Remove duplicates
    models = list(
        dict.fromkeys(models)
    )

    # Rank the models
    models.sort(
        key=model_score,
        reverse=True
    )

    return models


# ============================================================
# GEMINI GENERATION WITH AUTOMATIC FALLBACK
# ============================================================

def generate_with_fallback(
    contents,
    json_mode=False
):

    available_models = get_ranked_models()

    selected = st.session_state.selected_model

    ordered_models = []

    # Try the previously successful model first
    if selected:

        if selected in available_models:

            ordered_models.append(
                selected
            )

    # Then try every currently available model
    for model in available_models:

        if model not in ordered_models:

            ordered_models.append(
                model
            )

    if not ordered_models:

        raise Exception(
            "No Gemini model available for this API key. "
            "Please check the Gemini API access and billing/quota settings."
        )

    errors = []

    for model in ordered_models:

        try:

            if json_mode:

                config = types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2
                )

                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config
                )

            else:

                config = types.GenerateContentConfig(
                    temperature=0.3
                )

                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config
                )

            # Save successful model
            st.session_state.selected_model = model

            return response

        except Exception as error:

            errors.append(
                f"{model}: {str(error)}"
            )

            continue


    error_text = "\n\n".join(
        errors[-5:]
    )

    raise Exception(
        "All currently available Gemini models failed.\n\n"
        + error_text
    )


# ============================================================
# SAFE JSON PARSER
# ============================================================

def clean_json_response(text):

    if not text:

        return {}

    text = text.strip()

    # Remove markdown fences
    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    text = text.strip()

    # Direct JSON
    try:

        return json.loads(text)

    except Exception:

        pass


    # Search for JSON object
    start = text.find("{")
    end = text.rfind("}")

    if (
        start != -1
        and end != -1
        and end > start
    ):

        candidate = text[
            start:end + 1
        ]

        try:

            return json.loads(
                candidate
            )

        except Exception:

            pass


    return {}


# ============================================================
# PDF UPLOAD TO GEMINI
# ============================================================

def upload_pdf_to_gemini(uploaded_file):

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:

            temp_file.write(
                uploaded_file.getbuffer()
            )

            temp_path = temp_file.name


        gemini_file = client.files.upload(
            file=temp_path
        )


        # Wait for Gemini to finish processing
        for _ in range(60):

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

            if state_name == "ACTIVE":

                return gemini_file


            if state_name == "FAILED":

                raise Exception(
                    "Gemini failed while processing the PDF."
                )


            time.sleep(1)

            gemini_file = client.files.get(
                name=gemini_file.name
            )


        raise Exception(
            "PDF processing took too long. "
            "Please try uploading the report again."
        )


    finally:

        if temp_path:

            try:
                os.remove(temp_path)

            except Exception:
                pass


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title(
        "Financial Analysis Copilot"
    )

    st.write(
        "Upload an annual report or financial PDF "
        "and let Gemini analyse it."
    )

    st.markdown("---")

    uploaded_file = st.file_uploader(
        "Upload Financial Report",
        type=["pdf"],
        help="Upload an annual report or financial statement PDF."
    )


    # --------------------------------------------------------
    # NEW FILE
    # --------------------------------------------------------

    if uploaded_file:

        is_new_file = (
            st.session_state.uploaded_name
            != uploaded_file.name
        )


        if is_new_file:

            with st.spinner(
                "Uploading financial report..."
            ):

                try:

                    gemini_file = upload_pdf_to_gemini(
                        uploaded_file
                    )

                    st.session_state.gemini_file = (
                        gemini_file
                    )

                    st.session_state.uploaded_name = (
                        uploaded_file.name
                    )

                    st.session_state.analysis = None

                    st.session_state.chat_history = []

                    st.session_state.selected_model = None

                    st.success(
                        "Financial report uploaded successfully."
                    )

                except Exception as error:

                    st.error(
                        f"Could not upload the PDF:\n\n{error}"
                    )

        else:

            st.success(
                "Financial report ready."
            )


    # --------------------------------------------------------
    # FILE STATUS
    # --------------------------------------------------------

    if st.session_state.gemini_file:

        st.markdown("---")

        st.caption(
            "Uploaded report"
        )

        st.write(
            st.session_state.uploaded_name
        )

        if st.session_state.selected_model:

            st.caption(
                f"Gemini model: {st.session_state.selected_model}"
            )


# ============================================================
# HERO
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
# NO PDF
# ============================================================

if not st.session_state.gemini_file:

    st.info(
        "Upload a financial report from the sidebar to begin."
    )

    st.stop()


# ============================================================
# GENERATE ANALYSIS SECTION
# ============================================================

st.markdown(
    '<div class="section-title">Generate Financial Analysis</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Gemini will read the uploaded report and create a '
    'structured financial dashboard.'
    '</div>',
    unsafe_allow_html=True
)


generate_button = st.button(
    "Generate Financial Analysis",
    type="primary",
    use_container_width=False
)


if generate_button:

    analysis_prompt = """

You are a professional financial analyst.

Analyze ONLY the uploaded financial report.

The PDF can belong to ANY company.

First identify the actual:
- Company name
- Industry / sector
- Business type
- Reporting period
- Report type

Do NOT assume the company is Jio Financial Services,
Reliance, HDFC, SBI, or any other company.

============================================================
IMPORTANT ANALYSIS RULES
============================================================

1. Use ONLY information found in the uploaded PDF.

2. Never invent financial numbers.

3. Never create numbers that are not present in the report.

4. If information is unavailable, write:
   "Not available in the report."

5. Keep the language professional but simple.

6. Avoid unnecessary financial jargon.

7. Explain important numbers in practical business language.

8. Focus on useful information rather than copying the report.

9. Do not reproduce large portions of the annual report.

10. Do not give a Buy, Sell or Hold recommendation.

11. For investor-related information, explain what an investor
    should understand or monitor.

12. The analysis should work for ANY company.

============================================================
KEY METRICS
============================================================

Select approximately 10–18 of the most useful financial
and operating metrics.

Where available, include:

- Revenue / total income
- Operating income
- Profit
- PAT
- EBITDA / operating profit
- EPS
- Assets
- Net worth
- Debt
- Cash
- AUM
- Loan book
- Customer growth
- Operating expenses
- Cash flow
- Margins
- ROE
- ROA
- Other important company-specific metrics

Only include metrics that are actually relevant to the company.

============================================================
BUSINESS PERFORMANCE
============================================================

Identify 5–8 major developments.

For each development explain:

- What happened
- Why it matters

Use short explanations.

============================================================
MANAGEMENT
============================================================

Identify 4–6 important management comments or strategic themes.

Focus on:

- Future plans
- Strategy
- Growth
- Capital allocation
- New businesses
- Technology
- Market expansion
- Management outlook

============================================================
RISKS
============================================================

Identify 4–6 important risks.

For every risk explain:

- What is the risk?
- Why does it matter?

Keep the explanation simple.

============================================================
ANALYST TAKEAWAY
============================================================

Create four sections:

1. What is improving?
2. What is weakening?
3. Main growth drivers
4. What should an investor watch?

Each point should be short and useful.

============================================================
OUTPUT FORMAT
============================================================

Return ONLY valid JSON.

Do NOT return:

- HTML
- Markdown
- Code fences
- Tables
- Explanations outside the JSON

Use exactly this structure:

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

Remember:

The final answer must be valid JSON only.
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
                    "Gemini returned an invalid analysis. "
                    "Please click 'Generate Financial Analysis' again."
                )

            else:

                st.session_state.analysis = data

                st.success(
                    "Financial analysis generated successfully."
                )

                # Rerun so the dashboard appears immediately
                st.rerun()


        except Exception as error:

            st.error(
                "Gemini could not complete the analysis."
            )

            st.code(
                str(error)
            )


# ============================================================
# GET ANALYSIS
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

    st.markdown(
        '<div class="section-description">'
        'A quick snapshot of the company and the report analysed.'
        '</div>',
        unsafe_allow_html=True
    )


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


    overview_columns = st.columns(5)


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
    # KEY FINANCIAL METRICS
    # ========================================================

    st.markdown(
        '<div class="section-title">Key Financial Metrics</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'The most important numbers extracted from the report.'
        '</div>',
        unsafe_allow_html=True
    )


    # Find headline metrics
    headline_metrics = []

    priority_words = [
        "total income",
        "revenue",
        "profit after tax",
        "pat",
        "net profit",
        "ebitda",
        "assets under management",
        "aum"
    ]


    for metric in metrics:

        metric_name = str(
            metric.get(
                "metric",
                ""
            )
        ).lower()


        if any(
            word in metric_name
            for word in priority_words
        ):

            if metric not in headline_metrics:

                headline_metrics.append(
                    metric
                )


    # Add other metrics if needed
    for metric in metrics:

        if metric not in headline_metrics:

            headline_metrics.append(
                metric
            )


    headline_metrics = headline_metrics[:4]


    if headline_metrics:

        metric_columns = st.columns(
            len(headline_metrics)
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

                current = metric.get(
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


                value_text = (
                    f"{current} {unit}"
                ).strip()


                valid_growth = (
                    growth
                    and str(growth).lower()
                    not in [
                        "n/a",
                        "not available",
                        "not applicable"
                    ]
                )


                if valid_growth:

                    st.metric(
                        label=metric_name,
                        value=value_text,
                        delta=str(growth),
                        border=True
                    )

                else:

                    st.metric(
                        label=metric_name,
                        value=value_text,
                        border=True
                    )


                if basis:

                    st.caption(
                        f"Basis: {basis}"
                    )


    # ========================================================
    # MAIN DASHBOARD TABS
    # ========================================================

    tabs = st.tabs(
        [
            "Overview",
            "Financial Metrics",
            "Business Performance",
            "Management",
            "Risks",
            "Investor View"
        ]
    )


    overview_tab = tabs[0]
    metrics_tab = tabs[1]
    business_tab = tabs[2]
    management_tab = tabs[3]
    risks_tab = tabs[4]
    investor_tab = tabs[5]


    # ========================================================
    # OVERVIEW
    # ========================================================

    with overview_tab:

        st.subheader(
            "Financial Snapshot"
        )

        st.write(
            "Here are the main developments that stand out "
            "from the financial report."
        )


        if performance:

            for item in performance[:5]:

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

                        <div class="why-label">
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
    # FINANCIAL METRICS
    # ========================================================

    with metrics_tab:

        st.subheader(
            "Detailed Financial & Operating Metrics"
        )

        st.write(
            "Compare the current period with the previous "
            "period using the figures available in the report."
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
                hide_index=True,
                height=560
            )

        else:

            st.info(
                "No detailed financial metrics were found."
            )


    # ========================================================
    # BUSINESS PERFORMANCE
    # ========================================================

    with business_tab:

        st.subheader(
            "Business Performance"
        )

        st.write(
            "Major business developments identified in the report."
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

                    st.write(
                        summary
                    )

                    if why:

                        st.markdown(
                            "**Why it matters**"
                        )

                        st.write(
                            why
                        )


    # ========================================================
    # MANAGEMENT
    # ========================================================

    with management_tab:

        st.subheader(
            "Management Commentary"
        )

        st.write(
            "Important strategic and management themes "
            "identified in the annual report."
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

                    st.write(
                        summary
                    )

        else:

            st.info(
                "No management commentary was identified."
            )


    # ========================================================
    # RISKS
    # ========================================================

    with risks_tab:

        st.subheader(
            "Risk & Headwind Assessment"
        )

        st.write(
            "Key risks identified from the company's "
            "financial and business information."
        )


        if risks:

            for risk in risks:

                title = risk.get(
                    "title",
                    "Risk"
                )

                description = risk.get(
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

                        <div class="risk-label">
                            What is the risk?
                        </div>

                        <div class="risk-text">
                            {description}
                        </div>

                        <div class="risk-label">
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
    # INVESTOR VIEW
    # ========================================================

    with investor_tab:

        st.subheader(
            "Analyst Takeaway"
        )

        st.write(
            "A simplified view of what is improving, "
            "what is weakening and what deserves attention."
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


        # ----------------------------------------------------
        # IMPROVING
        # ----------------------------------------------------

        with col1:

            st.markdown(
                "### What is improving?"
            )

            if improving:

                for item in improving:

                    st.markdown(
                        f"""
                        <div class="takeaway-card">
                            {item}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            else:

                st.info(
                    "No specific improvement points identified."
                )


        # ----------------------------------------------------
        # WEAKENING
        # ----------------------------------------------------

        with col2:

            st.markdown(
                "### What is weakening?"
            )

            if weakening:

                for item in weakening:

                    st.markdown(
                        f"""
                        <div class="takeaway-card">
                            {item}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            else:

                st.info(
                    "No specific weakening points identified."
                )


        # ----------------------------------------------------
        # GROWTH DRIVERS
        # ----------------------------------------------------

        st.markdown(
            "### Main Growth Drivers"
        )


        if growth_drivers:

            for item in growth_drivers:

                st.markdown(
                    f"""
                    <div class="takeaway-card">
                        {item}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


        # ----------------------------------------------------
        # INVESTOR WATCH
        # ----------------------------------------------------

        st.markdown(
            "### What Should an Investor Watch?"
        )


        if investor_watch:

            for item in investor_watch:

                st.markdown(
                    f"""
                    <div class="takeaway-card">
                        {item}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


# ============================================================
# ASK QUESTIONS ABOUT THE REPORT
# ============================================================

st.divider()


st.markdown(
    '<div class="section-title">Ask Questions About This Financial Report</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Ask Gemini any reasonable question about the uploaded report. '
    'You are not limited to a fixed list of questions.'
    '</div>',
    unsafe_allow_html=True
)


question = st.text_area(
    "Your question",
    placeholder=(
        "Examples:\n"
        "• What are the biggest risks to the company's future growth?\n"
        "• Why did profit change compared with last year?\n"
        "• What are the main growth drivers?\n"
        "• Is the company's financial position improving?\n"
        "• What should a long-term investor monitor?"
    ),
    height=120
)


ask_button = st.button(
    "Ask Gemini",
    type="primary",
    key="ask_question"
)


if ask_button:

    if not question.strip():

        st.warning(
            "Please enter a question first."
        )

    else:

        question_prompt = f"""

You are a professional financial analyst.

The user has uploaded a financial report.

Answer the user's question using ONLY information
contained in that uploaded report.

USER QUESTION:
{question}

============================================================
ANSWER RULES
============================================================

1. Answer the user's actual question directly.

2. Use only information from the uploaded PDF.

3. Never invent financial figures.

4. If the PDF does not contain enough information,
   clearly say that the report does not provide enough
   information to answer that part.

5. Use simple, professional language.

6. Avoid unnecessary technical jargon.

7. If financial numbers are useful, include them.

8. Explain what important numbers mean in simple terms.

9. You may make reasonable interpretations based on
   the information in the report.

10. Clearly separate facts from interpretation.

11. If the user asks about future growth:
    explain the company's growth drivers, opportunities
    and risks found in the report.

12. If the user asks whether the company is financially
    strong:
    discuss revenue, profit, assets, debt, cash flow,
    margins and other relevant metrics available in
    the report.

13. If the user asks about investment potential:
    provide an analytical assessment based on the report,
    but DO NOT give a direct Buy, Sell or Hold recommendation.

14. If the question is unrelated to the uploaded report,
    politely explain that you can answer questions related
    to the uploaded financial report.

15. Do not pretend to know information that is not in
    the uploaded report.

============================================================
RESPONSE STYLE
============================================================

Make the answer visually easy to read.

Do NOT write one huge paragraph.

Use:

### Direct Answer

Then give the main answer in 2–4 short paragraphs.

Then, when useful:

### Key Points

- Point
- Point
- Point

Then, when useful:

### What This Means

Explain the practical meaning.

Then, when useful:

### What to Watch

- Point
- Point

Use only the sections that are useful.

Keep the answer concise but informative.

Do not return HTML.

Return normal Markdown.
"""


        with st.spinner(
            "Gemini is analysing the report and preparing your answer..."
        ):

            try:

                response = generate_with_fallback(
                    contents=[
                        question_prompt,
                        st.session_state.gemini_file
                    ],
                    json_mode=False
                )


                answer = response.text.strip()


                st.markdown(
                    "### Gemini's Answer"
                )


                if answer:

                    st.markdown(
                        answer
                    )

                else:

                    st.warning(
                        "Gemini returned an empty answer. "
                        "Please try asking the question again."
                    )


            except Exception as error:

                st.error(
                    "Gemini could not answer the question."
                )

                st.code(
                    str(error)
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div class="footer">
        Financial Analysis Copilot •
        AI-generated analysis based on the uploaded financial report.
        For educational and research purposes only.
    </div>
    """,
    unsafe_allow_html=True
)
