# 🚀 InsightPro BI Platform

A full-stack Real-Time Business Intelligence Platform that connects live market data, lets you upload any dataset, and delivers instant analytics — forecasting, anomaly detection, clustering, maps, SQL queries, MongoDB integration, and downloadable reports.

## 🔴 Live Demo
👉 [Click here to try the live app](https://realtime-bi-platform292003.streamlit.app/)

## ✨ Features

| Page | Features |
|------|---------|
| 📈 Live Market | Real-time stocks (yfinance), ARIMA forecasting, Anomaly Detection, News feed |
| 📊 Data Analytics | Upload CSV/Excel, Auto EDA, KMeans Clustering, Statistical Analysis, NLP Insights |
| 🗄️ SQL + MongoDB | SQLite queries on uploaded data, MongoDB Atlas cloud integration |
| 🗺️ Geo Intelligence | Interactive Folium maps, Choropleth, Location-based analytics |
| 📥 Reports | Excel (6 sheets) + PDF (colored) + PowerPoint (dark theme) |

## 🤖 ML Models Used
- **ARIMA** — Time series forecasting (statsmodels)
- **Isolation Forest** — Anomaly detection (scikit-learn)
- **KMeans** — Customer/data clustering (scikit-learn)
- **Statistical Analysis** — SciPy + Pingouin

## 🛠️ Tech Stack
- **Data** — Pandas, NumPy, SciPy, Statsmodels, Pingouin
- **ML** — Scikit-learn (IsolationForest, KMeans)
- **Visualization** — Plotly, Altair, Folium
- **Live APIs** — yfinance (stocks), feedparser (news)
- **Database** — SQLite + SQLAlchemy, MongoDB + PyMongo
- **Reports** — XlsxWriter, ReportLab, python-pptx
- **Dashboard** — Streamlit (multi-page)

## 🚀 Run Locally
```bash
git clone https://github.com/krishanchauhan29/realtime-bi-platform.git
cd realtime-bi-platform
pip install -r requirements.txt
streamlit run dashboard/app.py
```

## 👤 Built By
**Krishan Kumar Chauhan**
M.Tech Data Science | Gautam Buddha University
[LinkedIn](https://www.linkedin.com/in/krishan-chauhan-714011232/) | [GitHub](https://github.com/krishanchauhan29)
