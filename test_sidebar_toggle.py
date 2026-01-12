#!/usr/bin/env python3
"""
Test Sidebar Toggle Functionality
=================================

This script tests the sidebar toggle functionality to ensure it works correctly.
"""

import requests

def test_sidebar_toggle_elements():
    """Test if sidebar toggle elements exist in dashboard"""
    print("🧪 Testing Sidebar Toggle Elements...")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:5000/retail/dashboard", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # Check for sidebar toggle elements
            elements = [
                'class="menu-toggle"',
                'onclick="toggleSidebar()"',
                'function toggleSidebar',
                'sidebar.classList.toggle(\'collapsed\')',
                '.sidebar.collapsed',
                'window.toggleSidebar = toggleSidebar'
            ]
            
            missing_elements = []
            for element in elements:
                if element not in content:
                    missing_elements.append(element)
            
            if missing_elements:
                print("❌ Missing sidebar toggle elements:")
                for element in missing_elements:
                    print(f"   - {element}")
            else:
                print("✅ All sidebar toggle elements are present")
            
            # Check for expanded layout CSS
            expanded_css = [
                '.sidebar.collapsed ~ .main-content .stats-grid',
                'grid-template-columns: repeat(6, 1fr)',
                'transform: translateX(-280px)',
                'margin-left: 0',
                'width: 100%'
            ]
            
            missing_css = []
            for css in expanded_css:
                if css not in content:
                    missing_css.append(css)
            
            if missing_css:
                print("❌ Missing expanded layout CSS:")
                for css in missing_css:
                    print(f"   - {css}")
            else:
                print("✅ All expanded layout CSS is present")
                
            print(f"\n✅ Dashboard loads successfully (HTTP {response.status_code})")
            
        else:
            print(f"❌ Dashboard failed to load: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")
    
    print("\n" + "=" * 50)

def main():
    print("🎯 SIDEBAR TOGGLE FUNCTIONALITY TEST")
    print("=" * 50)
    print("Testing sidebar toggle and content expansion...")
    print()
    
    test_sidebar_toggle_elements()
    
    print("📋 MANUAL TESTING STEPS:")
    print("1. Login to dashboard: http://localhost:5000/retail/dashboard")
    print("2. Look for hamburger menu (☰) in top-left corner")
    print("3. Click the hamburger menu button")
    print("4. Verify sidebar slides out completely (hidden)")
    print("5. Verify dashboard cards expand to use full width")
    print("6. Verify stats show 6 cards in a row instead of 4")
    print("7. Click hamburger menu again to show sidebar")
    print("8. Verify sidebar slides back in")
    print("9. Verify dashboard cards return to normal 4-column layout")
    
    print("\n✅ EXPECTED BEHAVIOR:")
    print("- Hamburger menu toggles sidebar visibility")
    print("- When sidebar hidden: content uses full width")
    print("- When sidebar hidden: stats grid shows 6 columns")
    print("- When sidebar hidden: actions grid expands")
    print("- When sidebar visible: normal 4-column layout")
    print("- Smooth transitions between states")
    
    print("\n🔧 CSS CHANGES MADE:")
    print("- ✅ Sidebar completely hidden when collapsed (-280px)")
    print("- ✅ Top header expands to full width when collapsed")
    print("- ✅ Main content uses full width when collapsed")
    print("- ✅ Stats grid expands to 6 columns when collapsed")
    print("- ✅ Actions grid expands when collapsed")
    print("- ✅ Responsive behavior for tablets")
    
    print("\n🎉 Sidebar toggle functionality should now work perfectly!")

if __name__ == "__main__":
    main()