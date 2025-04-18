import os
import requests
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file
api_key = os.getenv('WEATHER_API_KEY')
url = 'https://api.openweathermap.org/data/2.5/weather'

def getCurrentWeatherData(lat = 53.344, lon = -6.2672):
    try:
        # Construct the full URL (including API key and city parameter)
        full_url = f'{url}?lat={lat}&lon={lon}&appid={api_key}&units=metric'

        # Send a GET request
        response = requests.get(full_url)
        return response
    except Exception as e:
        print(f"Failed to fetch weather data: {e}")
        return {
            "temp_max": 20.0,
            "humidity": 60.0,
            "wind_speed": 3.0,
            "pressure": 1013.0,
            "clouds_all": 50.0,
            "weather_main": "Clouds"
        }
