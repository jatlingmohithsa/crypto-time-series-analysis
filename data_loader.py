import requests
import pandas as pd
from functools import lru_cache

BASE_URL = "https://api.coingecko.com/api/v3"

@lru_cache(maxsize=32)
def get_market_chart(coin_id: str, vs_currency: str = "usd", days: int = 90) -> pd.DataFrame:
    url = f"{BASE_URL}/coins/{coin_id}/market_chart"
    params = {"vs_currency": vs_currency, "days": days}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()

    # prices: [ [timestamp_ms, price], ... ]
    prices = data.get("prices", [])
    volumes = data.get("total_volumes", [])

    df_price = pd.DataFrame(prices, columns=["timestamp", "price"])
    df_vol = pd.DataFrame(volumes, columns=["timestamp", "volume"])

    df = df_price.merge(df_vol, on="timestamp")
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df = df.set_index("timestamp").sort_index()

    # compute daily returns
    df["return"] = df["price"].pct_change()
    return df

def get_coin_info(coin_id: str) -> dict:
    """Get current coin information including market cap, 24h change, etc."""
    url = f"{BASE_URL}/coins/{coin_id}"
    params = {"localization": "false", "tickers": "false", "community_data": "false", "developer_data": "false"}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()
