"""
User Management Models
Database operations for the new user management system
"""

import sqlite3
from modules.shared.database import get_db_connection, get_db_type, generate_id, hash_password
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class UserManagementModels:
    
    @staticmethod
    def create_user_tables():
        """Create all user management tables"""
        conn = get_db_connection()
        cursor = conn.cursor()
        db_type = get_db_type()
        
        # Helper functions for database compatibility
        def get_text_pk():
            return 'VARCHAR(255) PRIMARY KEY' if db_type == 'postgresql' else 'TEXT PRIMARY KEY'
        
        def get_boolean_default(value):
            return str(value).upper() if db_type == 'postgresql' else str(int(value))
        
        try:
            # Roles table - Define available roles and permissions
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS user_roles (
                    id {get_text_pk()},
                    client_id VARCHAR(255) NOT NULL,
                    role_name VARCHAR(100) NOT NULL,
                    display_name VARCHAR(255) NOT NULL,
                    permissions TEXT NOT NULL DEFAULT '{{}}',
                    is_system_role BOOLEAN DEFAULT {get_boolean_default(False)},
                    is_active BOOLEAN DEFAULT {get_boolean_default(True)},
                    created_by VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(client_id, role_name)
                )
            ''')
            
            # User management table - All users under clients
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS user_accounts (
                    id {get_text_pk()},
                    client_id VARCHAR(255) NOT NULL,
                    user_id VARCHAR(255) UNIQUE NOT NULL,
                    full_name VARCHAR(255) NOT NULL,
                    email VARCHAR(255),
                    mobile VARCHAR(20) NOT NULL,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    temp_password VARCHAR(255),
                    role_id VARCHAR(255) NOT NULL,
                    department VARCHAR(100),
                    status VARCHAR(50) DEFAULT 'active',
                    force_password_change BOOLEAN DEFAULT {get_boolean_default(True)},
                    last_login TIMESTAMP,
                    login_count INTEGER DEFAULT 0,
                    failed_attempts INTEGER DEFAULT 0,
                    locked_until TIMESTAMP,
                    created_by VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients (id),
                    FOREIGN KEY (role_id) REFERENCES user_roles (id),
                    FOREIGN KEY (created_by) REFERENCES clients (id)
                )
            ''')
            
            # User activity log - Track all user actions
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS user_activity_log (
                    id {get_text_pk()},
                    client_id VARCHAR(255) NOT NULL,
                    user_id VARCHAR(255) NOT NULL,
                    module VARCHAR(100) NOT NULL,
                    action VARCHAR(100) NOT NULL,
                    details TEXT,
                    ip_address VARCHAR(50),
                    user_agent TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients (id),
                    FOREIGN KEY (user_id) REFERENCES user_accounts (id)
                )
            ''')
            
            # User sessions table - Track active sessions
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id {get_text_pk()},
                    client_id VARCHAR(255) NOT NULL,
                    user_id VARCHAR(255) NOT NULL,
                    session_token VARCHAR(255) UNIQUE NOT NULL,
                    ip_address VARCHAR(50),
                    user_agent TEXT,
                    expires_at TIMESTAMP NOT NULL,
                    is_active BOOLEAN DEFAULT {get_boolean_default(True)},
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients (id),
                    FOREIGN KEY (user_id) REFERENCES user_accounts (id)
                )
            ''')
            
            conn.commit()
            logger.info("✅ User management tables created successfully")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Error creating user tables: {e}")
            raise
        finally:
            conn.close()
    
    @staticmethod
    def create_default_roles(client_id, created_by):
        """Create default system roles for a client"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        default_roles = [
            {
                'role_name': 'cashier',
                'display_name': 'Cashier',
                'permissions': {
                    'sales': ['view', 'create'],
                    'customers': ['view', 'create'],
                    'products': ['view'],
                    'billing': ['view', 'create'],
                    'reports': ['view']
                }
            },
            {
                'role_name': 'biller',
                'display_name': 'Biller',
                'permissions': {
                    'sales': ['view', 'create', 'edit'],
                    'customers': ['view', 'create', 'edit'],
                    'products': ['view'],
                    'billing': ['view', 'create', 'edit'],
                    'invoices': ['view', 'create'],
                    'reports': ['view']
                }
            },
            {
                'role_name': 'manager',
                'display_name': 'Manager',
                'permissions': {
                    'sales': ['view', 'create', 'edit', 'delete'],
                    'customers': ['view', 'create', 'edit', 'delete'],
                    'products': ['view', 'create', 'edit'],
                    'billing': ['view', 'create', 'edit', 'delete'],
                    'invoices': ['view', 'create', 'edit'],
                    'inventory': ['view', 'create', 'edit'],
                    'reports': ['view', 'export'],
                    'settings': ['view']
                }
            },
            {
                'role_name': 'accountant',
                'display_name': 'Accountant',
                'permissions': {
                    'sales': ['view'],
                    'customers': ['view'],
                    'billing': ['view'],
                    'invoices': ['view', 'create', 'edit'],
                    'reports': ['view', 'export'],
                    'earnings': ['view'],
                    'credit': ['view', 'create', 'edit']
                }
            },
            {
                'role_name': 'supervisor',
                'display_name': 'Supervisor',
                'permissions': {
                    'sales': ['view', 'create', 'edit'],
                    'customers': ['view', 'create', 'edit'],
                    'products': ['view', 'create', 'edit'],
                    'billing': ['view', 'create', 'edit'],
                    'inventory': ['view', 'create', 'edit'],
                    'reports': ['view', 'export']
                }
            },
            {
                'role_name': 'store_keeper',
                'display_name': 'Store Keeper',
                'permissions': {
                    'products': ['view', 'create', 'edit'],
                    'inventory': ['view', 'create', 'edit', 'delete'],
                    'reports': ['view']
                }
            },
            {
                'role_name': 'sales_executive',
                'display_name': 'Sales Executive',
                'permissions': {
                    'sales': ['view', 'create', 'edit'],
                    'customers': ['view', 'create', 'edit'],
                    'products': ['view'],
                    'billing': ['view', 'create'],
                    'reports': ['view']
                }
            }
        ]
        
        try:
            for role_data in default_roles:
                role_id = generate_id()
                cursor.execute('''
                    INSERT INTO user_roles (id, client_id, role_name, display_name, permissions, is_system_role, created_by)
                    VALUES (?, ?, ?, ?, ?, 1, ?)
                ''', (
                    role_id, client_id, role_data['role_name'], role_data['display_name'],
                    json.dumps(role_data['permissions']), created_by
                ))
            
            conn.commit()
            logger.info(f"✅ Default roles created for client {client_id}")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Error creating default roles: {e}")
            raise
        finally:
            conn.close()
    
    @staticmethod
    def get_client_roles(client_id):
        """Get all roles for a client"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, role_name, display_name, permissions, is_system_role, is_active
            FROM user_roles
            WHERE client_id = ? AND is_active = 1
            ORDER BY is_system_role DESC, display_name
        ''', (client_id,))
        
        roles = []
        for row in cursor.fetchall():
            roles.append({
                'id': row[0],
                'role_name': row[1],
                'display_name': row[2],
                'permissions': json.loads(row[3]) if row[3] else {},
                'is_system_role': bool(row[4]),
                'is_active': bool(row[5])
            })
        
        conn.close()
        return roles
    
    @staticmethod
    def create_user(client_id, user_data, created_by):
        """Create a new user account"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Generate user ID and set password same as username
            user_id = generate_id()
            username = user_data['username']
            password = username  # Password same as username
            
            # Insert user account
            cursor.execute('''
                INSERT INTO user_accounts (
                    id, client_id, user_id, full_name, email, mobile, username,
                    password_hash, temp_password, role_id, department, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, client_id, user_id, user_data['full_name'],
                user_data.get('email'), user_data['mobile'], username,
                hash_password(password), password, user_data['role_id'],
                user_data.get('department'), created_by
            ))
            
            conn.commit()
            
            # Log activity
            UserManagementModels.log_activity(
                client_id, created_by, 'user_management', 'create_user',
                f"Created user: {user_data['full_name']} ({username})"
            )
            
            return {
                'success': True,
                'user_id': user_id,
                'username': username,
                'temp_password': password
            }
            
        except sqlite3.IntegrityError as e:
            conn.rollback()
            if 'username' in str(e):
                return {'success': False, 'error': 'Username already exists'}
            elif 'email' in str(e):
                return {'success': False, 'error': 'Email already exists'}
            else:
                return {'success': False, 'error': 'User creation failed'}
        except Exception as e:
            conn.rollback()
            logger.error(f"Error creating user: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    @staticmethod
    def get_client_users(client_id):
        """Get all users for a client"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.id, u.user_id, u.full_name, u.email, u.mobile, u.username,
                   u.department, u.status, u.last_login, u.login_count, u.created_at,
                   r.display_name as role_name, u.force_password_change, u.temp_password
            FROM user_accounts u
            LEFT JOIN user_roles r ON u.role_id = r.id
            WHERE u.client_id = ?
            ORDER BY u.created_at DESC
        ''', (client_id,))
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'id': row[0],
                'user_id': row[1],
                'full_name': row[2],
                'email': row[3],
                'mobile': row[4],
                'username': row[5],
                'department': row[6],
                'status': row[7],
                'last_login': row[8],
                'login_count': row[9],
                'created_at': row[10],
                'role_name': row[11],
                'force_password_change': bool(row[12]) if row[12] is not None else False,
                'temp_password': row[13]
            })
        
        conn.close()
        return users
    
    @staticmethod
    def update_user(client_id, user_id, user_data, updated_by):
        """Update user information"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Build update query dynamically
            update_fields = []
            values = []
            
            for field in ['full_name', 'email', 'mobile', 'role_id', 'department', 'status']:
                if field in user_data:
                    update_fields.append(f"{field} = ?")
                    values.append(user_data[field])
            
            if not update_fields:
                return {'success': False, 'error': 'No fields to update'}
            
            update_fields.append("updated_at = ?")
            values.append(datetime.now())
            values.extend([client_id, user_id])
            
            cursor.execute(f'''
                UPDATE user_accounts 
                SET {', '.join(update_fields)}
                WHERE client_id = ? AND id = ?
            ''', values)
            
            if cursor.rowcount == 0:
                return {'success': False, 'error': 'User not found'}
            
            conn.commit()
            
            # Log activity
            UserManagementModels.log_activity(
                client_id, updated_by, 'user_management', 'update_user',
                f"Updated user: {user_id}"
            )
            
            return {'success': True}
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error updating user: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    @staticmethod
    def reset_user_password(client_id, user_id, reset_by, new_password=None):
        """Reset user password"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # If no custom password provided, get username and use it as password
            if not new_password:
                cursor.execute('SELECT username FROM user_accounts WHERE client_id = ? AND id = ?', (client_id, user_id))
                user_row = cursor.fetchone()
                if not user_row:
                    return {'success': False, 'error': 'User not found'}
                new_password = user_row[0]  # Use username as password
            
            cursor.execute('''
                UPDATE user_accounts 
                SET password_hash = ?, temp_password = ?, updated_at = ?
                WHERE client_id = ? AND id = ?
            ''', (hash_password(new_password), new_password, datetime.now(), client_id, user_id))
            
            if cursor.rowcount == 0:
                return {'success': False, 'error': 'User not found'}
            
            conn.commit()
            
            # Log activity
            UserManagementModels.log_activity(
                client_id, reset_by, 'user_management', 'reset_password',
                f"Password reset for user: {user_id}"
            )
            
            return {'success': True, 'temp_password': new_password}
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error resetting password: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    @staticmethod
    def delete_user(client_id, user_id, deleted_by):
        """Delete user (only if no transactions)"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Check if user has any transactions
            tables_to_check = ['bills', 'sales', 'invoices', 'payments']
            has_transactions = False
            
            for table in tables_to_check:
                cursor.execute(f'SELECT COUNT(*) FROM {table} WHERE created_by = ?', (user_id,))
                if cursor.fetchone()[0] > 0:
                    has_transactions = True
                    break
            
            if has_transactions:
                return {'success': False, 'error': 'Cannot delete user with existing transactions. Deactivate instead.'}
            
            # Delete user
            cursor.execute('DELETE FROM user_accounts WHERE client_id = ? AND id = ?', (client_id, user_id))
            
            if cursor.rowcount == 0:
                return {'success': False, 'error': 'User not found'}
            
            conn.commit()
            
            # Log activity
            UserManagementModels.log_activity(
                client_id, deleted_by, 'user_management', 'delete_user',
                f"Deleted user: {user_id}"
            )
            
            return {'success': True}
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error deleting user: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    @staticmethod
    def log_activity(client_id, user_id, module, action, details=None, ip_address=None, user_agent=None):
        """Log user activity"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO user_activity_log (id, client_id, user_id, module, action, details, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (generate_id(), client_id, user_id, module, action, details, ip_address, user_agent))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error logging activity: {e}")
        finally:
            conn.close()
    
    @staticmethod
    def get_user_activity(client_id, user_id=None, limit=100):
        """Get user activity logs"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute('''
                SELECT u.full_name, l.module, l.action, l.details, l.timestamp
                FROM user_activity_log l
                LEFT JOIN user_accounts u ON l.user_id = u.id
                WHERE l.client_id = ? AND l.user_id = ?
                ORDER BY l.timestamp DESC
                LIMIT ?
            ''', (client_id, user_id, limit))
        else:
            cursor.execute('''
                SELECT u.full_name, l.module, l.action, l.details, l.timestamp
                FROM user_activity_log l
                LEFT JOIN user_accounts u ON l.user_id = u.id
                WHERE l.client_id = ?
                ORDER BY l.timestamp DESC
                LIMIT ?
            ''', (client_id, limit))
        
        activities = []
        for row in cursor.fetchall():
            activities.append({
                'user_name': row[0],
                'module': row[1],
                'action': row[2],
                'details': row[3],
                'timestamp': row[4]
            })
        
        conn.close()
        return activities

    
    @staticmethod
    def get_all_user_permissions(client_id):
        """Get module permissions for all users"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            logger.info(f"🔍 Getting permissions for client_id: {client_id}")
            
            cursor.execute('''
                SELECT u.id, u.user_id, u.full_name, u.username, u.module_permissions,
                       r.display_name as role_name
                FROM user_accounts u
                LEFT JOIN user_roles r ON u.role_id = r.id
                WHERE u.client_id = ?
                ORDER BY u.full_name
            ''', (client_id,))
            
            users = []
            for row in cursor.fetchall():
                permissions_json = row[4] if row[4] else '{}'
                try:
                    permissions = json.loads(permissions_json)
                except Exception as e:
                    logger.warning(f"Failed to parse permissions JSON for user {row[0]}: {e}")
                    permissions = {}
                
                users.append({
                    'id': row[0],
                    'user_id': row[1],
                    'full_name': row[2],
                    'username': row[3],
                    'permissions': permissions,
                    'role_name': row[5]
                })
            
            logger.info(f"✅ Found {len(users)} users with permissions")
            conn.close()
            return users
            
        except Exception as e:
            logger.error(f"❌ Error in get_all_user_permissions: {e}")
            conn.close()
            raise
    
    @staticmethod
    def update_user_permission(client_id, user_id, module, enabled, updated_by):
        """Update module permission for a user"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Get current permissions
            cursor.execute('''
                SELECT module_permissions FROM user_accounts 
                WHERE client_id = ? AND id = ?
            ''', (client_id, user_id))
            
            result = cursor.fetchone()
            if not result:
                return {'success': False, 'error': 'User not found'}
            
            # Parse current permissions
            permissions_json = result[0] if result[0] else '{}'
            try:
                permissions = json.loads(permissions_json)
            except:
                permissions = {}
            
            # Update permission
            permissions[module] = bool(enabled)
            
            # Save updated permissions
            cursor.execute('''
                UPDATE user_accounts 
                SET module_permissions = ?, updated_at = ?
                WHERE client_id = ? AND id = ?
            ''', (json.dumps(permissions), datetime.now(), client_id, user_id))
            
            conn.commit()
            
            # Log activity
            UserManagementModels.log_activity(
                client_id, updated_by, 'user_management', 'update_permission',
                f"{'Enabled' if enabled else 'Disabled'} {module} module for user {user_id}"
            )
            
            return {'success': True}
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error updating user permission: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    @staticmethod
    def add_permissions_column():
        """Add module_permissions column to user_accounts table if it doesn't exist"""
        conn = get_db_connection()
        cursor = conn.cursor()
        db_type = get_db_type()
        
        try:
            # Check if column exists (database-agnostic way)
            if db_type == 'postgresql':
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='user_accounts' AND column_name='module_permissions'
                """)
                column_exists = cursor.fetchone() is not None
            else:
                cursor.execute("PRAGMA table_info(user_accounts)")
                columns = [row[1] for row in cursor.fetchall()]
                column_exists = 'module_permissions' in columns
            
            if not column_exists:
                cursor.execute('''
                    ALTER TABLE user_accounts 
                    ADD COLUMN module_permissions TEXT DEFAULT '{}'
                ''')
                conn.commit()
                logger.info("✅ Added module_permissions column to user_accounts table")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Error adding permissions column: {e}")
        finally:
            conn.close()
    
    @staticmethod
    def get_user_permissions_by_id(user_id):
        """Get module permissions for a specific user by ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT module_permissions FROM user_accounts 
                WHERE id = ? OR user_id = ?
            ''', (user_id, user_id))
            
            result = cursor.fetchone()
            
            if not result or not result[0]:
                return None
            
            try:
                permissions = json.loads(result[0])
                return permissions
            except:
                return None
                
        except Exception as e:
            logger.error(f"Error getting user permissions by ID: {e}")
            return None
        finally:
            conn.close()
