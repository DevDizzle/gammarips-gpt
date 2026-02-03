# GammaRips API

**GammaRips Intelligence** (formerly ProfitScout) is the backend engine for our AI-driven financial research. It serves "High Gamma" options setups, strict market structure analysis, and grounded financial data by unifying **Google Cloud Storage (GCS)** and **Google BigQuery**.

> **Mission:** Stop guessing. Access the **GammaRips Winners Dashboard**—a rigorous, data-driven pipeline that identifies explosive options setups verified against live Volatility/OI walls.

---

## 🚀 API Overview

This API is designed to be the "Truth Source" for the GammaRips GPT. It routes requests to the appropriate data engine based on the endpoint:

- **Live Market Data (BigQuery):** Powers the **Winners Dashboard**. Queries live signals for "High Gamma" setups (Trend + Vol + Quality).
- **Static Intelligence (GCS):** Powers deep-dive analysis. Serves pre-computed datasets like **recommendations**, **technicals**, and **news-analysis** stored as JSON/Markdown artifacts.

### Key Capabilities
*   **Strict Data Grounding:** Every signal is verified. No hallucinations.
*   **Clean Filtering:** Instantly filter for top-tier **CALL** or **PUT** setups based on proprietary quality scores.
*   **Market Structure:** Deep dives into Gamma Exposure and key support/resistance levels.

---

## 🛣️ How to Route

The API uses a dual-routing architecture to ensure speed and freshness:

### 1. Dynamic Signals (The "Hot" Path)
**Route:** `/v1/options-signals/*`  
**Source:** BigQuery (`options_analysis_signals` table)  
**Latency:** ~500ms - 2s  
**Use Case:** finding today's best trades.
- `GET /v1/options-signals/top`: Returns the "Winners Dashboard" — ranked list of highest probability setups.
- `GET /v1/options-signals/{ticker}`: Returns all signals for a specific ticker.

### 2. Static Artifacts (The "Cold" Path)
**Route:** `/v1/{dataset}/{id}`  
**Source:** GCS (`profit-scout-data` bucket)  
**Latency:** < 200ms (Cached)  
**Use Case:** Context, fundamental research, and "Why" analysis.
- The API automatically finds the "best artifact" for a given ticker by looking for the latest file in the corresponding folder.
- Supports `as_of=YYYY-MM-DD` to time-travel to past analysis.

---

## 📂 Folder Glossary (Dataset Mapping)

The API exposes the following datasets, which map 1:1 to folders in our Data Lake (GCS).

| Dataset Endpoint | GCS Folder | Description |
| :--- | :--- | :--- |
| `recommendations` | `/recommendations` | Analyst-grade summary & outlook (Buy/Sell/Hold). |
| `technicals` | `/technicals` | Key levels, RSI, MACD, and trend indicators. |
| `technicals-analysis` | `/technicals-analysis` | AI commentary on technical patterns. |
| `news-analysis` | `/headline-news` | Sentiment scoring of recent headlines. |
| `earnings-call-transcripts` | `/earnings-call-transcripts` | Raw text of earnings calls. |
| `transcript-analysis` | `/transcript-analysis` | AI-summarized takeaways from earnings calls. |
| `business-summaries` | `/business-summaries` | Company profile, segments, and competitors. |
| `financials-analysis` | `/financials-analysis` | Deep dive on Balance Sheet & Cash Flow health. |
| `fundamentals-analysis` | `/fundamentals-analysis` | Valuation metrics (PE, EV/EBITDA, Growth). |
| `sec-mda` | `/sec-mda` | Management Discussion & Analysis from 10-K/10-Q. |
| `sec-risk` | `/sec-risk` | Risk Factors section from SEC filings. |

---

## 🛠️ Local Development

### Prerequisites
- Python 3.11+
- Google Cloud Credentials (Authorized for `profitscout-lx6bb` project)

### Setup
1. **Clone & Install:**
   ```bash
   git clone <repo>
   cd gammarips-api
   pip install -r app/requirements.txt
   ```

2. **Environment Variables:**
   Create a `.env` file in the root:
   ```env
   GCP_PROJECT_ID=profitscout-lx6bb
   GCS_BUCKET_NAME=profit-scout-data
   BIGQUERY_DATASET=profit_scout
   WINNERS_DASHBOARD_TABLE=options_analysis_signals
   ```

3. **Run Server:**
   ```bash
   chmod +x app/run.sh
   ./app/run.sh
   ```
   Access documentation at: `http://localhost:8080/docs`

### Docker Build
```bash
docker build -t gammarips-api .
docker run -p 8080:8080 --env-file .env gammarips-api
```

---

## 🔒 Authentication (Coming Soon)
Currently open for internal use. Future versions will require an `X-API-Key` header verified against our user database.

### License
Educational use only. Not investment advice.