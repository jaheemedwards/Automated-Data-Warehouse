import os, requests, json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv(dotenv_path="credentials.env")  

API_KEY = os.getenv("OPENWEATHER_API_KEY")
# print(API_KEY)

def get_weather(lat, lon, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}"
    response = requests.get(url).json()
    
    weather_data = {
        "temp_c": response["main"]["temp"],
        "feels_like_c": response["main"]["feels_like"],
        "humidity": response["main"]["humidity"],
        "pressure": response["main"]["pressure"],
        "wind_speed": response["wind"]["speed"],
        "weather_main": response["weather"][0]["main"],
        "weather_desc": response["weather"][0]["description"],
        "city_name": response["name"],
        "coord": response["coord"],
        "raw_json": json.dumps(response),
        "timestamp": datetime.now()
    }
    
    return weather_data

# weather_data = get_weather(51.5074, -0.1278, API_KEY)
# print(weather_data)