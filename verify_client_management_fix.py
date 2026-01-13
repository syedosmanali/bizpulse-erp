#!/usr/bin/env python3
"""
Comprehensive test to verify client management access for all admin users
"""

import sqlite3
from modules.shared.database import get_db_connection

def test_admin_users():
    """Test all admin users in the database"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("🧪 Testing Client Management Access Fix")
    print("=" * 60)
    
    # Get all users with admin flag
    cursor.execute("""
        SELECT id, first_name, last_name, email, is_admin 
        FROM users 
        WHERE is_active = 1 
        ORDER BY is_admin DESC, email
    """)
    
    users = cursor.fetchall()
    
    print(f"\n📋 Found {len(users)} active users:")
    print("-" * 60)
    
    admin_count = 0
    user_count = 0
    
    for user in users:
        user_id, first_name, last_name, email, is_admin = user
        name = f"{first_name} {last_name}"
        
        if is_admin:
            admin_count += 1
            status = "✅ ADMIN"
            access = "Should have Client Management access"
        else:
            user_count += 1
            status = "👤 USER"
            access = "Should NOT have Client Management access"
        
        print(f"{status} | {name:<25} | {email:<30} | {access}")
    
    print("-" * 60)
    print(f"📊 Summary: {admin_count} admins, {user_count} regular users")
    
    # Test authentication logic
    print(f"\n🔍 Testing Authentication Logic:")
    print("-" * 60)
    
    from modules.auth.service import AuthService
    auth_service = AuthService()
    
    # Test a few key users
    test_users = [
        ('bizpulse.erp@gmail.com', 'demo123', True),
        ('admin@bizpulse.com', 'demo123', True),
        ('support@bizpulse.com', 'demo123', True),
        ('admin@demo.com', 'demo123', False)
    ]
    
    for email, password, expected_admin in test_users:
        try:
            result = auth_service.authenticate_user(email, password)
            if result['success']:
                actual_admin = result['user']['is_super_admin']
                status = "✅" if actual_admin == expected_admin else "❌"
                print(f"{status} {email:<30} | Admin: {actual_admin} (Expected: {expected_admin})")
            else:
                print(f"❌ {email:<30} | Login failed")
        except Exception as e:
            print(f"❌ {email:<30} | Error: {e}")
    
    conn.close()
    
    print(f"\n🎯 Expected Behavior:")
    print("- All users with @bizpulse.com emails should be admins")
    print("- All users with is_admin=1 should be admins") 
    print("- Admin users should see Client Management in dashboard")
    print("- Regular users should NOT see Client Management")
    print("\n✅ Fix Applied:")
    print("- Frontend: Changed email check to is_super_admin flag")
    print("- Backend: Updated RBAC routes to use is_super_admin")
    print("- Database: Added is_admin column for flexible admin management")

def show_frontend_changes():
    """Show what was changed in the frontend"""
    
    print(f"\n📝 Frontend Changes Made:")
    print("-" * 60)
    print("File: frontend/screens/templates/retail_dashboard.html")
    print()
    print("BEFORE:")
    print("  if (userInfo.email && userInfo.email.toLowerCase() === 'bizpulse.erp@gmail.com') {")
    print("    document.getElementById('client-management-nav').style.display = 'flex';")
    print("  }")
    print()
    print("AFTER:")
    print("  if (userInfo.is_super_admin) {")
    print("    document.getElementById('client-management-nav').style.display = 'flex';")
    print("  }")
    print()
    print("📝 Backend Changes Made:")
    print("-" * 60)
    print("File: modules/rbac/routes.py")
    print()
    print("BEFORE:")
    print("  is_existing_admin = session.get('email') == 'bizpulse.erp@gmail.com'")
    print()
    print("AFTER:")
    print("  is_existing_admin = session.get('is_super_admin', False)")

if __name__ == '__main__':
    test_admin_users()
    show_frontend_changes()