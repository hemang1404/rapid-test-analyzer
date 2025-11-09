"""
Configuration management for Rapid Test Analyzer
Centralizes all configuration settings for different environments
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = "uploads"
    RESULT_IMAGES_FOLDER = "result_images"
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
    
    # Analysis settings
    KNN_NEIGHBORS = 3
    MIN_IMAGE_BRIGHTNESS = 20
    MAX_IMAGE_BRIGHTNESS = 235
    
    # Rate limiting
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_PER_MINUTE = 10
    
class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False
    RATE_LIMIT_ENABLED = False  # Disable rate limiting in dev
    
class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    RATE_LIMIT_ENABLED = True
    
class TestingConfig(Config):
    """Testing environment configuration"""
    DEBUG = True
    TESTING = True
    RATE_LIMIT_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(env=None):
    """
    Get configuration object based on environment
    
    Args:
        env: Environment name ('development', 'production', 'testing')
        
    Returns:
        Configuration class for the specified environment
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
