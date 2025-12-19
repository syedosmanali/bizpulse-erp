#!/usr/bin/env python3
"""
Fix mobile dashboard loading issue
"""

def fix_mobile_dashboard():
    """Fix the mobile dashboard loading issue"""
    
    print("🔧 Fixing Mobile Dashboard Loading Issue...")
    print("=" * 50)
    
    # Read the current mobile template
    try:
        with open('templates/mobile_simple_working.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("✅ Read mobile template successfully")
        
        # Add error handling and debugging to the loadDashboard function
        dashboard_fix = '''
        async function loadDashboard() {
            console.log('📊 Loading dashboard...');
            
            try {
                // Show loading indicator
                const loadingIndicator = document.createElement('div');
                loadingIndicator.id = 'dashboardLoading';
                loadingIndicator.innerHTML = '<div style="text-align: center; padding: 20px; color: #732C3F;">Loading dashboard... 📊</div>';
                const mainContent = document.getElementById('mainContent');
                if (mainContent) {
                    mainContent.insertBefore(loadingIndicator, mainContent.firstChild);
                }
                
                // Products with better error handling
                console.log('📦 Fetching products...');
                let products = [];
                try {
                    products = await apiCall('/api/products');
                    document.getElementById('totalProducts').textContent = products.length;
                    console.log(`✅ Products loaded: ${products.length}`);
                } catch (error) {
                    console.error('❌ Products API failed:', error);
                    document.getElementById('totalProducts').textContent = '0';
                }
                
                // Customers with better error handling
                console.log('👥 Fetching customers...');
                let customers = [];
                try {
                    customers = await apiCall('/api/customers');
                    document.getElementById('totalCustomers').textContent = customers.length;
                    console.log(`✅ Customers loaded: ${customers.length}`);
                } catch (error) {
                    console.error('❌ Customers API failed:', error);
                    document.getElementById('totalCustomers').textContent = '0';
                }
                
                // Sales with better error handling
                console.log('💰 Fetching sales...');
                let sales = {};
                try {
                    sales = await apiCall('/api/sales/summary');
                    document.getElementById('totalSales').textContent = '₹' + (sales.today?.total || 0).toFixed(0);
                    document.getElementById('totalBills').textContent = sales.today?.count || 0;
                    console.log(`✅ Sales loaded: ₹${sales.today?.total || 0}`);
                } catch (error) {
                    console.error('❌ Sales API failed:', error);
                    document.getElementById('totalSales').textContent = '₹0';
                    document.getElementById('totalBills').textContent = '0';
                }
                
                // Remove loading indicator
                const loading = document.getElementById('dashboardLoading');
                if (loading) loading.remove();
                
                console.log('✅ Dashboard loaded successfully!');
                
                // Load advanced modules based on user role
                loadAdvancedModules();
                
            } catch (error) {
                console.error('❌ Dashboard error:', error);
                
                // Remove loading indicator
                const loading = document.getElementById('dashboardLoading');
                if (loading) loading.remove();
                
                // Show user-friendly error
                const errorDiv = document.createElement('div');
                errorDiv.innerHTML = `
                    <div style="background: #ffebee; color: #c62828; padding: 15px; margin: 10px; border-radius: 10px; text-align: center;">
                        <h3>⚠️ Dashboard Loading Failed</h3>
                        <p>Please check:</p>
                        <ul style="text-align: left; margin: 10px 0;">
                            <li>Server is running</li>
                            <li>Same WiFi network</li>
                            <li>Correct IP address</li>
                        </ul>
                        <button onclick="location.reload()" style="background: #732C3F; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">
                            🔄 Retry
                        </button>
                    </div>
                `;
                const mainContent = document.getElementById('mainContent');
                if (mainContent) {
                    mainContent.insertBefore(errorDiv, mainContent.firstChild);
                }
            }
        }'''
        
        # Find and replace the loadDashboard function
        import re
        
        # Pattern to match the loadDashboard function
        pattern = r'async function loadDashboard\(\) \{.*?\n        \}'
        
        if re.search(pattern, content, re.DOTALL):
            # Replace the function
            content = re.sub(pattern, dashboard_fix.strip(), content, flags=re.DOTALL)
            
            # Write back to file
            with open('templates/mobile_simple_working.html', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Fixed loadDashboard function with better error handling")
            print("✅ Added loading indicator and user-friendly error messages")
            print("✅ Mobile dashboard should now work better!")
            
        else:
            print("❌ Could not find loadDashboard function to replace")
            
    except Exception as e:
        print(f"❌ Error fixing mobile dashboard: {e}")
    
    print("\n" + "=" * 50)
    print("🚀 Next Steps:")
    print("1. Restart your Flask server: python app.py")
    print("2. Open mobile app and try logging in")
    print("3. Check browser console (F12) for detailed logs")
    print("4. If still issues, run: python test_mobile_dashboard_fix.py")

if __name__ == "__main__":
    fix_mobile_dashboard()