#!/usr/bin/env python3
"""
Test Client Management Access for Admin Users
"""

import requests
import json

def test_admin_access():
    """Test that admin users can access client management"""
    
    # Test data for different user types
    test_users = [
        {
            'email': 'bizpulse.erp@gmail.com',
            'password': 'demo123',
            'expected_admin': True,
            'name': 'BizPulse Main Admin'
        },
        {
            'email': 'admin@bizpulse.com', 
            'password': 'demo123',
            'expected_admin': True,
            'name': 'BizPulse Admin'
        },
        {
            'email': 'support@bizpulse.com',
            'password': 'demo123', 
            'expected_admin': True,
            'name': 'BizPulse Support'
        },
        {
            'email': 'admin@demo.com',
            'password': 'demo123',
            'expected_admin': False,
            'name': 'Regular Demo User'
        }
    ]
    
    base_url = 'http://localhost:5000'
    
    print("🧪 Testing Client Management Access for Different User Types")
    print("=" * 70)
    
    for user in test_users:
        print(f"\n👤 Testing: {user['name']} ({user['email']})")
        
        # Create session
        session = requests.Session()
        
        try:
            # Login
            login_response = session.post(f'{base_url}/api/auth/unified-login', 
                json={
                    'login_id': user['email'],
                    'password': user['password']
                })
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                is_admin = login_data.get('user', {}).get('is_super_admin', False)
                
                print(f"   ✅ Login successful")
                print(f"   🔑 Is Super Admin: {is_admin}")
                print(f"   📋 Expected Admin: {user['expected_admin']}")
                
                if is_admin == user['expected_admin']:
                    print(f"   ✅ Admin status matches expectation")
                else:
                    print(f"   ❌ Admin status mismatch!")
                
                # Test client management page access
                cm_response = session.get(f'{base_url}/client-management')
                if cm_response.status_code == 200:
                    print(f"   ✅ Can access client management page")
                else:
                    print(f"   ❌ Cannot access client management page (Status: {cm_response.status_code})")
                
                # Test client management API access
                api_response = session.get(f'{base_url}/api/rbac/super-admin/clients')
                if api_response.status_code == 200:
                    print(f"   ✅ Can access client management API")
                elif api_response.status_code == 401:
                    print(f"   ⚠️  Unauthorized for client management API (expected for non-admins)")
                else:
                    print(f"   ❌ API error (Status: {api_response.status_code})")
                    
            else:
                print(f"   ❌ Login failed (Status: {login_response.status_code})")
                
        except Exception as e:
            print(f"   ❌ Error testing user: {e}")
    
    print("\n" + "=" * 70)
    print("🎯 Test Summary:")
    print("- BizPulse admin users should have is_super_admin = True")
    print("- BizPulse admin users should access client management page")
    print("- BizPulse admin users should access client management API")
    print("- Regular users should have is_super_admin = False")
    print("- Regular users should be unauthorized for client management API")

if __name__ == '__main__':
    test_admin_access()