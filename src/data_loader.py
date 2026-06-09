import pandas as pd
import numpy as np
import yfinance as yf
import requests
import feedparser
import sqlite3
import pymongo
from sqlalchemy import create_engine, text
import io
import warnings
warnings.filterwarnings('ignore')

# ==================== STOCK DATA ====================
def get_stock_data(ticker, period='1y'):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        df.reset_index(inplace=True)
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
        return df, stock.info
    except Exception as e:
        return None, {}

def get_multiple_stocks(tickers, period='1mo'):
    data = {}
    for ticker in tickers:
        df, info = get_stock_data(ticker, period)
        if df is not None and len(df) > 0:
            data[ticker] = df
    return data

# ==================== WEATHER DATA ====================
def get_weather(city, api_key=None):
    try:
        if api_key:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    'city': city,
                    'temperature': data['main']['temp'],
                    'humidity': data['main']['humidity'],
                    'description': data['weather'][0]['description'],
                    'wind_speed': data['wind']['speed']
                }
        # Fallback mock data if no API key
        return {
            'city': city,
            'temperature': round(np.random.uniform(15, 35), 1),
            'humidity': round(np.random.uniform(40, 80), 1),
            'description': 'partly cloudy',
            'wind_speed': round(np.random.uniform(5, 20), 1)
        }
    except:
        return None

# ==================== NEWS DATA ====================
def get_business_news(query='business finance'):
    try:
        url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(url)
        news = []
        for entry in feed.entries[:10]:
            news.append({
                'title': entry.get('title', ''),
                'published': entry.get('published', ''),
                'summary': entry.get('summary', '')[:200]
            })
        return news
    except:
        return []

# ==================== CSV/EXCEL UPLOAD ====================
def load_uploaded_file(uploaded_file):
    try:
        name = uploaded_file.name.lower()
        if name.endswith('.csv'):
            encodings = ['utf-8', 'windows-1252', 'latin-1']
            for enc in encodings:
                try:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding=enc)
                    if df.shape[1] > 1:
                        return df
                except:
                    continue
        elif name.endswith(('.xlsx', '.xls')):
            return pd.read_excel(uploaded_file)
        return None
    except Exception as e:
        return None

# ==================== SQL (SQLite) ====================
def df_to_sqlite(df, table_name='data'):
    try:
        engine = create_engine('sqlite:///data/analytics.db')
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        return engine
    except Exception as e:
        return None

def run_sql_query(query, engine):
    try:
        with engine.connect() as conn:
            result = pd.read_sql(text(query), conn)
        return result
    except Exception as e:
        return None

# ==================== MONGODB ====================
def connect_mongodb(connection_string=None):
    try:
        if connection_string:
            client = pymongo.MongoClient(connection_string, serverSelectionTimeoutMS=3000)
            client.server_info()
            return client
        return None
    except:
        return None

def insert_to_mongodb(client, db_name, collection_name, df):
    try:
        db = client[db_name]
        collection = db[collection_name]
        records = df.to_dict('records')
        collection.insert_many(records)
        return True
    except:
        return False

def query_mongodb(client, db_name, collection_name, query={}, limit=100):
    try:
        db = client[db_name]
        collection = db[collection_name]
        results = list(collection.find(query, {'_id': 0}).limit(limit))
        return pd.DataFrame(results)
    except:
        return None