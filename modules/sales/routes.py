"""
Sales routes - Handle all sales API endpoints
"""

print("=" * 80)
print("🔥 SALES ROUTES LOADED - VERSION 3.0 - FIXED")
print("=" * 80)

from flask import Blueprint, request, jsonify, session
from .service import SalesService
from datetime import datetime, timedelta

sales_bp = Blueprint('sales', __name__)
sales_service = SalesService()

def get_user_id_from_session():
    """Get user_id from session for filtering data"""
    user_type = session.get('user_type')
    if user_type == 'employee':
        return session.get('client_id')
    else:
        return session.get('user_id')

@sales_bp.route('/api/sales', methods=['GET'])
def get_sales():
    """Get all sales with optional date filtering - Filtered by user - Returns array for mobile"""
    try:
        date_filter = request.args.get('date_filter', 'today')  # Default to today
        user_id = get_user_id_from_session()
        
        sales = sales_service.get_all_sales(date_filter, user_id)
        summary = sales_service.get_sales_summary(date_filter, user_id)
        
        print(f"📊 [SALES API] Returning {len(sales)} sales for filter: {date_filter}")
        
        # Return sales array directly for mobile frontend compatibility
        return jsonify(sales)
        
    except Exception as e:
        print(f"❌ [SALES API] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify([]), 500

@sales_bp.route('/api/sales/all', methods=['GET'])
def get_all_sales():
    """Get all sales with date range filtering - for frontend compatibility - Filtered by user"""
    print("🔍 [SALES ROUTE] Version 2.0 - WITH JSON CLEANING")
    try:
        from_date = request.args.get('from') or request.args.get('startDate')
        to_date = request.args.get('to') or request.args.get('endDate')
        date_filter = request.args.get('filter')  # today, yesterday, week, month
        payment_method = request.args.get('payment_method')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 15, type=int)  # Default 15 per page
        user_id = get_user_id_from_session()
        
        # DEBUG: Log session info
        print(f"🔍 [SALES API] Session user_id: {user_id}")
        print(f"🔍 [SALES API] Session user_type: {session.get('user_type')}")
        print(f"🔍 [SALES API] Date filter: {date_filter}")
        
        # Use date_filter if provided, otherwise use date range
        if date_filter and date_filter in ['today', 'yesterday', 'week', 'month', 'all']:
            sales = sales_service.get_all_sales(date_filter, user_id)
            summary = sales_service.get_sales_summary(date_filter, user_id)
        elif from_date or to_date:
            sales = sales_service.get_sales_by_date_range(from_date, to_date, 10000, user_id)  # Get all, paginate later
            summary = sales_service.get_sales_summary(None, user_id)
        else:
            # Default to all sales
            sales = sales_service.get_all_sales('all', user_id)
            summary = sales_service.get_sales_summary('all', user_id)
        
        print(f"🔍 [SALES API] Found {len(sales)} sales")
        print(f"🔍 [SALES API] Summary: {summary}")
        
        # CRITICAL FIX: Convert all non-JSON-serializable objects to strings
        def clean_for_json(obj):
            if isinstance(obj, dict):
                return {k: clean_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_for_json(item) for item in obj]
            elif isinstance(obj, (str, int, float, bool, type(None))):
                return obj
            else:
                return str(obj)
        
        sales = clean_for_json(sales)
        summary = clean_for_json(summary)
        
        # Filter by payment method if specified
        if payment_method and payment_method != 'all':
            sales = [s for s in sales if s.get('payment_method') == payment_method]
        
        # Calculate pagination
        total_records = len(sales)
        total_pages = max(1, (total_records + per_page - 1) // per_page)
        
        # Ensure page is within valid range
        page = max(1, min(page, total_pages))
        
        # Slice data for current page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_sales = sales[start_idx:end_idx]
        
        # Return both 'bills' and 'sales' for frontend compatibility
        return jsonify({
            "success": True,
            "sales": paginated_sales,
            "bills": paginated_sales,  # Frontend expects 'bills'
            "summary": {
                "total_sales": summary.get('total_revenue', 0),  # Frontend expects this for revenue
                "total_bills": summary.get('total_sales', 0),    # Frontend expects this for count
                "total_revenue": summary.get('total_revenue', 0),
                "total_items": summary.get('total_items', 0),
                "avg_sale_value": summary.get('avg_sale_value', 0),
                "net_profit": summary.get('total_profit', 0),  # Actual profit calculation
                "receivable": summary.get('total_receivables', 0),
                "receivable_profit": summary.get('total_receivables', 0),
                "total_cost": summary.get('total_cost', 0),
                "profit_margin": summary.get('profit_margin', 0)
            },
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_records": total_records,
                "per_page": per_page,
                "has_prev": page > 1,
                "has_next": page < total_pages
            },
            "filters": {
                "date_filter": date_filter,
                "from_date": from_date,
                "to_date": to_date,
                "payment_method": payment_method
            },
            "total_count": total_records,
            "total_records": total_records
        })
        
    except Exception as e:
        print(f"❌ [SALES API] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Failed to get sales: {str(e)}",
            "sales": [],
            "bills": [],
            "summary": {},
            "pagination": {"current_page": 1, "total_pages": 1, "total_records": 0}
        }), 500

