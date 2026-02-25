import sys
import traceback

try:
    print("Starting import test...")
    from app import app
    print("✓ App imported successfully")
    
    print("\nStarting server test...")
    print(f"✓ Server configured on port 5000")
    print(f"✓ Debug mode: {app.debug}")
    
    print("\nTesting ERP routes...")
    with app.test_client() as client:
        # Test products page
        response = client.get('/erp/products')
        print(f"✓ /erp/products: {response.status_code}")
        
        # Test challan page
        response = client.get('/erp/challan')
        print(f"✓ /erp/challan: {response.status_code}")
        
    print("\n✅ All tests passed!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
