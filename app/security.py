"""
Security Module - Database Encryption and Security Features
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64
import os
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import session, request, abort
import json

class DatabaseEncryption:
    """Handle database encryption/decryption"""
    
    def __init__(self, master_key=None):
        """Initialize encryption with master key"""
        if master_key is None:
            master_key = os.environ.get('DB_ENCRYPTION_KEY')
            if not master_key:
                raise ValueError("DB_ENCRYPTION_KEY environment variable not set")
        
        # Derive encryption key from master key
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'daily_report_system_salt_2024',  # Use unique salt
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        self.cipher = Fernet(key)
    
    def encrypt(self, data):
        """Encrypt sensitive data"""
        if data is None:
            return None
        if isinstance(data, str):
            data = data.encode()
        return self.cipher.encrypt(data).decode()
    
    def decrypt(self, encrypted_data):
        """Decrypt sensitive data"""
        if encrypted_data is None:
            return None
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode()
        return self.cipher.decrypt(encrypted_data).decode()

class SecurityManager:
    """Manage security features"""
    
    # Rate limiting storage (in production, use Redis)
    _rate_limit_storage = {}
    _failed_login_attempts = {}
    _blocked_ips = {}
    
    @staticmethod
    def generate_secure_token(length=32):
        """Generate cryptographically secure random token"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_password_secure(password, salt=None):
        """Hash password with salt using PBKDF2"""
        if salt is None:
            salt = secrets.token_bytes(32)
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = kdf.derive(password.encode())
        return base64.b64encode(salt + key).decode()
    
    @staticmethod
    def verify_password_secure(password, hashed):
        """Verify password against hash"""
        try:
            decoded = base64.b64decode(hashed.encode())
            salt = decoded[:32]
            stored_key = decoded[32:]
            
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            
            key = kdf.derive(password.encode())
            return key == stored_key
        except:
            return False
    
    @staticmethod
    def check_rate_limit(identifier, max_attempts=5, window_minutes=15):
        """Check if rate limit exceeded"""
        now = datetime.utcnow()
        
        if identifier not in SecurityManager._rate_limit_storage:
            SecurityManager._rate_limit_storage[identifier] = []
        
        # Clean old attempts
        SecurityManager._rate_limit_storage[identifier] = [
            timestamp for timestamp in SecurityManager._rate_limit_storage[identifier]
            if now - timestamp < timedelta(minutes=window_minutes)
        ]
        
        # Check limit
        if len(SecurityManager._rate_limit_storage[identifier]) >= max_attempts:
            return False
        
        # Add current attempt
        SecurityManager._rate_limit_storage[identifier].append(now)
        return True
    
    @staticmethod
    def record_failed_login(username, ip_address):
        """Record failed login attempt"""
        key = f"{username}:{ip_address}"
        now = datetime.utcnow()
        
        if key not in SecurityManager._failed_login_attempts:
            SecurityManager._failed_login_attempts[key] = []
        
        SecurityManager._failed_login_attempts[key].append(now)
        
        # Clean old attempts (keep last 24 hours)
        SecurityManager._failed_login_attempts[key] = [
            timestamp for timestamp in SecurityManager._failed_login_attempts[key]
            if now - timestamp < timedelta(hours=24)
        ]
        
        # Block IP if too many failed attempts
        if len(SecurityManager._failed_login_attempts[key]) >= 10:
            SecurityManager._blocked_ips[ip_address] = now + timedelta(hours=1)
            return True
        
        return False
    
    @staticmethod
    def is_ip_blocked(ip_address):
        """Check if IP is blocked"""
        if ip_address in SecurityManager._blocked_ips:
            if datetime.utcnow() < SecurityManager._blocked_ips[ip_address]:
                return True
            else:
                del SecurityManager._blocked_ips[ip_address]
        return False
    
    @staticmethod
    def clear_failed_attempts(username, ip_address):
        """Clear failed login attempts after successful login"""
        key = f"{username}:{ip_address}"
        if key in SecurityManager._failed_login_attempts:
            del SecurityManager._failed_login_attempts[key]

class AuditLogger:
    """Log security-related events"""
    
    @staticmethod
    def log_event(event_type, user_id, details, ip_address=None):
        """Log security event"""
        from app.models import AuditLog, db
        
        log_entry = AuditLog(
            event_type=event_type,
            user_id=user_id,
            details=json.dumps(details),
            ip_address=ip_address or request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:200]
        )
        
        db.session.add(log_entry)
        db.session.commit()
    
    @staticmethod
    def log_login(user_id, success=True):
        """Log login attempt"""
        AuditLogger.log_event(
            'login_success' if success else 'login_failed',
            user_id,
            {'success': success}
        )
    
    @staticmethod
    def log_data_access(user_id, resource_type, resource_id, action):
        """Log data access"""
        AuditLogger.log_event(
            'data_access',
            user_id,
            {
                'resource_type': resource_type,
                'resource_id': resource_id,
                'action': action
            }
        )
    
    @staticmethod
    def log_data_modification(user_id, resource_type, resource_id, action, changes=None):
        """Log data modification"""
        AuditLogger.log_event(
            'data_modification',
            user_id,
            {
                'resource_type': resource_type,
                'resource_id': resource_id,
                'action': action,
                'changes': changes
            }
        )

def require_secure_connection(f):
    """Decorator to require HTTPS in production"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_secure and not request.headers.get('X-Forwarded-Proto') == 'https':
            if os.environ.get('FLASK_ENV') == 'production':
                abort(403, 'HTTPS required')
        return f(*args, **kwargs)
    return decorated_function

def check_csrf_token(f):
    """Decorator to check CSRF token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'DELETE']:
            token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
            if not token or token != session.get('csrf_token'):
                abort(403, 'Invalid CSRF token')
        return f(*args, **kwargs)
    return decorated_function

def sanitize_input(data):
    """Sanitize user input to prevent XSS"""
    if isinstance(data, str):
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';']
        for char in dangerous_chars:
            data = data.replace(char, '')
    return data

def validate_file_upload(file, allowed_extensions={'png', 'jpg', 'jpeg', 'pdf'}):
    """Validate uploaded file"""
    if not file or not file.filename:
        return False, "No file provided"
    
    # Check extension
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if ext not in allowed_extensions:
        return False, f"File type not allowed. Allowed: {', '.join(allowed_extensions)}"
    
    # Check file size (max 5MB)
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    
    if size > 5 * 1024 * 1024:
        return False, "File too large (max 5MB)"
    
    return True, "Valid"
