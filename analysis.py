import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA

def add_moving_averages(df: pd.DataFrame, windows=(7, 30)) -> pd.DataFrame:
    df = df.copy()
    for w in windows:
        df[f"ma_{w}"] = df["price"].rolling(window=w).mean()
    return df

def add_rolling_volatility(df: pd.DataFrame, window: int = 30) -> pd.DataFrame:
    df = df.copy()
    df["rolling_volatility"] = df["return"].rolling(window=window).std()
    return df

def add_rsi(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """Add Relative Strength Index"""
    df = df.copy()
    delta = df["price"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))
    return df

def add_bollinger_bands(df: pd.DataFrame, window: int = 20, num_std: float = 2) -> pd.DataFrame:
    """Add Bollinger Bands"""
    df = df.copy()
    df["bb_middle"] = df["price"].rolling(window=window).mean()
    std = df["price"].rolling(window=window).std()
    df["bb_upper"] = df["bb_middle"] + (std * num_std)
    df["bb_lower"] = df["bb_middle"] - (std * num_std)
    return df

def add_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """Add MACD indicator"""
    df = df.copy()
    ema_fast = df["price"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["price"].ewm(span=slow, adjust=False).mean()
    df["macd"] = ema_fast - ema_slow
    df["macd_signal"] = df["macd"].ewm(span=signal, adjust=False).mean()
    df["macd_histogram"] = df["macd"] - df["macd_signal"]
    return df

def calculate_sharpe_ratio(df: pd.DataFrame, risk_free_rate: float = 0.02) -> float:
    """Calculate annualized Sharpe ratio"""
    returns = df["return"].dropna()
    if len(returns) == 0:
        return 0.0
    excess_returns = returns - (risk_free_rate / 365)
    if excess_returns.std() == 0:
        return 0.0
    return np.sqrt(365) * excess_returns.mean() / excess_returns.std()

def calculate_max_drawdown(df: pd.DataFrame) -> float:
    """Calculate maximum drawdown"""
    cumulative = (1 + df["return"]).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    return drawdown.min()

def train_arima_forecast(df: pd.DataFrame, steps: int = 30):
    """
    Simple ARIMA on price series. Returns forecast index and values.
    """
    series = df["price"].dropna()
    model = ARIMA(series, order=(2, 1, 2))  # you can tune this
    fitted = model.fit()

    forecast = fitted.get_forecast(steps=steps)
    forecast_index = pd.date_range(
        start=series.index[-1] + pd.Timedelta(days=1),
        periods=steps,
        freq="D"
    )
    forecast_df = pd.DataFrame({
        "price": forecast.predicted_mean.values,
        "lower": forecast.conf_int()["lower price"].values,
        "upper": forecast.conf_int()["upper price"].values
    }, index=forecast_index)
    return forecast_df
