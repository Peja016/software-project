# tests/unit/test_getBikeData.py
import pytest
import requests
from unittest.mock import patch
import os
from getBikeData import getBikeData

@pytest.mark.skip(reason="External API test - skipping to avoid rate limits")
def test_getBikeData_direct():
    """Test the getBikeData function directly with API key."""
    # Always skip this test to avoid making real API calls
    pytest.skip("Skipping external API test")

def test_getBikeData_mocked(monkeypatch):
    """Test getBikeData function with mocked requests."""
    # Mock the requests.get
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
        
        def json(self):
            return self.json_data
    
    # Sample bike data
    mock_data = [
        {
            "number": 42, 
            "name": "TEST STATION",
            "address": "Test Address",
            "position": {"lat": 53.349562, "lng": -6.278198},
            "banking": True,
            "bonus": False,
            "status": "OPEN",
            "bike_stands": 30,
            "available_bike_stands": 20,
            "available_bikes": 10,
            "last_update": 1617202821000
        }
    ]
    
    def mock_get(*args, **kwargs):
        return MockResponse(mock_data, 200)
    
    # Apply the monkeypatch
    monkeypatch.setattr(requests, "get", mock_get)
    
    # Test the function
    response = getBikeData()
    assert response.status_code == 200
    data = response.json()
    assert data == mock_data
    assert data[0]["name"] == "TEST STATION"
    assert data[0]["position"]["lat"] == 53.349562

def test_getBikeData_error_handling(monkeypatch):
    """Test error handling in getBikeData function."""
    # Mock requests.get to raise an exception
    def mock_get_error(*args, **kwargs):
        raise requests.exceptions.RequestException("Test exception")
    
    # Apply the monkeypatch
    monkeypatch.setattr(requests, "get", mock_get_error)
    
    # Test the function
    with pytest.raises(requests.exceptions.RequestException):
        getBikeData()