import requests
import json
from datetime import datetime, timedelta

def test_dashboard_separation():
    """Test that sales and revenue are properly separated"""
    print("=== TESTING SALES vs REVENUE SEPARATION ===\n")
    
    # Get today's dashboard stats
    try:
        response = requests.get('http://localhost:5000/api/dashboard/stats')
        data = response.json()
        
        if not data.get('success'):
            print(f"❌ Failed to get dashboard stats: {data.get('error')}")
            return
            
        stats = data.get('data', {})
        today_stats = stats.get('today', {})
        
        print("📊 TODAY'S DASHBOARD STATS:")
        print(f"   Sales (Total Orders): ₹{today_stats.get('sales', 0):,.2f}")
        print(f"   Revenue (Payments): ₹{today_stats.get('revenue', 0):,.2f}")
        print(f"   Profit: ₹{today_stats.get('profit', 0):,.2f}")
        print(f"   Orders: {today_stats.get('transactions', 0)}")
        print()
        
        # Check the separation logic
        sales = today_stats.get('sales', 0)
        revenue = today_stats.get('revenue', 0)
        
        if sales >= revenue:
            print("✅ Sales >= Revenue (Correct - Sales includes all orders, Revenue only paid amounts)")
        else:
            print("❌ Sales < Revenue (Incorrect - Sales should always be >= Revenue)")
            
        if revenue > 0:
            print("✅ Revenue is being calculated (payments are being tracked)")
        else:
            print("⚠️  No revenue recorded today")
            
        print()
        print("💡 Expected Behavior:")
        print("   - Sales: Total value of all bills created today (credit + cash)")
        print("   - Revenue: Only money actually received today (payments processed)")
        print("   - Credit bills should show in Sales immediately but not in Revenue until paid")
        
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")

def test_credit_payment_timing():
    """Test that credit payments are counted on payment date, not billing date"""
    print("\n=== TESTING CREDIT PAYMENT TIMING ===\n")
    
    try:
        # Get credit history to see payment dates
        response = requests.get('http://localhost:5000/api/credit/history?date_range=all')
        data = response.json()
        
        if not data.get('success'):
            print(f"❌ Failed to get credit history: {data.get('error')}")
            return
            
        bills = data.get('bills', [])
        credit_bills = [b for b in bills if b.get('is_credit', False)]
        
        print(f"Found {len(credit_bills)} credit bills:")
        
        for bill in credit_bills[:3]:  # Show first 3
            print(f"   Bill {bill['bill_number']}:")
            print(f"     - Created: {bill['created_at']}")
            print(f"     - Status: {bill['payment_status']}")
            print(f"     - Total: ₹{bill['total_amount']}")
            print(f"     - Paid: ₹{bill['paid_amount']}")
            print(f"     - Balance: ₹{bill['balance_due']}")
            print()
            
        print("💡 To verify timing separation:")
        print("   1. Create a credit bill today - should show in Sales but not Revenue")
        print("   2. Receive payment tomorrow - should show in tomorrow's Revenue/Profit")
        print("   3. Sales should remain unchanged when payment is received")
        
    except Exception as e:
        print(f"❌ Error testing credit timing: {e}")

if __name__ == "__main__":
    test_dashboard_separation()
    test_credit_payment_timing()
    print("\n=== TEST COMPLETE ===")