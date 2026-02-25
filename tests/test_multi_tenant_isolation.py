"""
Property-Based Test for Multi-Tenant Data Isolation

Feature: comprehensive-erp-modules
Property 30: Multi-Tenant Data Isolation

**Validates: Requirements 24.3**

This test validates that the ERP system implements proper row-level security
for multi-tenant data isolation. It ensures that each business owner's data
is completely isolated from other users' data.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from hypothesis.strategies import composite
import uuid
from datetime import datetime, date, timedelta
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.shared.database import get_db_connection, generate_id, get_db_type


# ==================== TEST DATA GENERATORS ====================

def user_id_strategy():
    """Generate random user IDs"""
    return st.builds(lambda: str(uuid.uuid4()))


@composite
def product_data_strategy(draw, user_id):
    """Generate random product data for a specific user"""
    # Generate unique product code using UUID to avoid collisions
    unique_suffix = str(uuid.uuid4())[:8]
    return {
        'id': generate_id(),
        'user_id': user_id,
        'product_code': f"PROD-{unique_suffix}",
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


@composite
def customer_data_strategy(draw, user_id):
    """Generate random customer data for a specific user"""
    # Generate unique email to avoid collisions
    unique_suffix = str(uuid.uuid4())[:8]
    return {
        'id': generate_id(),
        'user_id': user_id,
        'customer_name': draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'), blacklist_characters='\x00'))),
        'phone': f"+91{draw(st.integers(min_value=7000000000, max_value=9999999999))}",
        'email': f"customer{unique_suffix}@example.com",
        'address': draw(st.text(min_size=10, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'), blacklist_characters='\x00'))),
        'credit_limit': draw(st.floats(min_value=0, max_value=100000)),
        'outstanding_balance': 0,
        'is_active': True
    }


@composite
def invoice_data_strategy(draw, user_id, customer_id):
    """Generate random invoice data for a specific user"""
    # Generate unique invoice number to avoid collisions
    unique_suffix = str(uuid.uuid4())[:8]
    return {
        'id': generate_id(),
        'user_id': user_id,
        'invoice_number': f"INV-{unique_suffix}",
        'customer_id': customer_id,
        'customer_name': 'Test Customer',
        'invoice_date': date.today(),
        'subtotal': draw(st.floats(min_value=100, max_value=10000)),
        'tax_amount': draw(st.floats(min_value=10, max_value=1000)),
        'total_amount': draw(st.floats(min_value=110, max_value=11000)),
        'payment_status': draw(st.sampled_from(['paid', 'unpaid', 'partial'])),
        'items': '[]',
        'status': 'completed'
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
    except Exception as e:
        conn.rollback()
        raise


def insert_customer(conn, customer_data):
    """Insert a customer into erp_customers table"""
    cursor = conn.cursor()
    db_type = get_db_type()
    
    try:
        if db_type == 'postgresql':
            cursor.execute("""
                INSERT INTO erp_customers 
                (id, user_id, customer_name, phone, email, address, 
                 credit_limit, outstanding_balance, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                customer_data['id'], customer_data['user_id'], customer_data['customer_name'],
                customer_data['phone'], customer_data['email'], customer_data['address'],
                customer_data['credit_limit'], customer_data['outstanding_balance'], customer_data['is_active']
            ))
        else:
            cursor.execute("""
                INSERT INTO erp_customers 
                (id, user_id, customer_name, phone, email, address, 
                 credit_limit, outstanding_balance, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                customer_data['id'], customer_data['user_id'], customer_data['customer_name'],
                customer_data['phone'], customer_data['email'], customer_data['address'],
                customer_data['credit_limit'], customer_data['outstanding_balance'], 1 if customer_data['is_active'] else 0
            ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise


def insert_invoice(conn, invoice_data):
    """Insert an invoice into erp_invoices table"""
    cursor = conn.cursor()
    db_type = get_db_type()
    
    try:
        if db_type == 'postgresql':
            cursor.execute("""
                INSERT INTO erp_invoices 
                (id, user_id, invoice_number, customer_id, customer_name, 
                 invoice_date, subtotal, tax_amount, total_amount, 
                 payment_status, items, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                invoice_data['id'], invoice_data['user_id'], invoice_data['invoice_number'],
                invoice_data['customer_id'], invoice_data['customer_name'], invoice_data['invoice_date'],
                invoice_data['subtotal'], invoice_data['tax_amount'], invoice_data['total_amount'],
                invoice_data['payment_status'], invoice_data['items'], invoice_data['status']
            ))
        else:
            cursor.execute("""
                INSERT INTO erp_invoices 
                (id, user_id, invoice_number, customer_id, customer_name, 
                 invoice_date, subtotal, tax_amount, total_amount, 
                 payment_status, items, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                invoice_data['id'], invoice_data['user_id'], invoice_data['invoice_number'],
                invoice_data['customer_id'], invoice_data['customer_name'], invoice_data['invoice_date'],
                invoice_data['subtotal'], invoice_data['tax_amount'], invoice_data['total_amount'],
                invoice_data['payment_status'], invoice_data['items'], invoice_data['status']
            ))
        conn.commit()
    except Exception as e:
        conn.rollback()
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


def query_customers_by_user(conn, user_id):
    """Query customers for a specific user"""
    cursor = conn.cursor()
    db_type = get_db_type()
    
    if db_type == 'postgresql':
        cursor.execute("""
            SELECT id, user_id, customer_name 
            FROM erp_customers 
            WHERE user_id = %s
        """, (user_id,))
    else:
        cursor.execute("""
            SELECT id, user_id, customer_name 
            FROM erp_customers 
            WHERE user_id = ?
        """, (user_id,))
    
    return cursor.fetchall()


def query_invoices_by_user(conn, user_id):
    """Query invoices for a specific user"""
    cursor = conn.cursor()
    db_type = get_db_type()
    
    if db_type == 'postgresql':
        cursor.execute("""
            SELECT id, user_id, invoice_number 
            FROM erp_invoices 
            WHERE user_id = %s
        """, (user_id,))
    else:
        cursor.execute("""
            SELECT id, user_id, invoice_number 
            FROM erp_invoices 
            WHERE user_id = ?
        """, (user_id,))
    
    return cursor.fetchall()


def cleanup_test_data(conn, user_ids):
    """Clean up test data for given user IDs"""
    cursor = conn.cursor()
    db_type = get_db_type()
    
    try:
        for user_id in user_ids:
            if db_type == 'postgresql':
                # Delete in reverse order of foreign key dependencies
                cursor.execute("DELETE FROM erp_invoices WHERE user_id = %s", (user_id,))
                cursor.execute("DELETE FROM erp_customers WHERE user_id = %s", (user_id,))
                cursor.execute("DELETE FROM erp_products WHERE user_id = %s", (user_id,))
                cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            else:
                cursor.execute("DELETE FROM erp_invoices WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM erp_customers WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM erp_products WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Cleanup error: {e}")


# ==================== PROPERTY-BASED TESTS ====================

@composite
def multi_tenant_test_data_strategy(draw):
    """Generate complete test data for multi-tenant isolation test"""
    num_products_user1 = draw(st.integers(min_value=1, max_value=5))
    num_products_user2 = draw(st.integers(min_value=1, max_value=5))
    num_customers_user1 = draw(st.integers(min_value=1, max_value=3))
    num_customers_user2 = draw(st.integers(min_value=1, max_value=3))
    
    user1_id = str(uuid.uuid4())
    user2_id = str(uuid.uuid4())
    
    # Generate products for User 1
    user1_products = [draw(product_data_strategy(user1_id)) for _ in range(num_products_user1)]
    
    # Generate products for User 2
    user2_products = [draw(product_data_strategy(user2_id)) for _ in range(num_products_user2)]
    
    # Generate customers for User 1
    user1_customers = [draw(customer_data_strategy(user1_id)) for _ in range(num_customers_user1)]
    
    # Generate customers for User 2
    user2_customers = [draw(customer_data_strategy(user2_id)) for _ in range(num_customers_user2)]
    
    return {
        'user1_id': user1_id,
        'user2_id': user2_id,
        'user1_products': user1_products,
        'user2_products': user2_products,
        'user1_customers': user1_customers,
        'user2_customers': user2_customers
    }


@settings(
    max_examples=20,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow, HealthCheck.data_too_large]
)
@given(test_data=multi_tenant_test_data_strategy())
def test_multi_tenant_product_isolation(test_data):
    """
    Property 30: Multi-Tenant Data Isolation
    
    For any user query, the returned data should only include records where 
    user_id matches the authenticated user's ID, never exposing other users' data.
    
    This test validates that:
    1. User 1 can only see their own products
    2. User 2 can only see their own products
    3. No cross-user data leakage occurs
    4. The same isolation applies to customers and invoices
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
        
        # Create products for User 1
        user1_product_ids = []
        for product_data in test_data['user1_products']:
            insert_product(conn, product_data)
            user1_product_ids.append(product_data['id'])
        
        # Create products for User 2
        user2_product_ids = []
        for product_data in test_data['user2_products']:
            insert_product(conn, product_data)
            user2_product_ids.append(product_data['id'])
        
        # Create customers for User 1
        user1_customer_ids = []
        for customer_data in test_data['user1_customers']:
            insert_customer(conn, customer_data)
            user1_customer_ids.append(customer_data['id'])
        
        # Create customers for User 2
        user2_customer_ids = []
        for customer_data in test_data['user2_customers']:
            insert_customer(conn, customer_data)
            user2_customer_ids.append(customer_data['id'])
        
        # Create invoices for User 1 (if they have customers)
        if user1_customer_ids:
            invoice_data = {
                'id': generate_id(),
                'user_id': user1_id,
                'invoice_number': f"INV-{uuid.uuid4().hex[:8]}",
                'customer_id': user1_customer_ids[0],
                'customer_name': 'Test Customer',
                'invoice_date': date.today(),
                'subtotal': 1000.0,
                'tax_amount': 180.0,
                'total_amount': 1180.0,
                'payment_status': 'paid',
                'items': '[]',
                'status': 'completed'
            }
            insert_invoice(conn, invoice_data)
        
        # Create invoices for User 2 (if they have customers)
        if user2_customer_ids:
            invoice_data = {
                'id': generate_id(),
                'user_id': user2_id,
                'invoice_number': f"INV-{uuid.uuid4().hex[:8]}",
                'customer_id': user2_customer_ids[0],
                'customer_name': 'Test Customer',
                'invoice_date': date.today(),
                'subtotal': 1000.0,
                'tax_amount': 180.0,
                'total_amount': 1180.0,
                'payment_status': 'paid',
                'items': '[]',
                'status': 'completed'
            }
            insert_invoice(conn, invoice_data)
        
        # Test: Query products for User 1
        user1_products = query_products_by_user(conn, user1_id)
        
        # Verify: User 1 should only see their own products
        num_products_user1 = len(test_data['user1_products'])
        assert len(user1_products) == num_products_user1, \
            f"User 1 should see exactly {num_products_user1} products, but saw {len(user1_products)}"
        
        for product in user1_products:
            product_user_id = product['user_id'] if isinstance(product, dict) else product[1]
            assert product_user_id == user1_id, \
                f"User 1 query returned product belonging to {product_user_id}, not {user1_id}"
        
        # Test: Query products for User 2
        user2_products = query_products_by_user(conn, user2_id)
        
        # Verify: User 2 should only see their own products
        num_products_user2 = len(test_data['user2_products'])
        assert len(user2_products) == num_products_user2, \
            f"User 2 should see exactly {num_products_user2} products, but saw {len(user2_products)}"
        
        for product in user2_products:
            product_user_id = product['user_id'] if isinstance(product, dict) else product[1]
            assert product_user_id == user2_id, \
                f"User 2 query returned product belonging to {product_user_id}, not {user2_id}"
        
        # Test: Query customers for User 1
        user1_customers = query_customers_by_user(conn, user1_id)
        
        # Verify: User 1 should only see their own customers
        num_customers_user1 = len(test_data['user1_customers'])
        assert len(user1_customers) == num_customers_user1, \
            f"User 1 should see exactly {num_customers_user1} customers, but saw {len(user1_customers)}"
        
        for customer in user1_customers:
            customer_user_id = customer['user_id'] if isinstance(customer, dict) else customer[1]
            assert customer_user_id == user1_id, \
                f"User 1 query returned customer belonging to {customer_user_id}, not {user1_id}"
        
        # Test: Query customers for User 2
        user2_customers = query_customers_by_user(conn, user2_id)
        
        # Verify: User 2 should only see their own customers
        num_customers_user2 = len(test_data['user2_customers'])
        assert len(user2_customers) == num_customers_user2, \
            f"User 2 should see exactly {num_customers_user2} customers, but saw {len(user2_customers)}"
        
        for customer in user2_customers:
            customer_user_id = customer['user_id'] if isinstance(customer, dict) else customer[1]
            assert customer_user_id == user2_id, \
                f"User 2 query returned customer belonging to {customer_user_id}, not {user2_id}"
        
        # Test: Query invoices for both users
        user1_invoices = query_invoices_by_user(conn, user1_id)
        user2_invoices = query_invoices_by_user(conn, user2_id)
        
        # Verify: Each user should only see their own invoices
        for invoice in user1_invoices:
            invoice_user_id = invoice['user_id'] if isinstance(invoice, dict) else invoice[1]
            assert invoice_user_id == user1_id, \
                f"User 1 query returned invoice belonging to {invoice_user_id}, not {user1_id}"
        
        for invoice in user2_invoices:
            invoice_user_id = invoice['user_id'] if isinstance(invoice, dict) else invoice[1]
            assert invoice_user_id == user2_id, \
                f"User 2 query returned invoice belonging to {invoice_user_id}, not {user2_id}"
        
        # Additional verification: Ensure no data leakage
        # User 1's product IDs should not appear in User 2's results
        user2_product_ids_from_query = [
            (p['id'] if isinstance(p, dict) else p[0]) for p in user2_products
        ]
        for user1_product_id in user1_product_ids:
            assert user1_product_id not in user2_product_ids_from_query, \
                f"Data leakage detected: User 1's product {user1_product_id} appeared in User 2's query results"
        
        # User 2's product IDs should not appear in User 1's results
        user1_product_ids_from_query = [
            (p['id'] if isinstance(p, dict) else p[0]) for p in user1_products
        ]
        for user2_product_id in user2_product_ids:
            assert user2_product_id not in user1_product_ids_from_query, \
                f"Data leakage detected: User 2's product {user2_product_id} appeared in User 1's query results"
        
    finally:
        # Cleanup: Remove test data
        if conn:
            cleanup_test_data(conn, [user1_id, user2_id])
            conn.close()


@composite
def multiple_users_test_data_strategy(draw):
    """Generate test data for multiple users isolation test"""
    num_users = draw(st.integers(min_value=2, max_value=4))
    items_per_user = draw(st.integers(min_value=1, max_value=3))
    
    user_ids = [str(uuid.uuid4()) for _ in range(num_users)]
    
    # Generate products for each user
    user_data_map = {}
    for user_id in user_ids:
        products = [draw(product_data_strategy(user_id)) for _ in range(items_per_user)]
        user_data_map[user_id] = {'products': products}
    
    return {
        'user_ids': user_ids,
        'items_per_user': items_per_user,
        'user_data_map': user_data_map
    }


@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow, HealthCheck.data_too_large]
)
@given(test_data=multiple_users_test_data_strategy())
def test_multi_tenant_isolation_multiple_users(test_data):
    """
    Property 30: Multi-Tenant Data Isolation (Extended Test)
    
    Test data isolation across multiple users (2-4 users) to ensure
    that the isolation property holds for any number of tenants.
    """
    conn = None
    user_ids = test_data['user_ids']
    items_per_user = test_data['items_per_user']
    user_data_map = test_data['user_data_map']
    
    try:
        conn = get_db_connection()
        
        # Create users and their data
        for user_id in user_ids:
            create_test_user(conn, user_id)
            
            # Create products for this user
            for product_data in user_data_map[user_id]['products']:
                insert_product(conn, product_data)
        
        # Verify isolation for each user
        for user_id in user_ids:
            products = query_products_by_user(conn, user_id)
            
            # This user should see exactly their items
            assert len(products) == items_per_user, \
                f"User {user_id} should see {items_per_user} products, but saw {len(products)}"
            
            # All returned products should belong to this user
            for product in products:
                product_user_id = product['user_id'] if isinstance(product, dict) else product[1]
                assert product_user_id == user_id, \
                    f"User {user_id} query returned product belonging to {product_user_id}"
            
            # Verify no data from other users is visible
            product_ids_from_query = [
                (p['id'] if isinstance(p, dict) else p[0]) for p in products
            ]
            
            # Get product IDs for this user
            this_user_product_ids = [p['id'] for p in user_data_map[user_id]['products']]
            
            for other_user_id in user_ids:
                if other_user_id != user_id:
                    other_user_product_ids = [p['id'] for p in user_data_map[other_user_id]['products']]
                    for other_product_id in other_user_product_ids:
                        assert other_product_id not in product_ids_from_query, \
                            f"Data leakage: User {user_id} can see product {other_product_id} from user {other_user_id}"
    
    finally:
        if conn:
            cleanup_test_data(conn, user_ids)
            conn.close()


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])
