"""
Security utilities for user management
Enhanced password hashing and security features
"""

import bcrypt
import secrets
import string
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SecurityManager:
    
    @staticmethod
    def hash_password(password):
        """Hash password using bcrypt"""
        try:
            # Generate salt and hash password
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            # Fallback to existing hash method for compatibility
            from modules.shared.database import hash_password as legacy_hash
            return legacy_hash(password)
    
    @staticmethod
    def verify_password(password, hashed):
        """Verify password against hash"""
        try:
            # Try bcrypt first
            if hashed.startswith('$2b$'):
                return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
            else:
                # Fallback to legacy hash verification
                from modules.shared.database import hash_password as legacy_hash
                return legacy_hash(password) == hashed
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    @staticmethod
    def generate_temp_password(length=8):
        """Generate secure temporary password"""
        # Use a mix of letters, numbers, and safe special characters
        characters = string.ascii_letters + string.digits + "!@#$%"
        password = ''.join(secrets.choice(characters) for _ in range(length))
        
        # Ensure password has at least one uppercase, lowercase, digit, and special char
        if not (any(c.isupper() for c in password) and 
                any(c.islower() for c in password) and 
                any(c.isdigit() for c in password) and
                any(c in "!@#$%" for c in password)):
            # Regenerate if requirements not met
            return SecurityManager.generate_temp_password(length)
        
        return password
    
    @staticmethod
    def validate_password_strength(password):
        """Validate password strength"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if len(password) > 128:
            errors.append("Password must be less than 128 characters")
        
        if not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("Password must contain at least one special character")
        
        # Check for common weak patterns
        weak_patterns = [
            r'(.)\1{2,}',  # Repeated characters (aaa, 111)
            r'(012|123|234|345|456|567|678|789|890)',  # Sequential numbers
            r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)',  # Sequential letters
        ]
        
        for pattern in weak_patterns:
            if re.search(pattern, password.lower()):
                errors.append("Password contains weak patterns (repeated or sequential characters)")
                break
        
        return errors
    
    @staticmethod
    def is_account_locked(failed_attempts, last_failed_time, lockout_duration_minutes=30):
        """Check if account should be locked due to failed attempts"""
        if failed_attempts >= 5:  # Lock after 5 failed attempts
            if last_failed_time:
                lockout_until = last_failed_time + timedelta(minutes=lockout_duration_minutes)
                return datetime.now() < lockout_until
        return False
    
    @staticmethod
    def generate_session_token():
        """Generate secure session token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def sanitize_input(input_string):
        """Sanitize user input to prevent injection attacks"""
        if not input_string:
            return ""
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`']
        sanitized = input_string
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized.strip()
    
    @staticmethod
    def log_security_event(client_id, user_id, event_type, details, ip_address=None, user_agent=None):
        """Log security-related events"""
        try:
            from modules.shared.database import get_db_connection, generate_id
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_activity_log (id, client_id, user_id, module, action, details, ip_address, user_agent)
                VALUES (?, ?, ?, 'security', ?, ?, ?, ?)
            ''', (generate_id(), client_id, user_id, event_type, details, ip_address, user_agent))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error logging security event: {e}")
    
    @staticmethod
    def check_permission(user_permissions, module, action):
        """Check if user has permission for specific module action"""
        try:
            import json
            
            if isinstance(user_permissions, str):
                permissions = json.loads(user_permissions)
            else:
                permissions = user_permissions
            
            if module in permissions:
                return action in permissions[module]
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking permissions: {e}")
            return False