#!/usr/bin/env python3
"""
Test the sales API endpoints to verify date filtering is working correctly
"""

import requests
import json
from datetime import datetime

def test_sales_api():
    print("🔍 Testing Sales API Date Filtering")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Test 1: Sales Summary API
    print("\n📊 Testing Sales Summary API:")
    try:
        response = requests.get(f"{base_url}/api/sales/summary")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Today's Sales: {data.get('today', {}).get('count', 0)} bills, ₹{data.get('today', {}).get('total', 0)}")
            print(f"   📅 Week's Sales: {data.get('week', {}).get('count', 0)} bills, ₹{data.get('week', {}).get('total', 0)}")
            print(f"   📅 Month's Sales: {data.get('month', {}).get('count', 0)} bills, ₹{data.get('month', {}).get('total', 0)}")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 2: Sales All API with today's date
    print("\n📋 Testing Sales All API (Today):")
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        response = requests.get(f"{base_url}/api/sales/all?from={today}&to={today}")
        if response.status_code == 200:
            data = response.json()
            sales = data.get('sales', [])
            summary = data.get('summary', {})
            print(f"   📅 Date Filter: {today}")
            print(f"   📊 Sales Found: {len(sales)}")
            print(f"   💰 Total Amount: ₹{summary.get('total_sales', 0)}")
            print(f"   🧾 Total Bills: {summary.get('total_bills', 0)}")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 3: Sales All API with yesterday's date
    print("\n📋 Testing Sales All API (Yesterday):")
    try:
        from datetime import timedelta
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        response = requests.get(f"{base_url}/api/sales/all?from={yesterday}&to={yesterday}")
        if response.status_code == 200:
            data = response.json()
            sales = data.get('sales', [])
            summary = data.get('summary', {})
            print(f"   📅 Date Filter: {yesterday}")
            print(f"   📊 Sales Found: {len(sales)}")
            print(f"   💰 Total Amount: ₹{summary.get('total_sales', 0)}")
            print(f"   🧾 Total Bills: {summary.get('total_bills', 0)}")
            
            # Show first few sales
            if sales:
                print("   📋 Sample Sales:")
                for i, sale in enumerate(sales[:3]):
                    print(f"      {i+1}. {sale.get('product_name', 'N/A')} - ₹{sale.get('total_price', 0)} ({sale.get('sale_date', 'N/A')})")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("✅ API Testing Complete!")

if __name__ == "__main__":
    test_sales_api()