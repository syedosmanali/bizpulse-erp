#!/usr/bin/env python3
"""
Test Live Deployment
"""
import requests

def test_live_site():
    """Test the live site"""
    try:
        print("🧪 Testing Live Site: https://bizpulse24.com")
        
        # Test with mobile user agent
        mobile_headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
        }
        
        response = requests.get('https://bizpulse24.com', headers=mobile_headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.text)}")
        
        # Check what template is being used
        if 'responsive_universal.html' in response.text or 'Business Management Made Simple' in response.text:
            print("✅ New responsive template detected")
        elif 'BizPulse Mobile' in response.text:
            print("❌ Old mobile template still being used")
        elif 'Modern Business Management Platform' in response.text:
            print("❌ Old desktop template still being used")
        else:
            print("❓ Unknown template")
        
        # Check for responsive indicators
        if '@media' in response.text:
            print("✅ CSS media queries found")
        else:
            print("❌ No CSS media queries found")
        
        # Show first 300 chars
        print(f"\nFirst 300 chars:")
        print(response.text[:300])
        
    except Exception as e:
        print(f"❌ Error testing live site: {e}")

if __name__ == "__main__":
    test_live_site()