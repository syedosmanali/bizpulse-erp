#!/usr/bin/env python3
"""
Test Actual Response Content
"""
import sys
import os
sys.path.append('BizPulse_Fresh_Deploy_20251211_015908')

from app import app

def test_response():
    """Test actual response content"""
    
    with app.test_client() as client:
        print("🧪 Testing iPhone Response...")
        
        response = client.get('/', headers={
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
        })
        
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.data)}")
        
        content = response.data.decode('utf-8')
        
        # Check for mobile indicators
        mobile_indicators = [
            'BizPulse Mobile',
            'mobile_simple_working',
            'class="top-bar"',
            'class="menu-btn"'
        ]
        
        desktop_indicators = [
            'Business Management Made Simple',
            'responsive_index',
            'class="hero"',
            'class="navbar"'
        ]
        
        print("\nMobile Indicators Found:")
        for indicator in mobile_indicators:
            found = indicator in content
            print(f"  {indicator}: {found}")
        
        print("\nDesktop Indicators Found:")
        for indicator in desktop_indicators:
            found = indicator in content
            print(f"  {indicator}: {found}")
        
        # Show first 200 chars
        print(f"\nFirst 200 chars of response:")
        print(content[:200])

if __name__ == "__main__":
    test_response()