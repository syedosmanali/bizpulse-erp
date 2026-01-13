#!/usr/bin/env python3
"""
Test script for the stock monitoring background service
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.shared.database import init_db, get_db_connection, generate_id
from modules.notifications.stock_monitor import StockMonitorService
from datetime import datetime
import time

def setup_test_data():
    """Create test client, products, and notification settings"""
    print("🧪 Setting up test data...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create test client
    test_client_id = 'test-client-123'
    cursor.execute("""
        INSERT OR REPLACE INTO clients (
            id, company_name, contact_email, username, password_hash, is_active
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (test_client_id, 'Test Company', 'test@example.com', 'testuser', 'hash123', 1))
    
    # Create notification settings for test client
    settings_id = generate_id()
    cursor.execute("""
        INSERT OR REPLACE INTO notification_settings (
            id, client_id, low_stock_enabled, low_stock_threshold, updated_at
        ) VALUES (?, ?, ?, ?, ?)
    """, (settings_id, test_client_id, 1, 5, datetime.now().isoformat()))
    
    # Create test products with low stock
    products = [
        ('test-prod-1', 'Test Product 1', 'Electronics', 2, 5),  # Below threshold
        ('test-prod-2', 'Test Product 2', 'Groceries', 0, 5),   # Out of stock
        ('test-prod-3', 'Test Product 3', 'Clothing', 10, 5),   # Above threshold
        ('test-prod-4', 'Test Product 4', 'Books', 3, 5),       # Below threshold
    ]
    
    for prod_id, name, category, stock, min_stock in products:
        cursor.execute("""
            INSERT OR REPLACE INTO products (
                id, code, name, category, price, cost, stock, min_stock, 
                unit, business_type, is_active, user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (prod_id, f'CODE-{prod_id}', name, category, 100.0, 80.0, 
              stock, min_stock, 'piece', 'retail', 1, test_client_id))
    
    conn.commit()
    conn.close()
    
    print("✅ Test data created:")
    print(f"  - Client: {test_client_id}")
    print(f"  - Notification settings: enabled, threshold=5")
    print(f"  - Products: 4 total (2 below threshold, 1 out of stock, 1 above threshold)")

def test_stock_monitor():
    """Test the stock monitoring service"""
    print("\n🧪 Testing stock monitor service...")
    
    # Initialize database
    init_db()
    
    # Setup test data
    setup_test_data()
    
    # Create and test the stock monitor
    monitor = StockMonitorService()
    
    # Run a single check manually
    print("\n🔍 Running manual stock check...")
    monitor.check_all_clients_stock()
    
    # Check notifications created
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT type, message, created_at 
        FROM notifications 
        WHERE user_id = 'test-client-123'
        ORDER BY created_at DESC
    """)
    
    notifications = cursor.fetchall()
    
    print(f"\n📋 Notifications created: {len(notifications)}")
    for notification in notifications:
        print(f"  - {notification[0]}: {notification[1]}")
    
    # Check alert log
    cursor.execute("""
        SELECT product_id, stock_level, threshold_level, alert_date
        FROM stock_alert_log 
        WHERE client_id = 'test-client-123'
    """)
    
    alert_logs = cursor.fetchall()
    
    print(f"\n📊 Alert logs created: {len(alert_logs)}")
    for log in alert_logs:
        print(f"  - Product {log[0]}: stock={log[1]}, threshold={log[2]}, date={log[3]}")
    
    conn.close()
    
    print("\n✅ Stock monitor test completed!")

def test_background_service():
    """Test the background service running"""
    print("\n🚀 Testing background service...")
    
    monitor = StockMonitorService()
    
    # Start the service
    monitor.start()
    
    print("⏰ Service started. Waiting 5 seconds...")
    time.sleep(5)
    
    # Stop the service
    monitor.stop()
    
    print("✅ Background service test completed!")

if __name__ == '__main__':
    print("🧪 Stock Monitor Test Suite")
    print("=" * 50)
    
    test_stock_monitor()
    test_background_service()
    
    print("\n🎉 All tests completed!")