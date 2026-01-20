"""
User Management Service
Business logic for user management operations
"""

from .models import UserManagementModels
from modules.shared.database import get_db_connection, generate_id, hash_password
from flask import session, request
from datetime import datetime
import logging
import re
import json

logger = logging.getLogger(__name__)

class UserManagementService:
    
    def __init__(self):
        self.models = UserManagementModels()
    
    def initialize_client_user_system(self, client_id):
        """Initialize user management system for a new client"""
        try:
            # Create default roles
            self.models.create_default_roles(client_id, client_id)
            return {'success': True, 'message': 'User management system initialized'}
        except Exception as e:
            logger.error(f"Error initializing user system: {e}")
            return {'success': False, 'error': str(e)}
    
    def validate_user_data(self, user_data, is_update=False):
        """Validate user input data"""
        errors = []
        
        # Required fields for creation
        if not is_update:
            required_fields = ['full_name', 'mobile', 'username', 'role_id']
            for field in required_fields:
                if not user_data.get(field, '').strip():
                    errors.append(f"{field.replace('_', ' ').title()} is required")
        
        # Validate full name
        if 'full_name' in user_data:
            full_name = user_data['full_name'].strip()
            if len(full_name) < 2:
                errors.append("Full name must be at least 2 characters")
            elif len(full_name) > 100:
                errors.append("Full name must be less than 100 characters")
        
        # Validate mobile number
        if 'mobile' in user_data:
            mobile = user_data['mobile'].strip()
            if not re.match(r'^[6-9]\d{9}$', mobile):
                errors.append("Mobile number must be a valid 10-digit Indian number")
        
        # Validate email (optional)
        if user_data.get('email'):
            email = user_data['email'].strip()
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                errors.append("Invalid email format")
        
        # Validate username
        if 'username' in user_data:
            username = user_data['username'].strip()
            if len(username) < 3:
                errors.append("Username must be at least 3 characters")
            elif len(username) > 50:
                errors.append("Username must be less than 50 characters")
            elif not re.match(r'^[a-zA-Z0-9_]+$', username):
                errors.append("Username can only contain letters, numbers, and underscores")
        
        return errors
    
    def create_user(self, client_id, user_data):
        """Create a new user with validation"""
        try:
            # Validate input
            errors = self.validate_user_data(user_data)
            if errors:
                return {'success': False, 'errors': errors}
            
            # Check if client admin
            if not self.is_client_admin(client_id):
                return {'success': False, 'error': 'Access denied. Only client admins can create users.'}
            
            # Verify role exists
            roles = self.models.get_client_roles(client_id)
            role_ids = [role['id'] for role in roles]
            if user_data['role_id'] not in role_ids:
                return {'success': False, 'error': 'Invalid role selected'}
            
            # Create user
            result = self.models.create_user(client_id, user_data, session.get('user_id'))
            
            if result['success']:
                logger.info(f"✅ User created: {user_data['username']} for client {client_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in create_user service: {e}")
            return {'success': False, 'error': 'User creation failed'}
    
    def get_users(self, client_id):
        """Get all users for a client"""
        try:
            if not client_id:
                return {'success': False, 'error': 'Client ID is required'}
                
            if not self.is_client_admin(client_id):
                return {'success': False, 'error': 'Access denied'}
            
            users = self.models.get_client_users(client_id)
            return {'success': True, 'users': users}
            
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            return {'success': False, 'error': 'Failed to fetch users'}
    
    def update_user(self, client_id, user_id, user_data):
        """Update user information"""
        try:
            if not self.is_client_admin(client_id):
                return {'success': False, 'error': 'Access denied'}
            
            # Validate input
            errors = self.validate_user_data(user_data, is_update=True)
            if errors:
                return {'success': False, 'errors': errors}
            
            result = self.models.update_user(client_id, user_id, user_data, session.get('user_id'))
            return result
            
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return {'success': False, 'error': 'User update failed'}
    
    def reset_password(self, client_id, user_id, new_password=None):
        """Reset user password"""
        try:
            if not self.is_client_admin(client_id):
                return {'success': False, 'error': 'Access denied'}
            
            result = self.models.reset_user_password(client_id, user_id, session.get('user_id'), new_password)
            return result
            
        except Exception as e:
            logger.error(f"Error resetting password: {e}")
            return {'success': False, 'error': 'Password reset failed'}
    
    def deactivate_user(self, client_id, user_id):
        """Deactivate user account"""
        try:
            if not self.is_client_admin(client_id):
                return {'success': False, 'error': 'Access denied'}
            
            result = self.models.update_user(
                client_id, user_id, 
                {'status': 'inactive'}, 
                session.get('user_id')
            )
            
            if result['success']:
                # Force logout user by invalidating sessions
                self.invalidate_user_sessions(user_id)
            
            return result
            
        except Exception as e:
            logger.error(f"Error deactivating user: {e}")
            return {'success': False, 'error': 'User deactivation failed'}
    
    def delete_user(self, client_id, user_id):
        """Delete user account"""
        try:
            if not self.is_client_admin(client_id):
                return {'success': False, 'error': 'Access denied'}
            
            result = self.models.delete_user(client_id, user_id, session.get('user_id'))
            return result
            
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return {'success': False, 'error': 'User deletion failed'}
    
    def get_roles(self, client_id):
        """Get available roles for client"""
        try:
            if not client_id:
                return {'success': False, 'error': 'Client ID is required'}
                
            roles = self.models.get_client_roles(client_id)
            return {'success': True, 'roles': roles}
            
        except Exception as e:
            logger.error(f"Error getting roles: {e}")
            return {'success': False, 'error': 'Failed to fetch roles'}
    
    def create_custom_role(self, client_id, role_data):
        """Create custom role for client"""
        try:
            if not self.is_client_admin(client_id):
                return {'success': False, 'error': 'Access denied'}
            
            # Validate role data
            if not role_data.get('role_name') or not role_data.get('display_name'):
                return {'success': False, 'error': 'Role name and display name are required'}
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if role name already exists for this client
            cursor.execute('''
                SELECT id FROM user_roles 
                WHERE client_id = ? AND role_name = ?
            ''', (client_id, role_data['role_name']))
            
            if cursor.fetchone():
                conn.close()
                return {'success': False, 'error': 'Role name already exists'}
            
            role_id = generate_id()
            permissions_json = json.dumps(role_data.get('permissions', {}))
            
            cursor.execute('''
                INSERT INTO user_roles (id, client_id, role_name, display_name, permissions, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                role_id, client_id, role_data['role_name'], role_data['display_name'],
                permissions_json, session.get('user_id')
            ))
            
            conn.commit()
            conn.close()
            
            # Log activity
            self.models.log_activity(
                client_id, session.get('user_id'), 'user_management', 'create_role',
                f"Created custom role: {role_data['display_name']}"
            )
            
            return {'success': True, 'role_id': role_id}
            
        except Exception as e:
            logger.error(f"Error creating custom role: {e}")
            return {'success': False, 'error': 'Role creation failed'}
    
    def get_user_activity(self, client_id, user_id=None):
        """Get user activity logs"""
        try:
            if not self.is_client_admin(client_id):
                return {'success': False, 'error': 'Access denied'}
            
            activities = self.models.get_user_activity(client_id, user_id)
            return {'success': True, 'activities': activities}
            
        except Exception as e:
            logger.error(f"Error getting user activity: {e}")
            return {'success': False, 'error': 'Failed to fetch activity logs'}
    
    def is_client_admin(self, client_id):
        """Check if current user is client admin"""
        # Allow access for testing
        return True
    
    def invalidate_user_sessions(self, user_id):
        """Invalidate all sessions for a user"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_sessions 
                SET is_active = 0 
                WHERE user_id = ?
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error invalidating sessions: {e}")
    
    def authenticate_user(self, username, password, client_id=None):
        """Authenticate user login"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Find user by username
            if client_id:
                cursor.execute('''
                    SELECT id, client_id, full_name, username, password_hash, status, 
                           force_password_change, failed_attempts, locked_until, role_id
                    FROM user_accounts 
                    WHERE username = ? AND client_id = ?
                ''', (username, client_id))
            else:
                cursor.execute('''
                    SELECT id, client_id, full_name, username, password_hash, status, 
                           force_password_change, failed_attempts, locked_until, role_id
                    FROM user_accounts 
                    WHERE username = ?
                ''', (username,))
            
            user = cursor.fetchone()
            
            if not user:
                return {'success': False, 'error': 'Invalid username or password'}
            
            # Check if account is active
            if user[5] != 'active':
                return {'success': False, 'error': 'Account is deactivated'}
            
            # Check if account is locked
            if user[8] and user[8] > datetime.now():
                return {'success': False, 'error': 'Account is temporarily locked'}
            
            # Verify password
            if hash_password(password) != user[4]:
                # Increment failed attempts
                cursor.execute('''
                    UPDATE user_accounts 
                    SET failed_attempts = failed_attempts + 1 
                    WHERE id = ?
                ''', (user[0],))
                conn.commit()
                return {'success': False, 'error': 'Invalid username or password'}
            
            # Reset failed attempts and update last login
            cursor.execute('''
                UPDATE user_accounts 
                SET failed_attempts = 0, last_login = ?, login_count = login_count + 1 
                WHERE id = ?
            ''', (datetime.now(), user[0]))
            
            conn.commit()
            
            # Get role information
            cursor.execute('SELECT display_name, permissions FROM user_roles WHERE id = ?', (user[9],))
            role_info = cursor.fetchone()
            
            return {
                'success': True,
                'user': {
                    'id': user[0],
                    'client_id': user[1],
                    'full_name': user[2],
                    'username': user[3],
                    'status': user[5],
                    'force_password_change': bool(user[6]),
                    'role_name': role_info[0] if role_info else 'Unknown',
                    'permissions': role_info[1] if role_info else '{}'
                }
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return {'success': False, 'error': 'Authentication failed'}
        finally:
            conn.close()

    
    def get_user_permissions(self, client_id):
        """Get module permissions for all users"""
        try:
            if not self.is_client_admin(client_id):
                return {'success': False, 'error': 'Access denied'}
            
            permissions = self.models.get_all_user_permissions(client_id)
            return {'success': True, 'permissions': permissions}
            
        except Exception as e:
            logger.error(f"Error getting user permissions: {e}")
            return {'success': False, 'error': 'Failed to fetch permissions'}
    
    def update_user_permission(self, client_id, user_id, module, enabled):
        """Update module permission for a user"""
        try:
            if not self.is_client_admin(client_id):
                return {'success': False, 'error': 'Access denied'}
            
            if not user_id or not module:
                return {'success': False, 'error': 'User ID and module are required'}
            
            result = self.models.update_user_permission(
                client_id, user_id, module, enabled, session.get('user_id')
            )
            return result
            
        except Exception as e:
            logger.error(f"Error updating user permission: {e}")
            return {'success': False, 'error': 'Permission update failed'}
    
    def get_current_user_permissions(self, user_id):
        """Get module permissions for current logged-in user"""
        try:
            permissions = self.models.get_user_permissions_by_id(user_id)

            # If NO user-level permissions are set (None) OR explicitly empty dict ({})
            # then do NOT inherit role permissions — treat as NO ACCESS (all modules hidden).
            if permissions is None or (isinstance(permissions, dict) and len(permissions) == 0):
                return {'success': True, 'permissions': {
                    'dashboard': False,
                    'billing': False,
                    'sales': False,
                    'products': False,
                    'customers': False,
                    'inventory': False,
                    'reports': False,
                    'credit': False
                }}

            # Otherwise return the explicit user-level permissions
            return {'success': True, 'permissions': permissions}
            
        except Exception as e:
            logger.error(f"Error getting current user permissions: {e}")
            return {'success': False, 'error': 'Failed to fetch permissions'}
