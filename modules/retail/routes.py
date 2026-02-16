"""
Retail management routes
COPIED AS-IS from app.py
"""

from flask import Blueprint, render_template, jsonify, session
from modules.shared.auth_decorators import require_auth
from .service import RetailService
from datetime import datetime, timedelta

retail_bp = Blueprint('retail', __name__)
retail_service = RetailService()

def get_user_id_from_session():
    """Get user_id from session for filtering data"""
    user_type = session.get('user_type')
    if user_type == 'employee':
        return session.get('client_id')
    else:
        return session.get('user_id')

# Retail Management module routes
@retail_bp.route('/retail/products')
def retail_products_page():
    return render_template('retail_products.html')

@retail_bp.route('/retail/customers')
def retail_customers():
    return render_template('retail_customers.html')

@retail_bp.route('/retail/billing')
def retail_billing():
    return render_template('retail_billing.html')

@retail_bp.route('/retail/billing-test')
def retail_billing_test():
    return "<h1>✅ Billing Route Working!</h1><p>This is a test route to verify billing is accessible.</p>"

@retail_bp.route('/retail/inventory')
def retail_inventory():
    return render_template('inventory_dashboard_redesigned.html')

@retail_bp.route('/retail/dashboard')
def retail_dashboard():
    from flask import session
    from modules.user_management.service import UserManagementService
    
    # Get user permissions if employee
    user_permissions = {}
    if session.get('user_type') in ['employee', 'staff', 'client_user']:
        user_service = UserManagementService()
        result = user_service.get_current_user_permissions(session.get('user_id'))
        if result.get('success'):
            user_permissions = result.get('permissions', {})
    
    return render_template('retail_dashboard.html', user_permissions=user_permissions)

