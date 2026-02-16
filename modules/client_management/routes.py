"""
Client Management Routes - Super Admin Only (bizpulse.erp@gmail.com)
Comprehensive client management system for BizPulse super admins
"""

from flask import Blueprint, request, jsonify, session, render_template
from modules.shared.database import get_db_connection, generate_id, hash_password
from modules.shared.auth_decorators import require_super_admin
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

client_management_bp = Blueprint('client_management', __name__, url_prefix='/admin')

# Add a simple test route
@client_management_bp.route('/test-reset')
def test_reset():
    return jsonify({'message': 'Reset route working'})

def is_super_admin():
    """Check if current user is super admin"""
    return session.get('is_super_admin', False)

# ==================== DASHBOARD ROUTES ====================

@client_management_bp.route('/clients')
@require_super_admin
def client_management_dashboard():
    """Super Admin Client Management Dashboard"""
    return render_template('client_management_dashboard.html')

@client_management_bp.route('/clients/analytics')
@require_super_admin
def client_analytics():
    """Client Analytics Dashboard"""
    return render_template('client_analytics.html')

# ==================== CLIENT CRUD OPERATIONS ====================

@client_management_bp.route('/api/test-clients', methods=['GET'])
def test_clients():
    """Test endpoint to check clients"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM clients')
        count = cursor.fetchone()[0]
        conn.close()
        return jsonify({'success': True, 'count': count, 'message': f'Found {count} clients'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@client_management_bp.route('/api/clients', methods=['GET'])
def get_all_clients():
    """Get all clients with detailed information"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Simple query to get all clients
        cursor.execute('''
            SELECT id, company_name, contact_email, contact_name, phone_number, 
                   whatsapp_number, business_address, business_type, gst_number,
                   username, is_active, last_login, created_at, updated_at,
                   city, state, country, password_plain
            FROM clients
            ORDER BY created_at DESC
        ''')
        
        clients = []
        for row in cursor.fetchall():
            clients.append({
                'id': row[0],
                'company_name': row[1] or 'Unknown Company',
                'contact_email': row[2] or '',
                'contact_name': row[3] or '',
                'phone_number': row[4] or '',
                'whatsapp_number': row[5] or '',
                'business_address': row[6] or '',
                'business_type': row[7] or 'retail',
                'gst_number': row[8] or '',
                'username': row[9] or '',
                'is_active': bool(row[10]) if row[10] is not None else True,
                'last_login': row[11],
                'created_at': row[12],
                'updated_at': row[13],
                'city': row[14] or '',
                'state': row[15] or '',
                'country': row[16] or 'India',
                'password_plain': row[17] or 'admin123',
                'product_count': 0,
                'bill_count': 0,
                'total_revenue': 0.0
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'clients': clients,
            'pagination': {
                'page': 1,
                'per_page': len(clients),
                'total': len(clients),
                'pages': 1
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching clients: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@client_management_bp.route('/api/clients', methods=['POST', 'OPTIONS'])
def create_client():
    """Create new client or handle special actions"""
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return jsonify({'success': True})
    
    try:
        # Try multiple ways to get JSON data
        data = None
        
        # Method 1: Standard get_json
        try:
            data = request.get_json(force=True, silent=False)
        except Exception as e:
            logger.warning(f"get_json failed: {e}")
        
        # Method 2: Parse from data
        if not data:
            try:
                import json
                data = json.loads(request.data.decode('utf-8'))
            except Exception as e:
                logger.warning(f"json.loads failed: {e}")
        
        # Method 3: Empty dict fallback
        if not data:
            data = {}
        
        logger.info(f"📥 Received data: {data}")
        logger.info(f"📥 Action: {data.get('action')}")
        logger.info(f"📥 Content-Type: {request.content_type}")
        
        # Handle password reset action - skip validation for this
        if data.get('action') == 'reset_password':
            client_id = data.get('client_id')
            new_password = data.get('password', '').strip()
            
            if not client_id or not new_password:
                return jsonify({
                    'success': False,
                    'message': 'Client ID and password are required'
                }), 400
            
            if len(new_password) < 6:
                return jsonify({
                    'success': False,
                    'message': 'Password must be at least 6 characters long'
                }), 400
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if client exists
            cursor.execute('SELECT company_name FROM clients WHERE id = ?', (client_id,))
            client = cursor.fetchone()
            if not client:
                conn.close()
                return jsonify({'success': False, 'message': 'Client not found'}), 404
            
            # Update password
            password_hash = hash_password(new_password)
            cursor.execute('''
                UPDATE clients 
                SET password_hash = ?, password_plain = ?, updated_at = ?
                WHERE id = ?
            ''', (password_hash, new_password, datetime.now().isoformat(), client_id))
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'Password reset successfully',
                'new_password': new_password
            })
        
        # Regular client creation logic - only validate if not password reset
        required_fields = ['company_name', 'contact_email', 'username']
        for field in required_fields:
            if not data.get(field, '').strip():
                return jsonify({
                    'success': False,
                    'message': f'{field.replace("_", " ").title()} is required'
                }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if username already exists
        cursor.execute('SELECT id FROM clients WHERE username = ?', (data['username'],))
        if cursor.fetchone():
            return jsonify({
                'success': False,
                'message': f'Username "{data["username"]}" already exists'
            }), 400
        
        # Check if email already exists
        cursor.execute('SELECT id FROM clients WHERE contact_email = ?', (data['contact_email'],))
        if cursor.fetchone():
            return jsonify({
                'success': False,
                'message': f'Email "{data["contact_email"]}" already exists'
            }), 400
        
        # Generate client ID and hash password
        client_id = generate_id()
        password = data.get('password')
        
        # Require strong password
        if not password or len(password) < 8:
            return jsonify({
                'success': False,
                'error': 'Password must be at least 8 characters long'
            }), 400
        
        password_hash = hash_password(password)
        
        # Insert new client
        cursor.execute('''
            INSERT INTO clients (
                id, company_name, contact_email, contact_name, phone_number,
                whatsapp_number, business_address, business_type, gst_number,
                username, password_hash, password_plain, is_active, city, state, country,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            client_id,
            data.get('company_name'),
            data.get('contact_email'),
            data.get('contact_name', ''),
            data.get('phone_number', ''),
            data.get('whatsapp_number', ''),
            data.get('business_address', ''),
            data.get('business_type', 'retail'),
            data.get('gst_number', ''),
            data.get('username'),
            password_hash,
            password,
            1,  # is_active
            data.get('city', ''),
            data.get('state', ''),
            data.get('country', 'India'),
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Client created: {data['company_name']} ({data['username']})")
        
        return jsonify({
            'success': True,
            'message': 'Client created successfully',
            'client_id': client_id,
            'temp_password': password
        })
        
    except Exception as e:
        logger.error(f"Error in client operation: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@client_management_bp.route('/api/clients/<client_id>/login-as', methods=['POST'])
@require_super_admin
def login_as_client(client_id):
    """Login as client (impersonation)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, company_name, contact_email, contact_name, username, is_active
            FROM clients
            WHERE id = ?
        ''', (client_id,))
        
        client = cursor.fetchone()
        if not client:
            return jsonify({'success': False, 'message': 'Client not found'}), 404
        
        if not client[5]:  # is_active
            return jsonify({'success': False, 'message': 'Client account is inactive'}), 400
        
        conn.close()
        
        # Store original admin session
        session['original_admin_id'] = session.get('user_id')
        session['original_admin_type'] = session.get('user_type')
        session['original_is_super_admin'] = session.get('is_super_admin')
        
        # Set client session
        session['user_id'] = client[0]
        session['user_type'] = 'client'
        session['user_name'] = client[3] or client[1]  # contact_name or company_name
        session['email'] = client[2]
        session['username'] = client[4]
        session['is_super_admin'] = False
        session['impersonating'] = True
        
        logger.info(f"✅ Admin impersonating client: {client[1]} ({client_id})")
        
        return jsonify({
            'success': True,
            'message': f'Now logged in as {client[1]}',
            'redirect_url': '/retail/dashboard'
        })
        
    except Exception as e:
        logger.error(f"Error logging in as client: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@client_management_bp.route('/api/clients/<client_id>', methods=['PUT'])
@require_super_admin
def update_client(client_id):
    """Update client information"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if client exists
        cursor.execute('SELECT id FROM clients WHERE id = ?', (client_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': 'Client not found'}), 404
        
        # Build update query dynamically
        update_fields = []
        params = []
        
        updatable_fields = [
            'company_name', 'contact_email', 'contact_name', 'phone_number',
            'whatsapp_number', 'business_address', 'business_type', 'gst_number',
            'username', 'city', 'state', 'country', 'is_active'
        ]
        
        for field in updatable_fields:
            if field in data:
                update_fields.append(f"{field} = ?")
                params.append(data[field])
        
        if not update_fields:
            return jsonify({'success': False, 'message': 'No fields to update'}), 400
        
        # Add updated_at
        update_fields.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(client_id)
        
        query = f"UPDATE clients SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, params)
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Client updated: {client_id}")
        
        return jsonify({
            'success': True,
            'message': 'Client updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating client: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@client_management_bp.route('/api/clients/<client_id>/reset-password', methods=['POST', 'OPTIONS'])
def reset_client_password(client_id):
    """Reset client password with custom password"""
    logger.info(f"🔑 Password reset request for client: '{client_id}'")
    logger.info(f"🔑 Client ID type: {type(client_id)}")
    logger.info(f"🔑 Client ID length: {len(client_id) if client_id else 0}")
    
    if request.method == 'OPTIONS':
        return jsonify({'success': True})
        
    try:
        data = request.get_json(force=True, silent=True)
        logger.info(f"📥 Reset password data: {data}")
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
            
        new_password = data.get('password', '').strip()
        
        if not new_password:
            return jsonify({
                'success': False,
                'message': 'Password is required'
            }), 400
        
        if len(new_password) < 6:
            return jsonify({
                'success': False,
                'message': 'Password must be at least 6 characters long'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if client exists - log the query
        logger.info(f"🔍 Looking for client with ID: '{client_id}'")
        cursor.execute('SELECT id, company_name FROM clients WHERE id = ?', (client_id,))
        client = cursor.fetchone()
        logger.info(f"🔍 Query result: {client}")
        
        if not client:
            # Try to find similar clients for debugging
            cursor.execute('SELECT id, company_name FROM clients LIMIT 5')
            sample_clients = cursor.fetchall()
            logger.info(f"🔍 Sample clients in DB: {sample_clients}")
            conn.close()
            return jsonify({'success': False, 'message': 'Client not found'}), 404
        
        company_name = client[1]
        
        # Update password and store plain text for admin viewing
        password_hash = hash_password(new_password)
        cursor.execute('''
            UPDATE clients 
            SET password_hash = ?, password_plain = ?, updated_at = ?
            WHERE id = ?
        ''', (password_hash, new_password, datetime.now().isoformat(), client_id))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'message': 'Failed to update password'}), 500
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Password reset successfully',
            'new_password': new_password
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

@client_management_bp.route('/api/clients/analytics/summary', methods=['GET'])
@require_super_admin
def get_client_analytics():
    """Get client analytics summary"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total clients
        cursor.execute('SELECT COUNT(*) FROM clients WHERE is_active = 1')
        total_clients = cursor.fetchone()[0]
        
        # New clients this month
        cursor.execute('''
            SELECT COUNT(*) FROM clients 
            WHERE created_at >= date('now', 'start of month')
        ''')
        new_this_month = cursor.fetchone()[0]
        
        # Clients by business type
        cursor.execute('''
            SELECT business_type, COUNT(*) as count
            FROM clients 
            WHERE is_active = 1
            GROUP BY business_type
            ORDER BY count DESC
        ''')
        business_types = [{'type': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        # Top clients by revenue
        cursor.execute('''
            SELECT c.company_name, c.contact_email, 
                   COALESCE(SUM(b.total_amount), 0) as total_revenue,
                   COUNT(b.id) as bill_count
            FROM clients c
            LEFT JOIN bills b ON c.id = b.user_id
            WHERE c.is_active = 1
            GROUP BY c.id, c.company_name, c.contact_email
            ORDER BY total_revenue DESC
            LIMIT 10
        ''')
        top_clients = []
        for row in cursor.fetchall():
            top_clients.append({
                'company_name': row[0],
                'contact_email': row[1],
                'total_revenue': float(row[2]),
                'bill_count': row[3]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'analytics': {
                'summary': {
                    'total_clients': total_clients,
                    'new_this_month': new_this_month
                },
                'business_types': business_types,
                'top_clients': top_clients
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching analytics: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500