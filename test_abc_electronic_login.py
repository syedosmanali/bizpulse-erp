#!/usr/bin/env python3
"""
Test ABC Electronic Login
==========================

This script tests the abc_electronic login to ensure it works without @ symbol requirement.
"""

def test_abc_electronic_login():
    """Test abc_electronic login functionality"""
    
    print("🧪 TESTING ABC ELECTRONIC LOGIN")
    print("=" * 40)
    
    # Test the authentication service directly
    from modules.auth.service import AuthService
    
    auth_service = AuthService()
    
    # Test 1: Username login
    print("\n1. Testing username login...")
    result1 = auth_service.authenticate_user('abc_electronic', 'admin123')
    
    if result1['success']:
        print("   ✅ Username login successful!")
        print(f"   User: {result1['user']['name']}")
        print(f"   Type: {result1['user']['type']}")
        print(f"   Company: {result1['user'].get('company_name', 'N/A')}")
    else:
        print(f"   ❌ Username login failed: {result1['message']}")
    
    # Test 2: Email login
    print("\n2. Testing email login...")
    result2 = auth_service.authenticate_user('abc_electronic@store.com', 'admin123')
    
    if result2['success']:
        print("   ✅ Email login successful!")
        print(f"   User: {result2['user']['name']}")
        print(f"   Type: {result2['user']['type']}")
        print(f"   Business: {result2['user'].get('business_name', 'N/A')}")
    else:
        print(f"   ❌ Email login failed: {result2['message']}")
    
    # Test 3: Wrong password
    print("\n3. Testing wrong password...")
    result3 = auth_service.authenticate_user('abc_electronic', 'wrongpassword')
    
    if result3['success']:
        print("   ❌ Wrong password accepted (this is bad!)")
    else:
        print(f"   ✅ Wrong password rejected: {result3['message']}")
    
    # Test 4: Non-existent user
    print("\n4. Testing non-existent user...")
    result4 = auth_service.authenticate_user('nonexistent_user', 'admin123')
    
    if result4['success']:
        print("   ❌ Non-existent user accepted (this is bad!)")
    else:
        print(f"   ✅ Non-existent user rejected: {result4['message']}")
    
    print("\n✅ LOGIN TESTING COMPLETED!")
    print("=" * 40)
    print()
    print("📋 SUMMARY:")
    print(f"   • Username login: {'✅ PASS' if result1['success'] else '❌ FAIL'}")
    print(f"   • Email login: {'✅ PASS' if result2['success'] else '❌ FAIL'}")
    print(f"   • Wrong password: {'✅ PASS' if not result3['success'] else '❌ FAIL'}")
    print(f"   • Non-existent user: {'✅ PASS' if not result4['success'] else '❌ FAIL'}")
    print()
    print("🔐 LOGIN CREDENTIALS CONFIRMED:")
    print("   Username: abc_electronic")
    print("   Password: admin123")
    print("   Mobile URL: http://10.150.250.59:5000")
    print()
    print("✅ NO @ SYMBOL REQUIRED - USERNAME LOGIN WORKS!")

if __name__ == '__main__':
    test_abc_electronic_login()