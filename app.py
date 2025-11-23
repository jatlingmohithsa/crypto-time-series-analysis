import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from data_loader import get_market_chart, get_coin_info
from analysis import (
    add_moving_averages, add_rolling_volatility, train_arima_forecast,
    add_rsi, add_bollinger_bands, add_macd, calculate_sharpe_ratio, calculate_max_drawdown
)
from ui_components import apply_custom_css, display_price_change, create_alert_box

# ----------------- PAGE CONFIG -----------------
# python -m streamlit run app.py
st.set_page_config(
    page_title="Crypto Time Series Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
apply_custom_css()

# ----------------- SIDEBAR -----------------
st.sidebar.title("⚙️ Controls")

# Coin selection
coin_options = {
    "Bitcoin (BTC)": "bitcoin",
    "Ethereum (ETH)": "ethereum",
    "Solana (SOL)": "solana",
    "Cardano (ADA)": "cardano",
    "Ripple (XRP)": "ripple",
    "Polkadot (DOT)": "polkadot",
    "Dogecoin (DOGE)": "dogecoin",
}

coin_label = st.sidebar.selectbox("Select cryptocurrency", list(coin_options.keys()))
coin_id = coin_options[coin_label]

# Comparison mode
st.sidebar.markdown("###  Comparison Mode")
enable_comparison = st.sidebar.checkbox("Compare with another coin", value=False)
compare_coin_id = None
if enable_comparison:
    compare_label = st.sidebar.selectbox("Compare with", [k for k in coin_options.keys() if k != coin_label])
    compare_coin_id = coin_options[compare_label]

# Time range
days = st.sidebar.select_slider("Lookback window (days)", options=[7, 30, 90, 180, 365], value=90)

# Chart options
st.sidebar.markdown("### 📈 Chart Options")
chart_type = st.sidebar.radio("Price chart type", ["Line", "Candlestick"], index=0)
show_ma = st.sidebar.checkbox("Show Moving Averages", value=True)
show_bb = st.sidebar.checkbox("Show Bollinger Bands", value=False)
show_volume = st.sidebar.checkbox("Show Volume", value=True)

# Technical indicators
st.sidebar.markdown("### 🔧 Technical Indicators")
show_rsi = st.sidebar.checkbox("Show RSI", value=True)
show_macd = st.sidebar.checkbox("Show MACD", value=True)
show_volatility = st.sidebar.checkbox("Show Rolling Volatility", value=False)

# Forecasting
st.sidebar.markdown("### 🔮 Forecasting")
do_forecast = st.sidebar.checkbox("Run ARIMA Forecast", value=True)
forecast_horizon = 30
if do_forecast:
    forecast_horizon = st.sidebar.slider("Forecast horizon (days)", 7, 90, 30)

# Price alerts
st.sidebar.markdown("### 🔔 Price Alerts")
enable_alerts = st.sidebar.checkbox("Enable price alerts", value=False)
alert_price = None
if enable_alerts:
    alert_price = st.sidebar.number_input("Alert when price reaches (USD)", min_value=0.0, value=0.0, step=100.0)

st.sidebar.markdown("---")
st.sidebar.caption("Built with Streamlit • Data from CoinGecko")

# ----------------- DATA LOADING -----------------
with st.spinner("Loading data..."):
    df = get_market_chart(coin_id=coin_id, days=days)
    df = add_moving_averages(df)
    df = add_rolling_volatility(df)
    df = add_rsi(df)
    df = add_bollinger_bands(df)
    df = add_macd(df)
    
    # Get coin info for additional metrics
    try:
        coin_info = get_coin_info(coin_id)
    except:
        coin_info = {}
    
    # Load comparison data if enabled
    df_compare = None
    if enable_comparison and compare_coin_id:
        df_compare = get_market_chart(coin_id=compare_coin_id, days=days)

# ----------------- HEADER -----------------
col_title, col_logo = st.columns([4, 1])
with col_title:
    st.title(" Cryptocurrency Time Series Analysis")
    st.subheader(f"{coin_label}")

# Display 24h change if available
if coin_info and "market_data" in coin_info:
    change_24h = coin_info["market_data"].get("price_change_percentage_24h", 0)
    change_7d = coin_info["market_data"].get("price_change_percentage_7d", 0)
    change_30d = coin_info["market_data"].get("price_change_percentage_30d", 0)
    
    st.markdown(
        f"**24h:** {display_price_change(change_24h)} | "
        f"**7d:** {display_price_change(change_7d)} | "
        f"**30d:** {display_price_change(change_30d)}",
        unsafe_allow_html=True
    )

# ----------------- PRICE ALERTS -----------------
if enable_alerts and alert_price and alert_price > 0:
    current_price = df["price"].iloc[-1]
    if current_price >= alert_price:
        create_alert_box(f"🔔 Alert: {coin_label} has reached ${current_price:,.2f}!", "success")
    elif current_price < alert_price * 0.95:
        create_alert_box(f"⚠️ Price is ${current_price:,.2f}, still below alert threshold of ${alert_price:,.2f}", "warning")

# ----------------- METRICS ROW -----------------
col1, col2, col3, col4, col5 = st.columns(5)

current_price = df["price"].iloc[-1]
max_price = df["price"].max()
min_price = df["price"].min()
total_return = (df["price"].iloc[-1] / df["price"].iloc[0]) - 1
sharpe = calculate_sharpe_ratio(df)

col1.metric("Current Price", f"${current_price:,.2f}")
col2.metric("Period High", f"${max_price:,.2f}")
col3.metric("Period Low", f"${min_price:,.2f}")
col4.metric("Total Return", f"{total_return*100:.2f}%", delta=f"{total_return*100:.2f}%")
col5.metric("Sharpe Ratio", f"{sharpe:.2f}")

# Additional metrics row
col1, col2, col3, col4 = st.columns(4)

avg_volume = df["volume"].mean()
max_drawdown = calculate_max_drawdown(df)
current_rsi = df["rsi"].iloc[-1] if not pd.isna(df["rsi"].iloc[-1]) else 0

col1.metric("Avg Daily Volume", f"${avg_volume:,.0f}")
col2.metric("Max Drawdown", f"{max_drawdown*100:.2f}%")
col3.metric("Current RSI", f"{current_rsi:.1f}")

if coin_info and "market_data" in coin_info:
    market_cap = coin_info["market_data"].get("market_cap", {}).get("usd", 0)
    col4.metric("Market Cap", f"${market_cap/1e9:.2f}B")

st.markdown("---")

# ----------------- LAYOUT WITH TABS -----------------
tab1, tab2, tab3, tab4 = st.tabs(["📈 Price & Volume", "📉 Technical Indicators", " Returns & Statistics", "🔮 Forecasting"])

# ---- TAB 1: Price & Volume ----
with tab1:
    st.subheader("Price Time Series")

    # Create price chart based on type
    if chart_type == "Candlestick" and days <= 90:
        # Resample to daily for candlestick
        df_daily = df.resample('D').agg({
            'price': ['first', 'max', 'min', 'last'],
            'volume': 'sum'
        }).dropna()
        df_daily.columns = ['open', 'high', 'low', 'close', 'volume']
        
        fig_price = go.Figure(data=[go.Candlestick(
            x=df_daily.index,
            open=df_daily['open'],
            high=df_daily['high'],
            low=df_daily['low'],
            close=df_daily['close'],
            name=coin_label
        )])
        fig_price.update_layout(title=f"{coin_label} Price (USD) - Candlestick", xaxis_rangeslider_visible=False)
    else:
        fig_price = go.Figure()
        fig_price.add_trace(go.Scatter(
            x=df.index,
            y=df["price"],
            mode="lines",
            name=coin_label,
            line=dict(color="#1f77b4", width=2)
        ))
        
        # Add comparison coin
        if enable_comparison and df_compare is not None:
            # Normalize for comparison
            df_compare_norm = df_compare.copy()
            df_compare_norm["price_norm"] = (df_compare_norm["price"] / df_compare_norm["price"].iloc[0]) * df["price"].iloc[0]
            fig_price.add_trace(go.Scatter(
                x=df_compare_norm.index,
                y=df_compare_norm["price_norm"],
                mode="lines",
                name=compare_label,
                line=dict(color="#ff7f0e", width=2, dash="dash")
            ))
        
        # Add moving averages
        if show_ma:
            for w, color in [(7, "#2ca02c"), (30, "#d62728")]:
                ma_col = f"ma_{w}"
                if ma_col in df.columns:
                    fig_price.add_trace(go.Scatter(
                        x=df.index,
                        y=df[ma_col],
                        mode="lines",
                        name=f"{w}-day MA",
                        line=dict(color=color, width=1.5, dash="dot")
                    ))
        
        # Add Bollinger Bands
        if show_bb and "bb_upper" in df.columns:
            fig_price.add_trace(go.Scatter(
                x=df.index,
                y=df["bb_upper"],
                mode="lines",
                name="BB Upper",
                line=dict(color="rgba(128,128,128,0.3)", width=1)
            ))
            fig_price.add_trace(go.Scatter(
                x=df.index,
                y=df["bb_lower"],
                mode="lines",
                name="BB Lower",
                line=dict(color="rgba(128,128,128,0.3)", width=1),
                fill='tonexty',
                fillcolor='rgba(128,128,128,0.1)'
            ))
        
        fig_price.update_layout(
            title=f"{coin_label} Price (USD)",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            hovermode="x unified",
            height=500
        )

    st.plotly_chart(fig_price, use_container_width=True)

    if show_volume:
        st.subheader("Volume Traded")
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Bar(
            x=df.index,
            y=df["volume"],
            name="Volume",
            marker_color="#17becf"
        ))
        fig_vol.update_layout(
            title=f"{coin_label} Trading Volume",
            xaxis_title="Date",
            yaxis_title="Volume (USD)",
            height=300
        )
        st.plotly_chart(fig_vol, use_container_width=True)

