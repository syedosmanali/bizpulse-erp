"""
Property-Based Tests for IFSC Code Validation
Feature: comprehensive-erp-modules
"""

import pytest
from hypothesis import given, strategies as st, assume
from modules.erp_modules.service import ERPService


# ============================================================================
# Property 4: IFSC Code Format Validation
# **Validates: Requirements 3.7**
# ============================================================================

@given(
    bank_code=st.text(min_size=4, max_size=4, alphabet=st.characters(whitelist_categories=('Lu',))),
    branch_code=st.text(min_size=7, max_size=7, alphabet=st.characters(whitelist_categories=('Lu', 'Nd')))
)
def test_valid_ifsc_format_accepted(bank_code, branch_code):
    """
    Property 4: IFSC Code Format Validation
    
    For any IFSC code input, the system should accept only strings matching 
    the format: 4 letters followed by 7 alphanumeric characters (total 11 characters).
    
    **Validates: Requirements 3.7**
    """
    # Construct a valid IFSC code
    ifsc_code = f"{bank_code}{branch_code}"
    
    # Valid IFSC should be accepted
    assert ERPService.validate_ifsc_code(ifsc_code) == True, \
        f"Valid IFSC code {ifsc_code} should be accepted"


@given(
    invalid_ifsc=st.one_of(
        # Too short
        st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('Lu', 'Nd'))),
        # Too long
        st.text(min_size=12, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Nd'))),
        # Empty string
        st.just('')
    )
)
def test_invalid_ifsc_length_rejected(invalid_ifsc):
    """
    Property 4: IFSC Code Format Validation (Invalid Length)
    
    For any IFSC code that doesn't have exactly 11 characters,
    the system should reject it.
    
    **Validates: Requirements 3.7**
    """
    # Assume the length is not 11
    assume(len(invalid_ifsc) != 11)
    
    # Invalid length IFSC should be rejected
    assert ERPService.validate_ifsc_code(invalid_ifsc) == False, \
        f"IFSC code {invalid_ifsc} with length {len(invalid_ifsc)} should be rejected"


@given(
    bank_code=st.text(min_size=4, max_size=4, alphabet=st.characters(whitelist_categories=('Nd',))),
    branch_code=st.text(min_size=7, max_size=7, alphabet=st.characters(whitelist_categories=('Lu', 'Nd')))
)
def test_ifsc_with_non_alpha_bank_code_rejected(bank_code, branch_code):
    """
    Property 4: IFSC Code Format Validation (Bank Code Must Be Letters)
    
    For any IFSC code where the first 4 characters are not all letters,
    the system should reject it.
    
    **Validates: Requirements 3.7**
    """
    # Construct IFSC with numeric bank code
    ifsc_code = f"{bank_code}{branch_code}"
    
    # Should be rejected because bank code must be letters
    assert ERPService.validate_ifsc_code(ifsc_code) == False, \
        f"IFSC code {ifsc_code} with non-alphabetic bank code should be rejected"


@given(
    bank_code=st.text(min_size=4, max_size=4, alphabet=st.characters(whitelist_categories=('Lu',))),
    branch_code=st.text(min_size=7, max_size=7, alphabet=st.characters(blacklist_categories=('Lu', 'Nd')))
)
def test_ifsc_with_special_chars_in_branch_rejected(bank_code, branch_code):
    """
    Property 4: IFSC Code Format Validation (Branch Code Must Be Alphanumeric)
    
    For any IFSC code where the last 7 characters contain non-alphanumeric characters,
    the system should reject it.
    
    **Validates: Requirements 3.7**
    """
    # Assume branch code has at least one non-alphanumeric character
    assume(not branch_code.isalnum())
    
    # Construct IFSC with special characters in branch code
    ifsc_code = f"{bank_code}{branch_code}"
    
    # Should be rejected because branch code must be alphanumeric
    assert ERPService.validate_ifsc_code(ifsc_code) == False, \
        f"IFSC code {ifsc_code} with special characters in branch code should be rejected"


def test_none_ifsc_rejected():
    """
    Property 4: IFSC Code Format Validation (None IFSC)
    
    None IFSC codes should be rejected as IFSC is required for bank accounts.
    
    **Validates: Requirements 3.7**
    """
    assert ERPService.validate_ifsc_code(None) == False, "None IFSC should be rejected"


