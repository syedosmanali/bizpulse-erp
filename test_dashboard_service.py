import sys
import os
sys.path.append(os.getcwd())

# Test the dashboard service directly
try:
    from modules.dashboard.service import DashboardService
    
    print("Testing DashboardService...")
    data = DashboardService.get_dashboard_data()
    print("Success!")
    print(f"Keys in data: {data.keys()}")
    
    sales_stats = data.get('sales_stats', {})
    print(f"Sales stats keys: {sales_stats.keys()}")
    
    today_stats = sales_stats.get('today', {})
    print(f"Today stats: {today_stats}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()