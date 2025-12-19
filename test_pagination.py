#!/usr/bin/env python3
"""
Test script to verify invoice pagination is working correctly
"""
import requests
import json

def test_pagination():
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Invoice Pagination API...")
    print("=" * 50)
    
    # Test 1: Get first page
    print("\n📄 Test 1: First page (10 items)")
    response = requests.get(f"{base_url}/api/invoices?page=1&per_page=10")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"📊 Total Records: {data['pagination']['total_records']}")
        print(f"📄 Total Pages: {data['pagination']['total_pages']}")
        print(f"📋 Current Page: {data['pagination']['current_page']}")
        print(f"📦 Items on this page: {len(data['invoices'])}")
        print(f"🔄 Has Next: {data['pagination']['has_next']}")
        print(f"🔄 Has Previous: {data['pagination']['has_prev']}")
        
        if data['invoices']:
            print(f"🧾 First Invoice: {data['invoices'][0]['bill_number']}")
            print(f"💰 Amount: ₹{data['invoices'][0]['total_amount']}")
    else:
        print(f"❌ Error: {response.status_code}")
        return
    
    # Test 2: Get second page if available
    if data['pagination']['has_next']:
        print("\n📄 Test 2: Second page")
        response2 = requests.get(f"{base_url}/api/invoices?page=2&per_page=10")
        
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"✅ Status: {response2.status_code}")
            print(f"📋 Current Page: {data2['pagination']['current_page']}")
            print(f"📦 Items on this page: {len(data2['invoices'])}")
            
            if data2['invoices']:
                print(f"🧾 First Invoice: {data2['invoices'][0]['bill_number']}")
        else:
            print(f"❌ Error: {response2.status_code}")
    else:
        print("\n📄 Test 2: No second page available")
    
    # Test 3: Test with filters
    print("\n📄 Test 3: With status filter")
    response3 = requests.get(f"{base_url}/api/invoices?page=1&per_page=10&status=completed")
    
    if response3.status_code == 200:
        data3 = response3.json()
        print(f"✅ Status: {response3.status_code}")
        print(f"📊 Filtered Records: {data3['pagination']['total_records']}")
        print(f"📦 Items on this page: {len(data3['invoices'])}")
        
        if data3['invoices']:
            statuses = [inv['status'] for inv in data3['invoices']]
            print(f"📋 Statuses: {set(statuses)}")
    else:
        print(f"❌ Error: {response3.status_code}")
    
    print("\n🎉 Pagination tests completed!")

if __name__ == "__main__":
    try:
        test_pagination()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server. Make sure the Flask app is running on localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")