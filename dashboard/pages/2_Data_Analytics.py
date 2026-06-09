import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
import sys
import os
# Fix path to find src modules
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, '..', '..', 'src')
sys.path.insert(0, os.path.abspath(src_path))
from data_loader import load_uploaded_file
from ml_models import perform_clustering, statistical_summary, correlation_analysis, detect_anomalies
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Data Analytics Studio", page_icon="📊", layout="wide")
st.title("📊 Data Analytics Studio")
st.markdown("**Upload any dataset — auto EDA, statistical analysis, ML clustering & NLP insights**")
st.markdown("---")

# Sidebar
st.sidebar.title("⚙️ Analytics Controls")
uploaded_file = st.sidebar.file_uploader("📂 Upload Dataset", type=['csv', 'xlsx', 'xls'])
n_clusters = st.sidebar.slider("KMeans Clusters", 2, 8, 3)
show_clustering = st.sidebar.checkbox("Run Clustering", value=True)
show_anomaly = st.sidebar.checkbox("Run Anomaly Detection", value=True)

if uploaded_file is None:
    st.markdown("## 👋 Welcome to Data Analytics Studio!")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📋 **Auto EDA**\nKPIs, distributions, correlations")
    with col2:
        st.success("🤖 **ML Analysis**\nKMeans clustering + Anomaly detection")
    with col3:
        st.warning("📊 **Statistical Analysis**\nSciPy + Pingouin advanced stats")
    st.stop()

# Load Data
with st.spinner("Loading dataset..."):
    df = load_uploaded_file(uploaded_file)

if df is None:
    st.error("❌ Could not load file. Please upload a valid CSV or Excel file.")
    st.stop()

# Clean column names
df.columns = df.columns.str.strip()
for col in df.columns:
    try:
        df[col] = pd.to_numeric(df[col])
    except:
        pass

st.success(f"✅ Dataset loaded: {df.shape[0]:,} rows × {df.shape[1]} columns")

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📋 Overview", "📊 EDA", "📈 Visualizations",
    "🤖 ML Analysis", "📐 Statistics", "💡 Insights"
])

with tab1:
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("🗂️ Rows", f"{df.shape[0]:,}")
    col2.metric("📊 Columns", df.shape[1])
    col3.metric("❓ Missing", df.isnull().sum().sum())
    col4.metric("🔁 Duplicates", df.duplicated().sum())
    col5.metric("🔢 Numeric", len(df.select_dtypes(include=np.number).columns))
    col6.metric("🔤 Categorical", len(df.select_dtypes(include='object').columns))

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔍 First 5 Rows")
        st.dataframe(df.head(), use_container_width=True)
    with col2:
        st.subheader("📊 Data Types")
        dtype_df = pd.DataFrame({
            'Column': df.columns,
            'Type': df.dtypes.values,
            'Missing': df.isnull().sum().values,
            'Unique': df.nunique().values,
            'Sample': [str(df[c].dropna().iloc[0]) if len(df[c].dropna()) > 0 else 'N/A' for c in df.columns]
        })
        st.dataframe(dtype_df, use_container_width=True)

with tab2:
    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols = df.select_dtypes(include='object').columns.tolist()

    if num_cols:
        st.subheader("📈 Numeric Distributions")
        selected_num = st.selectbox("Select column", num_cols, key='eda_num')
        col1, col2 = st.columns(2)
        with col1:
            fig = px.histogram(df, x=selected_num, title=f'Distribution of {selected_num}',
                              color_discrete_sequence=['#2196F3'], nbins=30)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig2 = px.box(df, y=selected_num, title=f'Boxplot — {selected_num}',
                         color_discrete_sequence=['#4CAF50'])
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("🔥 Correlation Heatmap")
        if len(num_cols) > 1:
            corr_matrix, strong_corr = correlation_analysis(df)
            if corr_matrix is not None:
                fig3 = px.imshow(corr_matrix.round(2), title='Correlation Matrix',
                                color_continuous_scale='RdBu_r', text_auto=True)
                fig3.update_layout(height=400)
                st.plotly_chart(fig3, use_container_width=True)
                if strong_corr is not None and len(strong_corr) > 0:
                    st.subheader("💡 Strong Correlations Found")
                    st.dataframe(strong_corr, use_container_width=True)

    if cat_cols:
        st.subheader("🏷️ Categorical Distributions")
        selected_cat = st.selectbox("Select column", cat_cols, key='eda_cat')
        val_counts = df[selected_cat].value_counts().head(15)
        fig4 = px.bar(x=val_counts.index, y=val_counts.values,
                     title=f'Distribution — {selected_cat}',
                     color=val_counts.values, color_continuous_scale='Blues',
                     labels={'x': selected_cat, 'y': 'Count'})
        st.plotly_chart(fig4, use_container_width=True)

