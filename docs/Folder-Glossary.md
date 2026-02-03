# GammaRips Data Glossary

This glossary describes the datasets available via the **GammaRips API**. Use it to choose the right dataset for a user’s question and map intent to API endpoints.

---

## 🚀 Live Market Intelligence (Dynamic)

### `options-signals` (BigQuery)
**What it contains:** Real-time "High Gamma" options setups sourced from the **Winners Dashboard**.
**Best for:** "What are the top trades today?", "Find me explosive Call options.", "Show me the market structure for NVDA."
**Key Endpoints:**
*   `/v1/options-signals/top`: Returns ranked list of highest probability setups (Trend + Vol + Quality).
*   `/v1/options-signals/{ticker}`: Returns all active signals for a specific ticker.
**Keys returned:** `ticker`, `option_type`, `strike`, `expiration`, `setup_quality_signal`, `stock_price_trend_signal`, `volatility_comparison_signal`, `weighted_score`.

---

## 📂 Static Analysis (GCS Data Lake)

### `recommendations/`
**What it contains:** The final, daily stock-level recommendation aggregating underlying analysis scores. Each ticker has a JSON with scores and a user-facing Markdown summary.  
**Best for:** “What’s the outlook on TSLA today?”, “Summarize the thesis for AAPL.”, “Bullish or bearish on GOOGL?”  
**Keys returned:** `outlook_signal`, `weighted_score`, `summary_md`, `artifact_url`.  
**ID format:** `{TICKER}.json` and `{TICKER}.md` (use `as_of` query param to select date).

### `news-analysis/`
**What it contains:** Short-term sentiment score and narrative analysis based on the day’s headlines.  
**Best for:** “Any notable headlines for NVDA today?”, “Quick take on today’s news for META?”  
**Keys returned:** `score` (0–1), `analysis` (paragraph).  
**Source data:** `headline-news/`

### `technicals-analysis/`
**What it contains:** Narrative score and analysis of the stock’s technical posture (e.g., momentum, trend).  
**Best for:** “Is momentum bullish or bearish for MSFT over the next 1–3 months?”  
**Keys returned:** `score` (0–1), `analysis` (paragraph).  
**Source data:** `technicals/`

### `transcript-analysis/`
**What it contains:** Summaries, key themes, and sentiment extracted from earnings call transcripts.  
**Best for:** “Summarize the latest earnings call for AMZN.”, “Key quotes/themes from AAPL’s last call?”  
**Keys returned:** `summary_md`, `key_themes_bullets`, `sentiment_score`, link to raw transcript.  
**Source data:** `earnings-call-transcripts/`

### `mda-analysis/`
**What it contains:** Analysis of SEC MD&A sections, focusing on forward-looking statements and risk.  
**Best for:** “Management’s outlook in the latest 10-K?”, “Key business drivers in MD&A?”  
**Keys returned:** `score`, `summary`, `identified_risks`.  
**Source data:** `sec-mda/`

### `fundamentals-analysis/` & `financials-analysis/`
**What they contain:** AI-generated analysis of financial health, valuation, and growth trends using statements, metrics, and ratios.  
**Best for:** “Valuation vs 5-year average?”, “Recent margin trends for TSLA?”, “Revenue growth outlook?”  
**Keys returned:** `score`, `analysis` (paragraph), `valuation_summary`, `growth_summary`.  
**Source data:** `financial-statements/`, `key-metrics/`, `ratios/`

### `business-summaries/`
**What it contains:** One-page overview of a company: segments, geographies, competitive moat.  
**Best for:** “What does Palantir do?”, “Business model for SNOW?”, “Main segments for Disney?”  
**Source data:** `sec-business/`

---

## 🧱 Raw Data & Inputs

### `headline-news/`
**What it contains:** Curated raw JSON of daily news headlines and snippets per ticker.  
**Best for:** Retrieving the exact headlines that fed into a given day’s `news-analysis/`.

### `technicals/`
**What it contains:** Time-series of technical indicators per ticker.  
**Best for:** “Key levels/SMAs/RSI for TSLA today?”, “MACD trend last 30 days.”  
**Common fields:** `SMA_50`, `SMA_200`, `EMA_21`, `MACD_12_26_9`, `RSI_14`, `ADX_14`, `52w_high`, `52w_low`.  
**Source data:** `prices/`

### `earnings-call-transcripts/`
**What it contains:** Raw/lightly formatted quarterly earnings call transcripts.  
**Best for:** “CEO’s commentary on margins?”, “Find quotes about ‘AI spending’.”

### `financial-statements/`, `key-metrics/`, `ratios/`
**What they contain:** Point-in-time tables for income statement, balance sheet, cash flow, KPIs (e.g., FCF), and valuation ratios (e.g., P/E).  
**Best for:** Sourcing raw numbers for fundamentals or custom calcs.

### `sec-business/`, `sec-mda/`, `sec-risk/`
**What they contain:** Raw text from specific SEC filing sections (10-K, 10-Q).  
**Best for:** Exact language for deep-dive analyses.

### `prices/`
**What it contains:** Raw daily OHLCV price data per ticker.  
**Best for:** Base data for technical and price-chart calculations.

---

## 📊 Visualization & UI Assets

### `price-chart-json/`
**What it contains:** Pre-formatted JSON payloads for charting libraries.  
**Best for:** “Show last 6 months of price candles for GOOGL.”  
**Source data:** `prices/`

---

## API Usage Hints (for the Agent)

- **Top Priority:** Check `/v1/options-signals` first for active trading ideas.
- Discover datasets: `GET /v1`  
- List items in a dataset: `GET /v1/{dataset}`  
- Retrieve latest for a ticker: `GET /v1/{dataset}/{symbol}?as_of=latest`  
- Prefer the most specific dataset that answers the question:
  - **Live Trade Ideas** → `options-signals`
  - key levels → `technicals` or `technicals-analysis`  
  - momentum/technicals → `technicals-analysis`  
  - broad thesis → `recommendations`  
  - earnings call context → `earnings-call-transcripts` + `transcript-analysis`  
- Always include the `as_of` timestamp and “Source: GammaRips Intelligence.”  
- Educational only; not investment advice.