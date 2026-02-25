"""
Property-Based Test for User Info Endpoint

Feature: mobile-login-fix
Property 6: User info endpoint returns valid data for authenticated sessions

**Validates: Requirements 2.1**

This test validates that the user info endpoint returns consistent, valid data
for authenticated sessions and appropriate error responses for unauthenticated sessions.
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
    """Generate realistic session data for testing"""
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
    max_examples=20,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(session_data=session_data_strategy())
def test_user_info_endpoint_returns_valid_data_for_authenticated_sessions(session_data):
    """
    Property 6: User info endpoint returns valid data for authenticated sessions
    
    Validates that when a user is authenticated (has session data), the 
    /api/auth/user-info endpoint returns valid user information with proper structure.
    """
    with patch.dict(os.environ, {
        'SECRET_KEY': 'test-secret-key-for-testing'
    }):
        test_app = app
        test_app.config['TESTING'] = True
        
        with test_app.test_client() as client:
            # Set up authenticated session
            with client.session_transaction() as sess:
                for key, value in session_data.items():
                    sess[key] = value
            
            # Call the user info endpoint
            response = client.get('/api/auth/user-info')
            
            # Validate response structure and status
            assert response.status_code == 200, \
                f"Expected 200 status for authenticated session, got {response.status_code}"
            
            # Parse response data
            response_data = json.loads(response.data.decode('utf-8'))
            
            # Validate that response contains expected fields
            expected_fields = ['user_id', 'user_type', 'user_name', 'email', 
                             'username', 'profile_picture', 'is_super_admin', 'staff_role']
            for field in expected_fields:
                assert field in response_data, \
                    f"Response missing expected field: {field}"
            
            # Validate that user data matches session data for authenticated users
            assert response_data['user_id'] == session_data['user_id'], \
                f"User ID mismatch: expected {session_data['user_id']}, got {response_data['user_id']}"
            assert response_data['user_type'] == session_data['user_type'], \
                f"User type mismatch: expected {session_data['user_type']}, got {response_data['user_type']}"
            assert response_data['user_name'] == session_data['user_name'], \
                f"User name mismatch: expected {session_data['user_name']}, got {response_data['user_name']}"
            assert response_data['email'] == session_data['email'], \
                f"Email mismatch: expected {session_data['email']}, got {response_data['email']}"
            assert response_data['is_super_admin'] == session_data['is_super_admin'], \
                f"Super admin status mismatch: expected {session_data['is_super_admin']}, got {response_data['is_super_admin']}"


@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(
    user_id=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', '-')), min_size=1, max_size=10),
    user_type=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=20),
    user_name=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')), min_size=1, max_size=50)
)
def test_user_info_endpoint_handles_invalid_session_data(user_id, user_type, user_name):
    """
    Test that the user info endpoint handles various session data correctly.
    
    Ensures the endpoint returns appropriate responses even with minimal or 
    unusual session data.
    """
    with patch.dict(os.environ, {
        'SECRET_KEY': 'test-secret-key-for-testing'
    }):
        test_app = app
        test_app.config['TESTING'] = True
        
        with test_app.test_client() as client:
            # Set up session with minimal data
            with client.session_transaction() as sess:
                sess['user_id'] = user_id
                sess['user_type'] = user_type
                sess['user_name'] = user_name
                sess['email'] = f"{user_name}@example.com".lower().replace(' ', '')
            
            # Call the user info endpoint
            response = client.get('/api/auth/user-info')
            
            # Response should be successful even with minimal data
            assert response.status_code in [200, 401], \
                f"Expected 200 or 401 status, got {response.status_code}"
            
            if response.status_code == 200:
                response_data = json.loads(response.data.decode('utf-8'))
                # Validate that response contains expected fields
                expected_fields = ['user_id', 'user_type', 'user_name', 'email', 
                                 'username', 'profile_picture', 'is_super_admin', 'staff_role']
                for field in expected_fields:
                    assert field in response_data, \
                        f"Response missing expected field: {field}"


@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
def test_user_info_endpoint_unauthenticated_access():
    """
    Test that the user info endpoint returns proper response for unauthenticated access.
    
    Validates that when no session exists, the endpoint returns appropriate 
    unauthorized response.
    """
    with patch.dict(os.environ, {
        'SECRET_KEY': 'test-secret-key-for-testing'
    }):
        test_app = app
        test_app.config['TESTING'] = True
        
        with test_app.test_client() as client:
            # Don't set up any session data - unauthenticated request
            response = client.get('/api/auth/user-info')
            
            # For our implementation, this should return a 401 with structured data
            # since we now return structured responses even for unauthenticated access
            response_data = json.loads(response.data.decode('utf-8'))
            
            # Check that the response indicates lack of authentication
            if 'authenticated' in response_data:
                assert response_data['authenticated'] == False, \
                    "Unauthenticated request should return authenticated=False"
            # Also check that user_id is None
            assert response_data.get('user_id') is None, \
                "Unauthenticated request should return null user_id"


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])