import os
import requests
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

def getBikesData():
    api_key = os.getenv('JCDecaux_API_KEY')
    url = 'https://api.jcdecaux.com/vls/v1/stations'
    # Optional: specify the city (e.g., Paris)
    city = 'dublin'
    # Construct the full URL (including API key and city parameter)
    # full_url = f'{url}?contract={city}&apiKey={api_key}'
    # Send a GET request
    response = requests.get(url, params={"apiKey": api_key, "contract": city})
    # print(type(response.json()))
    return response

# getBikesData()
