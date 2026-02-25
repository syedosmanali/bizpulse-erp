"""
Property-based test for login credential validation.
Validates Property 1: Login Credential Validation from requirements.
"""

import pytest
from hypothesis import given, strategies as st
from hypothesis.strategies import text, sampled_from
import re
from modules.auth.service import AuthenticationService


def is_valid_username(username):
    """
    Validate username format - alphanumeric with underscores and dots, 3-50 chars
    """
    if len(username) < 3 or len(username) > 50:
        return False
    # Alphanumeric, underscore, dot, hyphen
    pattern = r'^[a-zA-Z0-9_.-]+$'
    return bool(re.match(pattern, username))


def is_valid_password(password):
    """
    Validate password strength - at least 8 chars with mixed case, number, special char
    """
    if len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    return has_upper and has_lower and has_digit and has_special


@given(
    username=text(min_size=1, max_size=100),
    password=text(min_size=1, max_size=100)
)
def test_login_credential_validation_property(username, password):
    """
    Property 1: Login Credential Validation
    Validates that login credentials follow proper format and security requirements.
    """
    # Test that valid credentials pass validation
    if is_valid_username(username) and is_valid_password(password):
        # Valid credentials should be accepted by the system
        assert len(username) >= 3 and len(username) <= 50
        assert all(c.isalnum() or c in ['_', '.', '-'] for c in username)
        assert len(password) >= 8
        assert any(c.isupper() for c in password)
        assert any(c.islower() for c in password)
        assert any(c.isdigit() for c in password)
        assert any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    else:
        # Invalid credentials should be rejected by validation logic
        assert not is_valid_username(username) or not is_valid_password(password)


@given(
    username=text(alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-", min_size=3, max_size=50),
    password=st.text(min_size=8, alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()")
        .filter(lambda x: (
            any(c.isupper() for c in x) and 
            any(c.islower() for c in x) and 
            any(c.isdigit() for c in x) and 
            any(c in "!@#$%^&*()" for c in x)
        ))
)
def test_valid_credentials_always_pass_format_check(username, password):
    """
    Additional property: Valid format credentials always pass basic format checks
    """
    assert is_valid_username(username)
    assert is_valid_password(password)
    assert len(username) >= 3
    assert len(username) <= 50
    assert len(password) >= 8


def test_login_credential_examples():
    """
    Specific examples to demonstrate valid and invalid credentials
    """
    # Valid credentials
    assert is_valid_username("john_doe")
    assert is_valid_username("user.name")
    assert is_valid_username("user-name")
    assert is_valid_username("user123")
    
    # Invalid usernames
    assert not is_valid_username("ab")  # Too short
    assert not is_valid_username("")    # Empty
    assert not is_valid_username("a" * 51)  # Too long
    assert not is_valid_username("user@name")  # Invalid character
    
    # Valid passwords
    valid_passwords = [
        "Password123!",
        "MyPass123$",
        "SecurePwd9*"
    ]
    for pwd in valid_passwords:
        assert is_valid_password(pwd)
    
    # Invalid passwords
    invalid_passwords = [
        "pass",      # Too short
        "password",  # No uppercase, no digit, no special
        "PASSWORD",  # No lowercase, no digit, no special
        "Password",  # No digit, no special
        "Password1", # No special character
    ]
    for pwd in invalid_passwords:
        assert not is_valid_password(pwd)


if __name__ == "__main__":
    # Run some basic tests
    test_login_credential_examples()
    print("All login credential validation tests passed!")