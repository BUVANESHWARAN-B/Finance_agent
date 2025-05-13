from fastapi import FastAPI, HTTPException
from typing import Dict, Any
import requests
import os
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()  # Load environment variables from .env file (if it exists)
api_key = os.getenv("ALPHAVANTAGE_API_KEY")
if not api_key:
    raise ValueError("ALPHAVANTAGE_API_KEY not found in environment variables.")


def get_intraday_stock_data(symbol: str, interval: str = "5min") -> Dict[str, Any]:
    """Fetches intraday stock data for a given symbol and interval."""

    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&apikey={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        time_series_key = f"Time Series ({interval})"
        if data.get(time_series_key):
            latest_timestamp = max(data[time_series_key].keys())
            latest_data = data[time_series_key][latest_timestamp]
            price = latest_data.get("4. close")
            symbol_returned = data.get("Meta Data", {}).get("2. Symbol")
            if price and symbol_returned:
                return {"intraday_price": price, "symbol": symbol_returned, "timestamp": latest_timestamp, "interval": interval}
            else:
                return {"error": f"Could not retrieve intraday data for {symbol} ({interval})"}
        elif data.get("Note"):
            return {"error": f"Alpha Vantage API Note (Rate Limit?): {data['Note']}"}
        else:
            return {"error": f"Could not retrieve intraday data for {symbol} ({interval})" + str(data)}
    except requests.exceptions.RequestException as e:
        return {"error": f"Error fetching intraday data: {e}"}


@app.post("/get_data/")
async def get_agent_data(payload: Dict) -> Dict[str, Any]:
    """
    Endpoint to retrieve financial data based on the query.
    Now specifically for intraday stock data.

    Args:
        payload (Dict): JSON payload containing the query.

    Returns:
        Dict: A dictionary containing the intraday stock data or an error message.
    """
    query = payload.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="Query not provided")

    query = query.lower()
    words = query.split()

    if "intraday price" in query or "current price" in query:
        # Assuming the last word is the stock symbol
        symbol = words[-1].upper()
        intraday_data = get_intraday_stock_data(symbol)
        return intraday_data
    else:
        return {"response": f"API Agent cannot answer: '{query}'. Please ask for intraday stock price."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)