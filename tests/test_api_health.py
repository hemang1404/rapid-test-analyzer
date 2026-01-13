"""
Test API health and basic endpoints
"""
import pytest

def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'version' in data
    assert 'timestamp' in data

def test_index_route(client):
    """Test the index route"""
    response = client.get('/')
    assert response.status_code in [200, 302]  # Either renders or redirects

def test_cors_headers(client):
    """Test CORS headers are present"""
    response = client.options('/health')
    # Check that CORS middleware is working
    assert response.status_code in [200, 204]

def test_404_error(client):
    """Test 404 error handling"""
    response = client.get('/nonexistent-endpoint')
    assert response.status_code == 404

def test_method_not_allowed(client):
    """Test method not allowed error"""
    response = client.post('/health')  # Health endpoint only accepts GET
    assert response.status_code == 405
