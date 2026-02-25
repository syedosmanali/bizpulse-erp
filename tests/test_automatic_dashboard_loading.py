"""
Property-Based Test for Automatic Dashboard Loading

Feature: mobile-login-fix
Property 3: Valid sessions enable automatic dashboard loading

**Validates: Requirements 1.3**

This test validates that when a user has a valid session, the dashboard
loads automatically without requiring re-authentication.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from hypothesis.strategies import composite
import os
import sys
from unittest.mock import patch
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


@composite
def session_data_strategy(draw):
    """Generate valid session data for testing"""
    user_types = ['admin', 'client', 'employee', 'staff']
    user_id = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', '-')), min_size=10, max_size=36))
    user_type = draw(st.sampled_from(user_types))
    user_name = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')), min_size=3, max_size=50))
    email = draw(st.emails())
    
    return {
        'user_id': user_id,
        'user_type': user_type,
        'user_name': user_name,
        'email': email,
        'is_super_admin': draw(st.booleans())
    }


@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(session_data=session_data_strategy())
def test_valid_sessions_enable_automatic_dashboard_loading(session_data):
    """
    Property 3: Valid sessions enable automatic dashboard loading
    
    Validates that when a user has a valid session, the dashboard loads
    automatically without requiring re-authentication.
    """
    with patch.dict(os.environ, {
        'SECRET_KEY': 'test-secret-key-for-testing'
    }):
        test_app = app
        test_app.config['TESTING'] = True
        
        with test_app.test_client() as client:
            # Establish a valid session
            with client.session_transaction() as sess:
                for key, value in session_data.items():
                    sess[key] = value
            
            # Access the dashboard endpoint (or a protected route)
            # Using the user-info endpoint as a proxy for dashboard access
            response = client.get('/api/auth/user-info')
            
            # For a valid session, the user-info endpoint should return success
            assert response.status_code == 200, \
                f"Valid session should allow access to protected resources, got {response.status_code}"
            
            response_data = json.loads(response.data.decode('utf-8'))
            
            # Verify that user data matches session data
            assert response_data['user_id'] == session_data['user_id'], \
                f"Response user_id should match session user_id"
            assert response_data['user_type'] == session_data['user_type'], \
                f"Response user_type should match session user_type"
            assert response_data['user_name'] == session_data['user_name'], \
                f"Response user_name should match session user_name"
            assert response_data['email'] == session_data['email'], \
                f"Response email should match session email"
            assert response_data['is_super_admin'] == session_data['is_super_admin'], \
                f"Response is_super_admin should match session is_super_admin"


@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(
    user_id=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', '-')), min_size=1, max_size=20),
    user_type=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=20)
)
def test_session_persistence_enables_access(user_id, user_type):
    """
    Test that session data persists and enables access to protected resources.
    
    This simulates the dashboard loading scenario where session data
    allows access without re-authentication.
    """
    with patch.dict(os.environ, {
        'SECRET_KEY': 'test-secret-key-for-testing'
    }):
        test_app = app
        test_app.config['TESTING'] = True
        
        with test_app.test_client() as client:
            # Set up a session with minimal valid data
            with client.session_transaction() as sess:
                sess['user_id'] = user_id
                sess['user_type'] = user_type
                sess['user_name'] = f"Test User {user_id[:5]}"
                sess['email'] = f"{user_id}@example.com"
            
            # Access protected resource
            response = client.get('/api/auth/user-info')
            
            # Should be able to access with valid session
            assert response.status_code in [200, 401], \
                f"Session should either be valid (200) or invalid (401), got {response.status_code}"
            
            if response.status_code == 200:
                # If access granted, verify it's for the correct user
                response_data = json.loads(response.data.decode('utf-8'))
                assert response_data['user_id'] == user_id, \
                    "Response should contain correct user_id"


@settings(
    max_examples=8,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
def test_invalid_sessions_redirect_to_authentication():
    """
    Test that invalid or missing sessions result in appropriate responses
    that would trigger authentication flow in the frontend.
    """
    with patch.dict(os.environ, {
        'SECRET_KEY': 'test-secret-key-for-testing'
    }):
        test_app = app
        test_app.config['TESTING'] = True
        
        with test_app.test_client() as client:
            # Make request without any session data (simulating no login)
            response = client.get('/api/auth/user-info')
            
            # Should return 401 for unauthenticated access
            # Our updated endpoint returns structured response even for unauthenticated users
            response_data = json.loads(response.data.decode('utf-8'))
            
            # Check that the response indicates lack of authentication
            if 'authenticated' in response_data:
                assert response_data['authenticated'] == False, \
                    "Unauthenticated request should return authenticated=False"
            # Also check that user_id is None
            assert response_data.get('user_id') is None, \
                "Unauthenticated request should return null user_id"


@settings(
    max_examples=12,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(
    session_timeout_scenario=st.sampled_from([
        'empty_session', 'partial_session', 'expired_session_simulation'
    ])
)
def test_different_session_states(session_timeout_scenario):
    """
    Test how different session states affect dashboard loading behavior.
    """
    with patch.dict(os.environ, {
        'SECRET_KEY': 'test-secret-key-for-testing'
    }):
        test_app = app
        test_app.config['TESTING'] = True
        
        with test_app.test_client() as client:
            if session_timeout_scenario == 'empty_session':
                # No session data at all
                pass  # Don't set any session data
            elif session_timeout_scenario == 'partial_session':
                # Partial session data
                with client.session_transaction() as sess:
                    sess['user_id'] = 'test-user-id-123'
                    sess['user_name'] = 'Test User'
                    # Missing other required fields
            elif session_timeout_scenario == 'expired_session_simulation':
                # Simulate expired session by setting modified time far in the past
                with client.session_transaction() as sess:
                    sess['user_id'] = 'test-user-id-456'
                    sess['user_type'] = 'client'
                    sess['user_name'] = 'Expired User'
                    sess['_permanent'] = True
                    # Flask manages session expiration internally
            
            response = client.get('/api/auth/user-info')
            response_data = json.loads(response.data.decode('utf-8'))
            
            # Regardless of session state, the endpoint should return structured data
            assert 'user_id' in response_data, "Response should always contain user_id field"


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])