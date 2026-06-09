import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys
import os
# Fix path to find src modules
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, '..', '..', 'src')
sys.path.insert(0, os.path.abspath(src_path))
from data_loader import get_stock_data, get_multiple_stocks, get_business_news
from ml_models import forecast_arima, detect_anomalies
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Live Market", page_icon="📈", layout="wide")
st.title("📈 Live Market Intelligence")
st.markdown("**Real-time stock data with ML forecasting and anomaly detection**")
st.markdown("---")

# Sidebar Controls
st.sidebar.title("⚙️ Market Controls")
ticker = st.sidebar.text_input("Stock Ticker", value="AAPL", placeholder="e.g. AAPL, GOOGL, TSLA")
period = st.sidebar.selectbox("Time Period", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)
show_forecast = st.sidebar.checkbox("Show ARIMA Forecast", value=True)
show_anomalies = st.sidebar.checkbox("Show Anomaly Detection", value=True)
forecast_days = st.sidebar.slider("Forecast Days", 7, 60, 30)

compare_tickers = st.sidebar.multiselect(
    "Compare Stocks",
    ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA", "NFLX"],
    default=["AAPL", "MSFT"]
)

# Load Data
with st.spinner(f"🔄 Fetching live data for {ticker}..."):
    df, info = get_stock_data(ticker.upper(), period)

if df is None or len(df) == 0:
    st.error(f"❌ Could not fetch data for {ticker}. Try: AAPL, GOOGL, MSFT, TSLA")
    st.stop()

# KPI Cards
st.subheader(f"📊 {ticker.upper()} — {info.get('longName', ticker)}")
col1, col2, col3, col4, col5 = st.columns(5)
latest = df.iloc[-1]
prev = df.iloc[-2] if len(df) > 1 else latest
price_change = latest['Close'] - prev['Close']
price_pct = (price_change / prev['Close']) * 100

col1.metric("💰 Current Price", f"${latest['Close']:.2f}", f"{price_change:+.2f} ({price_pct:+.2f}%)")
col2.metric("📈 High (Today)", f"${latest['High']:.2f}")
col3.metric("📉 Low (Today)", f"${latest['Low']:.2f}")
col4.metric("📦 Volume", f"{int(latest['Volume']):,}")
col5.metric("📅 Period", period)

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Price Chart", "📈 Forecast", "⚠️ Anomalies", "🔄 Compare", "📰 News"
])

with tab1:
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.7, 0.3],
                        subplot_titles=[f'{ticker.upper()} Price', 'Volume'])

    fig.add_trace(go.Candlestick(
        x=df['Date'], open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'], name='OHLC'
    ), row=1, col=1)

    # Moving Averages
    df['MA20'] = df['Close'].rolling(20).mean()
    df['MA50'] = df['Close'].rolling(50).mean()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['MA20'], name='MA20',
                             line=dict(color='orange', width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['MA50'], name='MA50',
                             line=dict(color='blue', width=1.5)), row=1, col=1)

    colors_vol = ['red' if c < o else 'green'
                  for c, o in zip(df['Close'], df['Open'])]
    fig.add_trace(go.Bar(x=df['Date'], y=df['Volume'],
                         marker_color=colors_vol, name='Volume'), row=2, col=1)

    fig.update_layout(height=600, xaxis_rangeslider_visible=False,
                      title=f'{ticker.upper()} Candlestick Chart with MA')
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    if show_forecast:
        with st.spinner("🤖 Running ARIMA forecasting..."):
            forecast_df, aic = forecast_arima(df, 'Date', 'Close', forecast_days)

        if forecast_df is not None:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=df['Date'], y=df['Close'],
                                      name='Historical', line=dict(color='#2196F3', width=2)))
            fig2.add_trace(go.Scatter(x=forecast_df['Date'], y=forecast_df['Forecast'],
                                      name='Forecast', line=dict(color='#FF9800', width=2, dash='dash')))
            fig2.add_trace(go.Scatter(
                x=pd.concat([forecast_df['Date'], forecast_df['Date'][::-1]]),
                y=pd.concat([forecast_df['Upper'], forecast_df['Lower'][::-1]]),
                fill='toself', fillcolor='rgba(255,152,0,0.2)',
                line=dict(color='rgba(255,255,255,0)'), name='Confidence Band'
            ))
            fig2.update_layout(title=f'{ticker.upper()} — {forecast_days}-Day ARIMA Forecast',
                               height=450)
            st.plotly_chart(fig2, use_container_width=True)

            col1, col2 = st.columns(2)
            col1.metric("📊 AIC Score", f"{aic:.2f}" if aic else "N/A")
            col2.metric("🔮 Forecast Period", f"{forecast_days} days")

            st.subheader("📋 Forecast Table")
            st.dataframe(forecast_df.round(2), use_container_width=True)
    else:
        st.info("Enable 'Show ARIMA Forecast' in sidebar")

with tab3:
    if show_anomalies:
        with st.spinner("🔍 Detecting anomalies..."):
            df_anomaly, count = detect_anomalies(df, ['Close', 'Volume'])

        anomalies = df_anomaly[df_anomaly['Anomaly'] == 'Anomaly']
        normals = df_anomaly[df_anomaly['Anomaly'] == 'Normal']

        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=normals['Date'], y=normals['Close'],
                                   mode='markers', name='Normal',
                                   marker=dict(color='#4CAF50', size=5)))
        fig3.add_trace(go.Scatter(x=anomalies['Date'], y=anomalies['Close'],
                                   mode='markers', name='Anomaly',
                                   marker=dict(color='#E53935', size=10, symbol='x')))
        fig3.update_layout(title=f'{ticker.upper()} — Anomaly Detection (Isolation Forest)',
                           height=400)
        st.plotly_chart(fig3, use_container_width=True)

        col1, col2 = st.columns(2)
        col1.metric("⚠️ Anomalies Detected", count)
        col2.metric("✅ Normal Points", len(df) - count)

        if len(anomalies) > 0:
            st.subheader("📋 Anomaly Details")
            st.dataframe(anomalies[['Date', 'Close', 'Volume', 'Anomaly_Score']].round(3),
                        use_container_width=True)
    else:
        st.info("Enable 'Show Anomaly Detection' in sidebar")

with tab4:
    if compare_tickers:
        with st.spinner("🔄 Loading comparison data..."):
            compare_data = get_multiple_stocks(compare_tickers, period)

        fig4 = go.Figure()
        for t, data in compare_data.items():
            if len(data) > 0:
                normalized = data['Close'] / data['Close'].iloc[0] * 100
                fig4.add_trace(go.Scatter(x=data['Date'], y=normalized,
                                          name=t, mode='lines'))
        fig4.update_layout(title='Stock Comparison (Normalized to 100)',
                           yaxis_title='Normalized Price', height=400)
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Select stocks to compare in sidebar")

with tab5:
    with st.spinner("📰 Fetching latest news..."):
        news = get_business_news(f"{ticker} stock")

    if news:
        for item in news[:8]:
            with st.expander(f"📰 {item['title'][:80]}..."):
                st.write(f"**Published:** {item['published']}")
                st.write(item['summary'])
    else:
        st.info("No news available at the moment")

st.markdown("---")
st.caption("InsightPro BI | Live data via yfinance | ML: ARIMA + Isolation Forest")