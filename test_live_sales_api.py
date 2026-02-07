"""
Test the live sales API to see the exact error
"""
import requests
import json

# Test the live API
url = "https://bizpulse-erp-1.onrender.com/api/sales/all"

print("🔍 Testing live sales API...")
print(f"URL: {url}")

try:
    response = requests.get(url, params={"filter": "today"})
    print(f"\n📊 Status Code: {response.status_code}")
    print(f"📊 Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ SUCCESS!")
        print(f"Total sales: {len(data.get('sales', []))}")
        print(f"Summary: {data.get('summary', {})}")
    else:
        print(f"\n❌ ERROR!")
        print(f"Response text: {response.text[:500]}")
        
        # Try to parse as JSON
        try:
            error_data = response.json()
            print(f"\nError JSON: {json.dumps(error_data, indent=2)}")
        except:
            print("\nCould not parse error as JSON")
            
except Exception as e:
    print(f"\n❌ Exception: {e}")
    import traceback
    traceback.print_exc()
