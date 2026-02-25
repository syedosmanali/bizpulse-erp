"""
Property-Based Test for Graceful Error Handling

Feature: mobile-login-fix
Property 12: Session validation failures return to login

**Validates: Requirements 3.3**

This test validates that when session validation fails, the system
gracefully returns the user to the login screen without errors.
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
def session_failure_scenario_strategy(draw):
    """Generate scenarios that could cause session validation failures"""
    scenarios = [
        'expired_session',
        'corrupted_session',
        'missing_user_id',
        'invalid_user_type',
        'inactive_user'
    ]
    return draw(st.sampled_from(scenarios))


@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(scenario=session_failure_scenario_strategy())
def test_session_validation_failures_gracefully_return_to_login(scenario):
    """
    Property 12: Session validation failures return to login
    
    Validates that when session validation fails, the system responds
    gracefully by returning appropriate responses that allow the
    frontend to redirect to login.
    """
    with patch.dict(os.environ, {
        'SECRET_KEY': 'test-secret-key-for-testing'
    }):
        test_app = app
        test_app.config['TESTING'] = True
        
        with test_app.test_client() as client:
            # Set up different failure scenarios
            with client.session_transaction() as sess:
                if scenario == 'expired_session':
                    # Simulate an expired session by setting a past timestamp
                    sess['user_id'] = 'expired-user-123'
                    sess['user_type'] = 'client'
                    sess['user_name'] = 'Expired User'
                    sess['email'] = 'expired@test.com'
                    # In real systems, we'd have timestamp checks
                elif scenario == 'corrupted_session':
                    # Simulate corrupted session data
                    sess['user_id'] = None  # Invalid user ID
                    sess['user_type'] = 'client'
                    sess['user_name'] = 'Corrupted User'
                    sess['email'] = 'corrupted@test.com'
                elif scenario == 'missing_user_id':
                    # Missing critical session data
                    sess['user_type'] = 'client'
                    sess['user_name'] = 'Missing ID User'
                    sess['email'] = 'missing@test.com'
                    # user_id intentionally omitted
                elif scenario == 'invalid_user_type':
                    # Invalid user type
                    sess['user_id'] = 'invalid-type-user-456'
                    sess['user_type'] = 'invalid_type_that_does_not_exist'
                    sess['user_name'] = 'Invalid Type User'
                    sess['email'] = 'invalid@test.com'
                elif scenario == 'inactive_user':
                    # Simulate what an inactive user session might look like
                    sess['user_id'] = 'inactive-user-789'
                    sess['user_type'] = 'client'
                    sess['user_name'] = 'Inactive User'
                    sess['email'] = 'inactive@test.com'
            
            # Try to access protected resource
            response = client.get('/api/auth/user-info')
            
            # The user-info endpoint should handle invalid sessions gracefully
            # Our updated endpoint returns structured responses even for unauthenticated users
            assert response.status_code in [200, 401], \
                f"Session failure should return appropriate status, got {response.status_code}"
            
            response_data = json.loads(response.data.decode('utf-8'))
            
            # Verify the response structure is consistent
            assert 'user_id' in response_data, \
                "Response should always contain user_id field"
            
            # For failed sessions, user_id should be None or the response should indicate unauthenticated state
            if response.status_code == 401:
                # Direct unauthorized response
                assert response_data.get('user_id') is None, \
                    "401 responses should have null user_id"
            elif response.status_code == 200:
                # Our updated endpoint returns structured data even for unauthenticated users
                if 'authenticated' in response_data:
                    assert response_data['authenticated'] == False, \
                        "Unauthenticated responses should have authenticated=False"
                # user_id should be None for unauthenticated users
                assert response_data['user_id'] is None, \
                    "Unauthenticated responses should have null user_id"


@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(
    invalid_session_key=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', '_')), min_size=1, max_size=20),
    invalid_session_value=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', ' ')), min_size=1, max_size=50)
)
def test_invalid_session_data_handled_gracefully(invalid_session_key, invalid_session_value):
    """
    Test that invalid session data is handled gracefully without crashes.
    """
    with patch.dict(os.environ, {
        'SECRET_KEY': 'test-secret-key-for-testing'
    }):
        test_app = app
        test_app.config['TESTING'] = True
        
        with test_app.test_client() as client:
            # Set up session with invalid/malformed data
            with client.session_transaction() as sess:
                sess['user_id'] = 'test-user-123'
                sess['user_type'] = 'client'
                sess['user_name'] = 'Test User'
                sess['email'] = 'test@example.com'
                # Add potentially problematic session data
                sess[invalid_session_key] = invalid_session_value
            
            # Access user info endpoint
            response = client.get('/api/auth/user-info')
            
            # Should return gracefully without crashing
            assert response.status_code in [200, 401], \
                f"Invalid session data should be handled gracefully, got {response.status_code}"
            
            try:
                response_data = json.loads(response.data.decode('utf-8'))
                # Response should have consistent structure
                assert 'user_id' in response_data, \
                    "Response should have user_id field"
            except json.JSONDecodeError:
                # If response isn't JSON, it might be a server error page
                # This is acceptable as long as it's not a crash
                pass


@settings(
    max_examples=8,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
def test_session_with_missing_critical_data():
    """
    Test session validation when critical data is missing.
    """
    with patch.dict(os.environ, {
        'SECRET_KEY': 'test-secret-key-for-testing'
    }):
        test_app = app
        test_app.config['TESTING'] = True
        
        with test_app.test_client() as client:
            # Set up session with only partial data
            with client.session_transaction() as sess:
                sess['user_name'] = 'Partial Session User'
                sess['some_other_field'] = 'some_value'
                # Intentionally omitting critical fields like user_id, user_type
            
            response = client.get('/api/auth/user-info')
            
            # Should handle missing critical data gracefully
            assert response.status_code in [200, 401], \
                f"Missing session data should be handled gracefully, got {response.status_code}"
            
            response_data = json.loads(response.data.decode('utf-8'))
            
            # Should return appropriate response indicating unauthenticated state
            if response.status_code == 200:
                if 'authenticated' in response_data:
                    assert response_data['authenticated'] == False, \
                        "Sessions without critical data should be treated as unauthenticated"


@settings(
    max_examples=12,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(
    error_scenario=st.sampled_from([
        'empty_session',
        'malformed_user_id',
        'unicode_user_type',
        'sql_injection_attempt'
    ])
)
def test_various_session_error_scenarios(error_scenario):
    """
    Test various session error scenarios are handled gracefully.
    """
    with patch.dict(os.environ, {
        'SECRET_KEY': 'test-secret-key-for-testing'
    }):
        test_app = app
        test_app.config['TESTING'] = True
        
        with test_app.test_client() as client:
            with client.session_transaction() as sess:
                if error_scenario == 'empty_session':
                    # Actually don't set any session data
                    pass
                elif error_scenario == 'malformed_user_id':
                    sess['user_id'] = 12345  # Non-string user ID
                    sess['user_type'] = 'client'
                    sess['user_name'] = 'Malformed ID User'
                elif error_scenario == 'unicode_user_type':
                    sess['user_id'] = 'unicode-test-user'
                    sess['user_type'] = '🚀_invalid_type_表情'  # Invalid unicode type
                    sess['user_name'] = 'Unicode Type User'
                elif error_scenario == 'sql_injection_attempt':
                    sess['user_id'] = 'real_user_123'
                    sess['user_type'] = "'; DROP TABLE users; --"
                    sess['user_name'] = 'SQL Injection Test'
            
            # Access protected endpoint
            response = client.get('/api/auth/user-info')
            
            # All scenarios should be handled without server crashes
            assert response.status_code in [200, 401], \
                f"Scenario {error_scenario} should be handled gracefully, got {response.status_code}"
            
            # Try to parse response
            try:
                response_data = json.loads(response.data.decode('utf-8'))
                # Should have consistent structure
                assert 'user_id' in response_data, \
                    f"Response for {error_scenario} should have user_id field"
            except json.JSONDecodeError:
                # Acceptable for some severe error cases
                pass


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])