"""
Test if permissions endpoint is accessible
"""
import urllib.request
import json

url = "http://localhost:5000/api/user-management/permissions"

try:
    print(f"🧪 Testing endpoint: {url}")
    
    # Create request
    req = urllib.request.Request(url)
    req.add_header('Content-Type', 'application/json')
    
    # Make request
    try:
        response = urllib.request.urlopen(req, timeout=5)
        data = json.loads(response.read().decode())
        print(f"✅ Status: {response.status}")
        print(f"✅ Response: {json.dumps(data, indent=2)}")
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error: {e.code} {e.reason}")
        try:
            error_data = json.loads(e.read().decode())
            print(f"   Error details: {error_data}")
        except:
            print(f"   Raw error: {e.read().decode()}")
    except urllib.error.URLError as e:
        print(f"❌ URL Error: {e.reason}")
        
except Exception as e:
    print(f"❌ Error: {e}")
