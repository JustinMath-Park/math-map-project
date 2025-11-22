def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['firebase'] is True
    assert data['ai_client'] is True

def test_404_error(client):
    """Test that a non-existent route returns 404."""
    response = client.get('/non-existent-route')
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data

def test_cors_headers(client):
    """Test that CORS headers are present."""
    response = client.get('/health')
    assert 'Access-Control-Allow-Origin' in response.headers
    assert response.headers['Access-Control-Allow-Origin'] == '*'
