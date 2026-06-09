import streamlit as st

st.set_page_config(
    page_title="InsightPro BI Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #2196F3, #4CAF50, #FF9800);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
    }
    .feature-card {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 4px solid #2196F3;
        margin: 0.5rem 0;
    }
    .metric-highlight {
        background: #E3F2FD;
        padding: 0.8rem;
        border-radius: 8px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-title">🚀 InsightPro BI Platform</p>', unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center; color:#666;'>Enterprise-Grade Real-Time Business Intelligence</h4>",
            unsafe_allow_html=True)
st.markdown("---")

# Feature Cards
col1, col2, col3 = st.columns(3)
with col1:
    st.info("📈 **Live Market Intelligence**\nReal-time stock data, ARIMA forecasting & anomaly detection")
    st.info("🗄️ **SQL + MongoDB Analytics**\nQuery your data with SQL or store in MongoDB Atlas")

with col2:
    st.success("📊 **Data Analytics Studio**\nUpload any dataset — auto EDA, clustering & NLP insights")
    st.success("🔔 **Smart Alerts**\nSet thresholds & get automated alerts on your data")

with col3:
    st.warning("🗺️ **Geo Intelligence**\nInteractive maps with location-based analytics")
    st.warning("📥 **Multi-format Reports**\nDownload Excel, PDF & PowerPoint reports instantly")

st.markdown("---")

# Stats
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("📊 Pages", "5")
col2.metric("🤖 ML Models", "4")
col3.metric("📡 Live APIs", "3")
col4.metric("📁 File Formats", "CSV, Excel")
col5.metric("📥 Export Formats", "Excel, PDF, PPT")

st.markdown("---")

# Getting Started
st.subheader("🚀 Getting Started")
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    **Option 1 — Live Data:**
    1. Go to **📈 Live Market** in sidebar
    2. Enter stock ticker (e.g. AAPL, GOOGL)
    3. View real-time charts + forecasting
    """)
with col2:
    st.markdown("""
    **Option 2 — Your Data:**
    1. Go to **📊 Data Analytics** in sidebar
    2. Upload your CSV or Excel file
    3. Get instant EDA + ML insights
    """)

st.markdown("---")
st.caption("Built by Krishan Kumar Chauhan | M.Tech Data Science, GBU | InsightPro BI Platform v1.0")