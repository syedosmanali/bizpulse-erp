import sys
import traceback

def test_service_import():
    """Test if retail service can be imported and instantiated"""
    print("=== TESTING SERVICE IMPORT ===")
    
    try:
        print("1. Importing retail service...")
        from modules.retail.service import RetailService
        print("✅ RetailService imported successfully")
        
        print("2. Creating service instance...")
        service = RetailService()
        print("✅ RetailService instance created successfully")
        
        print("3. Testing get_dashboard_stats method...")
        # Test with no user_id to avoid session issues
        result = service.get_dashboard_stats(None)
        print("✅ get_dashboard_stats executed successfully")
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_service_import()