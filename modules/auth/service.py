"""
Authentication service
COPIED AS-IS from app.py
"""

import sqlite3
from modules.shared.database import get_db_connection, generate_id, hash_password
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AuthService:
    
    def authenticate_user(self, login_id, password):
        """Authenticate user against all user tables"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        from modules.shared.database import get_db_type
        db_type = get_db_type()
        placeholder = '%s' if db_type == 'postgresql' else '?'
        
        try:
            # First check users table (includes BizPulse admin users)
            cursor.execute(f"SELECT id, email, business_name, business_type, password_hash, is_active FROM users WHERE email = {placeholder}", (login_id,))
            user = cursor.fetchone()
            
            if user:
                user_dict = dict(user) if hasattr(user, 'keys') else {
                    'id': user[0], 'email': user[1], 'business_name': user[2],
                    'business_type': user[3], 'password_hash': user[4], 'is_active': user[5]
                }
                
                if hash_password(password) == user_dict['password_hash']:
                    # Check if user is active
                    if not user_dict.get('is_active', True):
                        conn.close()
                        return {'success': False, 'message': 'Account is inactive'}
                        
                    # Determine if this is a BizPulse admin user
                    bizpulse_emails = [
                        'bizpulse.erp@gmail.com',
                        'admin@bizpulse.com', 
                        'support@bizpulse.com',
                        'developer@bizpulse.com',
                        'osman@bizpulse.com'
                    ]
                    
                    # Check admin status from multiple sources
                    is_bizpulse_admin = (
                        user_dict['email'].lower() in bizpulse_emails or  # Email whitelist
                        '@bizpulse.com' in user_dict['email'].lower()  # Domain check
                    )
                    
                    # Extract name from email or use business name
                    user_name = user_dict['business_name'] or user_dict['email'].split('@')[0]
                    
                    session_data = {
                        'user_id': user_dict['id'],
                        'user_type': 'admin' if is_bizpulse_admin else 'client',
                        'user_name': user_name,
                        'email': user_dict['email'],
                        'username': user_dict['email'],  # Use email as username for BizPulse check
                        'business_name': user_dict['business_name'],
                        'business_type': user_dict['business_type'],
                        'is_super_admin': is_bizpulse_admin
                }
                
                # Update last login
                try:
                    cursor.execute(f"UPDATE users SET last_login = CURRENT_TIMESTAMP, login_count = COALESCE(login_count, 0) + 1 WHERE id = {placeholder}", (user_dict['id'],))
                    conn.commit()
                except Exception as e:
                    logger.warning(f"Failed to update last login: {e}")
                    # Continue anyway, this shouldn't prevent login
                
                conn.close()
                
                # Trigger sync on login
                from modules.sync.utils import sync_on_login
                try:
                    sync_data = sync_on_login(user_dict['id'])
                except Exception as e:
                    logger.warning(f"Sync on login failed: {e}")
                    # Continue anyway, sync shouldn't prevent login
                
                return {
                    'success': True,
                    'token': 'user-jwt-token',
                    'session_data': session_data,
                    'user': {
                        "id": user_dict['id'],
                        "name": user_name,
                        "email": user_dict['email'],
                        "username": user_dict['email'],
                        "type": 'admin' if is_bizpulse_admin else 'client',
                        "business_name": user_dict['business_name'],
                        "business_type": user_dict['business_type'],
                        "is_super_admin": is_bizpulse_admin
                    }
                }
            
            # Then check user_accounts table (new user management system)
            user_account_query = f"""
                SELECT ua.id, ua.client_id, ua.full_name, ua.username, ua.password_hash, 
                       ua.status, ua.force_password_change, c.company_name, r.display_name as role_name,
                       r.permissions, ua.temp_password
                FROM user_accounts ua
                LEFT JOIN clients c ON ua.client_id = c.id
                LEFT JOIN user_roles r ON ua.role_id = r.id
                WHERE ua.username = {placeholder} AND ua.status = 'active'
            """
            cursor.execute(user_account_query, (login_id,))
            user_account = cursor.fetchone()
            
            if user_account:
                # Check password - try both hashed and plain text
                password_match = False
                if user_account['password_hash'] and hash_password(password) == user_account['password_hash']:
                    password_match = True
                elif user_account['temp_password'] and password == user_account['temp_password']:
                    password_match = True
                
                if password_match:
                    # Check if user account is active
                    if user_account['status'] != 'active':
                        conn.close()
                        return {'success': False, 'message': 'Account is inactive'}
                        
                    # Parse permissions from JSON string if needed
                    permissions = user_account['permissions']
                    if isinstance(permissions, str):
                        import json
                        try:
                            permissions = json.loads(permissions)
                        except:
                            permissions = []
                    
                    session_data = {
                        'user_id': user_account['id'],
                        'user_type': 'employee',
                        'user_name': user_account['full_name'],
                        'email': login_id,  # Use login_id as email
                        'username': user_account['username'],
                        'client_id': user_account['client_id'],
                        'company_name': user_account['company_name'],
                        'role_name': user_account['role_name'],
                        'permissions': permissions,
                        'force_password_change': bool(user_account['force_password_change']),
                        'is_super_admin': False
                    }
                    
                    # Update last login
                    try:
                        last_login_query = f"""
                            UPDATE user_accounts 
                            SET last_login = CURRENT_TIMESTAMP, login_count = COALESCE(login_count, 0) + 1 
                            WHERE id = {placeholder}
                        """
                        cursor.execute(last_login_query, (user_account['id'],))
                        conn.commit()
                    except Exception as e:
                        logger.warning(f"Failed to update last login for user account: {e}")
                        # Continue anyway, this shouldn't prevent login
                    
                    conn.close()
                    return {
                        'success': True,
                        'token': 'employee-jwt-token',
                        'session_data': session_data,
                        'user': {
                            "id": user_account['id'],
                            "name": user_account['full_name'],
                            "email": login_id,
                            "username": user_account['username'],
                            "type": "employee",
                            "client_id": user_account['client_id'],
                            "company_name": user_account['company_name'],
                            "role_name": user_account['role_name'],
                            "permissions": permissions,  # CRITICAL: Include permissions in user object
                            "force_password_change": bool(user_account['force_password_change']),
                            "is_super_admin": False
                        }
                    }
            
            # Then check client database (business owners)
            cursor.execute(f"SELECT id, company_name, contact_name, contact_email, username, password_hash, is_active FROM clients WHERE (contact_email = {placeholder} OR username = {placeholder})", (login_id, login_id))
            client = cursor.fetchone()
            
            if client:
                client_dict = dict(client) if hasattr(client, 'keys') else {
                    'id': client[0], 'company_name': client[1], 'contact_name': client[2],
                    'contact_email': client[3], 'username': client[4], 'password_hash': client[5], 'is_active': client[6]
                }
                
                if hash_password(password) == client_dict['password_hash']:
                    # Check if client is active
                    if not client_dict.get('is_active', True):
                        conn.close()
                        return {'success': False, 'message': 'Account is inactive'}
                        
                    session_data = {
                        'user_id': client_dict['id'],
                        'user_type': "client",
                        'user_name': client_dict['contact_name'] or client_dict['company_name'],
                        'email': client_dict['contact_email'],
                        'username': client_dict['username'],
                        'company_name': client_dict['company_name'],
                        'is_super_admin': False
                    }
                    
                    # Update last login
                    try:
                        cursor.execute(f"UPDATE clients SET last_login = CURRENT_TIMESTAMP, login_count = COALESCE(login_count, 0) + 1 WHERE id = {placeholder}", (client_dict['id'],))
                        conn.commit()
                    except Exception as e:
                        logger.warning(f"Failed to update last login for client: {e}")
                        # Continue anyway, this shouldn't prevent login
                    
                    conn.close()
                    return {
                        'success': True,
                        'token': 'client-jwt-token',
                        'session_data': session_data,
                        'user': {
                            "id": client_dict['id'],
                            "name": client_dict['contact_name'] or client_dict['company_name'],
                            "email": client_dict['contact_email'],
                            "username": client_dict['username'],
                            "type": "client",
                            "company_name": client_dict['company_name'],
                            "business_type": "retail",
                            "is_super_admin": False
                        }
                    }
            
            # Finally check staff and employee tables
            staff_query = f"SELECT s.id, s.name, s.email, s.username, s.password_hash, s.role, s.is_active, s.business_owner_id, c.company_name as business_name FROM staff s JOIN clients c ON s.business_owner_id = c.id WHERE (s.email = {placeholder} OR s.username = {placeholder}) AND s.is_active = TRUE" if db_type == 'postgresql' else "SELECT s.id, s.name, s.email, s.username, s.password_hash, s.role, s.is_active, s.business_owner_id, c.company_name as business_name FROM staff s JOIN clients c ON s.business_owner_id = c.id WHERE (s.email = ? OR s.username = ?) AND s.is_active = 1"
            cursor.execute(staff_query, (login_id, login_id))
            staff = cursor.fetchone()
            
            if staff and hash_password(password) == staff['password_hash']:
                # Check if staff member is active
                if not staff['is_active']:
                    conn.close()
                    return {'success': False, 'message': 'Staff account is inactive'}
                    
                session_data = {
                    'user_id': staff['id'],
                    'user_type': "staff",
                    'user_name': staff['name'],
                    'email': staff['email'],
                    'username': staff['username'],
                    'business_owner_id': staff['business_owner_id'],
                    'staff_role': staff['role'],
                    'is_super_admin': False
                }
                
                # Update last login
                try:
                    update_staff_query = f"UPDATE staff SET last_login = CURRENT_TIMESTAMP WHERE id = {placeholder}"
                    cursor.execute(update_staff_query, (staff['id'],))
                    conn.commit()
                except Exception as e:
                    logger.warning(f"Failed to update last login for staff: {e}")
                    # Continue anyway, this shouldn't prevent login
                
                conn.close()
                return {
                    'success': True,
                    'token': 'staff-jwt-token',
                    'session_data': session_data,
                    'user': {
                        "id": staff['id'],
                        "name": staff['name'],
                        "email": staff['email'],
                        "username": staff['username'],
                        "type": "staff",
                        "role": staff['role'],
                        "business_name": staff['business_name'],
                        "business_type": "retail",
                        "is_super_admin": False
                    }
                }
            
            # Check client users (employees) - wrap in try-except for missing table
            client_user = None
            try:
                client_user_query = f"SELECT cu.id, cu.full_name, cu.email, cu.username, cu.password_hash, cu.is_active, cu.role, cu.client_id, c.company_name FROM client_users cu JOIN clients c ON cu.client_id = c.id WHERE (cu.email = {placeholder} OR cu.username = {placeholder}) AND cu.is_active = TRUE" if db_type == 'postgresql' else "SELECT cu.id, cu.full_name, cu.email, cu.username, cu.password_hash, cu.is_active, cu.role, cu.client_id, c.company_name FROM client_users cu JOIN clients c ON cu.client_id = c.id WHERE (cu.email = ? OR cu.username = ?) AND cu.is_active = 1"
                cursor.execute(client_user_query, (login_id, login_id))
                client_user = cursor.fetchone()
            except Exception as e:
                # Table doesn't exist or query failed, skip
                logger.debug(f"client_users table check skipped: {e}")
                client_user = None
            
            if client_user and hash_password(password) == client_user['password_hash']:
                # Check if client user is active
                if not client_user['is_active']:
                    conn.close()
                    return {'success': False, 'message': 'Employee account is inactive'}
                    
                session_data = {
                    'user_id': client_user['id'],
                    'user_type': "employee",
                    'user_name': client_user['full_name'],
                    'email': client_user['email'],
                    'username': client_user['username'],
                    'client_id': client_user['client_id'],
                    'is_super_admin': False
                }
                
                # Update last login
                try:
                    update_client_user_query = f"UPDATE client_users SET last_login = CURRENT_TIMESTAMP WHERE id = {placeholder}"
                    cursor.execute(update_client_user_query, (client_user['id'],))
                    conn.commit()
                except Exception as e:
                    logger.warning(f"Failed to update last login for client user: {e}")
                    # Continue anyway, this shouldn't prevent login
                
                conn.close()
                return {
                    'success': True,
                    'token': 'employee-jwt-token',
                    'session_data': session_data,
                    'user': {
                        "id": client_user['id'],
                        "name": client_user['full_name'],
                        "email": client_user['email'],
                        "username": client_user['username'],
                        "type": "employee",
                        "role": client_user['role'],
                        "company": client_user['company_name'],
                        "business_type": "retail",
                        "is_super_admin": False
                    }
                }
            
            # Check RBAC tenants (clients created by super admin) - Skip for now to avoid errors
            # tenant = conn.execute("""
            #     SELECT id, tenant_id, business_name, owner_name, email, 
            #            username, password_hash, plan_type, plan_expiry_date, 
            #            subscription_status, status, is_active
            #     FROM tenants 
            #     WHERE username = ? AND is_active = 1
            # """, (login_id,)).fetchone()
            
            conn.close()
            return {'success': False, 'message': 'Invalid credentials'}
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            try:
                conn.close()
            except:
                pass
            return {'success': False, 'message': f'Authentication error: {str(e)}'}

    
    def get_user_info(self, session):
        """Get current user information including role and profile data"""
        user_id = session.get('user_id')
        user_type = session.get('user_type')
        user_name = session.get('user_name')
        
        # If it's a client, get the actual contact name from database
        if user_type == 'client' and user_id:
            conn = get_db_connection()
            try:
                client = conn.execute("SELECT contact_name, company_name, contact_email, profile_picture FROM clients WHERE id = ?", (user_id,)).fetchone()
                
                if client:
                    # Use contact_name if available, otherwise use company_name
                    actual_name = client['contact_name'] or client['company_name'] or user_name
                    profile_picture = client['profile_picture']
                    email = client['contact_email']
                else:
                    actual_name = user_name
                    profile_picture = None
                    email = None
                    
            except Exception as e:
                print(f"Error getting client profile: {e}")
                actual_name = user_name
                profile_picture = None
                email = None
            finally:
                conn.close()
        else:
            actual_name = user_name
            profile_picture = None
            email = None
        
        return {
            "user_id": user_id,
            "user_type": user_type,
            "user_name": actual_name,
            "email": email or session.get('email'),  # Include session email as fallback
            "username": session.get('username'),     # Include username for BizPulse check
            "profile_picture": profile_picture,
            "is_super_admin": session.get('is_super_admin', False),
            "staff_role": session.get('staff_role')  # For staff members
        }
    
    def register_user(self, data):
        """Register a new user"""
        user_id = generate_id()
        
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (id, email, password_hash, business_name, business_type) VALUES (?, ?, ?, ?, ?)", (
                user_id, data['email'], hash_password(data['password']),
                data.get('business_name', ''), data.get('business_type', 'retail')
            ))
            conn.commit()
            return {'success': True, 'user_id': user_id}
        except sqlite3.IntegrityError:
            return {'success': False, 'message': 'Email already exists'}
        finally:
            conn.close()
    
    def forgot_password(self, email_or_username):
        """Handle forgot password functionality"""
        conn = get_db_connection()
        
        try:
            # Create password_reset_tokens table if it doesn't exist
            conn.execute('''
                CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    user_type TEXT NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    email TEXT NOT NULL,
                    username TEXT,
                    expires_at TIMESTAMP NOT NULL,
                    used BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            user_found = None
            user_type = None
            user_id = None
            username = None
            
            # Check in users table first
            user = conn.execute("SELECT id, email, business_name FROM users WHERE email = ? AND is_active = 1", (email_or_username,)).fetchone()
            
            if user:
                user_found = user
                user_type = 'user'
                user_id = user['id']
                username = user['email']
            else:
                # Check in clients table
                client = conn.execute("SELECT id, contact_email, company_name, username FROM clients WHERE (contact_email = ? OR username = ?) AND is_active = 1", (email_or_username, email_or_username)).fetchone()
                
                if client:
                    user_found = client
                    user_type = 'client'
                    user_id = client['id']
                    username = client['username']
                else:
                    # Check in client_users table (employees)
                    client_user = conn.execute("SELECT id, email, full_name, username FROM client_users WHERE (email = ? OR username = ?) AND is_active = 1", (email_or_username, email_or_username)).fetchone()
                    
                    if client_user:
                        user_found = client_user
                        user_type = 'client_user'
                        user_id = client_user['id']
                        username = client_user['username']
                    else:
                        # Check in staff table
                        staff = conn.execute("SELECT id, email, name, username FROM staff WHERE (email = ? OR username = ?) AND is_active = 1", (email_or_username, email_or_username)).fetchone()
                        
                        if staff:
                            user_found = staff
                            user_type = 'staff'
                            user_id = staff['id']
                            username = staff['username']
            
            if not user_found:
                conn.close()
                return {'success': False, 'message': 'User not found'}
            
            # Generate reset token
            import secrets
            from datetime import datetime, timedelta
            
            reset_token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=24)  # Token expires in 24 hours
            
            # Store reset token
            conn.execute('''
                INSERT INTO password_reset_tokens (id, user_id, user_type, token, email, username, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (generate_id(), user_id, user_type, reset_token, 
                  user_found.get('email') or user_found.get('contact_email'), 
                  username, expires_at.isoformat()))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': 'Password reset token generated successfully',
                'reset_token': reset_token,
                'user_type': user_type,
                'expires_at': expires_at.isoformat()
            }
            
        except Exception as e:
            conn.close()
            raise e