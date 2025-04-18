import os
import requests
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

def getBikeData():
    api_key = os.getenv('JCDecaux_API_KEY')
    url = 'https://api.jcdecaux.com/vls/v1/stations'
    # Optional: specify the city (e.g., Paris)
    city = 'dublin'
    # Construct the full URL (including API key and city parameter)
    # Send a GET request
    response = requests.get(url, params={"apiKey": api_key, "contract": city})
    return response
