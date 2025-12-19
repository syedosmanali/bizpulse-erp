#!/usr/bin/env python3
"""
Debug profile API to see what's happening with save/load
"""
import sqlite3
import json

def debug_profile_data():
    """Debug profile data in database"""
    print("🔍 Debugging Profile API Data")
    print("=" * 50)
    
    try:
        # Connect to database
        conn = sqlite3.connect('billing.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if clients table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clients'")
        if not cursor.fetchone():
            print("❌ Clients table does not exist!")
            return
        
        print("✅ Clients table exists")
        
        # Get all clients
        cursor.execute("SELECT * FROM clients")
        clients = cursor.fetchall()
        
        print(f"\n📊 Found {len(clients)} clients in database:")
        print("-" * 50)
        
        for i, client in enumerate(clients, 1):
            print(f"\n{i}. Client ID: {client['id']}")
            print(f"   Company Name: {client['company_name'] or 'Not set'}")
            print(f"   Contact Name: {client['contact_name'] or 'Not set'}")
            print(f"   Email: {client['contact_email'] or 'Not set'}")
            print(f"   Phone: {client['phone_number'] or 'Not set'}")
            print(f"   WhatsApp: {client['whatsapp_number'] or 'Not set'}")
            print(f"   Address: {client['business_address'] or 'Not set'}")
            print(f"   Business Type: {client['business_type'] or 'Not set'}")
            print(f"   GST Number: {client['gst_number'] or 'Not set'}")
            print(f"   Created: {client['created_at']}")
            print(f"   Updated: {client['updated_at']}")
        
        # Check table structure
        print(f"\n🏗️  Clients table structure:")
        cursor.execute("PRAGMA table_info(clients)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"   {col[1]} ({col[2]})")
        
        conn.close()
        
        print(f"\n" + "=" * 50)
        print("🎯 DEBUGGING COMPLETE")
        print("=" * 50)
        
        if len(clients) == 0:
            print("⚠️  No clients found in database!")
            print("   This might be why profile data is not loading.")
            print("   Try logging in first to create a client record.")
        else:
            print("✅ Client data exists in database")
            print("   If profile is still not loading, check:")
            print("   1. Session authentication")
            print("   2. Client ID matching")
            print("   3. Frontend API calls")
        
    except Exception as e:
        print(f"❌ Error debugging profile data: {e}")

def test_profile_api_simulation():
    """Simulate profile API calls"""
    print(f"\n🧪 Simulating Profile API Calls")
    print("-" * 30)
    
    try:
        conn = sqlite3.connect('billing.db')
        conn.row_factory = sqlite3.Row
        
        # Get first client for testing
        client = conn.execute("SELECT * FROM clients LIMIT 1").fetchone()
        
        if not client:
            print("❌ No client found for testing")
            return
        
        client_id = client['id']
        print(f"📋 Testing with Client ID: {client_id}")
        
        # Simulate GET profile
        print(f"\n1. 🔍 GET /api/client/profile")
        profile_data = {
            'id': client['id'],
            'company_name': client['company_name'],
            'contact_email': client['contact_email'],
            'contact_name': client['contact_name'],
            'phone_number': client['phone_number'],
            'whatsapp_number': client['whatsapp_number'],
            'business_address': client['business_address'],
            'business_type': client['business_type'],
            'gst_number': client['gst_number']
        }
        print(f"   Response: {json.dumps(profile_data, indent=2)}")
        
        # Simulate PUT profile (update)
        print(f"\n2. 📝 PUT /api/client/profile")
        test_update_data = {
            'storeName': 'Updated Store Name',
            'fullName': 'Updated Full Name',
            'email': client['contact_email'],
            'phone': '9999999999',
            'whatsapp': '9999999999',
            'storeAddress': 'Updated Address',
            'storeType': 'retail',
            'gstNumber': 'GST123456789'
        }
        print(f"   Update Data: {json.dumps(test_update_data, indent=2)}")
        
        # Actually perform the update to test
        conn.execute('''
            UPDATE clients 
            SET company_name = ?, contact_name = ?, phone_number = ?, 
                whatsapp_number = ?, business_address = ?, business_type = ?, 
                gst_number = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            test_update_data.get('storeName', ''),
            test_update_data.get('fullName', ''),
            test_update_data.get('phone', ''),
            test_update_data.get('whatsapp', ''),
            test_update_data.get('storeAddress', ''),
            test_update_data.get('storeType', ''),
            test_update_data.get('gstNumber', ''),
            client_id
        ))
        
        conn.commit()
        print(f"   ✅ Update executed successfully")
        
        # Verify the update
        print(f"\n3. 🔍 Verify Update - GET /api/client/profile")
        updated_client = conn.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
        
        if updated_client:
            print(f"   ✅ Data after update:")
            print(f"      Company Name: {updated_client['company_name']}")
            print(f"      Contact Name: {updated_client['contact_name']}")
            print(f"      Phone: {updated_client['phone_number']}")
            print(f"      Address: {updated_client['business_address']}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error in API simulation: {e}")

if __name__ == "__main__":
    debug_profile_data()
    test_profile_api_simulation()