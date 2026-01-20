"""
Test anam's permissions through the service layer
"""
from modules.user_management.service import UserManagementService
from modules.user_management.models import UserManagementModels

service = UserManagementService()

# Get anam's user_id
user_id = "0d0433c4-fef4-483e-85dd-8cdae60a0510"

print("🧪 Testing anam's permissions")
print("=" * 60)

# Test get_current_user_permissions
print("\n1️⃣ Testing get_current_user_permissions...")
result = service.get_current_user_permissions(user_id)

if result['success']:
    print("✅ Success!")
    print(f"Permissions: {result['permissions']}")
    
    # Check what should be visible
    print("\n📋 Modules that should be visible:")
    for module, enabled in result['permissions'].items():
        status = "✅ VISIBLE" if enabled else "🚫 HIDDEN"
        print(f"   {module}: {status}")
else:
    print(f"❌ Error: {result.get('error')}")

print("\n" + "=" * 60)
print("Expected: Only 'billing' should be True, all others False")
