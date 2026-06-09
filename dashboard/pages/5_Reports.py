import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sys
import os
# Fix path to find src modules
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, '..', '..', 'src')
sys.path.insert(0, os.path.abspath(src_path))
from data_loader import load_uploaded_file, get_stock_data
from ml_models import statistical_summary
from report_generator import generate_excel_report, generate_pdf_report, generate_ppt_report
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Reports", page_icon="📥", layout="wide")
st.title("📥 Smart Reports Generator")
st.markdown("**Generate professional Excel, PDF & PowerPoint reports instantly**")
st.markdown("---")

# Data Source Selection
st.subheader("📂 Choose Data Source")
data_source = st.radio("", ["Upload Dataset", "Live Stock Data"], horizontal=True)

df = None
title = "Analytics Report"

if data_source == "Upload Dataset":
    uploaded_file = st.file_uploader("Upload CSV/Excel", type=['csv', 'xlsx'])
    if uploaded_file:
        df = load_uploaded_file(uploaded_file)
        if df is not None:
            df.columns = df.columns.str.strip()
            title = f"Analytics Report — {uploaded_file.name}"
            st.success(f"✅ Loaded: {df.shape[0]:,} rows × {df.shape[1]} columns")

elif data_source == "Live Stock Data":
    ticker = st.text_input("Stock Ticker", value="AAPL")
    period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y"], index=2)
    if st.button("📡 Fetch Live Data"):
        with st.spinner(f"Fetching {ticker} data..."):
            fetched_df, info = get_stock_data(ticker.upper(), period)
        if fetched_df is not None and len(fetched_df) > 0:
            st.session_state['report_df'] = fetched_df
            st.session_state['report_title'] = f"Stock Report — {ticker.upper()}"
            st.success(f"✅ Fetched {len(fetched_df):,} records for {ticker.upper()}")
        else:
            st.error(f"❌ Could not fetch data for {ticker}. Try: AAPL, GOOGL, MSFT")

    if 'report_df' in st.session_state and data_source == "Live Stock Data":
        df = st.session_state['report_df']
        title = st.session_state.get('report_title', 'Stock Report')

if df is not None:
    st.markdown("---")

    # Preview
    st.subheader("👁️ Data Preview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows", f"{len(df):,}")
    col2.metric("Columns", len(df.columns))
    col3.metric("Missing", df.isnull().sum().sum())
    col4.metric("Duplicates", df.duplicated().sum())

    st.dataframe(df.head(10), use_container_width=True)

    # Stats Preview
    stats_df = statistical_summary(df)
    if len(stats_df) > 0:
        st.subheader("📐 Statistical Summary Preview")
        st.dataframe(stats_df, use_container_width=True)

    # Charts Preview
    st.subheader("📊 Charts Preview")
    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    if num_cols:
        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.histogram(df, x=num_cols[0], title=f'Distribution — {num_cols[0]}',
                               color_discrete_sequence=['#2196F3'])
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            if len(num_cols) > 1:
                fig2 = px.scatter(df, x=num_cols[0], y=num_cols[1],
                                 title=f'{num_cols[0]} vs {num_cols[1]}',
                                 color_discrete_sequence=['#4CAF50'])
                st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # Insights
    insights = []
    if df.isnull().sum().sum() == 0:
        insights.append("✅ No missing values — dataset is clean")
    else:
        insights.append(f"⚠️ {df.isnull().sum().sum()} missing values found")
    if df.duplicated().sum() > 0:
        insights.append(f"⚠️ {df.duplicated().sum()} duplicate rows found")
    else:
        insights.append("✅ No duplicate rows")
    for col in num_cols[:3]:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        outliers = df[(df[col] < q1-1.5*iqr) | (df[col] > q3+1.5*iqr)].shape[0]
        if outliers > 0:
            insights.append(f"📊 {col}: {outliers} outliers detected")

    # Download Section
    st.subheader("📥 Download Reports")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 📊 Excel Report")
        st.markdown("6 sheets: Raw Data, Summary Stats, Missing Values, Data Quality, Numeric Analysis, Statistical Analysis")
        excel_data = generate_excel_report(df, stats_df if len(stats_df) > 0 else None, title)
        st.download_button(
            label="📊 Download Excel",
            data=excel_data,
            file_name="insightpro_report.xlsx",
            mime="application/vnd.ms-excel",
            use_container_width=True
        )

    with col2:
        st.markdown("#### 📄 PDF Report")
        st.markdown("Professional PDF with dataset overview, statistics, and key insights")
        pdf_data = generate_pdf_report(df, title, insights)
        st.download_button(
            label="📄 Download PDF",
            data=pdf_data,
            file_name="insightpro_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    with col3:
        st.markdown("#### 📑 PowerPoint Report")
        st.markdown("Presentation-ready slides with dataset overview and key statistics")
        ppt_data = generate_ppt_report(df, title)
        st.download_button(
            label="📑 Download PPT",
            data=ppt_data,
            file_name="insightpro_report.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            use_container_width=True
        )

else:
    st.info("👆 Upload a dataset or fetch live stock data to generate reports")

st.markdown("---")
st.caption("InsightPro BI | Reports: Excel (xlsxwriter) + PDF (ReportLab) + PPT (python-pptx)")