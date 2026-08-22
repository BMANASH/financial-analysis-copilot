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
    page_title="Financial Analyst AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# INSTITUTIONAL FINTECH TERMINAL THEME & CSS
# ============================================================

st.markdown("""
<style>
.stApp {
    background: #07090e;
}
.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

@keyframes fadeInSlide {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.hero {
    background: linear-gradient(135deg, #0f172a 0%, #090d16 100%);
    border: 1px solid #1e293b;
    border-top: 3px solid #3b82f6;
    border-radius: 16px;
    padding: 32px 36px;
    margin-bottom: 20px;
    box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.7);
    animation: fadeInSlide 0.4s ease-out forwards;
}
.hero-title {
    font-size: 38px;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.15;
    margin-bottom: 8px;
    background: linear-gradient(90deg, #ffffff, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-subtitle {
    font-size: 15.5px;
    color: #94a3b8;
    line-height: 1.5;
    letter-spacing: 0.3px;
}
.section-title {
    font-size: 22px;
    font-weight: 750;
    color: #f8fafc;
    margin-top: 10px;
    margin-bottom: 4px;
}
.section-description {
    color: #94a3b8;
    font-size: 13.5px;
    margin-bottom: 18px;
}

/* Elegant Card Containers for Interactive Sections */
.card-container {
    background: #0e131f;
    border: 1px solid #1a2234;
    border-radius: 16px;
    padding: 28px;
    margin-top: 25px;
    margin-bottom: 25px;
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.6);
    animation: fadeInSlide 0.4s ease-out forwards;
    transition: all 0.3s ease;
}
.card-container:hover {
    border-color: #3b82f6;
    box-shadow: 0 14px 35px -10px rgba(59, 130, 246, 0.25);
}

/* Glassmorphic Fintech Cards with Hover Glow */
.company-card, .kpi-card, .scorecard-card, .risk-card, .invest-kpi-card, .invest-section-box, .chart-box {
    animation: fadeInSlide 0.4s ease-out forwards;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.company-card:hover, .kpi-card:hover, .scorecard-card:hover, .invest-kpi-card:hover, .invest-section-box:hover, .chart-box:hover {
    transform: translateY(-3px);
    border-color: #3b82f6 !important;
    box-shadow: 0 12px 30px -10px rgba(59, 130, 246, 0.3);
}

/* Symmetrical Company Overview Cards */
.company-card {
    background: #0e131f;
    border: 1px solid #1a2234;
    border-radius: 14px;
    padding: 16px;
    height: 145px;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    overflow-y: auto;
    margin-bottom: 10px;
}
.company-label {
    color: #fbbf24;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.9px;
    margin-bottom: 6px;
    font-weight: 700;
    flex-shrink: 0;
}
.company-value {
    color: #f8fafc;
    font-size: 13.5px;
    font-weight: 550;
    line-height: 1.45;
}

.kpi-card {
    background: #0e131f;
    border: 1px solid #1a2234;
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 10px;
    min-height: 145px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.kpi-label {
    color: #94a3b8;
    font-size: 12px;
    font-weight: 650;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}
.kpi-value {
    color: #ffffff;
    font-size: 26px;
    font-weight: 800;
    margin-top: 4px;
    margin-bottom: 6px;
}
.kpi-badge-pos {
    display: inline-block;
    background: rgba(16, 185, 129, 0.15);
    color: #34d399;
    font-size: 12px;
    font-weight: 700;
    padding: 3px 9px;
    border-radius: 6px;
    border: 1px solid rgba(16, 185, 129, 0.35);
}
.kpi-badge-neg {
    display: inline-block;
    background: rgba(239, 68, 68, 0.15);
    color: #f87171;
    font-size: 12px;
    font-weight: 700;
    padding: 3px 9px;
    border-radius: 6px;
    border: 1px solid rgba(239, 68, 68, 0.35);
}
.kpi-badge-neutral {
    display: inline-block;
    background: rgba(148, 163, 184, 0.15);
    color: #94a3b8;
    font-size: 12px;
    font-weight: 700;
    padding: 3px 9px;
    border-radius: 6px;
    border: 1px solid rgba(148, 163, 184, 0.3);
}
.kpi-basis {
    color: #64748b;
    font-size: 11px;
    margin-top: 6px;
    font-weight: 500;
}
.scorecard-card {
    background: #0e131f;
    border: 1px solid #1a2234;
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
    font-weight: 750;
}
.scorecard-badge {
    background: rgba(59, 130, 246, 0.2);
    color: #60a5fa;
    border: 1px solid rgba(59, 130, 246, 0.4);
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 750;
}
.scorecard-verdict {
    color: #cbd5e1;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 12px;
    line-height: 1.4;
}
.risk-card {
    background: #140d12;
    border: 1px solid #3b1b22;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 14px;
}
.risk-title {
    color: #fca5a5;
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 10px;
}
.risk-box {
    background: #0a0608;
    border-left: 3px solid #ef4444;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    margin-top: 10px;
}
.takeaway-improving {
    background: #0b1e17;
    border: 1px solid #133a2a;
    border-left: 4px solid #10b981;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
    color: #d1fae5;
    font-size: 14px;
    line-height: 1.5;
}
.takeaway-weakening {
    background: #240e13;
    border: 1px solid #481b25;
    border-left: 4px solid #ef4444;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
    color: #fee2e2;
    font-size: 14px;
    line-height: 1.5;
}
.takeaway-driver {
    background: #0d1b30;
    border: 1px solid #1b355e;
    border-left: 4px solid #3b82f6;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
    color: #dbeafe;
    font-size: 14px;
    line-height: 1.5;
}
.takeaway-watch {
    background: #231a0b;
    border: 1px solid #463417;
    border-left: 4px solid #f59e0b;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
    color: #fef3c7;
    font-size: 14px;
    line-height: 1.5;
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
    letter-spacing: 0.6px;
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
    display: flex;
    align-items: center;
    gap: 8px;
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
.price-gauge-card {
    background: #070a12;
    border: 1px solid #1a2234;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 14px;
}
.gauge-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
    font-size: 13.5px;
}
.chart-box {
    background: #070a12;
    border: 1px solid #1a2234;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 16px;
}
.chart-title {
    color: #ffffff;
    font-size: 15px;
    font-weight: 700;
    margin-bottom: 10px;
}
.vis-row {
    margin-bottom: 12px;
}
.vis-label {
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    font-weight: 600;
    color: #cbd5e1;
    margin-bottom: 4px;
}
.vis-track {
    background: #172033;
    border-radius: 6px;
    height: 22px;
    width: 100%;
    overflow: hidden;
}
.vis-fill-curr {
    background: linear-gradient(90deg, #1d4ed8, #3b82f6);
    height: 100%;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding-right: 8px;
    color: #ffffff;
    font-size: 11.5px;
    font-weight: 700;
}
.vis-fill-prev {
    background: #334155;
    height: 100%;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding-right: 8px;
    color: #ffffff;
    font-size: 11.5px;
    font-weight: 700;
}
.slicer-card {
    background: #0e131f;
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

<script>
document.addEventListener("DOMContentLoaded", function() {
    setInterval(() => {
        const inputs = window.parent.document.querySelectorAll('input');
        inputs.forEach(input => {
            input.setAttribute('autocomplete', 'new-password');
        });
    }, 1000);
});
</script>
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
                raise Exception("Professional Financial Analyst AI failed while processing the PDF.")

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
# HERO SECTION & MAIN BODY UPLOAD
# ============================================================

st.markdown("""
<div class="hero">
    <div class="hero-title">Financial Analyst AI</div>
    <div class="hero-subtitle">Institutional-grade AI financial analysis & portfolio intelligence from annual reports</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-title">Upload Financial Report</div>', unsafe_allow_html=True)
st.markdown('<div class="section-description">Upload your annual report or financial statement PDF below to automatically start the analysis.</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload Financial Report (PDF)",
    type=["pdf"],
    label_visibility="collapsed",
    key="main_pdf_uploader"
)

# ============================================================
# AUTOMATIC GENERATION ON UPLOAD
# ============================================================

if uploaded_file:
    is_new_file = (st.session_state.uploaded_name != uploaded_file.name)

    if is_new_file or st.session_state.analysis is None:
        with st.spinner("Processing PDF and running automatic financial analysis..."):
            try:
                gemini_file = upload_pdf_to_gemini(uploaded_file)
                st.session_state.gemini_file = gemini_file
                st.session_state.uploaded_name = uploaded_file.name

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
                response = generate_with_fallback(
                    contents=[analysis_prompt, gemini_file],
                    json_mode=True
                )
                data = clean_json_response(response.text)
                if data and "company_overview" in data:
                    st.session_state.analysis = data
                    st.session_state.deep_dive = None
                    st.session_state.position_assessment = None
                    st.session_state.chat_history = []
                    st.success("Financial analysis generated automatically!")
                    st.rerun()
                else:
                    st.error("Could not parse response. Please re-upload.")
            except Exception as e:
                st.error(f"Error processing document: {e}")

# ============================================================
# NO PDF STATE
# ============================================================

if not st.session_state.gemini_file or not st.session_state.analysis:
    st.info("👆 Upload an annual report PDF above to begin automatic financial analysis.")
    st.stop()

# ============================================================
# FULL WIDTH DASHBOARD DISPLAY
# ============================================================

data = st.session_state.analysis
company = data.get("company_overview", {})
metrics = data.get("key_metrics", [])
scorecard = data.get("investor_scorecard", {})
management = data.get("management_commentary", [])
risks = data.get("risks", {})
takeaway = data.get("analyst_takeaway", {})

# Optional Financial Glossary Expander at the top
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

# Company Overview - Symmetrical Cards
st.markdown('<div class="section-title">Company Overview</div>', unsafe_allow_html=True)
st.markdown('<div class="section-description">A quick snapshot of the company and what it does.</div>', unsafe_allow_html=True)

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

            st.markdown(f"""
            <div class="kpi-card">
                <div>
                    <div class="kpi-label">{m_name}</div>
                    <div class="kpi-value">{value_display}</div>
                    {badge_html}
                </div>
                {basis_html}
            </div>
            """, unsafe_allow_html=True)

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

with tab_metrics:
    st.subheader("All Financial & Operating Numbers")
    if metrics:
        col_search, col_filter = st.columns([2, 1])
        with col_search:
            search_query = st.text_input("🔍 Search line item...", placeholder="e.g. Revenue, Profit, Loan", key="metric_search").lower()
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
                    "Basis": basis_val
                })
        if filtered_rows and pd is not None:
            st.dataframe(filtered_rows, use_container_width=True, hide_index=True, height=400)

