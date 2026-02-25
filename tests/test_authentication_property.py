"""
Property-Based Test for Authentication

Feature: comprehensive-erp-modules
Property 1: Login Credential Validation

**Validates: Requirements 1.2**

This test validates that for any login attempt with credentials, the system 
should validate against the database and return success only when credentials 
match a valid user record.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck, assume
from hypothesis.strategies import composite
import os
import sys
import uuid

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.shared.database import get_db_connection, get_db_type
from modules.erp_modules.service import AuthenticationService


@composite
def valid_user_credentials_strategy(draw):
    """Generate valid user credentials for testing"""
    email = draw(st.emails())
    password = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
        min_size=8,
        max_size=20
    ))
    user_type = draw(st.sampled_from(['admin', 'operator', 'business_owner']))
    
    return {
        'email': email,
        'password': password,
        'user_type': user_type
    }


@composite
def invalid_credentials_strategy(draw):
    """Generate invalid credentials (wrong password)"""
    email = draw(st.emails())
    correct_password = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
        min_size=8,
        max_size=20
    ))
    wrong_password = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
        min_size=8,
        max_size=20
    ))
    # Ensure passwords are different
    assume(correct_password != wrong_password)
    
    user_type = draw(st.sampled_from(['admin', 'operator', 'business_owner']))
    
    return {
        'email': email,
        'correct_password': correct_password,
        'wrong_password': wrong_password,
        'user_type': user_type
    }


def create_test_user(email, password, user_type):
    """Helper function to create a test user in the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    db_type = get_db_type()
    ph = '%s' if db_type == 'postgresql' else '?'
    
    user_id = str(uuid.uuid4())
    password_hash = AuthenticationService.hash_password(password)
    
    try:
        if user_type == 'admin':
            cursor.execute(f"""
                INSERT INTO super_admins (id, email, password_hash, full_name, is_active)
                VALUES ({ph}, {ph}, {ph}, {ph}, {ph})
            """, (user_id, email, password_hash, 'Test Admin', True))
        elif user_type == 'operator':
            # Create a business owner first for the operator
            business_owner_id = str(uuid.uuid4())
            cursor.execute(f"""
                INSERT INTO users (id, email, password_hash, business_name, is_active)
                VALUES ({ph}, {ph}, {ph}, {ph}, {ph})
            """, (business_owner_id, f"owner_{email}", 'dummy_hash', 'Test Business', True))
            
            cursor.execute(f"""
                INSERT INTO erp_staff (id, user_id, email, password_hash, staff_name, is_active)
                VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})
            """, (user_id, business_owner_id, email, password_hash, 'Test Operator', True))
        else:  # business_owner
            cursor.execute(f"""
                INSERT INTO users (id, email, password_hash, business_name, is_active)
                VALUES ({ph}, {ph}, {ph}, {ph}, {ph})
            """, (user_id, email, password_hash, 'Test Business', True))
        
        conn.commit()
        return user_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def cleanup_test_user(email, user_type):
    """Helper function to clean up test user from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    db_type = get_db_type()
    ph = '%s' if db_type == 'postgresql' else '?'
    
    try:
        if user_type == 'admin':
            cursor.execute(f"DELETE FROM super_admins WHERE email = {ph}", (email,))
        elif user_type == 'operator':
            cursor.execute(f"DELETE FROM erp_staff WHERE email = {ph}", (email,))
            cursor.execute(f"DELETE FROM users WHERE email = {ph}", (f"owner_{email}",))
        else:  # business_owner
            cursor.execute(f"DELETE FROM users WHERE email = {ph}", (email,))
        
        conn.commit()
    except Exception:
        conn.rollback()
    finally:
        conn.close()


@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(credentials=valid_user_credentials_strategy())
def test_login_with_valid_credentials_succeeds(credentials):
    """
    Property 1: Login Credential Validation
    
    For any login attempt with valid credentials, the system should 
    validate against the database and return success.
    """
    email = credentials['email']
    password = credentials['password']
    user_type = credentials['user_type']
    
    # Create test user
    try:
        user_id = create_test_user(email, password, user_type)
        
        # Attempt authentication
        result = AuthenticationService.authenticate_user(email, password, user_type)
        
        # Verify success
        assert result['success'] is True, \
            f"Authentication should succeed with valid credentials for {user_type}"
        assert 'user' in result, "Result should contain user data"
        assert result['user']['email'] == email, "Email should match"
        
    finally:
        # Cleanup
        cleanup_test_user(email, user_type)


@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(credentials=invalid_credentials_strategy())
def test_login_with_invalid_password_fails(credentials):
    """
    Property 1: Login Credential Validation (negative case)
    
    For any login attempt with invalid password, the system should 
    return failure.
    """
    email = credentials['email']
    correct_password = credentials['correct_password']
    wrong_password = credentials['wrong_password']
    user_type = credentials['user_type']
    
    # Create test user with correct password
    try:
        user_id = create_test_user(email, correct_password, user_type)
        
        # Attempt authentication with wrong password
        result = AuthenticationService.authenticate_user(email, wrong_password, user_type)
        
        # Verify failure
        assert result['success'] is False, \
            f"Authentication should fail with invalid password for {user_type}"
        assert 'error' in result, "Result should contain error message"
        assert result['error'] == 'Invalid credentials', \
            "Error message should indicate invalid credentials"
        
    finally:
        # Cleanup
        cleanup_test_user(email, user_type)


@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(
    email=st.emails(),
    password=st.text(min_size=8, max_size=20),
    user_type=st.sampled_from(['admin', 'operator', 'business_owner'])
)
def test_login_with_nonexistent_user_fails(email, password, user_type):
    """
    Property 1: Login Credential Validation (nonexistent user)
    
    For any login attempt with credentials for a user that doesn't exist,
    the system should return failure.
    """
    # Ensure user doesn't exist by cleaning up first
    cleanup_test_user(email, user_type)
    
    # Attempt authentication
    result = AuthenticationService.authenticate_user(email, password, user_type)
    
    # Verify failure
    assert result['success'] is False, \
        f"Authentication should fail for nonexistent {user_type}"
    assert 'error' in result, "Result should contain error message"
    assert result['error'] == 'Invalid credentials', \
        "Error message should indicate invalid credentials"


@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(credentials=valid_user_credentials_strategy())
def test_inactive_user_cannot_login(credentials):
    """
    Property 1: Login Credential Validation (inactive user)
    
    For any login attempt with credentials for an inactive user,
    the system should return failure.
    """
    email = credentials['email']
    password = credentials['password']
    user_type = credentials['user_type']
    
    # Create test user
    user_id = create_test_user(email, password, user_type)
    
    try:
        # Deactivate the user
        conn = get_db_connection()
        cursor = conn.cursor()
        db_type = get_db_type()
        ph = '%s' if db_type == 'postgresql' else '?'
        
        if user_type == 'admin':
            cursor.execute(f"UPDATE super_admins SET is_active = {ph} WHERE email = {ph}", 
                         (False, email))
        elif user_type == 'operator':
            cursor.execute(f"UPDATE erp_staff SET is_active = {ph} WHERE email = {ph}", 
                         (False, email))
        else:  # business_owner
            cursor.execute(f"UPDATE users SET is_active = {ph} WHERE email = {ph}", 
                         (False, email))
        
        conn.commit()
        conn.close()
        
        # Attempt authentication
        result = AuthenticationService.authenticate_user(email, password, user_type)
        
        # Verify failure
        assert result['success'] is False, \
            f"Authentication should fail for inactive {user_type}"
        assert 'error' in result, "Result should contain error message"
        
    finally:
        # Cleanup
        cleanup_test_user(email, user_type)


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])
