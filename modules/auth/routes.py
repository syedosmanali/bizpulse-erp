"""
Authentication routes
COPIED AS-IS from app.py
"""

from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template, make_response, g
from .service import AuthService
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()

@auth_bp.route('/api/set_language', methods=['POST'])
def api_set_language():
    try:
        data = request.get_json(force=True)
        lang = data.get('lang') if isinstance(data, dict) else None
        if not lang:
            return jsonify({'status':'error','message':'missing lang'}), 400
        resp = make_response(jsonify({'status':'ok'}))
        # set cookie for 1 year
        resp.set_cookie('app_lang', lang, max_age=60*60*24*365, httponly=False)
        return resp
    except Exception as e:
        return jsonify({'status':'error','message': str(e)}), 500

@auth_bp.route('/api/auth/login', methods=['POST'])
@auth_bp.route('/api/auth/unified-login', methods=['POST'])
def api_login():
    """Unified login for all user types with proper database authentication"""
    data = request.get_json()
    
    # Handle both login_id and loginId (mobile uses loginId)
    login_id = data.get('loginId') or data.get('login_id') or data.get('email', '').strip()
    password = data.get('password', '').strip()
    
    logger.info(f"🔐 Login attempt for: {login_id}")
    
    if not login_id or not password:
        logger.warning(f"❌ Missing credentials")
        return jsonify({'message': 'Login ID and password are required'}), 400
    
    try:
        result = auth_service.authenticate_user(login_id, password)
        logger.info(f"🔍 Auth result: {result.get('success')} - {result.get('message', 'No message')}")
        
        if result['success']:
            # Set session data
            for key, value in result['session_data'].items():
                session[key] = value
            session.permanent = True
            
            logger.info(f"✅ User login successful: {result['user']['email']} (Type: {result['user']['type']})")
            
            return jsonify({
                "message": "Login successful",
                "token": result['token'],
                "user": result['user']
            })
        else:
            logger.warning(f"❌ Login failed: {result.get('message')}")
            return jsonify({"message": result.get('message', 'Invalid credentials')}), 401
        
    except Exception as e:
        logger.error(f"💥 Login error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"message": "Login error", "error": str(e)}), 500

@auth_bp.route('/api/auth/user-info', methods=['GET'])
def get_user_info():
    """Get current user information including role and profile data"""
    try:
        result = auth_service.get_user_info(session)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in get_user_info: {e}")
        return jsonify({
            "user_id": session.get('user_id'),
            "user_type": session.get('user_type'),
            "user_name": session.get('user_name'),
            "email": session.get('email'),           # Include session email
            "username": session.get('username'),     # Include username
            "profile_picture": None,
            "is_super_admin": session.get('is_super_admin', False),
            "staff_role": session.get('staff_role')
        })

@auth_bp.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.json
    
    try:
        result = auth_service.register_user(data)
        if result['success']:
            return jsonify({"message": "Registration successful", "user_id": result['user_id']})
        else:
            return jsonify({"message": result['message']}), 400
    except Exception as e:
        return jsonify({"message": "Registration error", "error": str(e)}), 500

@auth_bp.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Generate password reset token and allow user to set new password"""
    data = request.get_json()
    email_or_username = data.get('email', '').strip() or data.get('username', '').strip()
    
    if not email_or_username:
        return jsonify({'message': 'Email or username is required'}), 400
    
    try:
        result = auth_service.forgot_password(email_or_username)
        if result['success']:
            return jsonify(result)
        else:
            return jsonify({'message': result['message']}), 404
    except Exception as e:
        return jsonify({'message': 'Password reset error', 'error': str(e)}), 500

@auth_bp.route('/api/auth/logout', methods=['POST'])
def api_logout():
    """Logout user and clear session"""
    try:
        # Clear all session data
        session.clear()
        
        logger.info('✅ User logged out successfully')
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        })
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({
            'success': False,
            'message': 'Logout error',
            'error': str(e)
        }), 500

@auth_bp.route('/api/auth/client-login', methods=['POST'])
def client_login():
    """Client login with username/password for mobile app"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400
        
        from modules.shared.database import get_db_connection, get_db_type
        import hashlib
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get database type to handle query differences
        db_type = get_db_type()
        
        # Try to find client by username or email
        if db_type == 'postgresql':
            cursor.execute('''
                SELECT id, company_name, username, contact_email, password_hash, is_active
                FROM clients
                WHERE username = %s OR contact_email = %s
            ''', (username, username))
        else:
            cursor.execute('''
                SELECT id, company_name, username, contact_email, password_hash, is_active
                FROM clients
                WHERE username = ? OR contact_email = ?
            ''', (username, username))
        
        client = cursor.fetchone()
        conn.close()
        
        if not client:
            logger.warning(f"❌ Client not found: {username}")
            return jsonify({
                'success': False,
                'message': 'Invalid username or password'
            }), 401
        
        # Handle both dict and tuple results
        if hasattr(client, 'keys'):  # DictRow from PostgreSQL
            client_id = client['id']
            company_name = client['company_name']
            client_username = client['username']
            email = client['contact_email']
            password_hash = client['password_hash']
            is_active = client['is_active']
        else:  # Tuple from SQLite
            client_id, company_name, client_username, email, password_hash, is_active = client
        
        # Check if client is active
        if not is_active:
            logger.warning(f"❌ Client account inactive: {username}")
            return jsonify({
                'success': False,
                'message': 'Account is inactive. Please contact support.'
            }), 401
        
        # Verify password
        input_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if input_hash != password_hash:
            logger.warning(f"❌ Invalid password for client: {username}")
            return jsonify({
                'success': False,
                'message': 'Invalid username or password'
            }), 401
        
        # Update last login
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if db_type == 'postgresql':
            cursor.execute('''
                UPDATE clients 
                SET last_login = CURRENT_TIMESTAMP,
                    login_count = COALESCE(login_count, 0) + 1
                WHERE id = %s
            ''', (client_id,))
        else:
            cursor.execute('''
                UPDATE clients 
                SET last_login = CURRENT_TIMESTAMP,
                    login_count = COALESCE(login_count, 0) + 1
                WHERE id = ?
            ''', (client_id,))
        
        conn.commit()
        conn.close()
        
        # Set session
        session['user_id'] = client_id
        session['user_type'] = 'client'
        session['user_name'] = company_name
        session['email'] = email
        session['username'] = client_username
        session.permanent = True
        
        logger.info(f"✅ Client login successful: {username} ({company_name})")
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user_type': 'client',
            'client_id': client_id,
            'company_name': company_name,
            'username': client_username,
            'email': email
        })
        
    except Exception as e:
        logger.error(f"Client login error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': 'Login error',
            'error': str(e)
        }), 500


