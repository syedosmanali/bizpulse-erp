"""
Test ERP Authentication Module
Tests login, logout, and password change functionality
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.erp_modules.service import AuthenticationService
from modules.shared.database import get_db_connection, get_db_type
import uuid


class TestAuthenticationService:
    """Test authentication service functions"""
    
    def test_password_hashing(self):
        """Test that password hashing works correctly"""
        password = "test_password_123"
        
        # Hash password
        hashed = AuthenticationService.hash_password(password)
        
        # Verify it's a bcrypt hash (starts with $2b$)
        assert hashed.startswith('$2b$')
        
        # Verify password
        assert AuthenticationService.verify_password(password, hashed)
        
        # Verify wrong password fails
        assert not AuthenticationService.verify_password("wrong_password", hashed)
    
    def test_session_token_generation(self):
        """Test that session tokens are generated correctly"""
        token1 = AuthenticationService.generate_session_token()
        token2 = AuthenticationService.generate_session_token()
        
        # Tokens should be 64 characters (32 bytes in hex)
        assert len(token1) == 64
        assert len(token2) == 64
        
        # Tokens should be unique
        assert token1 != token2
    
    def test_authenticate_user_invalid_email(self):
        """Test authentication with invalid email"""
        result = AuthenticationService.authenticate_user(
            "nonexistent@example.com",
            "password123",
            "business_owner"
        )
        
        assert result['success'] == False
        assert 'error' in result
    
    def test_authenticate_user_invalid_password(self):
        """Test authentication with invalid password"""
        # Create a test user first
        conn = get_db_connection()
        cursor = conn.cursor()
        db_type = get_db_type()
        ph = '%s' if db_type == 'postgresql' else '?'
        
        test_user_id = str(uuid.uuid4())
        test_email = f"test_{test_user_id[:8]}@example.com"
        test_password = "correct_password"
        hashed_password = AuthenticationService.hash_password(test_password)
        
        try:
            # Insert test user
            cursor.execute(f"""
                INSERT INTO users (id, email, password_hash, business_name, is_active)
                VALUES ({ph}, {ph}, {ph}, {ph}, {ph})
            """, (test_user_id, test_email, hashed_password, "Test Business", True))
            conn.commit()
            
            # Try to authenticate with wrong password
            result = AuthenticationService.authenticate_user(
                test_email,
                "wrong_password",
                "business_owner"
            )
            
            assert result['success'] == False
            assert 'error' in result
            
        finally:
            # Cleanup
            cursor.execute(f"DELETE FROM users WHERE id = {ph}", (test_user_id,))
            conn.commit()
            conn.close()
    
    def test_authenticate_user_success(self):
        """Test successful authentication"""
        # Create a test user
        conn = get_db_connection()
        cursor = conn.cursor()
        db_type = get_db_type()
        ph = '%s' if db_type == 'postgresql' else '?'
        
        test_user_id = str(uuid.uuid4())
        test_email = f"test_{test_user_id[:8]}@example.com"
        test_password = "correct_password"
        hashed_password = AuthenticationService.hash_password(test_password)
        
        try:
            # Insert test user
            cursor.execute(f"""
                INSERT INTO users (id, email, password_hash, business_name, is_active)
                VALUES ({ph}, {ph}, {ph}, {ph}, {ph})
            """, (test_user_id, test_email, hashed_password, "Test Business", True))
            conn.commit()
            
            # Authenticate
            result = AuthenticationService.authenticate_user(
                test_email,
                test_password,
                "business_owner"
            )
            
            assert result['success'] == True
            assert 'user' in result
            assert result['user']['id'] == test_user_id
            assert result['user']['email'] == test_email
            assert 'password_hash' not in result['user']  # Should not return password
            
        finally:
            # Cleanup
            cursor.execute(f"DELETE FROM users WHERE id = {ph}", (test_user_id,))
            conn.commit()
            conn.close()
    
    def test_change_password_success(self):
        """Test successful password change"""
        # Create a test user
        conn = get_db_connection()
        cursor = conn.cursor()
        db_type = get_db_type()
        ph = '%s' if db_type == 'postgresql' else '?'
        
        test_user_id = str(uuid.uuid4())
        test_email = f"test_{test_user_id[:8]}@example.com"
        old_password = "old_password_123"
        new_password = "new_password_456"
        hashed_old_password = AuthenticationService.hash_password(old_password)
        
        try:
            # Insert test user
            cursor.execute(f"""
                INSERT INTO users (id, email, password_hash, business_name, is_active)
                VALUES ({ph}, {ph}, {ph}, {ph}, {ph})
            """, (test_user_id, test_email, hashed_old_password, "Test Business", True))
            conn.commit()
            
            # Change password
            result = AuthenticationService.change_password(
                test_user_id,
                old_password,
                new_password
            )
            
            assert result['success'] == True
            
            # Verify old password no longer works
            auth_result = AuthenticationService.authenticate_user(
                test_email,
                old_password,
                "business_owner"
            )
            assert auth_result['success'] == False
            
            # Verify new password works
            auth_result = AuthenticationService.authenticate_user(
                test_email,
                new_password,
                "business_owner"
            )
            assert auth_result['success'] == True
            
        finally:
            # Cleanup
            cursor.execute(f"DELETE FROM users WHERE id = {ph}", (test_user_id,))
            conn.commit()
            conn.close()
    
    def test_change_password_wrong_old_password(self):
        """Test password change with incorrect old password"""
        # Create a test user
        conn = get_db_connection()
        cursor = conn.cursor()
        db_type = get_db_type()
        ph = '%s' if db_type == 'postgresql' else '?'
        
        test_user_id = str(uuid.uuid4())
        test_email = f"test_{test_user_id[:8]}@example.com"
        old_password = "old_password_123"
        hashed_old_password = AuthenticationService.hash_password(old_password)
        
        try:
            # Insert test user
            cursor.execute(f"""
                INSERT INTO users (id, email, password_hash, business_name, is_active)
                VALUES ({ph}, {ph}, {ph}, {ph}, {ph})
            """, (test_user_id, test_email, hashed_old_password, "Test Business", True))
            conn.commit()
            
            # Try to change password with wrong old password
            result = AuthenticationService.change_password(
                test_user_id,
                "wrong_old_password",
                "new_password_456"
            )
            
            assert result['success'] == False
            assert result['error_code'] == 'INCORRECT_PASSWORD'
            
        finally:
            # Cleanup
            cursor.execute(f"DELETE FROM users WHERE id = {ph}", (test_user_id,))
            conn.commit()
            conn.close()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
