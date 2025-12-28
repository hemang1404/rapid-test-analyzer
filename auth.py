"""
Authentication utilities for JWT-based auth
"""
from functools import wraps
from flask import request, jsonify
import jwt
import os
from datetime import datetime, timedelta
from models import User

def get_secret_key():
    """Get JWT secret key from environment or use default"""
    return os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

def generate_token(user_id, username, email):
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'username': username,
        'email': email,
        'exp': datetime.utcnow() + timedelta(hours=24),  # Token expires in 24 hours
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(payload, get_secret_key(), algorithm='HS256')
    return token

def token_required(f):
    """Decorator to protect routes with JWT authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                # Format: "Bearer <token>"
                token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Authentication token is missing'}), 401
        
        try:
            # Decode and verify token
            data = jwt.decode(token, get_secret_key(), algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'error': f'Token validation failed: {str(e)}'}), 401
        
        # Pass current_user to the route
        return f(current_user, *args, **kwargs)
    
    return decorated

def optional_token(f):
    """Decorator that allows both authenticated and anonymous access"""
    @wraps(f)
    def decorated(*args, **kwargs):
        current_user = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
                data = jwt.decode(token, get_secret_key(), algorithms=['HS256'])
                current_user = User.query.get(data['user_id'])
            except:
                pass  # Invalid token, proceed as anonymous
        
        return f(current_user, *args, **kwargs)
    
    return decorated
