"""Test Anam's login to verify permissions are returned correctly"""
import sys
sys.path.insert(0, '.')

from modules.auth.service import AuthService

auth_service = AuthService()

# Test Anam's login
result = auth_service.authenticate_user('anam', 'anam123')

if result['success']:
    print("✅ Login successful!")
    print(f"\n📋 User object returned:")
    print(f"   Name: {result['user']['name']}")
    print(f"   Type: {result['user']['type']}")
    print(f"   Username: {result['user']['username']}")
    print(f"\n🔐 Permissions in user object:")
    if 'permissions' in result['user']:
        print(f"   {result['user']['permissions']}")
    else:
        print("   ❌ NO PERMISSIONS IN USER OBJECT!")
    
    print(f"\n📦 Session data permissions:")
    if 'permissions' in result['session_data']:
        print(f"   {result['session_data']['permissions']}")
    else:
        print("   ❌ NO PERMISSIONS IN SESSION DATA!")
else:
    print(f"❌ Login failed: {result['message']}")
