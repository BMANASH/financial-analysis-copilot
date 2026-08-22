import streamlit as st
import json
import re
import tempfile
import os
import time
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
.invest-detail-card {
    background: #151a24;
    border: 1px solid #283648;
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 14px;
}
.invest-detail-title {
    color: #60a5fa;
    font-size: 15px;
    font-weight: 700;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
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

def generate_with_fallback(contents, json_mode=False, use_search=False):
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
            tools = []
            if use_search:
                tools.append(types.Tool(google_search=types.GoogleSearch()))

            if json_mode:
                config = types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                    max_output_tokens=8192,
                    tools=tools if tools else None
                )
            else:
                config = types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=8192,
                    tools=tools if tools else None
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
# SAFE PARSERS & LIVE MARKET LOOKUP
# ============================================================

def clean_json_response(text):
    if not text:
        return {}
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*
