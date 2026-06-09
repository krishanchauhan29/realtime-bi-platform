import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from streamlit_folium import st_folium
import sys
import os
# Fix path to find src modules
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, '..', '..', 'src')
sys.path.insert(0, os.path.abspath(src_path))
from data_loader import load_uploaded_file
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Geo Intelligence", page_icon="🗺️", layout="wide")
st.title("🗺️ Geo Intelligence")
st.markdown("**Interactive maps with location-based analytics**")
st.markdown("---")

tab1, tab2 = st.tabs(["🗺️ Upload Geo Data", "🌍 World Demo"])

with tab1:
    st.subheader("📂 Upload Dataset with Location Data")
    st.info("Your dataset should have columns like: country, city, lat/latitude, lon/longitude")

    uploaded_file = st.file_uploader("Upload CSV/Excel", type=['csv', 'xlsx'], key='geo_upload')

    if uploaded_file:
        df = load_uploaded_file(uploaded_file)
        if df is not None:
            st.success(f"✅ Loaded: {df.shape[0]:,} rows")
            st.dataframe(df.head(3), use_container_width=True)

            col_lower = {c.lower(): c for c in df.columns}
            lat_col = col_lower.get('lat', col_lower.get('latitude', None))
            lon_col = col_lower.get('lon', col_lower.get('longitude', None))
            country_col = col_lower.get('country', None)

            if lat_col and lon_col:
                st.subheader("🗺️ Interactive Map")
                num_cols = df.select_dtypes(include=np.number).columns.tolist()
                color_col = st.selectbox("Color by", ['None'] + num_cols) if num_cols else 'None'
                size_col = st.selectbox("Size by", ['None'] + num_cols, key='size') if num_cols else 'None'

                fig = px.scatter_mapbox(
                    df.dropna(subset=[lat_col, lon_col]),
                    lat=lat_col, lon=lon_col,
                    color=None if color_col == 'None' else color_col,
                    size=None if size_col == 'None' else size_col,
                    hover_data=df.columns[:5].tolist(),
                    zoom=2, height=500,
                    title='Geo Distribution Map'
                )
                fig.update_layout(mapbox_style='open-street-map')
                st.plotly_chart(fig, use_container_width=True)

                # Folium map
                st.subheader("🗺️ Folium Interactive Map")
                df_map = df.dropna(subset=[lat_col, lon_col]).head(100)
                center_lat = df_map[lat_col].mean()
                center_lon = df_map[lon_col].mean()
                m = folium.Map(location=[center_lat, center_lon], zoom_start=3)
                for _, row in df_map.iterrows():
                    folium.CircleMarker(
                        location=[row[lat_col], row[lon_col]],
                        radius=6, color='#2196F3',
                        fill=True, fill_opacity=0.7,
                        popup=str(row.to_dict())[:200]
                    ).add_to(m)
                st_folium(m, width=700, height=400)

            elif country_col:
                st.subheader("🌍 Choropleth Map")
                num_cols = df.select_dtypes(include=np.number).columns.tolist()
                if num_cols:
                    value_col = st.selectbox("Value column", num_cols)
                    country_data = df.groupby(country_col)[value_col].sum().reset_index()
                    fig = px.choropleth(country_data, locations=country_col,
                                       locationmode='country names',
                                       color=value_col,
                                       color_continuous_scale='Viridis',
                                       title=f'{value_col} by Country')
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ No lat/lon or country column found. Add location data to visualize on map.")

with tab2:
    st.subheader("🌍 World GDP Demo Map")
    gdp_data = pd.DataFrame({
        'country': ['United States', 'China', 'Japan', 'Germany', 'India',
                    'United Kingdom', 'France', 'Brazil', 'Canada', 'Australia'],
        'gdp_trillion': [25.5, 17.9, 4.2, 4.1, 3.5, 3.1, 2.9, 1.9, 2.1, 1.7],
        'growth_rate': [2.1, 5.2, 1.1, 1.8, 7.2, 4.1, 2.5, 2.9, 3.4, 3.7],
        'population_m': [335, 1412, 125, 84, 1428, 67, 68, 215, 38, 26]
    })

    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.choropleth(gdp_data, locations='country',
                             locationmode='country names',
                             color='gdp_trillion',
                             color_continuous_scale='Blues',
                             title='World GDP (Trillion USD)',
                             hover_data=['growth_rate', 'population_m'])
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.scatter(gdp_data, x='gdp_trillion', y='growth_rate',
                         size='population_m', color='country',
                         title='GDP vs Growth Rate (Bubble = Population)',
                         labels={'gdp_trillion': 'GDP (Trillion USD)',
                                'growth_rate': 'Growth Rate (%)'})
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("🗺️ Folium World Map")
    m = folium.Map(location=[20, 0], zoom_start=2)
    coords = {
        'United States': [37.09, -95.71], 'China': [35.86, 104.19],
        'Japan': [36.2, 138.25], 'Germany': [51.16, 10.45],
        'India': [20.59, 78.96], 'United Kingdom': [55.37, -3.43]
    }
    for _, row in gdp_data.iterrows():
        if row['country'] in coords:
            folium.CircleMarker(
                location=coords[row['country']],
                radius=int(row['gdp_trillion'] * 3),
                color='#2196F3', fill=True, fill_opacity=0.7,
                popup=f"{row['country']}: ${row['gdp_trillion']}T GDP"
            ).add_to(m)
    st_folium(m, width=700, height=400)

st.markdown("---")
st.caption("InsightPro BI | Maps: Plotly + Folium | Geo Analytics")