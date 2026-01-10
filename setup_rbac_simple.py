"""
Simple RBAC Setup - Create tables and add sample clients
No bcrypt/cryptography needed
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_id():
    import uuid
    return str(uuid.uuid4())

def encrypt_data(data):
    """Simple base64 encoding"""
    import base64
    return base64.b64encode(data.encode('utf-8')).decode('utf-8')

def generate_tenant_id():
    return f"TNT-{secrets.token_hex(4).upper()}"

def setup_rbac():
    conn = sqlite3.connect('billing.db')
    cursor = conn.cursor()
    
    print("🔧 Setting up RBAC system...")
    print()
    
    # Create tenants table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tenants (
            id TEXT PRIMARY KEY,
            tenant_id TEXT UNIQUE NOT NULL,
            business_name TEXT NOT NULL,
            owner_name TEXT NOT NULL,
            mobile_encrypted TEXT NOT NULL,
            email_encrypted TEXT NOT NULL,
            gst_number TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            pincode TEXT,
            country TEXT DEFAULT 'India',
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            temp_password TEXT,
            plan_type TEXT DEFAULT 'trial',
            plan_start_date DATE,
            plan_expiry_date DATE,
            subscription_status TEXT DEFAULT 'active',
            status TEXT DEFAULT 'active',
            is_active BOOLEAN DEFAULT 1,
            suspended_reason TEXT,
            suspended_at TIMESTAMP,
            last_login TIMESTAMP,
            login_count INTEGER DEFAULT 0,
            failed_login_attempts INTEGER DEFAULT 0,
            account_locked_until TIMESTAMP,
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    print("✅ Tenants table created")
    
    # Check if clients already exist
    cursor.execute('SELECT COUNT(*) FROM tenants')
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"✅ Already have {count} clients")
        conn.close()
        return
    
    # Add 2 sample clients
    clients = [
        {
            'business_name': 'ABC Electronics Store',
            'owner_name': 'Rajesh Kumar',
            'mobile': '9876543210',
            'email': 'rajesh@abcelectronics.com',
            'gst_number': '29ABCDE1234F1Z5',
            'address': '123 MG Road',
            'city': 'Bangalore',
            'state': 'Karnataka',
            'pincode': '560001',
            'username': 'abc_electronics',
            'password': 'Demo@123'
        },
        {
            'business_name': 'XYZ Retail Shop',
            'owner_name': 'Priya Sharma',
            'mobile': '9876543211',
            'email': 'priya@xyzretail.com',
            'gst_number': '27XYZAB5678G1H9',
            'address': '456 Park Street',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'pincode': '400001',
            'username': 'xyz_retail',
            'password': 'Demo@123'
        }
    ]
    
    print()
    print("📝 Adding sample clients...")
    print()
    
    for client_data in clients:
        client_id = generate_id()
        tenant_id = generate_tenant_id()
        password_hash = hash_password(client_data['password'])
        mobile_encrypted = encrypt_data(client_data['mobile'])
        email_encrypted = encrypt_data(client_data['email'])
        
        plan_start = datetime.now().date()
        plan_expiry = plan_start + timedelta(days=30)
        
        cursor.execute('''
            INSERT INTO tenants (
                id, tenant_id, business_name, owner_name, mobile_encrypted, email_encrypted,
                gst_number, address, city, state, pincode, country,
                username, password_hash, temp_password,
                plan_type, plan_start_date, plan_expiry_date, subscription_status,
                status, is_active, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            client_id, tenant_id, client_data['business_name'], client_data['owner_name'],
            mobile_encrypted, email_encrypted, client_data['gst_number'],
            client_data['address'], client_data['city'], client_data['state'],
            client_data['pincode'], 'India',
            client_data['username'], password_hash, client_data['password'],
            'trial', plan_start, plan_expiry, 'active',
            'active', 1, 'admin-bizpulse'
        ))
        
        print(f"✅ Client Added: {client_data['business_name']}")
        print(f"   Tenant ID: {tenant_id}")
        print(f"   Username: {client_data['username']}")
        print(f"   Password: {client_data['password']}")
        print(f"   Plan Expires: {plan_expiry}")
        print()
    
    conn.commit()
    conn.close()
    
    print("=" * 70)
    print("✅ RBAC Setup Complete!")
    print("=" * 70)
    print()
    print("🌐 Access URL: http://localhost:5000/client-management")
    print()
    print("📋 Sample Clients Created:")
    print()
    print("1. ABC Electronics Store")
    print("   Username: abc_electronics")
    print("   Password: Demo@123")
    print()
    print("2. XYZ Retail Shop")
    print("   Username: xyz_retail")
    print("   Password: Demo@123")
    print()
    print("🔄 Now restart your server: python app.py")
    print("=" * 70)

if __name__ == '__main__':
    setup_rbac()
