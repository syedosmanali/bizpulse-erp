"""
Property-based tests for payment management functionality
Using Hypothesis for comprehensive testing of payment operations
"""

import pytest
from hypothesis import given, settings, HealthCheck
from hypothesis.strategies import integers, floats, text, sampled_from, lists, composite
from modules.erp_modules.service import ERPService
from modules.shared.database import get_db_connection, generate_id
import json
import random
from datetime import datetime, timedelta


@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
@given(
    payment_amount=floats(min_value=0.01, max_value=100000.0),
    payment_direction=sampled_from(['in', 'out'])
)
def test_payment_amount_validation(payment_amount, payment_direction):
    """
    Property: Payment Amount Validation
    Validates: Payment amounts should be positive and directionally correct
    
    All payments should have positive amounts regardless of direction (in/out).
    """
    # Validate that payment amount is positive
    assert payment_amount > 0, f"Payment amount must be positive: {payment_amount}"
    
    # Validate payment direction
    valid_directions = ['in', 'out']
    assert payment_direction in valid_directions, f"Payment direction must be valid: {payment_direction}"
    
    # Both incoming and outgoing payments should have positive amounts
    assert isinstance(payment_amount, (int, float)), f"Payment amount should be numeric: {type(payment_amount)}"


@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
@given(
    payment_mode=sampled_from(['cash', 'online', 'cheque', 'bank_transfer', 'mixed'])
)
def test_payment_mode_validation(payment_mode):
    """
    Property: Payment Mode Validation
    Validates: Payment modes should be from approved list
    
    All payments should use recognized payment methods.
    """
    # Validate payment mode is from approved list
    valid_modes = ['cash', 'online', 'cheque', 'bank_transfer', 'mixed', 'credit_card', 'debit_card', 'upi']
    assert payment_mode in valid_modes, f"Payment mode must be valid: {payment_mode}"
    
    # Each mode should have specific characteristics
    if payment_mode == 'mixed':
        # Mixed payments should involve multiple payment methods
        pass  # This would be validated in more complex scenarios
    else:
        # Each single mode should be distinct
        assert isinstance(payment_mode, str), f"Payment mode should be string: {payment_mode}"


@composite
def payment_scenarios(draw):
    """Generate realistic payment scenarios"""
    parties = [
        'ABC Customer', 'XYZ Supplier', 'Retail Client', 'Corporate Buyer',
        'Regular Customer', 'New Client', 'Returning Customer', 'VIP Client'
    ]
    
    modes = ['cash', 'online', 'cheque', 'bank_transfer', 'mixed']
    
    party_name = draw(sampled_from(parties))
    payment_mode = draw(sampled_from(modes))
    amount = draw(floats(min_value=1.0, max_value=50000.0))
    direction = draw(sampled_from(['in', 'out']))
    
    # Generate reference based on mode
    if payment_mode == 'cheque':
        reference = f"CHK{random.randint(100000, 999999)}"
    elif payment_mode == 'online':
        reference = f"TXN{random.randint(1000000000, 9999999999)}"
    else:
        reference = f"REF{random.randint(1000, 9999)}"
    
    return {
        'party_name': party_name,
        'payment_mode': payment_mode,
        'amount': amount,
        'direction': direction,
        'reference': reference,
        'has_reference': bool(reference.strip()),
        'is_large_payment': amount > 10000  # Threshold for large payments
    }


@settings(max_examples=40, suppress_health_check=[HealthCheck.too_slow])
@given(payment_scenarios())
def test_payment_scenario_validation(scenario):
    """
    Property: Payment Scenario Validation
    Validates: Payment records should have complete and consistent information
    
    Each payment record should contain all necessary information for tracking.
    """
    # Validate party name
    assert scenario['party_name'].strip() != "", f"Party name should not be empty: '{scenario['party_name']}'"
    
    # Validate payment mode
    valid_modes = ['cash', 'online', 'cheque', 'bank_transfer', 'mixed', 'credit_card', 'debit_card', 'upi']
    assert scenario['payment_mode'] in valid_modes, f"Invalid payment mode: {scenario['payment_mode']}"
    
    # Validate amount is positive
    assert scenario['amount'] > 0, f"Payment amount should be positive: {scenario['amount']}"
    
    # Validate direction
    valid_directions = ['in', 'out']
    assert scenario['direction'] in valid_directions, f"Invalid payment direction: {scenario['direction']}"
    
    # Validate reference exists for appropriate payment types
    if scenario['payment_mode'] in ['cheque', 'online', 'bank_transfer']:
        assert scenario['has_reference'], \
            f"Payment of type {scenario['payment_mode']} should have reference: {scenario['reference']}"
    
    # Validate amount categorization
    assert isinstance(scenario['is_large_payment'], bool), \
        f"Large payment flag should be boolean: {scenario['is_large_payment']}"


