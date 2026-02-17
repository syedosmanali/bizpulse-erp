"""Test authentication flow exactly as it happens in production"""
from modules.auth.service import AuthService
import logging

logging.basicConfig(level=logging.INFO)

auth_service = AuthService()

# Test Tasleem login
print("=" * 60)
print("Testing Tasleem login...")
print("=" * 60)

result = auth_service.authenticate_user('tasleem', 'Tasleem@123')

print(f"\nResult: {result.get('success')}")
print(f"Message: {result.get('message', 'No message')}")

if result['success']:
    print(f"\n✅ LOGIN SUCCESSFUL")
    print(f"User Type: {result['user']['type']}")
    print(f"User Name: {result['user']['name']}")
    print(f"Email: {result['user']['email']}")
    print(f"Username: {result['user']['username']}")
else:
    print(f"\n❌ LOGIN FAILED: {result.get('message')}")

# Test with email
print("\n" + "=" * 60)
print("Testing Tasleem login with email...")
print("=" * 60)

result2 = auth_service.authenticate_user('tasleem@gmail.com', 'Tasleem@123')

print(f"\nResult: {result2.get('success')}")
print(f"Message: {result2.get('message', 'No message')}")

if result2['success']:
    print(f"\n✅ LOGIN SUCCESSFUL")
    print(f"User Type: {result2['user']['type']}")
    print(f"User Name: {result2['user']['name']}")
else:
    print(f"\n❌ LOGIN FAILED: {result2.get('message')}")
