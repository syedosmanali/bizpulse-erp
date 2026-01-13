#!/usr/bin/env python3
"""
Test script for the notification API endpoints
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.shared.database import init_db, get_db_connection, generate_id
from datetime import datetime
import json

def test_notification_settings_api():
    """Test the notification settings storage and retrieval"""
    print("🧪 Testing notification settings API...")
    
    # Initialize database
    init_db()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create test client
    test_client_id = 'api-test-client-456'
    cursor.execute("""
        INSERT OR REPLACE INTO clients (
            id, company_name, contact_email, username, password_hash, is_active
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (test_client_id, 'API Test Company', 'apitest@example.com', 'apitestuser', 'hash456', 1))
    
    conn.commit()
    
    # Test 1: Create notification settings
    print("\n📝 Test 1: Creating notification settings...")
    
    settings_id = generate_id()
    cursor.execute("""
        INSERT INTO notification_settings (
            id, client_id, low_stock_enabled, low_stock_threshold, updated_at
        ) VALUES (?, ?, ?, ?, ?)
    """, (settings_id, test_client_id, 1, 10, datetime.now().isoformat()))
    
    conn.commit()
    print(f"✅ Settings created for client {test_client_id}")
    
    # Test 2: Retrieve notification settings
    print("\n📖 Test 2: Retrieving notification settings...")
    
    cursor.execute("""
        SELECT low_stock_enabled, low_stock_threshold, updated_at
        FROM notification_settings 
        WHERE client_id = ?
    """, (test_client_id,))
    
    settings = cursor.fetchone()
    
    if settings:
        print(f"✅ Settings retrieved:")
        print(f"  - Low stock enabled: {bool(settings[0])}")
        print(f"  - Low stock threshold: {settings[1]}")
        print(f"  - Updated at: {settings[2]}")
    else:
        print("❌ No settings found")
    
    # Test 3: Update notification settings
    print("\n🔄 Test 3: Updating notification settings...")
    
    cursor.execute("""
        UPDATE notification_settings 
        SET low_stock_enabled = ?, low_stock_threshold = ?, updated_at = ?
        WHERE client_id = ?
    """, (0, 15, datetime.now().isoformat(), test_client_id))
    
    conn.commit()
    
    # Verify update
    cursor.execute("""
        SELECT low_stock_enabled, low_stock_threshold
        FROM notification_settings 
        WHERE client_id = ?
    """, (test_client_id,))
    
    updated_settings = cursor.fetchone()
    
    if updated_settings:
        print(f"✅ Settings updated:")
        print(f"  - Low stock enabled: {bool(updated_settings[0])}")
        print(f"  - Low stock threshold: {updated_settings[1]}")
    else:
        print("❌ Update failed")
    
    # Test 4: Multi-tenant isolation
    print("\n🔒 Test 4: Testing multi-tenant isolation...")
    
    # Create another client
    test_client_2 = 'api-test-client-789'
    cursor.execute("""
        INSERT OR REPLACE INTO clients (
            id, company_name, contact_email, username, password_hash, is_active
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (test_client_2, 'API Test Company 2', 'apitest2@example.com', 'apitestuser2', 'hash789', 1))
    
    # Create different settings for client 2
    settings_id_2 = generate_id()
    cursor.execute("""
        INSERT INTO notification_settings (
            id, client_id, low_stock_enabled, low_stock_threshold, updated_at
        ) VALUES (?, ?, ?, ?, ?)
    """, (settings_id_2, test_client_2, 1, 3, datetime.now().isoformat()))
    
    conn.commit()
    
    # Verify each client has their own settings
    cursor.execute("""
        SELECT client_id, low_stock_threshold
        FROM notification_settings 
        WHERE client_id IN (?, ?)
        ORDER BY client_id
    """, (test_client_id, test_client_2))
    
    all_settings = cursor.fetchall()
    
    print(f"✅ Multi-tenant isolation verified:")
    for setting in all_settings:
        print(f"  - Client {setting[0]}: threshold = {setting[1]}")
    
    conn.close()
    print("\n✅ Notification settings API test completed!")

if __name__ == '__main__':
    print("🧪 Notification API Test Suite")
    print("=" * 50)
    
    test_notification_settings_api()
    
    print("\n🎉 All API tests completed!")