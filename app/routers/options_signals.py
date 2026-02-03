import logging
from fastapi import APIRouter, HTTPException, Query, Response, Depends
from typing import Optional, List, Dict, Any
from google.cloud import bigquery
from data.bigquery_client import BigQueryClient

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize BigQuery client
bq_client = BigQueryClient()

# --- Endpoints ---

@router.get(
    "/options-signals",
    summary="List distinct tickers for options signals",
    tags=["options-signals"],
)
async def list_options_signals(
    response: Response,
    run_date: Optional[str] = None,
    ticker: Optional[str] = None,
    option_type: Optional[str] = Query(None, enum=["CALL", "PUT"]),
):
    response.headers["Cache-Control"] = "public, max-age=300"
    
    # We use the raw client for this specific query as it's not a standard tool method
    client = bq_client.client
    table_id = bq_client._get_table_id("options_analysis_signals")
    
    effective_run_date = run_date if run_date else bq_client._get_latest_run_date("options_analysis_signals")
    
    query = f"SELECT DISTINCT ticker FROM `{table_id}`"
    where_clauses = ["run_date = @run_date"]
    params = [bigquery.ScalarQueryParameter("run_date", "STRING", effective_run_date)]
    
    if ticker:
        where_clauses.append("ticker LIKE @ticker")
        params.append(bigquery.ScalarQueryParameter("ticker", "STRING", f"{ticker.upper()}%"))
    if option_type:
        where_clauses.append("option_type = @option_type")
        params.append(bigquery.ScalarQueryParameter("option_type", "STRING", option_type))
        
    query += " WHERE " + " AND ".join(where_clauses) + " ORDER BY ticker"
    
    job_config = bigquery.QueryJobConfig(query_parameters=params)
    try:
        query_job = client.query(query, job_config=job_config)
        iterator = query_job.result()
        items = [{"id": row.ticker, "href": f"/v1/options-signals/{row.ticker}"} for row in iterator]
        return {"dataset": "options-signals", "items": items}
    except Exception as e:
        logger.error(f"Error querying options signals tickers: {e}")
        raise HTTPException(status_code=500, detail=f"Error querying BigQuery for distinct tickers: {e}")

@router.get(
    "/options-signals/top",
    summary="Get top-ranked options signals across all tickers",
    tags=["options-signals"],
)
async def get_top_options_signals(
    response: Response,
    as_of: str = "latest",
    option_type: Optional[str] = Query(None, enum=["CALL", "PUT"]),
    limit: int = 10,
):
    """
    Get today's top-ranked options signals (High Gamma).
    """
    response.headers["Cache-Control"] = "public, max-age=300"
    
    try:
        result = await bq_client.get_winners_dashboard(
            limit=limit,
            option_type=option_type,
            as_of=as_of
        )
        return {"dataset": "options-signals-top", "as_of": result.get("as_of"), "items": result.get("signals", [])}
    except Exception as e:
        logger.error(f"Error querying top options signals: {e}")
        raise HTTPException(status_code=500, detail=f"Error querying BigQuery for top signals: {e}")

@router.get(
    "/options-signals/{ticker}",
    summary="Get all options signals for a specific ticker",
    tags=["options-signals"],
)
async def get_ticker_options_signals(
    ticker: str,
    response: Response,
    as_of: str = "latest",
):
    """
    Retrieves all options signals for a specific ticker for a given date.
    """
    response.headers["Cache-Control"] = "public, max-age=120"
    
    # We can use get_winners_dashboard but filter for the ticker manually or via query
    # The BQ client doesn't explicitly support 'ticker' in get_winners_dashboard yet, 
    # so we might fallback to a raw query or add it. 
    # Looking at BQ client, it lacks a 'ticker' filter for winners dashboard.
    # So we use the raw query approach similar to list_options_signals to ensure compatibility.
    
    client = bq_client.client
    table_id = bq_client._get_table_id("options_analysis_signals")
    
    run_date_str = as_of
    if as_of == "latest":
        run_date_str = bq_client._get_latest_run_date("options_analysis_signals")
    
    query = f"SELECT * FROM `{table_id}` WHERE run_date = @run_date AND ticker = @ticker"
    params = [
        bigquery.ScalarQueryParameter("run_date", "STRING", run_date_str),
        bigquery.ScalarQueryParameter("ticker", "STRING", ticker.upper())
    ]
    
    job_config = bigquery.QueryJobConfig(query_parameters=params)
    
    try:
        query_job = client.query(query, job_config=job_config)
        results = [dict(row.items()) for row in query_job.result()]
        
        # Serialize dates
        for res in results:
            for k, v in res.items():
                if hasattr(v, "isoformat"):
                    res[k] = v.isoformat()
        
        if not results:
             raise HTTPException(status_code=404, detail=f"No options signals found for ticker {ticker.upper()} on {run_date_str}.")

        return {
            "dataset": "options-signals-item",
            "id": ticker.upper(),
            "as_of": run_date_str,
            "items": results
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error querying ticker signals for {ticker.upper()}: {e}")
        raise HTTPException(status_code=500, detail=f"Error querying BigQuery for ticker {ticker.upper()}: {e}")
