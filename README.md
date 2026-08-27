# 📊 Financial Analyst AI

> **An AI-powered institutional financial analysis and research terminal designed to make complex corporate annual reports actionable and easy to understand.**

## 🌐 Live Application

👉 [Open Financial Analyst AI](https://financial-analysis-copilot-kg4okfskbz6ne86yft9ypx.streamlit.app/)

---

## 📌 Overview

**Financial Analyst AI** is an AI-powered financial analysis web application designed to help **finance students, aspiring equity research analysts, investors, and general users** understand complex corporate annual reports more efficiently.

Corporate annual reports can often contain hundreds of pages covering financial statements, business performance, management discussions, risks, subsidiaries, strategic developments, and other important disclosures. Finding the most important information manually can be time-consuming.

Financial Analyst AI uses **Google Gemini AI** to analyze an uploaded financial report and transform important information into a **structured, interactive, and visually organized financial dashboard**.

The objective is not simply to summarize a PDF, but to help users understand:
- How the company is performing
- What is driving its growth
- What is improving & what is weakening
- What risks the company faces
- What management is focusing on
- What investors should monitor

The application is designed with a strong focus on **financial analysis, simplicity, usability, and practical learning**.

---

# ✨ Key Features

## 📄 AI-Powered Financial Report Analysis
Users can upload a corporate annual report or financial PDF and allow the AI to analyze the document. The application identifies and organizes important information such as:
- Company overview & business model
- Key operating metrics & YoY growth
- Assets, liabilities, debt, and financial position
- Management commentary & strategic developments
- Major risks and headwinds

## 📊 Key Financial Metrics Dashboard
The application extracts important financial and operating metrics and presents them in a structured, color-coded "liquid glass" dashboard. Depending on the report, it highlights:
- Revenue, Total Income, & Profit After Tax (PAT)
- Earnings Per Share (EPS) & Operating Margins
- Loan Book, Disbursements, & Deposits (for Banks/NBFCs)
- Year-over-Year (YoY) growth tracking

## 📈 Executive Financial Scorecard
Evaluates the company's performance across four broad pillars:
1. **🚀 Growth Momentum:** Revenue, customer activity, and business expansion.
2. **💰 Profitability Quality:** Expenses, margins, and earnings quality.
3. **🏦 Balance Sheet Resilience:** Assets, debt, net worth, and capital position.
4. **🎯 Strategic Execution:** New products, partnerships, and management initiatives.

## 🌍 Live Web-Sourced Strategic Forecasting (3-5 Years)
Goes beyond the static PDF by utilizing **Live Google Search** via the Gemini engine. It traces real-time internet market trends, macroeconomic data, and sector tailwinds to generate a dynamic 3 to 5-year predictive projection. This includes:
- Projected 3Y CAGR Growth
- Operating Margin Outlook
- Risk-Adjusted Scenarios
- Bulleted rationales backed by both historical data and live web intelligence.

## 💼 Personalized Investment Valuation
Combines company-level financial analysis with your personal portfolio data. 
- Input your **Total Capital Invested** and **Average Purchase Price**.
- The app fetches **Live Market Pricing** (via yfinance) to calculate your unrealized P&L.
- Cross-references your entry price against the company's net worth to provide **Fundamental Valuation Safety** metrics and **Long-Term Compounding Horizons**.

## ⚠️ Risk & Headwind Assessment (Heatmap)
Visual categorization of operational, credit, regulatory, and market threats. Each risk is broken down into **What the risk is** and **Why it matters (Financial Implication)**, color-coded by severity (High, Medium, Low).

## 💬 Interactive Institutional Research Copilot
An AI-powered chat interface that allows users to interact directly with the uploaded financial report. Users can ask questions in plain English (e.g., *"Why did the company's profit increase?"* or *"What is driving revenue growth?"*) and receive accurate, bulleted answers grounded strictly in the audited disclosures.

## 📥 Export Professional Excel Model
With one click, users can export their entire financial analysis into a perfectly formatted, multi-tab **Microsoft Excel Workbook (.xlsx)**. The export includes:
- **Executive Summary Dashboard:** Styled KPI cards with colors and data tracking.
- **Financial Metrics Table:** Auto-wrapped, frozen-header data tables.
- **Risk Matrix:** Complete breakdown of business threats and implications.

---

# Who Is This For?

- **🎓 Finance Students:** Understand how real companies present their financial performance and how analysts interpret financial information.
- **📈 Aspiring Equity Research Analysts:** Practice identifying financial metrics, business developments, growth drivers, and risks from real annual reports.
- **💼 Investors & Retail Traders:** Organize large financial reports into a structured research format and evaluate personal portfolio safety.
- **📚 Beginners in Financial Analysis:** Make financial reports easier to approach by reducing the complexity of technical terminology.

---

# 🚀 How to Use

1. **Open the Application:** Visit [Financial Analyst AI](https://financial-analysis-copilot-kg4okfskbz6ne86yft9ypx.streamlit.app/)
2. **Upload a Financial Report:** Upload a supported company annual report (PDF).
3. **Generate the Analysis:** Wait for the AI to ingest, parse, and synthesize the hundreds of pages into a scorecard.
4. **Explore the Dashboards:** Review the Financial Metrics, Growth Charts, Risk Matrices, and Web-Sourced Forecasts.
5. **Run Portfolio Diagnostics:** Enter your share price to evaluate your live market valuation.
6. **Chat with the Copilot:** Ask custom questions about the report.
7. **Export Results:** Download your complete Professional Excel Model Workbook.

---

# 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| **Python** | Core programming language |
| **Streamlit** | Web application and interactive dashboard |
| **Google GenAI SDK** | Next-generation API for AI-powered financial analysis |
| **Google Search Tool** | Live web-tracing for 3-5 year compounding forecasts |
| **pandas** | Data processing and analysis |
| **openpyxl** | Advanced Microsoft Excel formatting, styling, and `.xlsx` generation |
| **yfinance** | Live market and stock price data integration |
| **pypdf** | PDF processing and ingestion |

---

# 🧠 How the Application Works

```text
Corporate Financial Report (PDF)
            ↓
    Document Ingestion & Parsing
            ↓
  Gemini AI Core (Financial Extraction)
            ↓
   Live Web Search (Market Tracing)
            ↓
 Financial Dashboard & Executive Scorecard
            ↓
  Live Portfolio Valuation & Copilot Q&A
            ↓
  Download Professional Excel (.xlsx) Model