def test_empty_ifsc_rejected():
    """
    Property 4: IFSC Code Format Validation (Empty IFSC)
    
    Empty IFSC codes should be rejected as IFSC is required for bank accounts.
    
    **Validates: Requirements 3.7**
    """
    assert ERPService.validate_ifsc_code('') == False, "Empty IFSC should be rejected"


def test_specific_valid_ifsc_examples():
    """
    Property 4: IFSC Code Format Validation (Specific Valid Examples)
    
    Test specific known valid IFSC codes.
    
    **Validates: Requirements 3.7**
    """
    valid_ifsc_codes = [
        'SBIN0001234',  # State Bank of India
        'HDFC0000123',  # HDFC Bank
        'ICIC0001234',  # ICICI Bank
        'UTIB0000123',  # Axis Bank
        'KKBK0001234',  # Kotak Mahindra Bank
        'PUNB0123456',  # Punjab National Bank
        'BARB0MUMBAI',  # Bank of Baroda (alphanumeric branch)
    ]
    
    for ifsc in valid_ifsc_codes:
        assert ERPService.validate_ifsc_code(ifsc) == True, \
            f"Valid IFSC code {ifsc} should be accepted"


def test_specific_invalid_ifsc_examples():
    """
    Property 4: IFSC Code Format Validation (Specific Invalid Examples)
    
    Test specific known invalid IFSC codes.
    
    **Validates: Requirements 3.7**
    """
    invalid_ifsc_codes = [
        'SBIN001',           # Too short
        'SBIN-0001234',      # Contains hyphen
        'SB1N0001234',       # Digit in bank code
        'SBIN00012345',      # Too long
        '1234SBIN001',       # Bank code not letters
        'SBIN 001234',       # Contains space
        'SBIN@001234',       # Special character in branch code
    ]
    
    for ifsc in invalid_ifsc_codes:
        assert ERPService.validate_ifsc_code(ifsc) == False, \
            f"Invalid IFSC code {ifsc} should be rejected"


@given(
    bank_code=st.text(min_size=4, max_size=4, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))),
    branch_code=st.text(min_size=7, max_size=7, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))
)
def test_ifsc_accepts_both_cases(bank_code, branch_code):
    """
    Property 4: IFSC Code Format Validation (Case Acceptance)
    
    Test that IFSC validation accepts both uppercase and lowercase letters.
    The requirement specifies "4 letters" without case restriction.
    
    **Validates: Requirements 3.7**
    """
    # Valid IFSC with any case
    ifsc_code = f"{bank_code}{branch_code}"
    assert ERPService.validate_ifsc_code(ifsc_code) == True, \
        f"Valid IFSC code {ifsc_code} should be accepted regardless of case"


@given(
    bank_code=st.text(min_size=3, max_size=3, alphabet=st.characters(whitelist_categories=('Lu',))),
    branch_code=st.text(min_size=7, max_size=7, alphabet=st.characters(whitelist_categories=('Lu', 'Nd')))
)
def test_ifsc_with_short_bank_code_rejected(bank_code, branch_code):
    """
    Property 4: IFSC Code Format Validation (Bank Code Must Be 4 Letters)
    
    For any IFSC code where the bank code is less than 4 letters,
    the system should reject it.
    
    **Validates: Requirements 3.7**
    """
    # Construct IFSC with 3-letter bank code
    ifsc_code = f"{bank_code}{branch_code}"
    
    # Should be rejected because total length is 10, not 11
    assert ERPService.validate_ifsc_code(ifsc_code) == False, \
        f"IFSC code {ifsc_code} with 3-letter bank code should be rejected"


@given(
    bank_code=st.text(min_size=4, max_size=4, alphabet=st.characters(whitelist_categories=('Lu',))),
    branch_code=st.text(min_size=6, max_size=6, alphabet=st.characters(whitelist_categories=('Lu', 'Nd')))
)
def test_ifsc_with_short_branch_code_rejected(bank_code, branch_code):
    """
    Property 4: IFSC Code Format Validation (Branch Code Must Be 7 Characters)
    
    For any IFSC code where the branch code is less than 7 characters,
    the system should reject it.
    
    **Validates: Requirements 3.7**
    """
    # Construct IFSC with 6-character branch code
    ifsc_code = f"{bank_code}{branch_code}"
    
    # Should be rejected because total length is 10, not 11
    assert ERPService.validate_ifsc_code(ifsc_code) == False, \
        f"IFSC code {ifsc_code} with 6-character branch code should be rejected"
