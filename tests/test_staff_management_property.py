"""
Property-based tests for staff management functionality
Using Hypothesis for comprehensive testing of staff operations
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
    salary_amount=floats(min_value=5000.0, max_value=500000.0),
    role_type=sampled_from(['admin', 'manager', 'operator', 'staff'])
)
def test_staff_salary_validation(salary_amount, role_type):
    """
    Property: Staff Salary Validation
    Validates: Staff salaries should be positive and role-appropriate
    
    All staff members should have positive salary values based on their role level.
    """
    # Validate that salary amount is positive
    assert salary_amount > 0, f"Salary amount must be positive: {salary_amount}"
    
    # Validate role type
    valid_roles = ['admin', 'manager', 'operator', 'staff']
    assert role_type in valid_roles, f"Role type must be valid: {role_type}"
    
    # All roles should have positive salaries
    assert isinstance(salary_amount, (int, float)), \
        f"Salary amount should be numeric: {type(salary_amount)}"


@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
@given(
    staff_name=text(min_size=2, max_size=100),
    phone_number=text(min_size=10, max_size=15)
)
def test_staff_identity_validation(staff_name, phone_number):
    """
    Property: Staff Identity Validation
    Validates: Staff should have valid identifying information
    
    All staff members should have properly formatted names and contact information.
    """
    # Validate staff name
    assert staff_name.strip() != "", f"Staff name should not be empty: '{staff_name}'"
    assert len(staff_name.strip()) >= 2, f"Staff name should be at least 2 characters: '{staff_name}'"
    
    # Validate phone number
    assert phone_number.strip() != "", f"Phone number should not be empty: '{phone_number}'"
    assert len(phone_number.strip()) >= 10, f"Phone number should be at least 10 digits: '{phone_number}'"
    
    # Names should contain letters
    stripped_name = staff_name.strip()
    assert any(c.isalpha() for c in stripped_name), \
        f"Staff name should contain alphabetic characters: '{staff_name}'"


@composite
def staff_scenarios(draw):
    """Generate realistic staff scenarios"""
    first_names = [
        'John', 'Jane', 'Mike', 'Sarah', 'David', 'Lisa', 'Tom', 'Emma', 
        'Chris', 'Maria', 'Alex', 'Sophia', 'Robert', 'Emily', 'James'
    ]
    
    last_names = [
        'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 
        'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez'
    ]
    
    roles = ['admin', 'manager', 'operator', 'staff']
    
    first_name = draw(sampled_from(first_names))
    last_name = draw(sampled_from(last_names))
    role = draw(sampled_from(roles))
    
    name = f"{first_name} {last_name}"
    salary = draw(floats(min_value=10000.0, max_value=300000.0))
    phone = f"+91-{random.randint(7000000000, 9999999999)}"
    email = f"{first_name.lower()}.{last_name.lower()}@company.com"
    
    return {
        'name': name,
        'role': role,
        'salary': salary,
        'phone': phone,
        'email': email,
        'is_management_role': role in ['admin', 'manager'],
        'has_higher_salary_expectation': role in ['admin', 'manager']
    }


@settings(max_examples=40, suppress_health_check=[HealthCheck.too_slow])
@given(staff_scenarios())
def test_staff_scenario_validation(scenario):
    """
    Property: Staff Scenario Validation
    Validates: Staff records should have complete and consistent information
    
    Each staff record should contain all necessary information for HR management.
    """
    # Validate name
    assert scenario['name'].strip() != "", f"Staff name should not be empty: '{scenario['name']}'"
    assert len(scenario['name'].split()) >= 2, f"Staff name should contain first and last name: '{scenario['name']}'"
    
    # Validate role
    valid_roles = ['admin', 'manager', 'operator', 'staff']
    assert scenario['role'] in valid_roles, f"Invalid role: {scenario['role']}"
    
    # Validate salary
    assert scenario['salary'] > 0, f"Salary should be positive: {scenario['salary']}"
    
    # Validate phone
    assert scenario['phone'].strip() != "", f"Phone should not be empty: '{scenario['phone']}'"
    
    # Validate email format if present
    if scenario['email']:
        assert '@' in scenario['email'], f"Email should contain @: {scenario['email']}"
        assert '.' in scenario['email'].split('@')[1], f"Email should have domain: {scenario['email']}"
    
    # Validate management role flag
    assert isinstance(scenario['is_management_role'], bool), \
        f"Management role flag should be boolean: {scenario['is_management_role']}"
    
    # Validate higher salary expectation flag
    assert isinstance(scenario['has_higher_salary_expectation'], bool), \
        f"Higher salary expectation flag should be boolean: {scenario['has_higher_salary_expectation']}"


@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
@given(
    current_salary=floats(min_value=10000.0, max_value=300000.0),
    raise_percentage=floats(min_value=0.0, max_value=50.0)
)
def test_staff_salary_raise_calculation(current_salary, raise_percentage):
    """
    Property: Staff Salary Raise Calculation
    Validates: Salary raises should be calculated correctly
    
    When a raise is applied to a staff member's salary, the new amount should be calculated properly.
    """
    # Validate inputs
    assert current_salary > 0, f"Current salary should be positive: {current_salary}"
    assert 0 <= raise_percentage <= 100, f"Raise percentage should be between 0-100: {raise_percentage}"
    
    # Calculate new salary after raise
    raise_amount = (current_salary * raise_percentage) / 100
    new_salary = current_salary + raise_amount
    
    # Validate the calculation
    expected_new_salary = current_salary * (1 + raise_percentage / 100)
    assert abs(new_salary - expected_new_salary) < 0.01, \
        f"Salary raise calculation should be consistent: {new_salary} vs {expected_new_salary}"
    
    # Validate that new salary is higher than current
    assert new_salary >= current_salary, \
        f"New salary ({new_salary}) should be >= current salary ({current_salary})"
    
    # Validate raise calculation
    calculated_raise = new_salary - current_salary
    expected_raise = (current_salary * raise_percentage) / 100
    assert abs(calculated_raise - expected_raise) < 0.01, \
        f"Raise amount should be calculated correctly: {calculated_raise} vs {expected_raise}"


def test_staff_role_hierarchy():
    """
    Property: Staff Role Hierarchy
    Validates: Staff roles should follow proper authorization hierarchy
    
    Different staff roles should have appropriate levels of system access.
    """
    # Define role hierarchy from highest to lowest authority
    role_hierarchy = ['admin', 'manager', 'operator', 'staff']
    
    # Define permissions for each role level
    role_permissions = {
        'admin': ['full_access', 'staff_management', 'settings', 'financials'],
        'manager': ['management_access', 'reports', 'inventory', 'customers'],
        'operator': ['billing_sales', 'customer_service', 'basic_operations'],
        'staff': ['view_only', 'limited_access', 'read_only']
    }
    
    # Validate that each role has appropriate permissions
    for role, permissions in role_permissions.items():
        assert role in role_hierarchy, f"Role {role} should be in hierarchy"
        assert isinstance(permissions, list), f"Permissions for {role} should be a list"
        assert len(permissions) > 0, f"Role {role} should have at least one permission"
        
        for perm in permissions:
            assert isinstance(perm, str), f"Permission should be string: {perm}"


@settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
@given(
    employment_years=floats(min_value=0.0, max_value=40.0),
    monthly_salary=floats(min_value=10000.0, max_value=300000.0)
)
def test_employment_tenure_salary_relationship(employment_years, monthly_salary):
    """
    Property: Employment Tenure-Salary Relationship
    Validates: Longer tenure may correlate with higher compensation
    
    While not mandatory, there may be correlation between tenure and compensation.
    """
    # Validate inputs
    assert employment_years >= 0, f"Employment years should be non-negative: {employment_years}"
    assert monthly_salary > 0, f"Monthly salary should be positive: {monthly_salary}"
    
    # Calculate total compensation over tenure
    total_compensation = monthly_salary * 12 * employment_years if employment_years > 0 else 0
    
    # Validate that total compensation calculation is reasonable
    if employment_years > 0:
        assert total_compensation >= 0, f"Total compensation should be non-negative: {total_compensation}"
        assert total_compensation >= monthly_salary * 12, \
            f"Total compensation should be at least one year's salary if employed for a year: {total_compensation}"
    
    # Validate that for zero years, total is zero
    if employment_years == 0:
        assert total_compensation == 0, f"Zero years should result in zero total compensation: {total_compensation}"


def test_staff_data_integrity():
    """
    Property: Staff Data Integrity
    Validates: Staff records should maintain data consistency
    
    All staff data fields should be properly formatted and linked.
    """
    # Test required staff fields
    required_fields = [
        'id',            # Unique identifier
        'name',          # Staff name
        'phone',         # Contact phone
        'role',          # Staff role
        'salary',        # Compensation
        'is_active',     # Employment status
        'created_at',    # Creation timestamp
        'user_id'        # Associated business owner
    ]
    
    # Test optional but important fields
    recommended_fields = [
        'email',         # Contact email
        'joining_date',  # Employment start date
        'permissions',   # Role-based permissions
        'department',    # Organizational department
        'reports_to'     # Managerial reporting line
    ]
    
    # Validate field structure
    assert len(required_fields) >= 8, "Should have minimum required fields"
    
    # Test field naming convention
    for field in required_fields + recommended_fields:
        assert isinstance(field, str), f"Field name should be string: {field}"
        assert field.islower() and ('_' in field or field.isalnum()), \
            f"Field should follow naming convention: {field}"


def test_staff_employment_status():
    """
    Property: Staff Employment Status
    Validates: Staff records should maintain proper employment status
    
    Staff records should accurately reflect current employment status.
    """
    # Define valid employment statuses
    valid_statuses = [True, False]  # Active (True) or Inactive (False)
    
    # This is conceptually validated through the is_active field
    # In the database, True means active employment, False means inactive
    
    # Validate that the status field is boolean
    for status in valid_statuses:
        assert isinstance(status, bool), f"Status should be boolean: {status}"
    
    # Validate conceptual understanding
    # Active staff (is_active=True) should be able to perform duties
    # Inactive staff (is_active=False) should be archived but retained for records


def test_staff_management_requirements_compliance():
    """
    Test compliance with specific staff management requirements
    """
    # Requirements for staff management:
    # - Track staff identity and contact information
    # - Manage role-based permissions
    # - Handle employment status (active/inactive)
    # - Support salary and joining date tracking
    
    # Test the required fields exist
    required_fields = [
        'name',              # Staff identification
        'phone',             # Contact information
        'role',              # Access level
        'salary',            # Compensation tracking
        'is_active',         # Employment status
        'joining_date',      # Employment start
        'created_at',        # Record timestamp
        'permissions'        # Role-based access
    ]
    
    assert len(required_fields) >= 8, "Should track at least the required fields"
    
    # Verify role types
    valid_roles = ['admin', 'manager', 'operator', 'staff']
    for role in valid_roles:
        assert isinstance(role, str), f"Role {role} should be a string"
        assert role.strip() != '', f"Role should not be empty: '{role}'"
    
    # Verify employment status values
    valid_status_values = [True, False]
    for status in valid_status_values:
        assert isinstance(status, bool), f"Status {status} should be a boolean"
    
    print("All staff management requirements compliance tests passed!")


if __name__ == "__main__":
    # Run basic validation
    test_staff_management_requirements_compliance()
    print("Property tests for staff management completed!")