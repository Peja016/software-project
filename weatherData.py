import requests
import os
import re
import time
from dotenv import load_dotenv
import pandas as pd

from db import getEngine

# https://openweathermap.org/img/wn/04n.png

load_dotenv() # Load environment variables from .env file

def getWeatherData():
    print('Start running')
    cursor, connection = getEngine()

    createWeatherReports = """
        CREATE TABLE IF NOT EXISTS weatherReports (
            id BIGINT PRIMARY KEY AUTO_INCREMENT,
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
            timestamp BIGINT
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
            FOREIGN KEY (conditionId) REFERENCES weatherReports(id) CASCADE
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
        main = data['main']
        wind = data['wind']
        sys = data['sys']
        weather = data['weather'][0]
        insertReportsData = f"""
            INSERT INTO weatherReports (
                temperature,
                feels_like,
                temp_min,
                temp_max,
                pressure,
                humidity,
                visibility,
                wind_speed,
                wind_deg,
                cloudiness,
                sunrise,
                sunset,
                timestamp,
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(insertReportsData, (
                main['temp'], 
                main['feels_like'], 
                main['temp_min'],
                main['temp_max'],
                main['pressure'],
                main['humidity'],
                data['visibility'],
                wind['speed'],
                wind['deg'],
                data['clouds']['all'],
                sys['sunrise'],
                sys['sunset'],
                data['dt'],
            )
        )
        insertConditionsData = f"""
            INSERT INTO weatherConditions (
                conditionId,
                weatherStatus,
                description,
                icon,
            )
            VALUES (%s, %s, %s, %s);
        """
        cursor.execute(insertConditionsData, (
                weather['id'], 
                weather['main'], 
                weather['description'], 
                weather['icon'],
            )
        )
    
        connection.commit()
        cursor.close()
        connection.close()
    else:
        print(f"Error: {response.status_code}")

# while True:
getWeatherData()
    # time.sleep(5*60) 