@retail_bp.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get comprehensive dashboard statistics with real-time data - Filtered by user"""
    try:
        print("🔍 [ROUTE] Dashboard stats route called")
        user_id = get_user_id_from_session()
        print(f"🔍 [ROUTE] User ID: {user_id}")
        result = retail_service.get_dashboard_stats(user_id)
        print(f"🔍 [ROUTE] Service result: {result}")
        return jsonify(result)
        
    except Exception as e:
        print(f"Error getting dashboard stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@retail_bp.route('/api/dashboard/activity', methods=['GET'])
def get_dashboard_activity():
    """Get recent activity for dashboard - Filtered by user"""
    try:
        user_id = get_user_id_from_session()
        result = retail_service.get_recent_activity(user_id)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error getting dashboard activity: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@retail_bp.route('/retail/profile')
def retail_profile():
    return render_template('retail_profile_professional.html')

@retail_bp.route('/test-reports')
def test_reports():
    return "<h1>🎉 Reports Module Working!</h1><p>Route is active!</p><a href='/retail/dashboard'>Back to Dashboard</a>"

@retail_bp.route('/retail/sales')
def retail_sales():
    # Add cache busting headers
    from flask import make_response
    response = make_response(render_template('retail_sales_professional.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@retail_bp.route('/retail/test-sales-api')
def test_sales_api():
    """Test page to verify sales API is working"""
    from flask import make_response
    response = make_response(render_template('test_sales_api.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@retail_bp.route('/retail/debug-sales')
def debug_sales():
    """Debug page to troubleshoot sales display issue"""
    from flask import make_response
    response = make_response(render_template('debug_sales.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@retail_bp.route('/retail/credit')
def retail_credit():
    return render_template('retail_credit_professional.html')

@retail_bp.route('/retail/sales-old')
def retail_sales_old():
    return render_template('retail_sales_enhanced.html')

@retail_bp.route('/retail/settings')
def retail_settings():
    return render_template('settings_professional.html')

@retail_bp.route('/retail/invoices')
def retail_invoices():
    try:
        return render_template('invoices_professional.html')
    except Exception as e:
        return f"<h1>❌ Invoice Template Error</h1><p>Error: {str(e)}</p><p>Template: invoices_professional.html</p><a href='/retail/dashboard'>Back to Dashboard</a>"

@retail_bp.route('/retail/invoices-test')
def retail_invoices_test():
    return "<h1>✅ Invoice Route Working!</h1><p>This is a test route to verify invoices are accessible.</p><a href='/retail/dashboard'>Back to Dashboard</a>"

@retail_bp.route('/retail/invoice/<invoice_id>')
def retail_invoice_detail(invoice_id):
    try:
        return render_template('retail_invoice_multi_theme.html', invoice_id=invoice_id)
    except Exception as e:
        return f"<h1>❌ Invoice Detail Template Error</h1><p>Error: {str(e)}</p><p>Template: retail_invoice_multi_theme.html</p><p>Invoice ID: {invoice_id}</p><a href='/retail/invoices'>Back to Invoices</a>"

@retail_bp.route('/retail/invoice-new/<invoice_id>')
def retail_invoice_new(invoice_id):
    """New multi-theme invoice template"""
    try:
        return render_template('retail_invoice_multi_theme.html', invoice_id=invoice_id)
    except Exception as e:
        return f"<h1>❌ Template Error</h1><p>Error: {str(e)}</p><p>Invoice ID: {invoice_id}</p>"

@retail_bp.route('/invoice-demo')
def invoice_demo():
    return render_template('invoice_demo.html')

@retail_bp.route('/invoice-test')
def invoice_test():
    """Invoice System Test Page"""
    return render_template('invoice_test_page.html')


# ============================================================================
# CREDIT MANAGEMENT ROUTES - Added directly to retail blueprint
# ============================================================================

@retail_bp.route('/api/credit/test', methods=['GET'])
def credit_test():
    """Test credit API"""
    return jsonify({
        'success': True,
        'message': 'Credit API working via retail blueprint!',
        'timestamp': datetime.now().isoformat()
    })

@retail_bp.route('/api/credit/bills/debug', methods=['GET'])
def get_credit_bills():
    """Get all credit bills - Filtered by user"""
    from flask import request
    from modules.shared.database import get_db_connection, get_db_type
    import traceback
    
    print("=" * 80)
    print("🔥 CREDIT API CALLED VIA RETAIL BLUEPRINT")
    print("=" * 80)
    
    try:
        # Get user_id for filtering
        user_id = get_user_id_from_session()
        print(f"🔍 [CREDIT] Filtering by user_id: {user_id}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get filter parameters
        status = request.args.get('status', 'all')
        customer = request.args.get('customer', 'all')
        date_range = request.args.get('date_range', 'all')
        
        print(f"📋 Filters: status={status}, customer={customer}, date_range={date_range}")
        
        db_type = get_db_type()
        
        # Use Python datetime for date filtering
        from datetime import datetime, timedelta
        today_str = datetime.now().strftime('%Y-%m-%d')
        yesterday_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        week_ago_str = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        month_ago_str = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Build query based on database type
        if db_type == 'postgresql':
            query = """
                SELECT 
                    b.id,
                    b.bill_number,
                    b.customer_name,
                    b.customer_id,
                    b.total_amount,
                    COALESCE(b.credit_paid_amount, b.partial_payment_amount, 0) as paid_amount,
                    COALESCE(b.credit_balance, b.total_amount - COALESCE(b.partial_payment_amount, 0), 0) as balance_due,
                    b.payment_method,
                    b.payment_status,
                    b.created_at,
                    b.is_credit,
                    COALESCE(b.customer_phone, c.phone) as customer_phone
                FROM bills b
                LEFT JOIN customers c ON b.customer_id = c.id
                WHERE (
                    (b.is_credit = TRUE AND b.credit_balance > 0)
                    OR (b.payment_method = 'partial' AND (b.total_amount - COALESCE(b.partial_payment_amount, 0)) > 0)
                    OR (b.payment_method = 'credit')
                )
            """
        else:
            query = """
                SELECT 
                    b.id,
                    b.bill_number,
                    b.customer_name,
                    b.customer_id,
                    b.total_amount,
                    COALESCE(b.credit_paid_amount, b.partial_payment_amount, 0) as paid_amount,
                    COALESCE(b.credit_balance, b.total_amount - COALESCE(b.partial_payment_amount, 0), 0) as balance_due,
                    b.payment_method,
                    b.payment_status,
                    b.created_at,
                    b.is_credit,
                    COALESCE(b.customer_phone, c.phone) as customer_phone
                FROM bills b
                LEFT JOIN customers c ON b.customer_id = c.id
                WHERE (
                    (b.is_credit = 1 AND b.credit_balance > 0)
                    OR (b.payment_method = 'partial' AND (b.total_amount - COALESCE(b.partial_payment_amount, 0)) > 0)
                    OR (b.payment_method = 'credit')
                )
            """
        
        params = []
        
        # Add user filtering
        if user_id:
            if db_type == 'postgresql':
                query += " AND (b.business_owner_id = %s OR b.business_owner_id IS NULL)"
            else:
                query += " AND (b.business_owner_id = ? OR b.business_owner_id IS NULL)"
            params.append(user_id)
        
        # Add date filter using Python-generated dates
        if date_range != 'all':
            if db_type == 'postgresql':
                if date_range == 'today':
                    query += f" AND CAST(b.created_at AS DATE) = '{today_str}'"
                elif date_range == 'yesterday':
                    query += f" AND CAST(b.created_at AS DATE) = '{yesterday_str}'"
                elif date_range == 'week':
                    query += f" AND CAST(b.created_at AS DATE) >= '{week_ago_str}'"
                elif date_range == 'month':
                    query += f" AND CAST(b.created_at AS DATE) >= '{month_ago_str}'"
            else:
                if date_range == 'today':
                    query += f" AND DATE(b.created_at) = '{today_str}'"
                elif date_range == 'yesterday':
                    query += f" AND DATE(b.created_at) = '{yesterday_str}'"
                elif date_range == 'week':
                    query += f" AND DATE(b.created_at) >= '{week_ago_str}'"
                elif date_range == 'month':
                    query += f" AND DATE(b.created_at) >= '{month_ago_str}'"
        
        # Add customer filter
        if customer != 'all':
            if db_type == 'postgresql':
                query += " AND b.customer_name = %s"
            else:
                query += " AND b.customer_name = ?"
            params.append(customer)
        
        # Add status filter
        if status != 'all':
            if status.lower() == 'unpaid':
                query += " AND b.payment_status = 'unpaid'"
            elif status.lower() == 'partial':
                query += " AND b.payment_status = 'partial'"
        
        query += " ORDER BY b.created_at DESC"
        
        print(f"🔍 Executing query with {len(params)} params...")
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        print(f"✅ Found {len(rows)} credit bills")
        
        bills = []
        for row in rows:
            paid_amount = float(row['paid_amount'] or 0)
            balance_due = float(row['balance_due'] or 0)
            total_amount = float(row['total_amount'] or 0)
            
            if balance_due == 0 and paid_amount < total_amount:
                balance_due = total_amount - paid_amount
            
            bills.append({
                'id': row['id'],
                'bill_number': row['bill_number'],
                'customer_name': row['customer_name'] or 'Walk-in Customer',
                'customer_id': row['customer_id'],
                'total_amount': total_amount,
                'paid_amount': paid_amount,
                'balance_due': balance_due,
                'remaining_amount': balance_due,
                'payment_method': row['payment_method'] or 'cash',
                'payment_status': row['payment_status'] or 'unpaid',
                'created_at': str(row['created_at']),
                'is_credit': row['is_credit'],
                'customer_phone': row['customer_phone'] or ''
            })
        
        total_credit = sum(bill['balance_due'] for bill in bills)
        total_paid = sum(bill['paid_amount'] for bill in bills)
        total_amount = sum(bill['total_amount'] for bill in bills)
        total_bills = len(bills)
        
        customers = list(set(bill['customer_name'] for bill in bills))
        
        print(f"💰 Total Credit: ₹{total_credit:.2f}")
        print(f"📊 Total Bills: {total_bills}")
        
        conn.close()
        
        return jsonify({
            'success': True,
            'bills': bills,
            'customers': customers,
            'summary': {
                'total_credit': round(total_credit, 2),
                'total_bills': total_bills,
                'total_customers': len(customers)
            },
            'stats': {
                'total_bills': total_bills,
                'pending_amount': round(total_credit, 2),
                'total_amount': round(total_amount, 2),
                'received_amount': round(total_paid, 2)
            }
        })
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'bills': [],
            'customers': [],
            'stats': {'total_bills': 0, 'pending_amount': 0, 'total_amount': 0, 'received_amount': 0}
        }), 500

@retail_bp.route('/api/credit/export', methods=['GET'])
def export_credit():
    """Export credit bills - Filtered by user"""
    from modules.shared.database import get_db_connection
    
    try:
        # 🔥 Get user_id for filtering
        user_id = get_user_id_from_session()
        print(f"🔍 [CREDIT EXPORT] Filtering by user_id: {user_id}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query with user filtering
        query = """
            SELECT 
                b.bill_number,
                b.customer_name,
                b.total_amount,
                b.credit_paid_amount,
                b.credit_balance,
                b.payment_status,
                b.created_at
            FROM bills b
            WHERE b.is_credit = 1 AND b.credit_balance > 0
        """
        
        params = []
        
        # 🔥 Add user filtering
        if user_id:
            query += " AND (b.business_owner_id = ? OR b.business_owner_id IS NULL)"
            params.append(user_id)
        
        query += " ORDER BY b.created_at DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        bills = []
        for row in rows:
            bills.append({
                'bill_number': row[0],
                'customer_name': row[1] or 'Walk-in Customer',
                'customer_phone': '',
                'total_amount': float(row[2] or 0),
                'paid_amount': float(row[3] or 0),
                'remaining_amount': float(row[4] or 0),
                'payment_status': row[5] or 'unpaid',
                'date': row[6]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': bills
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@retail_bp.route('/api/credit/cheque-cleared', methods=['POST'])
def mark_cheque_cleared():
    """Mark a cheque payment as cleared/received in bank"""
    from flask import request
    from modules.shared.database import get_db_connection, get_db_type
    import traceback
    
    try:
        data = request.json
        bill_id = data.get('bill_id')
        action = data.get('action', 'cleared')  # 'cleared' or 'bounced'
        
        if not bill_id:
            return jsonify({
                'success': False,
                'error': 'Invalid bill ID'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        db_type = get_db_type()
        
        # Get current bill details
        if db_type == 'postgresql':
            cursor.execute("""
                SELECT total_amount, credit_paid_amount, credit_balance, payment_status, bill_number, customer_name
                FROM bills
                WHERE id = %s
            """, (bill_id,))
        else:
            cursor.execute("""
                SELECT total_amount, credit_paid_amount, credit_balance, payment_status, bill_number, customer_name
                FROM bills
                WHERE id = ?
            """, (bill_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Bill not found'
            }), 404
        
        total_amount = float(row['total_amount'])
        current_paid = float(row['credit_paid_amount'] or 0)
        current_balance = float(row['credit_balance'] or 0)
        current_status = row['payment_status']
        bill_number = row['bill_number']
        customer_name = row['customer_name'] or 'Walk-in Customer'
        
        # Only process if status is cheque_deposited
        if current_status != 'cheque_deposited':
            return jsonify({
                'success': False,
                'error': 'Bill is not in cheque deposited status'
            }), 400
        
        if action == 'bounced':
            # Handle cheque bounce - revert the payment
            new_paid = 0.0
            new_balance = total_amount
            new_status = 'cheque_bounced'
            bill_status = 'initiated'  # Keep as initiated when bounced
            is_credit = True
            message = 'Cheque marked as bounced'
        else:
            # Handle cheque cleared
            if current_balance <= 0:
                new_status = 'paid'
                bill_status = 'completed'  # Change to completed when cleared
                is_credit = False
            else:
                new_status = 'partial'
                bill_status = 'completed'  # Change to completed when cleared
                is_credit = True
            message = 'Cheque marked as cleared'
        
        # Update bill with proper parameter binding
        if db_type == 'postgresql':
            cursor.execute("""
                UPDATE bills
                SET payment_status = %s,
                    status = %s,
                    is_credit = %s,
                    credit_paid_amount = %s,
                    credit_balance = %s
                WHERE id = %s
            """, (str(new_status), str(bill_status), bool(is_credit), float(new_paid) if action == 'bounced' else None, float(new_balance) if action == 'bounced' else None, str(bill_id)))
        else:
            cursor.execute("""
                UPDATE bills
                SET payment_status = ?,
                    status = ?,
                    is_credit = ?,
                    credit_paid_amount = ?,
                    credit_balance = ?
                WHERE id = ?
            """, (new_status, bill_status, is_credit, new_paid if action == 'bounced' else None, new_balance if action == 'bounced' else None, bill_id))
        
        # Log the transaction in credit_transactions table
        if db_type == 'postgresql':
            from modules.shared.database import generate_id
            transaction_id = generate_id()
            cursor.execute("""
                INSERT INTO credit_transactions (id, bill_id, customer_id, transaction_type, amount, payment_method, reference_number, notes, created_at)
                SELECT %s, %s, customer_id, %s, %s, 'CHEQUE', %s, %s, NOW()
                FROM bills WHERE id = %s
            """, (transaction_id, bill_id, 'cheque_' + action, current_paid if action == 'cleared' else 0, bill_number, f'Cheque {action}', bill_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': message,
            'bill_number': bill_number,
            'customer_name': customer_name,
            'amount': round(current_paid, 2) if action == 'cleared' else 0,
            'new_status': new_status,
            'action': action
        })
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@retail_bp.route('/api/credit/payment', methods=['POST'])
def record_credit_payment():
    """Record a payment for a credit bill"""
    from flask import request
    from modules.shared.database import get_db_connection
    import traceback
    import uuid
    from datetime import datetime
    
    print("=" * 80)
    print("💰 RECORDING CREDIT PAYMENT")
    print("=" * 80)
    
    try:
        data = request.json
        print(f"📥 Received data: {data}")
        
        bill_id = data.get('bill_id')
        payment_amount = float(data.get('payment_amount', 0))
        payment_method = data.get('payment_method', 'CASH')
        
        print(f"📋 Bill ID: {bill_id}")
        print(f"💵 Payment Amount: ₹{payment_amount}")
        print(f"💳 Payment Method: {payment_method}")
        
        if not bill_id or payment_amount <= 0:
            print("❌ Invalid input")
            return jsonify({
                'success': False,
                'error': 'Invalid bill ID or payment amount'
            }), 400
        
        print("🔌 Connecting to database...")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("🔍 Fetching bill details...")
        # Get current bill details
        from modules.shared.database import get_db_type
        db_type = get_db_type()
        
        if db_type == 'postgresql':
            cursor.execute("""
                SELECT total_amount, credit_paid_amount, credit_balance, payment_status, bill_number, created_at
                FROM bills
                WHERE id = %s
            """, (bill_id,))
        else:
            cursor.execute("""
                SELECT total_amount, credit_paid_amount, credit_balance, payment_status, bill_number, created_at
                FROM bills
                WHERE id = ?
            """, (bill_id,))
        
        row = cursor.fetchone()
        print(f"📊 Row fetched: {row}")
        
        if not row:
            print("❌ Bill not found")
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Bill not found'
            }), 404
        
        print("💾 Extracting row data...")
        total_amount = float(row['total_amount'])
        print(f"   total_amount: {total_amount}")
        current_paid = float(row['credit_paid_amount'] or 0)
        print(f"   current_paid: {current_paid}")
        current_balance = float(row['credit_balance'] or 0)
        print(f"   current_balance: {current_balance}")
        bill_number = row['bill_number']
        print(f"   bill_number: {bill_number}")
        bill_created_at = row['created_at']
        print(f"   bill_created_at: {bill_created_at}")
        
        print(f"📊 Current Status:")
        print(f"   Total: ₹{total_amount}")
        print(f"   Paid: ₹{current_paid}")
        print(f"   Balance: ₹{current_balance}")
        print(f"   Bill Date: {bill_created_at}")
        
        new_paid = current_paid + payment_amount
        new_balance = total_amount - new_paid
        
        print(f"🔢 Calculated values:")
        print(f"   new_paid: {new_paid} (type: {type(new_paid)})")
        print(f"   new_balance: {new_balance} (type: {type(new_balance)})")
        
        # Determine new status based on payment method
        if payment_method.upper() == 'CHEQUE':
            # Cheque payment - mark as "cheque_deposited" not fully paid
            new_status = 'cheque_deposited'
            is_credit = True  # Still a credit bill until cheque clears
            payment_status_display = 'Cheque Deposited'
        elif new_balance <= 0:
            new_status = 'paid'
            new_balance = 0.0  # Explicitly set to float
            new_paid = total_amount  # Use total amount
            is_credit = False  # No longer a credit bill
            payment_status_display = 'Paid'
        elif new_paid > 0:
            new_status = 'partial'
            is_credit = True  # Still a credit bill
            payment_status_display = 'Partial'
        else:
            new_status = 'unpaid'
            is_credit = True
            payment_status_display = 'Unpaid'
        
        # CRITICAL: Ensure new_balance is ALWAYS float, never boolean
        new_balance = float(new_balance)
        new_paid = float(new_paid)
        
        print(f"📊 New Status:")
        print(f"   Paid: ₹{new_paid} (type: {type(new_paid)})")
        print(f"   Balance: ₹{new_balance} (type: {type(new_balance)})")
        print(f"   Status: {new_status}")
        print(f"   is_credit: {is_credit} (type: {type(is_credit)})")
        print(f"   Balance: ₹{new_balance} (type: {type(new_balance)})")
        print(f"   Status: {new_status}")
        print(f"   is_credit: {is_credit} (type: {type(is_credit)})")
        
        # Insert payment record in payments table
        payment_id = str(uuid.uuid4())
        payment_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"💾 Creating payment record:")
        print(f"   payment_id: {payment_id}")
        print(f"   bill_id: {bill_id}")
        print(f"   method: {payment_method}")
        print(f"   amount: {payment_amount}")
        print(f"   processed_at: {payment_timestamp}")
        print(f"   bill_created_at: {bill_created_at}")
        
        # Use parameterized query with proper placeholder
        from modules.shared.database import get_db_type
        db_type = get_db_type()
        
        if db_type == 'postgresql':
            cursor.execute("""
                INSERT INTO payments (id, bill_id, method, amount, reference, processed_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (payment_id, bill_id, payment_method, payment_amount, f"Credit payment for {bill_number}", payment_timestamp))
        else:
            cursor.execute("""
                INSERT INTO payments (id, bill_id, method, amount, reference, processed_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (payment_id, bill_id, payment_method, payment_amount, f"Credit payment for {bill_number}", payment_timestamp))
        
        print(f"✅ Payment record created: {payment_id}")
        print(f"📅 This payment will be counted in revenue for: {datetime.now().strftime('%Y-%m-%d')}")
        
        # Update bill - ensure all types are correct for PostgreSQL
        # CRITICAL: Verify all values before UPDATE
        final_paid = float(new_paid)
        final_balance = float(new_balance)
        final_status = str(new_status)
        final_method = str(payment_method)
        final_is_credit = bool(is_credit)
        final_bill_id = str(bill_id)
        
        print(f"🔄 FINAL VALUES BEFORE UPDATE:")
        print(f"   1. credit_paid_amount = {final_paid} (type: {type(final_paid).__name__})")
        print(f"   2. credit_balance = {final_balance} (type: {type(final_balance).__name__})")
        print(f"   3. payment_status = {final_status} (type: {type(final_status).__name__})")
        print(f"   4. payment_method = {final_method} (type: {type(final_method).__name__})")
        print(f"   5. is_credit = {final_is_credit} (type: {type(final_is_credit).__name__})")
        print(f"   6. bill_id = {final_bill_id} (type: {type(final_bill_id).__name__})")
        
        if db_type == 'postgresql':
            # PostgreSQL: Use named parameters to avoid binding issues
            cursor.execute("""
                UPDATE bills
                SET credit_paid_amount = %(paid)s,
                    credit_balance = %(balance)s,
                    payment_status = %(status)s,
                    payment_method = %(method)s,
                    is_credit = %(is_credit)s
                WHERE id = %(bill_id)s
            """, {
                'paid': final_paid,
                'balance': final_balance,
                'status': final_status,
                'method': final_method,
                'is_credit': final_is_credit,
                'bill_id': final_bill_id
            })
        else:
            cursor.execute("""
                UPDATE bills
                SET credit_paid_amount = ?,
                    credit_balance = ?,
                    payment_status = ?,
                    payment_method = ?,
                    is_credit = ?
                WHERE id = ?
            """, (float(new_paid), float(new_balance), str(new_status), str(payment_method), int(is_credit), str(bill_id)))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Payment recorded successfully for {bill_number}")
        print(f"📅 Revenue will be counted for bill date: {bill_created_at}")
        print("=" * 80)
        
        return jsonify({
            'success': True,
            'message': 'Payment recorded successfully',
            'bill_number': bill_number,
            'new_paid_amount': round(new_paid, 2),
            'new_balance': round(new_balance, 2),
            'new_status': new_status,
            'payment_status_display': payment_status_display,
            'payment_amount': round(payment_amount, 2),
            'payment_id': payment_id,
            'is_cheque': payment_method.upper() == 'CHEQUE'
        })
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@retail_bp.route('/api/credit/history/test', methods=['GET'])
def test_credit_history_route():
    """Test endpoint to verify route is accessible"""
    print("✅ TEST ROUTE HIT!", flush=True)
    return jsonify({
        'success': True,
        'message': 'Credit history route is accessible!',
        'timestamp': datetime.now().isoformat()
    })


@retail_bp.route('/api/credit/history', methods=['GET'])
def get_retail_credit_history():
    """Get credit payment history - paid and partially paid bills - Supabase PostgreSQL"""
    import sys
    sys.stdout.flush()  # Force flush output
    
    print("\n" + "=" * 80, flush=True)
    print("🔥🔥🔥 CREDIT HISTORY ROUTE HIT (retail_bp)! 🔥🔥🔥", flush=True)
    print("=" * 80 + "\n", flush=True)
    
    from flask import request
    from modules.shared.database import get_db_connection
    import traceback
    
    print("=" * 80)
    print("📜 LOADING CREDIT PAYMENT HISTORY")
    print("=" * 80)
    
    try:
        # Get user_id for filtering
        user_id = get_user_id_from_session()
        print(f"🔍 [CREDIT HISTORY] User ID: {user_id}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get filter parameters
        date_range = request.args.get('date_range', 'all')
        customer = request.args.get('customer', 'all')
        
        print(f"🔍 [CREDIT HISTORY] Filters: date_range={date_range}, customer={customer}")
        
        # Use Python datetime for date filtering
        from datetime import datetime, timedelta
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Build PostgreSQL query - bills that have received payments OR are cheque bills
        query = """
            SELECT 
                b.id,
                b.bill_number,
                b.customer_name,
                b.customer_id,
                b.total_amount,
                b.credit_paid_amount,
                b.credit_balance,
                b.payment_method,
                b.payment_status,
                b.created_at,
                b.is_credit
            FROM bills b
            WHERE b.credit_paid_amount > 0 OR (b.payment_method = 'cheque' AND b.payment_status = 'cheque_deposited')
        """
        
        params = []
        
        # Add user filtering
        if user_id:
            query += " AND (b.business_owner_id = %s OR b.business_owner_id IS NULL)"
            params.append(user_id)
        
        # Add date filter
        if date_range == 'today':
            query += f" AND CAST(b.created_at AS DATE) = '{today}'"
        elif date_range == 'yesterday':
            query += f" AND CAST(b.created_at AS DATE) = '{yesterday}'"
        elif date_range == 'week':
            query += f" AND CAST(b.created_at AS DATE) >= '{week_ago}'"
        elif date_range == 'month':
            query += f" AND CAST(b.created_at AS DATE) >= '{month_ago}'"
        
        # Add customer filter
        if customer != 'all':
            query += " AND b.customer_name = %s"
            params.append(customer)
        
        query += " ORDER BY b.created_at DESC"
        
        print(f"🔍 [CREDIT HISTORY] Executing query with {len(params)} params")
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        print(f"✅ [CREDIT HISTORY] Found {len(rows)} records")
        print(f"🔍 [CREDIT HISTORY] Row type: {type(rows[0]) if rows else 'No rows'}")
        print(f"🔍 [CREDIT HISTORY] First row: {rows[0] if rows else 'No rows'}")
        
        bills = []
        for row in rows:
            try:
                print(f"🔍 [CREDIT HISTORY] Processing row: {type(row)} - {row}")
                bills.append({
                    'id': row['id'],
                    'bill_number': row['bill_number'],
                    'customer_name': row['customer_name'] or 'Walk-in Customer',
                    'customer_id': row['customer_id'],
                    'total_amount': float(row['total_amount'] or 0),
                    'paid_amount': float(row['credit_paid_amount'] or 0),
                    'balance_due': float(row['credit_balance'] or 0),
                    'remaining_amount': float(row['credit_balance'] or 0),
                    'payment_method': row['payment_method'] or 'cash',
                    'payment_status': row['payment_status'] or 'unpaid',
                    'created_at': str(row['created_at']),
                    'is_credit': row['is_credit'],
                    'last_payment_date': str(row['created_at']),
                    'customer_phone': ''
                })
            except Exception as row_error:
                print(f"❌ Error processing row: {row_error}")
                continue
        
        # Calculate summary
        total_paid = sum(bill['paid_amount'] for bill in bills)
        total_amount = sum(bill['total_amount'] for bill in bills)
        total_remaining = sum(bill['balance_due'] for bill in bills)
        total_bills = len(bills)
        
        # Get unique customers
        customers = list(set(bill['customer_name'] for bill in bills))
        
        print(f"💰 [CREDIT HISTORY] Total Paid: ₹{total_paid:.2f}")
        print(f"📊 [CREDIT HISTORY] Total Bills: {total_bills}")
        
        conn.close()
        
        return jsonify({
            'success': True,
            'bills': bills,
            'customers': customers,
            'summary': {
                'total_paid': round(total_paid, 2),
                'total_bills': total_bills,
                'total_customers': len(customers),
                'total_remaining': round(total_remaining, 2)
            },
            'stats': {
                'total_bills': total_bills,
                'pending_amount': round(total_remaining, 2),
                'total_amount': round(total_amount, 2),
                'received_amount': round(total_paid, 2)
            }
        })
        
    except KeyError as ke:
        print(f"❌ [CREDIT HISTORY] KEY ERROR: {str(ke)}")
        print(f"❌ [CREDIT HISTORY] This means trying to access a column that doesn't exist")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f"KeyError: {str(ke)}",
            'bills': [],
            'customers': [],
            'stats': {'total_bills': 0, 'pending_amount': 0, 'total_amount': 0, 'received_amount': 0},
            'summary': {'total_paid': 0, 'total_bills': 0, 'total_customers': 0, 'total_remaining': 0}
        }), 500
    except Exception as e:
        print(f"❌ [CREDIT HISTORY] ERROR: {str(e)}")
        print(f"❌ [CREDIT HISTORY] ERROR TYPE: {type(e).__name__}")
        print(f"❌ [CREDIT HISTORY] ERROR REPR: {repr(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f"{type(e).__name__}: {str(e)}",
            'error_details': repr(e),
            'bills': [],
            'customers': [],
            'stats': {'total_bills': 0, 'pending_amount': 0, 'total_amount': 0, 'received_amount': 0},
            'summary': {'total_paid': 0, 'total_bills': 0, 'total_customers': 0, 'total_remaining': 0}
        }), 500


@retail_bp.route('/api/credit/bill/<bill_id>/payments', methods=['GET'])
def get_bill_payment_history(bill_id):
    """Get payment history for a specific credit bill"""
    from modules.shared.database import get_db_connection
    import traceback
    
    print("=" * 80)
    print(f"📜 LOADING PAYMENT HISTORY FOR BILL: {bill_id}")
    print("=" * 80)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get bill details
        cursor.execute("""
            SELECT bill_number, customer_name, total_amount, credit_paid_amount, credit_balance
            FROM bills
            WHERE id = ?
        """, (bill_id,))
        
        bill_row = cursor.fetchone()
        if not bill_row:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Bill not found'
            }), 404
        
        bill_info = {
            'bill_number': bill_row['bill_number'],
            'customer_name': bill_row['customer_name'] or 'Walk-in Customer',
            'total_amount': float(bill_row['total_amount'] or 0),
            'paid_amount': float(bill_row['credit_paid_amount'] or 0),
            'balance': float(bill_row['credit_balance'] or 0)
        }
        
        # Get payment history from payments table (oldest first)
        cursor.execute("""
            SELECT id, method, amount, reference, processed_at
            FROM payments
            WHERE bill_id = ?
            ORDER BY processed_at ASC
        """, (bill_id,))
        
        payment_rows = cursor.fetchall()
        
        payments = []
        for row in payment_rows:
            payments.append({
                'id': row['id'],
                'method': row['method'],
                'amount': float(row['amount']),
                'reference': row['reference'],
                'processed_at': row['processed_at']
            })
        
        print(f"✅ Found {len(payments)} payment records")
        
        conn.close()
        
        return jsonify({
            'success': True,
            'bill': bill_info,
            'payments': payments,
            'total_payments': len(payments)
        })
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# PRODUCTS API ROUTES
# ============================================================================

@retail_bp.route('/api/products', methods=['GET'])
def get_products():
    """Get all products - Filtered by user (except for admins)"""
    from modules.shared.database import get_db_connection
    import traceback
    
    try:
        # Get user_id and check if admin
        user_id = get_user_id_from_session()
        user_type = session.get('user_type')
        is_admin = session.get('is_super_admin', False)
        
        print(f"🔍 [PRODUCTS] user_id: {user_id}, type: {user_type}, admin: {is_admin}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query with conditional user filtering
        query = """
            SELECT 
                id, name, description, category, price, cost, stock, min_stock, 
                unit, code, barcode_data, image_url, is_active, created_at
            FROM products
            WHERE is_active = 1
        """
        
        params = []
        
        # Only filter by user_id if NOT admin
        if user_id and not is_admin and user_type != 'admin':
            query += " AND (user_id = ? OR user_id IS NULL)"
            params.append(user_id)
        
        query += " ORDER BY name ASC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        products = []
        for row in rows:
            products.append({
                'id': row[0],
                'name': row[1],
                'description': row[2] or '',
                'category': row[3] or 'Other',
                'price': float(row[4] or 0),
                'cost': float(row[5] or 0),
                'stock': int(row[6] or 0),
                'min_stock': int(row[7] or 0),
                'unit': row[8] or 'piece',
                'code': row[9] or '',
                'barcode_data': row[10] or '',
                'image_url': row[11] or '',
                'is_active': row[12],
                'created_at': row[13]
            })
        
        conn.close()
        
        print(f"✅ Found {len(products)} products")
        
        return jsonify(products)
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        traceback.print_exc()
        return jsonify([]), 500


# REMOVED: Duplicate endpoint - use products_bp instead
# @retail_bp.route('/api/products', methods=['POST'])
# def add_product():
#     """This endpoint is now handled by products_bp"""
#     pass


@retail_bp.route('/api/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    """Update a product"""
    from flask import request
    from modules.shared.database import get_db_connection
    
    try:
        data = request.json
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE products SET
                name = ?, description = ?, category = ?, price = ?, cost = ?,
                stock = ?, min_stock = ?, unit = ?, code = ?, barcode_data = ?, image_url = ?
            WHERE id = ?
        """, (
            data.get('name'),
            data.get('description', ''),
            data.get('category', 'Other'),
            data.get('price', 0),
            data.get('cost', 0),
            data.get('stock', 0),
            data.get('min_stock', 0),
            data.get('unit', 'piece'),
            data.get('code', ''),
            data.get('barcode_data', ''),
            data.get('image_url', ''),
            product_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Product updated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@retail_bp.route('/api/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product (soft delete)"""
    from modules.shared.database import get_db_connection
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE products SET is_active = 0 WHERE id = ?", (product_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Product deleted successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@retail_bp.route('/api/products/next-code', methods=['GET'])
def get_next_product_code():
    """Get the next available product code"""
    from modules.shared.database import get_db_connection
    
    try:
        user_id = get_user_id_from_session()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get the highest numeric code
        cursor.execute("""
            SELECT code FROM products 
            WHERE (user_id = ? OR user_id IS NULL) AND is_active = 1
            ORDER BY CAST(code AS INTEGER) DESC LIMIT 1
        """, (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            try:
                max_code = int(result[0])
                next_code = str(max_code + 1)
            except:
                next_code = '1'
        else:
            next_code = '1'
        
        return jsonify({
            'success': True,
            'next_code': next_code
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'next_code': '1'
        }), 500

