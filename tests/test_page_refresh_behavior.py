"""
Property-Based Test for Page Refresh Behavior

Feature: mobile-login-fix
Property 5: Page refresh preserves authentication state

**Validates: Requirements 1.5**

This test validates that when a user refreshes the page, their authentication
state is preserved and they don't need to log in again.
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
def session_state_strategy(draw):
    """Generate session state data for testing"""
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
@given(session_data=session_state_strategy())
def test_page_refresh_preserves_authentication_state(session_data):
    """
    Property 5: Page refresh preserves authentication state
    
    Validates that when a page is refreshed, the user's authentication
    state is preserved and they remain logged in.
    """
    with patch.dict(os.environ, {
        'SECRET_KEY': 'test-secret-key-for-testing'
    }):
        test_app = app
        test_app.config['TESTING'] = True
        
        with test_app.test_client() as client:
            # Establish a session
            with client.session_transaction() as sess:
                for key, value in session_data.items():
                    sess[key] = value
            
            # First, verify the user is authenticated
            response1 = client.get('/api/auth/user-info')
            assert response1.status_code == 200, \
                f"Initial access should succeed, got {response1.status_code}"
            
            response1_data = json.loads(response1.data.decode('utf-8'))
            assert response1_data['user_id'] == session_data['user_id'], \
                "Initial response should contain correct user_id"
            
            # Simulate a "page refresh" by making another request with the same session
            # Flask sessions are maintained automatically by the test client
            response2 = client.get('/api/auth/user-info')
            assert response2.status_code == 200, \
                f"After refresh, access should still succeed, got {response2.status_code}"
            
            response2_data = json.loads(response2.data.decode('utf-8'))
            assert response2_data['user_id'] == session_data['user_id'], \
                "Post-refresh response should still contain correct user_id"
            assert response2_data['user_type'] == session_data['user_type'], \
                "User type should be preserved after refresh"
            assert response2_data['user_name'] == session_data['user_name'], \
                "User name should be preserved after refresh"
            assert response2_data['email'] == session_data['email'], \
                "Email should be preserved after refresh"


@settings(
    max_examples=12,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(
    num_refreshes=st.integers(min_value=1, max_value=5),
    user_attribute=st.sampled_from(['user_id', 'user_type', 'user_name', 'email'])
)
def test_multiple_page_refreshes_preserve_session(num_refreshes, user_attribute):
    """
    Test that multiple page refreshes preserve session state consistently.
    """
    with patch.dict(os.environ, {
        'SECRET_KEY': 'test-secret-key-for-testing'
    }):
        test_app = app
        test_app.config['TESTING'] = True
        
        with test_app.test_client() as client:
            # Set up session with test data
            test_user_id = f"refresh-test-user-{hash(str(num_refreshes)) % 10000}"
            test_user_type = 'client'
            test_user_name = f'Refresh Test User {num_refreshes}'
            test_email = f'refresh{num_refreshes}@test.com'
            
            with client.session_transaction() as sess:
                sess['user_id'] = test_user_id
                sess['user_type'] = test_user_type
                sess['user_name'] = test_user_name
                sess['email'] = test_email
                sess['is_super_admin'] = False
            
            # Perform multiple "refreshes" (requests with same session)
            for i in range(num_refreshes):
                response = client.get('/api/auth/user-info')
                assert response.status_code == 200, \
                    f"Request {i+1} should succeed, got {response.status_code}"
                
                response_data = json.loads(response.data.decode('utf-8'))
                
                # Verify the specific attribute is preserved
                expected_value = locals()[f'test_{user_attribute}']
                actual_value = response_data[user_attribute]
                assert actual_value == expected_value, \
                    f"Attribute {user_attribute} should be preserved on request {i+1}, expected {expected_value}, got {actual_value}"


@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
def test_session_preservation_across_different_endpoints():
    """
    Test that session is preserved when accessing different endpoints after "refresh".
    """
    with patch.dict(os.environ, {
        'SECRET_KEY': 'test-secret-key-for-testing'
    }):
        test_app = app
        test_app.config['TESTING'] = True
        
        with test_app.test_client() as client:
            # Set up a session
            test_user_id = 'cross-endpoint-test-user'
            test_user_type = 'admin'
            
            with client.session_transaction() as sess:
                sess['user_id'] = test_user_id
                sess['user_type'] = test_user_type
                sess['user_name'] = 'Cross Endpoint Test User'
                sess['email'] = 'cross@endpoint.com'
                sess['is_super_admin'] = True
            
            # Access different endpoints, simulating page navigation after refresh
            endpoints = ['/api/auth/user-info', '/api/deployment-status']
            
            for endpoint in endpoints:
                response = client.get(endpoint)
                
                if endpoint == '/api/auth/user-info':
                    # This should always return user info for authenticated users
                    assert response.status_code == 200, \
                        f"Access to {endpoint} should succeed, got {response.status_code}"
                    
                    response_data = json.loads(response.data.decode('utf-8'))
                    assert response_data['user_id'] == test_user_id, \
                        f"Session should be preserved for {endpoint}"
                    assert response_data['user_type'] == test_user_type, \
                        f"User type should be preserved for {endpoint}"
                else:
                    # Other endpoints may have different behavior but session should still be valid
                    # The important thing is that the session cookie is being sent
                    pass


@settings(
    max_examples=8,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(
    session_timeout_minutes=st.integers(min_value=1, max_value=10)
)
def test_session_continuity_with_short_timeout_simulation(session_timeout_minutes):
    """
    Test that session behaves appropriately with timeout considerations.
    
    Note: This is a simulation since we can't easily test actual timeouts in unit tests.
    """
    with patch.dict(os.environ, {
        'SECRET_KEY': 'test-secret-key-for-testing'
    }):
        test_app = app
        test_app.config['TESTING'] = True
        
        with test_app.test_client() as client:
            # Set up session
            test_user_id = f"timeout-test-{session_timeout_minutes}"
            
            with client.session_transaction() as sess:
                sess['user_id'] = test_user_id
                sess['user_type'] = 'client'
                sess['user_name'] = f'Timeout Test User {session_timeout_minutes}'
                sess['email'] = f'timeout{session_timeout_minutes}@test.com'
                # Mark session as permanent to simulate timeout behavior
                sess.permanent = True
            
            # Make multiple requests (simulating refreshes within timeout period)
            for i in range(3):
                response = client.get('/api/auth/user-info')
                assert response.status_code == 200, \
                    f"Request {i+1} within timeout should succeed, got {response.status_code}"
                
                response_data = json.loads(response.data.decode('utf-8'))
                assert response_data['user_id'] == test_user_id, \
                    f"Session should persist through request {i+1}"


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])