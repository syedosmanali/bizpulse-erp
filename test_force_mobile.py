#!/usr/bin/env python3
"""
Test Force Mobile Template
"""
import sys
import os
sys.path.append('BizPulse_Fresh_Deploy_20251211_015908')

from app import app
from flask import render_template

def test_force_mobile():
    """Test forcing mobile template directly"""
    
    with app.app_context():
        print("🧪 Testing Direct Mobile Template Render...")
        
        try:
            # Try to render mobile template directly
            content = render_template('mobile_simple_working.html')
            print(f"✅ Mobile template rendered successfully")
            print(f"Content length: {len(content)}")
            
            # Check for mobile indicators
            if 'BizPulse Mobile' in content:
                print("✅ Found 'BizPulse Mobile' title")
            else:
                print("❌ Missing 'BizPulse Mobile' title")
                
            if 'class="top-bar"' in content:
                print("✅ Found mobile top-bar")
            else:
                print("❌ Missing mobile top-bar")
                
            print(f"\nFirst 200 chars:")
            print(content[:200])
            
        except Exception as e:
            print(f"❌ Error rendering mobile template: {e}")

if __name__ == "__main__":
    test_force_mobile()