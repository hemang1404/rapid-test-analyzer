"""
Test database models
"""
import pytest
from models import User, Analysis

class TestUserModel:
    """Test User model"""
    
    def test_create_user(self, app):
        """Test creating a user"""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            
            assert user.username == 'testuser'
            assert user.email == 'test@example.com'
            assert user.password_hash is not None
            assert user.password_hash != 'password123'  # Should be hashed
    
    def test_password_hashing(self, app):
        """Test password hashing"""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('mypassword')
            
            # Password should be hashed
            assert user.password_hash != 'mypassword'
            
            # Should verify correct password
            assert user.check_password('mypassword') is True
            
            # Should reject incorrect password
            assert user.check_password('wrongpassword') is False
    
    def test_generate_verification_token(self, app):
        """Test verification token generation"""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            token = user.generate_verification_token()
            
            assert token is not None
            assert len(token) > 20  # Should be a long random token
            assert user.verification_token == token
    
    def test_user_to_dict(self, app):
        """Test user serialization"""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            
            user_dict = user.to_dict()
            
            assert 'username' in user_dict
            assert 'email' in user_dict
            assert 'email_verified' in user_dict
            assert 'password_hash' not in user_dict  # Should not expose password
            assert 'password' not in user_dict
    
    def test_default_values(self, app):
        """Test default field values"""
        with app.app_context():
            from models import db
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            assert user.email_verified is False
            assert user.verification_token is None
            assert user.last_login is None