# ============================================================================
# CLIENT MANAGEMENT APIs
# ============================================================================

@auth_bp.route('/api/admin/clients', methods=['GET'])
def get_all_clients():
    """Get all clients for admin"""
    try:
        from modules.shared.database import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, company_name, contact_email, contact_name, phone_number, 
                   username, is_active, last_login, created_at, business_type,
                   city, state, country
            FROM clients
            ORDER BY created_at DESC
        ''')
        
        clients = []
        for row in cursor.fetchall():
            clients.append({
                'id': row[0],
                'company_name': row[1],
                'contact_email': row[2],
                'contact_name': row[3],
                'phone_number': row[4],
                'username': row[5],
                'is_active': row[6],
                'last_login': row[7],
                'created_at': row[8],
                'business_type': row[9],
                'city': row[10],
                'state': row[11],
                'country': row[12]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'clients': clients,
            'total': len(clients)
        })
        
    except Exception as e:
        logger.error(f"Error fetching clients: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@auth_bp.route('/api/admin/clients', methods=['POST'])
def create_client():
    """Create new client"""
    try:
        from modules.shared.database import get_db_connection, generate_id, get_db_type
        import hashlib
        
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({
                'success': False,
                'message': 'Username is required'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        db_type = get_db_type()
        ph = '%s' if db_type == 'postgresql' else '?'
        
        # Check if username already exists
        cursor.execute(f'SELECT id FROM clients WHERE username = {ph}', (username,))
        existing_client = cursor.fetchone()
        
        if existing_client:
            conn.close()
            return jsonify({
                'success': False,
                'message': f'Username "{username}" already exists. Please choose a different username.'
            }), 400
        
        # Check if email already exists
        email = data.get('contact_email', '').strip()
        if email:
            cursor.execute(f'SELECT id FROM clients WHERE contact_email = {ph}', (email,))
            existing_email = cursor.fetchone()
            
            if existing_email:
                conn.close()
                return jsonify({
                    'success': False,
                    'message': f'Email "{email}" already exists. Please use a different email.'
                }), 400
        
        # Generate client ID
        client_id = generate_id()
        
        # Hash password - require password to be provided
        password = data.get('password')
        if not password or len(password) < 8:
            return jsonify({
                'success': False,
                'error': 'Password must be at least 8 characters long'
            }), 400
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        is_active_val = True if db_type == 'postgresql' else 1
        
        cursor.execute(f'''
            INSERT INTO clients (
                id, company_name, contact_email, contact_name, phone_number,
                username, password_hash, is_active, business_type, country
            ) VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})
        ''', (
            client_id,
            data.get('company_name'),
            data.get('contact_email'),
            data.get('contact_name'),
            data.get('phone_number'),
            username,
            password_hash,
            is_active_val,
            data.get('business_type', 'retail'),
            data.get('country', 'India')
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Client created successfully',
            'client_id': client_id
        })
        
    except Exception as e:
        logger.error(f"Error creating client: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@auth_bp.route('/api/admin/clients/<client_id>', methods=['DELETE'])
def delete_client(client_id):
    """Delete client"""
    try:
        from modules.shared.database import get_db_connection, get_db_type
        
        conn = get_db_connection()
        cursor = conn.cursor()
        db_type = get_db_type()
        ph = '%s' if db_type == 'postgresql' else '?'
        
        cursor.execute(f'DELETE FROM clients WHERE id = {ph}', (client_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Client deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting client: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@auth_bp.route('/api/admin/login-as-client', methods=['POST'])
def login_as_client():
    """Admin login as client"""
    try:
        data = request.get_json()
        client_id = data.get('clientId')
        
        from modules.shared.database import get_db_connection, get_db_type
        
        conn = get_db_connection()
        cursor = conn.cursor()
        db_type = get_db_type()
        ph = '%s' if db_type == 'postgresql' else '?'
        
        cursor.execute(f'''
            SELECT id, company_name, contact_email, username
            FROM clients
            WHERE id = {ph}
        ''', (client_id,))
        
        client = cursor.fetchone()
        conn.close()
        
        if client:
            # Handle both dict and tuple results
            if hasattr(client, 'keys'):
                c_id, c_name, c_email, c_username = client['id'], client['company_name'], client['contact_email'], client['username']
            else:
                c_id, c_name, c_email, c_username = client[0], client[1], client[2], client[3]
            # Set session as this client
            session['user_id'] = c_id
            session['user_type'] = 'client'
            session['user_name'] = c_name
            session['email'] = c_email
            session['username'] = c_username
            session.permanent = True
            
            return jsonify({
                'success': True,
                'message': 'Logged in as client',
                'redirect': '/retail/dashboard'
            })
        else:
            return jsonify({'success': False, 'message': 'Client not found'}), 404
        
    except Exception as e:
        logger.error(f"Error logging in as client: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================================
# CLIENT PROFILE APIs
# ============================================================================

@auth_bp.route('/api/client/profile', methods=['GET'])
def get_client_profile():
    """Get client profile information"""
    try:
        user_id = session.get('user_id')
        user_type = session.get('user_type')
        
        if not user_id or user_type != 'client':
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        from modules.shared.database import get_db_connection, get_db_type
        
        conn = get_db_connection()
        cursor = conn.cursor()
        db_type = get_db_type()
        ph = '%s' if db_type == 'postgresql' else '?'
        
        cursor.execute(f'''
            SELECT contact_name, company_name, contact_email, phone_number, 
                   profile_picture, city, state, country, business_type
            FROM clients
            WHERE id = {ph}
        ''', (user_id,))
        
        client = cursor.fetchone()
        conn.close()
        
        if client:
            # Handle both dict (PostgreSQL) and tuple (SQLite) results
            if hasattr(client, 'keys'):
                return jsonify({
                    'success': True,
                    'full_name': client['contact_name'] or client['company_name'],
                    'company_name': client['company_name'],
                    'email': client['contact_email'],
                    'phone': client['phone_number'],
                    'profile_picture': client['profile_picture'],
                    'city': client['city'],
                    'state': client['state'],
                    'country': client['country'],
                    'business_type': client['business_type']
                })
            else:
                return jsonify({
                    'success': True,
                    'full_name': client[0] or client[1],
                    'company_name': client[1],
                    'email': client[2],
                    'phone': client[3],
                    'profile_picture': client[4],
                    'city': client[5],
                    'state': client[6],
                    'country': client[7],
                    'business_type': client[8]
                })
        else:
            return jsonify({'success': False, 'message': 'Profile not found'}), 404
        
    except Exception as e:
        logger.error(f"Error getting client profile: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@auth_bp.route('/api/client/profile', methods=['PUT'])
def update_client_profile():
    """Update client profile information"""
    try:
        user_id = session.get('user_id')
        user_type = session.get('user_type')
        
        if not user_id or user_type != 'client':
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        data = request.get_json()
        
        from modules.shared.database import get_db_connection, get_db_type
        
        conn = get_db_connection()
        cursor = conn.cursor()
        db_type = get_db_type()
        ph = '%s' if db_type == 'postgresql' else '?'
        
        # Update client profile
        cursor.execute(f'''
            UPDATE clients 
            SET contact_name = {ph}, contact_email = {ph}, phone_number = {ph}, company_name = {ph}
            WHERE id = {ph}
        ''', (
            data.get('full_name'),
            data.get('email'),
            data.get('phone'),
            data.get('company_name'),
            user_id
        ))
        
        conn.commit()
        conn.close()
        
        # Update session data
        session['user_name'] = data.get('full_name') or data.get('company_name')
        session['email'] = data.get('email')
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating client profile: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@auth_bp.route('/api/client/profile/picture', methods=['POST'])
def upload_profile_picture():
    """Upload client profile picture"""
    try:
        user_id = session.get('user_id')
        user_type = session.get('user_type')
        
        if not user_id or user_type != 'client':
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        if 'profile_picture' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'}), 400
        
        file = request.files['profile_picture']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'success': False, 'message': 'Invalid file type. Only PNG, JPG, JPEG, GIF allowed'}), 400
        
        # Save file
        import os
        from werkzeug.utils import secure_filename
        
        # Create uploads directory if it doesn't exist
        upload_folder = os.path.join('static', 'uploads', 'profiles')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Generate unique filename
        import uuid
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{user_id}_{uuid.uuid4().hex[:8]}.{file_extension}"
        file_path = os.path.join(upload_folder, filename)
        
        file.save(file_path)
        
        # Update database
        profile_picture_url = f"/static/uploads/profiles/{filename}"
        
        from modules.shared.database import get_db_connection, get_db_type
        
        conn = get_db_connection()
        cursor = conn.cursor()
        db_type = get_db_type()
        ph = '%s' if db_type == 'postgresql' else '?'
        
        cursor.execute(f'''
            UPDATE clients 
            SET profile_picture = {ph}
            WHERE id = {ph}
        ''', (profile_picture_url, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Profile picture uploaded successfully',
            'profile_picture_url': profile_picture_url
        })
        
    except Exception as e:
        logger.error(f"Error uploading profile picture: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
