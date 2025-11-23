# Cryptocurrency Time Series Analytics Dashboard

An enhanced Streamlit dashboard for comprehensive cryptocurrency time series analysis, including technical indicators, forecasting, and risk metrics.

---

## 🚀 Features

### 1. UI & UX
- Modern, professional layout built with **Streamlit**
- Custom CSS styling for a clean dashboard look
- Color-coded KPI cards for price changes and risk metrics
- Clear separation of analysis views using tabs and sidebars

### 2. Price & Volume Analysis
- Historical price charts with selectable date ranges
- Line chart or candlestick chart options
- Volume chart with toggle
- Multiple moving averages (e.g., 7-day, 30-day)
- Bollinger Bands for volatility visualization

### 3. Technical Indicators
- **RSI (Relative Strength Index)** with overbought/oversold zones
- **MACD** with signal line and histogram
- **Bollinger Bands**
- Short-term and long-term moving averages

### 4. Returns & Risk Metrics
- Daily returns time-series
- Returns distribution (histogram)
- **Sharpe Ratio** (risk-adjusted return)
- **Maximum Drawdown**
- Rolling volatility analysis

### 5. Forecasting
- Time-series forecasting (e.g., ARIMA or similar models)
- Forecast horizon selection
- Confidence intervals for predictions
- Comparison of actual vs predicted prices

### 6. Interactive Tools
- Select cryptocurrency and date range from the sidebar
- Optional comparison mode between two coins
- Price alert thresholds (basic in-app notifications)
- Download buttons for:
  - Raw time-series data (CSV)
  - Summary statistics (CSV)

---

## 🧱 Project Structure

```text
crypto-time-series-app/
│
├── app.py              # Main Streamlit app entry point
├── analysis.py         # Time series analysis, indicators, forecasting logic
├── data_loader.py      # Functions to load/preprocess crypto data
├── ui_components.py    # Reusable Streamlit UI components
├── requirements.txt    # Python dependencies
├── Procfile            # Process definition for Railway deployment
└── README.md           # Project documentation
