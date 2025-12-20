"""
Test script to verify production fix
"""

import urllib.request
import urllib.parse

def test_production_route(name, url):
    """Test production route"""
    print(f"\n🧪 Testing: {name}")
    print(f"URL: {url}")
    
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            print(f"Status: {status_code}")
            
            if status_code == 200:
                print("✅ SUCCESS! Route is working")
                return True
            else:
                print(f"❌ FAILED! Status: {status_code}")
                return False
                
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("❌ FAILED! 404 Not Found")
        else:
            print(f"❌ FAILED! HTTP Error: {e.code}")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("🌐 PRODUCTION FIX VERIFICATION")
    print("=" * 50)
    
    # Test production URLs
    results = []
    
    # Test the fixed billing route
    results.append(test_production_route(
        "Retail Billing Page (FIXED)", 
        "https://www.bizpulse24.com/retail/billing"
    ))
    
    # Test other routes for comparison
    results.append(test_production_route(
        "Retail Dashboard", 
        "https://www.bizpulse24.com/retail/dashboard"
    ))
    
    results.append(test_production_route(
        "Main Homepage", 
        "https://www.bizpulse24.com/"
    ))
    
    print("\n" + "=" * 50)
    print("📊 RESULTS:")
    
    success_count = sum(results)
    total_count = len(results)
    
    if results[0]:  # Billing route specifically
        print("🎉 SUCCESS! Retail billing route is now working!")
        print("✅ 404 issue has been resolved")
        print("✅ Users can now access billing page")
    else:
        print("❌ Billing route still has issues")
        print("⚠️  May need more time for deployment to propagate")
    
    print(f"\n📈 Overall: {success_count}/{total_count} routes working")
    
    if success_count == total_count:
        print("🚀 All routes working perfectly!")
    else:
        print("⏳ Some routes may still be deploying...")

if __name__ == "__main__":
    main()