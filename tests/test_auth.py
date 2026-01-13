"""
Test authentication endpoints
"""
import pytest
from models import User, db

class TestRegistration:
    """Test user registration"""
    
    def test_successful_registration(self, client):
        """Test successful user registration"""
        response = client.post('/register', json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'verification_token' in data
        assert data['user']['username'] == 'newuser'
        assert data['user']['email'] == 'newuser@example.com'
        assert data['user']['email_verified'] is False
    
    def test_registration_duplicate_email(self, client):
        """Test registration with duplicate email"""
        user_data = {
            'username': 'user1',
            'email': 'duplicate@example.com',
            'password': 'password123'
        }
        
        # First registration
        client.post('/register', json=user_data)
        
        # Try to register again with same email
        user_data['username'] = 'user2'
        response = client.post('/register', json=user_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'already registered' in data['error'].lower()
    
    def test_registration_duplicate_username(self, client):
        """Test registration with duplicate username"""
        # First user
        client.post('/register', json={
            'username': 'sameusername',
            'email': 'user1@example.com',
            'password': 'password123'
        })
        
        # Try with same username, different email
        response = client.post('/register', json={
            'username': 'sameusername',
            'email': 'user2@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'already taken' in data['error'].lower()
    
    def test_registration_short_username(self, client):
        """Test registration with short username"""
        response = client.post('/register', json={
            'username': 'ab',  # Less than 3 characters
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert '3 characters' in data['error'].lower()
    
    def test_registration_short_password(self, client):
        """Test registration with short password"""
        response = client.post('/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': '12345'  # Less than 6 characters
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert '6 characters' in data['error'].lower()
    
    def test_registration_invalid_email(self, client):
        """Test registration with invalid email"""
        response = client.post('/register', json={
            'username': 'testuser',
            'email': 'abc@123',  # Invalid email
            'password': 'password123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_registration_missing_fields(self, client):
        """Test registration with missing fields"""
        response = client.post('/register', json={
            'username': 'testuser'
            # Missing email and password
        })
        
        assert response.status_code == 400


class TestLogin:
    """Test user login"""
    
    def test_login_unverified_email(self, client):
        """Test login with unverified email"""
        # Register user
        client.post('/register', json={
            'username': 'unverified',
            'email': 'unverified@example.com',
            'password': 'password123'
        })
        
        # Try to login without verifying email
        response = client.post('/login', json={
            'email': 'unverified@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 403
        data = response.get_json()
        assert data['email_verified'] is False
        assert 'verify' in data['message'].lower()
    
    def test_successful_login(self, client):
        """Test successful login with verified email"""
        # Register user
        client.post('/register', json={
            'username': 'verified',
            'email': 'verified@example.com',
            'password': 'password123'
        })
        
        # Verify email manually
        with client.application.app_context():
            user = User.query.filter_by(email='verified@example.com').first()
            user.email_verified = True
            db.session.commit()
        
        # Login
        response = client.post('/login', json={
            'email': 'verified@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'token' in data
        assert data['user']['email'] == 'verified@example.com'
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post('/login', json={
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
        assert 'invalid' in data['error'].lower()
    
    def test_login_missing_fields(self, client):
        """Test login with missing fields"""
        response = client.post('/login', json={
            'email': 'test@example.com'
            # Missing password
        })
        
        assert response.status_code == 400


class TestEmailVerification:
    """Test email verification"""
    
    def test_verify_email_success(self, client):
        """Test successful email verification"""
        # Register user
        register_response = client.post('/register', json={
            'username': 'toverify',
            'email': 'toverify@example.com',
            'password': 'password123'
        })
        
        token = register_response.get_json()['verification_token']
        
        # Verify email
        response = client.get(f'/verify-email/{token}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'verified successfully' in data['message'].lower()
    
    def test_verify_email_invalid_token(self, client):
        """Test email verification with invalid token"""
        response = client.get('/verify-email/invalid-token-12345')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_verify_email_already_verified(self, client):
        """Test verifying already verified email"""
        # Register and verify
        register_response = client.post('/register', json={
            'username': 'alreadyverified',
            'email': 'already@example.com',
            'password': 'password123'
        })
        
        token = register_response.get_json()['verification_token']
        client.get(f'/verify-email/{token}')  # First verification
        
        # Try to verify again
        response = client.get(f'/verify-email/{token}')
        
        # Should still return success but indicate already verified
        assert response.status_code in [200, 400]
        data = response.get_json()
        if response.status_code == 200:
            assert 'already' in data['message'].lower()


class TestProtectedRoutes:
    """Test protected routes requiring authentication"""
    
    def test_access_protected_route_without_token(self, client):
        """Test accessing protected route without authentication"""
        response = client.get('/profile')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_access_protected_route_with_token(self, client, auth_headers):
        """Test accessing protected route with valid token"""
        response = client.get('/profile', headers=auth_headers)
        
        assert response.status_code == 200
    
    def test_access_with_invalid_token(self, client):
        """Test accessing protected route with invalid token"""
        response = client.get('/profile', headers={
            'Authorization': 'Bearer invalid-token-123'
        })
        
        assert response.status_code == 401
