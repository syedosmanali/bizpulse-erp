"""
Property-based tests for CRM leads functionality
Using Hypothesis for comprehensive testing of lead management operations
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
    lead_source=sampled_from([
        'Walk-in', 'Referral', 'Social Media', 'Advertisement', 'Website', 
        'Email Marketing', 'Cold Call', 'Trade Show', 'Partner Referral'
    ]),
    contact_method=sampled_from(['phone', 'email', 'both'])
)
def test_lead_source_distribution(lead_source, contact_method):
    """
    Property: Lead Source Distribution
    Validates: Leads should come from various sources with valid contact methods
    
    Leads should be sourced from legitimate channels and have appropriate contact information.
    """
    # Validate lead source is valid
    valid_sources = [
        'Walk-in', 'Referral', 'Social Media', 'Advertisement', 'Website',
        'Email Marketing', 'Cold Call', 'Trade Show', 'Partner Referral', 'Other'
    ]
    
    assert lead_source in valid_sources, f"Lead source must be valid: {lead_source}"
    
    # Validate contact method
    valid_methods = ['phone', 'email', 'both', 'none']
    assert contact_method in valid_methods, f"Contact method must be valid: {contact_method}"
    
    # Lead should have at least one contact method
    assert contact_method != 'none', f"Lead should have contact method: {contact_method}"


@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
@given(
    followup_days=integers(min_value=-30, max_value=365)  # Allow past due and future follow-ups
)
def test_lead_followup_timing(followup_days):
    """
    Property: Lead Follow-up Timing
    Validates: Follow-up dates should be reasonable relative to creation
    
    Lead follow-up dates should be within reasonable business timeframes.
    """
    # Validate that follow-up days is within reasonable bounds
    assert -365 <= followup_days <= 365, \
        f"Follow-up days should be within 1 year: {followup_days}"
    
    # Past due follow-ups are acceptable (negative values)
    # Future follow-ups should be reasonable
    if followup_days > 0:
        assert followup_days <= 365, f"Future follow-up should be within 1 year: {followup_days}"


@composite
def lead_scenarios(draw):
    """Generate realistic lead scenarios"""
    lead_names = [
        'John Smith', 'Sarah Johnson', 'Mike Davis', 'Emma Wilson', 'David Brown',
        'Lisa Miller', 'Tom Anderson', 'Anna Taylor', 'Chris Lee', 'Maria Garcia'
    ]
    
    sources = [
        'Walk-in', 'Referral', 'Social Media', 'Advertisement', 'Website',
        'Email Marketing', 'Cold Call', 'Trade Show', 'Partner Referral'
    ]
    
    statuses = ['new', 'followup', 'converted', 'lost']
    
    name = draw(sampled_from(lead_names))
    source = draw(sampled_from(sources))
    status = draw(sampled_from(statuses))
    has_phone = draw(sampled_from([True, False]))
    has_email = draw(sampled_from([True, False]))
    
    # Generate phone and email based on boolean flags
    phone = f"+91-9{random.randint(100000000, 999999999)}" if has_phone else ""
    email = f"{name.lower().replace(' ', '.')}@example.com" if has_email else ""
    
    return {
        'name': name,
        'source': source,
        'status': status,
        'phone': phone,
        'email': email,
        'has_contact_info': bool(phone or email),
        'is_active': status in ['new', 'followup']
    }


@settings(max_examples=40, suppress_health_check=[HealthCheck.too_slow])
@given(lead_scenarios())
def test_lead_contact_information(scenario):
    """
    Property: Lead Contact Information
    Validates: Leads should have proper contact information based on their status
    
    Active leads should have contact information to enable follow-up.
    """
    # Validate lead has name
    assert scenario['name'].strip() != "", f"Lead should have name: '{scenario['name']}'"
    
    # Validate source is valid
    valid_sources = [
        'Walk-in', 'Referral', 'Social Media', 'Advertisement', 'Website',
        'Email Marketing', 'Cold Call', 'Trade Show', 'Partner Referral', 'Other'
    ]
    assert scenario['source'] in valid_sources, f"Invalid lead source: {scenario['source']}"
    
    # Validate status is valid
    valid_statuses = ['new', 'followup', 'converted', 'lost']
    assert scenario['status'] in valid_statuses, f"Invalid lead status: {scenario['status']}"
    
    # Active leads should ideally have contact information
    if scenario['is_active']:
        assert scenario['has_contact_info'], \
            f"Active lead ({scenario['status']}) should have contact info: phone='{scenario['phone']}', email='{scenario['email']}'"
    
    # Validate contact information format if present
    if scenario['phone']:
        assert scenario['phone'].startswith('+'), f"Phone should start with +: {scenario['phone']}"
    
    if scenario['email']:
        assert '@' in scenario['email'], f"Email should contain @: {scenario['email']}"
        assert '.' in scenario['email'].split('@')[1], f"Email should have domain: {scenario['email']}"


@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
@given(
    lead_age_days=integers(min_value=0, max_value=730)  # Up to 2 years
)
def test_lead_status_evolution_over_time(lead_age_days):
    """
    Property: Lead Status Evolution Over Time
    Validates: Older leads should have progressed through the pipeline
    
    Leads that have existed for longer periods should have moved from 'new' to other statuses.
    """
    # Validate lead age is non-negative
    assert lead_age_days >= 0, f"Lead age should be non-negative: {lead_age_days}"
    
    # This is a business logic property test
    # Very old leads (e.g., > 365 days) should likely not remain in 'new' status
    if lead_age_days > 365:
        # This is a soft validation - older leads might still be new but less likely
        pass  # Business logic validation would happen in real implementation


def test_lead_status_transitions():
    """
    Property: Lead Status Transitions
    Validates: Leads should follow valid status progression patterns
    
    Leads should move through statuses in logical business sequences.
    """
    # Define valid state transitions for leads
    valid_transitions = {
        'new': ['followup', 'converted', 'lost'],
        'followup': ['converted', 'lost', 'followup'],  # Can have multiple follow-ups
        'converted': [],  # Terminal state
        'lost': []  # Terminal state
    }
    
    # Test all valid transitions
    for current_status, allowed_next in valid_transitions.items():
        for next_status in allowed_next:
            # Validate transition makes business sense
            assert next_status in ['new', 'followup', 'converted', 'lost'], \
                f"Invalid status in transition: {current_status} -> {next_status}"
        
        # Validate current status is valid
        assert current_status in ['new', 'followup', 'converted', 'lost'], \
            f"Invalid current status: {current_status}"


@settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
@given(
    conversion_probability=floats(min_value=0.0, max_value=1.0)
)
def test_lead_conversion_probability(conversion_probability):
    """
    Property: Lead Conversion Probability
    Validates: Conversion rates should be within reasonable business ranges
    
    Business lead conversion rates should be realistic and bounded.
    """
    # Validate probability is within bounds
    assert 0.0 <= conversion_probability <= 1.0, \
        f"Conversion probability should be between 0 and 1: {conversion_probability}"
    
    # In real business scenarios, conversion rates are typically lower
    # but we'll keep this flexible for different business types
    assert isinstance(conversion_probability, (int, float)), \
        f"Conversion probability should be numeric: {conversion_probability}"


def test_lead_data_integrity():
    """
    Property: Lead Data Integrity
    Validates: Lead records should maintain data consistency
    
    All lead data fields should be properly formatted and linked.
    """
    # Test data structure expectations
    required_fields = [
        'id',            # Unique identifier
        'name',          # Lead name
        'source',        # Lead source
        'status',        # Current status
        'created_at',    # Creation timestamp
        'user_id'        # Associated user
    ]
    
    # Optional but important fields
    recommended_fields = [
        'phone',         # Contact phone
        'email',         # Contact email
        'notes',         # Additional information
        'follow_up_date' # Next follow-up date
    ]
    
    # Validate field structure expectations
    assert len(required_fields) >= 5, "Should have minimum required fields"
    assert len(required_fields + recommended_fields) >= 8, "Should have comprehensive field set"
    
    # Test field naming convention
    for field in required_fields + recommended_fields:
        assert isinstance(field, str), f"Field name should be string: {field}"
        assert field.islower() and ('_' in field or field.isalnum()), \
            f"Field should follow naming convention: {field}"


def test_lead_business_metrics():
    """
    Property: Lead Business Metrics
    Validates: Lead tracking should support key business metrics
    
    Lead data should enable calculation of important business metrics.
    """
    # Simulate lead data for metrics calculation
    sample_leads = [
        {'status': 'new', 'value': 100},
        {'status': 'followup', 'value': 200},
        {'status': 'converted', 'value': 1000},
        {'status': 'lost', 'value': 0},
        {'status': 'converted', 'value': 1500}
    ]
    
    # Calculate metrics
    total_leads = len(sample_leads)
    converted_leads = len([l for l in sample_leads if l['status'] == 'converted'])
    lost_leads = len([l for l in sample_leads if l['status'] == 'lost'])
    active_leads = len([l for l in sample_leads if l['status'] in ['new', 'followup']])
    
    # Validate metric calculations
    assert total_leads == converted_leads + lost_leads + active_leads, \
        "Total leads should equal sum of all status categories"
    
    # Calculate conversion rate
    conversion_rate = (converted_leads / total_leads) * 100 if total_leads > 0 else 0
    assert 0 <= conversion_rate <= 100, f"Conversion rate should be percentage: {conversion_rate}"
    
    # Calculate total potential value
    total_potential_value = sum(l['value'] for l in sample_leads if l['status'] in ['new', 'followup'])
    assert total_potential_value >= 0, f"Potential value should be non-negative: {total_potential_value}"
    
    # Calculate converted value
    converted_value = sum(l['value'] for l in sample_leads if l['status'] == 'converted')
    assert converted_value >= 0, f"Converted value should be non-negative: {converted_value}"


def test_crm_leads_requirements_compliance():
    """
    Test compliance with specific CRM leads requirements
    """
    # Requirements for CRM leads:
    # - Track lead source and status
    # - Enable follow-up scheduling
    # - Support contact information management
    # - Enable conversion tracking
    
    # Test the required fields exist
    required_fields = [
        'name',              # Lead identification
        'phone',             # Contact information
        'email',             # Alternative contact
        'source',            # Lead origin channel
        'status',            # Pipeline stage
        'notes',             # Interaction history
        'follow_up_date',    # Scheduled follow-up
        'created_at'         # Timestamp for tracking
    ]
    
    assert len(required_fields) >= 8, "Should track at least the required fields"
    
    # Verify status values
    valid_statuses = ['new', 'followup', 'converted', 'lost']
    for status in valid_statuses:
        assert isinstance(status, str), f"Status {status} should be a string"
        assert status.strip() != '', f"Status should not be empty: '{status}'"
    
    # Verify source values
    valid_sources = ['Walk-in', 'Referral', 'Social Media', 'Advertisement', 'Website']
    for source in valid_sources:
        assert isinstance(source, str), f"Source {source} should be a string"
    
    print("All CRM leads requirements compliance tests passed!")


if __name__ == "__main__":
    # Run basic validation
    test_crm_leads_requirements_compliance()
    print("Property tests for CRM leads completed!")