# tests/conftest.py
import pytest
import json
import os
from unittest.mock import patch, MagicMock
from flask import Flask
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your application
from app import app as flask_app

@pytest.fixture
def app():
    """Create a Flask application for testing."""
    return flask_app

@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture
def bike_data_sample():
    """Sample bike station data for testing."""
    return [
        {
            "number": 42,
            "name": "SMITHFIELD NORTH",
            "address": "Smithfield North",
            "position": {
                "lat": 53.349562,
                "lng": -6.278198
            },
            "banking": True,
            "bonus": False,
            "status": "OPEN",
            "bike_stands": 30,
            "available_bike_stands": 20,
            "available_bikes": 10,
            "last_update": 1617202821000
        },
        {
            "number": 30,
            "name": "PARNELL SQUARE NORTH",
            "address": "Parnell Square North",
            "position": {
                "lat": 53.353462,
                "lng": -6.265305
            },
            "banking": True,
            "bonus": False,
            "status": "OPEN",
            "bike_stands": 20,
            "available_bike_stands": 15,
            "available_bikes": 5,
            "last_update": 1617202810000
        }
    ]

@pytest.fixture
def weather_data_sample():
    """Sample weather data for testing."""
    return {
        "coord": {
            "lon": -6.2672,
            "lat": 53.344
        },
        "weather": [
            {
                "id": 804,
                "main": "Clouds",
                "description": "overcast clouds",
                "icon": "04d"
            }
        ],
        "base": "stations",
        "main": {
            "temp": 10.5,
            "feels_like": 8.9,
            "temp_min": 9.2,
            "temp_max": 11.8,
            "pressure": 1013,
            "humidity": 76
        },
        "visibility": 10000,
        "wind": {
            "speed": 5.7,
            "deg": 240
        },
        "clouds": {
            "all": 90
        },
        "dt": 1617202800,
        "sys": {
            "type": 1,
            "id": 1575,
            "country": "IE",
            "sunrise": 1617168540,
            "sunset": 1617215460
        },
        "timezone": 3600,
        "id": 2964574,
        "name": "Dublin",
        "cod": 200
    }

@pytest.fixture
def mock_getBikeData(bike_data_sample):
    """Mock for the getBikeData function."""
    with patch('getBikeData.getBikeData') as mock_get:
        response_mock = MagicMock()
        response_mock.status_code = 200
        response_mock.json.return_value = bike_data_sample
        mock_get.return_value = response_mock
        yield mock_get

@pytest.fixture
def mock_getWeatherData(weather_data_sample):
    """Mock for the getWeatherData function."""
    with patch('getWeatherData.getCurrentWeatherData') as mock_get:
        response_mock = MagicMock()
        response_mock.status_code = 200
        response_mock.json.return_value = weather_data_sample
        mock_get.return_value = response_mock
        yield mock_get

@pytest.fixture
def mock_session():
    """Mock for the Flask session."""
    with patch('flask.session', dict()) as mock_session:
        yield mock_session