#!/usr/bin/env python3
"""
Simple authentication test
"""

from modules.auth.service import AuthService

def test_auth():
    auth = AuthService()
    
    # Test BizPulse admin
    print("Testing bizpulse.erp@gmail.com...")
    result = auth.authenticate_user('bizpulse.erp@gmail.com', 'demo123')
    
    if result['success']:
        user = result['user']
        print(f"✅ Login successful")
        print(f"   Email: {user['email']}")
        print(f"   Name: {user['name']}")
        print(f"   Type: {user['type']}")
        print(f"   Is Super Admin: {user['is_super_admin']}")
    else:
        print(f"❌ Login failed: {result.get('message', 'Unknown error')}")

if __name__ == '__main__':
    test_auth()