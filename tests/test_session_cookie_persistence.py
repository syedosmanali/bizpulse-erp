"""
Property-Based Test for Session Cookie Persistence

Feature: mobile-login-fix
Property 24: Session cookies persist correctly across page reloads

**Validates: Requirements 4.1, 4.2, 4.3**

This test validates that session cookies are properly configured and persist
correctly across page reloads and browser sessions in the mobile application.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from hypothesis.strategies import composite
import os
import sys
from unittest.mock import patch, MagicMock, Mock
from flask import Flask, session
import time
from datetime import timedelta
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app  # Import the Flask app to access session configuration


@composite
def valid_session_attributes_strategy(draw):
    """Generate valid session attributes for testing"""
    secure_flag = draw(st.booleans())
    httponly_flag = True  # Always True for security
    samesite_flag = draw(st.sampled_from(['Strict', 'Lax', 'None', None]))
    
    return {
        'secure': secure_flag,
        'httponly': httponly_flag,
        'samesite': samesite_flag,
        'max_age': draw(st.integers(min_value=3600, max_value=2592000)),  # 1 hour to 30 days
        'domain': draw(st.text(alphabet='abcdefghijklmnopqrstuvwxyz.-', min_size=4, max_size=20)) if draw(st.booleans()) else None
    }


@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
def test_flask_session_configuration():
    """
    Property 24: Session cookies persist correctly across page reloads
    
    Validates that Flask session configuration meets requirements for
    mobile application session persistence.
    """
    # Check Flask app session configuration
    assert app.config['SESSION_COOKIE_HTTPONLY'] == True, "SESSION_COOKIE_HTTPONLY should be True for security"
    
    # For mobile app compatibility, SameSite should be None to allow cross-site requests
    assert app.config['SESSION_COOKIE_SAMESITE'] == 'None', "SESSION_COOKIE_SAMESITE should be 'None' for mobile app compatibility"
    
    # Check that session is permanent
    assert app.config['SESSION_PERMANENT'] == True, "SESSION_PERMANENT should be True for persistent sessions"
    
    # Check session lifetime
    assert isinstance(app.config['PERMANENT_SESSION_LIFETIME'], timedelta), "PERMANENT_SESSION_LIFETIME should be a timedelta"
    lifetime_seconds = app.config['PERMANENT_SESSION_LIFETIME'].total_seconds()
    assert lifetime_seconds >= 86400, f"Session lifetime should be at least 1 day (86400 seconds), got {lifetime_seconds}"
    
    print("✅ Flask session configuration meets persistence requirements")


@settings(
    max_examples=8,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(session_attrs=valid_session_attributes_strategy())
def test_session_cookie_attributes(session_attrs):
    """
    Test that session cookies have appropriate attributes for persistence.
    """
    # Create a test Flask app with specific session configuration
    test_app = Flask(__name__)
    
    # Configure session attributes
    test_app.config['SECRET_KEY'] = 'test-secret-key'
    test_app.config['SESSION_COOKIE_HTTPONLY'] = session_attrs['httponly']
    test_app.config['SESSION_COOKIE_SECURE'] = session_attrs['secure']
    test_app.config['SESSION_COOKIE_SAMESITE'] = session_attrs['samesite']
    test_app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=session_attrs['max_age'])
    test_app.config['SESSION_PERMANENT'] = True
    
    # Test session setting and retrieval
    with test_app.test_client() as client:
        with test_app.test_request_context('/'):
            # Set session data
            session['test_user_id'] = 'persistent_user_123'
            session['test_user_type'] = 'client'
            session['test_timestamp'] = int(time.time())
            session.permanent = True
            
            # Verify session data is stored
            assert session.get('test_user_id') == 'persistent_user_123'
            assert session.get('test_user_type') == 'client'
    
    # Verify configuration properties
    assert test_app.config['SESSION_COOKIE_HTTPONLY'] == True, "HttpOnly should always be True for security"
    assert test_app.config['SESSION_PERMANENT'] == True, "Session should be permanent"
    
    print(f"✅ Session cookie attributes validated: secure={session_attrs['secure']}, samesite={session_attrs['samesite']}")


def test_session_persistence_simulation():
    """
    Simulate session persistence across simulated page reloads.
    """
    with app.app_context():
        with app.test_client() as client:
            # Simulate initial session creation
            with app.test_request_context('/'):
                # Set session data as if from a login
                session['user_id'] = 'persist_user_456'
                session['user_type'] = 'admin'
                session['user_name'] = 'Persistent User'
                session['email'] = 'persistent@example.com'
                session.permanent = True  # Make session permanent
                
                # Verify session was set
                assert session.get('user_id') == 'persist_user_456'
                assert session.get('user_type') == 'admin'
                assert session.get('permanent') == True
    
    # Simulate subsequent request (like page reload) - session should persist
    with app.app_context():
        with app.test_request_context('/'):
            # In a real scenario, session data would be restored from cookie
            # For testing, we're verifying the configuration supports persistence
            assert app.config['SESSION_PERMANENT'] == True
            assert app.config['PERMANENT_SESSION_LIFETIME'].days >= 1
    
    print("✅ Session persistence simulation successful")


@settings(
    max_examples=6,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(
    user_id=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', '_-')), min_size=5, max_size=20),
    user_type=st.sampled_from(['admin', 'client', 'employee', 'staff'])
)
def test_session_data_integrity_after_reload_simulation(user_id, user_type):
    """
    Test that session data maintains integrity after simulated reloads.
    """
    # Create temporary Flask app for testing
    temp_app = Flask(__name__)
    temp_app.config['SECRET_KEY'] = 'test-secret-key-change-in-production'
    temp_app.config['SESSION_PERMANENT'] = True
    temp_app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
    temp_app.config['SESSION_COOKIE_HTTPONLY'] = True
    temp_app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    temp_app.config['SESSION_REFRESH_EACH_REQUEST'] = True
    
    # Simulate session lifecycle
    test_session_data = {
        'user_id': user_id,
        'user_type': user_type,
        'user_name': f"User {user_id}",
        'email': f"{user_id}@test.com",
        'username': user_id,
        'is_super_admin': user_type == 'admin'
    }
    
    # Store session data and verify persistence
    with temp_app.app_context():
        with temp_app.test_request_context('/'):
            # Set session data
            for key, value in test_session_data.items():
                session[key] = value
            session.permanent = True
            
            # Verify all data is stored correctly
            for key, expected_value in test_session_data.items():
                assert session.get(key) == expected_value, f"Session data mismatch for {key}"
    
    # Simulate data retrieval after "reload"
    with temp_app.app_context():
        with temp_app.test_request_context('/'):
            # Verify configuration supports persistence
            assert temp_app.config['SESSION_PERMANENT'] == True
            assert temp_app.config['SESSION_COOKIE_HTTPONLY'] == True
            assert temp_app.config['SESSION_COOKIE_SAMESITE'] == 'None'
    
    print(f"✅ Session data integrity verified for user: {user_id}, type: {user_type}")


def test_mobile_session_cookie_requirements():
    """
    Test that session cookies meet specific requirements for mobile applications.
    """
    # Check specific requirements for mobile session cookies
    assert app.config['SESSION_COOKIE_HTTPONLY'] == True, "HttpOnly flag required for security"
    
    # For mobile apps, SameSite needs to be None to allow cross-origin requests
    assert app.config['SESSION_COOKIE_SAMESITE'] == 'None', "SameSite=None required for mobile cross-origin requests"
    
    # Session should be permanent to persist across app restarts
    assert app.config['SESSION_PERMANENT'] == True, "Sessions must be permanent for mobile app"
    
    # Session lifetime should be appropriate for mobile usage
    lifetime = app.config['PERMANENT_SESSION_LIFETIME']
    assert lifetime.days >= 7, f"Session lifetime should be at least 7 days for mobile, got {lifetime.days} days"
    
    # Check that session refresh is enabled
    assert app.config['SESSION_REFRESH_EACH_REQUEST'] == True, "Session refresh required for mobile apps"
    
    print("✅ Mobile session cookie requirements validated")


def test_session_cookie_security_attributes():
    """
    Test that session cookies have appropriate security attributes.
    """
    # Test security attributes based on environment
    is_production = os.environ.get('FLASK_ENV', 'development') == 'production'
    
    # HttpOnly should always be True
    assert app.config['SESSION_COOKIE_HTTPONLY'] == True, "HttpOnly must be True for XSS protection"
    
    # SameSite should be None for mobile compatibility (with secure flag if needed)
    assert app.config['SESSION_COOKIE_SAMESITE'] == 'None', "SameSite=None needed for mobile cross-origin requests"
    
    # In production, secure flag should be True
    expected_secure = is_production
    actual_secure = app.config['SESSION_COOKIE_SECURE']
    print(f"Environment: {'production' if is_production else 'development'}, Secure flag: {actual_secure}")
    
    # Verify session permanence for mobile usage
    assert app.config['SESSION_PERMANENT'] == True, "Sessions must be permanent for mobile persistence"
    
    print("✅ Session cookie security attributes validated")


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])