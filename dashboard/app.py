import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="Automated Data Warehouse", layout="wide")
st.title("🌦️ Automated Data Warehouse Dashboard")
st.markdown(
    """
    This dashboard displays the latest weather data collected from OpenWeather API
    for tracked world capitals. Non-technical users can see city information, recent
    weather readings, and trends over time.
    """
)

# -----------------------------
# Load environment variables & connect to DB
# -----------------------------
load_dotenv(dotenv_path="credentials.env")  
engine = create_engine(os.getenv("DATABASE_URL"))

# -----------------------------
# Load data
# -----------------------------
cities_df = pd.read_sql("SELECT * FROM dim_city ORDER BY city_name", engine)
weather_df = pd.read_sql("""
    SELECT fw.*, dc.city_name, dc.country
    FROM fact_weather fw
    JOIN dim_city dc USING(city_id)
    ORDER BY fw.ingested_at DESC
""", engine)

# Ensure ingested_at is a datetime object
weather_df['ingested_at'] = pd.to_datetime(weather_df['ingested_at'])

# -----------------------------
# Summary metrics
# -----------------------------
st.subheader("Summary Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Cities Tracked", len(cities_df))
col2.metric("Total Weather Records", len(weather_df))

latest_etl = weather_df['ingested_at'].max()
col3.metric("Latest ETL Run", latest_etl.strftime("%Y-%m-%d %H:%M:%S"))

# -----------------------------
# Show cities table
# -----------------------------
st.subheader("Tracked Cities")
st.dataframe(cities_df)

# -----------------------------
# Show recent weather table
# -----------------------------
st.subheader("Recent Weather Data")
st.dataframe(weather_df[['city_name','country','temp_c','feels_like_c',
                         'humidity','pressure','wind_speed','weather_main',
                         'weather_desc','ingested_at']])

# -----------------------------
# Interactive chart: Temperature trends
# -----------------------------
st.subheader("Temperature Trends")
city_selection = st.selectbox("Select a city to see temperature over time", cities_df['city_name'])
city_weather = weather_df[weather_df['city_name'] == city_selection].sort_values('ingested_at')

# Convert ingested_at to index for plotting
city_weather_chart = city_weather.set_index('ingested_at')['temp_c']
st.line_chart(city_weather_chart)

# -----------------------------
# Optional: Weather condition counts
# -----------------------------
st.subheader("Weather Condition Distribution")
condition_counts = weather_df['weather_main'].value_counts()
st.bar_chart(condition_counts)
