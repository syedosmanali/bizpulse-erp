"""
Property-Based Tests for GST Number Validation
Feature: comprehensive-erp-modules
"""

import pytest
from hypothesis import given, strategies as st, assume
from modules.erp_modules.service import ERPService


# ============================================================================
# Property 3: GST Number Format Validation
# **Validates: Requirements 2.3**
# ============================================================================

@given(
    state_code=st.integers(min_value=0, max_value=99),
    pan=st.text(min_size=10, max_size=10, alphabet=st.characters(whitelist_categories=('Lu', 'Nd'))),
    entity_digit=st.integers(min_value=0, max_value=9),
    check_digit=st.integers(min_value=0, max_value=9)
)
def test_valid_gst_format_accepted(state_code, pan, entity_digit, check_digit):
    """
    Property 3: GST Number Format Validation
    
    For any GST registration number input, the system should accept only strings 
    matching the format: 2 digits + 10 alphanumeric (PAN) + 1 digit + 1 letter Z + 1 check digit 
    (total 15 characters).
    
    **Validates: Requirements 2.3**
    """
    # Construct a valid GST number
    gst_number = f"{state_code:02d}{pan}{entity_digit}Z{check_digit}"
    
    # Valid GST should be accepted
    assert ERPService.validate_gst_number(gst_number) == True, \
        f"Valid GST number {gst_number} should be accepted"


@given(
    invalid_gst=st.one_of(
        # Too short (but not empty)
        st.text(min_size=1, max_size=14, alphabet=st.characters(whitelist_categories=('Lu', 'Nd'))),
        # Too long
        st.text(min_size=16, max_size=30, alphabet=st.characters(whitelist_categories=('Lu', 'Nd'))),
        # Missing Z at position 13
        st.text(min_size=15, max_size=15, alphabet=st.characters(blacklist_characters='Zz')),
    )
)
def test_invalid_gst_format_rejected(invalid_gst):
    """
    Property 3: GST Number Format Validation (Invalid Cases)
    
    For any GST registration number that doesn't match the required format,
    the system should reject it.
    
    **Validates: Requirements 2.3**
    """
    # Assume the invalid GST is not accidentally valid and not empty
    assume(len(invalid_gst) > 0)
    assume(len(invalid_gst) != 15 or invalid_gst[13].upper() != 'Z')
    
    # Invalid GST should be rejected
    assert ERPService.validate_gst_number(invalid_gst) == False, \
        f"Invalid GST number {invalid_gst} should be rejected"


@given(
    state_code=st.text(min_size=2, max_size=2, alphabet=st.characters(whitelist_categories=('Lu',))),
    pan=st.text(min_size=10, max_size=10, alphabet=st.characters(whitelist_categories=('Lu', 'Nd'))),
    entity_digit=st.integers(min_value=0, max_value=9),
    check_digit=st.integers(min_value=0, max_value=9)
)
def test_gst_with_non_digit_state_code_rejected(state_code, pan, entity_digit, check_digit):
    """
    Property 3: GST Number Format Validation (State Code Must Be Digits)
    
    For any GST registration number where the first 2 characters are not digits,
    the system should reject it.
    
    **Validates: Requirements 2.3**
    """
    # Construct GST with non-digit state code
    gst_number = f"{state_code}{pan}{entity_digit}Z{check_digit}"
    
    # Should be rejected because state code must be digits
    assert ERPService.validate_gst_number(gst_number) == False, \
        f"GST number {gst_number} with non-digit state code should be rejected"


@given(
    state_code=st.integers(min_value=0, max_value=99),
    pan=st.text(min_size=10, max_size=10, alphabet=st.characters(whitelist_categories=('Lu', 'Nd'))),
    entity_digit=st.integers(min_value=0, max_value=9),
    wrong_letter=st.text(min_size=1, max_size=1, alphabet=st.characters(blacklist_characters='Zz')),
    check_digit=st.integers(min_value=0, max_value=9)
)
def test_gst_without_z_at_position_13_rejected(state_code, pan, entity_digit, wrong_letter, check_digit):
    """
    Property 3: GST Number Format Validation (Must Have Z at Position 13)
    
    For any GST registration number where position 13 (0-indexed) is not 'Z',
    the system should reject it.
    
    **Validates: Requirements 2.3**
    """
    # Construct GST with wrong letter instead of Z
    gst_number = f"{state_code:02d}{pan}{entity_digit}{wrong_letter}{check_digit}"
    
    # Should be rejected because position 13 must be Z
    assert ERPService.validate_gst_number(gst_number) == False, \
        f"GST number {gst_number} without Z at position 13 should be rejected"


def test_empty_gst_accepted():
    """
    Property 3: GST Number Format Validation (Empty GST)
    
    Empty or None GST numbers should be accepted as GST is optional.
    
    **Validates: Requirements 2.3**
    """
    assert ERPService.validate_gst_number('') == True, "Empty GST should be accepted"
    assert ERPService.validate_gst_number(None) == True, "None GST should be accepted"


def test_specific_valid_gst_examples():
    """
    Property 3: GST Number Format Validation (Specific Valid Examples)
    
    Test specific known valid GST numbers.
    
    **Validates: Requirements 2.3**
    """
    valid_gst_numbers = [
        '27AABCU9603R1Z5',  # Maharashtra
        '29AABCU9603R1Z5',  # Karnataka
        '07AABCU9603R1Z1',  # Delhi
        '33AABCU9603R1Z9',  # Tamil Nadu
    ]
    
    for gst in valid_gst_numbers:
        assert ERPService.validate_gst_number(gst) == True, \
            f"Valid GST number {gst} should be accepted"


def test_specific_invalid_gst_examples():
    """
    Property 3: GST Number Format Validation (Specific Invalid Examples)
    
    Test specific known invalid GST numbers.
    
    **Validates: Requirements 2.3**
    """
    invalid_gst_numbers = [
        '27AABCU9603',           # Too short
        '27-AABCU-9603-R1Z5',    # Contains hyphens
        '27AABCU9603R1X5',       # X instead of Z
        'AABCU9603R1Z5',         # Missing state code
        '2AABCU9603R1Z5',        # Only 1 digit state code
        '27AABCU9603R1Z51',      # Too long
        'AA27AABCU9603R1Z5',     # State code not digits
        '27AABCU9603R1ZM',       # Last char not digit
    ]
    
    for gst in invalid_gst_numbers:
        assert ERPService.validate_gst_number(gst) == False, \
            f"Invalid GST number {gst} should be rejected"


@given(
    state_code=st.integers(min_value=0, max_value=99),
    pan=st.text(min_size=10, max_size=10, alphabet=st.characters(whitelist_categories=('Lu', 'Nd'))),
    entity_digit=st.integers(min_value=0, max_value=9),
    check_digit=st.integers(min_value=0, max_value=9)
)
def test_gst_case_insensitive_for_z(state_code, pan, entity_digit, check_digit):
    """
    Property 3: GST Number Format Validation (Case Insensitive Z)
    
    The validation should accept both uppercase and lowercase 'z' at position 13.
    
    **Validates: Requirements 2.3**
    """
    # Test with lowercase z
    gst_lowercase = f"{state_code:02d}{pan}{entity_digit}z{check_digit}"
    
    # Should be accepted (validation converts to uppercase)
    result = ERPService.validate_gst_number(gst_lowercase)
    assert result == True, \
        f"GST number {gst_lowercase} with lowercase z should be accepted"
