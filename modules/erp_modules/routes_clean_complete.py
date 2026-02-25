"""
ERP Modules - Complete Clean Implementation
Covers: All required ERP modules with no duplicates
"""

from flask import Blueprint, render_template, jsonify, session, request
from modules.shared.database import get_db_connection, get_db_type
import traceback, uuid, json
from datetime import datetime, timedelta

erp_bp = Blueprint('erp', __name__)

def get_user_id():
    user_type = session.get('user_type')
    if user_type == 'employee':
        return session.get('client_id')
    return session.get('user_id')

# ─── Page Routes ───────────────────────────────────────────────────────────────

@erp_bp.route('/erp/dashboard')
def erp_dashboard():
    return render_template('erp_dashboard.html')

@erp_bp.route('/erp/company-setup')
def company_setup():
    return render_template('erp_company_setup.html')

@erp_bp.route('/erp/bank-management')
def bank_management():
    return render_template('erp_bank_management.html')

@erp_bp.route('/erp/products')
def products():
    return render_template('erp_products.html')

@erp_bp.route('/erp/invoices')
def invoices():
    return render_template('erp_invoices.html')

@erp_bp.route('/erp/purchase')
def purchase():
    return render_template('erp_purchase.html')

@erp_bp.route('/erp/purchase-order')
def purchase_order():
    return render_template('erp_purchase_order.html')

@erp_bp.route('/erp/grn')
def grn():
    return render_template('erp_grn.html')

@erp_bp.route('/erp/batch-expiry')
def batch_expiry():
    return render_template('erp_batch_expiry.html')

@erp_bp.route('/erp/barcode')
def barcode():
    return render_template('erp_barcode.html')

@erp_bp.route('/erp/vendor')
def vendor():
    return render_template('erp_vendor.html')

@erp_bp.route('/erp/crm')
def crm():
    return render_template('erp_crm.html')

@erp_bp.route('/erp/payments')
def payments():
    return render_template('erp_payments.html')

@erp_bp.route('/erp/income-expense')
def income_expense():
    return render_template('erp_income_expense.html')

@erp_bp.route('/erp/accounting')
def accounting():
    return render_template('erp_accounting.html')

@erp_bp.route('/erp/staff-operator')
def staff_operator():
    return render_template('erp_staff_operator.html')

@erp_bp.route('/erp/backup-settings')
def backup_settings():
    return render_template('erp_backup_settings.html')

@erp_bp.route('/erp/customers')
def customers():
    return render_template('erp_customer.html')

@erp_bp.route('/erp/stock')
def stock():
    return render_template('erp_stock.html')

@erp_bp.route('/erp/reports')
def reports():
    return render_template('erp_reports.html')

# ─── MODULE 1: Batch & Expiry Management ───────────────────────────────────────

