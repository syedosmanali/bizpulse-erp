import requests
import json

def test_existing_cheque_flow():
    """Test the cheque flow with existing data"""
    print("=== TESTING EXISTING CHEQUE FLOW ===")
    
    # Get existing credit history
    print("\n1. Getting existing credit history...")
    try:
        response = requests.get('http://localhost:5000/api/credit/history')
        if response.status_code == 200:
            data = response.json()
            cheque_bills = [b for b in data['bills'] if b['payment_method'] == 'CHEQUE']
            print(f"✅ Found {len(cheque_bills)} cheque bills")
            
            if cheque_bills:
                test_bill = cheque_bills[0]
                print(f"Using bill: {test_bill['bill_number']}")
                print(f"Customer: {test_bill['customer_name']}")
                print(f"Amount: ₹{test_bill['total_amount']}")
                print(f"Status: {test_bill['payment_status']}")
                print(f"Created: {test_bill['created_at']}")
            else:
                print("❌ No cheque bills found")
                return
        else:
            print(f"❌ Failed to get credit history: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error getting credit history: {e}")
        return
    
    # Test 2: Check dashboard stats
    print("\n2. Checking dashboard stats...")
    try:
        response = requests.get('http://localhost:5000/api/dashboard/stats')
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Dashboard stats:")
            print(f"   Sales: ₹{stats.get('today_sales', 0)}")
            print(f"   Revenue: ₹{stats.get('today_revenue', 0)}")
            print(f"   Orders: {stats.get('today_orders', 0)}")
            print(f"   Profit: ₹{stats.get('today_profit', 0)}")
            
            # Verify sales vs revenue logic
            sales = stats.get('today_sales', 0)
            revenue = stats.get('today_revenue', 0)
            if sales >= revenue:
                print("✅ Sales vs Revenue logic is working correctly")
                if sales > revenue:
                    print("   (Sales > Revenue as expected for credit transactions)")
                else:
                    print("   (Sales = Revenue - all transactions are cash)")
            else:
                print("❌ Sales vs Revenue logic has issues")
        else:
            print(f"❌ Failed to get dashboard stats: {response.text}")
    except Exception as e:
        print(f"❌ Error getting dashboard stats: {e}")
    
    # Test 3: Test cheque bounced functionality
    print("\n3. Testing cheque bounced functionality...")
    try:
        # Find a cheque deposited bill (if any)
        cheque_deposited_bills = [b for b in data['bills'] if b['payment_status'] == 'cheque_deposited']
        
        if cheque_deposited_bills:
            test_bill = cheque_deposited_bills[0]
            print(f"Testing bounced on: {test_bill['bill_number']}")
            
            bounce_response = requests.post('http://localhost:5000/api/credit/cheque-cleared', 
                                          json={'bill_id': test_bill['id'], 'action': 'bounced'})
            
            if bounce_response.status_code == 200:
                bounce_data = bounce_response.json()
                print(f"✅ Bounced successfully:")
                print(f"   Message: {bounce_data.get('message')}")
                print(f"   New Status: {bounce_data.get('new_status')}")
                print(f"   Bill Status: {bounce_data.get('bill_status', 'Not provided')}")
            else:
                print(f"❌ Bounce failed: {bounce_response.text}")
        else:
            print("ℹ️ No cheque deposited bills found for bounce testing")
    except Exception as e:
        print(f"❌ Error testing bounce: {e}")
    
    # Test 4: Verify sales module status display
    print("\n4. Checking sales module status display...")
    try:
        response = requests.get('http://localhost:5000/api/retail/sales')
        if response.status_code == 200:
            sales_data = response.json()
            initiated_bills = [b for b in sales_data.get('bills', []) if b.get('status') == 'initiated']
            completed_bills = [b for b in sales_data.get('bills', []) if b.get('status') == 'completed']
            
            print(f"✅ Sales module status summary:")
            print(f"   Initiated bills: {len(initiated_bills)}")
            print(f"   Completed bills: {len(completed_bills)}")
            
            # Show some examples
            if initiated_bills:
                print("   Sample initiated bills:")
                for bill in initiated_bills[:3]:
                    print(f"     - {bill['bill_number']}: {bill['customer_name']} (₹{bill['total_amount']})")
            
            if completed_bills:
                print("   Sample completed bills:")
                for bill in completed_bills[:3]:
                    print(f"     - {bill['bill_number']}: {bill['customer_name']} (₹{bill['total_amount']})")
        else:
            print(f"❌ Failed to get sales data: {response.text}")
    except Exception as e:
        print(f"❌ Error getting sales data: {e}")

if __name__ == "__main__":
    test_existing_cheque_flow()