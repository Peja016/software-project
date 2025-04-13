# tests/unit/test_accountApiFunction.py
import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, request, session, jsonify
import json
from accountApiFunction import accessData

@pytest.fixture
def test_app():
    """Create a test Flask app for request context."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.secret_key = 'test_secret_key'
    return app

def test_accessData_success(test_app):
    """Test accessData function with successful API response."""
    test_url = "https://test-url.com/script"
    test_form_data = {"name": "test_user", "password": "test_pass"}
    success_response = {"status": "success", "message": "Login successful"}
    
    # Create a mock for requests.post
    mock_response = MagicMock()
    mock_response.json.return_value = success_response
    
    with patch('accountApiFunction.requests.post', return_value=mock_response) as mock_post:
        with test_app.test_request_context(method='POST', data=test_form_data):
            response = accessData(test_url)
            
            # Check the function called requests.post with right args
            mock_post.assert_called_once_with(test_url, data=test_form_data)
            
            # Check the response
            assert response.status_code == 200
            response_data = json.loads(response.data)
            assert response_data == success_response
            
            # Check the session was updated
            assert session.get('name') == "test_user"

def test_accessData_api_error(test_app):
    """Test accessData with error response from API."""
    test_url = "https://test-url.com/script"
    test_form_data = {"name": "test_user", "password": "wrong_pass"}
    error_response = {"status": "error", "message": "Invalid credentials"}
    
    # Create a mock for requests.post
    mock_response = MagicMock()
    mock_response.json.return_value = error_response
    
    with patch('accountApiFunction.requests.post', return_value=mock_response) as mock_post:
        with test_app.test_request_context(method='POST', data=test_form_data):
            response = accessData(test_url)
            
            # Check the response
            assert response.status_code == 200
            response_data = json.loads(response.data)
            assert response_data == error_response
            
            # Session should not be updated
            assert 'name' not in session

def test_accessData_exception(test_app):
    """Test accessData handles exceptions properly."""
    test_url = "https://test-url.com/script"
    test_form_data = {"name": "test_user", "password": "test_pass"}
    
    # Create a mock that raises an exception
    with patch('accountApiFunction.requests.post', side_effect=Exception("Test exception")) as mock_post:
        with test_app.test_request_context(method='POST', data=test_form_data):
            response = accessData(test_url)
            
            # The function should return a tuple (response, status_code)
            # based on the implementation in accountApiFunction.py
            assert isinstance(response, tuple)
            json_response, status_code = response
            assert status_code == 500
            
            # Check the response content
            response_data = json.loads(json_response.data)
            assert response_data["status"] == "error"
            assert "Test exception" in response_data["message"]

def test_accessData_empty_form(test_app):
    """Test accessData when no form data is provided."""
    test_url = "https://test-url.com/script"
    
    with test_app.test_request_context(method='POST'):
        response = accessData(test_url)
        
        # The function should return a tuple (response, status_code) 
        # based on the implementation in accountApiFunction.py
        assert isinstance(response, tuple)
        json_response, status_code = response
        assert status_code == 400
        
        # Check the response content
        response_data = json.loads(json_response.data)
        assert response_data["status"] == "error"
        assert "No data received" in response_data["message"]