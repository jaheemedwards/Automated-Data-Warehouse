from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from scrape_wiki import scrape_city_coordinates, capitals
from fetch_weather import get_weather
import pandas as pd
import os
import json

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv(dotenv_path="credentials.env")  
API_KEY = os.getenv("OPENWEATHER_API_KEY")
engine = create_engine(os.getenv("DATABASE_URL"))

# -----------------------------
# Insert city into dim_city
# -----------------------------
def insert_city(engine, city_data):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO dim_city (city_name, latitude, longitude, country)
            VALUES (:city_name, :latitude, :longitude, :country)
            ON CONFLICT (city_name) DO UPDATE
            SET latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude,
                country = EXCLUDED.country,
                updated_at = now();
        """), city_data)

# -----------------------------
# Insert time into dim_time
# -----------------------------
def insert_time(engine, timestamp):
    with engine.begin() as conn:
        result = conn.execute(text("""
            INSERT INTO dim_time (ts, date, hour, day, month, year, weekday)
            VALUES (:ts, :date, :hour, :day, :month, :year, :weekday)
            ON CONFLICT (ts) DO NOTHING
            RETURNING time_id;
        """), {
            "ts": timestamp,
            "date": timestamp.date(),
            "hour": timestamp.hour,
            "day": timestamp.day,
            "month": timestamp.month,
            "year": timestamp.year,
            "weekday": timestamp.weekday()
        })
        row = result.fetchone()
        if row:
            return row[0]
        # If already exists, fetch it
        time_id = conn.execute(text("SELECT time_id FROM dim_time WHERE ts = :ts"), {"ts": timestamp}).scalar()
        return time_id

# -----------------------------
# Insert weather into fact_weather
# -----------------------------
def insert_weather(engine, city_name, weather_data):
    timestamp = weather_data["timestamp"]
    
    # Get city_id
    with engine.begin() as conn:
        city_id = conn.execute(text("SELECT city_id FROM dim_city WHERE city_name = :name"), {"name": city_name}).scalar()
    
    # Insert or get time_id
    time_id = insert_time(engine, timestamp)
    
    # Insert weather record
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO fact_weather (
                city_id, time_id, source, temp_c, feels_like_c, humidity,
                pressure, wind_speed, weather_main, weather_desc, raw_json
            )
            VALUES (
                :city_id, :time_id, :source, :temp_c, :feels_like_c, :humidity,
                :pressure, :wind_speed, :weather_main, :weather_desc, :raw_json
            )
        """), {
            "city_id": city_id,
            "time_id": time_id,
            "source": "OpenWeather API",
            "temp_c": weather_data["temp_c"],
            "feels_like_c": weather_data["feels_like_c"],
            "humidity": weather_data["humidity"],
            "pressure": weather_data["pressure"],
            "wind_speed": weather_data["wind_speed"],
            "weather_main": weather_data["weather_main"],
            "weather_desc": weather_data["weather_desc"],
            "raw_json": json.dumps(weather_data["raw_json"])
        })

# -----------------------------
# Main ETL workflow
# -----------------------------
records = []
for cap in capitals:
    lat, lon = scrape_city_coordinates(cap["city"])
    records.append({
        "city_name": cap["city"],
        "country": cap["country"],
        "latitude": lat,
        "longitude": lon
    })

capital_data = pd.DataFrame(records)

# Insert all cities into dim_city
for _, row in capital_data.iterrows():
    insert_city(engine, row.to_dict())

# Fetch and insert weather for all cities
for _, row in capital_data.iterrows():
    city_name = row["city_name"]
    lat = row["latitude"]
    lon = row["longitude"]
    
    weather = get_weather(lat, lon, API_KEY)
    
    if weather is None:
        print(f"Skipping {city_name} due to API error")
        continue
    
    insert_weather(engine, city_name, weather)

print("ETL completed successfully!")
