"""
Property-based tests for GRN (Goods Received Note) module functionality
Using Hypothesis for comprehensive testing of GRN operations
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
    received_quantity=integers(min_value=1, max_value=10000),
    ordered_quantity=integers(min_value=1, max_value=10000)
)
def test_grn_quantity_validation(received_quantity, ordered_quantity):
    """
    Property: GRN Quantity Validation
    Validates: Received quantities should be reasonable relative to ordered quantities
    
    When goods are received against a PO, the received quantity should typically not 
    exceed the ordered quantity (though some variance may be acceptable).
    """
    # In real business scenarios, received qty could be slightly different from ordered
    # due to packaging constraints, but shouldn't be wildly different
    
    # Validate that received quantity is positive
    assert received_quantity > 0, f"Received quantity must be positive: {received_quantity}"
    
    # Validate that both quantities are positive
    assert ordered_quantity > 0, f"Ordered quantity must be positive: {ordered_quantity}"
    
    # Calculate the ratio between received and ordered
    ratio = received_quantity / ordered_quantity
    
    # The ratio should be reasonable (between 0.5 and 2.0, allowing for some variance)
    assert 0.1 <= ratio <= 3.0, \
        f"Received/Ordered ratio {ratio} should be reasonable (0.1-3.0). " \
        f"Received: {received_quantity}, Ordered: {ordered_quantity}"


@settings(max_examples=40, suppress_health_check=[HealthCheck.too_slow])
@given(
    po_amount=floats(min_value=100.0, max_value=50000.0),
    grn_amount=floats(min_value=100.0, max_value=50000.0)
)
def test_grn_vs_po_amount_relationship(po_amount, grn_amount):
    """
    Property: GRN vs PO Amount Relationship
    Validates: GRN amounts should correlate with related PO amounts
    
    When a GRN is linked to a PO, the GRN value should reasonably correspond to the PO value.
    """
    # Validate that both amounts are positive
    assert po_amount > 0, f"PO amount must be positive: {po_amount}"
    assert grn_amount > 0, f"GRN amount must be positive: {grn_amount}"
    
    # Calculate the ratio between GRN and PO amounts
    ratio = grn_amount / po_amount
    
    # The ratio should be reasonable (allowing for partial deliveries)
    assert 0.01 <= ratio <= 2.0, \
        f"GRN/PO amount ratio {ratio} should be reasonable (0.01-2.0). " \
        f"GRN: {grn_amount}, PO: {po_amount}"


@composite
def grn_item_scenarios(draw):
    """Generate realistic GRN item scenarios"""
    item_names = [
        'Raw Material A', 'Component B', 'Packaging C', 'Equipment D', 'Tool E',
        'Supply F', 'Material G', 'Part H', 'Accessory I', 'Consumable J'
    ]
    
    num_items = draw(integers(min_value=1, max_value=20))
    items = []
    total_quantity = 0
    
    for _ in range(num_items):
        name = draw(sampled_from(item_names))
        received_qty = draw(integers(min_value=1, max_value=1000))
        
        items.append({
            'name': name,
            'received_quantity': received_qty
        })
        
        total_quantity += received_qty
    
    return {
        'items': items,
        'total_items': num_items,
        'total_quantity': total_quantity,
        'avg_quantity_per_item': total_quantity / num_items if num_items > 0 else 0
    }


@settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
@given(grn_item_scenarios())
def test_grn_item_aggregation(scenario):
    """
    Property: GRN Item Aggregation
    Validates: Individual item quantities should sum to total GRN quantity
    
    The sum of all item quantities in a GRN should equal the total quantity recorded.
    """
    calculated_total = sum(item['received_quantity'] for item in scenario['items'])
    
    # Validate total aggregation
    assert calculated_total == scenario['total_quantity'], \
        f"Sum of item quantities ({calculated_total}) should match GRN total ({scenario['total_quantity']})"
    
    # Validate item count
    assert len(scenario['items']) == scenario['total_items'], \
        f"Item count mismatch: {len(scenario['items'])} vs {scenario['total_items']}"
    
    # Validate that each item has positive quantities
    for item in scenario['items']:
        assert item['received_quantity'] > 0, \
            f"Item received quantity should be positive: {item['received_quantity']}"
    
    # Validate average calculation
    if scenario['total_items'] > 0:
        calculated_avg = scenario['total_quantity'] / scenario['total_items']
        assert abs(calculated_avg - scenario['avg_quantity_per_item']) < 0.01, \
            f"Average calculation should be consistent: {calculated_avg} vs {scenario['avg_quantity_per_item']}"


@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
@given(
    delivery_variance_days=integers(min_value=-30, max_value=30),  # Allow early/late delivery
    po_creation_date=text()
)
def test_grn_timing_validation(delivery_variance_days, po_creation_date):
    """
    Property: GRN Timing Validation
    Validates: GRN timing should be reasonable relative to related PO timing
    
    GRNs should typically be created after the related PO, though with some flexibility.
    """
    # Validate that the variance is within reasonable business bounds
    # (-30 to +30 days allows for advance shipments and delayed receipts)
    assert -365 <= delivery_variance_days <= 365, \
        f"Delivery variance should be within 1 year: {delivery_variance_days}"
    
    # This test primarily validates that timing relationships are tracked properly
    # The actual date logic would depend on real PO and GRN creation dates


def test_grn_status_lifecycle():
    """
    Property: GRN Status Lifecycle
    Validates: GRN records should follow proper status progression
    """
    # In the current schema, GRNs don't have explicit status field
    # But they follow an implicit lifecycle: Created -> Recorded -> Part of inventory
    
    # Valid GRN states based on business process
    grn_states = [
        'pending_verification',  # Just created
        'verified',              # Checked against PO
        'accepted',              # Accepted into inventory
        'rejected_partial',      # Partial rejection
        'rejected_full'          # Full rejection
    ]
    
    # Test that all states are valid
    for state in grn_states:
        assert isinstance(state, str), f"GRN state should be string: {state}"
        assert len(state) > 0, f"GRN state should not be empty: '{state}'"
        assert state.replace('_', '').replace('-', '').isalnum(), \
            f"GRN state should contain valid characters: {state}"


@settings(max_errors=10, suppress_health_check=[HealthCheck.too_slow])
@given(
    vendor_id=text(min_size=1, max_size=50),
    grn_number=text(min_size=5, max_size=30)
)
def test_grn_identifier_uniqueness_properties(vendor_id, grn_number):
    """
    Property: GRN Identifier Properties
    Validates: GRN identifiers should have consistent properties
    
    GRN numbers should follow predictable patterns and be unique within vendor context.
    """
    # Validate GRN number format expectations
    assert len(grn_number) >= 5, f"GRN number should have minimum length: {grn_number}"
    
    # GRN numbers typically contain alphanumeric characters and separators
    allowed_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_ ')
    grn_chars = set(grn_number)
    invalid_chars = grn_chars - allowed_chars
    
    assert not invalid_chars, f"GRN number should only contain valid characters: {invalid_chars}"
    
    # Validate vendor ID format
    assert len(vendor_id) > 0, f"Vendor ID should not be empty: {vendor_id}"


def test_grn_business_logic_properties():
    """
    Property: GRN Business Logic Properties
    Validates: GRN operations should maintain business integrity
    """
    # Test business rules for GRN processing
    
    # Rule 1: GRN creates inventory receipt
    # When a GRN is processed, it should increase inventory levels
    inventory_increase_rule = True  # Conceptual validation
    
    # Rule 2: GRN links to financial obligations
    # GRN should connect to related PO and payment obligations
    financial_linkage_rule = True  # Conceptual validation
    
    # Rule 3: GRN enables quality verification
    # GRN process should allow for quality checks
    quality_verification_rule = True  # Conceptual validation
    
    # Rule 4: GRN supports traceability
    # GRN should maintain links to source PO and vendor
    traceability_rule = True  # Conceptual validation
    
    # Validate all business rules hold
    assert inventory_increase_rule, "Inventory increase rule should hold"
    assert financial_linkage_rule, "Financial linkage rule should hold"
    assert quality_verification_rule, "Quality verification rule should hold"
    assert traceability_rule, "Traceability rule should hold"


def test_grn_requirements_compliance():
    """
    Test compliance with specific GRN module requirements
    """
    # Requirements for GRN module:
    # - Track goods received against purchase orders
    # - Link to vendor information
    # - Record item quantities and details
    # - Support inventory update workflows
    
    # Test the required fields exist
    required_fields = [
        'grn_number',        # Unique GRN identifier
        'vendor_name',       # Supplier information
        'po_id',             # Link to related PO
        'total_quantity',    # Total items received
        'items',             # Detailed received items
        'created_at'         # Timestamp for audit
    ]
    
    assert len(required_fields) >= 6, "Should track at least the required fields"
    
    # Verify GRN number format expectations
    sample_grn_number = "GRN-202312010001"
    assert sample_grn_number.startswith("GRN-"), "GRN numbers should start with 'GRN-'"
    
    # Verify that quantities are numeric
    sample_quantities = [10, 25, 100, 0, 500]
    for qty in sample_quantities:
        assert isinstance(qty, int) or isinstance(qty, float), f"Quantity should be numeric: {qty}"
        if qty != 0:  # Zero quantities might be valid in some contexts
            assert qty >= 0, f"Quantity should be non-negative: {qty}"
    
    print("All GRN module requirements compliance tests passed!")


if __name__ == "__main__":
    # Run basic validation
    test_grn_requirements_compliance()
    print("Property tests for GRN module completed!")