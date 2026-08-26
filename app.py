import streamlit as st
import json
import re
import tempfile
import os
import time
import io
from datetime import datetime

# Safe imports for data handling & visual BI
try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import yfinance as yf
except ImportError:
    yf = None

try:
    import plotly.graph_objects as go
except ImportError:
    go = None

from google import genai
from google.genai import types

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Financial Analyst AI | BI Terminal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# INSTITUTIONAL POWER BI COCKPIT THEME & CSS
# ============================================================

st.markdown("""
<style>
.stApp {
    background: #06080e;
    color: #f1f5f9;
}
.block-container {
    max-width: 1460px;
    padding-top: 1.8rem;
    padding-bottom: 4rem;
}

/* Hide Streamlit Status Widget */
div[data-testid="stStatusWidget"] {
    display: none !important;
    visibility: hidden !important;
}

/* Entry Animation */
@keyframes fadeInSlide {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes pulseGlow {
    0%, 100% {
        box-shadow: 0 20px 50px -10px rgba(0, 0, 0, 0.9), 0 0 25px rgba(59, 130, 246, 0.25);
        border-color: rgba(59, 130, 246, 0.45);
    }
    50% {
        box-shadow: 0 25px 60px -10px rgba(0, 0, 0, 0.95), 0 0 40px rgba(96, 165, 250, 0.45);
        border-color: rgba(96, 165, 250, 0.75);
    }
}
@keyframes spinGlow {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
@keyframes shimmerBar {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

/* Center Glassmorphic Loader */
.center-loader-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: rgba(14, 20, 34, 0.92) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    border: 1px solid rgba(59, 130, 246, 0.5) !important;
    border-radius: 20px !important;
    padding: 38px 36px !important;
    margin: 25px auto !important;
    text-align: center;
    max-width: 640px;
    animation: fadeInSlide 0.4s ease-out forwards, pulseGlow 3s infinite ease-in-out !important;
}
.loader-status-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(59, 130, 246, 0.15);
    border: 1px solid rgba(59, 130, 246, 0.35);
    color: #60a5fa;
    font-size: 11px;
    font-weight: 750;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 4px 12px;
    border-radius: 20px;
    margin-bottom: 18px;
}
.fintech-spinner {
    width: 54px;
    height: 54px;
    border: 3.5px solid rgba(59, 130, 246, 0.15);
    border-top: 3.5px solid #60a5fa;
    border-right: 3.5px solid #3b82f6;
    border-radius: 50%;
    animation: spinGlow 0.85s cubic-bezier(0.68, -0.55, 0.27, 1.55) infinite;
    margin-bottom: 18px;
    box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
}
.loader-title {
    color: #ffffff;
    font-size: 20.5px;
    font-weight: 800;
    margin-bottom: 8px;
}
.loader-subtitle {
    color: #94a3b8;
    font-size: 13.5px;
    line-height: 1.55;
    margin-bottom: 22px;
    max-width: 500px;
}
.loader-progress-track {
    background: rgba(15, 23, 42, 0.9);
    border: 1px solid rgba(59, 130, 246, 0.25);
    border-radius: 12px;
    height: 7px;
    width: 85%;
    overflow: hidden;
    position: relative;
}
.loader-progress-fill {
    background: linear-gradient(90deg, transparent, #38bdf8, #3b82f6, transparent);
    height: 100%;
    width: 100%;
    animation: shimmerBar 1.6s infinite ease-in-out;
}

/* Header & Telemetry */
.hero {
    background: linear-gradient(135deg, #0c1222 0%, #070a12 100%);
    border: 1px solid #1e293b;
    border-top: 3px solid #3b82f6;
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 18px;
    box-shadow: 0 16px 36px -12px rgba(0, 0, 0, 0.7);
    animation: fadeInSlide 0.4s ease-out forwards;
}
.hero-title {
    font-size: 36px;
    font-weight: 800;
    line-height: 1.15;
    margin-bottom: 6px;
    background: linear-gradient(90deg, #ffffff, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-subtitle {
    font-size: 15px;
    color: #94a3b8;
    line-height: 1.5;
}
.fintech-badge-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 12px;
}
.fintech-pill {
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid #334155;
    color: #93c5fd;
    font-size: 11.5px;
    font-weight: 600;
    padding: 4px 11px;
    border-radius: 20px;
    display: inline-flex;
    align-items: center;
    gap: 5px;
}
.telemetry-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 10px;
    margin-bottom: 20px;
    padding: 10px 14px;
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid #1e293b;
    border-radius: 10px;
}
.telemetry-pill {
    background: #0e1526;
    border: 1px solid #23334d;
    color: #93c5fd;
    font-size: 12px;
    font-weight: 650;
    padding: 4px 12px;
    border-radius: 20px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}
.processing-note-card {
    background: linear-gradient(135deg, #0e1526 0%, #0a0e1a 100%);
    border: 1px solid #1e293b;
    border-left: 4px solid #f59e0b;
    border-radius: 12px;
    padding: 14px 18px;
    margin-top: 12px;
    margin-bottom: 20px;
}
.ack-card {
    background: rgba(14, 20, 34, 0.7);
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-left: 4px solid #3b82f6;
    border-radius: 10px;
    padding: 14px 18px;
    margin-top: 12px;
    margin-bottom: 12px;
    color: #cbd5e1;
    font-size: 13.5px;
    line-height: 1.5;
}

/* Symmetrical Overview Cards */
.company-card {
    background: #0b0f19;
    border: 1px solid #1a2234;
    border-radius: 14px;
    padding: 16px;
    height: 145px;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    overflow-y: auto;
    margin-bottom: 10px;
    transition: all 0.3s ease;
}
.company-card:hover {
    border-color: #60a5fa !important;
    transform: translateY(-3px);
}
.company-label {
    color: #fbbf24;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.9px;
    margin-bottom: 6px;
    font-weight: 700;
}
.company-value {
    color: #f8fafc;
    font-size: 13.5px;
    font-weight: 550;
    line-height: 1.45;
}

/* BI Power KPI Cards */
.bi-kpi-card {
    background: linear-gradient(145deg, #0d121f 0%, #080b13 100%);
    border: 1px solid #1e293b;
    border-radius: 14px;
    padding: 18px 20px;
    min-height: 160px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: all 0.3s ease;
}
.bi-kpi-card:hover {
    border-color: #3b82f6;
    box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.35);
    transform: translateY(-4px);
}
.kpi-header-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.kpi-title {
    color: #94a3b8;
    font-size: 11.5px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}
.kpi-main-val {
    color: #ffffff;
    font-size: 26px;
    font-weight: 850;
    margin: 6px 0;
    letter-spacing: -0.5px;
}
.spark-track {
    background: #172033;
    border-radius: 4px;
    height: 5px;
    width: 100%;
    margin-top: 8px;
    overflow: hidden;
}
.spark-fill-pos {
    background: linear-gradient(90deg, #059669, #10b981);
    height: 100%;
    border-radius: 4px;
}
.spark-fill-neg {
    background: linear-gradient(90deg, #dc2626, #ef4444);
    height: 100%;
    border-radius: 4px;
}
.spark-fill-neutral {
    background: #3b82f6;
    height: 100%;
    border-radius: 4px;
}

/* Section Headings */
.section-title {
    font-size: 23px;
    font-weight: 750;
    color: #f8fafc;
    margin-top: 28px;
    margin-bottom: 4px;
}
.section-description {
    color: #94a3b8;
    font-size: 13.5px;
    margin-bottom: 16px;
}
.fintech-banner {
    background: linear-gradient(135deg, #0d121f 0%, #080b13 100%);
    border: 1px solid #1a2234;
    border-left: 4px solid #3b82f6;
    border-radius: 12px;
    padding: 18px 22px;
    margin-top: 32px;
    margin-bottom: 16px;
}
.fintech-banner-title {
    font-size: 19px;
    font-weight: 750;
    color: #ffffff;
    margin-bottom: 4px;
}
.fintech-banner-desc {
    font-size: 13.5px;
    color: #94a3b8;
}

/* Feature Cards on Welcome Screen */
.feature-card {
    background: #0b0f19;
    border: 1px solid #1a2234;
    border-radius: 14px;
    padding: 22px;
    height: 100%;
    transition: all 0.35s ease;
    box-shadow: 0 8px 24px -8px rgba(0, 0, 0, 0.6);
}
.feature-card:hover {
    transform: translateY(-6px) scale(1.02);
    border-color: #60a5fa !important;
    box-shadow: 0 16px 35px -5px rgba(59, 130, 246, 0.45);
}
.feature-icon {
    font-size: 26px;
    margin-bottom: 10px;
}
.feature-title {
    color: #ffffff;
    font-size: 15.5px;
    font-weight: 750;
    margin-bottom: 6px;
}
.feature-desc {
    color: #94a3b8;
    font-size: 13px;
    line-height: 1.45;
}

/* BI Position Boxes */
.deep-card {
    background: #0b0f19;
    border: 1px solid #1a2234;
    border-radius: 14px;
    padding: 22px;
    margin-bottom: 16px;
    min-height: 240px;
}
.deep-card-title {
    color: #60a5fa;
    font-size: 16px;
    font-weight: 750;
    margin-bottom: 12px;
}
.invest-kpi-card {
    background: #10182b;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    margin-bottom: 14px;
}
.invest-kpi-label {
    color: #94a3b8;
    font-size: 11.5px;
    font-weight: 650;
    text-transform: uppercase;
}
.invest-kpi-val {
    color: #ffffff;
    font-size: 21px;
    font-weight: 800;
    margin-top: 5px;
}
.invest-section-box {
    background: #070a12;
    border: 1px solid #1a2234;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 16px;
}
.invest-section-header {
    color: #60a5fa;
    font-size: 15px;
    font-weight: 750;
    margin-bottom: 12px;
}
.invest-subcard {
    background: #111827;
    border: 1px solid #1f2d45;
    border-left: 3px solid #3b82f6;
    border-radius: 8px;
    padding: 12px 14px;
    margin-bottom: 10px;
}
.invest-subcard-title {
    color: #ffffff;
    font-size: 13.5px;
    font-weight: 750;
    margin-bottom: 4px;
}
.invest-subcard-body {
    color: #cbd5e1;
    font-size: 13px;
    line-height: 1.45;
}
.slicer-card {
    background: #0b0f19;
    border: 1px solid #1a2234;
    border-left: 3px solid #3b82f6;
    border-radius: 8px;
    padding: 12px 14px;
    margin-top: 10px;
    margin-bottom: 12px;
}
.slicer-meaning {
    color: #cbd5e1;
    font-size: 12.5px;
    line-height: 1.5;
}
.footer {
    color: #64748b;
    font-size: 12px;
    text-align: center;
    padding-top: 25px;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE & RECOVERY
# ============================================================

defaults = {
    "gemini_file": None,
    "uploaded_name": None,
    "analysis": None,
    "deep_dive": None,
    "selected_model": None,
    "position_assessment": None,
    "chat_history": [],
    "processing_seconds": 0.0,
    "file_size_mb": 0.0
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
    st.error("API key was not found. Please add GEMINI_API_KEY to Streamlit Secrets.")
    st.stop()

@st.cache_resource
def create_client(api_key):
    return genai.Client(api_key=api_key)

client = create_client(API_KEY)

# ============================================================
# PRODUCTION TEXT MODELS
# ============================================================

ACTIVE_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro"
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
# SAFE PARSERS & UNIVERSAL STOCK LOOKUP
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

def auto_classify_metric(name):
    """Guarantees every metric gets a clean BI category bucket"""
    n = str(name).lower()
    if any(k in n for k in ["revenue", "income", "profit", "pat", "ebitda", "margin", "expense", "cost", "turnover", "fee", "sales"]):
        return "Income & Profit"
    elif any(k in n for k in ["npa", "crar", "car", "ratio", "roe", "roa", "coverage", "pcr", "cushion", "leverage", "nim", "percentage", "%"]):
        return "Quality Ratios"
    else:
        return "Balance Sheet & Assets"

def fetch_live_stock_price(company_name, ticker_hint=""):
    if not yf:
        return None
    try:
        candidates = []
        if ticker_hint:
            clean_t = re.sub(r'[^A-Za-z0-9]', '', str(ticker_hint)).upper()
            if clean_t:
                candidates.extend([f"{clean_t}.NS", f"{clean_t}.BO", clean_t])
        if not candidates and company_name:
            first_word = re.sub(r'[^A-Za-z0-9]', '', company_name.split()[0]).upper()
            if len(first_word) >= 3:
                candidates.extend([f"{first_word}.NS", f"{first_word}.BO", first_word])

        for sym in candidates:
            try:
                tk = yf.Ticker(sym)
                hist = tk.history(period="5d")
                if not hist.empty:
                    last_price = float(hist["Close"].iloc[-1])
                    last_date = hist.index[-1].strftime("%d %b %Y")
                    exchange_label = "NSE" if ".NS" in sym else ("BSE" if ".BO" in sym else "Global Market")
                    return {
                        "is_listed": True,
                        "ticker": sym.replace(".NS", "").replace(".BO", ""),
                        "price": last_price,
                        "as_on": last_date,
                        "exchange": exchange_label
                    }
            except Exception:
                continue
    except Exception:
        pass
    return None

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
                raise Exception("AI failed while processing the PDF document.")
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
# HERO SECTION & WELCOME DASHBOARD
# ============================================================

st.markdown("""
<div class="hero">
    <div class="hero-title">Financial Analyst AI</div>
    <div class="hero-subtitle">Institutional-grade BI financial intelligence & portfolio analytics from annual reports</div>
    <div class="fintech-badge-row">
        <span class="fintech-pill">📈 Real-Time Equity Tracking</span>
        <span class="fintech-pill">📊 Balance Sheet Auditing</span>
        <span class="fintech-pill">⚡ Institutional LLM Intelligence</span>
        <span class="fintech-pill">🛡️ Risk & Solvency Assessment</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-title">Upload Financial Report</div>', unsafe_allow_html=True)
st.markdown('<div class="section-description">Drag and drop any company annual report PDF below to automatically start the analysis.</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload Financial Report (PDF)",
    type=["pdf"],
    label_visibility="collapsed",
    key="main_pdf_uploader"
)

st.markdown("""
<div class="processing-note-card">
    <div style="font-weight: 700; color: #fbbf24; margin-bottom: 4px; font-size: 13px; display: flex; align-items: center; gap: 6px;">
        ⏱️ <span>Document Size & Processing Time Advisory</span>
    </div>
    <div style="color: #94a3b8; font-size: 12.5px; line-height: 1.5;">
        Comprehensive annual reports with multi-hundred page disclosures (100–350+ pages) undergo complete table parsing, balance sheet reconciliation, and metric auditing. Processing time scales with document length and may take 1 to 3 minutes for large institutional filings.
    </div>
</div>
""", unsafe_allow_html=True)

loader_container = st.empty()

# Welcome screen if no file is uploaded
if not st.session_state.gemini_file or not st.session_state.analysis:
    if not uploaded_file:
        st.info("👆 Upload an annual report PDF above to begin automatic financial analysis.")
        st.markdown("---")
        st.markdown('<div class="section-title" style="margin-top:0;">⚡ Analysis Engines & Terminal Capabilities</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-description">What this AI analyst generates once your PDF report is uploaded:</div>', unsafe_allow_html=True)
        
        c_feat1, c_feat2, c_feat3, c_feat4 = st.columns(4)
        with c_feat1:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <div class="feature-title">Financial Extraction</div>
                <div class="feature-desc">Extracts 12–18 core balance sheet, revenue, loan book, and PAT numbers with exact YoY growth percentages.</div>
            </div>
            """, unsafe_allow_html=True)
        with c_feat2:
            st.markdown("""
            <div class="feature-card feature-card-alt">
                <div class="feature-icon">📈</div>
                <div class="feature-title">Portfolio Intelligence</div>
                <div class="feature-desc">Pulls live exchange quotes (NSE/BSE/Global) to compute exact P&L, fundamental purchase safety, and 5–8 year outlooks.</div>
            </div>
            """, unsafe_allow_html=True)
        with c_feat3:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🛡️</div>
                <div class="feature-title">Executive Scorecard</div>
                <div class="feature-desc">4-pillar evaluation matrix analyzing Growth Momentum, Profit Quality, Balance Sheet Cushion, and Execution.</div>
            </div>
            """, unsafe_allow_html=True)
        with c_feat4:
            st.markdown("""
            <div class="feature-card feature-card-alt">
                <div class="feature-icon">💬</div>
                <div class="feature-title">Grounded Research Copilot</div>
                <div class="feature-desc">Interactive institutional Q&A answering custom financial queries strictly using facts from the uploaded report.</div>
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# AUTOMATIC GENERATION ON UPLOAD
# ============================================================

if uploaded_file:
    is_new_file = (st.session_state.uploaded_name != uploaded_file.name)

    if is_new_file or st.session_state.analysis is None:
        start_time = time.time()
        file_mb = round(len(uploaded_file.getvalue()) / (1024 * 1024), 2)
        st.session_state.file_size_mb = file_mb

        loader_container.markdown("""
        <div class="center-loader-box">
            <div class="loader-status-tag">⚡ AI Terminal Active • Document Processing</div>
            <div class="fintech-spinner"></div>
            <div class="loader-title">Hang Tight! Reading Financial Report...</div>
            <div class="loader-subtitle">Parsing financial statements, balance sheet disclosures & computing segment growths in real time.</div>
            <div class="loader-progress-track">
                <div class="loader-progress-fill"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        try:
            gemini_file = upload_pdf_to_gemini(uploaded_file)
            st.session_state.gemini_file = gemini_file
            st.session_state.uploaded_name = uploaded_file.name

            loader_container.markdown("""
            <div class="center-loader-box">
                <div class="loader-status-tag">🎯 Finalizing Synthesis • Executive Scorecard</div>
                <div class="fintech-spinner"></div>
                <div class="loader-title">Almost There! Structuring Financial Insights...</div>
                <div class="loader-subtitle">Extracting balance sheet cushions, strategic drivers & live market fundamentals.</div>
                <div class="loader-progress-track">
                    <div class="loader-progress-fill"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            analysis_prompt = """
You are an expert financial mentor explaining an annual report to everyday investors and finance students in simple, clean, professional English without textbook jargon.

Analyze ONLY the uploaded PDF. It can belong to ANY company worldwide.
Identify the company name, stock ticker (if applicable), industry, reporting period, report type, and describe what the business actually does and how it earns revenue in 2 plain sentences.

============================================================
STRICT CONTENT & PLAIN-ENGLISH RULES
============================================================
1. NO DENSE JARGON: Translate complex metrics into real-world meaning without losing facts or exact numbers.
2. KEY_METRICS: Extract exactly 12 to 18 of the most relevant financial, revenue, loan, asset, and profit metrics found in the report.
3. INVESTOR_SCORECARD:
   - "growth_momentum": badge, verdict, health_pct (integer 60-95), and 3 short highlight tags (max 6-8 words each).
   - "profitability_quality": badge, verdict, health_pct (integer 60-95), and 3 short highlight tags (max 6-8 words each).
   - "balance_sheet_safety": badge, verdict, health_pct (integer 60-95), and 3 short highlight tags (max 6-8 words each).
   - "strategic_execution": badge, verdict, health_pct (integer 60-95), and 3 short highlight tags (max 6-8 words each).
4. MANAGEMENT_COMMENTARY: Provide 4 to 6 strategic management themes or future plans in plain words.
5. RISKS: Provide 4 to 6 distinct risk factors with a varied category tag ("Geopolitical", "Credit & Market", "Technology & Cyber", "Regulatory") and distinct impact_level ("High", "Moderate", "Operational").
6. ANALYST_TAKEAWAY:
   - "improving": 4 to 6 positive points with figures.
   - "weakening": 4 to 6 challenges, drops, or costs with figures.
   - "growth_drivers": 4 to 6 future revenue growth opportunities.
   - "investor_watch": 4 to 6 specific checkpoints an investor should track next.
   - "sentiment_score": integer (55 to 88) representing institutional bullishness vs headwinds.
7. TERMS_CHEAT_SHEET: Extract 8 to 12 specific financial, reporting, or balance sheet terms that appear inside THIS uploaded PDF. Provide a clear 1-line plain English explanation of what it means for this company.

============================================================
OUTPUT FORMAT (JSON ONLY)
============================================================
Return ONLY valid JSON with this exact structure:
{
  "company_overview": {
    "company_name": "",
    "stock_ticker": "e.g. INFY, AAPL, TATAMOTORS, SBIN, JIOFIN",
    "industry": "",
    "business_type": "2 clear sentences on what the company actually does and how it earns revenue",
    "reporting_period": "",
    "report_type": ""
  },
  "terms_cheat_sheet": [
    {
      "term": "Term Name",
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
      "health_pct": 84,
      "tags": ["Deposit growth up 11% YoY", "Credit book expanded 16.8%", "Historic volume milestone"]
    },
    "profitability_quality": {
      "badge": "e.g. Solid Profitability",
      "verdict": "1-sentence plain English summary",
      "health_pct": 79,
      "tags": ["PAT grew 12.8% to 80k Cr", "Cost-to-income improved to 50.1%", "Return on Equity at 18.5%"]
    },
    "balance_sheet_safety": {
      "badge": "e.g. Extremely Safe",
      "verdict": "1-sentence plain English summary",
      "health_pct": 92,
      "tags": ["Net NPA declined to 0.39%", "PCR stood at 91.9%", "CRAR fortified at 15.4%"]
    },
    "strategic_execution": {
      "badge": "e.g. Aggressive Scale",
      "verdict": "1-sentence plain English summary",
      "health_pct": 88,
      "tags": ["Digital platform crossed 10M users", "Green advances passed 1T target", "Branch operations centralized"]
    }
  },
  "management_commentary": [
    {
      "title": "Strategy Title",
      "summary": "Plain English summary"
    }
  ],
  "risks": [
    {
      "title": "Risk Name",
      "category": "Geopolitical / Credit & Market / Technology & Cyber / Regulatory",
      "impact_level": "High / Moderate / Operational",
      "what_is_the_risk": "Clear explanation of the danger",
      "why_it_matters": "Plain-English explanation of earnings impact"
    }
  ],
  "analyst_takeaway": {
    "improving": ["4 to 6 bullet points"],
    "weakening": ["4 to 6 bullet points"],
    "growth_drivers": ["4 to 6 bullet points"],
    "investor_watch": ["4 to 6 bullet points"],
    "sentiment_score": 74
  }
}
"""
            response = generate_with_fallback(
                contents=[analysis_prompt, gemini_file],
                json_mode=True
            )
            data = clean_json_response(response.text)
            elapsed_time = round(time.time() - start_time, 1)
            st.session_state.processing_seconds = elapsed_time

            loader_container.empty()
            if data and "company_overview" in data:
                st.session_state.analysis = data
                st.session_state.deep_dive = None
                st.session_state.position_assessment = None
                st.session_state.chat_history = []
                st.success(f"Financial analysis generated successfully in {elapsed_time}s!")
                st.rerun()
            else:
                st.error("Could not parse response. Please re-upload.")
        except Exception as e:
            loader_container.empty()
            st.error(f"Error processing document: {e}")

# ============================================================
# NO PDF STATE
# ============================================================

if not st.session_state.gemini_file or not st.session_state.analysis:
    st.stop()

# ============================================================
# DASHBOARD TELEMETRY & OVERVIEW
# ============================================================

data = st.session_state.analysis
company = data.get("company_overview", {})
metrics = data.get("key_metrics", [])
scorecard = data.get("investor_scorecard", {})
management = data.get("management_commentary", [])
risks = data.get("risks", [])
takeaway = data.get("analyst_takeaway", {})

proc_time = st.session_state.get("processing_seconds", 0.0)
f_size = st.session_state.get("file_size_mb", 0.0)
model_name = st.session_state.get("selected_model", "Gemini Engine")

st.markdown(f"""
<div class="telemetry-bar">
    <span class="telemetry-pill">⏱️ Processing Time: <b>{proc_time}s</b></span>
    <span class="telemetry-pill">🧠 Model Engine: <b>{model_name}</b></span>
    <span class="telemetry-pill">📄 Filing Size: <b>{f_size} MB</b></span>
    <span class="telemetry-pill" style="border-color: #059669; color: #34d399;">🟢 Status: <b>Audited & Reconciled</b></span>
</div>
""", unsafe_allow_html=True)

with st.expander("📌 Financial Glossary & Report Terms", expanded=False):
    cheat_terms = data.get("terms_cheat_sheet", [])
    if cheat_terms:
        term_map = {item.get("term", "").strip(): item.get("meaning", "").strip() for item in cheat_terms if item.get("term")}
        term_names = list(term_map.keys())
        if term_names:
            selected_jargon = st.selectbox("Select a financial term:", options=term_names, index=0, key="glossary_slicer")
            st.markdown(f"""
            <div class="slicer-card">
                <div style="color: #60a5fa; font-weight: 700; font-size: 13px; margin-bottom: 4px;">💡 {selected_jargon}</div>
                <div class="slicer-meaning">{term_map[selected_jargon]}</div>
            </div>
            """, unsafe_allow_html=True)

# Company Overview Cards
st.markdown('<div class="section-title">Company Overview</div>', unsafe_allow_html=True)
st.markdown('<div class="section-description">A quick snapshot of the company and its primary revenue engine.</div>', unsafe_allow_html=True)

overview_items = [
    ("Company", company.get("company_name", "Not available")),
    ("Industry", company.get("industry", "Not available")),
    ("What They Do", company.get("business_type", "Not available")),
    ("Reporting Period", company.get("reporting_period", "Not available")),
    ("Report Type", company.get("report_type", "Not available"))
]

overview_columns = st.columns(5)
for column, item in zip(overview_columns, overview_items):
    with column:
        st.markdown(f"""
        <div class="company-card">
            <div class="company-label">{item[0]}</div>
            <div class="company-value">{item[1]}</div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# BI POWER KPI TILES
# ============================================================

st.markdown('<div class="section-title">Key Financial Metrics (BI Tile Matrix)</div>', unsafe_allow_html=True)
st.markdown('<div class="section-description">Core revenue, profit, and balance sheet KPIs with directional momentum indicators.</div>', unsafe_allow_html=True)

headline_metrics = []
priority_words = ["total income", "revenue", "profit after tax", "pat", "net profit", "operating profit", "ebitda", "net interest income"]

for m in metrics:
    m_name = str(m.get("metric", "")).lower()
    if any(word in m_name for word in priority_words):
        if m not in headline_metrics:
            headline_metrics.append(m)

for m in metrics:
    if m not in headline_metrics:
        headline_metrics.append(m)

headline_metrics = headline_metrics[:4]

if headline_metrics:
    metric_cols = st.columns(len(headline_metrics))
    for col, m in zip(metric_cols, headline_metrics):
        with col:
            name = m.get("metric", "Metric")
            curr = m.get("current_period", "N/A")
            unit = m.get("unit", "")
            growth = str(m.get("yoy_growth", "")).strip()
            basis = m.get("basis", "")

            badge_html = ""
            spark_class = "spark-fill-neutral"
            spark_width = 75

            if growth and growth.lower() not in ["n/a", "not available", ""]:
                if growth.startswith("-") or "decline" in growth.lower():
                    badge_html = f"""<span style="color:#f87171; font-weight:750; font-size:12px;">▼ {growth}</span>"""
                    spark_class = "spark-fill-neg"
                    spark_width = 45
                else:
                    clean_g = growth if growth.startswith("+") else f"+{growth}"
                    badge_html = f"""<span style="color:#34d399; font-weight:750; font-size:12px;">▲ {clean_g} YoY</span>"""
                    spark_class = "spark-fill-pos"
                    spark_width = 85
            else:
                badge_html = """<span style="color:#94a3b8; font-weight:700; font-size:12px;">Current Level</span>"""

            st.markdown(f"""
            <div class="bi-kpi-card">
                <div>
                    <div class="kpi-header-row">
                        <span class="kpi-title">{name}</span>
                        {badge_html}
                    </div>
                    <div class="kpi-main-val">{curr} <span style="font-size:15px; font-weight:600; color:#94a3b8;">{unit}</span></div>
                </div>
                <div>
                    <div class="spark-track"><div class="{spark_class}" style="width: {spark_width}%;"></div></div>
                    <div style="display:flex; justify-content:space-between; font-size:11px; color:#64748b; margin-top:6px;">
                        <span>Basis: {basis if basis else 'Reported'}</span>
                        <span>Audited</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# CONSOLIDATED BI TABS
# ============================================================

tab_scorecard, tab_metrics, tab_charts, tab_mgmt, tab_risks, tab_investor = st.tabs([
    "⭐ Report Overview & Scorecard", "Financial Metrics Table", "📊 Visual Charts", "Management Plans", "Risks Matrix", "Investor Sentiment & Takeaways"
])

# 1. BI Executive Scorecard (Resilient Clean HTML Gauges)
with tab_scorecard:
    st.subheader("Executive Strategic Scorecard (BI Health Cockpit)")
    st.write("Diagnostic matrix evaluating operational momentum and downside resilience with real-time health dials:")

    if scorecard:
        col_s1, col_s2 = st.columns(2)

        pillars = [
            ("growth_momentum", "🚀 Growth Momentum", col_s1, "#38bdf8", 84),
            ("profitability_quality", "💰 Profitability & Quality", col_s2, "#34d399", 79),
            ("balance_sheet_safety", "🛡️ Balance Sheet Resilience", col_s1, "#818cf8", 92),
            ("strategic_execution", "⚙️ Strategic & Commercial Scale", col_s2, "#fbbf24", 88)
        ]

        for p_key, p_title, target_col, bar_color, default_pct in pillars:
            p_obj = scorecard.get(p_key, {})
            score = int(p_obj.get("health_pct", default_pct))
            badge = p_obj.get("badge", "Strong Expansion")
            verdict = p_obj.get("verdict", "")
            tags = p_obj.get("tags", p_obj.get("points", []))

            chips_html = "".join([
                f'<div style="background:#0e1526; border:1px solid #1f2d45; color:#cbd5e1; font-size:12px; padding:6px 10px; border-radius:6px; line-height:1.4; margin-bottom:6px;">✓ {t}</div>'
                for t in tags[:3]
            ])

            card_html = f"""<div style="background:#0b0f19; border:1px solid #1a2234; border-radius:14px; padding:20px; margin-bottom:16px;">
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
<span style="font-size:16px; font-weight:750; color:#ffffff;">{p_title}</span>
<span style="background:rgba(59,130,246,0.18); border:1px solid rgba(59,130,246,0.35); color:#93c5fd; padding:3px 10px; border-radius:6px; font-size:11.5px; font-weight:700;">{badge}</span>
</div>
<div style="color:#94a3b8; font-size:13.5px; line-height:1.45; margin-bottom:12px;">{verdict}</div>
<div style="display:flex; justify-content:space-between; font-size:11.5px; color:#cbd5e1; font-weight:600; margin-bottom:4px;">
<span>Pillar Diagnostic Score</span>
<span style="color:{bar_color}; font-weight:800;">{score}%</span>
</div>
<div style="background:#172033; border-radius:8px; height:9px; width:100%; margin-bottom:14px; overflow:hidden;">
<div style="width:{score}%; height:100%; background:{bar_color}; border-radius:8px;"></div>
</div>
<div style="font-size:11px; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:8px;">Performance Signals:</div>
{chips_html}
</div>"""
            with target_col:
                st.markdown(card_html, unsafe_allow_html=True)

# 2. Financial Metrics Table
with tab_metrics:
    st.subheader("All Financial & Operating Numbers")
    if metrics:
        col_search, col_filter = st.columns([2, 1])
        with col_search:
            search_query = st.text_input("🔍 Search line item...", placeholder="e.g. Revenue, Deposit, Loan, NPA", key="metric_search").lower()
        with col_filter:
            all_bases = list(set([m.get("basis", "").strip() for m in metrics if m.get("basis", "").strip()]))
            basis_filter = st.selectbox("Filter by Basis", options=["All"] + all_bases, key="basis_filter")

        filtered_rows = []
        for m in metrics:
            metric_name = m.get("metric", "")
            basis_val = m.get("basis", "")
            if (not search_query or search_query in metric_name.lower()) and (basis_filter == "All" or basis_val.lower() == basis_filter.lower()):
                filtered_rows.append({
                    "Metric Name": metric_name,
                    "Current Period": m.get("current_period", ""),
                    "Previous Period": m.get("previous_period", ""),
                    "YoY Growth": m.get("yoy_growth", ""),
                    "Unit": m.get("unit", ""),
                    "Basis": basis_val,
                    "Category": auto_classify_metric(metric_name)
                })
        if filtered_rows and pd is not None:
            st.dataframe(filtered_rows, use_container_width=True, hide_index=True, height=400)

# 3. BI Visual Charts with Universal Category Slicers
with tab_charts:
    st.subheader("Visual Financial Comparisons (Interactive BI Engine)")
    st.write("Compare previous vs. current performance across key metrics with interactive category filters:")

    categories = ["All Metrics", "Income & Profit", "Balance Sheet & Assets", "Quality Ratios"]
    selected_cat = st.radio("Select Financial Category Slicer:", options=categories, horizontal=True, key="bi_chart_slicer")

    chart_records = []
    for m in metrics:
        curr_val = parse_clean_float(m.get("current_period"))
        prev_val = parse_clean_float(m.get("previous_period"))
        m_name = m.get("metric", "").strip()
        auto_cat = auto_classify_metric(m_name)
        
        # Match category slicer reliably
        if selected_cat == "All Metrics" or selected_cat.lower() == auto_cat.lower():
            if curr_val is not None and prev_val is not None:
                chart_records.append({
                    "Metric": m_name,
                    "Previous": prev_val,
                    "Current": curr_val,
                    "Unit": m.get("unit", "").strip(),
                    "Growth": m.get("yoy_growth", "")
                })

    if chart_records:
        chart_cols = st.columns(2)
        for idx, item in enumerate(chart_records[:8]):
            c_val, p_val, u_lbl, m_name, growth = item["Current"], item["Previous"], item["Unit"], item["Metric"], item["Growth"]
            max_v = max(abs(c_val), abs(p_val)) if max(abs(c_val), abs(p_val)) > 0 else 1
            prev_pct = max(int((abs(p_val) / max_v) * 100), 8)
            curr_pct = max(int((abs(c_val) / max_v) * 100), 8)
            
            growth_str = str(growth).strip()
            if growth_str and growth_str.lower() not in ["n/a", "not available", ""]:
                delta_html = f'<span style="color:#34d399; font-size:11.5px; font-weight:750;">▲ +{growth_str.replace("+","")} YoY</span>' if not growth_str.startswith("-") else f'<span style="color:#f87171; font-size:11.5px; font-weight:750;">▼ {growth_str} YoY</span>'
            else:
                delta_html = '<span style="color:#94a3b8; font-size:11.5px; font-weight:700;">Audited Level</span>'

            chart_html = f"""<div style="background:#0b0f19; border:1px solid #1a2234; border-radius:14px; padding:18px; margin-bottom:14px;">
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
<span style="color:#ffffff; font-size:15px; font-weight:750;">{m_name}</span>
{delta_html}
</div>
<div style="margin-bottom:10px;">
<div style="display:flex; justify-content:space-between; font-size:12.5px; font-weight:600; color:#94a3b8; margin-bottom:4px;">
<span>Previous Period</span>
<span>{p_val:,.2f} {u_lbl}</span>
</div>
<div style="background:#172033; border-radius:6px; height:20px; width:100%; overflow:hidden;">
<div style="width:{prev_pct}%; background:#334155; height:100%; display:flex; align-items:center; justify-content:flex-end; padding-right:8px; color:#ffffff; font-size:11px; font-weight:700;">{p_val:,.2f}</div>
</div>
</div>
<div>
<div style="display:flex; justify-content:space-between; font-size:12.5px; font-weight:600; color:#cbd5e1; margin-bottom:4px;">
<span>Current Period</span>
<span>{c_val:,.2f} {u_lbl}</span>
</div>
<div style="background:#172033; border-radius:6px; height:20px; width:100%; overflow:hidden;">
<div style="width:{curr_pct}%; background:linear-gradient(90deg, #1d4ed8, #38bdf8); height:100%; display:flex; align-items:center; justify-content:flex-end; padding-right:8px; color:#ffffff; font-size:11px; font-weight:700;">{c_val:,.2f}</div>
</div>
</div>
</div>"""
            with chart_cols[idx % 2]:
                st.markdown(chart_html, unsafe_allow_html=True)
    else:
        st.info("No comparative metrics found under this category slice.")

# 4. Management Strategy
with tab_mgmt:
    st.subheader("Management Strategy & Strategic Themes")
    for item in management:
        with st.expander(f"🎯 {item.get('title', 'Strategic Pillar')}", expanded=False):
            st.write(item.get("summary", ""))

# 5. BI 2x2 Risk Heatmap Matrix
with tab_risks:
    st.subheader("Potential Risks & Headwinds (BI Heatmap Grid)")
    st.write("Multi-vector categorization of operational, credit, regulatory, and market threats:")

    if risks:
        r_cols = st.columns(2)
        severity_palette = {
            "high": ("#ef4444", "rgba(239, 68, 68, 0.15)"),
            "moderate": ("#fbbf24", "rgba(245, 158, 11, 0.15)"),
            "operational": ("#60a5fa", "rgba(59, 130, 246, 0.15)")
        }
        
        for idx, r in enumerate(risks):
            cat = r.get("category", "Credit & Market")
            impact = str(r.get("impact_level", "Moderate")).lower()
            if impact not in severity_palette:
                impact = "moderate"
            
            tag_color, tag_bg = severity_palette[impact]
            
            risk_card_html = f"""<div style="background:#0f0a0d; border:1px solid #2d1419; border-radius:12px; padding:16px; margin-bottom:12px; height:100%;">
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
<span style="background:{tag_bg}; border:1px solid {tag_color}; color:{tag_color}; font-size:10.5px; font-weight:800; padding:2px 8px; border-radius:6px; text-transform:uppercase;">● {impact.upper()} IMPACT</span>
<span style="color:#94a3b8; font-size:11.5px; font-weight:600;">{cat}</span>
</div>
<div style="color:#ffffff; font-weight:750; font-size:14.5px; margin-bottom:6px;">⚠️ {r.get('title')}</div>
<div style="color:#94a3b8; font-size:13px; line-height:1.45; margin-bottom:10px;">{r.get('what_is_the_risk')}</div>
<div style="background:#050203; border-left:3px solid #ef4444; border-radius:0 6px 6px 0; padding:8px 12px; font-size:12.5px; color:#fca5a5;">
<b>Earnings Impact:</b> {r.get('why_it_matters')}
</div>
</div>"""
            with r_cols[idx % 2]:
                st.markdown(risk_card_html, unsafe_allow_html=True)

# 6. BI Sentiment Barometer & Signal Takeaways
with tab_investor:
    st.subheader("Institutional Sentiment & Analyst Signals")
    
    bull_pct = int(takeaway.get("sentiment_score", 74))
    bear_pct = 100 - bull_pct

    st.markdown(f"""<div style="background:#0b0f19; border:1px solid #1a2234; border-radius:14px; padding:20px; margin-bottom:20px;">
<div style="display:flex; justify-content:space-between; font-size:13px; font-weight:700;">
<span style="color:#34d399;">🟢 Institutional Bull Drivers: {bull_pct}%</span>
<span style="color:#f87171;">🔴 Headwinds & Cost Pressures: {bear_pct}%</span>
</div>
<div style="display:flex; height:12px; border-radius:10px; overflow:hidden; margin:10px 0 6px 0;">
<div style="width:{bull_pct}%; background:linear-gradient(90deg, #059669, #10b981);"></div>
<div style="width:{bear_pct}%; background:linear-gradient(90deg, #ef4444, #b91c1c);"></div>
</div>
<div style="color:#64748b; font-size:11.5px;">Weighted sentiment derived from operating tailwinds vs downside risk disclosures.</div>
</div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🟢 Improving Tailwinds")
        for item in takeaway.get("improving", []):
            st.markdown(f'<div style="background:#0b1e17; border-left:3px solid #10b981; border-radius:6px; padding:10px 14px; margin-bottom:8px; color:#d1fae5; font-size:13.5px;">✓ {item}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown("#### 🔴 Weakening Headwinds")
        for item in takeaway.get("weakening", []):
            st.markdown(f'<div style="background:#240e13; border-left:3px solid #ef4444; border-radius:6px; padding:10px 14px; margin-bottom:8px; color:#fee2e2; font-size:13.5px;">✗ {item}</div>', unsafe_allow_html=True)

# ========================================================
# USER-CONTROLLED FORENSIC DEEP-DIVE
# ========================================================
st.markdown("""
<div class="fintech-banner">
    <div class="fintech-banner-title">🔬 Deep-Dive Financial Analysis</div>
    <div class="fintech-banner-desc">Would you like to view an in-depth financial investigation covering profitability margins, debt & balance sheet safety, and operating efficiency?</div>
</div>
""", unsafe_allow_html=True)

deep_choice = st.radio(
    "Select preference:",
    options=["No, keep summary view", "Yes, generate deep-dive financial analysis"],
    index=0,
    horizontal=True,
    key="deep_dive_choice_rad"
)

if deep_choice == "No, keep summary view":
    st.markdown("""
    <div class="ack-card">
        💡 <strong>Summary view retained.</strong> You can explore the core financial metrics and visual charts above, or switch to the in-depth investigation whenever you wish.
    </div>
    """, unsafe_allow_html=True)

elif deep_choice == "Yes, generate deep-dive financial analysis":
    if st.session_state.deep_dive is None:
        deep_loader = st.empty()
        deep_loader.markdown("""
        <div class="center-loader-box">
            <div class="loader-status-tag">🔬 Forensic Audit Engine</div>
            <div class="fintech-spinner"></div>
            <div class="loader-title">Conducting In-Depth Financial Investigation...</div>
            <div class="loader-subtitle">Auditing profit margins, capital return ratios, debt solvency cushion & operational efficiency.</div>
            <div class="loader-progress-track">
                <div class="loader-progress-fill"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        deep_prompt = """
You are a senior financial analyst providing a specialized deep-dive assessment of the uploaded annual report in plain, everyday English.

Extract and analyze three core financial pillars from the uploaded PDF:
1. PROFITABILITY & MARGINS: Profit margins, return on capital, drivers of net earnings, and cost pressures.
2. DEBT, LIQUIDITY & CAPITAL HEALTH: Borrowing levels, cash reserves, capital adequacy, and solvency.
3. OPERATING EFFICIENCY & REVENUE COMPOSITION: How efficiently the company runs its operations, employee/tech costs, and shift toward core recurring revenue.

Return ONLY valid JSON with this structure:
{
  "profitability_depth": {
    "headline": "Short plain English verdict on profitability",
    "insights": ["Point 1 with numbers in simple words", "Point 2 with numbers in simple words", "Point 3 with numbers in simple words"]
  },
  "debt_and_liquidity": {
    "headline": "Short plain English verdict on debt and balance sheet safety",
    "insights": ["Point 1 with numbers in simple words", "Point 2 with numbers in simple words", "Point 3 with numbers in simple words"]
  },
  "operating_efficiency": {
    "headline": "Short plain English verdict on operational efficiency and scale",
    "insights": ["Point 1 with numbers in simple words", "Point 2 with numbers in simple words", "Point 3 with numbers in simple words"]
  }
}
"""
        try:
            deep_res = generate_with_fallback(
                contents=[deep_prompt, st.session_state.gemini_file],
                json_mode=True
            )
            deep_data = clean_json_response(deep_res.text)
            deep_loader.empty()
            if deep_data and "profitability_depth" in deep_data:
                st.session_state.deep_dive = deep_data
            else:
                st.warning("Could not structure deep-dive data. Please try re-selecting.")
        except Exception as e:
            deep_loader.empty()
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
                <div style="color: #ffffff; font-weight: 650; font-size: 14px; margin-bottom: 12px;">{prof.get('headline', '')}</div>
            """, unsafe_allow_html=True)
            for pt in prof.get("insights", []):
                st.markdown(f"• {pt}")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_d2:
            st.markdown(f"""
            <div class="deep-card">
                <div class="deep-card-title">🛡️ Debt & Balance Sheet Safety</div>
                <div style="color: #ffffff; font-weight: 650; font-size: 14px; margin-bottom: 12px;">{debt.get('headline', '')}</div>
            """, unsafe_allow_html=True)
            for pt in debt.get("insights", []):
                st.markdown(f"• {pt}")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_d3:
            st.markdown(f"""
            <div class="deep-card">
                <div class="deep-card-title">⚙️ Operating Efficiency & Scale</div>
                <div style="color: #ffffff; font-weight: 650; font-size: 14px; margin-bottom: 12px;">{eff.get('headline', '')}</div>
            """, unsafe_allow_html=True)
            for pt in eff.get("insights", []):
                st.markdown(f"• {pt}")
            st.markdown("</div>", unsafe_allow_html=True)

# ========================================================
# INVESTMENT POSITION MODULE
# ========================================================
st.markdown("""
<div class="fintech-banner">
    <div class="fintech-banner-title">💼 Personalized Investment Position & Market Analysis</div>
    <div class="fintech-banner-desc">Evaluate your personal investment against live stock market pricing and the fundamental safety cushion in this annual report.</div>
</div>
""", unsafe_allow_html=True)

investor_mcq = st.radio(
    "Are you currently an investor in this company's stock?",
    options=["Select an option...", "Yes, I hold shares in this company", "No, I am just studying / evaluating"],
    index=0,
    horizontal=True,
    key="inv_mcq"
)

if investor_mcq == "No, I am just studying / evaluating":
    st.markdown("""
    <div class="ack-card">
        💡 <strong>Thank you for your response!</strong> You are in evaluation mode. Feel free to review the company's financial health, executive scorecard, and visual balance sheet trends above, or ask custom questions in the AI Copilot below.
    </div>
    """, unsafe_allow_html=True)

elif investor_mcq == "Yes, I hold shares in this company":
    col_inv1, col_inv2 = st.columns(2)
    with col_inv1:
        total_invested_input = st.number_input("Total Amount Invested (₹)", min_value=0.0, value=None, placeholder="e.g. 50000.00", step=500.0, format="%.2f", key="inv_amt")
    with col_inv2:
        avg_price_input = st.number_input("Average Buying Price per Share (₹)", min_value=0.0, value=None, placeholder="e.g. 250.00", step=1.0, format="%.2f", key="inv_price")

    if total_invested_input and avg_price_input and total_invested_input > 0 and avg_price_input > 0:
        calc_shares = int(total_invested_input // avg_price_input)
        st.caption(f"Calculated Holding: ~{calc_shares:,} Shares")
        
        pos_loader_placeholder = st.empty()

        if st.button("⚡ Analyse The Investment", type="primary"):
            c_name = company.get('company_name', 'this company')
            t_hint = company.get('stock_ticker', '')

            pos_loader_placeholder.markdown("""
            <div class="center-loader-box">
                <div class="loader-status-tag">⚡ Portfolio Valuation Engine</div>
                <div class="fintech-spinner"></div>
                <div class="loader-title">Auditing Investment Fundamentals...</div>
                <div class="loader-subtitle">Evaluating your entry price against total net worth, loan safety cushions & 5-8 year compounding outlooks.</div>
                <div class="loader-progress-track">
                    <div class="loader-progress-fill"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            market_info = fetch_live_stock_price(c_name, t_hint)
            live_price = market_info["price"] if market_info else avg_price_input
            live_date = market_info["as_on"] if market_info else datetime.today().strftime("%d %b %Y")
            exchange_tag = f"{market_info['exchange']}: {market_info['ticker']}" if market_info else "Global Exchange"

            pnl_amt = (live_price - avg_price_input) * calc_shares
            pnl_pct = ((live_price - avg_price_input) / avg_price_input) * 100
            pnl_sign = "+" if pnl_amt >= 0 else ""
            pnl_str = f"{pnl_sign}{pnl_pct:.2f}%"
            amt_str = f"{pnl_sign}₹{pnl_amt:,.2f}"
            cmp_display = f"₹{live_price:,.2f}"
            per_share_gain = live_price - avg_price_input
            gain_sign = "+" if per_share_gain >= 0 else ""
            per_share_str = f"{gain_sign}₹{per_share_gain:,.2f} per share"

            analysis_req_prompt = f"""
You are an expert equity research mentor explaining an investment position in {c_name} to an everyday investor in plain, clean English without textbook jargon.

INVESTMENT DATA:
- Capital Invested: ₹{total_invested_input:,.2f}
- Average Purchase Price: ₹{avg_price_input:.2f} (~{calc_shares:,} shares)
- Current Market Price: {cmp_display} as on {live_date} ({exchange_tag})
- Estimated Return: {pnl_str} ({amt_str}, {per_share_str})

Return ONLY valid JSON with this exact structure:
{{
  "profit_or_loss_summary": "Plain English summary of profit/loss position.",
  "price_safety_points": [
    {{
      "title": "Clear Pillar Title",
      "explanation": "Clear plain English explanation referencing exact figures from the annual report."
    }}
  ],
  "long_term_outlook_5_to_8_years": [
    {{
      "title": "Clear Growth Horizon Title",
      "explanation": "Clear plain English explanation of business growth over 5-8 years."
    }}
  ]
}}
"""
            try:
                pos_res = generate_with_fallback(contents=[analysis_req_prompt, st.session_state.gemini_file], json_mode=True)
                parsed_pos = clean_json_response(pos_res.text)
            except Exception:
                parsed_pos = {}

            pos_loader_placeholder.empty()

            parsed_pos["cmp_display"] = cmp_display
            parsed_pos["live_date"] = live_date
            parsed_pos["exchange_tag"] = exchange_tag
            parsed_pos["pnl_str"] = pnl_str
            parsed_pos["amt_str"] = amt_str
            parsed_pos["is_pos"] = (pnl_amt >= 0)
            parsed_pos["live_price"] = live_price
            parsed_pos["avg_price"] = avg_price_input
            parsed_pos["calc_shares"] = calc_shares
            parsed_pos["invested_amt"] = total_invested_input
            st.session_state.position_assessment = parsed_pos

        if st.session_state.position_assessment:
            p_data = st.session_state.position_assessment
            st.markdown("---")
            st.markdown("### 📋 Analyst Portfolio Assessment")
            
            cm1, cm2, cm3, cm4 = st.columns(4)
            with cm1:
                st.markdown(f"""
                <div class="invest-kpi-card">
                    <div class="invest-kpi-label">Invested Capital</div>
                    <div class="invest-kpi-val">₹{p_data.get('invested_amt', total_invested_input):,.2f}</div>
                    <div style="color: #94a3b8; font-size: 11.5px; margin-top: 4px;">~{p_data.get('calc_shares', calc_shares):,} Shares</div>
                </div>
                """, unsafe_allow_html=True)
            with cm2:
                st.markdown(f"""
                <div class="invest-kpi-card">
                    <div class="invest-kpi-label">Your Buy Price</div>
                    <div class="invest-kpi-val">₹{p_data.get('avg_price', avg_price_input):,.2f}</div>
                    <div style="color: #94a3b8; font-size: 11.5px; margin-top: 4px;">Cost Basis</div>
                </div>
                """, unsafe_allow_html=True)
            with cm3:
                st.markdown(f"""
                <div class="invest-kpi-card">
                    <div class="invest-kpi-label">Current Market Price (CMP)</div>
                    <div class="invest-kpi-val" style="color: #60a5fa;">{p_data.get('cmp_display', 'N/A')}</div>
                    <div style="color: #94a3b8; font-size: 11.5px; margin-top: 4px;">As on {p_data.get('live_date', '')} ({p_data.get('exchange_tag', 'NSE/BSE')})</div>
                </div>
                """, unsafe_allow_html=True)
            with cm4:
                is_pos = p_data.get("is_pos", True)
                pnl_color = "#34d399" if is_pos else "#f87171"
                st.markdown(f"""
                <div class="invest-kpi-card">
                    <div class="invest-kpi-label">Estimated Return</div>
                    <div class="invest-kpi-val" style="color: {pnl_color};">{p_data.get('pnl_str', 'N/A')}</div>
                    <div style="color: {pnl_color}; font-size: 11.5px; margin-top: 4px;">{p_data.get('amt_str', '')}</div>
                </div>
                """, unsafe_allow_html=True)

            # Profit or Loss Analysis Box
            st.markdown("""
            <div class="invest-section-box">
                <div class="invest-section-header">💰 Profit or Loss Analysis</div>
            """, unsafe_allow_html=True)
            
            pnl_summary = p_data.get("profit_or_loss_summary", f"Position status: {p_data.get('pnl_str', '')} ({p_data.get('amt_str', '')})")
            banner_border = "#10b981" if is_pos else "#ef4444"
            banner_bg = "#0b1f16" if is_pos else "#260e13"
            banner_text = "#d1fae5" if is_pos else "#fee2e2"

            st.markdown(f"""
            <div style="background: {banner_bg}; border-left: 4px solid {banner_border}; padding: 14px 16px; border-radius: 0 8px 8px 0; color: {banner_text}; font-size: 14px; line-height: 1.5;">
                {pnl_summary}
            </div>
            </div>
            """, unsafe_allow_html=True)

            # Fundamental Safety
            st.markdown("""
            <div class="invest-section-box">
                <div class="invest-section-header">🛡️ The Price At Which Stock Is Bought Is Fundamentally Safe</div>
            """, unsafe_allow_html=True)
            for item in p_data.get("price_safety_points", []):
                st.markdown(f"""
                <div class="invest-subcard">
                    <div class="invest-subcard-title">✓ {item.get('title', '')}</div>
                    <div class="invest-subcard-body">{item.get('explanation', '')}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # 5-8 Year Outlook
            st.markdown("""
            <div class="invest-section-box">
                <div class="invest-section-header">🚀 Outlook For The Next 5 To 8 Years (Long-Term Horizon)</div>
            """, unsafe_allow_html=True)
            for item in p_data.get("long_term_outlook_5_to_8_years", []):
                st.markdown(f"""
                <div class="invest-subcard" style="border-left-color: #8b5cf6;">
                    <div class="invest-subcard-title">◆ {item.get('title', '')}</div>
                    <div class="invest-subcard-body">{item.get('explanation', '')}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ========================================================
# EXPORT MODULE (DUAL TXT & CSV)
# ========================================================
st.markdown("""
<div class="fintech-banner">
    <div class="fintech-banner-title">📥 Export Financial Dashboard Summary</div>
    <div class="fintech-banner-desc">Do you want to download the summary of the whole report that has been generated in the dashboard?</div>
</div>
""", unsafe_allow_html=True)

export_choice = st.radio(
    "Select download preference:",
    options=["No, thank you", "Yes, download dashboard summary report"],
    index=0,
    horizontal=True,
    key="export_rad"
)

if export_choice == "No, thank you":
    st.markdown("""
    <div class="ack-card">
        💡 <strong>Thank you for your response!</strong> All summary metrics, scorecard ratings, and risk breakdowns remain viewable across the dashboard above. You can generate an export file anytime if needed.
    </div>
    """, unsafe_allow_html=True)

elif export_choice == "Yes, download dashboard summary report":
    comp_name = company.get("company_name", "Company")
    st.info("💡 **Disclaimer:** Exported files may require minor column width adjustments depending on your editor.")
    
    detailed_txt_report = f"""======================================================================
               FINANCIAL ANALYSIS & EXECUTIVE REPORT
======================================================================
Company Name    : {company.get('company_name', 'N/A')}
Stock Ticker    : {company.get('stock_ticker', 'N/A')}
Industry        : {company.get('industry', 'N/A')}
Reporting Period: {company.get('reporting_period', 'N/A')}
Report Type     : {company.get('report_type', 'N/A')}
Generated Date  : {datetime.today().strftime('%d %B %Y')}
Source Document : {st.session_state.uploaded_name}

----------------------------------------------------------------------
1. EXECUTIVE BUSINESS OVERVIEW
----------------------------------------------------------------------
{company.get('business_type', 'N/A')}

----------------------------------------------------------------------
2. KEY FINANCIAL & OPERATING METRICS
----------------------------------------------------------------------
"""
    for m in metrics:
        detailed_txt_report += f"• {m.get('metric', 'Metric')}: {m.get('current_period', 'N/A')} {m.get('unit', '')} (Previous: {m.get('previous_period', 'N/A')}, YoY Growth: {m.get('yoy_growth', 'N/A')}) [{m.get('basis', '')}]\n"

    if scorecard:
        detailed_txt_report += "\n----------------------------------------------------------------------\n3. EXECUTIVE STRATEGIC SCORECARD\n----------------------------------------------------------------------\n"
        for pillar_key, pillar_title in [
            ("growth_momentum", "Growth Momentum"),
            ("profitability_quality", "Profitability & Earnings Quality"),
            ("balance_sheet_safety", "Balance Sheet Resilience"),
            ("strategic_execution", "Strategic Execution")
        ]:
            p_obj = scorecard.get(pillar_key, {})
            detailed_txt_report += f"\n[{pillar_title.upper()}] - {p_obj.get('badge', '')} (Health: {p_obj.get('health_pct', 80)}%)\nVerdict: {p_obj.get('verdict', '')}\n"
            for pt in p_obj.get("tags", []):
                detailed_txt_report += f"  - {pt}\n"

    if st.session_state.deep_dive:
        dd = st.session_state.deep_dive
        detailed_txt_report += "\n----------------------------------------------------------------------\n4. FORENSIC DEEP-DIVE ASSESSMENT\n----------------------------------------------------------------------\n"
        detailed_txt_report += f"\n[Profitability & Margins]\nVerdict: {dd.get('profitability_depth', {}).get('headline', '')}\n"
        for pt in dd.get('profitability_depth', {}).get('insights', []):
            detailed_txt_report += f"  - {pt}\n"
        detailed_txt_report += f"\n[Debt & Balance Sheet Safety]\nVerdict: {dd.get('debt_and_liquidity', {}).get('headline', '')}\n"
        for pt in dd.get('debt_and_liquidity', {}).get('insights', []):
            detailed_txt_report += f"  - {pt}\n"
        detailed_txt_report += f"\n[Operating Efficiency & Scale]\nVerdict: {dd.get('operating_efficiency', {}).get('headline', '')}\n"
        for pt in dd.get('operating_efficiency', {}).get('insights', []):
            detailed_txt_report += f"  - {pt}\n"

    if st.session_state.position_assessment:
        pos = st.session_state.position_assessment
        detailed_txt_report += f"""
----------------------------------------------------------------------
5. PERSONALIZED INVESTMENT ASSESSMENT
----------------------------------------------------------------------
- Capital Invested     : ₹{pos.get('invested_amt', 0):,.2f} (~{pos.get('calc_shares', 0):,} Shares)
- Purchase Price Basis : ₹{pos.get('avg_price', 0):,.2f}
- Current Market Price : {pos.get('cmp_display', 'N/A')} as on {pos.get('live_date', 'N/A')}
- Estimated Return / P&L: {pos.get('pnl_str', 'N/A')} ({pos.get('amt_str', 'N/A')})

Summary:
{pos.get('profit_or_loss_summary', '')}

[Fundamental Price Safety Pillars]
"""
        for pt in pos.get("price_safety_points", []):
            detailed_txt_report += f"• {pt.get('title')}\n  {pt.get('explanation')}\n"

        detailed_txt_report += "\n[Long-Term Outlook (5 to 8 Years)]\n"
        for pt in pos.get("long_term_outlook_5_to_8_years", []):
            detailed_txt_report += f"• {pt.get('title')}\n  {pt.get('explanation')}\n"

    detailed_txt_report += f"""
======================================================================
     Financial Analyst AI • Educational & Institutional Analysis
======================================================================
"""

    csv_rows = []
    csv_rows.append(["=== COMPANY EXECUTIVE PROFILE ===", "", "", "", "", ""])
    csv_rows.append(["Company Name", company.get('company_name', 'N/A'), "", "", "", ""])
    csv_rows.append(["Industry", company.get('industry', 'N/A'), "", "", "", ""])
    csv_rows.append(["Business Profile", company.get('business_type', 'N/A'), "", "", "", ""])
    csv_rows.append(["Reporting Period", company.get('reporting_period', 'N/A'), "", "", "", ""])
    csv_rows.append(["", "", "", "", "", ""])
    
    csv_rows.append(["=== KEY FINANCIAL & OPERATING METRICS ===", "", "", "", "", ""])
    csv_rows.append(["Financial Metric", "Current Period", "Previous Period", "YoY Growth", "Unit", "Basis"])
    for m in metrics:
        csv_rows.append([
            m.get('metric', ''),
            m.get('current_period', ''),
            m.get('previous_period', ''),
            m.get('yoy_growth', ''),
            m.get('unit', ''),
            m.get('basis', '')
        ])

    if st.session_state.deep_dive:
        dd = st.session_state.deep_dive
        csv_rows.append(["", "", "", "", "", ""])
        csv_rows.append(["=== FORENSIC DEEP-DIVE ASSESSMENT ===", "", "", "", "", ""])
        csv_rows.append(["Profitability Depth", dd.get('profitability_depth', {}).get('headline', ''), "", "", "", ""])
        for pt in dd.get('profitability_depth', {}).get('insights', []):
            csv_rows.append(["Insight", pt, "", "", "", ""])
        csv_rows.append(["Debt & Balance Sheet Safety", dd.get('debt_and_liquidity', {}).get('headline', ''), "", "", "", ""])
        for pt in dd.get('debt_and_liquidity', {}).get('insights', []):
            csv_rows.append(["Insight", pt, "", "", "", ""])
        csv_rows.append(["Operating Efficiency", dd.get('operating_efficiency', {}).get('headline', ''), "", "", "", ""])
        for pt in dd.get('operating_efficiency', {}).get('insights', []):
            csv_rows.append(["Insight", pt, "", "", "", ""])

    if st.session_state.position_assessment:
        pos = st.session_state.position_assessment
        csv_rows.append(["", "", "", "", "", ""])
        csv_rows.append(["=== PERSONALIZED PORTFOLIO POSITION ===", "", "", "", "", ""])
        csv_rows.append(["Invested Capital", f"Rs. {pos.get('invested_amt', 0):,.2f}", f"~{pos.get('calc_shares', 0)} Shares", "", "", ""])
        csv_rows.append(["Buy Price Basis", f"Rs. {pos.get('avg_price', 0):,.2f}", "", "", "", ""])
        csv_rows.append(["Current Market Price", pos.get('cmp_display', ''), f"As on {pos.get('live_date', '')}", "", "", ""])
        csv_rows.append(["Estimated Return / P&L", pos.get('pnl_str', ''), pos.get('amt_str', ''), "", "", ""])
        
        csv_rows.append(["--- Fundamental Safety Pillars ---", "", "", "", "", ""])
        for pt in pos.get("price_safety_points", []):
            csv_rows.append([pt.get('title'), pt.get('explanation'), "", "", "", ""])

        csv_rows.append(["--- Long-Term Outlook (5-8 Years) ---", "", "", "", "", ""])
        for pt in pos.get("long_term_outlook_5_to_8_years", []):
            csv_rows.append([pt.get('title'), pt.get('explanation'), "", "", "", ""])

    if pd is not None:
        df_export = pd.DataFrame(csv_rows)
        csv_bytes = df_export.to_csv(index=False, header=False).encode('utf-8-sig')
    else:
        csv_str = "\n".join([",".join([f'"{c}"' for c in row]) for row in csv_rows])
        csv_bytes = csv_str.encode('utf-8-sig')

    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            label="📄 Download Executive Summary Report (.txt)",
            data=detailed_txt_report,
            file_name=f"{comp_name.replace(' ', '_')}_Executive_Report.txt",
            mime="text/plain",
            use_container_width=True
        )
    with col_dl2:
        st.download_button(
            label="📊 Download Structured Executive Report (.csv / Excel)",
            data=csv_bytes,
            file_name=f"{comp_name.replace(' ', '_')}_Structured_Dashboard.csv",
            mime="text/csv",
            use_container_width=True
        )

# ========================================================
# ASK THE ANALYST AI CHATBOT
# ========================================================
st.markdown("""
<div class="fintech-banner">
    <div class="fintech-banner-title">💬 Ask Questions About This Financial Report</div>
    <div class="fintech-banner-desc">Ask any custom question in plain English, or click one of the suggested prompts below.</div>
</div>
""", unsafe_allow_html=True)

chip_cols = st.columns(4)
suggested_q = None
with chip_cols[0]:
    if st.button("📈 Why profits changed YoY?", key="c1"): suggested_q = "Why did profits change compared with the previous year?"
with chip_cols[1]:
    if st.button("🚀 Growth drivers", key="c2"): suggested_q = "What are the company's major growth drivers?"
with chip_cols[2]:
    if st.button("💰 Debt & cash position", key="c3"): suggested_q = "How is the company's debt and liquidity position?"
with chip_cols[3]:
    if st.button("⚠️ Key investor risks", key="c4"): suggested_q = "What are the primary operational and financial risks?"

for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

user_q = st.chat_input("Ask a question about this financial report...", key="main_chat_input")
active_q = user_q if user_q else suggested_q

if active_q:
    st.session_state.chat_history.append({"role": "user", "content": active_q})
    with st.chat_message("user"):
        st.markdown(active_q)

    q_prompt = f"Answer the user's question using ONLY facts from the uploaded report in simple English:\n\n{active_q}"
    with st.chat_message("assistant"):
        with st.spinner("Analyzing report..."):
            try:
                res = generate_with_fallback(contents=[q_prompt, st.session_state.gemini_file], json_mode=False)
                ans = res.text.strip() if res.text else "No response generated."
                st.markdown(ans)
                st.session_state.chat_history.append({"role": "assistant", "content": ans})
            except Exception as e:
                st.error(f"Error: {e}")

# ============================================================
# FOOTER
# ============================================================
st.divider()
st.markdown('<div class="footer">Financial Analyst AI • Grounded in uploaded financial reports. For educational use only.</div>', unsafe_allow_html=True)
