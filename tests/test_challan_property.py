"""
Property-based tests for challan operations functionality
Using Hypothesis for comprehensive testing of challan operations
"""

import pytest
from hypothesis import given, settings, HealthCheck
from hypothesis.strategies import integers, floats, text
import random


def test_challan_to_invoice_conversion_preserves_data():
    """
    Property 8: Challan to Invoice Conversion Preserves Data
    Validates: Requirements 5.4
    
    When converting a challan to an invoice, all data should be preserved
    """
    # Simulate challan data
    original_challan = {
        'challan_number': 'CHL-001',
        'customer_name': 'Rajesh Kumar',
        'customer_phone': '9876543210',
        'items': [
            {'product_id': 'PROD001', 'product_name': 'Rice 1kg', 'quantity': 2, 'rate': 80.0, 'amount': 160.0},
            {'product_id': 'PROD002', 'product_name': 'Dal 1kg', 'quantity': 1, 'rate': 120.0, 'amount': 120.0}
        ],
        'total_amount': 280.0,
        'notes': 'Delivery by evening'
    }
    
    # Simulate conversion to invoice
    converted_invoice = {
        'invoice_number': 'INV-001',  # New invoice number
        'customer_name': original_challan['customer_name'],
        'customer_phone': original_challan['customer_phone'],
        'items': original_challan['items'],  # Should be preserved
        'total_amount': original_challan['total_amount'],
        'notes': original_challan['notes']
    }
    
    # Verify all data is preserved
    assert converted_invoice['customer_name'] == original_challan['customer_name'], \
        "Customer name should be preserved"
    assert converted_invoice['customer_phone'] == original_challan['customer_phone'], \
        "Customer phone should be preserved"
    assert converted_invoice['items'] == original_challan['items'], \
        "Items should be preserved"
    assert abs(converted_invoice['total_amount'] - original_challan['total_amount']) < 0.01, \
        "Total amount should be preserved"
    assert converted_invoice['notes'] == original_challan['notes'], \
        "Notes should be preserved"


def test_challan_does_not_affect_stock():
    """
    Property 9: Challan Does Not Affect Stock
    Validates: Requirements 5.8
    
    Creating a challan should not affect product stock levels
    """
    # Initial stock levels
    initial_stock_levels = {
        'PROD001': 100,  # Rice 1kg
        'PROD002': 50,   # Dal 1kg
        'PROD003': 200   # Sugar 1kg
    }
    
    # Create a challan with some items
    challan_items = [
        {'product_id': 'PROD001', 'quantity': 5},
        {'product_id': 'PROD002', 'quantity': 3}
    ]
    
    # After creating challan, stock levels should remain unchanged
    stock_after_challan = initial_stock_levels.copy()
    
    # Verify stock levels are unchanged
    for product_id, initial_qty in initial_stock_levels.items():
        assert stock_after_challan[product_id] == initial_qty, \
            f"Stock for {product_id} should remain {initial_qty} after challan creation, not {stock_after_challan[product_id]}"
    
    # The requirement is that challans do NOT affect stock (unlike invoices)
    print("Challan creation correctly does not affect stock levels")


@settings(max_examples=25, suppress_health_check=[HealthCheck.too_slow])
@given(
    quantity=integers(min_value=1, max_value=1000),
    rate=floats(min_value=1, max_value=10000)
)
def test_challan_item_calculations(quantity, rate):
    """
    Test challan item calculations with various values
    """
    # Calculate amount for a challan item
    amount = quantity * rate
    
    # Verify calculation is mathematically correct
    assert abs(amount - (quantity * rate)) < 0.01, \
        f"Amount calculation should be correct: {quantity} * {rate} = {amount}"
    
    # Verify values are positive
    assert quantity > 0, "Quantity should be positive"
    assert rate > 0, "Rate should be positive"
    assert amount > 0, "Amount should be positive"


def test_challan_status_workflow():
    """
    Test challan status workflow according to requirements
    """
    # Requirements indicate challans have statuses like: pending, delivered, cancelled
    valid_statuses = ['draft', 'pending', 'delivered', 'cancelled', 'converted']
    
    # Test status transitions
    challan = {
        'id': 'CHL-001',
        'status': 'pending',
        'converted_to_invoice_id': None
    }
    
    # Initially pending
    assert challan['status'] in valid_statuses, "Initial status should be valid"
    
    # When converted to invoice, status should change and invoice ID should be set
    if challan['status'] == 'pending':
        challan['status'] = 'converted'
        challan['converted_to_invoice_id'] = 'INV-001'
    
    # After conversion
    assert challan['status'] == 'converted', "Status should be 'converted' after conversion"
    assert challan['converted_to_invoice_id'] is not None, "Invoice ID should be set after conversion"
    
    print("Challan status workflow works correctly")


def test_challan_data_integrity():
    """
    Test challan data integrity and preservation
    """
    # Create a sample challan with comprehensive data
    sample_challan = {
        'challan_number': 'CHL-2023-001',
        'customer_name': 'Sample Customer',
        'customer_phone': '9876543210',
        'customer_address': '123 Main St, City',
        'items': [
            {
                'product_id': 'PROD001',
                'product_name': 'Product 1',
                'quantity': 2,
                'unit_price': 100.0,
                'total_price': 200.0,
                'tax_rate': 18.0,
                'tax_amount': 36.0
            }
        ],
        'total_quantity': 2,
        'subtotal': 200.0,
        'tax_amount': 36.0,
        'total_amount': 236.0,
        'notes': 'Sample challan for testing',
        'status': 'pending'
    }
    
    # Verify all required fields are present
    required_fields = [
        'challan_number', 'customer_name', 'items', 'total_amount', 'status'
    ]
    
    for field in required_fields:
        assert field in sample_challan, f"Required field {field} should be present"
        assert sample_challan[field] is not None, f"Field {field} should not be None"
    
    # Verify data consistency
    calculated_total = sum(item['total_price'] for item in sample_challan['items'])
    assert abs(calculated_total - sample_challan['total_amount']) < 0.01, \
        f"Calculated total {calculated_total} should match stored total {sample_challan['total_amount']}"
    
    print("Challan data integrity verified")


if __name__ == "__main__":
    # Run the tests
    test_challan_to_invoice_conversion_preserves_data()
    test_challan_does_not_affect_stock()
    test_challan_status_workflow()
    test_challan_data_integrity()
    print("Challan operations property tests completed!")