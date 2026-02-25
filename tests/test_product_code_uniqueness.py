"""
Property-Based Test for Product Code Uniqueness Per User

Feature: comprehensive-erp-modules
Property 16: Product Code Uniqueness Per User

**Validates: Requirements 9.8**

This test validates that product codes are unique within each user account,
while allowing different users to have products with the same product code
(multi-tenant isolation).
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck, assume
from hypothesis.strategies import composite
import uuid
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.shared.database import get_db_connection, generate_id, get_db_type


# ==================== TEST DATA GENERATORS ====================

@composite
def product_code_strategy(draw):
    """Generate random product codes"""
    prefix = draw(st.sampled_from(['PROD', 'ITEM', 'SKU', 'CODE']))
    number = draw(st.integers(min_value=1000, max_value=9999))
    return f"{prefix}-{number}"


@composite
def product_data_strategy(draw, user_id, product_code=None):
    """Generate random product data for a specific user"""
    if product_code is None:
        product_code = draw(product_code_strategy())
    
    return {
        'id': generate_id(),
        'user_id': user_id,
        'product_code': product_code,
        'product_name': draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), blacklist_characters='\x00'))),
        'category': draw(st.sampled_from(['Electronics', 'Grocery', 'Clothing', 'Hardware', 'Food'])),
        'hsn_code': draw(st.sampled_from(['1006', '100630', '10063010'])),
        'gst_rate': draw(st.sampled_from([0, 5, 12, 18, 28])),
        'unit': draw(st.sampled_from(['pcs', 'kg', 'ltr', 'box'])),
        'cost_price': draw(st.floats(min_value=10.0, max_value=1000.0)),
        'selling_price': draw(st.floats(min_value=20.0, max_value=2000.0)),
        'current_stock': draw(st.integers(min_value=0, max_value=1000)),
        'is_active': True
    }


# ==================== HELPER FUNCTIONS ====================

def create_test_user(conn, user_id):
    """Create a test user in the users table"""
    cursor = conn.cursor()
    db_type = get_db_type()
    
    try:
        if db_type == 'postgresql':
            cursor.execute("""
                INSERT INTO users (id, email, password_hash, business_name, is_active)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (user_id, f"user_{user_id}@test.com", "test_hash", f"Business_{user_id}", True))
        else:
            cursor.execute("""
                INSERT OR IGNORE INTO users (id, email, password_hash, business_name, is_active)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, f"user_{user_id}@test.com", "test_hash", f"Business_{user_id}", 1))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise


def insert_product(conn, product_data):
    """Insert a product into erp_products table"""
    cursor = conn.cursor()
    db_type = get_db_type()
    
    try:
        if db_type == 'postgresql':
            cursor.execute("""
                INSERT INTO erp_products 
                (id, user_id, product_code, product_name, category, hsn_code, 
                 gst_rate, unit, cost_price, selling_price, current_stock, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                product_data['id'], product_data['user_id'], product_data['product_code'],
                product_data['product_name'], product_data['category'], product_data['hsn_code'],
                product_data['gst_rate'], product_data['unit'], product_data['cost_price'],
                product_data['selling_price'], product_data['current_stock'], product_data['is_active']
            ))
        else:
            cursor.execute("""
                INSERT INTO erp_products 
                (id, user_id, product_code, product_name, category, hsn_code, 
                 gst_rate, unit, cost_price, selling_price, current_stock, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_data['id'], product_data['user_id'], product_data['product_code'],
                product_data['product_name'], product_data['category'], product_data['hsn_code'],
                product_data['gst_rate'], product_data['unit'], product_data['cost_price'],
                product_data['selling_price'], product_data['current_stock'], 1 if product_data['is_active'] else 0
            ))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        # Check if it's a uniqueness constraint violation
        error_msg = str(e).lower()
        if 'unique' in error_msg or 'duplicate' in error_msg:
            return False
        raise


def query_products_by_user(conn, user_id):
    """Query products for a specific user"""
    cursor = conn.cursor()
    db_type = get_db_type()
    
    if db_type == 'postgresql':
        cursor.execute("""
            SELECT id, user_id, product_code, product_name 
            FROM erp_products 
            WHERE user_id = %s
        """, (user_id,))
    else:
        cursor.execute("""
            SELECT id, user_id, product_code, product_name 
            FROM erp_products 
            WHERE user_id = ?
        """, (user_id,))
    
    return cursor.fetchall()


def query_product_by_code(conn, user_id, product_code):
    """Query a specific product by user_id and product_code"""
    cursor = conn.cursor()
    db_type = get_db_type()
    
    if db_type == 'postgresql':
        cursor.execute("""
            SELECT id, user_id, product_code, product_name 
            FROM erp_products 
            WHERE user_id = %s AND product_code = %s
        """, (user_id, product_code))
    else:
        cursor.execute("""
            SELECT id, user_id, product_code, product_name 
            FROM erp_products 
            WHERE user_id = ? AND product_code = ?
        """, (user_id, product_code))
    
    return cursor.fetchall()


def cleanup_test_data(conn, user_ids):
    """Clean up test data for given user IDs"""
    cursor = conn.cursor()
    db_type = get_db_type()
    
    try:
        for user_id in user_ids:
            if db_type == 'postgresql':
                cursor.execute("DELETE FROM erp_products WHERE user_id = %s", (user_id,))
                cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            else:
                cursor.execute("DELETE FROM erp_products WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Cleanup error: {e}")


# ==================== PROPERTY-BASED TESTS ====================

@composite
def product_uniqueness_test_data_strategy(draw):
    """Generate test data for product code uniqueness test"""
    # Generate 2 users
    user1_id = str(uuid.uuid4())
    user2_id = str(uuid.uuid4())
    
    # Generate a shared product code that both users will try to use
    shared_product_code = draw(product_code_strategy())
    
    # Generate 2-4 products for User 1 with unique codes
    num_products_user1 = draw(st.integers(min_value=2, max_value=4))
    user1_products = []
    user1_codes_used = set()
    for _ in range(num_products_user1):
        product = draw(product_data_strategy(user1_id))
        # Ensure unique product codes within user1
        while product['product_code'] in user1_codes_used or product['product_code'] == shared_product_code:
            product = draw(product_data_strategy(user1_id))
        user1_codes_used.add(product['product_code'])
        user1_products.append(product)
    
    # Generate 2-4 products for User 2 with unique codes
    num_products_user2 = draw(st.integers(min_value=2, max_value=4))
    user2_products = []
    user2_codes_used = set()
    for _ in range(num_products_user2):
        product = draw(product_data_strategy(user2_id))
        # Ensure unique product codes within user2
        while product['product_code'] in user2_codes_used or product['product_code'] == shared_product_code:
            product = draw(product_data_strategy(user2_id))
        user2_codes_used.add(product['product_code'])
        user2_products.append(product)
    
    # Add products with the shared code for both users
    user1_shared_product = draw(product_data_strategy(user1_id, shared_product_code))
    user2_shared_product = draw(product_data_strategy(user2_id, shared_product_code))
    
    # Generate a duplicate product for User 1 (same code as one of their existing products)
    duplicate_code = user1_products[0]['product_code']
    user1_duplicate_product = draw(product_data_strategy(user1_id, duplicate_code))
    
    return {
        'user1_id': user1_id,
        'user2_id': user2_id,
        'user1_products': user1_products,
        'user2_products': user2_products,
        'user1_shared_product': user1_shared_product,
        'user2_shared_product': user2_shared_product,
        'user1_duplicate_product': user1_duplicate_product,
        'shared_product_code': shared_product_code,
        'duplicate_code': duplicate_code
    }


@settings(
    max_examples=20,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow, HealthCheck.data_too_large, HealthCheck.large_base_example]
)
@given(test_data=product_uniqueness_test_data_strategy())
def test_product_code_uniqueness_per_user(test_data):
    """
    Property 16: Product Code Uniqueness Per User
    
    For any business owner account, all product codes should be unique within that account.
    
    This test validates that:
    1. Each user can have products with unique product codes
    2. Different users can have products with the same product code (multi-tenant isolation)
    3. Attempting to create a product with a duplicate code for the same user should fail
    4. The uniqueness constraint is enforced at the database level
    """
    conn = None
    user1_id = test_data['user1_id']
    user2_id = test_data['user2_id']
    
    try:
        # Setup: Create database connection
        conn = get_db_connection()
        
        # Create test users
        create_test_user(conn, user1_id)
        create_test_user(conn, user2_id)
        
        # Test 1: Create products with unique codes for User 1
        for product_data in test_data['user1_products']:
            success = insert_product(conn, product_data)
            assert success, f"Failed to insert product with unique code {product_data['product_code']} for User 1"
        
        # Test 2: Create products with unique codes for User 2
        for product_data in test_data['user2_products']:
            success = insert_product(conn, product_data)
            assert success, f"Failed to insert product with unique code {product_data['product_code']} for User 2"
        
        # Test 3: Both users can use the same product code (multi-tenant isolation)
        success1 = insert_product(conn, test_data['user1_shared_product'])
        assert success1, f"User 1 should be able to create product with code {test_data['shared_product_code']}"
        
        success2 = insert_product(conn, test_data['user2_shared_product'])
        assert success2, f"User 2 should be able to create product with code {test_data['shared_product_code']}"
        
        # Verify both users have the shared product code
        user1_shared_products = query_product_by_code(conn, user1_id, test_data['shared_product_code'])
        user2_shared_products = query_product_by_code(conn, user2_id, test_data['shared_product_code'])
        
        assert len(user1_shared_products) == 1, \
            f"User 1 should have exactly 1 product with code {test_data['shared_product_code']}"
        assert len(user2_shared_products) == 1, \
            f"User 2 should have exactly 1 product with code {test_data['shared_product_code']}"
        
        # Test 4: Attempting to create a duplicate product code for the same user should fail
        duplicate_success = insert_product(conn, test_data['user1_duplicate_product'])
        assert not duplicate_success, \
            f"User 1 should NOT be able to create duplicate product with code {test_data['duplicate_code']}"
        
        # Verify User 1 still has only one product with the duplicate code
        user1_duplicate_products = query_product_by_code(conn, user1_id, test_data['duplicate_code'])
        assert len(user1_duplicate_products) == 1, \
            f"User 1 should have exactly 1 product with code {test_data['duplicate_code']}, not {len(user1_duplicate_products)}"
        
        # Test 5: Verify all product codes are unique within each user
        user1_all_products = query_products_by_user(conn, user1_id)
        user2_all_products = query_products_by_user(conn, user2_id)
        
        # Extract product codes for User 1
        user1_codes = [
            (p['product_code'] if isinstance(p, dict) else p[2]) for p in user1_all_products
        ]
        
        # Extract product codes for User 2
        user2_codes = [
            (p['product_code'] if isinstance(p, dict) else p[2]) for p in user2_all_products
        ]
        
        # Verify uniqueness within each user
        assert len(user1_codes) == len(set(user1_codes)), \
            f"User 1 has duplicate product codes: {user1_codes}"
        assert len(user2_codes) == len(set(user2_codes)), \
            f"User 2 has duplicate product codes: {user2_codes}"
        
        # Test 6: Verify the shared code exists in both users' products
        assert test_data['shared_product_code'] in user1_codes, \
            f"User 1 should have product with code {test_data['shared_product_code']}"
        assert test_data['shared_product_code'] in user2_codes, \
            f"User 2 should have product with code {test_data['shared_product_code']}"
        
    finally:
        # Cleanup: Remove test data
        if conn:
            cleanup_test_data(conn, [user1_id, user2_id])
            conn.close()


@composite
def single_user_uniqueness_test_data_strategy(draw):
    """Generate test data for single user uniqueness test"""
    user_id = str(uuid.uuid4())
    
    # Generate 3-6 products with unique codes
    num_products = draw(st.integers(min_value=3, max_value=6))
    products = []
    codes_used = set()
    for _ in range(num_products):
        product = draw(product_data_strategy(user_id))
        # Ensure unique product codes
        while product['product_code'] in codes_used:
            product = draw(product_data_strategy(user_id))
        codes_used.add(product['product_code'])
        products.append(product)
    
    # Pick a random product code to duplicate
    duplicate_index = draw(st.integers(min_value=0, max_value=num_products - 1))
    duplicate_code = products[duplicate_index]['product_code']
    
    # Create a duplicate product
    duplicate_product = draw(product_data_strategy(user_id, duplicate_code))
    
    return {
        'user_id': user_id,
        'products': products,
        'duplicate_product': duplicate_product,
        'duplicate_code': duplicate_code
    }


@settings(
    max_examples=20,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow, HealthCheck.data_too_large, HealthCheck.large_base_example]
)
@given(test_data=single_user_uniqueness_test_data_strategy())
def test_product_code_uniqueness_single_user(test_data):
    """
    Property 16: Product Code Uniqueness Per User (Single User Test)
    
    For any business owner account, all product codes should be unique within that account.
    
    This test focuses on a single user and validates that:
    1. Multiple products with unique codes can be created
    2. Attempting to create a product with a duplicate code fails
    3. The database enforces uniqueness at the constraint level
    """
    conn = None
    user_id = test_data['user_id']
    
    try:
        # Setup: Create database connection
        conn = get_db_connection()
        
        # Create test user
        create_test_user(conn, user_id)
        
        # Test 1: Create all products with unique codes
        for product_data in test_data['products']:
            success = insert_product(conn, product_data)
            assert success, f"Failed to insert product with unique code {product_data['product_code']}"
        
        # Test 2: Verify all products were created
        all_products = query_products_by_user(conn, user_id)
        assert len(all_products) == len(test_data['products']), \
            f"Expected {len(test_data['products'])} products, but found {len(all_products)}"
        
        # Test 3: Attempt to create a duplicate product code
        duplicate_success = insert_product(conn, test_data['duplicate_product'])
        assert not duplicate_success, \
            f"Should NOT be able to create duplicate product with code {test_data['duplicate_code']}"
        
        # Test 4: Verify the product count hasn't changed
        all_products_after = query_products_by_user(conn, user_id)
        assert len(all_products_after) == len(test_data['products']), \
            f"Product count should remain {len(test_data['products'])} after duplicate attempt"
        
        # Test 5: Verify all product codes are still unique
        product_codes = [
            (p['product_code'] if isinstance(p, dict) else p[2]) for p in all_products_after
        ]
        assert len(product_codes) == len(set(product_codes)), \
            f"Duplicate product codes found: {product_codes}"
        
        # Test 6: Verify the duplicate code exists exactly once
        duplicate_products = query_product_by_code(conn, user_id, test_data['duplicate_code'])
        assert len(duplicate_products) == 1, \
            f"Should have exactly 1 product with code {test_data['duplicate_code']}, found {len(duplicate_products)}"
        
    finally:
        # Cleanup: Remove test data
        if conn:
            cleanup_test_data(conn, [user_id])
            conn.close()


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])
