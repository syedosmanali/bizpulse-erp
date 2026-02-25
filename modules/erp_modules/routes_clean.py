"""
ERP Modules - Clean Routes Implementation
Covers: Authentication, Company Setup, Bank Management, Purchase, PO, GRN, Batch & Expiry,
        Barcode, Vendor/Supplier, CRM, Payments, Income & Expense, Accounting,
        Staff & Operator, Backup & Settings
"""

from flask import Blueprint, render_template, jsonify, session, request
from modules.shared.database import get_db_connection, get_db_type
from modules.erp_modules.service import ERPService, AuthenticationService
import traceback, uuid, json
from datetime import datetime, timedelta

erp_bp = Blueprint('erp', __name__)

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

# ─── API: Authentication ───────────────────────────────────────────────────────

@erp_bp.route('/api/auth/login', methods=['POST'])
def login():
    """
    User login endpoint
    Supports three user types: Admin, Operator, Business Owner
    Returns session token valid for 24 hours
    """
    try:
        data = request.json
        email = data.get('email', '').strip()
        password = data.get('password', '')
        user_type = data.get('user_type', 'business_owner').lower()
        
        # Validate input
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email and password are required',
                'error_code': 'MISSING_CREDENTIALS'
            }), 400
        
        # Validate user type
        valid_user_types = ['admin', 'operator', 'business_owner']
        if user_type not in valid_user_types:
            return jsonify({
                'success': False,
                'error': f'Invalid user type. Must be one of: {", ".join(valid_user_types)}',
                'error_code': 'INVALID_USER_TYPE'
            }), 400
        
        # Authenticate user
        auth_service = AuthenticationService()
        result = auth_service.authenticate_user(email, password, user_type)
        
        if result['success']:
            # Set session
            session['user_id'] = result['user_id']
            session['user_type'] = user_type
            session['email'] = email
            session['name'] = result.get('name', '')
            session['company_id'] = result.get('company_id')
            
            # For employees, also store client_id
            if user_type == 'employee' and 'client_id' in result:
                session['client_id'] = result['client_id']
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': result['user_id'],
                    'email': email,
                    'name': result.get('name', ''),
                    'user_type': user_type,
                    'company_id': result.get('company_id')
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error'],
                'error_code': result.get('error_code', 'AUTH_FAILED')
            }), 401
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred during login',
            'error_code': 'INTERNAL_ERROR'
        }), 500

@erp_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    """User logout endpoint - clears session"""
    try:
        session.clear()
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to logout'
        }), 500

@erp_bp.route('/api/auth/change-password', methods=['POST'])
def change_password():
    """Change user password"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
        data = request.json
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password or not new_password:
            return jsonify({
                'success': False,
                'error': 'Current and new passwords are required'
            }), 400
        
        auth_service = AuthenticationService()
        result = auth_service.change_password(user_id, current_password, new_password)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Password changed successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to change password'
        }), 500

@erp_bp.route('/api/auth/session', methods=['GET'])
def check_session():
    """Check if user session is valid"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'No active session',
                'authenticated': False
            }), 401
        
        return jsonify({
            'success': True,
            'authenticated': True,
            'user': {
                'id': user_id,
                'email': session.get('email', ''),
                'name': session.get('name', ''),
                'user_type': session.get('user_type', ''),
                'company_id': session.get('company_id')
            }
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Session check failed',
            'authenticated': False
        }), 500

# ─── API: Company Setup ────────────────────────────────────────────────────────

@erp_bp.route('/api/erp/company', methods=['GET'])
def get_company():
    """Get company information for the logged-in user"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        db = get_db_type()
        ph = '%s' if db == 'postgresql' else '?'
        
        # For employees, get company through client_id
        user_type = session.get('user_type')
        if user_type == 'employee':
            client_id = session.get('client_id')
            cursor.execute(f"SELECT * FROM erp_companies WHERE id={ph}", (client_id,))
        else:
            cursor.execute(f"SELECT * FROM erp_companies WHERE owner_id={ph}", (user_id,))
        
        company = cursor.fetchone()
        conn.close()
        
        if company:
            return jsonify({'success': True, 'data': dict(company)})
        else:
            return jsonify({'success': False, 'error': 'Company not found'})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/company', methods=['POST'])
def create_company():
    """Create company setup for the user"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        db = get_db_type()
        ph = '%s' if db == 'postgresql' else '?'
        
        now = datetime.now().isoformat()
        company_id = str(uuid.uuid4())
        
        cursor.execute(f"""
            INSERT INTO erp_companies (id, owner_id, company_name, company_email, company_phone, 
            company_address, company_gst, company_pan, company_logo, created_at, updated_at)
            VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})
        """, (
            company_id, user_id, 
            data.get('company_name', ''),
            data.get('company_email', ''), 
            data.get('company_phone', ''),
            data.get('company_address', ''),
            data.get('company_gst', ''),
            data.get('company_pan', ''),
            data.get('company_logo', ''),
            now, now
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': 'Company created successfully',
            'id': company_id
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@erp_bp.route('/api/erp/company', methods=['PUT'])
def update_company():
    """Update company information"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        db = get_db_type()
        ph = '%s' if db == 'postgresql' else '?'
        
        now = datetime.now().isoformat()
        
        # For employees, get company through client_id
        user_type = session.get('user_type')
        if user_type == 'employee':
            client_id = session.get('client_id')
            cursor.execute(f"""
                UPDATE erp_companies 
                SET company_name={ph}, company_email={ph}, company_phone={ph}, 
                    company_address={ph}, company_gst={ph}, company_pan={ph}, 
                    company_logo={ph}, updated_at={ph}
                WHERE id={ph}
            """, (
                data.get('company_name'), data.get('company_email'), data.get('company_phone'),
                data.get('company_address'), data.get('company_gst'), data.get('company_pan'),
                data.get('company_logo'), now, client_id
            ))
        else:
            cursor.execute(f"""
                UPDATE erp_companies 
                SET company_name={ph}, company_email={ph}, company_phone={ph}, 
                    company_address={ph}, company_gst={ph}, company_pan={ph}, 
                    company_logo={ph}, updated_at={ph}
                WHERE owner_id={ph}
            """, (
                data.get('company_name'), data.get('company_email'), data.get('company_phone'),
                data.get('company_address'), data.get('company_gst'), data.get('company_pan'),
                data.get('company_logo'), now, user_id
            ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Company updated successfully'})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