@sales_bp.route('/api/sales/refresh', methods=['POST'])
def refresh_sales():
    """Refresh sales data - for frontend compatibility"""
    try:
        data = request.json or {}
        from_date = data.get('from_date')
        to_date = data.get('to_date')
        
        sales = sales_service.get_sales_by_date_range(from_date, to_date, 500)
        summary = sales_service.get_sales_summary()
        
        return jsonify({
            "success": True,
            "sales": sales,
            "summary": summary,
            "total_count": len(sales)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to refresh sales: {str(e)}"
        }), 500

@sales_bp.route('/api/sales/export', methods=['GET'])
def export_sales():
    """Export sales data - for frontend compatibility"""
    try:
        from flask import session
        
        date_range = request.args.get('date_range', 'today')
        payment_method = request.args.get('payment_method', 'all')
        format_type = request.args.get('format', 'json')
        
        # Get user_id from session for filtering
        user_type = session.get('user_type')
        if user_type == 'employee':
            user_id = session.get('client_id')
        else:
            user_id = session.get('user_id')
        
        # Map date_range to date_filter
        date_filter = date_range if date_range in ['today', 'yesterday', 'week', 'month'] else None
        
        sales = sales_service.get_all_sales(date_filter, user_id)
        
        # Filter by payment method if specified
        if payment_method and payment_method != 'all':
            sales = [s for s in sales if s.get('payment_method') == payment_method]
        
        # If WhatsApp format requested, generate Excel file and share
        if format_type == 'whatsapp':
            return handle_whatsapp_export(sales, date_range)
        
        return jsonify({
            "success": True,
            "sales": sales,
            "total_count": len(sales),
            "export_format": format_type
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to export sales: {str(e)}"
        }), 500


def handle_whatsapp_export(sales, date_range):
    """Generate Excel file and share via WhatsApp"""
    try:
        from datetime import datetime
        import os
        import csv
        import io
        
        print(f"🔍 [WhatsApp Export] Processing {len(sales)} sales for {date_range}")
        
        # Calculate totals
        total_amount = sum(float(sale.get('total_amount', 0)) for sale in sales)
        total_sales = len(sales)
        
        print(f"📊 [WhatsApp Export] Total: {total_sales} sales, Amount: ₹{total_amount}")
        
        # Create CSV content (Excel compatible)
        filename = f"sales_report_{date_range}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join('static', 'temp', filename)
        
        # Create temp directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Write CSV file
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header information
            writer.writerow(['SALES REPORT'])
            writer.writerow([f'Period: {date_range.title()}'])
            writer.writerow([f'Generated: {datetime.now().strftime("%d/%m/%Y at %H:%M")}'])
            writer.writerow([])  # Empty row
            
            # Write summary
            writer.writerow(['SUMMARY'])
            writer.writerow(['Total Sales', total_sales])
            writer.writerow(['Total Amount', f'₹{total_amount:,.2f}'])
            writer.writerow([])  # Empty row
            
            # Write table headers
            writer.writerow(['SALES DETAILS'])
            writer.writerow(['Bill No.', 'Customer', 'Amount', 'Payment Method', 'Date', 'Time'])
            
            # Write sales data
            for sale in sales:
                customer_name = sale.get('customer_name', 'Walk-in Customer')
                
                # Format date and time
                created_at = sale.get('created_at', '')
                if created_at:
                    try:
                        date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        formatted_date = date_obj.strftime('%d/%m/%Y')
                        formatted_time = date_obj.strftime('%H:%M')
                    except:
                        formatted_date = 'N/A'
                        formatted_time = 'N/A'
                else:
                    formatted_date = 'N/A'
                    formatted_time = 'N/A'
                
                writer.writerow([
                    sale.get('bill_number', 'N/A'),
                    customer_name,
                    f'₹{float(sale.get("total_amount", 0)):,.2f}',
                    sale.get('payment_method', 'Cash').upper(),
                    formatted_date,
                    formatted_time
                ])
        
        print(f"📄 [WhatsApp Export] Excel file created: {filepath}")
        
        # Generate URLs
        file_url = f"{request.host_url}static/temp/{filename}"
        
        # Create WhatsApp message
        whatsapp_text = f"""📊 *Sales Report - {date_range.title()}*

📈 *Summary:*
• Total Sales: {total_sales}
• Total Amount: ₹{total_amount:,.2f}
• Period: {date_range.title()}

📄 *Download Excel File:*
{file_url}

Generated on {datetime.now().strftime('%d/%m/%Y at %H:%M')}

_Open the file in Excel or Google Sheets_"""
        
        # URL encode the message
        import urllib.parse
        encoded_message = urllib.parse.quote(whatsapp_text)
        whatsapp_url = f"https://wa.me/?text={encoded_message}"
        
        print(f"✅ [WhatsApp Export] Success! File URL: {file_url}")
        
        return jsonify({
            "success": True,
            "message": "Excel file generated successfully",
            "file_url": file_url,
            "whatsapp_url": whatsapp_url,
            "total_sales": total_sales,
            "total_amount": total_amount,
            "filename": filename
        })
        
    except Exception as e:
        print(f"❌ [WhatsApp Export] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Failed to generate Excel file: {str(e)}"
        }), 500

