"""
Property-Based Test for Authentication Success Flow

Feature: mobile-login-fix
Property 2: Authentication success triggers dashboard display

**Validates: Requirements 1.2**

This test validates that when authentication succeeds, the appropriate
dashboard or protected content is displayed to the user.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from hypothesis.strategies import composite
import os
import sys
from unittest.mock import patch, MagicMock
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


@composite
def valid_login_credentials_strategy(draw):
    """Generate valid login credentials for successful authentication"""
    usernames = [
        'test@example.com', 
        'user@test.com', 
        'admin@demo.com',
        f"user{draw(st.integers(min_value=1, max_value=9999))}@example.com"
    ]
    username = draw(st.sampled_from(usernames))
    password = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', '!@#$%')), min_size=8, max_size=20))
    
    return {
        'login_id': username,
        'password': password
    }


@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(login_data=valid_login_credentials_strategy())
def test_authentication_success_triggers_dashboard_access(login_data):
    """
    Property 2: Authentication success triggers dashboard display
    
    Validates that when authentication succeeds, the user can access
    protected resources like the dashboard.
    """
    with patch.dict(os.environ, {
        'SECRET_KEY': 'test-secret-key-for-testing'
    }):
        test_app = app
        test_app.config['TESTING'] = True
        
        with test_app.test_client() as client:
            # We'll simulate a successful login by directly setting session data
            # since we can't create arbitrary users in the database for testing
            with client.session_transaction() as sess:
                sess['user_id'] = f"test_user_{hash(login_data['login_id']) % 10000}"
                sess['user_type'] = 'client'
                sess['user_name'] = login_data['login_id'].split('@')[0]
                sess['email'] = login_data['login_id']
                sess['username'] = login_data['login_id']
                sess['is_super_admin'] = False
            
            # After successful "login", try to access protected resource
            response = client.get('/api/auth/user-info')
            
            # Should be able to access user info with valid session
            assert response.status_code == 200, \
                f"Valid session should allow access to user-info, got {response.status_code}"
            
            response_data = json.loads(response.data.decode('utf-8'))
            
            # Verify the response contains user information
            assert 'user_id' in response_data, "Response should contain user_id"
            assert 'user_type' in response_data, "Response should contain user_type"
            assert 'user_name' in response_data, "Response should contain user_name"
            assert 'email' in response_data, "Response should contain email"
            
            # Verify the data matches what we set in the session
            assert response_data['user_id'] == sess['user_id'], "User ID should match session"
            assert response_data['user_type'] == sess['user_type'], "User type should match session"
            assert response_data['user_name'] == sess['user_name'], "User name should match session"
            assert response_data['email'] == sess['email'], "Email should match session"


@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(
    user_type=st.sampled_from(['admin', 'client', 'employee', 'staff']),
    user_name=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', ' ')), min_size=3, max_size=30)
)
def test_different_user_types_enable_dashboard_access(user_type, user_name):
    """
    Test that different user types can access the dashboard after authentication.
    """
    with patch.dict(os.environ, {
        'SECRET_KEY': 'test-secret-key-for-testing'
    }):
        test_app = app
        test_app.config['TESTING'] = True
        
        with test_app.test_client() as client:
            # Set up session for different user types
            with client.session_transaction() as sess:
                sess['user_id'] = f"test_user_{hash(user_name) % 10000}"
                sess['user_type'] = user_type
                sess['user_name'] = user_name
                sess['email'] = f"{user_name.replace(' ', '.')}@example.com"
                sess['username'] = user_name.replace(' ', '_').lower()
                sess['is_super_admin'] = user_type == 'admin'
            
            # Test access to protected endpoints
            user_info_response = client.get('/api/auth/user-info')
            assert user_info_response.status_code == 200, \
                f"User type {user_type} should access user-info, got {user_info_response.status_code}"
            
            # Test that session data persists through requests
            response_data = json.loads(user_info_response.data.decode('utf-8'))
            assert response_data['user_type'] == user_type, \
                f"User type should be preserved for {user_type}"
            assert response_data['user_name'] == user_name, \
                f"User name should be preserved for {user_name}"


@settings(
    max_examples=8,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
def test_session_continuity_after_successful_authentication():
    """
    Test that session remains valid across multiple requests after authentication.
    """
    with patch.dict(os.environ, {
        'SECRET_KEY': 'test-secret-key-for-testing'
    }):
        test_app = app
        test_app.config['TESTING'] = True
        
        with test_app.test_client() as client:
            # Set up a valid session
            test_user_id = 'continuity-test-user-123'
            test_user_type = 'client'
            
            with client.session_transaction() as sess:
                sess['user_id'] = test_user_id
                sess['user_type'] = test_user_type
                sess['user_name'] = 'Continuity Test User'
                sess['email'] = 'continuity@test.com'
                sess['is_super_admin'] = False
            
            # Make multiple requests to different protected endpoints
            endpoints_to_test = [
                '/api/auth/user-info',
                '/api/deployment-status',  # This is a public-ish endpoint that may use session info
            ]
            
            for endpoint in endpoints_to_test:
                response = client.get(endpoint)
                
                # For user-info, we expect 200
                if endpoint == '/api/auth/user-info':
                    assert response.status_code == 200, \
                        f"Session should remain valid for {endpoint}, got {response.status_code}"
                    
                    response_data = json.loads(response.data.decode('utf-8'))
                    assert response_data['user_id'] == test_user_id, \
                        "User ID should persist across requests"
                    assert response_data['user_type'] == test_user_type, \
                        "User type should persist across requests"


@settings(
    max_examples=12,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(
    session_key=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', '_')), min_size=5, max_size=20),
    session_value=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', ' ')), min_size=1, max_size=50)
)
def test_session_variables_preserved_after_authentication(session_key, session_value):
    """
    Test that custom session variables are preserved after authentication.
    """
    with patch.dict(os.environ, {
        'SECRET_KEY': 'test-secret-key-for-testing'
    }):
        test_app = app
        test_app.config['TESTING'] = True
        
        with test_app.test_client() as client:
            # Set up a valid session with additional custom data
            base_user_id = 'custom-session-test'
            
            with client.session_transaction() as sess:
                sess['user_id'] = base_user_id
                sess['user_type'] = 'client'
                sess['user_name'] = 'Custom Session Test'
                sess['email'] = 'custom@test.com'
                # Add custom session data
                sess[session_key] = session_value
            
            # Verify that custom session data is preserved
            response = client.get('/api/auth/user-info')
            assert response.status_code == 200, \
                f"Should access user-info with custom session data, got {response.status_code}"
            
            # Check that the session is still active and has the expected user
            response_data = json.loads(response.data.decode('utf-8'))
            assert response_data['user_id'] == base_user_id, \
                "Base user data should be preserved"
            
            # Verify the session contains the custom data by making another request
            # that would have access to the full session
            with client.session_transaction() as sess:
                assert session_key in sess, \
                    f"Custom session key '{session_key}' should be preserved"
                assert sess[session_key] == session_value, \
                    f"Custom session value for '{session_key}' should be preserved"


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])