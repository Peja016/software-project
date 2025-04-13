# tests/unit/test_getWeatherData.py
import pytest
import requests
from unittest.mock import patch, MagicMock
import os
from getWeatherData import getCurrentWeatherData

@pytest.mark.skip(reason="External API test - skipping to avoid rate limits")
def test_getCurrentWeatherData_direct():
    """Test the getCurrentWeatherData function directly with API key."""
    # Always skip this test to avoid making real API calls
    pytest.skip("Skipping external API test")

def test_getCurrentWeatherData_mocked(monkeypatch):
    """Test getCurrentWeatherData function with mocked requests."""
    # Mock the requests.get
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
        
        def json(self):
            return self.json_data
    
    # Sample weather data
    mock_data = {
        "main": {"temp": 10.5, "humidity": 76},
        "weather": [{"id": 804, "main": "Clouds", "description": "overcast clouds", "icon": "04d"}],
        "wind": {"speed": 5.7, "deg": 240},
        "clouds": {"all": 90}
    }
    
    def mock_get(*args, **kwargs):
        return MockResponse(mock_data, 200)
    
    # Apply the monkeypatch
    monkeypatch.setattr(requests, "get", mock_get)
    
    # Test the function
    response = getCurrentWeatherData()
    assert response.status_code == 200
    data = response.json()
    assert data == mock_data
    assert data["main"]["temp"] == 10.5
    assert data["weather"][0]["main"] == "Clouds"

@pytest.mark.skip(reason="External API test - skipping to avoid rate limits")
def test_getCurrentWeatherData_custom_location():
    """Test getCurrentWeatherData with custom location."""
    # Always skip this test to avoid making real API calls
    pytest.skip("Skipping external API test")