# ---- TAB 2: Technical Indicators ----
with tab2:
    if show_rsi:
        st.subheader("Relative Strength Index (RSI)")
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(
            x=df.index,
            y=df["rsi"],
            mode="lines",
            name="RSI",
            line=dict(color="#9467bd", width=2)
        ))
        # Add overbought/oversold lines
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
        fig_rsi.update_layout(
            title=f"{coin_label} RSI (14-day)",
            xaxis_title="Date",
            yaxis_title="RSI",
            height=350
        )
        st.plotly_chart(fig_rsi, use_container_width=True)
        
        current_rsi = df["rsi"].iloc[-1]
        if current_rsi > 70:
            create_alert_box(f"⚠️ RSI is {current_rsi:.1f} - Potentially overbought", "warning")
        elif current_rsi < 30:
            create_alert_box(f"⚠️ RSI is {current_rsi:.1f} - Potentially oversold", "warning")
    
    if show_macd:
        st.subheader("MACD (Moving Average Convergence Divergence)")
        fig_macd = make_subplots(rows=2, cols=1, row_heights=[0.7, 0.3], vertical_spacing=0.05)
        
        fig_macd.add_trace(go.Scatter(
            x=df.index,
            y=df["macd"],
            mode="lines",
            name="MACD",
            line=dict(color="#1f77b4", width=2)
        ), row=1, col=1)
        
        fig_macd.add_trace(go.Scatter(
            x=df.index,
            y=df["macd_signal"],
            mode="lines",
            name="Signal",
            line=dict(color="#ff7f0e", width=2)
        ), row=1, col=1)
        
        colors = ['green' if val >= 0 else 'red' for val in df["macd_histogram"]]
        fig_macd.add_trace(go.Bar(
            x=df.index,
            y=df["macd_histogram"],
            name="Histogram",
            marker_color=colors
        ), row=2, col=1)
        
        fig_macd.update_layout(
            title=f"{coin_label} MACD",
            height=500,
            showlegend=True
        )
        st.plotly_chart(fig_macd, use_container_width=True)
    
    if not show_rsi and not show_macd:
        st.info("Enable RSI or MACD in the sidebar to view technical indicators")

