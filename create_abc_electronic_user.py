#!/usr/bin/env python3
"""
Create ABC Electronic User
===========================

This script creates the abc_electronic user account that can login with any username/password format.
"""

import sqlite3
from datetime import datetime
from modules.shared.database import hash_password

def create_abc_electronic_user():
    """Create abc_electronic user account"""
    
    print("🔧 CREATING ABC ELECTRONIC USER")
    print("=" * 40)
    
    conn = sqlite3.connect('billing.db')
    cursor = conn.cursor()
    
    # Check if abc_electronic already exists in clients table
    cursor.execute('SELECT * FROM clients WHERE username = ?', ('abc_electronic',))
    existing_client = cursor.fetchone()
    
    if existing_client:
        print("   ℹ️ abc_electronic client already exists")
        print(f"   Username: {existing_client[9]}")
        print(f"   Company: {existing_client[1]}")
    else:
        print("   Creating abc_electronic client...")
        
        # Create abc_electronic client
        client_id = 'abc-electronic-001'
        cursor.execute('''
            INSERT INTO clients (
                id, company_name, contact_email, contact_name, phone_number,
                username, password_hash, is_active, created_at, updated_at,
                country, language, timezone, currency, date_format
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            client_id,
            'ABC Electronics Store',
            'abc@electronics.com',
            'ABC Electronics',
            '9876543210',
            'abc_electronic',
            hash_password('admin123'),  # Default password
            1,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'India',
            'en',
            'Asia/Kolkata',
            'INR',
            'DD/MM/YYYY'
        ))
        
        print(f"   ✅ Created abc_electronic client with ID: {client_id}")
        
        # Create some test data for abc_electronic
        print("   📦 Creating test products for abc_electronic...")
        
        test_products = [
            ('abc-product-001', 'ABC TV 32 inch', 'TV001', 25000.0, 10, 2, 'Electronics', 'piece'),
            ('abc-product-002', 'ABC Mobile Phone', 'MOB001', 15000.0, 20, 5, 'Electronics', 'piece'),
            ('abc-product-003', 'ABC Laptop', 'LAP001', 45000.0, 5, 1, 'Electronics', 'piece')
        ]
        
        for product in test_products:
            cursor.execute('''
                INSERT INTO products (
                    id, name, code, price, stock, min_stock, category, unit,
                    user_id, is_active, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (*product, client_id, 1, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        print(f"   ✅ Created {len(test_products)} test products")
        
        # Create test customers
        print("   👥 Creating test customers for abc_electronic...")
        
        test_customers = [
            ('abc-customer-001', 'ABC Customer A', '9111111111', 'customer.a@abc.com'),
            ('abc-customer-002', 'ABC Customer B', '9222222222', 'customer.b@abc.com')
        ]
        
        for customer in test_customers:
            cursor.execute('''
                INSERT INTO customers (
                    id, name, phone, email, user_id, is_active, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (*customer, client_id, 1, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        print(f"   ✅ Created {len(test_customers)} test customers")
    
    # Also create alternative login methods
    print("\n   🔐 Creating alternative login methods...")
    
    # Check if user exists in users table
    cursor.execute('SELECT * FROM users WHERE email = ?', ('abc_electronic@store.com',))
    existing_user = cursor.fetchone()
    
    if not existing_user:
        cursor.execute('''
            INSERT INTO users (
                id, first_name, last_name, email, business_name, business_type,
                password_hash, is_active, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'abc-electronic-user-001',
            'ABC',
            'Electronics',
            'abc_electronic@store.com',
            'ABC Electronics Store',
            'retail',
            hash_password('admin123'),
            1,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        print("   ✅ Created abc_electronic user in users table")
    
    # Commit changes
    conn.commit()
    
    # Verify creation
    print("\n   🧪 Verification:")
    
    cursor.execute('SELECT username, contact_name, company_name FROM clients WHERE username = ?', ('abc_electronic',))
    client = cursor.fetchone()
    if client:
        print(f"   ✅ Client: {client[0]} - {client[1]} ({client[2]})")
    
    cursor.execute('SELECT email, first_name, business_name FROM users WHERE email = ?', ('abc_electronic@store.com',))
    user = cursor.fetchone()
    if user:
        print(f"   ✅ User: {user[0]} - {user[1]} ({user[2]})")
    
    conn.close()
    
    print("\n✅ ABC ELECTRONIC USER CREATED!")
    print("=" * 40)
    print()
    print("🔐 LOGIN CREDENTIALS:")
    print("   Username: abc_electronic")
    print("   Password: admin123")
    print("   Alternative: abc_electronic@store.com / admin123")
    print()
    print("📱 MOBILE URL:")
    print("   http://10.150.250.59:5000")
    print()
    print("✅ User can now login with username 'abc_electronic' and password 'admin123'")
    print("✅ No @ symbol required - username login works!")

if __name__ == '__main__':
    create_abc_electronic_user()