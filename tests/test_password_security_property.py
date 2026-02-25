"""
Property-based test for password security.
Validates Property 2: Password Storage Security from requirements.
"""

import pytest
from hypothesis import given, strategies as st
from hypothesis.strategies import text, sampled_from
import bcrypt
import re


def is_secure_password(password):
    """
    Check if password meets security requirements
    """
    if len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    return has_upper and has_lower and has_digit and has_special


def is_password_hashed_correctly(plain_password, hashed_password):
    """
    Check if password is correctly hashed using bcrypt
    """
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)
    except:
        return False


def calculate_password_entropy(password):
    """
    Calculate password entropy as a measure of randomness
    """
    import math
    charset_size = 0
    
    if any(c.islower() for c in password):
        charset_size += 26  # lowercase letters
    if any(c.isupper() for c in password):
        charset_size += 26  # uppercase letters
    if any(c.isdigit() for c in password):
        charset_size += 10  # digits
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        charset_size += 32  # special characters
    
    if charset_size == 0:
        return 0
    
    # Entropy = log2(charset_size^length)
    entropy = len(password) * math.log2(charset_size)
    return entropy


@given(
    password=st.text(min_size=8, max_size=128, alphabet=st.characters(codec='utf-8'))
        .filter(lambda x: (
            len(x) >= 8 and
            any(c.isupper() for c in x) and 
            any(c.islower() for c in x) and 
            any(c.isdigit() for c in x) and 
            any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in x)
        ))
)
def test_password_storage_security_property(password):
    """
    Property 2: Password Storage Security
    Validates that passwords are securely stored using proper hashing.
    """
    # Hash the password using bcrypt
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # Verify that the hash is different from the original password
    assert hashed != password.encode('utf-8')
    
    # Verify that the hash can be used to authenticate the password
    assert bcrypt.checkpw(password.encode('utf-8'), hashed)
    
    # Verify that a different password fails to authenticate
    wrong_password = password + "wrong"
    assert not bcrypt.checkpw(wrong_password.encode('utf-8'), hashed)
    
    # Check that the hash contains bcrypt identifier
    assert b'$2b$' in hashed or b'$2a$' in hashed or b'$2y$' in hashed


@given(
    password=st.text(min_size=1, max_size=128, alphabet=st.characters(codec='utf-8'))
)
def test_password_hash_verification_consistency(password):
    """
    Property: Hash verification is consistent for the same password
    """
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # Multiple verifications should yield the same result
    assert bcrypt.checkpw(password.encode('utf-8'), hashed)
    assert bcrypt.checkpw(password.encode('utf-8'), hashed)
    assert bcrypt.checkpw(password.encode('utf-8'), hashed)


def test_secure_password_examples():
    """
    Test examples of secure and insecure passwords
    """
    # Secure passwords
    secure_passwords = [
        "SecurePass123!",
        "MyStrongPwd9*",
        "ComplexPwd123$"
    ]
    
    for pwd in secure_passwords:
        assert is_secure_password(pwd), f"Password {pwd} should be secure"
        
        # Test that it hashes correctly
        hashed = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())
        assert is_password_hashed_correctly(pwd, hashed)
        
        # Test that entropy is reasonably high for secure passwords
        entropy = calculate_password_entropy(pwd)
        assert entropy > 30, f"Entropy {entropy} for password {pwd} is too low"


def test_insecure_password_detection():
    """
    Test that insecure passwords are properly detected
    """
    insecure_passwords = [
        "pass",          # Too short
        "password",      # No complexity
        "12345678",      # Only digits
        "abcdefgh",      # Only lowercase
        "ABCDEFGH",      # Only uppercase
        "Pass123",       # Missing special character
        "Pass!"          # Missing digit
    ]
    
    for pwd in insecure_passwords:
        assert not is_secure_password(pwd), f"Password {pwd} should be detected as insecure"


def test_password_hash_uniqueness():
    """
    Test that hashing the same password multiple times produces different hashes
    """
    password = "SecurePassword123!"
    
    hash1 = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    hash2 = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # Different salt should produce different hashes
    assert hash1 != hash2
    
    # But both should verify against the same password
    assert bcrypt.checkpw(password.encode('utf-8'), hash1)
    assert bcrypt.checkpw(password.encode('utf-8'), hash2)


if __name__ == "__main__":
    # Run tests
    test_secure_password_examples()
    test_insecure_password_detection()
    test_password_hash_uniqueness()
    print("All password security tests passed!")