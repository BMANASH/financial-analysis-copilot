import streamlit as st
import json
import re
import tempfile
import os
import time
import io
from datetime import datetime

# Safe imports for data handling
try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import yfinance as yf
except ImportError:
    yf = None

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
.scorecard-card {
    background: #151a24;
    border: 1px solid #283648;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 16px;
    min-height: 240px;
}
.scorecard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}
.scorecard-title {
    color: #ffffff;
    font-size: 16px;
    font-weight: 700;
}
.scorecard-badge {
    background: rgba(59, 130, 246, 0.18);
    color: #60a5fa;
    border: 1px solid rgba(59, 130, 246, 0.35);
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 700;
}
.scorecard-verdict {
    color: #cbd5e1;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 12px;
    line-height: 1.4;
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
.position-box {
    background: #131822;
    border: 1px solid #28374d;
    border-radius: 14px;
    padding: 22px;
    margin-top: 15px;
    margin-bottom: 20px;
}
.invest-kpi-card {
    background: #171f2d;
    border: 1px solid #2e405a;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    margin-bottom: 14px;
}
.invest-kpi-label {
    color: #94a3b8;
    font-size: 11.5px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.invest-kpi-val {
    color: #ffffff;
    font-size: 21px;
    font-weight: 750;
    margin-top: 5px;
}
.invest-section-box {
    background: #141a24;
    border: 1px solid #283648;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 18px;
}
.invest-section-header {
    color: #60a5fa;
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.invest-subcard {
    background: #18202d;
    border: 1px solid #2a384d;
    border-left: 3px solid #3b82f6;
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.invest-subcard-title {
    color: #ffffff;
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 4px;
}
.invest-subcard-body {
    color: #cbd5e1;
    font-size: 13.5px;
    line-height: 1.5;
}
.price-gauge-card {
    background: #161e2c;
    border: 1px solid #2d3e58;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 16px;
}
.gauge-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
    font-size: 13.5px;
}
.chart-box {
    background: #151a24;
    border: 1px solid #283241;
    border-radius: 14px;
    padding: 22px;
    margin-bottom: 18px;
}
.chart-title {
    color: #ffffff;
    font-size: 16px;
    font-weight: 650;
    margin-bottom: 4px;
}
.chart-desc {
    color: #8f9aaa;
    font-size: 13px;
    margin-bottom: 18px;
}
.vis-row {
    margin-bottom: 16px;
}
.vis-label {
    display: flex;
    justify-content: space-between;
    font-size: 13.5px;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 6px;
}
.vis-track {
    background: #232b38;
    border-radius: 8px;
    height: 26px;
    width: 100%;
    overflow: hidden;
    position: relative;
}
.vis-fill-curr {
    background: linear-gradient(90deg, #3b82f6, #60a5fa);
    height: 100%;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding-right: 10px;
    color: #ffffff;
    font-size: 12px;
    font-weight: 700;
}
.vis-fill-prev {
    background: #475569;
    height: 100%;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding-right: 10px;
    color: #ffffff;
    font-size: 12px;
    font-weight: 700;
}
.vis-fill-pos {
    background: linear-gradient(90deg, #059669, #10b981);
    height: 100%;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding-right: 10px;
    color: #ffffff;
    font-size: 12px;
    font-weight: 700;
}
.vis-fill-neg {
    background: linear-gradient(90deg, #dc2626, #ef4444);
    height: 100%;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding-right: 10px;
    color: #ffffff;
    font-size: 12px;
    font-weight: 700;
}
.slicer-card {
    background: #151d2a;
    border: 1px solid #2d3e58;
    border-left: 3px solid #3b82f6;
    border-radius: 8px;
    padding: 12px 14px;
    margin-top: 10px;
    margin-bottom: 12px;
}
.slicer-meaning {
    color: #e2e8f0;
    font-size: 12.5px;
    line-height: 1.5;
}
.footer {
    color: #707b8c;
    font-size: 12px;
    text-align: center;
    padding-top: 25px;
}
input::-webkit-contacts-auto-fill-button,
input::-webkit-credentials-auto-fill-button {
    visibility: hidden;
    display: none !important;
    pointer-events: none;
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
    "position_assessment": None,
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
# PRODUCTION TEXT MODELS
# ============================================================

ACTIVE_MODELS = [
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-pro-preview"
]

def generate_with_fallback(contents, json_mode=False):
    errors = []
    ordered = ACTIVE_MODELS.copy()
    if st.session_state.selected_model and st.session_state.selected_model in ordered:
        ordered.remove(st.session_state.selected_model)
        ordered.insert(0, st.session_state.selected_model)

    for model in ordered:
        for attempt in range(2):
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
                err_str = str(error)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    time.sleep(2.5)
                    continue
                errors.append(f"{model}: {err_str}")
                break

    error_text = "\n\n".join(errors)
    raise Exception(f"API Rate limit reached. Please wait a few seconds and try again.\n\n{error_text}")

# ============================================================
# SAFE PARSERS & LIVE MARKET LOOKUP
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

def parse_clean_float(val):
    if val is None:
        return None
    cleaned = str(val).replace(",", "").replace("₹", "").replace("$", "").replace("%", "").strip()
    match = re.search(r"[-+]?\d*\.?\d+", cleaned)
    if match:
        try:
            return float(match.group())
        except Exception:
            return None
    return None

def fetch_live_stock_price(company_name, ticker_hint=""):
    """Pulls live stock quote from NSE/BSE using yfinance or falls back cleanly"""
    if not yf:
        return None

    try:
        candidates = []
        if ticker_hint:
            candidates.extend([f"{ticker_hint}.NS", f"{ticker_hint}.BO", ticker_hint])

        c_lower = company_name.lower()
        if "jio" in c_lower:
            candidates.extend(["JIOFIN.NS", "JIOFIN.BO"])
        elif "tata motors" in c_lower:
            candidates.extend(["TATAMOTORS.NS", "TATAMOTORS.BO"])
        elif "tata power" in c_lower:
            candidates.extend(["TATAPOWER.NS", "TATAPOWER.BO"])
        elif "varun beverages" in c_lower:
            candidates.extend(["VBL.NS", "VBL.BO"])
        elif "hudco" in c_lower:
            candidates.extend(["HUDCO.NS", "HUDCO.BO"])
        elif "nhpc" in c_lower:
            candidates.extend(["NHPC.NS", "NHPC.BO"])

        for sym in candidates:
            try:
                tk = yf.Ticker(sym)
                hist = tk.history(period="5d")
                if not hist.empty:
                    last_price = float(hist["Close"].iloc[-1])
                    last_date = hist.index[-1].strftime("%d %b %Y")
                    return {
                        "is_listed": True,
                        "ticker": sym.replace(".NS", "").replace(".BO", ""),
                        "price": last_price,
                        "as_on": last_date,
                        "exchange": "NSE" if ".NS" in sym else ("BSE" if ".BO" in sym else "Exchange")
                    }
            except Exception:
                continue
    except Exception:
        pass
    return None

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
                    st.session_state.position_assessment = None
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

    # ========================================================
    # SIDEBAR EXPORT SECTION
    # ========================================================
    if st.session_state.analysis and pd is not None:
        st.markdown("---")
        st.markdown("### 📥 Export Dashboard")
        
        # Excel Export Buffer
        metrics_list = st.session_state.analysis.get("key_metrics", [])
        if metrics_list:
            df_export = pd.DataFrame(metrics_list)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_export.to_excel(writer, index=False, sheet_name='Key Financial Metrics')
            excel_data = output.getvalue()

            st.download_button(
                label="Download Metrics Excel (.xlsx)",
                data=excel_data,
                file_name=f"{st.session_state.uploaded_name.replace('.pdf', '')}_Financial_Metrics.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        # Text/PDF Report Summary Export
        comp_name = st.session_state.analysis.get("company_overview", {}).get("company_name", "Financial_Report")
        summary_text = f"FINANCIAL ANALYSIS SUMMARY: {comp_name}\n" + "="*50 + "\n\n"
        summary_text += f"Report File: {st.session_state.uploaded_name}\n"
        summary_text += f"Generated Date: {datetime.today().strftime('%d %b %Y')}\n\n"
        
        overview = st.session_state.analysis.get("company_overview", {})
        summary_text += f"Industry: {overview.get('industry', 'N/A')}\n"
        summary_text += f"Business: {overview.get('business_type', 'N/A')}\n\n"
        
        if st.session_state.position_assessment:
            pos = st.session_state.position_assessment
            summary_text += "PERSONALIZED INVESTMENT ASSESSMENT:\n" + "-"*35 + "\n"
            summary_text += f"Status: {pos.get('position_summary', '')}\n"
            summary_text += f"Return: {pos.get('pnl_str', '')} ({pos.get('amt_str', '')})\n"
            summary_text += f"Market Price: {pos.get('cmp_display', '')} as on {pos.get('live_date', '')}\n\n"

        st.download_button(
            label="Download Report Summary (.txt)",
            data=summary_text,
            file_name=f"{comp_name.replace(' ', '_')}_Summary_Report.txt",
            mime="text/plain",
            use_container_width=True
        )

    # ========================================================
    # SIDEBAR INTERACTIVE GLOSSARY (PDF-GROUNDED)
    # ========================================================
    if st.session_state.analysis and "terms_cheat_sheet" in st.session_state.analysis:
        cheat_terms = st.session_state.analysis.get("terms_cheat_sheet", [])
        if cheat_terms:
            st.markdown("---")
            st.markdown("### 📌 Financial Glossary")
            st.caption("Choose a term from this report to see a simple, one-sentence explanation:")

            term_map = {item.get("term", "").strip(): item.get("meaning", "").strip() for item in cheat_terms if item.get("term")}
            term_names = list(term_map.keys())

            if term_names:
                selected_jargon = st.selectbox(
                    "Select a financial term:",
                    options=term_names,
                    index=0,
                    key="sidebar_jargon_slicer",
                    label_visibility="collapsed"
                )

                selected_definition = term_map[selected_jargon]
                st.markdown(f"""
                <div class="slicer-card">
                    <div style="color: #60a5fa; font-weight: 700; font-size: 13px; margin-bottom: 4px;">💡 {selected_jargon}</div>
                    <div class="slicer-meaning">{selected_definition}</div>
                </div>
                """, unsafe_allow_html=True)

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
You are an expert financial mentor explaining an annual report to everyday investors and finance students in simple, clean, professional English without textbook jargon.

Analyze ONLY the uploaded PDF. It can belong to ANY company.
Identify the company name, stock ticker (if applicable), industry, reporting period, report type, and describe what the business actually does and how it earns revenue in 2 plain sentences.

============================================================
STRICT CONTENT & PLAIN-ENGLISH RULES
============================================================
1. NO DENSE JARGON: Translate complex metrics into real-world meaning without losing facts or exact numbers.
2. KEY_METRICS: Extract exactly 12 to 18 of the most relevant financial, revenue, loan, asset, and profit metrics found in the report. Keep the metric name clean and concise.
3. INVESTOR_SCORECARD:
   - "growth_momentum": badge, verdict, and 3 bullet points with figures.
   - "profitability_quality": badge, verdict, and 3 bullet points explaining why profits moved.
   - "balance_sheet_safety": badge, verdict, and 3 bullet points explaining debt, cash, and safety cushion.
   - "strategic_execution": badge, verdict, and 3 bullet points explaining new businesses, apps, and major milestones.
4. MANAGEMENT_COMMENTARY: Provide 4 to 6 strategic management themes or future plans in plain words.
5. RISKS: Provide 5 to 6 distinct risk factors. Explain the risk clearly and what it means for an everyday investor.
6. ANALYST_TAKEAWAY:
   - "improving": 4 to 6 positive points with figures.
   - "weakening": 4 to 6 challenges, drops, or costs with figures.
   - "growth_drivers": 4 to 6 future revenue growth opportunities.
   - "investor_watch": 4 to 6 specific checkpoints an investor should track next.
7. TERMS_CHEAT_SHEET: Extract 8 to 12 specific financial, reporting, or balance sheet terms that appear inside THIS uploaded PDF. Provide a clear 1-line plain English explanation of what it means for this company.

============================================================
OUTPUT FORMAT (JSON ONLY)
============================================================
Return ONLY valid JSON with this exact structure:
{
  "company_overview": {
    "company_name": "",
    "stock_ticker": "e.g. JIOFIN or TATAMOTORS",
    "industry": "",
    "business_type": "2 clear sentences on what the company actually does and how it earns revenue",
    "reporting_period": "",
    "report_type": ""
  },
  "terms_cheat_sheet": [
    {
      "term": "Term Name (e.g. Consolidated)",
      "meaning": "1 short plain English sentence explaining what it means for this company"
    }
  ],
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
  "investor_scorecard": {
    "growth_momentum": {
      "badge": "e.g. Robust Expansion",
      "verdict": "1-sentence plain English summary",
      "points": ["Point 1 with numbers in simple words", "Point 2 with numbers in simple words", "Point 3 with numbers in simple words"]
    },
    "profitability_quality": {
      "badge": "e.g. Under Near-term Cost Pressure",
      "verdict": "1-sentence plain English summary",
      "points": ["Point 1 with numbers in simple words", "Point 2 with numbers in simple words", "Point 3 with numbers in simple words"]
    },
    "balance_sheet_safety": {
      "badge": "e.g. Extremely Safe & Well-Capitalized",
      "verdict": "1-sentence plain English summary",
      "points": ["Point 1 with numbers in simple words", "Point 2 with numbers in simple words", "Point 3 with numbers in simple words"]
    },
    "strategic_execution": {
      "badge": "e.g. Rapid Commercial Scale",
      "verdict": "1-sentence plain English summary",
      "points": ["Point 1 with numbers in simple words", "Point 2 with numbers in simple words", "Point 3 with numbers in simple words"]
    }
  },
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

    with st.spinner("Gemini is reading the complete report and generating simple, professional analysis..."):
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
                st.session_state.position_assessment = None
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
    scorecard = data.get("investor_scorecard", {})
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

    # Consolidated Tabs
    tab_scorecard, tab_metrics, tab_charts, tab_mgmt, tab_risks, tab_investor = st.tabs([
        "⭐ Report Overview & Scorecard", "Financial Metrics Table", "📊 Visual Charts", "Management Plans", "Risks", "Investor Takeaway"
    ])

    with tab_scorecard:
        st.subheader("Executive Strategic Scorecard")
        st.write("A structured 4-pillar evaluation matrix explained in simple, practical terms:")

        if scorecard:
            growth_info = scorecard.get("growth_momentum", {})
            prof_info = scorecard.get("profitability_quality", {})
            safety_info = scorecard.get("balance_sheet_safety", {})
            exec_info = scorecard.get("strategic_execution", {})

            col_s1, col_s2 = st.columns(2)

            with col_s1:
                st.markdown(f"""
                <div class="scorecard-card">
                    <div class="scorecard-header">
                        <div class="scorecard-title">🚀 Growth Momentum</div>
                        <div class="scorecard-badge">{growth_info.get('badge', 'Expanding')}</div>
                    </div>
                    <div class="scorecard-verdict">{growth_info.get('verdict', '')}</div>
                """, unsafe_allow_html=True)
                for pt in growth_info.get("points", []):
                    st.markdown(f"• {pt}")
                st.markdown("</div>", unsafe_allow_html=True)

            with col_s2:
                st.markdown(f"""
                <div class="scorecard-card">
                    <div class="scorecard-header">
                        <div class="scorecard-title">💰 Profitability & Earnings Quality</div>
                        <div class="scorecard-badge">{prof_info.get('badge', 'Operating Profit')}</div>
                    </div>
                    <div class="scorecard-verdict">{prof_info.get('verdict', '')}</div>
                """, unsafe_allow_html=True)
                for pt in prof_info.get("points", []):
                    st.markdown(f"• {pt}")
                st.markdown("</div>", unsafe_allow_html=True)

            col_s3, col_s4 = st.columns(2)

            with col_s3:
                st.markdown(f"""
                <div class="scorecard-card">
                    <div class="scorecard-header">
                        <div class="scorecard-title">🛡️ Balance Sheet Resilience</div>
                        <div class="scorecard-badge">{safety_info.get('badge', 'Capital Cushion')}</div>
                    </div>
                    <div class="scorecard-verdict">{safety_info.get('verdict', '')}</div>
                """, unsafe_allow_html=True)
                for pt in safety_info.get("points", []):
                    st.markdown(f"• {pt}")
                st.markdown("</div>", unsafe_allow_html=True)

            with col_s4:
                st.markdown(f"""
                <div class="scorecard-card">
                    <div class="scorecard-header">
                        <div class="scorecard-title">⚙️ Strategic & Commercial Scale</div>
                        <div class="scorecard-badge">{exec_info.get('badge', 'Executing')}</div>
                    </div>
                    <div class="scorecard-verdict">{exec_info.get('verdict', '')}</div>
                """, unsafe_allow_html=True)
                for pt in exec_info.get("points", []):
                    st.markdown(f"• {pt}")
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Scorecard will automatically appear once the report is analysed.")

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
                if pd is not None:
                    st.dataframe(filtered_rows, use_container_width=True, hide_index=True, height=450)
                else:
                    for row in filtered_rows:
                        st.write(f"**{row['Metric Name']}**: {row['Current Period']} {row['Unit']} (YoY: {row['YoY Growth']})")
            else:
                st.info("No metrics matching your search.")
        else:
            st.info("No financial metrics found.")

    with tab_charts:
        st.subheader("Visual Financial Comparisons")
        st.write("Clean graphical views to help compare performance at a glance:")

        chart_records = []
        for m in metrics:
            curr_val = parse_clean_float(m.get("current_period"))
            prev_val = parse_clean_float(m.get("previous_period"))
            growth_val = parse_clean_float(m.get("yoy_growth"))
            m_name = m.get("metric", "").strip()

            if curr_val is not None and prev_val is not None:
                chart_records.append({
                    "Metric": m_name,
                    "Previous": prev_val,
                    "Current": curr_val,
                    "Growth (%)": growth_val if growth_val is not None else 0.0,
                    "Unit": m.get("unit", "").strip()
                })

        if chart_records:
            col_v1, col_v2 = st.columns(2)

            with col_v1:
                st.markdown("""
                <div class="chart-box">
                    <div class="chart-title">🔍 Metric Visual Comparison</div>
                    <div class="chart-desc">Select any metric to see its Previous vs. Current value side-by-side:</div>
                """, unsafe_allow_html=True)

                metric_options = [r["Metric"] for r in chart_records]
                chosen_metric_name = st.selectbox(
                    "Choose metric to inspect:",
                    options=metric_options,
                    index=0,
                    key="visual_metric_selector"
                )

                selected_item = next(r for r in chart_records if r["Metric"] == chosen_metric_name)
                c_val = selected_item["Current"]
                p_val = selected_item["Previous"]
                u_lbl = selected_item["Unit"]
                g_val = selected_item["Growth (%)"]

                max_val = max(abs(c_val), abs(p_val)) if max(abs(c_val), abs(p_val)) > 0 else 1
                prev_pct = max(int((abs(p_val) / max_val) * 100), 10)
                curr_pct = max(int((abs(c_val) / max_val) * 100), 10)

                diff_amt = c_val - p_val
                growth_sign = "+" if diff_amt >= 0 else ""
                growth_color = "#34d399" if diff_amt >= 0 else "#f87171"

                compare_card_html = f"""
                <div style="background: #111722; padding: 18px; border-radius: 12px; border: 1px solid #233145; margin-top: 10px;">
                    <div class="vis-row">
                        <div class="vis-label">
                            <span style="color: #94a3b8;">Previous Period</span>
                            <span>{p_val:,.2f} {u_lbl}</span>
                        </div>
                        <div class="vis-track">
                            <div class="vis-fill-prev" style="width: {prev_pct}%;">{p_val:,.2f} {u_lbl}</div>
                        </div>
                    </div>
                    <div class="vis-row" style="margin-top: 15px;">
                        <div class="vis-label">
                            <span style="color: #60a5fa;">Current Period</span>
                            <span>{c_val:,.2f} {u_lbl}</span>
                        </div>
                        <div class="vis-track">
                            <div class="vis-fill-curr" style="width: {curr_pct}%;">{c_val:,.2f} {u_lbl}</div>
                        </div>
                    </div>
                    <div style="margin-top: 16px; padding-top: 12px; border-top: 1px solid #1f2a3c; display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #8f9aaa; font-size: 13px;">Net Change:</span>
                        <span style="color: {growth_color}; font-weight: 700; font-size: 15px;">
                            {growth_sign}{diff_amt:,.2f} {u_lbl} ({growth_sign}{g_val:,.1f}% YoY)
                        </span>
                    </div>
                </div>
                </div>
                """
                st.markdown(compare_card_html, unsafe_allow_html=True)

            with col_v2:
                st.markdown("""
                <div class="chart-box">
                    <div class="chart-title">📈 Year-over-Year Growth Leaders</div>
                    <div class="chart-desc">Horizontal performance bars with exact percentages:</div>
                """, unsafe_allow_html=True)

                growth_items = [r for r in chart_records if r["Growth (%)"] != 0.0]
                growth_items.sort(key=lambda x: abs(x["Growth (%)"]), reverse=True)
                top_growers = growth_items[:6]

                if top_growers:
                    max_growth = max(abs(r["Growth (%)"]) for r in top_growers) if top_growers else 100
                    
                    for item in top_growers:
                        g_pct = item["Growth (%)"]
                        bar_w = min(max(int((abs(g_pct) / max_growth) * 100), 12), 100)
                        bar_class = "vis-fill-pos" if g_pct >= 0 else "vis-fill-neg"
                        g_tag = f"+{g_pct:,.1f}%" if g_pct >= 0 else f"{g_pct:,.1f}%"

                        growth_row_html = f"""
                        <div class="vis-row">
                            <div class="vis-label">
                                <span>{item['Metric']}</span>
                                <span style="color: {'#34d399' if g_pct >= 0 else '#f87171'};">{g_tag}</span>
                            </div>
                            <div class="vis-track">
                                <div class="{bar_class}" style="width: {bar_w}%;">{g_tag}</div>
                            </div>
                        </div>
                        """
                        st.markdown(growth_row_html, unsafe_allow_html=True)
                else:
                    st.info("No comparative growth items found.")

                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("💡 Charts will appear as soon as numerical values are recorded in the report.")

    with tab_mgmt:
        st.subheader("Management Strategy & Outlook")
        st.write("What company leadership says about future plans and technology in everyday language:")
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
            stThe `requirements.txt` file for your **financial-analysis-copilot** repository looks solid and covers all the core dependencies needed for a Streamlit-based financial assistant using Yahoo Finance, Pandas, PDF processing, and the Gemini API. 

However, there is one small detail to double-check regarding the Google GenAI library:

* **Package Name Check:** Depending on which version of the SDK you are using, the package name is typically `google-genai` (which matches line 5 in your file) or the older `google-generativeai`. If you are using the modern `google-genai` client library, `google-genai` is correct. 
* **Pinning Versions:** It's often a good practice to pin specific versions (e.g., `streamlit>=1.30.0` or `pandas==2.2.0`) to prevent any breaking changes from upstream updates when deploying your app.

Everything else—`streamlit`, `pypdf`, `pandas`, and `yfinance`—is lined up correctly for financial data ingestion and dashboarding. Want to review the `app.py` structure next?
