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
    import openpyxl
except ImportError:
    openpyxl = None

try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import plotly.graph_objects as go
    import plotly.express as px
except ImportError:
    go = None
    px = None

from google import genai
from google.genai import types

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Financial Analyst AI | Terminal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# INSTITUTIONAL LIQUID GLASS FINTECH COCKPIT THEME & CSS
# ============================================================

st.markdown("""
<style>
/* Base Theme with Financial Analytics Watermark Background */
.stApp {
    background-color: #06080e;
    background-image: 
        radial-gradient(circle at 15% 20%, rgba(30, 58, 138, 0.15) 0%, transparent 40%),
        radial-gradient(circle at 85% 80%, rgba(16, 185, 129, 0.08) 0%, transparent 40%),
        linear-gradient(rgba(6, 8, 14, 0.94), rgba(6, 8, 14, 0.94)),
        url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M10 10h80v80H10z' fill='none'/%3E%3Cpath d='M20 70l20-30 20 15 25-35' stroke='rgba(59, 130, 246, 0.04)' stroke-width='2' fill='none'/%3E%3Ctext x='15' y='30' fill='rgba(255,255,255,0.02)' font-family='monospace' font-size='10'%3EBI-ANALYTICS%3C/text%3E%3C/svg%3E");
    background-size: cover, cover, cover, 180px 180px;
    color: #f1f5f9;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
.block-container {
    max-width: 1450px;
    padding-top: 1.8rem;
    padding-bottom: 4rem;
}

/* Hide Default Streamlit Status Widget */
div[data-testid="stStatusWidget"] {
    display: none !important;
    visibility: hidden !important;
}

/* Landing Page Downward Sliding Bouncy Animation */
@keyframes landingBounce {
    0% {
        opacity: 0;
        transform: translateY(-60px) scale(0.98);
    }
    50% {
        opacity: 1;
        transform: translateY(12px) scale(1.01);
    }
    75% {
        transform: translateY(-6px) scale(0.995);
    }
    90% {
        transform: translateY(3px) scale(1.002);
    }
    100% {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

.landing-animate {
    animation: landingBounce 1.1s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
}

/* Liquid Glass Card Styling */
.liquid-glass-card {
    background: rgba(13, 20, 36, 0.65);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-top: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    transition: all 0.3s ease;
}

.liquid-glass-card:hover {
    border-color: rgba(59, 130, 246, 0.4);
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.6), 0 0 20px rgba(59, 130, 246, 0.15);
}

/* Electric Glowing Animations for Cards and Uploader */
@keyframes electricPulseBlue {
    0%, 100% {
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.3), inset 0 0 10px rgba(59, 130, 246, 0.1);
        border-color: rgba(59, 130, 246, 0.7);
    }
    50% {
        box-shadow: 0 0 30px rgba(96, 165, 250, 0.6), inset 0 0 20px rgba(96, 165, 250, 0.25);
        border-color: #60a5fa;
    }
}

@keyframes electricPulseGreen {
    0%, 100% {
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.3), inset 0 0 10px rgba(16, 185, 129, 0.1);
        border-color: rgba(16, 185, 129, 0.7);
    }
    50% {
        box-shadow: 0 0 30px rgba(52, 211, 153, 0.6), inset 0 0 20px rgba(52, 211, 153, 0.25);
        border-color: #34d399;
    }
}

@keyframes electricPulseYellow {
    0%, 100% {
        box-shadow: 0 0 15px rgba(245, 158, 11, 0.3), inset 0 0 10px rgba(245, 158, 11, 0.1);
        border-color: rgba(245, 158, 11, 0.7);
    }
    50% {
        box-shadow: 0 0 30px rgba(251, 191, 36, 0.6), inset 0 0 20px rgba(251, 191, 36, 0.25);
        border-color: #fbbf24;
    }
}

@keyframes electricPulseRed {
    0%, 100% {
        box-shadow: 0 0 15px rgba(239, 68, 68, 0.3), inset 0 0 10px rgba(239, 68, 68, 0.1);
        border-color: rgba(239, 68, 68, 0.7);
    }
    50% {
        box-shadow: 0 0 30px rgba(248, 113, 113, 0.6), inset 0 0 20px rgba(248, 113, 113, 0.25);
        border-color: #f87171;
    }
}

/* Streamlit Native File Uploader Electric Border Frame */
div[data-testid="stFileUploader"] {
    background: rgba(11, 17, 30, 0.85);
    backdrop-filter: blur(12px);
    border: 2px dashed #3b82f6;
    border-radius: 16px;
    padding: 16px;
    animation: electricPulseBlue 3s infinite ease-in-out;
}

/* Symmetrical Electric KPI Cards with 4 Performance Statuses */
.electric-kpi-card-blue {
    background: linear-gradient(145deg, #0b101c 0%, #060911 100%);
    border-radius: 16px;
    padding: 20px;
    height: 155px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    animation: electricPulseBlue 3.5s infinite ease-in-out;
    border: 2px solid #3b82f6;
}

.electric-kpi-card-green {
    background: linear-gradient(145deg, #071f16 0%, #040d0a 100%);
    border-radius: 16px;
    padding: 20px;
    height: 155px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    animation: electricPulseGreen 3.5s infinite ease-in-out;
    border: 2px solid #10b981;
}

.electric-kpi-card-yellow {
    background: linear-gradient(145deg, #221808 0%, #0d0a04 100%);
    border-radius: 16px;
    padding: 20px;
    height: 155px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    animation: electricPulseYellow 3.5s infinite ease-in-out;
    border: 2px solid #fbbf24;
}

.electric-kpi-card-red {
    background: linear-gradient(145deg, #240d12 0%, #0d0406 100%);
    border-radius: 16px;
    padding: 20px;
    height: 155px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    animation: electricPulseRed 3.5s infinite ease-in-out;
    border: 2px solid #ef4444;
}

/* Spinner & Dynamic Loaders */
@keyframes spinGlow {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@keyframes shimmerBar {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(200%); }
}

@keyframes pulseText {
    0%, 100% { opacity: 0.6; }
    50% { opacity: 1; }
}

.center-loader-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: rgba(13, 18, 30, 0.95) !important;
    backdrop-filter: blur(24px) !important;
    border: 1px solid rgba(59, 130, 246, 0.45) !important;
    border-radius: 18px !important;
    padding: 36px 32px !important;
    margin: 25px auto !important;
    text-align: center;
    max-width: 620px;
}
.fintech-spinner {
    width: 50px;
    height: 50px;
    border: 3.5px solid rgba(59, 130, 246, 0.15);
    border-top: 3.5px solid #60a5fa;
    border-right: 3.5px solid #3b82f6;
    border-radius: 50%;
    animation: spinGlow 0.85s linear infinite;
    margin-bottom: 16px;
}

.loader-progress-track {
    background: #151d2f;
    border-radius: 4px;
    height: 6px;
    width: 80%;
    margin: 20px auto 0 auto;
    overflow: hidden;
    position: relative;
}

.loader-progress-fill {
    background: linear-gradient(90deg, transparent, #3b82f6, #60a5fa, transparent);
    height: 100%;
    width: 50%;
    position: absolute;
    animation: shimmerBar 1.5s infinite linear;
}

.pulse-text {
    animation: pulseText 2s infinite ease-in-out;
}

/* Telemetry & Badges */
.telemetry-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 10px;
    margin-bottom: 20px;
    padding: 10px 14px;
    background: rgba(13, 18, 30, 0.65);
    border: 1px solid #1e293b;
    border-radius: 10px;
}
.telemetry-pill {
    background: #0a0e1a;
    border: 1px solid #23334d;
    color: #93c5fd;
    font-size: 12px;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 20px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

/* Typography & Banners */
.section-title {
    font-size: 21px;
    font-weight: 750;
    color: #f8fafc;
    margin-top: 24px;
    margin-bottom: 4px;
}
.section-description {
    color: #94a3b8;
    font-size: 13.5px;
    margin-bottom: 16px;
}
.fintech-banner {
    background: linear-gradient(135deg, #0c1220 0%, #060913 100%);
    border: 1px solid #1e293b;
    border-left: 4px solid #3b82f6;
    border-radius: 12px;
    padding: 18px 22px;
    margin-top: 30px;
    margin-bottom: 16px;
}
.fintech-banner-title {
    font-size: 18px;
    font-weight: 750;
    color: #ffffff;
    margin-bottom: 4px;
}
.fintech-banner-desc {
    font-size: 13px;
    color: #94a3b8;
}

/* Symmetrical Overview Cards */
.company-card {
    background: rgba(10, 14, 26, 0.85);
    border: 1px solid #1a2234;
    border-radius: 16px;
    padding: 18px;
    height: 155px;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    overflow-y: auto;
    margin-bottom: 10px;
    animation: electricPulseBlue 4s infinite ease-in-out;
}
.company-label {
    color: #fbbf24;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 6px;
    font-weight: 700;
}
.company-value {
    color: #f8fafc;
    font-size: 13.5px;
    font-weight: 550;
    line-height: 1.4;
}

/* BI KPI Cards */
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
    letter-spacing: 0.5px;
}
.kpi-main-val {
    color: #ffffff;
    font-size: 22px;
    font-weight: 800;
    margin: 4px 0;
}
.spark-track {
    background: #151d2f;
    border-radius: 4px;
    height: 5px;
    width: 100%;
    margin-top: 8px;
    overflow: hidden;
}

/* Chat Styling */
.chat-box-card {
    background: #0a0e1a;
    border: 1px solid #1a2234;
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 14px;
}
.chat-user-badge {
    color: #60a5fa;
    font-weight: 750;
    font-size: 13px;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.chat-bot-badge {
    color: #34d399;
    font-weight: 750;
    font-size: 13px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.chat-text {
    color: #e2e8f0;
    font-size: 13.5px;
    line-height: 1.6;
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
# SESSION STATE INITIALIZATION
# ============================================================

defaults = {
    "gemini_file": None,
    "uploaded_name": None,
    "analysis": None,
    "selected_model": None,
    "position_assessment": None,
    "chat_history": [],
    "processing_seconds": 0.0,
    "file_size_mb": 0.0,
    "forecast_data": None,
    "forecast_company": None
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
# ACTIVE GEMINI 3-SERIES MODELS
# ============================================================

ACTIVE_MODELS = [
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-pro-preview"
]

def generate_with_fallback(contents, json_mode=False, use_search=False):
    errors = []
    ordered = ACTIVE_MODELS.copy()
    if st.session_state.selected_model and st.session_state.selected_model in ordered:
        ordered.remove(st.session_state.selected_model)
        ordered.insert(0, st.session_state.selected_model)

    for model in ordered:
        for attempt in range(5):  # Exponential Backoff enabled: 5 Attempts max
            try:
                tools_list = [types.Tool(google_search=types.GoogleSearch())] if use_search else None
                
                # When search tool is enabled, response_mime_type cannot be application/json
                if json_mode and not use_search:
                    config = types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.1,
                        max_output_tokens=8192
                    )
                else:
                    config = types.GenerateContentConfig(
                        temperature=0.2,
                        max_output_tokens=8192,
                        tools=tools_list
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
                # Catch both Rate Limits (429) AND Overloaded Servers (503) seamlessly
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "503" in err_str or "UNAVAILABLE" in err_str:
                    sleep_time = 2.0 * (2 ** attempt)  # 2s, 4s, 8s, 16s...
                    time.sleep(sleep_time)
                    continue
                errors.append(f"{model}: {err_str}")
                break

    error_text = "\n\n".join(errors)
    raise Exception(f"API Rate limit reached or server is currently overloaded. Please try again in a few minutes.\n\n{error_text}")

# ============================================================
# SAFE PARSERS & UNIVERSAL STOCK LOOKUP
# ============================================================

def clean_json_response(text):
    if not text:
        return {}
    raw = text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*
