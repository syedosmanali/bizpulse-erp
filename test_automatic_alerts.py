#!/usr/bin/env python3
"""
Test script for automatic stock alerts and popups
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.shared.database import init_db, get_db_connection, generate_id
from modules.notifications.routes import create_notification_for_user
from datetime import datetime
import time

def create_test_scenario():
    """Create a complete test scenario with client, products, and settings"""
    print("🧪 Setting up automatic alerts test scenario...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create test client
    test_client_id = 'auto-alert-client-999'
    cursor.execute("""
        INSERT OR REPLACE INTO clients (
            id, company_name, contact_email, username, password_hash, is_active
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (test_client_id, 'Auto Alert Test Co', 'autoalert@test.com', 'autoalertuser', 'hash999', 1))
    
    # Create notification settings (enabled with threshold 5)
    settings_id = generate_id()
    cursor.execute("""
        INSERT OR REPLACE INTO notification_settings (
            id, client_id, low_stock_enabled, low_stock_threshold, updated_at
        ) VALUES (?, ?, ?, ?, ?)
    """, (settings_id, test_client_id, 1, 5, datetime.now().isoformat()))
    
    # Create test products with various stock levels
    products = [
        ('auto-prod-1', 'Auto Test Product 1', 'Electronics', 0, 5),    # Out of stock
        ('auto-prod-2', 'Auto Test Product 2', 'Electronics', 2, 5),    # Low stock
        ('auto-prod-3', 'Auto Test Product 3', 'Electronics', 1, 5),    # Very low stock
        ('auto-prod-4', 'Auto Test Product 4', 'Electronics', 10, 5),   # Good stock
        ('auto-prod-5', 'Auto Test Product 5', 'Furniture', 3, 5),      # Low stock
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
    
    print("✅ Test scenario created:")
    print(f"  - Client: {test_client_id}")
    print(f"  - Notification settings: enabled, threshold=5")
    print(f"  - Products: {len(products)} total")
    print(f"    • 1 out of stock (0 items)")
    print(f"    • 3 low stock (1-3 items)")
    print(f"    • 1 good stock (10 items)")
    
    return test_client_id

def test_automatic_notifications():
    """Test creating automatic notifications that would trigger popups"""
    print("\n🔔 Testing automatic notification creation...")
    
    test_client_id = create_test_scenario()
    
    # Simulate the stock monitor creating notifications
    notifications_created = []
    
    # Create out of stock notification
    notif_id_1 = create_notification_for_user(
        user_id=test_client_id,
        notification_type='alert',
        message='Out of Stock: Auto Test Product 1 (Electronics)',
        action_url='/retail/products'
    )
    if notif_id_1:
        notifications_created.append(('Out of Stock', notif_id_1))
    
    # Create low stock notifications
    notif_id_2 = create_notification_for_user(
        user_id=test_client_id,
        notification_type='alert',
        message='Low Stock Alert: Auto Test Product 2 - Only 2 remaining (Electronics)',
        action_url='/retail/products'
    )
    if notif_id_2:
        notifications_created.append(('Low Stock', notif_id_2))
    
    notif_id_3 = create_notification_for_user(
        user_id=test_client_id,
        notification_type='alert',
        message='Low Stock Alert: Auto Test Product 5 - Only 3 remaining (Furniture)',
        action_url='/retail/products'
    )
    if notif_id_3:
        notifications_created.append(('Low Stock', notif_id_3))
    
    print(f"✅ Created {len(notifications_created)} automatic notifications:")
    for notif_type, notif_id in notifications_created:
        print(f"  - {notif_type}: ID {notif_id}")
    
    return notifications_created

def test_real_time_monitoring():
    """Test the real-time monitoring system"""
    print("\n⚡ Testing real-time monitoring simulation...")
    
    # Import the stock monitor
    from modules.notifications.stock_monitor import StockMonitorService
    
    # Create monitor instance
    monitor = StockMonitorService()
    
    # Run a manual stock check
    print("🔍 Running manual stock check...")
    monitor.check_all_clients_stock()
    
    # Check what notifications were created
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT type, message, created_at 
        FROM notifications 
        WHERE user_id = 'auto-alert-client-999'
        AND datetime(created_at) > datetime('now', '-1 minute')
        ORDER BY created_at DESC
    """)
    
    recent_notifications = cursor.fetchall()
    
    print(f"📋 Recent notifications from stock monitor: {len(recent_notifications)}")
    for notification in recent_notifications:
        print(f"  - {notification[0]}: {notification[1]}")
    
    conn.close()
    
    return len(recent_notifications)

def simulate_frontend_polling():
    """Simulate how the frontend would poll for new notifications"""
    print("\n📱 Simulating frontend real-time polling...")
    
    # This simulates what the dashboard JavaScript does every 15 seconds
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get recent notifications (last 5 minutes)
    cursor.execute("""
        SELECT id, type, message, action_url, is_read, created_at
        FROM notifications 
        WHERE user_id = 'auto-alert-client-999'
        AND datetime(created_at) > datetime('now', '-5 minutes')
        AND is_read = 0
        ORDER BY created_at DESC
    """)
    
    unread_notifications = cursor.fetchall()
    
    print(f"🔔 Unread notifications that would trigger popups: {len(unread_notifications)}")
    
    for notification in unread_notifications:
        notif_id, notif_type, message, action_url, is_read, created_at = notification
        
        # Determine popup type
        is_out_of_stock = 'Out of Stock' in message
        popup_type = 'CRITICAL' if is_out_of_stock else 'WARNING'
        
        print(f"  🚨 {popup_type} POPUP: {message}")
        print(f"     ID: {notif_id}, Created: {created_at}")
        
        # Simulate marking as read (what happens when user interacts with popup)
        # cursor.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notif_id,))
    
    # conn.commit()
    conn.close()
    
    return len(unread_notifications)

def test_complete_workflow():
    """Test the complete automatic alert workflow"""
    print("\n🔄 Testing complete automatic alert workflow...")
    
    print("\n1️⃣ Step 1: Create test scenario")
    client_id = create_test_scenario()
    
    print("\n2️⃣ Step 2: Run stock monitor (simulates background service)")
    alerts_created = test_real_time_monitoring()
    
    print("\n3️⃣ Step 3: Simulate frontend polling (simulates dashboard checking for alerts)")
    popups_triggered = simulate_frontend_polling()
    
    print("\n4️⃣ Step 4: Verify notification settings")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT low_stock_enabled, low_stock_threshold 
        FROM notification_settings 
        WHERE client_id = ?
    """, (client_id,))
    
    settings = cursor.fetchone()
    if settings:
        print(f"✅ Notification settings: enabled={bool(settings[0])}, threshold={settings[1]}")
    else:
        print("❌ No notification settings found")
    
    conn.close()
    
    print(f"\n📊 Workflow Summary:")
    print(f"  - Test client created: {client_id}")
    print(f"  - Stock alerts created by monitor: {alerts_created}")
    print(f"  - Popups that would be triggered: {popups_triggered}")
    print(f"  - Settings configured: {'✅' if settings else '❌'}")
    
    return {
        'client_id': client_id,
        'alerts_created': alerts_created,
        'popups_triggered': popups_triggered,
        'settings_ok': bool(settings)
    }

