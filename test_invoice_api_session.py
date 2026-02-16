import requests

# Create a session to maintain cookies
session = requests.Session()

# First login to get session
login_data = {
    'username': 'admin',
    'password': 'admin123'
}

# Try to login (this might fail if no login endpoint, but let's see)
try:
    login_response = session.post('http://localhost:5000/login', data=login_data)
    print("Login status:", login_response.status_code)
except:
    print("Login endpoint not found or failed")

print("\nTesting invoice API with session...")
# Test with existing invoice ID
response = session.get('http://localhost:5000/api/invoices/61f6f126-4c57-4376-8c29-6e52537cc0b3')
print("Status code:", response.status_code)
print("Response:", response.json())

print("\n" + "="*50 + "\n")

# Test with non-existent invoice ID
response = session.get('http://localhost:5000/api/invoices/574b342a-3c57-4376-8c29-6e52537cc0b3')
print("Status code:", response.status_code)
print("Response:", response.json())