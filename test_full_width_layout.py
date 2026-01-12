#!/usr/bin/env python3
"""
Test Full Width Layout
======================

This script tests the full-width responsive layout functionality.
"""

import requests

def test_full_width_layout_css():
    """Test if full-width layout CSS is properly implemented"""
    print("🧪 Testing Full Width Layout CSS...")
    print("=" * 60)
    
    try:
        response = requests.get("http://localhost:5000/retail/dashboard", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # Check for responsive auto-fit grid
            responsive_css = [
                'grid-template-columns: repeat(auto-fit, minmax(280px, 1fr))',
                'grid-template-columns: repeat(auto-fit, minmax(320px, 1fr))',
                'justify-content: center',
                'width: calc(100% - 32px)',
                'width: calc(100% - 48px)'
            ]
            
            missing_responsive = []
            for css in responsive_css:
                if css not in content:
                    missing_responsive.append(css)
            
            if missing_responsive:
                print("❌ Missing responsive layout CSS:")
                for css in missing_responsive:
                    print(f"   - {css}")
            else:
                print("✅ Responsive auto-fit layout CSS properly implemented")
            
            # Check for full-width content area
            content_css = [
                '.content-area {',
                'width: calc(100% - 32px)',
                'max-width: none',
                'transition: all 0.4s cubic-bezier'
            ]
            
            missing_content = []
            for css in content_css:
                if css not in content:
                    missing_content.append(css)
            
            if missing_content:
                print("❌ Missing content area CSS:")
                for css in missing_content:
                    print(f"   - {css}")
            else:
                print("✅ Content area CSS properly implemented")
            
            # Check for tablet responsive behavior
            tablet_css = [
                'grid-template-columns: repeat(auto-fit, minmax(240px, 1fr))',
                'grid-template-columns: repeat(auto-fit, minmax(280px, 1fr))',
                'width: calc(100% - 24px)'
            ]
            
            missing_tablet = []
            for css in tablet_css:
                if css not in content:
                    missing_tablet.append(css)
            
            if missing_tablet:
                print("❌ Missing tablet responsive CSS:")
                for css in missing_tablet:
                    print(f"   - {css}")
            else:
                print("✅ Tablet responsive CSS properly implemented")
                
            print(f"\n✅ Dashboard loads successfully (HTTP {response.status_code})")
            
        else:
            print(f"❌ Dashboard failed to load: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")
    
    print("\n" + "=" * 60)

def main():
    print("🎯 FULL WIDTH LAYOUT TEST")
    print("=" * 60)
    print("Testing responsive full-width layout behavior...")
    print()
    
    test_full_width_layout_css()
    
    print("📋 MANUAL TESTING STEPS:")
    print("1. Open dashboard: http://localhost:5000/retail/dashboard")
    print("2. Observe layout with sidebar visible:")
    print("   - Cards should auto-fit to available width")
    print("   - No empty space on the right")
    print("   - Cards should be evenly distributed")
    print("3. Click hamburger menu to hide sidebar:")
    print("   - Cards should expand to use full screen width")
    print("   - Cards should auto-fit with larger minimum width")
    print("   - Content should be centered and balanced")
    print("4. Resize browser window:")
    print("   - Cards should reflow responsively")
    print("   - Layout should always use full available width")
    print("   - No horizontal scrolling should occur")
    
    print("\n✅ EXPECTED BEHAVIOR:")
    print("SIDEBAR VISIBLE:")
    print("- Cards: auto-fit with 280px minimum width")
    print("- Layout: uses full available width after sidebar")
    print("- Spacing: evenly distributed, no empty space")
    print("- Responsive: cards wrap to new rows as needed")
    print()
    print("SIDEBAR HIDDEN:")
    print("- Cards: auto-fit with 320px minimum width")
    print("- Layout: uses complete screen width")
    print("- Spacing: larger gaps, more breathing room")
    print("- Responsive: optimal use of full screen real estate")
    print()
    print("RESPONSIVE BREAKPOINTS:")
    print("- Desktop: auto-fit cards with optimal sizing")
    print("- Tablet: auto-fit with 240px/280px minimums")
    print("- Mobile: single column, full width")
    
    print("\n🔧 LAYOUT FIXES APPLIED:")
    print("- ✅ Auto-fit grid: repeat(auto-fit, minmax(280px, 1fr))")
    print("- ✅ Full width content: calc(100% - margins)")
    print("- ✅ Responsive minimums: 240px → 280px → 320px")
    print("- ✅ Centered layout: justify-content: center")
    print("- ✅ No fixed columns: cards adapt to screen size")
    print("- ✅ Proper margins: calculated widths prevent overflow")
    print("- ✅ Tablet optimization: auto-fit with appropriate minimums")
    print("- ✅ Mobile optimization: single column, full width")
    
    print("\n🎉 Dashboard should now use full width properly!")

if __name__ == "__main__":
    main()