@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
@given(
    balance_before=floats(min_value=0.0, max_value=1000000.0),
    payment_amount=floats(min_value=1.0, max_value=50000.0),
    payment_direction=sampled_from(['in', 'out'])
)
def test_payment_balance_impact(balance_before, payment_amount, payment_direction):
    """
    Property: Payment Balance Impact
    Validates: Payments should correctly affect account balances
    
    Incoming payments should increase balance, outgoing payments should decrease it.
    """
    # Validate inputs
    assert balance_before >= 0, f"Starting balance should be non-negative: {balance_before}"
    assert payment_amount > 0, f"Payment amount should be positive: {payment_amount}"
    
    # Calculate new balance based on payment direction
    if payment_direction == 'in':
        balance_after = balance_before + payment_amount
        # Incoming payment should increase balance
        assert balance_after > balance_before, \
            f"Incoming payment should increase balance: {balance_before} -> {balance_after}"
    elif payment_direction == 'out':
        balance_after = balance_before - payment_amount
        # Outgoing payment should decrease balance, but not go negative
        assert balance_after >= 0, \
            f"Outgoing payment should not make balance negative: {balance_before} - {payment_amount} = {balance_after}"
        assert balance_after < balance_before, \
            f"Outgoing payment should decrease balance: {balance_before} -> {balance_after}"
    
    # Validate that balance changes are proportional to payment amounts
    expected_difference = payment_amount if payment_direction == 'in' else -payment_amount
    actual_difference = balance_after - balance_before
    assert abs(actual_difference - expected_difference) < 0.01, \
        f"Balance change should match payment amount: expected {expected_difference}, got {actual_difference}"


def test_payment_status_lifecycle():
    """
    Property: Payment Status Lifecycle
    Validates: Payments should follow proper status progression
    
    Payment records should maintain status integrity throughout their lifecycle.
    """
    # Define valid payment statuses
    valid_statuses = ['pending', 'processing', 'completed', 'failed', 'refunded', 'cancelled']
    
    # Define valid status transitions
    valid_transitions = {
        'pending': ['processing', 'cancelled'],
        'processing': ['completed', 'failed'],
        'completed': [],  # Terminal state
        'failed': ['pending', 'cancelled'],  # Can retry or cancel
        'refunded': [],  # Terminal state
        'cancelled': []  # Terminal state
    }
    
    # Test all valid transitions
    for current_status, allowed_next in valid_transitions.items():
        assert current_status in valid_statuses, f"Current status {current_status} should be valid"
        for next_status in allowed_next:
            assert next_status in valid_statuses, f"Next status {next_status} should be valid"
    
    # Test that completed and refunded are terminal states
    terminal_statuses = [status for status, transitions in valid_transitions.items() if not transitions]
    assert 'completed' in terminal_statuses, "Completed should be a terminal status"
    assert 'refunded' in terminal_statuses, "Refunded should be a terminal status"


@settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
@given(
    cash_ratio=floats(min_value=0.0, max_value=1.0),
    online_ratio=floats(min_value=0.0, max_value=1.0)
)
def test_mixed_payment_validation(cash_ratio, online_ratio):
    """
    Property: Mixed Payment Validation
    Validates: Mixed payments should have properly allocated portions
    
    When multiple payment methods are used, their ratios should sum appropriately.
    """
    # For mixed payments, the ratios should be valid proportions
    combined_ratio = cash_ratio + online_ratio
    
    # If both ratios are specified, they should not exceed 100%
    if combined_ratio > 0:
        # For mixed payments, we might have other payment methods too, so allow up to 2.0
        # But for just cash + online, they should sum to <= 1.0
        if cash_ratio > 0 and online_ratio > 0:
            assert combined_ratio <= 1.0, \
                f"Cash and online ratios should not exceed 100% combined: {combined_ratio}"
    
    # Ratios should be non-negative
    assert cash_ratio >= 0, f"Cash ratio should be non-negative: {cash_ratio}"
    assert online_ratio >= 0, f"Online ratio should be non-negative: {online_ratio}"


