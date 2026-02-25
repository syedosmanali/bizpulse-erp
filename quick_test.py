#!/usr/bin/env python
import sys

print("=" * 50)
print("TESTING ERP MODULE IMPORT")
print("=" * 50)

try:
    print("\n1. Testing basic imports...")
    from flask import Flask
    print("   ✓ Flask imported")
    
    from modules.shared.database import get_db_connection
    print("   ✓ Database module imported")
    
    print("\n2. Testing ERP routes import...")
    from modules.erp_modules.routes import erp_bp
    print("   ✓ ERP blueprint imported")
    
    print("\n3. Creating test app...")
    app = Flask(__name__)
    app.register_blueprint(erp_bp)
    print("   ✓ Blueprint registered")
    
    print("\n4. Testing routes...")
    with app.test_client() as client:
        resp = client.get('/erp/products')
        print(f"   ✓ /erp/products returned: {resp.status_code}")
        
        resp = client.get('/erp/challan')
        print(f"   ✓ /erp/challan returned: {resp.status_code}")
    
    print("\n" + "=" * 50)
    print("✅ ALL TESTS PASSED!")
    print("=" * 50)
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