@erp_bp.route('/api/erp/batches', methods=['GET'])
def get_batches():
    """
    Get all batches with optional filters
    Query params: product_id, status (active/expired), near_expiry (days)
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        # Get query parameters
        product_id = request.args.get('product_id')
        status = request.args.get('status')  # active/expired
        near_expiry_days = request.args.get('near_expiry', type=int, default=30)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query
        query = """
            SELECT b.*, p.product_name, p.product_code
            FROM erp_batches b
            LEFT JOIN erp_products p ON b.product_id = p.id
            WHERE b.user_id = %s AND b.is_deleted = FALSE
        """
        params = [user_id]
        
        if product_id:
            query += " AND b.product_id = %s"
            params.append(product_id)
        
        if status:
            if status == 'expired':
                query += " AND b.expiry_date < %s"
                params.append(datetime.now().date().isoformat())
            elif status == 'active':
                query += " AND b.expiry_date >= %s"
                params.append(datetime.now().date().isoformat())
        
        query += " ORDER BY b.expiry_date ASC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        batches = [dict(row) for row in rows]
        
        # Add expiry status calculation
        today = datetime.now().date()
        for batch in batches:
            if batch['expiry_date']:
                expiry_date = datetime.strptime(str(batch['expiry_date']), '%Y-%m-%d').date()
                days_diff = (expiry_date - today).days
                if days_diff < 0:
                    batch['expiry_status'] = 'expired'
                elif days_diff <= near_expiry_days:
                    batch['expiry_status'] = 'near_expiry'
                else:
                    batch['expiry_status'] = 'active'
            else:
                batch['expiry_status'] = 'no_expiry'
        
        return jsonify({'success': True, 'data': batches})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/batches', methods=['POST'])
def create_batch():
    """
    Create new batch
    Required: product_id, batch_number, mfg_date, expiry_date, quantity
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        required_fields = ['product_id', 'batch_number', 'mfg_date', 'expiry_date', 'quantity']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        # Validate product exists
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if batch number already exists for this product
        cursor.execute("""
            SELECT id FROM erp_batches 
            WHERE product_id = %s AND batch_number = %s AND user_id = %s AND is_deleted = FALSE
        """, (data['product_id'], data['batch_number'], user_id))
        
        if cursor.fetchone():
            return jsonify({'success': False, 'error': 'Batch number already exists for this product'}), 400
        
        # Get product details for reference
        cursor.execute("SELECT product_name, product_code FROM erp_products WHERE id = %s AND user_id = %s", 
                      (data['product_id'], user_id))
        product = cursor.fetchone()
        
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        # Insert new batch
        batch_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO erp_batches (id, user_id, product_id, product_name, product_code, 
            batch_number, mfg_date, expiry_date, quantity, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            batch_id, user_id, data['product_id'], product['product_name'], product['product_code'],
            data['batch_number'], data['mfg_date'], data['expiry_date'], 
            float(data['quantity']), now, now
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': 'Batch created successfully',
            'id': batch_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/batches/<batch_id>', methods=['PUT'])
def update_batch(batch_id):
    """Update existing batch"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if batch exists and belongs to user
        cursor.execute("SELECT id FROM erp_batches WHERE id = %s AND user_id = %s AND is_deleted = FALSE", 
                      (batch_id, user_id))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Batch not found'}), 404
        
        # Build update query dynamically
        update_fields = []
        params = []
        
        if 'batch_number' in data:
            update_fields.append("batch_number = %s")
            params.append(data['batch_number'])
        if 'mfg_date' in data:
            update_fields.append("mfg_date = %s")
            params.append(data['mfg_date'])
        if 'expiry_date' in data:
            update_fields.append("expiry_date = %s")
            params.append(data['expiry_date'])
        if 'quantity' in data:
            update_fields.append("quantity = %s")
            params.append(float(data['quantity']))
        if 'product_id' in data:
            # Also update product_name and product_code if product changes
            cursor.execute("SELECT product_name, product_code FROM erp_products WHERE id = %s AND user_id = %s", 
                          (data['product_id'], user_id))
            product = cursor.fetchone()
            if product:
                update_fields.extend(["product_id = %s", "product_name = %s", "product_code = %s"])
                params.extend([data['product_id'], product['product_name'], product['product_code']])
        
        update_fields.append("updated_at = %s")
        params.append(datetime.now().isoformat())
        
        if update_fields:
            query = f"UPDATE erp_batches SET {', '.join(update_fields)} WHERE id = %s AND user_id = %s"
            params.extend([batch_id, user_id])
            
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
        
        return jsonify({'success': True, 'message': 'Batch updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/batches/<batch_id>', methods=['DELETE'])
def delete_batch(batch_id):
    """Delete batch (soft delete)"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Soft delete - mark as deleted instead of removing
        cursor.execute("""
            UPDATE erp_batches 
            SET is_deleted = TRUE, updated_at = %s 
            WHERE id = %s AND user_id = %s
        """, (datetime.now().isoformat(), batch_id, user_id))
        
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'error': 'Batch not found'}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Batch deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/batches/near-expiry', methods=['GET'])
def get_near_expiry_batches():
    """
    Get batches expiring within X days (default 30)
    Query param: days (optional, default=30)
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        days = request.args.get('days', type=int, default=30)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get batches expiring within specified days
        future_date = (datetime.now() + timedelta(days=days)).date().isoformat()
        today = datetime.now().date().isoformat()
        
        cursor.execute("""
            SELECT b.*, p.product_name, p.product_code
            FROM erp_batches b
            LEFT JOIN erp_products p ON b.product_id = p.id
            WHERE b.user_id = %s 
              AND b.expiry_date BETWEEN %s AND %s
              AND b.is_deleted = FALSE
            ORDER BY b.expiry_date ASC
        """, (user_id, today, future_date))
        
        rows = cursor.fetchall()
        conn.close()
        
        batches = [dict(row) for row in rows]
        
        return jsonify({'success': True, 'data': batches, 'days': days})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ─── MODULE 2: Barcode Management ──────────────────────────────────────────────

@erp_bp.route('/api/erp/products/<product_id>/barcode', methods=['POST'])
def generate_barcode(product_id):
    """
    Generate barcode for product
    Body: { "format": "EAN-13" or "Code-128" }
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        barcode_format = data.get('format', 'EAN-13').upper()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if product exists
        cursor.execute("SELECT id FROM erp_products WHERE id = %s AND user_id = %s", (product_id, user_id))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        # Generate unique barcode
        # Use product ID as base and add a prefix
        import random
        barcode_prefix = {
            'EAN-13': '200',  # Internal use prefix for EAN-13
            'CODE-128': 'C',
            'UPC-A': '0'
        }.get(barcode_format, '200')
        
        # Generate a unique number
        unique_part = str(random.randint(10000000, 99999999))  # 8 digits
        barcode = barcode_prefix + unique_part
        
        # Ensure uniqueness
        while True:
            cursor.execute("SELECT id FROM erp_products WHERE barcode = %s", (barcode,))
            if not cursor.fetchone():
                break
            unique_part = str(random.randint(10000000, 99999999))
            barcode = barcode_prefix + unique_part
        
        # Update product with barcode
        cursor.execute("""
            UPDATE erp_products 
            SET barcode = %s, updated_at = %s 
            WHERE id = %s AND user_id = %s
        """, (barcode, datetime.now().isoformat(), product_id, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'product_id': product_id,
                'barcode': barcode,
                'format': barcode_format
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/products/barcode/<barcode>', methods=['GET'])
def lookup_barcode(barcode):
    """
    Lookup product by barcode
    Returns product details if found
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Find product by barcode
        cursor.execute("""
            SELECT * FROM erp_products 
            WHERE barcode = %s AND user_id = %s AND is_deleted = FALSE
        """, (barcode, user_id))
        
        product = cursor.fetchone()
        conn.close()
        
        if product:
            return jsonify({
                'success': True,
                'data': dict(product)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Product not found for this barcode'
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ─── MODULE 3: Vendor Management ───────────────────────────────────────────────

@erp_bp.route('/api/erp/vendors/<vendor_id>', methods=['GET'])
def get_vendor_details(vendor_id):
    """Get specific vendor with transaction summary"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get vendor details
        cursor.execute("""
            SELECT * FROM erp_vendors 
            WHERE id = %s AND user_id = %s AND is_deleted = FALSE
        """, (vendor_id, user_id))
        
        vendor = cursor.fetchone()
        if not vendor:
            return jsonify({'success': False, 'error': 'Vendor not found'}), 404
        
        # Get transaction summary
        cursor.execute("""
            SELECT 
                COUNT(*) as total_transactions,
                SUM(amount) as total_amount,
                AVG(amount) as avg_amount
            FROM erp_purchase_orders 
            WHERE vendor_id = %s AND user_id = %s
        """, (vendor_id, user_id))
        
        summary = cursor.fetchone()
        vendor_dict = dict(vendor)
        vendor_dict['transaction_summary'] = dict(summary) if summary else {
            'total_transactions': 0,
            'total_amount': 0,
            'avg_amount': 0
        }
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': vendor_dict
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/vendors/<vendor_id>/transactions', methods=['GET'])
def get_vendor_transactions(vendor_id):
    """Get all transactions for a vendor"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify vendor exists
        cursor.execute("SELECT id FROM erp_vendors WHERE id = %s AND user_id = %s", (vendor_id, user_id))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Vendor not found'}), 404
        
        # Get all transactions for this vendor
        cursor.execute("""
            SELECT * FROM erp_purchase_orders 
            WHERE vendor_id = %s AND user_id = %s 
            ORDER BY created_at DESC
        """, (vendor_id, user_id))
        
        transactions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'data': transactions
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ─── MODULE 4: CRM & Leads ─────────────────────────────────────────────────────

@erp_bp.route('/api/erp/leads', methods=['GET'])
def get_leads():
    """Get all leads with filters (status, source, date_range)"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        # Get filter parameters
        status = request.args.get('status')
        source = request.args.get('source')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM erp_leads WHERE user_id = %s AND is_deleted = FALSE"
        params = [user_id]
        
        if status:
            query += " AND status = %s"
            params.append(status)
        if source:
            query += " AND source = %s"
            params.append(source)
        if start_date:
            query += " AND created_at >= %s"
            params.append(start_date)
        if end_date:
            query += " AND created_at <= %s"
            params.append(end_date)
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        leads = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'data': leads
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/leads', methods=['POST'])
def create_lead():
    """Create new lead"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        required_fields = ['name', 'contact']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        lead_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO erp_leads (id, user_id, name, contact, email, company, 
            source, status, notes, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            lead_id, user_id, data['name'], data['contact'], 
            data.get('email', ''), data.get('company', ''),
            data.get('source', 'Unknown'), data.get('status', 'New'),
            data.get('notes', ''), now, now
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Lead created successfully',
            'id': lead_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/leads/<lead_id>', methods=['PUT'])
def update_lead(lead_id):
    """Update lead (including status changes)"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if lead exists
        cursor.execute("SELECT id FROM erp_leads WHERE id = %s AND user_id = %s AND is_deleted = FALSE", 
                      (lead_id, user_id))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Lead not found'}), 404
        
        # Build update query
        update_fields = []
        params = []
        
        if 'name' in data:
            update_fields.append("name = %s")
            params.append(data['name'])
        if 'contact' in data:
            update_fields.append("contact = %s")
            params.append(data['contact'])
        if 'email' in data:
            update_fields.append("email = %s")
            params.append(data['email'])
        if 'company' in data:
            update_fields.append("company = %s")
            params.append(data['company'])
        if 'source' in data:
            update_fields.append("source = %s")
            params.append(data['source'])
        if 'status' in data:
            update_fields.append("status = %s")
            params.append(data['status'])
        if 'notes' in data:
            update_fields.append("notes = %s")
            params.append(data['notes'])
        
        update_fields.append("updated_at = %s")
        params.append(datetime.now().isoformat())
        params.extend([lead_id, user_id])
        
        if update_fields:
            query = f"UPDATE erp_leads SET {', '.join(update_fields)} WHERE id = %s AND user_id = %s AND is_deleted = FALSE"
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Lead updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/leads/<lead_id>/convert', methods=['POST'])
def convert_lead_to_customer(lead_id):
    """
    Convert lead to customer
    Creates new customer record and marks lead as converted
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get lead details
        cursor.execute("SELECT * FROM erp_leads WHERE id = %s AND user_id = %s AND is_deleted = FALSE", 
                      (lead_id, user_id))
        lead = cursor.fetchone()
        
        if not lead:
            return jsonify({'success': False, 'error': 'Lead not found'}), 404
        
        # Check if already converted
        if lead['status'] == 'Converted':
            return jsonify({'success': False, 'error': 'Lead already converted to customer'}), 400
        
        # Create customer from lead
        customer_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO erp_customers (id, user_id, customer_name, phone, email, address, 
            gst_number, pan_number, credit_limit, credit_days, customer_category, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            customer_id, user_id, lead['name'], lead['contact'], lead['email'], '',
            '', '', 0, 0, 'General', now, now
        ))
        
        # Update lead status to converted
        cursor.execute("""
            UPDATE erp_leads 
            SET status = 'Converted', converted_to_customer_id = %s, updated_at = %s 
            WHERE id = %s AND user_id = %s
        """, (customer_id, now, lead_id, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Lead converted to customer successfully',
            'customer_id': customer_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ─── MODULE 5: Purchase Orders ─────────────────────────────────────────────────

@erp_bp.route('/api/erp/purchase-orders/<po_id>', methods=['GET'])
def get_purchase_order_details(po_id):
    """Get specific PO with items"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get PO header
        cursor.execute("""
            SELECT po.*, v.vendor_name 
            FROM erp_purchase_orders po
            LEFT JOIN erp_vendors v ON po.vendor_id = v.id
            WHERE po.id = %s AND po.user_id = %s AND po.is_deleted = FALSE
        """, (po_id, user_id))
        
        po_header = cursor.fetchone()
        if not po_header:
            return jsonify({'success': False, 'error': 'Purchase Order not found'}), 404
        
        # Get PO items
        cursor.execute("""
            SELECT poi.*, p.product_name, p.product_code 
            FROM erp_purchase_order_items poi
            LEFT JOIN erp_products p ON poi.product_id = p.id
            WHERE poi.po_id = %s AND poi.is_deleted = FALSE
            ORDER BY poi.created_at ASC
        """, (po_id,))
        
        po_items = [dict(row) for row in cursor.fetchall()]
        
        result = dict(po_header)
        result['items'] = po_items
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/purchase-orders/<po_id>', methods=['PUT'])
def update_purchase_order(po_id):
    """Update PO (only if status is Draft)"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if PO exists and is in draft status
        cursor.execute("""
            SELECT id, status FROM erp_purchase_orders 
            WHERE id = %s AND user_id = %s AND is_deleted = FALSE
        """, (po_id, user_id))
        
        po = cursor.fetchone()
        if not po:
            return jsonify({'success': False, 'error': 'Purchase Order not found'}), 404
        
        if po['status'] != 'Draft':
            return jsonify({'success': False, 'error': 'Cannot update PO after it is approved'}), 400
        
        # Update PO header (only allowed fields for Draft status)
        update_fields = []
        params = []
        
        if 'vendor_id' in data:
            update_fields.append("vendor_id = %s")
            params.append(data['vendor_id'])
        if 'po_number' in data:
            update_fields.append("po_number = %s")
            params.append(data['po_number'])
        if 'po_date' in data:
            update_fields.append("po_date = %s")
            params.append(data['po_date'])
        if 'delivery_date' in data:
            update_fields.append("delivery_date = %s")
            params.append(data['delivery_date'])
        if 'terms_conditions' in data:
            update_fields.append("terms_conditions = %s")
            params.append(data['terms_conditions'])
        if 'notes' in data:
            update_fields.append("notes = %s")
            params.append(data['notes'])
        
        if update_fields:
            update_fields.append("updated_at = %s")
            params.append(datetime.now().isoformat())
            params.extend([po_id, user_id])
            
            query = f"UPDATE erp_purchase_orders SET {', '.join(update_fields)} WHERE id = %s AND user_id = %s AND is_deleted = FALSE"
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Purchase Order updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/purchase-orders/<po_id>/reject', methods=['POST'])
def reject_purchase_order(po_id):
    """Reject PO with reason"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        reason = data.get('reason', 'Rejected by manager')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if PO exists
        cursor.execute("""
            SELECT id, status FROM erp_purchase_orders 
            WHERE id = %s AND user_id = %s AND is_deleted = FALSE
        """, (po_id, user_id))
        
        po = cursor.fetchone()
        if not po:
            return jsonify({'success': False, 'error': 'Purchase Order not found'}), 404
        
        # Update PO status to Rejected
        cursor.execute("""
            UPDATE erp_purchase_orders 
            SET status = 'Rejected', rejection_reason = %s, updated_at = %s 
            WHERE id = %s AND user_id = %s AND is_deleted = FALSE
        """, (reason, datetime.now().isoformat(), po_id, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Purchase Order rejected successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ─── MODULE 6: GRN (Goods Receipt Note) ────────────────────────────────────────

@erp_bp.route('/api/erp/grn', methods=['GET'])
def get_grn_list():
    """Get all GRNs with filters"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        # Get filter parameters
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT g.*, v.vendor_name, po.po_number 
            FROM erp_grn g
            LEFT JOIN erp_vendors v ON g.vendor_id = v.id
            LEFT JOIN erp_purchase_orders po ON g.po_id = po.id
            WHERE g.user_id = %s AND g.is_deleted = FALSE
        """
        params = [user_id]
        
        if status:
            query += " AND g.status = %s"
            params.append(status)
        if start_date:
            query += " AND g.grn_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND g.grn_date <= %s"
            params.append(end_date)
        
        query += " ORDER BY g.grn_date DESC"
        
        cursor.execute(query, params)
        grns = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'data': grns
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/grn', methods=['POST'])
def create_grn():
    """
    Create GRN from PO
    Updates stock quantities
    Updates PO status
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        required_fields = ['po_id', 'received_items']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Start transaction
        conn.autocommit = False
        
        try:
            # Get PO details
            cursor.execute("""
                SELECT id, vendor_id, status FROM erp_purchase_orders 
                WHERE id = %s AND user_id = %s AND is_deleted = FALSE
            """, (data['po_id'], user_id))
            
            po = cursor.fetchone()
            if not po:
                return jsonify({'success': False, 'error': 'Purchase Order not found'}), 404
            
            if po['status'] != 'Approved':
                return jsonify({'success': False, 'error': 'PO must be approved before creating GRN'}), 400
            
            # Get PO items to verify received items
            cursor.execute("""
                SELECT * FROM erp_purchase_order_items 
                WHERE po_id = %s AND is_deleted = FALSE
            """, (data['po_id'],))
            po_items = cursor.fetchall()
            
            # Validate received items against PO items
            po_item_map = {item['product_id']: dict(item) for item in po_items}
            for received_item in data['received_items']:
                product_id = received_item['product_id']
                if product_id not in po_item_map:
                    return jsonify({'success': False, 'error': f'Product {product_id} not in PO'}), 400
                
                expected_qty = po_item_map[product_id]['quantity']
                received_qty = received_item['received_quantity']
                
                if received_qty > expected_qty:
                    return jsonify({
                        'success': False, 
                        'error': f'Received quantity {received_qty} exceeds ordered quantity {expected_qty} for product {product_id}'
                    }), 400
            
            # Create GRN
            grn_id = str(uuid.uuid4())
            grn_number = f"GRN-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            now = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO erp_grn (id, user_id, grn_number, po_id, vendor_id, grn_date, 
                total_amount, status, notes, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                grn_id, user_id, grn_number, data['po_id'], po['vendor_id'],
                data.get('grn_date', now.split('T')[0]), data.get('total_amount', 0),
                'Received', data.get('notes', ''), now, now
            ))
            
            # Create GRN items and update stock
            for received_item in data['received_items']:
                grn_item_id = str(uuid.uuid4())
                
                cursor.execute("""
                    INSERT INTO erp_grn_items (id, grn_id, product_id, ordered_quantity, 
                    received_quantity, unit_price, total_amount, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    grn_item_id, grn_id, received_item['product_id'],
                    received_item.get('ordered_quantity', 0), received_item['received_quantity'],
                    received_item.get('unit_price', 0), received_item.get('total_amount', 0),
                    now, now
                ))
                
                # Update stock quantity
                cursor.execute("""
                    UPDATE erp_stock 
                    SET quantity = quantity + %s, updated_at = %s 
                    WHERE product_id = %s AND user_id = %s
                """, (received_item['received_quantity'], now, received_item['product_id'], user_id))
                
                # If no stock record exists, create one
                if cursor.rowcount == 0:
                    cursor.execute("""
                        INSERT INTO erp_stock (id, user_id, product_id, quantity, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        str(uuid.uuid4()), user_id, received_item['product_id'], 
                        received_item['received_quantity'], now, now
                    ))
                
                # If batch info is provided, create/update batch
                if 'batch_number' in received_item:
                    batch_id = str(uuid.uuid4())
                    cursor.execute("""
                        INSERT INTO erp_batches (id, user_id, product_id, batch_number, 
                        expiry_date, quantity, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (product_id, batch_number) 
                        DO UPDATE SET quantity = erp_batches.quantity + %s, updated_at = %s
                    """, (
                        batch_id, user_id, received_item['product_id'], 
                        received_item['batch_number'], received_item.get('expiry_date'),
                        received_item['received_quantity'], now, now,
                        received_item['received_quantity'], now
                    ))
            
            # Update PO status to Partially Received or Fully Received
            cursor.execute("""
                UPDATE erp_purchase_orders 
                SET status = 'Partially Received', updated_at = %s 
                WHERE id = %s AND user_id = %s
            """, (now, data['po_id'], user_id))
            
            # Check if PO is fully received
            cursor.execute("""
                SELECT SUM(quantity) as total_ordered, 
                       (SELECT SUM(received_quantity) FROM erp_grn_items WHERE po_id = %s) as total_received
                FROM erp_purchase_order_items WHERE po_id = %s
            """, (data['po_id'], data['po_id']))
            
            po_totals = cursor.fetchone()
            if po_totals and po_totals['total_received'] >= po_totals['total_ordered']:
                cursor.execute("""
                    UPDATE erp_purchase_orders 
                    SET status = 'Fully Received', updated_at = %s 
                    WHERE id = %s AND user_id = %s
                """, (now, data['po_id'], user_id))
            
            conn.commit()
            conn.autocommit = True
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'GRN created successfully',
                'id': grn_id,
                'grn_number': grn_number
            })
        except Exception as e:
            conn.rollback()
            conn.autocommit = True
            raise e
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/grn/<grn_id>', methods=['GET'])
def get_grn_details(grn_id):
    """Get specific GRN with items"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get GRN header
        cursor.execute("""
            SELECT g.*, v.vendor_name, po.po_number 
            FROM erp_grn g
            LEFT JOIN erp_vendors v ON g.vendor_id = v.id
            LEFT JOIN erp_purchase_orders po ON g.po_id = po.id
            WHERE g.id = %s AND g.user_id = %s AND g.is_deleted = FALSE
        """, (grn_id, user_id))
        
        grn_header = cursor.fetchone()
        if not grn_header:
            return jsonify({'success': False, 'error': 'GRN not found'}), 404
        
        # Get GRN items
        cursor.execute("""
            SELECT gri.*, p.product_name, p.product_code 
            FROM erp_grn_items gri
            LEFT JOIN erp_products p ON gri.product_id = p.id
            WHERE gri.grn_id = %s AND gri.is_deleted = FALSE
            ORDER BY gri.created_at ASC
        """, (grn_id,))
        
        grn_items = [dict(row) for row in cursor.fetchall()]
        
        result = dict(grn_header)
        result['items'] = grn_items
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ─── MODULE 7: Income/Expense Tracking ─────────────────────────────────────────

@erp_bp.route('/api/erp/transactions', methods=['GET'])
def get_transactions():
    """Get all transactions with filters (type, category, date_range)"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        # Get filter parameters
        transaction_type = request.args.get('type')  # income/expense
        category = request.args.get('category')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM erp_transactions WHERE user_id = %s AND is_deleted = FALSE"
        params = [user_id]
        
        if transaction_type:
            query += " AND transaction_type = %s"
            params.append(transaction_type)
        if category:
            query += " AND category = %s"
            params.append(category)
        if start_date:
            query += " AND transaction_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND transaction_date <= %s"
            params.append(end_date)
        
        query += " ORDER BY transaction_date DESC, created_at DESC"
        
        cursor.execute(query, params)
        transactions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'data': transactions
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/transactions', methods=['POST'])
def create_transaction():
    """Create income or expense transaction"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        required_fields = ['amount', 'transaction_type', 'category', 'transaction_date']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        if data['transaction_type'] not in ['income', 'expense']:
            return jsonify({'success': False, 'error': 'Transaction type must be income or expense'}), 400
        
        if float(data['amount']) <= 0:
            return jsonify({'success': False, 'error': 'Amount must be greater than 0'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        transaction_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO erp_transactions (id, user_id, amount, transaction_type, category, 
            transaction_date, description, reference, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            transaction_id, user_id, float(data['amount']), data['transaction_type'], 
            data['category'], data['transaction_date'], data.get('description', ''),
            data.get('reference', ''), now, now
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Transaction created successfully',
            'id': transaction_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/transactions/<transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    """Update transaction"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if transaction exists
        cursor.execute("""
            SELECT id FROM erp_transactions 
            WHERE id = %s AND user_id = %s AND is_deleted = FALSE
        """, (transaction_id, user_id))
        
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Transaction not found'}), 404
        
        # Build update query
        update_fields = []
        params = []
        
        if 'amount' in data:
            if float(data['amount']) <= 0:
                return jsonify({'success': False, 'error': 'Amount must be greater than 0'}), 400
            update_fields.append("amount = %s")
            params.append(float(data['amount']))
        if 'transaction_type' in data:
            if data['transaction_type'] not in ['income', 'expense']:
                return jsonify({'success': False, 'error': 'Transaction type must be income or expense'}), 400
            update_fields.append("transaction_type = %s")
            params.append(data['transaction_type'])
        if 'category' in data:
            update_fields.append("category = %s")
            params.append(data['category'])
        if 'transaction_date' in data:
            update_fields.append("transaction_date = %s")
            params.append(data['transaction_date'])
        if 'description' in data:
            update_fields.append("description = %s")
            params.append(data['description'])
        if 'reference' in data:
            update_fields.append("reference = %s")
            params.append(data['reference'])
        
        if update_fields:
            update_fields.append("updated_at = %s")
            params.append(datetime.now().isoformat())
            params.extend([transaction_id, user_id])
            
            query = f"UPDATE erp_transactions SET {', '.join(update_fields)} WHERE id = %s AND user_id = %s AND is_deleted = FALSE"
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Transaction updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/transactions/categories', methods=['GET'])
def get_transaction_categories():
    """Get all transaction categories"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all unique categories for this user
        cursor.execute("""
            SELECT DISTINCT category FROM erp_transactions 
            WHERE user_id = %s AND is_deleted = FALSE
            ORDER BY category
        """, (user_id,))
        
        categories = [row['category'] for row in cursor.fetchall() if row['category']]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': categories
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ─── MODULE 8: Accounting Reports ──────────────────────────────────────────────

@erp_bp.route('/api/erp/reports/sales-summary', methods=['GET'])
def get_sales_summary():
    """
    Get sales summary report
    Query params: start_date, end_date
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Base query for sales
        query = """
            SELECT 
                COUNT(*) as total_invoices,
                SUM(total_amount) as total_sales,
                AVG(total_amount) as avg_invoice_value,
                SUM(CASE WHEN payment_status = 'paid' THEN total_amount ELSE 0 END) as paid_amount,
                SUM(CASE WHEN payment_status != 'paid' THEN total_amount ELSE 0 END) as pending_amount
            FROM erp_invoices 
            WHERE user_id = %s AND is_deleted = FALSE AND invoice_date IS NOT NULL
        """
        params = [user_id]
        
        if start_date:
            query += " AND invoice_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND invoice_date <= %s"
            params.append(end_date)
        
        cursor.execute(query, params)
        sales_data = cursor.fetchone()
        
        # Calculate top selling products
        products_query = """
            SELECT 
                p.product_name,
                SUM(ii.quantity) as total_sold,
                SUM(ii.total_amount) as revenue
            FROM erp_invoice_items ii
            JOIN erp_invoices i ON ii.invoice_id = i.id
            JOIN erp_products p ON ii.product_id = p.id
            WHERE i.user_id = %s AND i.is_deleted = FALSE
        """
        prod_params = [user_id]
        
        if start_date:
            products_query += " AND i.invoice_date >= %s"
            prod_params.append(start_date)
        if end_date:
            products_query += " AND i.invoice_date <= %s"
            prod_params.append(end_date)
        
        products_query += " GROUP BY p.id, p.product_name ORDER BY total_sold DESC LIMIT 5"
        
        cursor.execute(products_query, prod_params)
        top_products = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        result = {
            'summary': dict(sales_data) if sales_data else {
                'total_invoices': 0,
                'total_sales': 0,
                'avg_invoice_value': 0,
                'paid_amount': 0,
                'pending_amount': 0
            },
            'top_products': top_products,
            'date_filter': {
                'start_date': start_date,
                'end_date': end_date
            }
        }
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/reports/purchase-summary', methods=['GET'])
def get_purchase_summary():
    """Get purchase summary report"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Base query for purchases
        query = """
            SELECT 
                COUNT(*) as total_orders,
                SUM(total_amount) as total_purchases,
                AVG(total_amount) as avg_order_value,
                SUM(CASE WHEN status = 'Paid' THEN total_amount ELSE 0 END) as paid_amount,
                SUM(CASE WHEN status IN ('Pending', 'Partial') THEN total_amount ELSE 0 END) as pending_amount
            FROM erp_purchase_orders 
            WHERE user_id = %s AND is_deleted = FALSE
        """
        params = [user_id]
        
        if start_date:
            query += " AND created_at >= %s"
            params.append(start_date)
        if end_date:
            query += " AND created_at <= %s"
            params.append(end_date)
        
        cursor.execute(query, params)
        purchase_data = cursor.fetchone()
        
        # Calculate top suppliers
        suppliers_query = """
            SELECT 
                v.vendor_name,
                COUNT(*) as total_orders,
                SUM(total_amount) as total_spent
            FROM erp_purchase_orders po
            JOIN erp_vendors v ON po.vendor_id = v.id
            WHERE po.user_id = %s AND po.is_deleted = FALSE
        """
        supp_params = [user_id]
        
        if start_date:
            suppliers_query += " AND po.created_at >= %s"
            supp_params.append(start_date)
        if end_date:
            suppliers_query += " AND po.created_at <= %s"
            supp_params.append(end_date)
        
        suppliers_query += " GROUP BY v.id, v.vendor_name ORDER BY total_spent DESC LIMIT 5"
        
        cursor.execute(suppliers_query, supp_params)
        top_suppliers = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        result = {
            'summary': dict(purchase_data) if purchase_data else {
                'total_orders': 0,
                'total_purchases': 0,
                'avg_order_value': 0,
                'paid_amount': 0,
                'pending_amount': 0
            },
            'top_suppliers': top_suppliers,
            'date_filter': {
                'start_date': start_date,
                'end_date': end_date
            }
        }
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/reports/profit-loss', methods=['GET'])
def get_profit_loss():
    """
    Calculate profit & loss
    Formula: (Total Sales - COGS) - Total Expenses
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Calculate total sales
        sales_query = "SELECT SUM(total_amount) as total_sales FROM erp_invoices WHERE user_id = %s AND is_deleted = FALSE"
        sales_params = [user_id]
        
        # Calculate COGS (Cost of Goods Sold) - based on products sold
        cogs_query = """
            SELECT SUM(ii.quantity * p.cost_price) as total_cogs
            FROM erp_invoice_items ii
            JOIN erp_invoices i ON ii.invoice_id = i.id
            JOIN erp_products p ON ii.product_id = p.id
            WHERE i.user_id = %s AND i.is_deleted = FALSE AND p.cost_price IS NOT NULL
        """
        cogs_params = [user_id]
        
        # Calculate total expenses
        expenses_query = "SELECT SUM(amount) as total_expenses FROM erp_transactions WHERE user_id = %s AND transaction_type = 'expense' AND is_deleted = FALSE"
        expenses_params = [user_id]
        
        # Add date filters if provided
        if start_date:
            sales_query += " AND invoice_date >= %s"
            sales_params.append(start_date)
            cogs_query += " AND i.invoice_date >= %s"
            cogs_params.append(start_date)
            expenses_query += " AND transaction_date >= %s"
            expenses_params.append(start_date)
        
        if end_date:
            sales_query += " AND invoice_date <= %s"
            sales_params.append(end_date)
            cogs_query += " AND i.invoice_date <= %s"
            cogs_params.append(end_date)
            expenses_query += " AND transaction_date <= %s"
            expenses_params.append(end_date)
        
        # Execute queries
        cursor.execute(sales_query, sales_params)
        sales_result = cursor.fetchone()
        total_sales = float(sales_result['total_sales'] or 0)
        
        cursor.execute(cogs_query, cogs_params)
        cogs_result = cursor.fetchone()
        total_cogs = float(cogs_result['total_cogs'] or 0)
        
        cursor.execute(expenses_query, expenses_params)
        expenses_result = cursor.fetchone()
        total_expenses = float(expenses_result['total_expenses'] or 0)
        
        # Calculate gross profit and net profit
        gross_profit = total_sales - total_cogs
        net_profit = gross_profit - total_expenses
        
        conn.close()
        
        result = {
            'total_sales': total_sales,
            'total_cogs': total_cogs,
            'gross_profit': gross_profit,
            'total_expenses': total_expenses,
            'net_profit': net_profit,
            'profit_margin_percent': (net_profit / total_sales * 100) if total_sales > 0 else 0,
            'date_filter': {
                'start_date': start_date,
                'end_date': end_date
            }
        }
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ─── MODULE 9: Staff Management ────────────────────────────────────────────────

@erp_bp.route('/api/erp/staff/<staff_id>', methods=['GET'])
def get_staff_details(staff_id):
    """Get specific staff member details"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM erp_staff 
            WHERE id = %s AND company_id = %s AND is_deleted = FALSE
        """, (staff_id, user_id))
        
        staff = cursor.fetchone()
        if not staff:
            return jsonify({'success': False, 'error': 'Staff member not found'}), 404
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': dict(staff)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/staff/<staff_id>', methods=['PUT'])
def update_staff(staff_id):
    """Update staff member"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if staff exists
        cursor.execute("""
            SELECT id FROM erp_staff 
            WHERE id = %s AND company_id = %s AND is_deleted = FALSE
        """, (staff_id, user_id))
        
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Staff member not found'}), 404
        
        # Build update query
        update_fields = []
        params = []
        
        if 'name' in data:
            update_fields.append("name = %s")
            params.append(data['name'])
        if 'email' in data:
            update_fields.append("email = %s")
            params.append(data['email'])
        if 'phone' in data:
            update_fields.append("phone = %s")
            params.append(data['phone'])
        if 'position' in data:
            update_fields.append("position = %s")
            params.append(data['position'])
        if 'department' in data:
            update_fields.append("department = %s")
            params.append(data['department'])
        if 'salary' in data:
            update_fields.append("salary = %s")
            params.append(float(data['salary']))
        if 'hire_date' in data:
            update_fields.append("hire_date = %s")
            params.append(data['hire_date'])
        if 'address' in data:
            update_fields.append("address = %s")
            params.append(data['address'])
        
        if update_fields:
            update_fields.append("updated_at = %s")
            params.append(datetime.now().isoformat())
            params.extend([staff_id, user_id])
            
            query = f"UPDATE erp_staff SET {', '.join(update_fields)} WHERE id = %s AND company_id = %s AND is_deleted = FALSE"
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Staff updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/staff/<staff_id>/activate', methods=['POST'])
def toggle_staff_status(staff_id):
    """Activate/deactivate staff member"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if staff exists
        cursor.execute("""
            SELECT id, is_active FROM erp_staff 
            WHERE id = %s AND company_id = %s AND is_deleted = FALSE
        """, (staff_id, user_id))
        
        staff = cursor.fetchone()
        if not staff:
            return jsonify({'success': False, 'error': 'Staff member not found'}), 404
        
        # Toggle active status
        new_status = not staff['is_active']
        
        cursor.execute("""
            UPDATE erp_staff 
            SET is_active = %s, updated_at = %s 
            WHERE id = %s AND company_id = %s AND is_deleted = FALSE
        """, (new_status, datetime.now().isoformat(), staff_id, user_id))
        
        conn.commit()
        conn.close()
        
        status_text = 'activated' if new_status else 'deactivated'
        
        return jsonify({
            'success': True,
            'message': f'Staff member {status_text} successfully',
            'is_active': new_status
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ─── MODULE 10: Backup & Settings ──────────────────────────────────────────────

@erp_bp.route('/api/erp/backup/export', methods=['GET'])
def export_backup():
    """
    Export all user data as JSON backup
    Include: products, customers, vendors, invoices, etc.
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Define tables to backup
        tables_to_backup = [
            'erp_products', 'erp_customers', 'erp_vendors', 'erp_invoices', 
            'erp_invoice_items', 'erp_purchase_orders', 'erp_purchase_order_items',
            'erp_transactions', 'erp_staff', 'erp_leads', 'erp_batches',
            'erp_stock', 'erp_grn', 'erp_grn_items', 'erp_companies'
        ]
        
        backup_data = {}
        
        for table in tables_to_backup:
            query = f"SELECT * FROM {table} WHERE user_id = %s OR company_id = %s"
            cursor.execute(query, (user_id, user_id))
            rows = cursor.fetchall()
            backup_data[table] = [dict(row) for row in rows]
        
        conn.close()
        
        # Add metadata
        backup_data['_metadata'] = {
            'export_date': datetime.now().isoformat(),
            'user_id': user_id,
            'version': '1.0'
        }
        
        return jsonify({
            'success': True,
            'data': backup_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/backup/restore', methods=['POST'])
def restore_backup():
    """
    Restore data from backup file
    Validate backup integrity first
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        if 'backup_data' not in data:
            return jsonify({'success': False, 'error': 'Backup data is required'}), 400
        
        backup_data = data['backup_data']
        
        # Validate backup structure
        if '_metadata' not in backup_data:
            return jsonify({'success': False, 'error': 'Invalid backup format - missing metadata'}), 400
        
        # Start transaction for restoration
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # For safety, we'll only restore data for the current user
        # First, mark existing data as deleted (soft delete)
        tables_to_restore = [
            'erp_products', 'erp_customers', 'erp_vendors', 'erp_invoices', 
            'erp_invoice_items', 'erp_purchase_orders', 'erp_purchase_order_items',
            'erp_transactions', 'erp_staff', 'erp_leads', 'erp_batches',
            'erp_stock', 'erp_grn', 'erp_grn_items'
        ]
        
        conn.autocommit = False
        try:
            # Soft delete existing data for this user
            for table in tables_to_restore:
                if table in backup_data:
                    cursor.execute(f"UPDATE {table} SET is_deleted = TRUE WHERE user_id = %s OR company_id = %s", 
                                 (user_id, user_id))
            
            # Restore data from backup (only for current user)
            restored_counts = {}
            
            for table, records in backup_data.items():
                if table.startswith('_') or not isinstance(records, list):
                    continue
                
                if table in tables_to_restore:
                    restored_count = 0
                    for record in records:
                        # Only restore records that belong to current user
                        record_user_id = record.get('user_id') or record.get('company_id')
                        if record_user_id == user_id:
                            # Prepare insert statement
                            columns = [k for k, v in record.items() if k != 'id']
                            placeholders = ', '.join(['%s'] * len(columns))
                            column_names = ', '.join(columns)
                            
                            values = [record[col] for col in columns]
                            
                            cursor.execute(
                                f"INSERT INTO {table} (id, {column_names}) VALUES (%s, {placeholders}) "
                                f"ON CONFLICT (id) DO NOTHING",
                                [record.get('id', str(uuid.uuid4()))] + values
                            )
                            restored_count += 1
                    
                    restored_counts[table] = restored_count
            
            conn.commit()
            conn.autocommit = True
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'Backup restored successfully',
                'restored_counts': restored_counts
            })
        except Exception as e:
            conn.rollback()
            conn.autocommit = True
            conn.close()
            raise e
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/settings', methods=['GET'])
def get_settings():
    """Get user settings"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user settings
        cursor.execute("""
            SELECT * FROM erp_user_settings 
            WHERE user_id = %s
        """, (user_id,))
        
        settings = cursor.fetchone()
        conn.close()
        
        if settings:
            return jsonify({
                'success': True,
                'data': dict(settings)
            })
        else:
            # Return default settings
            default_settings = {
                'theme': 'wine',
                'currency': 'INR',
                'date_format': 'DD/MM/YYYY',
                'time_format': 'HH:mm',
                'notifications_enabled': True,
                'auto_backup_enabled': True,
                'backup_frequency': 'weekly',
                'low_stock_threshold': 10,
                'default_tax_rate': 18.0,
                'round_off_enabled': True
            }
            
            return jsonify({
                'success': True,
                'data': default_settings
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/settings', methods=['POST'])
def update_settings():
    """Update user settings"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if settings exist, if not create them
        cursor.execute("SELECT id FROM erp_user_settings WHERE user_id = %s", (user_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing settings
            update_fields = []
            params = []
            
            for key, value in data.items():
                if key != 'id' and key != 'user_id':  # Don't update id or user_id
                    update_fields.append(f"{key} = %s")
                    params.append(value)
            
            if update_fields:
                update_fields.append("updated_at = %s")
                params.append(datetime.now().isoformat())
                params.append(user_id)
                
                query = f"UPDATE erp_user_settings SET {', '.join(update_fields)} WHERE user_id = %s"
                cursor.execute(query, params)
        else:
            # Create new settings
            settings_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            
            # Prepare columns and values
            columns = ['id', 'user_id']
            values_placeholders = ['%s', '%s']
            values = [settings_id, user_id]
            
            for key, value in data.items():
                if key != 'id' and key != 'user_id':
                    columns.append(key)
                    values_placeholders.append('%s')
                    values.append(value)
            
            columns.append('created_at')
            columns.append('updated_at')
            values_placeholders.append('%s')
            values_placeholders.append('%s')
            values.append(now)
            values.append(now)
            
            query = f"INSERT INTO erp_user_settings ({', '.join(columns)}) VALUES ({', '.join(values_placeholders)})"
            cursor.execute(query, values)
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Settings updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500