@sales_bp.route('/api/sales/summary', methods=['GET'])
def get_sales_summary():
    """Get sales summary with totals - Mobile ERP format with today/yesterday breakdown"""
    try:
        # Get today's summary
        today_summary = sales_service.get_sales_summary('today')
        
        # Get yesterday's summary
        yesterday_summary = sales_service.get_sales_summary('yesterday')
        
        # Get top products for today
        top_products = sales_service.get_top_products(5, 'today')
        
        # Format response for mobile frontend
        return jsonify({
            "success": True,
            "today": {
                "total": today_summary.get('total_revenue', 0),
                "count": today_summary.get('total_sales', 0),
                "items": today_summary.get('total_items', 0)
            },
            "yesterday": {
                "total": yesterday_summary.get('total_revenue', 0),
                "count": yesterday_summary.get('total_sales', 0),
                "items": yesterday_summary.get('total_items', 0)
            },
            "top_products": top_products,
            "summary": today_summary  # Keep for backward compatibility
        })
        
    except Exception as e:
        print(f"❌ [SALES SUMMARY] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Failed to get sales summary: {str(e)}",
            "today": {"total": 0, "count": 0, "items": 0},
            "yesterday": {"total": 0, "count": 0, "items": 0},
            "top_products": []
        }), 500

@sales_bp.route('/api/sales/top-products', methods=['GET'])
def get_top_products():
    """Get top selling products"""
    try:
        limit = int(request.args.get('limit', 10))
        date_filter = request.args.get('date_filter')
        
        products = sales_service.get_top_products(limit, date_filter)
        
        return jsonify({
            "success": True,
            "top_products": products,
            "limit": limit,
            "date_filter": date_filter
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get top products: {str(e)}"
        }), 500

@sales_bp.route('/api/sales/chart', methods=['GET'])
def get_sales_chart():
    """Get daily sales data for chart"""
    try:
        days = int(request.args.get('days', 7))
        
        chart_data = sales_service.get_daily_sales_chart(days)
        
        return jsonify({
            "success": True,
            "chart_data": chart_data,
            "days": days
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get chart data: {str(e)}"
        }), 500

@sales_bp.route('/api/sales/health', methods=['GET'])
def check_sales_health():
    """Check if sales data is being stored properly"""
    try:
        health = sales_service.check_database_health()
        
        return jsonify({
            "success": True,
            "health": health,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to check health: {str(e)}"
        }), 500

@sales_bp.route('/api/sales/today', methods=['GET'])
def get_today_sales():
    """Get today's sales - Quick endpoint"""
    try:
        sales = sales_service.get_all_sales('today')
        summary = sales_service.get_sales_summary('today')
        
        return jsonify({
            "success": True,
            "today_sales": sales,
            "today_summary": summary,
            "date": datetime.now().strftime('%Y-%m-%d')
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get today's sales: {str(e)}"
        }), 500

@sales_bp.route('/api/sales/yesterday', methods=['GET'])
def get_yesterday_sales():
    """Get yesterday's sales - Quick endpoint"""
    try:
        sales = sales_service.get_all_sales('yesterday')
        summary = sales_service.get_sales_summary('yesterday')
        
        return jsonify({
            "success": True,
            "yesterday_sales": sales,
            "yesterday_summary": summary,
            "date": (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get yesterday's sales: {str(e)}"
        }), 500