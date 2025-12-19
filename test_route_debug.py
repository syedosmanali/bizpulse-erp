#!/usr/bin/env python3
"""
Test Route with Debug
"""
import sys
import os
sys.path.append('BizPulse_Fresh_Deploy_20251211_015908')

from app import app

def test_route_debug():
    """Test route with debug output"""
    
    with app.test_client() as client:
        print("🧪 Testing Route with Debug...")
        
        # Capture stdout to see debug prints
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        
        with redirect_stdout(f):
            response = client.get('/', headers={
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
            })
        
        debug_output = f.getvalue()
        print("Debug Output:")
        print(debug_output)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Length: {len(response.data)}")
        
        content = response.data.decode('utf-8')
        
        # Check title
        if '<title>BizPulse Mobile</title>' in content:
            print("✅ Mobile template detected")
        elif '<title>BizPulse - Modern Business Management Platform</title>' in content:
            print("❌ Desktop template detected")
        else:
            print("❓ Unknown template")
            
        print(f"\nTitle line:")
        for line in content.split('\n'):
            if '<title>' in line:
                print(line.strip())
                break

if __name__ == "__main__":
    test_route_debug()