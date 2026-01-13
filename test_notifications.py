#!/usr/bin/env python3
"""
Test script for the notification system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.shared.database import init_db, get_db_connection
from modules.notifications.routes import create_notification_for_user

def test_notifications():
    """Test the notification system"""
    print("🧪 Testing notification system...")
    
    # Initialize database
    init_db()
    print("✅ Database initialized")
    
    # Test creating a notification
    try:
        notification_id = create_notification_for_user(
            user_id='test-user-123',
            notification_type='sale',
            message='Test sale completed: ₹1,500 from John Doe',
            action_url='/retail/sales'
        )
        
        if notification_id:
            print(f"✅ Notification created with ID: {notification_id}")
        else:
            print("❌ Failed to create notification")
            
    except Exception as e:
        print(f"❌ Error creating notification: {e}")
    
    # Test reading notifications
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM notifications ORDER BY created_at DESC LIMIT 5")
        notifications = cursor.fetchall()
        
        print(f"📋 Found {len(notifications)} notifications:")
        for notification in notifications:
            print(f"  - {notification[3]} ({notification[2]})")  # message (type)
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading notifications: {e}")

if __name__ == '__main__':
    test_notifications()