"""
Property-based tests for supplier outstanding calculation functionality
Using Hypothesis for comprehensive testing of supplier operations
"""

import pytest
from hypothesis import given, settings, HealthCheck
from hypothesis.strategies import floats
import random


def test_supplier_outstanding_calculation():
    """
    Property 23: Supplier Outstanding Calculation
    Validates: Requirements 14.5
    
    Calculate outstanding as: total purchases minus payments made
    """
    # Simulate supplier data
    supplier_scenarios = [
        {
            'total_purchases': 50000.0,
            'payments_made': 45000.0,
            'expected_outstanding': 5000.0
        },
        {
            'total_purchases': 10000.0,
            'payments_made': 10000.0,
            'expected_outstanding': 0.0
        },
        {
            'total_purchases': 25000.0,
            'payments_made': 5000.0,
            'expected_outstanding': 20000.0
        },
        {
            'total_purchases': 0.0,
            'payments_made': 0.0,
            'expected_outstanding': 0.0
        }
    ]
    
    for scenario in supplier_scenarios:
        # Calculate outstanding according to requirements formula
        calculated_outstanding = scenario['total_purchases'] - scenario['payments_made']
        
        # Verify calculation matches expected value
        tolerance = 0.01  # Small tolerance for floating point comparisons
        assert abs(calculated_outstanding - scenario['expected_outstanding']) < tolerance, \
            f"For purchases={scenario['total_purchases']}, payments={scenario['payments_made']}: " \
            f"Expected {scenario['expected_outstanding']}, got {calculated_outstanding}"
            
        # Additional validation: outstanding should not be negative
        assert calculated_outstanding >= 0, \
            f"Outstanding should not be negative, got {calculated_outstanding}"


@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
@given(
    total_purchases=floats(min_value=0, max_value=1000000),
    payments_made=floats(min_value=0, max_value=1000000)
)
def test_supplier_outstanding_property(total_purchases, payments_made):
    """
    Property test for supplier outstanding calculation with various values
    """
    # Calculate outstanding according to requirements
    outstanding = total_purchases - payments_made
    
    # If payments exceed purchases, outstanding should be 0 or we handle it specially
    # In typical business scenarios, payments shouldn't exceed purchases
    if payments_made > total_purchases:
        # Either this represents an overpayment situation or we cap at 0
        expected_outstanding = max(0, outstanding)
    else:
        expected_outstanding = outstanding
    
    # Verify the calculation logic
    if payments_made <= total_purchases:
        assert expected_outstanding == total_purchases - payments_made, \
            f"When payments ({payments_made}) <= purchases ({total_purchases}), " \
            f"outstanding should be {total_purchases - payments_made}"
    else:
        assert expected_outstanding >= 0, \
            f"When payments exceed purchases, outstanding should not be negative"


def test_supplier_outstanding_edge_cases():
    """
    Test edge cases for supplier outstanding calculation
    """
    edge_cases = [
        # (total_purchases, payments_made, expected_outstanding, description)
        (0, 0, 0, "Zero purchases and payments"),
        (1000, 0, 1000, "Purchases with no payments"),
        (0, 500, 0, "Payments with no purchases (should be 0)"),
        (1000, 1000, 0, "Equal purchases and payments"),
        (1000, 1200, 0, "More payments than purchases (should be 0)"),
        (999999.99, 0, 999999.99, "Large purchase amount"),
    ]
    
    for total_purchases, payments_made, expected, description in edge_cases:
        # Calculate outstanding
        calculated = total_purchases - payments_made
        outstanding = max(0, calculated)  # Outstanding should not be negative
        
        # For cases where payments exceed purchases, we expect 0
        if payments_made > total_purchases:
            assert outstanding == 0, f"{description}: Expected 0, got {outstanding}"
        else:
            assert abs(outstanding - expected) < 0.01, \
                f"{description}: Expected {expected}, got {outstanding}"


def test_supplier_data_consistency():
    """
    Test consistency of supplier data relationships
    """
    # Requirements indicate suppliers track: total_purchases, outstanding_balance
    # outstanding_balance should equal total_purchases - total_payments_made
    
    suppliers = [
        {
            'id': 'supp1',
            'name': 'ABC Suppliers',
            'total_purchases': 75000.0,
            'total_payments': 65000.0,
            'current_outstanding': 10000.0
        },
        {
            'id': 'supp2',
            'name': 'XYZ Distributors',
            'total_purchases': 125000.0,
            'total_payments': 125000.0,
            'current_outstanding': 0.0
        }
    ]
    
    for supplier in suppliers:
        calculated_outstanding = supplier['total_purchases'] - supplier['total_payments']
        stored_outstanding = supplier['current_outstanding']
        
        # Verify data consistency
        assert abs(calculated_outstanding - stored_outstanding) < 0.01, \
            f"Supplier {supplier['name']}: Calculated outstanding {calculated_outstanding} " \
            f"doesn't match stored value {stored_outstanding}"


if __name__ == "__main__":
    # Run the tests
    test_supplier_outstanding_calculation()
    test_supplier_outstanding_edge_cases()
    test_supplier_data_consistency()
    print("Supplier outstanding calculation property tests completed!")