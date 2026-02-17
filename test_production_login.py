"""
Test production login API directly
"""
import requests
import json

BASE_URL = "https://bizpulse24.com"

print("="*60)
print("TESTING PRODUCTION LOGIN API")
print("="*60)

# Test tasleem login
print("\n1️⃣ Testing Tasleem login...")
response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={
        "login_id": "tasleem",
        "password": "Tasleem@123"
    },
    headers={"Content-Type": "application/json"}
)

print(f"   Status: {response.status_code}")
print(f"   Response: {response.text[:200]}")

if response.status_code == 200:
    print("   ✅ LOGIN SUCCESSFUL!")
else:
    print("   ❌ LOGIN FAILED!")
    print(f"   Full response: {response.text}")

# Test with email
print("\n2️⃣ Testing with email...")
response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={
        "login_id": "tasleem@gmail.com",
        "password": "Tasleem@123"
    },
    headers={"Content-Type": "application/json"}
)

print(f"   Status: {response.status_code}")
if response.status_code == 200:
    print("   ✅ LOGIN SUCCESSFUL!")
else:
    print("   ❌ LOGIN FAILED!")
    print(f"   Response: {response.text}")

print("\n" + "="*60)
