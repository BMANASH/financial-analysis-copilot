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

st.markdown("""
<style>
.stApp {
    background: #0e1117;
}
.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}
.hero {
    background: linear-gradient(135deg, #18202d 0%, #111722 100%);
    border: 1px solid #2d3748;
    border-radius: 18px;
    padding: 30px 34px;
    margin-bottom: 25px;
}
.hero-title {
    font-size: 38px;
    font-weight: 750;
    color: #ffffff;
    line-height: 1.15;
    margin-bottom: 8px;
}
.hero-subtitle {
    font-size: 16px;
    color: #aeb8c7;
    line-height: 1.5;
}
.section-title {
    font-size: 24px;
    font-weight: 700;
    color: #ffffff;
    margin-top: 25px;
    margin-bottom: 4px;
}
.section-description {
    color: #9ca7b6;
    font-size: 14px;
    margin-bottom: 18px;
}
.company-card {
    background: #151a24;
    border: 1px solid #2c3543;
    border-radius: 14px;
    padding: 16px;
    min-height: 110px;
    margin-bottom: 10px;
}
.company-label {
    color: #8f9aaa;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.7px;
    margin-bottom: 6px;
}
.company-value {
    color: #ffffff;
    font-size: 15px;
    font-weight: 600;
    line-height: 1.4;
}
.kpi-card {
    background: #151a24;
    border: 1px solid #283241;
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 10px;
    min-height: 145px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.kpi-label {
    color: #8f9aaa;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.kpi-value {
    color: #ffffff;
    font-size: 26px;
    font-weight: 750;
    margin-top: 4px;
    margin-bottom: 6px;
}
.kpi-badge-pos {
    display: inline-block;
    background: rgba(16, 185, 129, 0.15);
    color: #34d399;
    font-size: 12px;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 6px;
    border: 1px solid rgba(16, 185, 129, 0.3);
}
.kpi-badge-neg {
    display: inline-block;
    background: rgba(239, 68, 68, 0.15);
    color: #f87171;
    font-size: 12px;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 6px;
    border: 1px solid rgba(239, 68, 68, 0.3);
}
.kpi-badge-neutral {
    display: inline-block;
    background: rgba(156, 163, 175, 0.15);
    color: #9ca3af;
    font-size: 12px;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 6px;
    border: 1px solid rgba(156, 163, 175, 0.3);
}
.kpi-basis {
    color: #6c7889;
    font-size: 11px;
    margin-top: 6px;
}
.insight-card {
    background: #151a24;
    border: 1px solid #2d3748;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 14px;
}
.insight-title {
    color: #ffffff;
    font-size: 16px;
    font-weight: 650;
    margin-bottom: 8px;
}
.insight-text {
    color: #b8c1ce;
    font-size: 14px;
    line-height: 1.6;
}
.why-box {
    background: #10141d;
    border-left: 3px solid #3b82f6;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    margin-top: 12px;
}
.why-title {
    color: #60a5fa;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    font-weight: 700;
    margin-bottom: 4px;
}
.why-content {
    color: #cbd5e1;
    font-size: 13.5px;
    line-height: 1.5;
}
.risk-card {
    background: #19161a;
    border: 1px solid #483438;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 14px;
}
.risk-title {
    color: #fca5a5;
    font-size: 16px;
    font-weight: 650;
    margin-bottom: 10px;
}
.risk-box {
    background: #141113;
    border-left: 3px solid #ef4444;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    margin-top: 10px;
}
.takeaway-improving {
    background: #121d19;
    border: 1px solid #1e3a2f;
    border-left: 4px solid #10b981;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
    color: #d1fae5;
    font-size: 14px;
    line-height: 1.5;
}
.takeaway-weakening {
    background: #201417;
    border: 1px solid #451e24;
    border-left: 4px solid #ef4444;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
    color: #fee2e2;
    font-size: 14px;
    line-height: 1.5;
}
.takeaway-driver {
    background: #131b26;
    border: 1px solid #23354d;
    border-left: 4px solid #3b82f6;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
    color: #dbeafe;
    font-size: 14px;
    line-height: 1.5;
}
.takeaway-watch {
    background: #1c1a14;
    border: 1px solid #3d351e;
    border-left: 4px solid #f59e0b;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
    color: #fef3c7;
    font-size: 14px;
    line-height: 1.5;
}
.deep-card {
    background: #161c28;
    border: 1px solid #2e3d54;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 14px;
}
.deep-card-title {
    color: #60a5fa;
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 8px;
}
.footer {
    color: #707b8c;
    font-size: 12px;
    text-align: center;
    padding-top: 25px;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "gemini_file": None,
    "uploaded_name": None,
    "analysis": None,
    "deep_dive": None,
    "selected_model": None,
    "chat_history": []
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ============================================================
# API KEY & CLIENT
# ============================================================

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    API_KEY = None

if not API_KEY:
    st.error("Gemini API key was not found. Please add GEMINI_API_KEY to Streamlit Secrets.")
    st.stop()

@st.cache_resource
def create_client(api_key):
    return genai.Client(api_key=api_key)

client = create_client(API_KEY)

# ============================================================
# DYNAMIC MODEL DISCOVERY & SMART RANKING
# ============================================================

def get_available_models():
    try:
        available = []
        for model in client.models.list():
            name = getattr(model, "name", "")
            if not name:
                continue
            clean_name = name.replace("models/", "")
            supported_actions = getattr(model, "supported_actions", []) or []
            if "generateContent" in supported_actions and "gemini" in clean_name.lower():
                available.append(clean_name)
        return available
    except Exception:
        return []

def model_score(model_name):
    name = model_name.lower()
    score = 0
    if "flash" in name and "lite" not in name:
        score += 150
    elif "pro" in name:
        score += 100
    elif "flash-lite" in name or "lite" in name:
        score += 50
    
    if "latest" in name:
        score += 30
    return score

def get_ranked_models():
    live_models = get_available_models()
    candidate_pool = ["gemini-flash-latest", "gemini-pro-latest"] + live_models
    unique_models = list(dict.fromkeys(candidate_pool))
    unique_models.sort(key=model_score, reverse=True)
    return unique_models

def generate_with_fallback(contents, json_mode=False):
    available_models = get_ranked_models()
    selected = st.session_state.selected_model

    ordered_models = []
    if selected and selected in available_models:
        ordered_models.append(selected)

    for m in available_models:
        if m not in ordered_models:
            ordered_models.append(m)

    errors = []
    for model in ordered_models:
        try:
            if json_mode:
                config = types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                    max_output_tokens=8192
                )
            else:
                config = types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=8192
                )

            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config
            )

            st.session_state.selected_model = model
            return response

        except Exception as error:
            errors.append(f"{model}: {str(error)}")
            continue

    error_text = "\n\n".join(errors)
    raise Exception(f"All available models failed.\n\n{error_text}")

# ============================================================
# SAFE JSON PARSER
# ============================================================

def clean_json_response(text):
    if not text:
        return {}
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()

    try:
        return json.loads(text)
    except Exception:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start:end + 1]
        try:
            return json.loads(candidate)
        except Exception:
            pass

    return {}

# ============================================================
# PDF UPLOAD TO GEMINI
# ============================================================

def upload_pdf_to_gemini(uploaded_file):
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(uploaded_file.getbuffer())
            temp_path = temp_file.name

        gemini_file = client.files.upload(file=temp_path)

        for _ in range(60):
            state = getattr(gemini_file, "state", None)
            state_name = getattr(state, "name", "")

            if state_name == "ACTIVE":
                return gemini_file

            if state_name == "FAILED":
                raise Exception("Gemini failed while processing the PDF.")

            time.sleep(1)
            gemini_file = client.files.get(name=gemini_file.name)

        raise Exception("PDF processing took too long. Please try uploading again.")
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
    st.title("Financial Analysis Copilot")
    st.write("Upload an annual report or financial PDF and let Gemini analyse it.")
    st.markdown("---")

    uploaded_file = st.file_uploader(
        "Upload Financial Report",
        type=["pdf"],
        help="Upload an annual report or financial statement PDF."
    )

    if uploaded_file:
        is_new_file = (st.session_state.uploaded_name != uploaded_file.name)

        if is_new_file:
            with st.spinner("Uploading and processing PDF..."):
                try:
                    gemini_file = upload_pdf_to_gemini(uploaded_file)
                    st.session_state.gemini_file = gemini_file
                    st.session_state.uploaded_name = uploaded_file.name
                    st.session_state.analysis = None
                    st.session_state.deep_dive = None
                    st.session_state.chat_history = []
                    st.session_state.selected_model = None
                    st.success("Financial report ready for analysis.")
                except Exception as error:
                    st.error(f"Could not process PDF:\n\n{error}")
        else:
            st.success("Financial report active.")

    if st.session_state.gemini_file:
        st.markdown("---")
        st.caption("Active Document:")
        st.write(f"📄 **{st.session_state.uploaded_name}**")
        if st.session_state.selected_model:
            st.caption(f"Engine: `{st.session_state.selected_model}`")

# ============================================================
# HERO SECTION
# ============================================================

st.markdown("""
<div class="hero">
    <div class="hero-title">Financial Analysis Copilot</div>
    <div class="hero-subtitle">AI-powered financial analysis from annual reports</div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# NO PDF STATE
# ============================================================

if not st.session_state.gemini_file:
    st.info("Upload a financial report from the sidebar to begin.")
    st.stop()

# ============================================================
# GENERATE ANALYSIS SECTION
# ============================================================

st.markdown('<div class="section-title">Generate Financial Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="section-description">Gemini will read the uploaded report and create a complete, easy-to-understand financial dashboard.</div>', unsafe_allow_html=True)

generate_button = st.button("Generate Financial Analysis", type="primary")

if generate_button:
    analysis_prompt = """
You are an expert financial analyst who explains financial annual reports to regular investors and finance students in simple, everyday English without losing depth or numbers.

Analyze ONLY the uploaded PDF. It can belong to ANY company.
Identify the company name, industry, reporting period, report type, and provide a clear 2-sentence description of what the business does.

============================================================
STRICT CONTENT DEPTH & COUNT REQUIREMENTS
============================================================
1. KEY_METRICS: Extract exactly 12 to 18 of the most relevant financial, revenue, margin, loan, asset, and profit metrics found in the report. Keep the metric name clean and concise.
2. BUSINESS_PERFORMANCE: Provide exactly 5 to 7 major developments. For each, give a clear 2-sentence summary and a 1-sentence explanation of why it matters.
3. MANAGEMENT_COMMENTARY: Provide exactly 4 to 6 strategic management themes or plans.
4. RISKS: Provide exactly 5 to 6 distinct risk factors. Explain the risk clearly and explain what it means for an investor in everyday terms.
5. ANALYST_TAKEAWAY:
   - "improving": exactly 4 to 6 clear positive points with specific numbers/facts.
   - "weakening": exactly 4 to 6 challenges, drops, or concerns with specific numbers/facts.
   - "growth_drivers": exactly 4 to 6 key factors that could drive future revenue.
   - "investor_watch": exactly 4 to 6 specific checkpoints an investor should track next.

============================================================
LANGUAGE STYLE RULES
============================================================
- Write in clean, professional, plain English.
- Avoid academic, textbook jargon (e.g. explain what treasury volatility, credit provisioning, or margin compression actually means in real-world terms).
- Always anchor findings with exact numbers, percentages, and growth figures from the document.
- Never invent figures. Do NOT give Buy/Sell/Hold advice.

============================================================
OUTPUT FORMAT (JSON ONLY)
============================================================
Return ONLY valid JSON with this exact structure:
{
  "company_overview": {
    "company_name": "",
    "industry": "",
    "business_type": "2 clear sentences on what the company actually does and how it earns revenue",
    "reporting_period": "",
    "report_type": ""
  },
  "key_metrics": [
    {
      "metric": "Clean name e.g. Total Revenue, Net Profit (PAT), Total Loan Book",
      "current_period": "",
      "previous_period": "",
      "yoy_growth": "",
      "unit": "",
      "basis": ""
    }
  ],
  "business_performance": [
    {
      "title": "Clear development title",
      "summary": "2 simple sentences on what happened with exact numbers",
      "why_it_matters": "1 sentence on why this matters to the business"
    }
  ],
  "management_commentary": [
    {
      "title": "Strategy or Theme Title",
      "summary": "What leadership is doing or planning in clear plain English"
    }
  ],
  "risks": [
    {
      "title": "Risk Name",
      "what_is_the_risk": "Clear explanation of the danger or challenge",
      "why_it_matters": "Plain-English explanation of how this affects business earnings"
    }
  ],
  "analyst_takeaway": {
    "improving": ["4 to 6 bullet points"],
    "weakening": ["4 to 6 bullet points"],
    "growth_drivers": ["4 to 6 bullet points"],
    "investor_watch": ["4 to 6 bullet points"]
  }
}
"""

    with st.spinner("Gemini is reading the complete report and generating full detailed analysis..."):
        try:
            response = generate_with_fallback(
                contents=[analysis_prompt, st.session_state.gemini_file],
                json_mode=True
            )
            data = clean_json_response(response.text)

            if not data or "company_overview" not in data:
                st.error("Gemini returned an incomplete response. Please click 'Generate Financial Analysis' again.")
            else:
                st.session_state.analysis = data
                st.session_state.deep_dive = None
                st.success("Financial analysis generated successfully.")
                st.rerun()

        except Exception as error:
            st.error("Gemini could not complete the analysis.")
            st.code(str(error))

# ============================================================
# DISPLAY ANALYSIS DASHBOARD
# ============================================================

data = st.session_state.analysis

if data:
    company = data.get("company_overview", {})
    metrics = data.get("key_metrics", [])
    performance = data.get("business_performance", [])
    management = data.get("management_commentary", [])
    risks = data.get("risks", [])
    takeaway = data.get("analyst_takeaway", {})

    # Company Overview
    st.markdown('<div class="section-title">Company Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-description">A quick snapshot of the company and what it does.</div>', unsafe_allow_html=True)

    overview_items = [
        ("Company", company.get("company_name", "Not available")),
        ("Industry", company.get("industry", "Not available")),
        ("What They Do", company.get("business_type", "Not available")),
        ("Reporting Period", company.get("reporting_period", "Not available")),
        ("Report Type", company.get("report_type", "Not available"))
    ]

    overview_columns = st.columns([1.2, 1.2, 2.2, 1, 1])
    for column, item in zip(overview_columns, overview_items):
        with column:
            column_html = f"""<div class="company-card"><div class="company-label">{item[0]}</div><div class="company-value">{item[1]}</div></div>"""
            st.markdown(column_html, unsafe_allow_html=True)

    # Key Financial Metrics Cards
    st.markdown('<div class="section-title">Key Financial Metrics</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-description">The main headline numbers extracted from the financial report.</div>', unsafe_allow_html=True)

    headline_metrics = []
    priority_words = ["total income", "revenue", "profit after tax", "pat", "net profit", "ebitda", "assets under management", "aum", "total client"]

    for metric in metrics:
        metric_name = str(metric.get("metric", "")).lower()
        if any(word in metric_name for word in priority_words):
            if metric not in headline_metrics:
                headline_metrics.append(metric)

    for metric in metrics:
        if metric not in headline_metrics:
            headline_metrics.append(metric)

    headline_metrics = headline_metrics[:4]

    if headline_metrics:
        metric_columns = st.columns(len(headline_metrics))
        for column, metric in zip(metric_columns, headline_metrics):
            with column:
                m_name = metric.get("metric", "Metric")
                current = metric.get("current_period", "N/A")
                unit = metric.get("unit", "")
                growth = str(metric.get("yoy_growth", "")).strip()
                basis = metric.get("basis", "")
                value_display = f"{current} {unit}".strip()

                badge_html = ""
                if growth and growth.lower() not in ["n/a", "not available", "not applicable", ""]:
                    if growth.startswith("-") or "decline" in growth.lower():
                        badge_html = f"""<div class="kpi-badge-neg">▼ {growth}</div>"""
                    elif growth.startswith("+") or not growth.startswith("-"):
                        clean_growth = growth if growth.startswith("+") else f"+{growth}"
                        badge_html = f"""<div class="kpi-badge-pos">▲ {clean_growth} YoY</div>"""
                else:
                    badge_html = """<div class="kpi-badge-neutral">Current Level</div>"""

                basis_html = f"""<div class="kpi-basis">Basis: {basis}</div>""" if basis else ""

                kpi_card_html = f"""
                <div class="kpi-card">
                    <div>
                        <div class="kpi-label">{m_name}</div>
                        <div class="kpi-value">{value_display}</div>
                        {badge_html}
                    </div>
                    {basis_html}
                </div>
                """
                st.markdown(kpi_card_html, unsafe_allow_html=True)

    # Tabs
    tab_overview, tab_metrics, tab_business, tab_mgmt, tab_risks, tab_investor = st.tabs([
        "Overview", "Financial Metrics Table", "Business Updates", "Management Plans", "Risks (Plain English)", "Investor Takeaway"
    ])

    with tab_overview:
        st.subheader("Financial Snapshot")
        st.write("The main business developments from this report:")
        if performance:
            for item in performance:
                title = item.get("title", "Business Development")
                summary = item.get("summary", "")
                why = item.get("why_it_matters", "")

                card_html = f"""
                <div class="insight-card">
                    <div class="insight-title">{title}</div>
                    <div class="insight-text">{summary}</div>
                    <div class="why-box">
                        <div class="why-title">Why it matters</div>
                        <div class="why-content">{why}</div>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)

    with tab_metrics:
        st.subheader("All Financial & Operating Numbers")
        st.write("Search and filter the numbers reported in the financial statements:")

        if metrics:
            col_search, col_filter = st.columns([2, 1])
            with col_search:
                search_query = st.text_input("🔍 Search line item...", placeholder="e.g. Revenue, Profit, Loan, Expenses", key="metric_search").lower()
            with col_filter:
                all_bases = list(set([m.get("basis", "").strip() for m in metrics if m.get("basis", "").strip()]))
                basis_filter = st.selectbox("Filter by Basis", options=["All"] + all_bases, key="basis_filter")

            filtered_rows = []
            for m in metrics:
                metric_name = m.get("metric", "")
                basis_val = m.get("basis", "")

                match_search = (not search_query) or (search_query in metric_name.lower())
                match_basis = (basis_filter == "All") or (basis_val.lower() == basis_filter.lower())

                if match_search and match_basis:
                    filtered_rows.append({
                        "Metric Name": metric_name,
                        "Current Period": m.get("current_period", ""),
                        "Previous Period": m.get("previous_period", ""),
                        "YoY Growth": m.get("yoy_growth", ""),
                        "Unit": m.get("unit", ""),
                        "Basis": basis_val
                    })

            if filtered_rows:
                st.dataframe(filtered_rows, use_container_width=True, hide_index=True, height=450)
            else:
                st.info("No metrics matching your search.")
        else:
            st.info("No financial metrics found.")

    with tab_business:
        st.subheader("Business Updates")
        st.write("How different parts of the business performed:")
        if performance:
            for idx, item in enumerate(performance, start=1):
                title = item.get("title", f"Update {idx}")
                summary = item.get("summary", "")
                why = item.get("why_it_matters", "")

                with st.expander(f"{idx}. {title}", expanded=(idx <= 2)):
                    st.write(summary)
                    if why:
                        st.markdown(f"""
                        <div class="why-box">
                            <div class="why-title">Why it matters</div>
                            <div class="why-content">{why}</div>
                        </div>
                        """, unsafe_allow_html=True)

    with tab_mgmt:
        st.subheader("Management Strategy & Outlook")
        st.write("What company leadership says about future plans and technology:")
        if management:
            for item in management:
                title = item.get("title", "Management View")
                summary = item.get("summary", "")
                with st.expander(title, expanded=False):
                    st.write(summary)
        else:
            st.info("No management commentary identified.")

    with tab_risks:
        st.subheader("Potential Risks & Challenges")
        st.write("Key risks explained in plain English:")
        if risks:
            for r in risks:
                title = r.get("title", "Risk")
                desc = r.get("what_is_the_risk", "")
                why = r.get("why_it_matters", "")

                risk_html = f"""
                <div class="risk-card">
                    <div class="risk-title">⚠️ {title}</div>
                    <div class="insight-text">{desc}</div>
                    <div class="risk-box">
                        <div style="color: #f87171; font-size: 11px; text-transform: uppercase; font-weight: 700; margin-bottom: 4px;">What this means for investors</div>
                        <div class="why-content">{why}</div>
                    </div>
                </div>
                """
                st.markdown(risk_html, unsafe_allow_html=True)

    with tab_investor:
        st.subheader("Analyst Takeaway")
        st.write("Simplified summary for investors and analysts:")

        improving = takeaway.get("improving", [])
        weakening = takeaway.get("weakening", [])
        growth_drivers = takeaway.get("growth_drivers", [])
        investor_watch = takeaway.get("investor_watch", [])

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🟢 What is improving?")
            if improving:
                for item in improving:
                    card_html = f"""<div class="takeaway-improving">✓ {item}</div>"""
                    st.markdown(card_html, unsafe_allow_html=True)
            else:
                st.info("No specific improvement points identified.")

        with col2:
            st.markdown("### 🔴 What is weakening?")
            if weakening:
                for item in weakening:
                    card_html = f"""<div class="takeaway-weakening">✗ {item}</div>"""
                    st.markdown(card_html, unsafe_allow_html=True)
            else:
                st.info("No specific weakening points identified.")

        st.markdown("### 🚀 Main Growth Drivers")
        if growth_drivers:
            for item in growth_drivers:
                card_html = f"""<div class="takeaway-driver">◆ {item}</div>"""
                st.markdown(card_html, unsafe_allow_html=True)

        st.markdown("### 🔍 What Should an Investor Watch?")
        if investor_watch:
            for item in investor_watch:
                card_html = f"""<div class="takeaway-watch">◉ {item}</div>"""
                st.markdown(card_html, unsafe_allow_html=True)

    # ========================================================
    # STEP 21: MCQ-TYPE DEEP-DIVE SELECTION
    # ========================================================
    st.markdown("---")
    st.markdown('<div class="section-title">🔬 Deep-Dive Financial Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-description">Would you like to view an in-depth financial investigation covering profitability margins, debt & balance sheet safety, and operating efficiency?</div>', unsafe_allow_html=True)

    mcq_choice = st.radio(
        "Select the given option:",
        options=["Yes", "No"],
        index=None,
        horizontal=True,
        key="deep_dive_mcq"
    )

    if mcq_choice == "Yes":
        if st.session_state.deep_dive is None:
            deep_prompt = """
You are a senior financial analyst providing a specialized deep-dive assessment of the uploaded annual report in plain, everyday English.

Extract and analyze three core financial pillars from the uploaded PDF:
1. PROFITABILITY & MARGINS: Profit margins, return on capital, drivers of net earnings, and cost pressures.
2. DEBT, LIQUIDITY & CAPITAL HEALTH: Borrowing levels, cash reserves, capital adequacy, and solvency.
3. OPERATING EFFICIENCY & REVENUE COMPOSITION: How efficiently the company runs its operations, employee/tech costs, and shift toward core recurring revenue.

============================================================
RULES:
- Use plain, conversational, professional English.
- Explain technical metrics in brackets or everyday terms.
- Use exact figures and percentages found in the report.
- Return ONLY valid JSON with this structure:
{
  "profitability_depth": {
    "headline": "Short plain English verdict on profitability",
    "insights": ["Point 1 with numbers", "Point 2 with numbers", "Point 3 with numbers"]
  },
  "debt_and_liquidity": {
    "headline": "Short plain English verdict on debt and balance sheet safety",
    "insights": ["Point 1 with numbers", "Point 2 with numbers", "Point 3 with numbers"]
  },
  "operating_efficiency": {
    "headline": "Short plain English verdict on operational efficiency and scale",
    "insights": ["Point 1 with numbers", "Point 2 with numbers", "Point 3 with numbers"]
  }
}
"""
            with st.spinner("Gemini is conducting an in-depth financial investigation..."):
                try:
                    deep_res = generate_with_fallback(
                        contents=[deep_prompt, st.session_state.gemini_file],
                        json_mode=True
                    )
                    deep_data = clean_json_response(deep_res.text)
                    if deep_data and "profitability_depth" in deep_data:
                        st.session_state.deep_dive = deep_data
                    else:
                        st.warning("Could not structure deep-dive data. Please try again.")
                except Exception as e:
                    st.error(f"Deep-dive analysis error: {e}")

        if st.session_state.deep_dive:
            dd = st.session_state.deep_dive
            prof = dd.get("profitability_depth", {})
            debt = dd.get("debt_and_liquidity", {})
            eff = dd.get("operating_efficiency", {})

            col_d1, col_d2, col_d3 = st.columns(3)

            with col_d1:
                st.markdown(f"""
                <div class="deep-card">
                    <div class="deep-card-title">📊 Profitability & Margins</div>
                    <div style="color: #ffffff; font-weight: 600; font-size: 14px; margin-bottom: 10px;">{prof.get('headline', '')}</div>
                """, unsafe_allow_html=True)
                for pt in prof.get("insights", []):
                    st.markdown(f"• {pt}")
                st.markdown("</div>", unsafe_allow_html=True)

            with col_d2:
                st.markdown(f"""
                <div class="deep-card">
                    <div class="deep-card-title">🛡️ Debt & Balance Sheet Safety</div>
                    <div style="color: #ffffff; font-weight: 600; font-size: 14px; margin-bottom: 10px;">{debt.get('headline', '')}</div>
                """, unsafe_allow_html=True)
                for pt in debt.get("insights", []):
                    st.markdown(f"• {pt}")
                st.markdown("</div>", unsafe_allow_html=True)

            with col_d3:
                st.markdown(f"""
                <div class="deep-card">
                    <div class="deep-card-title">⚙️ Operating Efficiency & Scale</div>
                    <div style="color: #ffffff; font-weight: 600; font-size: 14px; margin-bottom: 10px;">{eff.get('headline', '')}</div>
                """, unsafe_allow_html=True)
                for pt in eff.get("insights", []):
                    st.markdown(f"• {pt}")
                st.markdown("</div>", unsafe_allow_html=True)

    elif mcq_choice == "No":
        st.info("💡 Feel free to explore the tabs above or ask any question below if you have any doubts!")

# ============================================================
# ASK GEMINI EXPERIENCE
# ============================================================

st.divider()
st.markdown('<div class="section-title">💬 Ask Questions About This Financial Report</div>', unsafe_allow_html=True)
st.markdown('<div class="section-description">Ask any custom question in plain English, or click one of the suggested prompts below. Gemini answers strictly using the uploaded PDF.</div>', unsafe_allow_html=True)

# Quick Prompts / Chips
st.markdown("**Suggested Questions:**")
chip_cols = st.columns(4)
suggested_question = None

with chip_cols[0]:
    if st.button("📈 Why did profits change YoY?", use_container_width=True):
        suggested_question = "Why did profits change compared with the previous year? Break down key drivers of the profit change in simple terms."
with chip_cols[1]:
    if st.button("🚀 What are the biggest growth drivers?", use_container_width=True):
        suggested_question = "What are the company's major growth drivers and biggest future expansion opportunities based on this report?"
with chip_cols[2]:
    if st.button("💰 Explain debt & cash position", use_container_width=True):
        suggested_question = "How is the company's debt, borrowings, and overall cash/liquidity position? Is its financial footing strong?"
with chip_cols[3]:
    if st.button("⚠️ Key risks for investors", use_container_width=True):
        suggested_question = "What are the primary operational, financial, and market risks an investor should know about?"

# Header row with clear button
chat_header_left, chat_header_right = st.columns([4, 1])
with chat_header_right:
    if st.session_state.chat_history:
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

# Display Conversation History
for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# Text Input Bar
user_input = st.chat_input("Ask a question about this financial report...")

active_query = user_input or suggested_question

if active_query:
    st.session_state.chat_history.append({
        "role": "user",
        "content": active_query
    })
    
    with st.chat_message("user"):
        st.markdown(active_query)

    question_prompt = f"""
You are a helpful, clear financial guide talking to a regular investor or finance student.
Answer the user's question using ONLY facts from the uploaded financial report.

USER QUESTION:
{active_query}

============================================================
RULES FOR ANSWERING
============================================================
1. Answer directly and in simple, clear everyday English.
2. Avoid textbook jargon. If a technical term is necessary, explain what it means in plain words immediately.
3. Use concrete numbers and percentages from the report whenever helpful, and explain what those numbers mean in real life.
4. If the question is outside the scope of the report or the information is missing, state clearly:
   "The uploaded report does not contain specific information regarding this."
5. Do NOT give direct Buy, Sell or Hold recommendations.
6. Format your answer cleanly with Markdown:
   ### Direct Answer
   (2-3 clear plain-English paragraphs answering the question directly)
   
   ### Key Numbers & Facts
   (Bullet points with specific figures and what they mean)
   
   ### What This Means For You
   (Practical takeaway for an investor or analyst)
   
   ### What to Watch
   (1-2 specific future checkpoints or indicators)
"""

    with st.chat_message("assistant"):
        with st.spinner("Gemini is reading the report and preparing your answer..."):
            try:
                response = generate_with_fallback(
                    contents=[question_prompt, st.session_state.gemini_file],
                    json_mode=False
                )
                answer = response.text.strip() if response.text else "Gemini returned an empty response. Please try asking again."
                st.markdown(answer)
                
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": answer
                })
            except Exception as error:
                error_msg = f"Could not generate answer: {str(error)}"
                st.error(error_msg)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": error_msg
                })

# ============================================================
# FOOTER
# ============================================================

st.divider()
st.markdown("""
<div class="footer">
    Financial Analysis Copilot • AI analysis grounded in uploaded financial reports. For analytical and educational purposes only.
</div>
""", unsafe_allow_html=True)
