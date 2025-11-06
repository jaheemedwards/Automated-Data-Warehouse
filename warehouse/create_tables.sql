-- Dimension table for cities (simple version)
CREATE TABLE IF NOT EXISTS dim_city (
    city_id SERIAL PRIMARY KEY,
    city_name TEXT UNIQUE,           -- e.g., "London"
    latitude DOUBLE PRECISION,       -- Latitude
    longitude DOUBLE PRECISION,      -- Longitude
    country TEXT,                    -- Country name
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Dimension table for time
CREATE TABLE IF NOT EXISTS dim_time (
    time_id SERIAL PRIMARY KEY,
    ts TIMESTAMPTZ UNIQUE,           -- Timestamp of weather data
    date DATE,
    hour INT,
    day INT,
    month INT,
    year INT,
    weekday INT
);

-- Fact table for weather (dynamic / API data)
CREATE TABLE IF NOT EXISTS fact_weather (
    weather_id SERIAL PRIMARY KEY,
    city_id INT REFERENCES dim_city(city_id),
    time_id INT REFERENCES dim_time(time_id),
    source TEXT,                      -- e.g., "OpenWeather API"
    temp_c DOUBLE PRECISION,
    feels_like_c DOUBLE PRECISION,
    humidity INT,
    pressure INT,
    wind_speed DOUBLE PRECISION,
    weather_main TEXT,                -- e.g., "Clouds"
    weather_desc TEXT,                -- e.g., "overcast clouds"
    raw_json JSONB,                   -- store the full API response
    ingested_at TIMESTAMPTZ DEFAULT now()
);
