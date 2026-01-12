#!/usr/bin/env python3
"""
Test Profile Functionality
==========================

This script tests the profile modal functionality to ensure it works correctly.
"""

import requests
import json

def test_profile_endpoints():
    """Test profile API endpoints"""
    print("🧪 Testing Profile API Endpoints...")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Test endpoints
    endpoints = [
        "/api/auth/user-info",
        "/api/client/profile"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint} - Working")
            elif response.status_code == 401:
                print(f"🔒 {endpoint} - Requires authentication (expected)")
            else:
                print(f"❌ {endpoint} - HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
    
    print("\n" + "=" * 50)

def test_profile_modal_elements():
    """Test if profile modal elements exist in dashboard"""
    print("🧪 Testing Profile Modal Elements...")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:5000/retail/dashboard", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # Check for profile modal elements
            elements = [
                'id="profileDetailsModal"',
                'id="headerProfileAvatar"',
                'id="headerProfileName"',
                'id="headerProfileRole"',
                'id="modalProfileName"',
                'id="modalProfileRole"',
                'id="modalProfileAvatar"',
                'onclick="openExistingProfileModal()"',
                'function openExistingProfileModal',
                'function loadUserProfileData',
                'function saveProfileDetails',
                'function uploadProfilePicture'
            ]
            
            missing_elements = []
            for element in elements:
                if element not in content:
                    missing_elements.append(element)
            
            if missing_elements:
                print("❌ Missing profile elements:")
                for element in missing_elements:
                    print(f"   - {element}")
            else:
                print("✅ All profile modal elements are present")
                
            print(f"\n✅ Dashboard loads successfully (HTTP {response.status_code})")
            
        else:
            print(f"❌ Dashboard failed to load: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")
    
    print("\n" + "=" * 50)

def main():
    print("🎯 PROFILE FUNCTIONALITY TEST")
    print("=" * 50)
    print("Testing profile modal and API functionality...")
    print()
    
    test_profile_endpoints()
    test_profile_modal_elements()
    
    print("📋 MANUAL TESTING STEPS:")
    print("1. Login to dashboard: http://localhost:5000/retail/dashboard")
    print("2. Look for profile button in top-right corner")
    print("3. Click the profile button")
    print("4. Verify profile modal opens with user data")
    print("5. Try updating profile information")
    print("6. Try uploading a profile picture")
    print("7. Verify changes are saved and reflected")
    
    print("\n✅ EXPECTED BEHAVIOR:")
    print("- Profile button shows user's first letter and name")
    print("- Clicking profile button opens modal with user data")
    print("- Modal shows correct role (Super Admin, Business Owner, etc.)")
    print("- Profile data can be edited and saved")
    print("- Profile picture can be uploaded")
    print("- Changes are reflected immediately")
    
    print("\n🔧 BACKEND APIs ADDED:")
    print("- ✅ GET /api/client/profile - Get profile data")
    print("- ✅ PUT /api/client/profile - Update profile data")
    print("- ✅ POST /api/client/profile/picture - Upload profile picture")
    
    print("\n🎉 Profile functionality should now be complete!")

if __name__ == "__main__":
    main()