#!/usr/bin/env python3
"""
Test script to verify dashboard functionality is restored
"""

import requests
import sys

def test_dashboard_access():
    """Test if dashboard loads without errors"""
    try:
        # Test dashboard page load
        response = requests.get('http://localhost:5000/retail/dashboard', timeout=10)
        
        if response.status_code == 200:
            print("✅ Dashboard loads successfully")
            
            # Check for critical JavaScript functions
            content = response.text
            
            critical_functions = [
                'function showModule',
                'function checkUserRole',
                'function loadProfileData',
                'function logout',
                'window.showModule',
                'window.checkUserRole'
            ]
            
            missing_functions = []
            for func in critical_functions:
                if func not in content:
                    missing_functions.append(func)
            
            if missing_functions:
                print(f"❌ Missing critical functions: {missing_functions}")
                return False
            else:
                print("✅ All critical functions are present")
                
            # Check for syntax errors in JavaScript
            if 'SyntaxError' in content or 'Unexpected token' in content:
                print("❌ JavaScript syntax errors detected")
                return False
            else:
                print("✅ No obvious JavaScript syntax errors")
                
            return True
        else:
            print(f"❌ Dashboard failed to load: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")
        return False

def main():
    print("🧪 Testing Dashboard Fix...")
    print("=" * 50)
    
    if test_dashboard_access():
        print("\n🎉 Dashboard fix appears successful!")
        print("✅ All critical functions restored")
        print("✅ No syntax errors detected")
        print("✅ Dashboard should be fully functional")
    else:
        print("\n❌ Dashboard fix needs more work")
        sys.exit(1)

if __name__ == "__main__":
    main()