import requests
import json

def test_dashboard_api():
    """Test the dashboard API to verify receivables and profit calculations"""
    try:
        print("Testing Dashboard API...")
        response = requests.get('http://localhost:5000/api/dashboard/stats', timeout=10)
        data = response.json()
        
        print("Dashboard API Response:")
        print(json.dumps(data, indent=2))
        
        # Check if the new fields are present
        required_fields = [
            'today_sales', 'today_revenue', 'today_profit', 'today_orders',
            'total_receivable', 'total_pending_bills', 'total_receivable_profit'
        ]
        
        print("\nField Validation:")
        for field in required_fields:
            if field in data:
                print(f"✅ {field}: {data[field]}")
            else:
                print(f"❌ {field}: MISSING")
                
    except Exception as e:
        print(f"Error testing dashboard API: {e}")

def test_sales_api():
    """Test the sales API to verify profit calculation"""
    try:
        print("\nTesting Sales API...")
        response = requests.get('http://localhost:5000/api/sales/all?filter=today', timeout=10)
        data = response.json()
        
        print("Sales API Response Summary:")
        if 'summary' in data:
            summary = data['summary']
            print(json.dumps(summary, indent=2))
            
            # Check profit calculation
            if 'total_profit' in summary and 'total_cost' in summary:
                print(f"\nProfit Calculation Verification:")
                print(f"Total Revenue: ₹{summary.get('total_revenue', 0)}")
                print(f"Total Cost: ₹{summary.get('total_cost', 0)}")
                print(f"Calculated Profit: ₹{summary.get('total_profit', 0)}")
                print(f"Profit Margin: {summary.get('profit_margin', 0)}%")
            else:
                print("❌ Profit calculation fields missing")
        else:
            print("❌ No summary in sales API response")
            
    except Exception as e:
        print(f"Error testing sales API: {e}")

if __name__ == "__main__":
    test_dashboard_api()
    test_sales_api()