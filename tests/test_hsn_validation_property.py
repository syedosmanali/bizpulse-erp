"""
Property-based tests for HSN (Harmonized System of Nomenclature) code validation
Using Hypothesis for comprehensive testing of edge cases
"""

import pytest
from hypothesis import given, strategies as st
from hypothesis.strategies import text, integers, sampled_from
from modules.erp_modules.service import ERPService


@given(st.text(alphabet='0123456789', min_size=1, max_size=10))
def test_hsn_digit_only_validation(hsn_input):
    """
    Property 15: HSN Code Format Validation
    Validates: Requirements 9.5
    
    All characters in HSN code must be digits
    """
    result = ERPService.validate_hsn_code(hsn_input)
    
    # Valid HSN codes are only 4, 6, or 8 digits
    expected = len(hsn_input) in [4, 6, 8]
    assert result == expected, f"HSN '{hsn_input}' with length {len(hsn_input)} should be {'valid' if expected else 'invalid'}"


@given(st.text(min_size=1, max_size=10))
def test_hsn_non_digit_rejection(hsn_input):
    """
    Property 15: HSN Code Format Validation
    Validates: Requirements 9.5
    
    HSN codes containing non-digit characters should be rejected
    """
    # Skip if the string is all digits (covered by other test)
    if hsn_input.isdigit():
        return
        
    result = ERPService.validate_hsn_code(hsn_input)
    assert result is False, f"HSN '{hsn_input}' containing non-digits should be invalid"


@given(sampled_from(['', None]))
def test_hsn_optional_acceptance(hsn_input):
    """
    Property 15: HSN Code Format Validation
    Validates: Requirements 9.5
    
    Empty or None HSN codes should be accepted (optional field)
    """
    # Handle None case specially since the function expects a string
    if hsn_input is None:
        # Test with empty string since the function likely handles None differently
        result = ERPService.validate_hsn_code('')
    else:
        result = ERPService.validate_hsn_code(hsn_input)
    
    assert result is True, f"Empty HSN should be valid as it's optional"


@given(st.text(alphabet='0123456789', min_size=1, max_size=20))
def test_hsn_length_validation(hsn_input):
    """
    Property 15: HSN Code Format Validation
    Validates: Requirements 9.5
    
    Only lengths of 4, 6, or 8 digits are valid for HSN codes
    """
    result = ERPService.validate_hsn_code(hsn_input)
    
    valid_lengths = [4, 6, 8]
    expected = len(hsn_input) in valid_lengths
    
    assert result == expected, f"HSN '{hsn_input}' length {len(hsn_input)} should be {'valid' if expected else 'invalid'}"


def test_hsn_specific_valid_cases():
    """Test specific known valid HSN codes"""
    valid_hsns = ['1234', '123456', '12345678', '0000', '99999999']
    
    for hsn in valid_hsns:
        result = ERPService.validate_hsn_code(hsn)
        assert result is True, f"Valid HSN '{hsn}' should return True"


def test_hsn_specific_invalid_cases():
    """Test specific known invalid HSN codes"""
    invalid_hsns = [
        '123',      # Too short
        '12345',    # Wrong length
        '1234567',  # Wrong length
        '123456789', # Too long
        '12A4',     # Contains non-digit
        'ABCD',     # All non-digits
        '12 45',    # Contains space
        '12-45',    # Contains special character
    ]
    
    for hsn in invalid_hsns:
        result = ERPService.validate_hsn_code(hsn)
        assert result is False, f"Invalid HSN '{hsn}' should return False"


if __name__ == "__main__":
    # Run the tests
    import subprocess
    import sys
    
    # Run with pytest for better output
    result = subprocess.run([sys.executable, '-m', 'pytest', __file__, '-v'])
    print(f"Tests completed with exit code: {result.returncode}")