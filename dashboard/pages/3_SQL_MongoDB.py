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
from data_loader import load_uploaded_file, df_to_sqlite, run_sql_query, connect_mongodb, insert_to_mongodb, query_mongodb
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="SQL + MongoDB", page_icon="🗄️", layout="wide")
st.title("🗄️ SQL + MongoDB Analytics")
st.markdown("**Query your data with SQL or store/retrieve from MongoDB Atlas**")
st.markdown("---")

tab1, tab2 = st.tabs(["🗃️ SQL Analytics", "🍃 MongoDB Analytics"])

# ==================== SQL TAB ====================
with tab1:
    st.subheader("🗃️ SQL Analytics (SQLite)")
    st.info("Upload a dataset and run SQL queries on it directly!")

    uploaded_file = st.file_uploader("📂 Upload Dataset for SQL", type=['csv', 'xlsx'], key='sql_upload')

    if uploaded_file:
        df = load_uploaded_file(uploaded_file)
        if df is not None:
            df.columns = df.columns.str.strip().str.replace(' ', '_').str.lower()
            engine = df_to_sqlite(df, 'data')

            if engine:
                st.success(f"✅ Dataset loaded into SQLite: {df.shape[0]:,} rows × {df.shape[1]} columns")
                st.subheader("📋 Table Schema")
                schema_df = pd.DataFrame({
                    'Column': df.columns,
                    'Type': df.dtypes.values,
                    'Sample': [str(df[c].iloc[0]) if len(df) > 0 else 'N/A' for c in df.columns]
                })
                st.dataframe(schema_df, use_container_width=True)

                st.subheader("💡 Sample Queries")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📊 SELECT All (Top 10)"):
                        st.session_state['sql_query'] = "SELECT * FROM data LIMIT 10"
                    if st.button("🔢 Count Rows"):
                        st.session_state['sql_query'] = "SELECT COUNT(*) as total_rows FROM data"
                with col2:
                    num_cols = df.select_dtypes(include=np.number).columns.tolist()
                    if num_cols and st.button("📈 Summary Stats"):
                        col = num_cols[0]
                        st.session_state['sql_query'] = f"SELECT AVG({col}) as avg, MIN({col}) as min, MAX({col}) as max FROM data"
                    if st.button("🔍 Distinct Values"):
                        cat_cols = df.select_dtypes(include='object').columns.tolist()
                        if cat_cols:
                            st.session_state['sql_query'] = f"SELECT DISTINCT {cat_cols[0]}, COUNT(*) as count FROM data GROUP BY {cat_cols[0]} ORDER BY count DESC LIMIT 10"

                default_query = st.session_state.get('sql_query', 'SELECT * FROM data LIMIT 10')
                sql_query = st.text_area("✏️ Write SQL Query", value=default_query, height=100)

                if st.button("▶️ Run Query", use_container_width=True):
                    with st.spinner("Executing query..."):
                        result = run_sql_query(sql_query, engine)
                    if result is not None:
                        st.success(f"✅ Query returned {len(result):,} rows")
                        st.dataframe(result, use_container_width=True)
                        num_cols_r = result.select_dtypes(include=np.number).columns.tolist()
                        if len(num_cols_r) >= 1 and len(result) > 1:
                            fig = px.bar(result.head(20), y=num_cols_r[0],
                                        title=f'Query Result — {num_cols_r[0]}',
                                        color_discrete_sequence=['#2196F3'])
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("❌ Query failed. Check syntax and try again.")

# ==================== MONGODB TAB ====================
with tab2:
    st.subheader("🍃 MongoDB Atlas Analytics")
    st.info("Connect to MongoDB Atlas to store and query your data in the cloud!")

    with st.expander("🔗 How to get MongoDB Atlas connection string"):
        st.markdown("""
        1. Go to [mongodb.com/atlas](https://www.mongodb.com/cloud/atlas)
        2. Create free account → Free cluster (M0)
        3. Database Access → Add user
        4. Network Access → Allow 0.0.0.0/0
        5. Connect → Drivers → Copy connection string
        6. Replace `<password>` with your password
        """)

    mongo_uri = st.text_input("🔑 MongoDB Connection String",
                               placeholder="mongodb+srv://user:password@cluster.mongodb.net/",
                               type="password")

    col1, col2 = st.columns(2)
    with col1:
        db_name = st.text_input("Database Name", value="insightpro_db")
    with col2:
        collection_name = st.text_input("Collection Name", value="analytics_data")

    if mongo_uri:
        with st.spinner("Connecting to MongoDB..."):
            client = connect_mongodb(mongo_uri)

        if client:
            st.success("✅ Connected to MongoDB Atlas!")

            mongo_tab1, mongo_tab2 = st.tabs(["📤 Insert Data", "📥 Query Data"])

            with mongo_tab1:
                upload_mongo = st.file_uploader("Upload dataset to MongoDB", type=['csv', 'xlsx'], key='mongo_upload')
                if upload_mongo:
                    df_mongo = load_uploaded_file(upload_mongo)
                    if df_mongo is not None:
                        st.dataframe(df_mongo.head(), use_container_width=True)
                        if st.button("📤 Insert to MongoDB", use_container_width=True):
                            with st.spinner("Inserting data..."):
                                success = insert_to_mongodb(client, db_name, collection_name, df_mongo)
                            if success:
                                st.success(f"✅ {len(df_mongo):,} records inserted to {db_name}.{collection_name}")
                            else:
                                st.error("❌ Insert failed")

            with mongo_tab2:
                if st.button("📥 Fetch All Data", use_container_width=True):
                    with st.spinner("Fetching from MongoDB..."):
                        result = query_mongodb(client, db_name, collection_name)
                    if result is not None and len(result) > 0:
                        st.success(f"✅ Fetched {len(result):,} records")
                        st.dataframe(result, use_container_width=True)
                        num_cols = result.select_dtypes(include=np.number).columns.tolist()
                        if num_cols:
                            fig = px.histogram(result, x=num_cols[0],
                                             title=f'Distribution from MongoDB',
                                             color_discrete_sequence=['#4CAF50'])
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("No data found in collection")
        else:
            st.error("❌ Connection failed. Check your connection string.")
    else:
        st.info("Enter MongoDB connection string above to get started")

st.markdown("---")
st.caption("InsightPro BI | SQL: SQLite + SQLAlchemy | NoSQL: MongoDB + PyMongo")