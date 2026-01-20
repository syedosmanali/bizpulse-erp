"""Integration test to log in as a user and fetch permission debug info.

Run this when the dev server is running (http://localhost:5000).
"""
import requests

BASE = "http://localhost:5000"

# Replace with real credentials that exist in your DB
USERNAME = "ajay711"
PASSWORD = "ajay123"

s = requests.Session()

print("Logging in as:", USERNAME)
resp = s.post(f"{BASE}/api/auth/login", json={"loginId": USERNAME, "password": PASSWORD})
print("Login status:", resp.status_code)
print(resp.text)

if resp.status_code != 200 and resp.status_code != 201:
    print("Login failed; make sure the server is running and credentials are correct.")
else:
    print('\nRequesting /api/user-management/debug-permissions')
    r = s.get(f"{BASE}/api/user-management/debug-permissions")
    print('Status:', r.status_code)
    print(r.text)

    print('\nRequesting /api/user-management/user-permissions')
    r2 = s.get(f"{BASE}/api/user-management/user-permissions")
    print('Status:', r2.status_code)
    print(r2.text)