with tab3:
    st.subheader("📈 Interactive Visualizations")
    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    all_cols = df.columns.tolist()

    chart_type = st.selectbox("Chart Type", [
        "Bar Chart", "Line Chart", "Scatter Plot",
        "Histogram", "Pie Chart", "Area Chart", "Heatmap", "Altair Chart"
    ])

    if chart_type == "Bar Chart":
        x = st.selectbox("X axis", all_cols, key='bar_x')
        y = st.selectbox("Y axis", num_cols, key='bar_y')
        color = st.selectbox("Color by", ['None'] + all_cols, key='bar_c')
        fig = px.bar(df, x=x, y=y, color=None if color == 'None' else color,
                    title=f'{y} by {x}')
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Line Chart":
        x = st.selectbox("X axis", all_cols, key='line_x')
        y = st.selectbox("Y axis", num_cols, key='line_y')
        fig = px.line(df, x=x, y=y, title=f'{y} over {x}')
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Scatter Plot":
        x = st.selectbox("X axis", num_cols, key='sc_x')
        y = st.selectbox("Y axis", num_cols, key='sc_y')
        color = st.selectbox("Color by", ['None'] + all_cols, key='sc_c')
        fig = px.scatter(df, x=x, y=y, color=None if color == 'None' else color,
                        title=f'{x} vs {y}', trendline='ols')
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Histogram":
        col = st.selectbox("Column", num_cols, key='hist_c')
        bins = st.slider("Bins", 10, 100, 30)
        fig = px.histogram(df, x=col, nbins=bins, title=f'Distribution of {col}',
                          color_discrete_sequence=['#4CAF50'])
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Pie Chart":
        col = st.selectbox("Column", all_cols, key='pie_c')
        val_counts = df[col].value_counts().head(10)
        fig = px.pie(values=val_counts.values, names=val_counts.index,
                    title=f'{col} Distribution', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Area Chart":
        x = st.selectbox("X axis", all_cols, key='area_x')
        y = st.selectbox("Y axis", num_cols, key='area_y')
        fig = px.area(df, x=x, y=y, title=f'{y} Area Chart')
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Heatmap":
        num_cols_h = df.select_dtypes(include=np.number).columns.tolist()
        if len(num_cols_h) > 1:
            fig = px.imshow(df[num_cols_h].corr().round(2), title='Heatmap',
                           color_continuous_scale='RdBu_r', text_auto=True)
            st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Altair Chart":
        if len(num_cols) >= 2:
            x_alt = st.selectbox("X axis", num_cols, key='alt_x')
            y_alt = st.selectbox("Y axis", num_cols, key='alt_y')
            chart = alt.Chart(df.sample(min(500, len(df)))).mark_circle(size=60).encode(
                x=x_alt, y=y_alt,
                tooltip=list(df.columns[:4])
            ).interactive().properties(title=f'Altair: {x_alt} vs {y_alt}', height=400)
            st.altair_chart(chart, use_container_width=True)

with tab4:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔵 KMeans Clustering")
        if show_clustering:
            with st.spinner("Running KMeans..."):
                df_clustered, silhouette = perform_clustering(df, n_clusters)
            st.metric("Silhouette Score", silhouette)
            num_cols_c = df.select_dtypes(include=np.number).columns.tolist()
            if len(num_cols_c) >= 2 and 'Cluster' in df_clustered.columns:
                fig_c = px.scatter(df_clustered, x=num_cols_c[0], y=num_cols_c[1],
                                  color='Cluster', title='KMeans Clusters',
                                  color_discrete_sequence=px.colors.qualitative.Set1)
                st.plotly_chart(fig_c, use_container_width=True)
                cluster_summary = df_clustered.groupby('Cluster').size().reset_index(name='Count')
                st.dataframe(cluster_summary, use_container_width=True)

    with col2:
        st.subheader("⚠️ Anomaly Detection")
        if show_anomaly:
            num_cols_a = df.select_dtypes(include=np.number).columns.tolist()
            if num_cols_a:
                with st.spinner("Detecting anomalies..."):
                    df_anomaly, count = detect_anomalies(df, num_cols_a[:3])
                st.metric("Anomalies Found", count)
                anomalies = df_anomaly[df_anomaly['Anomaly'] == 'Anomaly']
                normals = df_anomaly[df_anomaly['Anomaly'] == 'Normal']
                fig_a = px.scatter(df_anomaly, x=num_cols_a[0],
                                  y=num_cols_a[1] if len(num_cols_a) > 1 else num_cols_a[0],
                                  color='Anomaly',
                                  color_discrete_map={'Normal': '#4CAF50', 'Anomaly': '#E53935'},
                                  title='Anomaly Detection (Isolation Forest)')
                st.plotly_chart(fig_a, use_container_width=True)

with tab5:
    st.subheader("📐 Advanced Statistical Analysis")
    with st.spinner("Computing statistics..."):
        stats_df = statistical_summary(df)
    if len(stats_df) > 0:
        st.dataframe(stats_df, use_container_width=True)
        st.subheader("📊 Distribution Tests")
        num_cols_s = df.select_dtypes(include=np.number).columns.tolist()
        if num_cols_s:
            selected = st.selectbox("Select column for analysis", num_cols_s)
            data = df[selected].dropna()
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Mean", f"{data.mean():.3f}")
            col2.metric("Median", f"{data.median():.3f}")
            col3.metric("Std Dev", f"{data.std():.3f}")
            col4.metric("Skewness", f"{data.skew():.3f}")

with tab6:
    st.subheader("💡 Auto Business Insights")
    insights = []
    missing_total = df.isnull().sum().sum()
    if missing_total == 0:
        insights.append("✅ Dataset is clean — no missing values found")
    else:
        insights.append(f"⚠️ {missing_total} missing values detected — consider imputation")

    dups = df.duplicated().sum()
    if dups > 0:
        insights.append(f"⚠️ {dups} duplicate rows found — consider removing")
    else:
        insights.append("✅ No duplicate rows found")

    num_cols_i = df.select_dtypes(include=np.number).columns
    for col in num_cols_i:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        outliers = df[(df[col] < q1 - 1.5*iqr) | (df[col] > q3 + 1.5*iqr)].shape[0]
        if outliers > 0:
            insights.append(f"📊 Column '{col}' has {outliers} outliers (IQR method)")

    corr_matrix, strong_corr = correlation_analysis(df)
    if strong_corr is not None and len(strong_corr) > 0:
        insights.append(f"🔗 {len(strong_corr)} strong correlations found between features")

    for insight in insights:
        st.markdown(f"- {insight}")

st.markdown("---")
st.caption("InsightPro BI | ML: KMeans + Isolation Forest | Stats: SciPy + Pingouin")