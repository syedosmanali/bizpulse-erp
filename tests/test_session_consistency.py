"""
Property-Based Test for Session Consistency

Feature: mobile-login-fix
Property 23: Session consistency is maintained across requests

**Validates: Requirements 4.6**

This test validates that session data remains consistent across multiple
requests and page reloads in the mobile application.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from hypothesis.strategies import composite
import os
import sys
from unittest.mock import patch, MagicMock, Mock
import time
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.auth.service import AuthService
from modules.auth.routes import auth_service


@composite
def valid_session_data_strategy(draw):
    """Generate valid session data for testing"""
    user_types = ['admin', 'client', 'employee', 'staff']
    user_type = draw(st.sampled_from(user_types))
    
    return {
        'user_id': f"user_{draw(st.integers(min_value=1, max_value=9999))}",
        'user_type': user_type,
        'user_name': f"User{draw(st.text(alphabet='abcdefghijklmnopqrstuvwxyz', min_size=3, max_size=10))}",
        'email': f"user{draw(st.integers(min_value=1, max_value=9999))}@example.com",
        'username': f"username_{draw(st.integers(min_value=1, max_value=9999))}",
        'is_super_admin': draw(st.booleans()),
        'business_name': f"Business {draw(st.text(alphabet='abcdefghijklmnopqrstuvwxyz ', min_size=5, max_size=15))}" if user_type in ['admin', 'client'] else None
    }


@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(session_data=valid_session_data_strategy())
def test_session_data_consistency_across_requests(session_data):
    """
    Property 23: Session consistency is maintained across requests
    
    Validates that session data remains consistent when accessed multiple times
    and across different requests.
    """
    # Mock Flask session object
    mock_session = {}
    
    # Populate session with test data
    for key, value in session_data.items():
        if value is not None:  # Only set non-None values
            mock_session[key] = value
    
    # Test multiple accesses to session data
    for i in range(5):  # Test 5 consecutive accesses
        retrieved_user_info = auth_service.get_user_info(mock_session)
        
        # Verify that retrieved data matches original session data
        for key, original_value in session_data.items():
            if original_value is not None:  # Only check non-None values
                retrieved_value = retrieved_user_info.get(key)
                assert retrieved_value == original_value, f"Session data inconsistency for {key}: expected {original_value}, got {retrieved_value}"
    
    print(f"✅ Session consistency verified for user type: {session_data['user_type']}")


@settings(
    max_examples=8,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
def test_session_consistency_with_user_info_endpoint():
    """
    Test that session consistency is maintained when using the user-info endpoint.
    """
    # Create mock session
    mock_session = {
        'user_id': 'test_user_123',
        'user_type': 'client',
        'user_name': 'Test Client',
        'email': 'test@example.com',
        'username': 'test_client',
        'is_super_admin': False
    }
    
    # Test multiple calls to get_user_info
    results = []
    for i in range(3):
        result = auth_service.get_user_info(mock_session)
        results.append(result)
    
    # All results should be identical
    for i in range(1, len(results)):
        assert results[i] == results[0], f"Session consistency failed: result {i} differs from result 0"
    
    print("✅ Session consistency verified across multiple user-info calls")


@settings(
    max_examples=6,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(
    user_id=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', '_-')), min_size=5, max_size=20),
    user_type=st.sampled_from(['admin', 'client', 'employee', 'staff'])
)
def test_session_consistency_different_user_types(user_id, user_type):
    """
    Test session consistency across different user types.
    """
    # Create session data for different user types
    session_data = {
        'user_id': user_id,
        'user_type': user_type,
        'user_name': f"User {user_id}",
        'email': f"{user_id}@example.com",
        'username': user_id,
        'is_super_admin': user_type == 'admin'
    }
    
    # Add type-specific fields
    if user_type == 'client':
        session_data.update({
            'business_name': f"Business {user_id}",
            'business_type': 'retail'
        })
    elif user_type == 'staff':
        session_data.update({
            'staff_role': 'manager'
        })
    
    # Test session consistency
    mock_session = session_data.copy()
    
    # Get user info multiple times
    for i in range(3):
        result = auth_service.get_user_info(mock_session)
        
        # Verify critical fields remain consistent
        assert result['user_id'] == session_data['user_id'], "User ID changed unexpectedly"
        assert result['user_type'] == session_data['user_type'], "User type changed unexpectedly"
        assert result['user_name'] == session_data['user_name'], "User name changed unexpectedly"
        assert result['email'] == session_data['email'], "Email changed unexpectedly"
        assert result['is_super_admin'] == session_data['is_super_admin'], "Super admin status changed unexpectedly"
    
    print(f"✅ Session consistency verified for user type: {user_type}")


def test_session_consistency_after_authentication():
    """
    Test that session consistency is maintained after successful authentication.
    """
    auth_service = AuthService()
    
    # Mock database response for successful authentication
    with patch('modules.auth.service.get_db_connection') as mock_conn:
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            'id': 'test_user_456',
            'email': 'consistency@test.com',
            'business_name': 'Consistency Test',
            'business_type': 'retail',
            'password_hash': 'hashed_password',
            'is_active': True
        }
        mock_conn.return_value.cursor.return_value = mock_cursor
        mock_conn.return_value.commit = MagicMock()
        
        with patch('modules.auth.service.hash_password', return_value='hashed_password'):
            # Authenticate user
            auth_result = auth_service.authenticate_user('consistency@test.com', 'valid_password')
            
            assert auth_result['success'] == True, "Authentication should succeed"
            
            # Simulate session data from authentication
            mock_session = auth_result['session_data'].copy()
            
            # Test session consistency by retrieving user info multiple times
            for i in range(3):
                user_info = auth_service.get_user_info(mock_session)
                
                # Verify session data consistency
                assert user_info['user_id'] == mock_session['user_id']
                assert user_info['user_type'] == mock_session['user_type']
                assert user_info['user_name'] == mock_session['user_name']
                assert user_info['email'] == mock_session['email']
    
    print("✅ Session consistency verified after authentication")


def test_session_field_consistency():
    """
    Test that specific session fields maintain consistency across operations.
    """
    # Define expected session fields
    expected_fields = {
        'user_id': 'consistent_user_789',
        'user_type': 'admin',
        'user_name': 'Consistent User',
        'email': 'consistent@example.com',
        'username': 'consistent_user',
        'is_super_admin': True
    }
    
    # Create mock session
    mock_session = expected_fields.copy()
    
    # Test field consistency across multiple operations
    for operation_count in range(5):
        # Simulate different operations that access session data
        user_info = auth_service.get_user_info(mock_session)
        
        # Verify each field remains consistent
        for field, expected_value in expected_fields.items():
            actual_value = user_info.get(field)
            assert actual_value == expected_value, f"Field {field} inconsistent: expected {expected_value}, got {actual_value}"
        
        # Simulate session refresh/update
        refreshed_session = mock_session.copy()
        assert refreshed_session == mock_session, "Session data changed during refresh"
    
    print("✅ All session fields maintained consistency across operations")


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])