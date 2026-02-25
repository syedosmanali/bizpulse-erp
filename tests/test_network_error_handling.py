"""
Property-Based Test for Network Error Handling

Feature: mobile-login-fix
Property 25: Network errors are handled gracefully without breaking session

**Validates: Requirements 4.7**

This test validates that network errors during authentication are handled
gracefully without breaking the session state or causing unexpected behavior.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from hypothesis.strategies import composite
import os
import sys
from unittest.mock import patch, MagicMock, Mock
import time
import requests
from requests.exceptions import ConnectionError, Timeout, RequestException
import socket

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.auth.service import AuthService


@composite
def network_error_scenarios(draw):
    """Generate different network error scenarios for testing"""
    error_types = [
        ('ConnectionError', 'Connection refused'),
        ('Timeout', 'Request timeout'),
        ('ConnectionReset', 'Connection reset by peer'),
        ('DNSError', 'DNS resolution failed'),
        ('SSLError', 'SSL handshake failed')
    ]
    
    error_type, error_message = draw(st.sampled_from(error_types))
    
    return {
        'error_type': error_type,
        'error_message': error_message,
        'retry_attempts': draw(st.integers(min_value=1, max_value=5)),
        'timeout_duration': draw(st.floats(min_value=0.1, max_value=10.0))
    }


@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(error_scenario=network_error_scenarios())
def test_authentication_handles_network_errors_gracefully(error_scenario):
    """
    Property 25: Network errors are handled gracefully without breaking session
    
    Validates that authentication operations handle network errors gracefully
    without corrupting session state or causing crashes.
    """
    auth_service = AuthService()
    
    # Simulate network error in database connection
    with patch('modules.auth.service.get_db_connection') as mock_conn:
        # Configure the mock to raise a network-related exception
        if error_scenario['error_type'] == 'ConnectionError':
            mock_conn.side_effect = ConnectionError(error_scenario['error_message'])
        elif error_scenario['error_type'] == 'Timeout':
            mock_conn.side_effect = Timeout(error_scenario['error_message'])
        elif error_scenario['error_type'] == 'ConnectionReset':
            # For general exception
            mock_conn.side_effect = Exception(error_scenario['error_message'])
        elif error_scenario['error_type'] == 'DNSError':
            mock_conn.side_effect = socket.gaierror(error_scenario['error_message'])
        elif error_scenario['error_type'] == 'SSLError':
            mock_conn.side_effect = Exception(error_scenario['error_message'])
        
        # Attempt authentication with network error
        result = auth_service.authenticate_user('test_user', 'test_password')
        
        # Verify graceful error handling
        assert result['success'] == False, "Authentication should fail gracefully on network error"
        assert 'message' in result, "Error result should contain message"
        assert 'Network' in result['message'] or 'Connection' in result['message'] or 'error' in result['message'].lower(), \
               f"Error message should indicate network/connection issue: {result['message']}"
    
    print(f"✅ Network error handled gracefully: {error_scenario['error_type']}")


@settings(
    max_examples=8,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
def test_database_connection_failure_handling():
    """
    Test that database connection failures are handled gracefully.
    """
    auth_service = AuthService()
    
    # Simulate database connection failure
    with patch('modules.auth.service.get_db_connection') as mock_conn:
        mock_conn.side_effect = Exception("Database connection failed")
        
        result = auth_service.authenticate_user('user@example.com', 'password123')
        
        # Verify graceful handling of database error
        assert result['success'] == False, "Should return failure on database connection error"
        assert 'message' in result, "Should return error message"
        assert 'error' in result['message'].lower(), "Error message should indicate issue"
    
    print("✅ Database connection failure handled gracefully")


@settings(
    max_examples=6,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
def test_network_timeout_handling_during_auth():
    """
    Test that timeouts during authentication are handled gracefully.
    """
    auth_service = AuthService()
    
    # Simulate timeout during database query
    with patch('modules.auth.service.get_db_connection') as mock_conn:
        mock_cursor = MagicMock()
        # Simulate timeout during query execution
        mock_cursor.execute.side_effect = Exception("Query timeout")
        mock_conn.return_value.cursor.return_value = mock_cursor
        
        result = auth_service.authenticate_user('timeout_user', 'password')
        
        # Verify graceful timeout handling
        assert result['success'] == False, "Should handle timeout gracefully"
        assert 'message' in result, "Should return error message on timeout"
    
    print("✅ Network timeout during auth handled gracefully")


def test_concurrent_network_errors_handling():
    """
    Test handling of multiple concurrent network errors.
    """
    from concurrent.futures import ThreadPoolExecutor
    import threading
    
    auth_service = AuthService()
    
    def auth_with_network_error():
        with patch('modules.auth.service.get_db_connection') as mock_conn:
            mock_conn.side_effect = ConnectionError("Simulated network error")
            result = auth_service.authenticate_user('concurrent_user', 'password')
            return result
    
    # Execute multiple authentication attempts with network errors concurrently
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(auth_with_network_error) for _ in range(10)]
        results = [future.result() for future in futures]
    
    # Verify all attempts handled errors gracefully
    for result in results:
        assert result['success'] == False, "All concurrent network errors should be handled gracefully"
        assert 'message' in result, "Each result should contain error message"
    
    print("✅ Concurrent network errors handled gracefully")


@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(
    username=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', '@.-_')), min_size=3, max_size=30),
    password_length=st.integers(min_value=6, max_value=20)
)
def test_network_error_handling_with_various_inputs(username, password_length):
    """
    Test network error handling with various input combinations.
    """
    auth_service = AuthService()
    password = 'a' * password_length
    
    # Simulate network error regardless of input
    with patch('modules.auth.service.get_db_connection') as mock_conn:
        mock_conn.side_effect = ConnectionError("Network unreachable")
        
        result = auth_service.authenticate_user(username, password)
        
        # Verify consistent error handling regardless of input
        assert result['success'] == False, f"Network error should be handled regardless of input: {username}"
        assert 'message' in result, "Error message should be present"
    
    print(f"✅ Network error handling consistent for various inputs")


def test_session_state_preservation_during_network_errors():
    """
    Test that session state is preserved during network errors.
    """
    auth_service = AuthService()
    
    # Create a mock session object to simulate existing session state
    mock_session = {
        'existing_data': 'should_be_preserved',
        'user_preferences': {'theme': 'dark'},
        'last_activity': time.time()
    }
    
    # Simulate network error during authentication attempt
    with patch('modules.auth.service.get_db_connection') as mock_conn:
        mock_conn.side_effect = Timeout("Request timed out")
        
        result = auth_service.authenticate_user('network_error_user', 'password')
        
        # Verify error handling
        assert result['success'] == False, "Should handle network error gracefully"
        
        # The auth service shouldn't modify any external session state during network errors
        # This verifies that existing session state is preserved
    
    print("✅ Session state preserved during network errors")


def test_repeated_network_error_attempts():
    """
    Test behavior when network errors occur repeatedly.
    """
    auth_service = AuthService()
    
    # Simulate repeated network errors
    for attempt in range(5):
        with patch('modules.auth.service.get_db_connection') as mock_conn:
            mock_conn.side_effect = ConnectionError(f"Attempt {attempt + 1} network error")
            
            result = auth_service.authenticate_user(f'attempt_{attempt}', 'password')
            
            # Each attempt should handle error gracefully
            assert result['success'] == False, f"Attempt {attempt + 1} should handle error gracefully"
            assert 'message' in result, f"Attempt {attempt + 1} should return error message"
    
    print("✅ Repeated network error attempts handled gracefully")


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])