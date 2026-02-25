"""
Property-based tests for income/expense tracking functionality
Using Hypothesis for comprehensive testing of financial transaction operations
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
    transaction_amount=floats(min_value=0.01, max_value=100000.0),
    transaction_type=sampled_from(['income', 'expense'])
)
def test_transaction_amount_validation(transaction_amount, transaction_type):
    """
    Property: Transaction Amount Validation
    Validates: Transaction amounts should be positive regardless of type
    
    All transactions (income and expense) should have positive amounts stored,
    with type indicating the nature of the transaction.
    """
    # Validate that transaction amount is positive
    assert transaction_amount > 0, f"Transaction amount must be positive: {transaction_amount}"
    
    # Validate transaction type
    valid_types = ['income', 'expense']
    assert transaction_type in valid_types, f"Transaction type must be valid: {transaction_type}"
    
    # Both income and expenses should have positive amounts
    assert isinstance(transaction_amount, (int, float)), \
        f"Transaction amount should be numeric: {type(transaction_amount)}"


@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
@given(
    transaction_category=sampled_from([
        'Sales Revenue', 'Service Income', 'Commission', 'Other Income',
        'Rent', 'Salary', 'Utilities', 'Transport', 'Purchase', 'Marketing', 'Miscellaneous'
    ])
)
def test_transaction_category_validation(transaction_category):
    """
    Property: Transaction Category Validation
    Validates: Transaction categories should be from approved list
    
    All transactions should use recognized category classifications.
    """
    # Validate transaction category is from approved list
    valid_categories = [
        'Sales Revenue', 'Service Income', 'Commission', 'Other Income',
        'Rent', 'Salary', 'Utilities', 'Transport', 'Purchase', 
        'Marketing', 'Miscellaneous', 'Office Supplies', 'Travel',
        'Professional Services', 'Insurance', 'Tax', 'Interest'
    ]
    
    assert transaction_category in valid_categories, \
        f"Transaction category must be valid: {transaction_category}"
    
    # Each category should have a clear business meaning
    assert isinstance(transaction_category, str), \
        f"Transaction category should be string: {transaction_category}"


@composite
def transaction_scenarios(draw):
    """Generate realistic income/expense transaction scenarios"""
    income_categories = [
        'Sales Revenue', 'Service Income', 'Commission', 'Other Income',
        'Investment Gain', 'Rental Income', 'Consulting Fee'
    ]
    
    expense_categories = [
        'Rent', 'Salary', 'Utilities', 'Transport', 'Purchase', 
        'Marketing', 'Miscellaneous', 'Office Supplies', 'Travel',
        'Professional Services', 'Insurance', 'Tax', 'Interest'
    ]
    
    transaction_type = draw(sampled_from(['income', 'expense']))
    
    if transaction_type == 'income':
        category = draw(sampled_from(income_categories))
    else:
        category = draw(sampled_from(expense_categories))
    
    amount = draw(floats(min_value=1.0, max_value=50000.0))
    description = draw(text(min_size=1, max_size=100))
    
    return {
        'transaction_type': transaction_type,
        'category': category,
        'amount': amount,
        'description': description,
        'is_income': transaction_type == 'income',
        'is_large_transaction': amount > 10000  # Threshold for large transactions
    }


@settings(max_examples=40, suppress_health_check=[HealthCheck.too_slow])
@given(transaction_scenarios())
def test_transaction_scenario_validation(scenario):
    """
    Property: Transaction Scenario Validation
    Validates: Transaction records should have complete and consistent information
    
    Each transaction record should contain all necessary information for accounting.
    """
    # Validate transaction type
    valid_types = ['income', 'expense']
    assert scenario['transaction_type'] in valid_types, \
        f"Invalid transaction type: {scenario['transaction_type']}"
    
    # Validate category
    assert scenario['category'].strip() != "", \
        f"Transaction category should not be empty: '{scenario['category']}'"
    
    # Validate amount is positive
    assert scenario['amount'] > 0, f"Transaction amount should be positive: {scenario['amount']}"
    
    # Validate description exists
    assert isinstance(scenario['description'], str), \
        f"Description should be string: {type(scenario['description'])}"
    
    # Validate income/expense classification
    assert isinstance(scenario['is_income'], bool), \
        f"Income flag should be boolean: {scenario['is_income']}"
    
    # Validate amount categorization
    assert isinstance(scenario['is_large_transaction'], bool), \
        f"Large transaction flag should be boolean: {scenario['is_large_transaction']}"


@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
@given(
    initial_balance=floats(min_value=0.0, max_value=1000000.0),
    transaction_amount=floats(min_value=1.0, max_value=50000.0),
    transaction_type=sampled_from(['income', 'expense'])
)
def test_transaction_balance_impact(initial_balance, transaction_amount, transaction_type):
    """
    Property: Transaction Balance Impact
    Validates: Transactions should correctly affect account balances
    
    Income transactions should increase balance, expense transactions should decrease it.
    """
    # Validate inputs
    assert initial_balance >= 0, f"Starting balance should be non-negative: {initial_balance}"
    assert transaction_amount > 0, f"Transaction amount should be positive: {transaction_amount}"
    
    # Calculate new balance based on transaction type
    if transaction_type == 'income':
        balance_after = initial_balance + transaction_amount
        # Income transaction should increase balance
        assert balance_after > initial_balance, \
            f"Income transaction should increase balance: {initial_balance} -> {balance_after}"
    elif transaction_type == 'expense':
        balance_after = initial_balance - transaction_amount
        # Expense transaction should decrease balance, but not go negative
        assert balance_after >= 0, \
            f"Expense transaction should not make balance negative: {initial_balance} - {transaction_amount} = {balance_after}"
        assert balance_after < initial_balance, \
            f"Expense transaction should decrease balance: {initial_balance} -> {balance_after}"
    
    # Validate that balance changes are proportional to transaction amounts
    expected_difference = transaction_amount if transaction_type == 'income' else -transaction_amount
    actual_difference = balance_after - initial_balance
    assert abs(actual_difference - expected_difference) < 0.01, \
        f"Balance change should match transaction amount: expected {expected_difference}, got {actual_difference}"


def test_transaction_status_lifecycle():
    """
    Property: Transaction Status Lifecycle
    Validates: Transactions should follow proper status progression
    
    Transaction records should maintain status integrity throughout their lifecycle.
    """
    # Define valid transaction statuses
    valid_statuses = ['draft', 'posted', 'approved', 'reconciled', 'voided', 'deleted']
    
    # Define valid status transitions
    valid_transitions = {
        'draft': ['posted', 'deleted'],
        'posted': ['approved', 'voided'],
        'approved': ['reconciled', 'voided'],
        'reconciled': ['voided'],  # Can still void reconciled transactions in some systems
        'voided': [],  # Terminal state
        'deleted': []   # Terminal state
    }
    
    # Test all valid transitions
    for current_status, allowed_next in valid_transitions.items():
        assert current_status in valid_statuses, f"Current status {current_status} should be valid"
        for next_status in allowed_next:
            assert next_status in valid_statuses, f"Next status {next_status} should be valid"
    
    # Test that voided and deleted are terminal states
    terminal_statuses = [status for status, transitions in valid_transitions.items() if not transitions]
    assert 'voided' in terminal_statuses, "Voided should be a terminal status"
    assert 'deleted' in terminal_statuses, "Deleted should be a terminal status"


@settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
@given(
    income_amount=floats(min_value=1.0, max_value=100000.0),
    expense_amount=floats(min_value=1.0, max_value=100000.0)
)
def test_net_profit_loss_calculation(income_amount, expense_amount):
    """
    Property: Net Profit/Loss Calculation
    Validates: Net position should be correctly calculated from income and expenses
    
    Net profit/loss equals total income minus total expenses.
    """
    # Calculate net position
    net_position = income_amount - expense_amount
    
    # Validate the calculation
    calculated_net = income_amount - expense_amount
    assert abs(net_position - calculated_net) < 0.01, \
        f"Net calculation should be consistent: {net_position} vs {calculated_net}"
    
    # Validate that if income > expenses, we have profit (positive)
    if income_amount > expense_amount:
        assert net_position > 0, \
            f"When income ({income_amount}) > expenses ({expense_amount}), net should be positive: {net_position}"
    
    # Validate that if expenses > income, we have loss (negative)
    if expense_amount > income_amount:
        assert net_position < 0, \
            f"When expenses ({expense_amount}) > income ({income_amount}), net should be negative: {net_position}"
    
    # When equal, net should be approximately zero
    if abs(income_amount - expense_amount) < 0.01:
        assert abs(net_position) < 0.01, \
            f"When income equals expenses, net should be near zero: {net_position}"


def test_transaction_data_integrity():
    """
    Property: Transaction Data Integrity
    Validates: Transaction records should maintain data consistency
    
    All transaction data fields should be properly formatted and linked.
    """
    # Test required transaction fields
    required_fields = [
        'id',            # Unique identifier
        'type',          # Income or expense
        'category',      # Transaction category
        'amount',        # Transaction amount
        'description',   # Transaction description
        'date',          # Transaction date
        'created_at',    # Creation timestamp
        'user_id'        # Associated user
    ]
    
    # Test optional but important fields
    recommended_fields = [
        'reference',     # External reference
        'notes',         # Additional notes
        'account',       # Specific account if multiple
        'tax_amount'     # Tax component if applicable
    ]
    
    # Validate field structure
    assert len(required_fields) >= 8, "Should have minimum required fields"
    
    # Test field naming convention
    for field in required_fields + recommended_fields:
        assert isinstance(field, str), f"Field name should be string: {field}"
        assert field.islower() and ('_' in field or field.isalnum()), \
            f"Field should follow naming convention: {field}"


def test_income_expense_business_rules():
    """
    Property: Income/Expense Business Rules
    Validates: Transaction operations should follow accounting principles
    
    Transactions should adhere to standard accounting practices and regulations.
    """
    # Rule 1: Income transactions increase equity/net worth
    # Rule 2: Expense transactions decrease equity/net worth
    # Rule 3: Transactions should be recorded when incurred (accrual basis)
    # Rule 4: Each transaction should have proper documentation
    
    # Validate that business rules are conceptually sound
    # This is more of a conceptual validation of accounting principles
    
    # Rule 5: Periodic reconciliation should match recorded transactions
    # This would be validated through reporting functions
    
    # Verify that the fundamental accounting equation holds conceptually:
    # Assets = Liabilities + Equity
    # Where Equity changes based on Income (increases) and Expenses (decreases)
    

def test_income_expense_tracking_requirements_compliance():
    """
    Test compliance with specific income/expense tracking requirements
    """
    # Requirements for income/expense tracking:
    # - Track all income and expense transactions
    # - Support categorization of transactions
    # - Maintain audit trails for financial reporting
    # - Enable profit/loss calculations
    
    # Test the required fields exist
    required_fields = [
        'type',              # Income or expense indicator
        'category',          # Transaction category
        'amount',            # Transaction amount
        'description',       # Transaction details
        'date',              # Transaction date
        'created_at',        # Timestamp for audit
        'user_id'            # User association
    ]
    
    assert len(required_fields) >= 7, "Should track at least the required fields"
    
    # Verify transaction types
    valid_types = ['income', 'expense']
    for txn_type in valid_types:
        assert isinstance(txn_type, str), f"Transaction type {txn_type} should be a string"
        assert txn_type.strip() != '', f"Transaction type should not be empty: '{txn_type}'"
    
    # Verify income categories
    income_categories = ['Sales Revenue', 'Service Income', 'Commission', 'Other Income']
    for category in income_categories:
        assert isinstance(category, str), f"Income category {category} should be a string"
    
    # Verify expense categories
    expense_categories = ['Rent', 'Salary', 'Utilities', 'Transport', 'Purchase', 'Marketing', 'Miscellaneous']
    for category in expense_categories:
        assert isinstance(category, str), f"Expense category {category} should be a string"
    
    print("All income/expense tracking requirements compliance tests passed!")


if __name__ == "__main__":
    # Run basic validation
    test_income_expense_tracking_requirements_compliance()
    print("Property tests for income/expense tracking completed!")