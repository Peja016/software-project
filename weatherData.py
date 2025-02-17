import requests
import os
import re
import time
from dotenv import load_dotenv
import pandas as pd

from db import getEngine

# https://openweathermap.org/img/wn/04n.png

load_dotenv() # Load environment variables from .env file

def check_table_exists(cursor, table_name):
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    result = cursor.fetchone()
    return result is not None  # if true，the table exists

def getWeatherData():
    print('Start running')
    # Replace with your actual API key
    cursor, connection = getEngine()

    createWeatherReports = """
        CREATE TABLE IF NOT EXISTS weatherReports (
            id BIGINT PRIMARY KEY AUTO_INCREMENT,
            timestamp BIGINT,
            temperature FLOAT,
            feels_like FLOAT,
            temp_min FLOAT,
            temp_max FLOAT,
            pressure INT,
            humidity INT,
            visibility INT,
            wind_speed FLOAT,
            wind_deg INT,
            cloudiness INT,
            sunrise BIGINT,
            sunset BIGINT,
        );
    """
    cursor.execute(createWeatherReports)

    createWeatherConditions = """
        CREATE TABLE IF NOT EXISTS weatherConditions (
            id INT PRIMARY KEY AUTO_INCREMENT,
            conditionId BIGINT,
            weatherStatus VARCHAR(50),
            description VARCHAR(100),
            icon VARCHAR(10),
            FOREIGN KEY (report_id) REFERENCES weatherReports(id) CASCADE
        );
    """
    cursor.execute(createWeatherConditions)

    api_key = os.getenv('WEATHER_API_KEY')
    url = 'https://api.openweathermap.org/data/2.5/weather'

    # Optional: specify the city (e.g., Paris)
    lat = 53.344
    lon = -6.2672


    # Construct the full URL (including API key and city parameter)
    full_url = f'{url}?lat={lat}&lon={lon}&&appid={api_key}'

    # Send a GET request
    response = requests.get(full_url)

    # Check if the request was successful (status code 200 means success)
    if response.status_code == 200:
        data = response.json()
        print(data)
        # with open("output.json", "w", encoding="utf-8") as json_file:
        #     json.dump(data, json_file, indent=4, ensure_ascii=False)
        # Output the raw data (JSON format)
        
        # print(json.dumps(data, indent=4))  # Beautify the output JSON data
        
        # For example, extract the station name and available bike count
        # for forecast in data:

        # connection.commit()
        # cursor.close()
        # connection.close()
    else:
        print(f"Error: {response.status_code}")

# while True:
getWeatherData()
    # time.sleep(5*60) 