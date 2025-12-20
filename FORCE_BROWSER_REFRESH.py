#!/usr/bin/env python3
"""
Force browser to refresh by adding cache-busting to the template
"""

def add_cache_busting():
    print("🔧 Adding cache-busting to sales_management_wine.html...")
    
    # Read the template
    with open('templates/sales_management_wine.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add cache-busting parameter to API calls
    cache_buster = "Date.now()"
    
    # Replace the API call in loadSales function
    old_api_call = "const response = await fetch(`/api/sales/all?${params.toString()}`);"
    new_api_call = f"const response = await fetch(`/api/sales/all?${{params.toString()}}&_cb=${{Date.now()}}`);"
    
    content = content.replace(old_api_call, new_api_call)
    
    # Add a version comment to force browser refresh
    version_comment = f"<!-- CACHE BUSTER: {cache_buster} -->\n"
    content = version_comment + content
    
    # Write back
    with open('templates/sales_management_wine.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Cache-busting added!")
    print("📋 Changes:")
    print("   - Added cache-busting parameter to API calls")
    print("   - Added version comment to force browser refresh")
    print("   - Browser will now reload fresh JavaScript")

def main():
    print("🚀 FORCE BROWSER REFRESH - Sales Management")
    print("=" * 50)
    
    add_cache_busting()
    
    print("\n🌐 Testing Instructions:")
    print("1. Open: http://localhost:5000/debug-sales")
    print("2. Test the API directly in browser")
    print("3. Then open: http://localhost:5000/sales-management")
    print("4. Hard refresh (Ctrl+F5) to force reload")
    print("5. Clear browser cache if still not working")
    
    print("\n✅ If API test works but page doesn't:")
    print("   - Clear browser cache completely")
    print("   - Try incognito/private mode")
    print("   - Check browser console for errors (F12)")

if __name__ == "__main__":
    main()