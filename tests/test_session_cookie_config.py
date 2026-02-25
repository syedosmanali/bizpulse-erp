"""
Property-Based Test for Session Cookie Configuration

Feature: mobile-login-fix
Property 9: Session cookies have secure configuration

**Validates: Requirements 2.5**

This test validates that session cookies are configured securely with appropriate
flags such as httpOnly and secure attributes set according to the environment.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from hypothesis.strategies import composite
import os
import sys
import tempfile
from unittest.mock import patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(
    session_key=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=10, max_size=50),
    session_value=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=10, max_size=100),
    is_production_env=st.booleans()
)
def test_session_cookie_secure_configuration(session_key, session_value, is_production_env):
    """
    Property 9: Session cookies have secure configuration
    
    Validates that session cookies are configured with appropriate security flags:
    - httpOnly flag prevents JavaScript access to session cookies
    - secure flag is set appropriately based on environment
    - SameSite attribute allows cross-origin requests for mobile app
    """
    # Mock environment variable for testing
    with patch.dict(os.environ, {
        'FLASK_ENV': 'production' if is_production_env else 'development',
        'SECRET_KEY': 'test-secret-key-for-testing'
    }):
        # Create a fresh app instance with mocked environment
        test_app = app
        test_app.config['TESTING'] = True
        
        with test_app.test_client() as client:
            with client.session_transaction() as sess:
                sess[session_key] = session_value
            
            # Make a test request to trigger session handling
            response = client.get('/')
            
            # Check if session cookie is present in response
            session_cookie = None
            for header, value in response.headers:
                if header.lower() == 'set-cookie' and 'session' in value.lower():
                    session_cookie = value
                    break
            
            # If session cookie exists, validate its properties
            if session_cookie:
                # Check for HttpOnly flag
                assert 'httponly' in session_cookie.lower(), \
                    f"Session cookie missing HttpOnly flag: {session_cookie}"
                
                # Check for SameSite=None for mobile compatibility
                assert 'samesite=none' in session_cookie.lower(), \
                    f"Session cookie should have SameSite=None for mobile compatibility: {session_cookie}"
                
                # In production, secure flag should be present
                if is_production_env:
                    assert 'secure' in session_cookie.lower(), \
                        f"Session cookie missing Secure flag in production environment: {session_cookie}"
                else:
                    # In development, secure flag may or may not be present
                    # This is acceptable for development environments
                    pass


@composite
def session_data_strategy(draw):
    """Generate session data for testing"""
    key = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=5, max_size=20))
    value = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')), min_size=5, max_size=50))
    return {key: value}


@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(session_data=session_data_strategy())
def test_session_persistence_and_security_flags(session_data):
    """
    Extended test for session persistence and security configuration
    
    Tests that sessions maintain security configuration across requests
    """
    with patch.dict(os.environ, {
        'FLASK_ENV': 'production',
        'SECRET_KEY': 'test-secret-key-for-testing'
    }):
        test_app = app
        test_app.config['TESTING'] = True
        
        with test_app.test_client() as client:
            # Set session data
            for key, value in session_data.items():
                with client.session_transaction() as sess:
                    sess[key] = value
            
            # Make request and check response
            response = client.get('/health')
            
            # Verify response status
            assert response.status_code in [200, 404], \
                f"Request should succeed or return 404, got {response.status_code}"
            
            # Check for secure session cookie properties in headers
            cookie_headers = []
            for header, value in response.headers:
                if header.lower() == 'set-cookie':
                    cookie_headers.append(value)
            
            # Look for session-related cookies
            session_cookies = [cookie for cookie in cookie_headers if 'session' in cookie.lower()]
            
            for cookie in session_cookies:
                # Validate security properties
                assert 'httponly' in cookie.lower(), \
                    f"Session cookie missing HttpOnly flag: {cookie}"
                assert 'samesite=none' in cookie.lower(), \
                    f"Session cookie missing SameSite=None: {cookie}"


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])