with tab_charts:
    st.subheader("Visual Financial Comparisons")
    st.write("Compare previous vs. current performance across key metrics at a glance:")
    
    chart_records = []
    for m in metrics:
        curr_val = parse_clean_float(m.get("current_period"))
        prev_val = parse_clean_float(m.get("previous_period"))
        if curr_val is not None and prev_val is not None:
            chart_records.append({
                "Metric": m.get("metric", "").strip(),
                "Previous": prev_val,
                "Current": curr_val,
                "Unit": m.get("unit", "").strip()
            })
    
    if chart_records:
        chart_cols = st.columns(2)
        for idx, item in enumerate(chart_records[:6]):
            c_val, p_val, u_lbl, m_name = item["Current"], item["Previous"], item["Unit"], item["Metric"]
            max_v = max(abs(c_val), abs(p_val)) if max(abs(c_val), abs(p_val)) > 0 else 1
            prev_pct = max(int((abs(p_val) / max_v) * 100), 10)
            curr_pct = max(int((abs(c_val) / max_v) * 100), 10)
            
            with chart_cols[idx % 2]:
                st.markdown(f"""
                <div class="chart-box">
                    <div class="chart-title">{m_name}</div>
                    <div class="vis-row">
                        <div class="vis-label"><span>Previous Period</span><span>{p_val:,.2f} {u_lbl}</span></div>
                        <div class="vis-track"><div class="vis-fill-prev" style="width: {prev_pct}%;">{p_val:,.2f}</div></div>
                    </div>
                    <div class="vis-row" style="margin-top:10px;">
                        <div class="vis-label"><span>Current Period</span><span>{c_val:,.2f} {u_lbl}</span></div>
                        <div class="vis-track"><div class="vis-fill-curr" style="width: {curr_pct}%;">{c_val:,.2f}</div></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

with tab_mgmt:
    st.subheader("Management Strategy & Outlook")
    for item in management:
        with st.expander(item.get("title", "Strategy"), expanded=False):
            st.write(item.get("summary", ""))

with tab_risks:
    st.subheader("Potential Risks & Challenges")
    for r in risks:
        st.markdown(f"""
        <div class="risk-card">
            <div class="risk-title">⚠️ {r.get('title')}</div>
            <div>{r.get('what_is_the_risk')}</div>
            <div class="risk-box"><b>Why it matters:</b> {r.get('why_it_matters')}</div>
        </div>""", unsafe_allow_html=True)

with tab_investor:
    st.subheader("Analyst Takeaway")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🟢 Improving")
        for item in takeaway.get("improving", []):
            st.markdown(f'<div class="takeaway-improving">✓ {item}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown("### 🔴 Weakening")
        for item in takeaway.get("weakening", []):
            st.markdown(f'<div class="takeaway-weakening">✗ {item}</div>', unsafe_allow_html=True)

# ========================================================
# INVESTMENT POSITION MODULE (WRAPPED IN CARD CONTAINER)
# ========================================================
st.markdown('<div class="card-container">', unsafe_allow_html=True)
st.markdown('<div class="section-title" style="margin-top:0;">💼 Personalized Investment Position & Market Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="section-description">Evaluate your personal investment against live stock market pricing and the financial health in this annual report.</div>', unsafe_allow_html=True)

investor_mcq = st.radio("Are you currently an investor in this company's stock?", options=["Select an option...", "Yes, I hold shares in this company", "No, I am just studying / evaluating"], index=0, horizontal=True, key="inv_mcq")

if investor_mcq == "Yes, I hold shares in this company":
    col_inv1, col_inv2 = st.columns(2)
    with col_inv1:
        total_invested_input = st.number_input("Total Amount Invested (₹)", min_value=0.0, value=None, placeholder="e.g. 50000.00", step=500.0, format="%.2f", key="inv_amt")
    with col_inv2:
        avg_price_input = st.number_input("Average Buying Price per Share (₹)", min_value=0.0, value=None, placeholder="e.g. 250.00", step=1.0, format="%.2f", key="inv_price")

    if total_invested_input and avg_price_input and total_invested_input > 0 and avg_price_input > 0:
        calc_shares = int(total_invested_input // avg_price_input)
        st.caption(f"Calculated Holding: ~{calc_shares:,} Shares")
        if st.button("⚡ Analyse The Investment", type="primary"):
            c_name = company.get('company_name', 'this company')
            t_hint = company.get('stock_ticker', '')
            market_info = fetch_live_stock_price(c_name, t_hint)
            live_price = market_info["price"] if market_info else 0.0
            live_date = market_info["as_on"] if market_info else datetime.today().strftime("%d %b %Y")
            exchange_tag = f"{market_info['exchange']}: {market_info['ticker']}" if market_info else "NSE / BSE"

            if live_price > 0:
                pnl_pct = ((live_price - avg_price_input) / avg_price_input) * 100
                pnl_amt = (live_price - avg_price_input) * calc_shares
                pnl_str = f"+{pnl_pct:.2f}%" if pnl_pct >= 0 else f"{pnl_pct:.2f}%"
                amt_str = f"+₹{pnl_amt:,.2f}" if pnl_amt >= 0 else f"-₹{abs(pnl_amt):,.2f}"
                cmp_display = f"₹{live_price:,.2f}"
            else:
                cmp_display = "Active Quote"
                pnl_str = "Active"
                amt_str = ""

            pos_prompt = f"Explain investment in {c_name}. Buy price: ₹{avg_price_input:.2f}, CMP: {cmp_display}, Return: {pnl_str}."
            try:
                pos_res = generate_with_fallback(contents=[pos_prompt, st.session_state.gemini_file], json_mode=True)
                parsed_pos = clean_json_response(pos_res.text)
            except Exception:
                parsed_pos = {}

            parsed_pos["cmp_display"] = cmp_display
            parsed_pos["live_date"] = live_date
            parsed_pos["exchange_tag"] = exchange_tag
            parsed_pos["pnl_str"] = pnl_str
            parsed_pos["amt_str"] = amt_str
            parsed_pos["is_pos"] = not str(pnl_str).startswith("-")
            parsed_pos["live_price"] = live_price
            parsed_pos["avg_price"] = avg_price_input
            st.session_state.position_assessment = parsed_pos

        if st.session_state.position_assessment:
            p_data = st.session_state.position_assessment
            st.markdown("### 📋 Analyst Portfolio Assessment")
            cm1, cm2, cm3, cm4 = st.columns(4)
            with cm1: st.metric("Invested Capital", f"₹{total_invested_input:,.2f}", f"~{calc_shares} Shares")
            with cm2: st.metric("Buy Price", f"₹{avg_price_input:,.2f}", "Cost Basis")
            with cm3: st.metric("Current Market Price", p_data.get('cmp_display', 'N/A'), f"As on {p_data.get('live_date','')}")
            with cm4: st.metric("Estimated Return", p_data.get('pnl_str', 'N/A'), p_data.get('amt_str', ''))
st.markdown('</div>', unsafe_allow_html=True)

# ========================================================
# EXPORT MODULE (WRAPPED IN CARD CONTAINER)
# ========================================================
st.markdown('<div class="card-container">', unsafe_allow_html=True)
st.markdown('<div class="section-title" style="margin-top:0;">📥 Export Financial Dashboard Summary</div>', unsafe_allow_html=True)
st.markdown('<div class="section-description">Do you want to download the summary of the whole report that has been generated in the dashboard?</div>', unsafe_allow_html=True)

export_choice = st.radio("Select download preference:", options=["No, thank you", "Yes, download dashboard summary report"], index=0, horizontal=True, key="export_rad")

if export_choice == "Yes, download dashboard summary report":
    comp_name = company.get("company_name", "Company")
    st.info("💡 **Disclaimer:** Exported files may require minor column width adjustments depending on your editor.")
    
    report_text = f"FINANCIAL ANALYSIS & INVESTMENT REPORT: {comp_name}\n" + "="*50 + f"\nGenerated: {datetime.today().strftime('%d %b %Y')}\n\n"
    for m in metrics:
        report_text += f"• {m.get('metric')}: {m.get('current_period')} {m.get('unit')} (YoY: {m.get('yoy_growth')})\n"

    st.download_button("📄 Download Executive Summary Report (.txt)", data=report_text, file_name=f"{comp_name.replace(' ', '_')}_Summary.txt", mime="text/plain", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ========================================================
# ASK THE ANALYST AI CHATBOT (WRAPPED IN CARD CONTAINER)
# ========================================================
st.markdown('<div class="card-container">', unsafe_allow_html=True)
st.markdown('<div class="section-title" style="margin-top:0;">💬 Ask Questions About This Financial Report</div>', unsafe_allow_html=True)
st.markdown('<div class="section-description">Ask any custom question in plain English, or click one of the suggested prompts below.</div>', unsafe_allow_html=True)

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
st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================
st.divider()
st.markdown('<div class="footer">Financial Analyst AI • Grounded in uploaded financial reports. For educational use only.</div>', unsafe_allow_html=True)