# ---- TAB 3: Returns & Statistics ----
with tab3:
    st.subheader("Daily Returns")

    df_returns = df.dropna(subset=["return"])
    fig_ret = go.Figure()
    colors = ['green' if val >= 0 else 'red' for val in df_returns["return"]]
    fig_ret.add_trace(go.Bar(
        x=df_returns.index,
        y=df_returns["return"],
        marker_color=colors,
        name="Daily Return"
    ))
    fig_ret.update_layout(
        title=f"{coin_label} Daily Returns",
        xaxis_title="Date",
        yaxis_title="Return (%)",
        height=400
    )
    st.plotly_chart(fig_ret, use_container_width=True)
    
    # Returns distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Returns Distribution")
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=df_returns["return"],
            nbinsx=50,
            name="Returns",
            marker_color="#1f77b4"
        ))
        fig_hist.update_layout(
            title="Distribution of Daily Returns",
            xaxis_title="Return",
            yaxis_title="Frequency",
            height=350
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        st.subheader("Key Statistics")
        stats_df = pd.DataFrame({
            "Metric": ["Mean Return", "Std Dev", "Skewness", "Kurtosis", "Min Return", "Max Return"],
            "Value": [
                f"{df_returns['return'].mean()*100:.4f}%",
                f"{df_returns['return'].std()*100:.4f}%",
                f"{df_returns['return'].skew():.4f}",
                f"{df_returns['return'].kurtosis():.4f}",
                f"{df_returns['return'].min()*100:.2f}%",
                f"{df_returns['return'].max()*100:.2f}%"
            ]
        })
        st.dataframe(stats_df, use_container_width=True, hide_index=True)

    if show_volatility:
        st.subheader("Rolling Volatility (30-day)")
        df_vol = df.dropna(subset=["rolling_volatility"])
        fig_vola = go.Figure()
        fig_vola.add_trace(go.Scatter(
            x=df_vol.index,
            y=df_vol["rolling_volatility"],
            mode="lines",
            name="Volatility",
            line=dict(color="#e377c2", width=2),
            fill='tozeroy',
            fillcolor='rgba(227,119,194,0.2)'
        ))
        fig_vola.update_layout(
            title=f"{coin_label} Rolling Volatility",
            xaxis_title="Date",
            yaxis_title="Volatility",
            height=350
        )
        st.plotly_chart(fig_vola, use_container_width=True)

# ---- TAB 4: Forecasting ----
with tab4:
    st.subheader("ARIMA-based Price Forecast")

    if not do_forecast:
        st.info("Enable **Run ARIMA Forecast** in the sidebar to generate a forecast.")
    else:
        with st.spinner("Training ARIMA model and generating forecast..."):
            forecast_df = train_arima_forecast(df, steps=forecast_horizon)

        # Create forecast visualization
        fig_forecast = go.Figure()
        
        # Historical prices
        fig_forecast.add_trace(go.Scatter(
            x=df.index,
            y=df["price"],
            mode="lines",
            name="Historical",
            line=dict(color="#1f77b4", width=2)
        ))
        
        # Forecast
        fig_forecast.add_trace(go.Scatter(
            x=forecast_df.index,
            y=forecast_df["price"],
            mode="lines",
            name="Forecast",
            line=dict(color="#ff7f0e", width=2, dash="dash")
        ))
        
        # Confidence interval
        fig_forecast.add_trace(go.Scatter(
            x=forecast_df.index,
            y=forecast_df["upper"],
            mode="lines",
            name="Upper CI",
            line=dict(color="rgba(255,127,14,0.3)", width=1)
        ))
        
        fig_forecast.add_trace(go.Scatter(
            x=forecast_df.index,
            y=forecast_df["lower"],
            mode="lines",
            name="Lower CI",
            line=dict(color="rgba(255,127,14,0.3)", width=1),
            fill='tonexty',
            fillcolor='rgba(255,127,14,0.2)'
        ))
        
        fig_forecast.update_layout(
            title=f"{coin_label} Price Forecast ({forecast_horizon} days)",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            hovermode="x unified",
            height=500
        )

        st.plotly_chart(fig_forecast, use_container_width=True)
        
        # Forecast summary
        col1, col2, col3 = st.columns(3)
        forecast_end_price = forecast_df["price"].iloc[-1]
        forecast_change = (forecast_end_price / df["price"].iloc[-1] - 1) * 100
        
        col1.metric("Current Price", f"${df['price'].iloc[-1]:,.2f}")
        col2.metric("Forecasted Price", f"${forecast_end_price:,.2f}", delta=f"{forecast_change:.2f}%")
        col3.metric("Forecast Horizon", f"{forecast_horizon} days")

        create_alert_box("⚠️ ARIMA is a statistical model. Forecasts are for educational purposes only and should not be considered financial advice.", "warning")

# ----------------- DATA DOWNLOAD & EXPORT -----------------
st.markdown("---")
st.subheader("📥 Export Data")

col1, col2 = st.columns(2)

with col1:
    csv = df.reset_index().to_csv(index=False).encode("utf-8")
    st.download_button(
        " Download Full Dataset (CSV)",
        csv,
        file_name=f"{coin_id}_time_series_{days}d.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:
    # Export summary statistics
    summary_stats = pd.DataFrame({
        "Metric": ["Current Price", "Period High", "Period Low", "Total Return", "Sharpe Ratio", 
                   "Max Drawdown", "Avg Volume", "Current RSI"],
        "Value": [
            f"${current_price:,.2f}",
            f"${max_price:,.2f}",
            f"${min_price:,.2f}",
            f"{total_return*100:.2f}%",
            f"{sharpe:.2f}",
            f"{max_drawdown*100:.2f}%",
            f"${avg_volume:,.0f}",
            f"{current_rsi:.1f}"
        ]
    })
    summary_csv = summary_stats.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📈 Download Summary Stats (CSV)",
        summary_csv,
        file_name=f"{coin_id}_summary_{days}d.csv",
        mime="text/csv",
        use_container_width=True
    )

# Footer
st.markdown("---")
st.caption("💡 **Tip:** Use the sidebar to customize your analysis. Enable comparison mode to compare multiple cryptocurrencies!")
st.caption("⚠️ **Disclaimer:** This tool is for educational and informational purposes only. Not financial advice.")