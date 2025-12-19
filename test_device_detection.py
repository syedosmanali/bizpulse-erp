#!/usr/bin/env python3
"""
Test Device Detection Logic
"""
import sys
import os
sys.path.append('BizPulse_Fresh_Deploy_20251211_015908')

from app import app

def test_device_detection():
    """Test device detection with different user agents"""
    
    test_cases = [
        {
            'name': 'iPhone',
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
            'expected': 'Mobile'
        },
        {
            'name': 'Android',
            'user_agent': 'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36',
            'expected': 'Mobile'
        },
        {
            'name': 'iPad',
            'user_agent': 'Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
            'expected': 'Mobile'
        },
        {
            'name': 'Desktop Chrome',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'expected': 'Desktop'
        },
        {
            'name': 'Desktop Firefox',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'expected': 'Desktop'
        }
    ]
    
    with app.test_client() as client:
        print("🧪 Testing Device Detection...")
        print("=" * 50)
        
        for test in test_cases:
            response = client.get('/', headers={'User-Agent': test['user_agent']})
            
            # Check if mobile template or desktop template
            if 'mobile_simple_working.html' in str(response.data) or 'BizPulse Mobile' in str(response.data):
                detected = 'Mobile'
            else:
                detected = 'Desktop'
            
            status = "✅ PASS" if detected == test['expected'] else "❌ FAIL"
            print(f"{status} {test['name']}: Expected {test['expected']}, Got {detected}")
        
        print("=" * 50)
        
        # Test force desktop
        print("🖥️ Testing Force Desktop...")
        response = client.get('/?desktop=1', headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)'})
        if 'responsive_index.html' in str(response.data) or 'Business Management' in str(response.data):
            print("✅ PASS Force Desktop: iPhone user got desktop view")
        else:
            print("❌ FAIL Force Desktop: iPhone user didn't get desktop view")
        
        print("\n🚀 Device Detection Test Complete!")

if __name__ == "__main__":
    test_device_detection()