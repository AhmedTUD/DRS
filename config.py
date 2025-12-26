import os
import secrets

class Config:
    # Security Keys - MUST be changed in production
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # Database Encryption Key - MUST be set in production
    DB_ENCRYPTION_KEY = os.environ.get('DB_ENCRYPTION_KEY') or 'change-this-in-production-to-secure-key'
    
    # Database configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    # For PythonAnywhere or local development
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        # Use provided database URL (MySQL on PythonAnywhere)
        if DATABASE_URL.startswith('mysql://'):
            DATABASE_URL = DATABASE_URL.replace('mysql://', 'mysql+pymysql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Use SQLite for local development
        db_path = os.path.join(basedir, 'instance', 'daily_report.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True,
    }
    
    # Security Settings
    SESSION_COOKIE_SECURE = False  # Allow cookies over HTTP for development
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    PERMANENT_SESSION_LIFETIME = 3600  # Session timeout: 1 hour
    
    # File Upload Settings
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max file size
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    
    # Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = 'memory://'
    
    # Security Headers
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; font-src 'self' https://cdn.jsdelivr.net;"
    }

class ProductionConfig(Config):
    """Production-specific configuration"""
    DEBUG = False
    TESTING = False
    
    # Force HTTPS
    SESSION_COOKIE_SECURE = True
    
    # Stricter security
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes in production

class DevelopmentConfig(Config):
    """Development-specific configuration"""
    DEBUG = True
    TESTING = False
    
    # Allow HTTP in development
    SESSION_COOKIE_SECURE = False

class TestingConfig(Config):
    """Testing-specific configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False