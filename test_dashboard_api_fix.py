#!/usr/bin/env python3
"""
Test dashboard API to verify it's returning correct data
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_dashboard_api():
    print("🔍 Testing Dashboard API Fix")
    print("=" * 50)
    
    try:
        import app
        
        # Create test request context
        with app.app.test_request_context('/api/dashboard/stats'):
            # Mock authentication
            from flask import session
            session['user_id'] = 'test_user'
            
            # Call the dashboard API
            response = app.get_dashboard_stats()
            
            if hasattr(response, 'get_json'):
                data = response.get_json()
            else:
                data = response
            
            print(f"📊 API Response Status: {'✅ Success' if data.get('success') else '❌ Failed'}")
            
            if data.get('success'):
                print(f"\n📈 Dashboard Data:")
                print(f"   Today's Revenue: ₹{data.get('today_revenue', 0)}")
                print(f"   Today's Orders: {data.get('today_orders', 0)}")
                print(f"   Today's Profit: ₹{data.get('today_profit', 0)}")
                print(f"   Total Products: {data.get('total_products', 0)}")
                print(f"   Total Customers: {data.get('total_customers', 0)}")
                print(f"   Low Stock: {data.get('low_stock', 0)}")
                print(f"   Out of Stock: {data.get('out_of_stock', 0)}")
                
                print(f"\n📋 Recent Sales: {len(data.get('recent_sales', []))}")
                for sale in data.get('recent_sales', [])[:3]:
                    print(f"   - {sale.get('bill_number', 'N/A')}: ₹{sale.get('total_amount', 0)} ({sale.get('customer_name', 'Unknown')})")
                
                print(f"\n🏆 Top Products: {len(data.get('top_products', []))}")
                for product in data.get('top_products', [])[:3]:
                    print(f"   - {product.get('product_name', 'Unknown')}: {product.get('total_quantity', 0)} sold")
                
                # Check if data is realistic
                revenue = data.get('today_revenue', 0)
                orders = data.get('today_orders', 0)
                
                print(f"\n🔧 Data Validation:")
                if revenue > 0 and orders > 0:
                    avg_order = revenue / orders
                    print(f"   ✅ Average order value: ₹{avg_order:.2f}")
                elif revenue == 0 and orders == 0:
                    print(f"   ✅ No sales today - this is normal")
                else:
                    print(f"   ⚠️  Inconsistent data: Revenue={revenue}, Orders={orders}")
                
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown error')}")
                
    except Exception as e:
        print(f"❌ Test Error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n" + "=" * 50)
    print("💡 Expected Dashboard Behavior:")
    print("   1. Shows today's actual sales data")
    print("   2. Updates when new sales are made")
    print("   3. Consistent data across refreshes")
    print("   4. Compact UI that fits on one page")

if __name__ == "__main__":
    test_dashboard_api()