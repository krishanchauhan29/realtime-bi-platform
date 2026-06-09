import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import silhouette_score
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
import scipy.stats as stats
import pingouin as pg
import warnings
warnings.filterwarnings('ignore')

# ==================== FORECASTING ====================
def forecast_arima(df, date_col, value_col, periods=30):
    try:
        ts = df[[date_col, value_col]].copy()
        ts[date_col] = pd.to_datetime(ts[date_col])
        ts = ts.sort_values(date_col).set_index(date_col)
        ts = ts[value_col].dropna()
        
        model = ARIMA(ts, order=(2, 1, 2))
        fitted = model.fit()
        forecast = fitted.forecast(steps=periods)
        
        last_date = ts.index[-1]
        future_dates = pd.date_range(start=last_date, periods=periods+1, freq='D')[1:]
        
        forecast_df = pd.DataFrame({
            'Date': future_dates,
            'Forecast': forecast.values,
            'Lower': forecast.values * 0.95,
            'Upper': forecast.values * 1.05
        })
        return forecast_df, fitted.aic
    except Exception as e:
        return None, None

# ==================== ANOMALY DETECTION ====================
def detect_anomalies(df, columns, contamination=0.05):
    try:
        num_df = df[columns].dropna()
        scaler = StandardScaler()
        scaled = scaler.fit_transform(num_df)
        
        iso = IsolationForest(contamination=contamination, random_state=42)
        predictions = iso.fit_predict(scaled)
        
        result = df.copy()
        result['Anomaly'] = 'Normal'
        result.loc[num_df.index[predictions == -1], 'Anomaly'] = 'Anomaly'
        result['Anomaly_Score'] = 0.0
        scores = iso.score_samples(scaled)
        result.loc[num_df.index, 'Anomaly_Score'] = np.round(scores, 3)
        
        anomaly_count = sum(predictions == -1)
        return result, anomaly_count
    except Exception as e:
        return df, 0

# ==================== CLUSTERING ====================
def perform_clustering(df, n_clusters=3):
    try:
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        if len(num_cols) < 2:
            return df, 0
        
        X = df[num_cols].dropna()
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        
        silhouette = silhouette_score(X_scaled, labels) if n_clusters > 1 else 0
        
        result = df.copy()
        result.loc[X.index, 'Cluster'] = [f'Cluster {l+1}' for l in labels]
        
        return result, round(silhouette, 3)
    except Exception as e:
        return df, 0

# ==================== STATISTICAL ANALYSIS ====================
def statistical_summary(df):
    try:
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        stats_results = {}
        
        for col in num_cols:
            data = df[col].dropna()
            if len(data) < 3:
                continue
            stat, p_value = stats.shapiro(data[:50])
            skewness = stats.skew(data)
            kurt = stats.kurtosis(data)
            
            stats_results[col] = {
                'Mean': round(data.mean(), 3),
                'Median': round(data.median(), 3),
                'Std Dev': round(data.std(), 3),
                'Skewness': round(skewness, 3),
                'Kurtosis': round(kurt, 3),
                'Normal Distribution': 'Yes' if p_value > 0.05 else 'No',
                'Min': round(data.min(), 3),
                'Max': round(data.max(), 3),
                'Q1': round(data.quantile(0.25), 3),
                'Q3': round(data.quantile(0.75), 3)
            }
        
        return pd.DataFrame(stats_results).T
    except:
        return pd.DataFrame()

# ==================== CORRELATION ANALYSIS ====================
def correlation_analysis(df):
    try:
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        if len(num_cols) < 2:
            return None, None
        corr_matrix = df[num_cols].corr()
        
        strong_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.5:
                    strong_corr.append({
                        'Feature 1': corr_matrix.columns[i],
                        'Feature 2': corr_matrix.columns[j],
                        'Correlation': round(corr_val, 3),
                        'Strength': 'Strong' if abs(corr_val) > 0.7 else 'Moderate'
                    })
        return corr_matrix, pd.DataFrame(strong_corr)
    except:
        return None, None