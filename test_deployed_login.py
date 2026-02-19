"""
Simple test script to check deployed login functionality
"""

import os
import requests
import json

def test_deployed_login():
    """Test login against the deployed server"""
    
    # Replace with your actual deployed URL
    deployed_url = "https://bizpulse-erp.onrender.com"  # or your actual URL
    
    print(f"Testing login against: {deployed_url}")
    
    # Test login endpoint
    login_url = f"{deployed_url}/api/auth/login"
    
    # Test data
    test_credentials = {
        'loginId': 'bizpulse.erp@gmail.com',
        'password': 'BizPulse@2024!'
    }
    
    print(f"Sending POST request to: {login_url}")
    print(f"Payload: {json.dumps(test_credentials, indent=2)}")
    
    try:
        response = requests.post(
            login_url,
            json=test_credentials,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"Response Body: {json.dumps(response_data, indent=2)}")
        except:
            print(f"Response Text: {response.text}")
            
        # Check if it's a successful login
        if response.status_code == 200:
            if response_data.get('success') or response_data.get('message') == 'Login successful':
                print("\n✅ LOGIN SUCCESSFUL!")
                print("The deployed server is working correctly")
            else:
                print(f"\n❌ LOGIN FAILED: {response_data.get('message', 'Unknown error')}")
        else:
            print(f"\n❌ HTTP ERROR: {response.status_code}")
            if response.status_code == 401:
                print("Authentication failed - invalid credentials")
            elif response.status_code == 500:
                print("Server error - check server logs")
            elif response.status_code == 404:
                print("Login endpoint not found - check if deployment completed")
                
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Cannot reach the deployed server")
        print("Make sure your server is running and accessible")
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT: Server took too long to respond")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

def check_server_health():
    """Check if the server is responding"""
    deployed_url = "https://bizpulse-erp.onrender.com"  # or your actual URL
    
    print(f"\nChecking server health at: {deployed_url}")
    
    try:
        response = requests.get(f"{deployed_url}/health", timeout=10)
        print(f"Health check status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Server is responding")
            try:
                print(f"Health data: {response.json()}")
            except:
                print("Health check endpoint working but returned non-JSON")
        else:
            print("❌ Server health check failed")
    except Exception as e:
        print(f"❌ Cannot reach server: {e}")

if __name__ == "__main__":
    print("🚀 Testing Deployed Login Functionality")
    print("=" * 50)
    
    check_server_health()
    test_deployed_login()
    
    print("\n" + "=" * 50)
    print("💡 Troubleshooting Tips:")
    print("1. Make sure your deployment is complete and running")
    print("2. Verify the database schema fixes were applied to Supabase")
    print("3. Check server logs for any error messages")
    print("4. Ensure DATABASE_URL is correctly configured in your deployment")