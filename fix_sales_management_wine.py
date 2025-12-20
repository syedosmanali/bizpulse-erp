#!/usr/bin/env python3
"""
Fix the sales_management_wine.html template to use the working API
"""

def fix_template():
    print("🔧 Fixing sales_management_wine.html template...")
    
    # Read the current template
    with open('templates/sales_management_wine.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the script section and replace the loadSales function
    new_load_sales = '''        async function loadSales() {
            try {
                console.log('📅 Loading sales data with proper date filtering...');
                
                // Get current filter
                const dateRange = document.getElementById('dateRange')?.value || 'today';
                console.log('🔧 Current filter:', dateRange);
                
                // Build API URL with proper parameters
                const params = new URLSearchParams();
                params.append('filter', dateRange);
                
                // Add custom date range if selected
                if (dateRange === 'custom') {
                    const fromDate = document.getElementById('fromDate')?.value;
                    const toDate = document.getElementById('toDate')?.value;
                    
                    if (fromDate && toDate) {
                        params.append('startDate', fromDate);
                        params.append('endDate', toDate);
                    } else {
                        console.log('⚠️ Custom range selected but dates not provided');
                        return;
                    }
                }
                
                // Call the working API endpoint
                const response = await fetch(`/api/sales/all?${params.toString()}`);
                const data = await response.json();
                
                console.log('📊 API Response:', data);
                
                if (data.success && data.sales) {
                    allSales = data.sales;
                    filteredSales = data.sales;
                    
                    console.log(`📦 Loaded ${allSales.length} sales records`);
                    console.log(`💰 Total Sales: ₹${data.summary?.total_sales || 0}`);
                    
                    renderSales();
                    updateStats(data.summary);
                    updatePagination();
                } else {
                    console.error('❌ API Error:', data.error);
                    showEmptyState();
                }
                
            } catch (error) {
                console.error('❌ Error loading sales:', error);
                showError();
            }
        }'''
    
    # Replace the loadSales function
    import re
    
    # Find and replace the loadSales function
    pattern = r'async function loadSales\(\) \{.*?\n        \}'
    content = re.sub(pattern, new_load_sales, content, flags=re.DOTALL)
    
    # Replace the filterSales function with a simple version
    new_filter_sales = '''        function filterSales() {
            // Simply reload data with current filter - let the API handle the filtering
            loadSales();
        }'''
    
    # Find and replace filterSales function
    pattern = r'function filterSales\(\) \{.*?\n        \}'
    content = re.sub(pattern, new_filter_sales, content, flags=re.DOTALL)
    
    # Write the fixed template
    with open('templates/sales_management_wine.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Template fixed successfully!")
    print("📋 Changes made:")
    print("   - Updated loadSales() to use /api/sales/all")
    print("   - Simplified filterSales() to reload data")
    print("   - Removed hardcoded dates")
    print("   - Added proper API parameter handling")

if __name__ == "__main__":
    fix_template()