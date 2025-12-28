"""
Database models for Rapid Test Analyzer
Handles User accounts and Analysis history
"""
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationship with analyses
    analyses = db.relationship('Analysis', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary (without password)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Analysis(db.Model):
    """Analysis model for storing test results"""
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    test_type = db.Column(db.String(50), nullable=False)  # 'ph', 'fob', 'urinalysis'
    result = db.Column(db.Text, nullable=False)
    diagnosis = db.Column(db.Text)
    image_path = db.Column(db.String(255))
    result_image_path = db.Column(db.String(255))
    confidence = db.Column(db.Float)
    raw_data = db.Column(db.Text)  # JSON string of detailed results
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """Convert analysis to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'test_type': self.test_type,
            'result': self.result,
            'diagnosis': self.diagnosis,
            'image_path': self.image_path,
            'result_image_path': self.result_image_path,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
