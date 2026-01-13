"""
Pytest configuration and fixtures
"""
import pytest
import sys
import os

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app
from models import db, User

@pytest.fixture
def app():
    """Create and configure a test Flask application"""
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # In-memory database for testing
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False,
    })
    
    # Create tables
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a test CLI runner"""
    return app.test_cli_runner()

@pytest.fixture
def auth_headers(client):
    """Create a verified user and return authorization headers"""
    # Register user
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    }
    client.post('/register', json=user_data)
    
    # Manually verify the user in database
    with client.application.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        user.email_verified = True
        db.session.commit()
    
    # Login to get token
    login_response = client.post('/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    token = login_response.get_json()['token']
    return {'Authorization': f'Bearer {token}'}