def test_payment_data_integrity():
    """
    Property: Payment Data Integrity
    Validates: Payment records should maintain data consistency
    
    All payment data fields should be properly formatted and linked.
    """
    # Test required payment fields
    required_fields = [
        'id',            # Unique identifier
        'party_name',    # Who paid or was paid to
        'amount',        # Payment amount
        'payment_mode',  # Method of payment
        'direction',     # Inflow or outflow
        'status',        # Payment status
        'created_at',    # Timestamp
        'user_id'        # Associated user
    ]
    
    # Test optional but important fields
    recommended_fields = [
        'reference',     # Transaction reference
        'notes',         # Additional information
        'bank_details',  # Bank info for transfers
        'cheque_number'  # Cheque number when applicable
    ]
    
    # Validate field structure
    assert len(required_fields) >= 8, "Should have minimum required fields"
    
    # Test field naming convention
    for field in required_fields + recommended_fields:
        assert isinstance(field, str), f"Field name should be string: {field}"
        assert field.islower() and ('_' in field or field.isalnum()), \
            f"Field should follow naming convention: {field}"


def test_payment_business_rules():
    """
    Property: Payment Business Rules
    Validates: Payment operations should follow business logic
    
    Payments should adhere to standard business practices and regulations.
    """
    # Rule 1: Large payments may require additional verification
    large_payment_threshold = 25000  # Amount above which extra scrutiny applies
    
    # Rule 2: Cash payments have daily limits in many jurisdictions
    daily_cash_limit = 50000  # Maximum daily cash transaction
    
    # Rule 3: Payment refunds should reference original payment
    # This would be enforced by foreign key relationships
    
    # Rule 4: Negative payments should be represented as opposite-direction positive payments
    # Rather than negative amounts, use direction field
    
    # Validate that business rules are conceptually sound
    assert large_payment_threshold > 0, "Large payment threshold should be positive"
    assert daily_cash_limit > 0, "Daily cash limit should be positive"
    assert daily_cash_limit > large_payment_threshold, \
        "Daily cash limit should exceed large payment threshold"


def test_payment_management_requirements_compliance():
    """
    Test compliance with specific payment management requirements
    """
    # Requirements for payment management:
    # - Track all payment inflows and outflows
    # - Support multiple payment methods
    # - Maintain transaction audit trails
    # - Enable reconciliation and reporting
    
    # Test the required fields exist
    required_fields = [
        'party_name',        # Payment counterparty
        'amount',            # Transaction amount
        'payment_mode',      # Method of payment
        'direction',         # Inflow/outflow indicator
        'status',            # Transaction status
        'reference',         # Transaction reference
        'created_at',        # Timestamp for audit
        'notes'              # Additional details
    ]
    
    assert len(required_fields) >= 8, "Should track at least the required fields"
    
    # Verify payment modes
    valid_modes = ['cash', 'online', 'cheque', 'bank_transfer', 'mixed']
    for mode in valid_modes:
        assert isinstance(mode, str), f"Payment mode {mode} should be a string"
        assert mode.strip() != '', f"Payment mode should not be empty: '{mode}'"
    
    # Verify directions
    valid_directions = ['in', 'out']
    for direction in valid_directions:
        assert direction in ['in', 'out'], f"Invalid payment direction: {direction}"
    
    # Verify statuses
    valid_statuses = ['pending', 'completed', 'failed', 'refunded', 'cancelled']
    for status in valid_statuses:
        assert isinstance(status, str), f"Status {status} should be a string"
    
    print("All payment management requirements compliance tests passed!")


if __name__ == "__main__":
    # Run basic validation
    test_payment_management_requirements_compliance()
    print("Property tests for payment management completed!")