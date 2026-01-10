#!/usr/bin/env python3
"""
Test Data Isolation
===================

This script tests that data isolation is working correctly between different client accounts.
"""

import sqlite3
import json

def test_data_isolation():
    """Test data isolation between different users"""
    
    print("🧪 TESTING DATA ISOLATION")
    print("=" * 50)
    
    # Test database level isolation
    conn = sqlite3.connect('billing.db')
    cursor = conn.cursor()
    
    print("\n1. Database Level Isolation Test")
    print("-" * 30)
    
    # Test demo-user-123 data
    cursor.execute('SELECT COUNT(*) FROM bills WHERE business_owner_id = ?', ('demo-user-123',))
    demo_bills = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM products WHERE user_id = ? AND is_active = 1', ('demo-user-123',))
    demo_products = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM customers WHERE user_id = ? AND is_active = 1', ('demo-user-123',))
    demo_customers = cursor.fetchone()[0]
    
    print(f"   demo-user-123: {demo_bills} bills, {demo_products} products, {demo_customers} customers")
    
    # Test rajesh data
    cursor.execute('SELECT COUNT(*) FROM bills WHERE business_owner_id = ?', ('rajesh-test-client-001',))
    rajesh_bills = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM products WHERE user_id = ? AND is_active = 1', ('rajesh-test-client-001',))
    rajesh_products = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM customers WHERE user_id = ? AND is_active = 1', ('rajesh-test-client-001',))
    rajesh_customers = cursor.fetchone()[0]
    
    print(f"   rajesh-test-client-001: {rajesh_bills} bills, {rajesh_products} products, {rajesh_customers} customers")
    
    # Test BIZPULSE admin data
    cursor.execute('SELECT COUNT(*) FROM bills WHERE business_owner_id = ?', ('BIZPULSE-ADMIN-001',))
    bizpulse_bills = cursor.fetchone()[0]
    
    print(f"   BIZPULSE-ADMIN-001: {bizpulse_bills} bills")
    
    # Verify no data mixing
    print("\n2. Data Mixing Verification")
    print("-" * 30)
    
    # Check for NULL user_ids (should be 0 after fix)
    cursor.execute('SELECT COUNT(*) FROM bills WHERE business_owner_id IS NULL')
    null_bills = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM products WHERE user_id IS NULL AND is_active = 1')
    null_products = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM customers WHERE user_id IS NULL AND is_active = 1')
    null_customers = cursor.fetchone()[0]
    
    print(f"   NULL user_id data: {null_bills} bills, {null_products} products, {null_customers} customers")
    
    if null_bills == 0 and null_products == 0 and null_customers == 0:
        print("   ✅ No NULL user_id data found - isolation is working!")
    else:
        print("   ❌ Found NULL user_id data - isolation needs fixing!")
    
    # Test unique data per user
    print("\n3. Unique Data Per User Test")
    print("-" * 30)
    
    # Get sample product names for each user
    cursor.execute('SELECT name FROM products WHERE user_id = ? AND is_active = 1 LIMIT 3', ('demo-user-123',))
    demo_product_names = [row[0] for row in cursor.fetchall()]
    
    cursor.execute('SELECT name FROM products WHERE user_id = ? AND is_active = 1 LIMIT 3', ('rajesh-test-client-001',))
    rajesh_product_names = [row[0] for row in cursor.fetchall()]
    
    print(f"   demo-user-123 products: {demo_product_names}")
    print(f"   rajesh products: {rajesh_product_names}")
    
    # Check for overlap (should be none)
    overlap = set(demo_product_names) & set(rajesh_product_names)
    if not overlap:
        print("   ✅ No product name overlap - users have separate data!")
    else:
        print(f"   ⚠️ Product name overlap found: {overlap}")
    
    conn.close()
    
    print("\n4. API Level Isolation Test")
    print("-" * 30)
    print("   ℹ️ API testing requires running server - skipping for now")
    print("   ℹ️ Manual test: Login as different users and verify separate data")
    
    print("\n✅ DATA ISOLATION TEST COMPLETED!")
    print("=" * 50)
    print()
    print("📋 TEST RESULTS:")
    print(f"   • demo-user-123: {demo_bills} bills, {demo_products} products, {demo_customers} customers")
    print(f"   • rajesh-test-client-001: {rajesh_bills} bills, {rajesh_products} products, {rajesh_customers} customers")
    print(f"   • BIZPULSE-ADMIN-001: {bizpulse_bills} bills")
    print(f"   • NULL data: {null_bills} bills, {null_products} products, {null_customers} customers")
    print()
    print("🔐 MANUAL TESTING:")
    print("   1. Login as 'rajesh' (password: admin123)")
    print("   2. Check that only Rajesh's data is visible")
    print("   3. Login as different user and verify separate data")
    print("   4. Ensure no BizPulse data appears in client accounts")

if __name__ == '__main__':
    test_data_isolation()