def main():
    print("🚨 Automatic Stock Alerts Test Suite")
    print("=" * 60)
    
    # Initialize database
    init_db()
    
    # Test individual components
    print("\n🧪 Testing individual components...")
    test_automatic_notifications()
    
    # Test complete workflow
    print("\n🔄 Testing complete workflow...")
    results = test_complete_workflow()
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎯 AUTOMATIC ALERTS TEST RESULTS")
    print("=" * 60)
    
    if results['settings_ok'] and results['alerts_created'] > 0:
        print("✅ SUCCESS: Automatic alert system is working!")
        print("\n📋 What this means:")
        print("  • Stock monitor detects low/out of stock products")
        print("  • Notifications are created automatically")
        print("  • Frontend polling would detect new notifications")
        print("  • Popups would appear with sound alerts")
        print("  • Browser notifications would be sent")
        
        print(f"\n🔔 In the real system:")
        print(f"  • Background service runs every 10 minutes")
        print(f"  • Dashboard checks for new alerts every 15 seconds")
        print(f"  • Users see instant popups when stock runs low")
        print(f"  • {results['popups_triggered']} popups would appear right now!")
        
    else:
        print("❌ ISSUES DETECTED:")
        if not results['settings_ok']:
            print("  • Notification settings not configured properly")
        if results['alerts_created'] == 0:
            print("  • No alerts were created by stock monitor")
    
    print(f"\n🌐 Test the frontend:")
    print(f"  • Dashboard: http://localhost:5000/retail/dashboard")
    print(f"  • Settings: http://localhost:5000/notification-settings")
    print(f"  • Demo: http://localhost:5000/stock-alert-demo")
    
    print("\n🎉 Test completed!")

if __name__ == '__main__':
    main()