"""
Client Management Service
Business logic for tenant management
"""

import sqlite3
from modules.shared.database import get_db_connection, generate_id, hash_password
from datetime import datetime, timedelta
import secrets
import string
import logging

logger = logging.getLogger(__name__)

class ClientManagementService:
    
    def __init__(self):
        self.conn = None
    
    def get_connection(self):
        """Get database connection"""
        if not self.conn:
            self.conn = get_db_connection()
        return self.conn
    
    def close_connection(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def generate_tenant_id(self):
        """Generate unique tenant ID"""
        return f"tenant_{generate_id()[:8]}"
    
    def generate_password(self, length=12):
        """Generate secure random password"""
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(characters) for _ in range(length))
    
    def create_tenant(self, data, created_by):
        """Create new tenant account"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Validate required fields
            required_fields = ['business_name', 'owner_name', 'email', 'username']
            for field in required_fields:
                if not data.get(field, '').strip():
                    return {
                        'success': False,
                        'message': f'{field.replace("_", " ").title()} is required'
                    }
            
            # Check if email already exists
            cursor.execute('SELECT id FROM tenants WHERE email = ?', (data['email'],))
            if cursor.fetchone():
                return {
                    'success': False,
                    'message': f'Email {data["email"]} already exists'
                }
            
            # Check if username already exists
            cursor.execute('SELECT id FROM tenants WHERE username = ?', (data['username'],))
            if cursor.fetchone():
                return {
                    'success': False,
                    'message': f'Username {data["username"]} already exists'
                }
            
            # Generate tenant data
            tenant_id = self.generate_tenant_id()
            password = data.get('password') or self.generate_password()
            password_hash = hash_password(password)
            
            # Set plan expiry (default 1 year)
            plan_expiry = datetime.now() + timedelta(days=365)
            
            # Insert tenant
            cursor.execute('''
                INSERT INTO tenants (
                    id, tenant_id, business_name, owner_name, email, phone, address,
                    username, password_hash, plan_type, plan_expiry_date,
                    subscription_status, status, is_active, created_by, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                generate_id(),
                tenant_id,
                data['business_name'],
                data['owner_name'],
                data['email'],
                data.get('phone', ''),
                data.get('address', ''),
                data['username'],
                password_hash,
                data.get('plan_type', 'basic'),
                plan_expiry.date(),
                'active',
                'active',
                1,
                created_by,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            
            logger.info(f"✅ Tenant created: {data['business_name']} ({tenant_id})")
            
            return {
                'success': True,
                'message': 'Tenant created successfully',
                'tenant_id': tenant_id,
                'password': password,
                'login_url': f'/tenant/login'
            }
            
        except Exception as e:
            logger.error(f"Error creating tenant: {e}")
            if conn:
                conn.rollback()
            return {
                'success': False,
                'message': f'Error creating tenant: {str(e)}'
            }
        finally:
            self.close_connection()
    
    def get_all_tenants(self, page=1, per_page=20, search='', status=''):
        """Get all tenants with pagination and filtering"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Build query
            base_query = """
                SELECT t.*, 
                       COUNT(DISTINCT tu.id) as user_count,
                       COUNT(DISTINCT p.id) as product_count,
                       COUNT(DISTINCT b.id) as bill_count,
                       COALESCE(SUM(b.total_amount), 0) as total_revenue
                FROM tenants t
                LEFT JOIN tenant_users tu ON t.tenant_id = tu.tenant_id AND tu.is_active = 1
                LEFT JOIN products p ON t.tenant_id = p.tenant_id AND p.is_active = 1
                LEFT JOIN bills b ON t.tenant_id = b.tenant_id
            """
            
            conditions = []
            params = []
            
            if search:
                conditions.append("(t.business_name LIKE ? OR t.owner_name LIKE ? OR t.email LIKE ? OR t.username LIKE ?)")
                search_param = f'%{search}%'
                params.extend([search_param, search_param, search_param, search_param])
            
            if status:
                if status == 'active':
                    conditions.append("t.is_active = 1 AND t.status = 'active'")
                elif status == 'inactive':
                    conditions.append("t.is_active = 0 OR t.status != 'active'")
                elif status == 'expired':
                    conditions.append("t.subscription_status = 'expired' OR t.plan_expiry_date < date('now')")
            
            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)
            
            base_query += " GROUP BY t.id"
            
            # Get total count
            count_query = f"SELECT COUNT(*) FROM ({base_query}) as counted"
            cursor.execute(count_query, params)
            total_count = cursor.fetchone()[0]
            
            # Add pagination
            base_query += " ORDER BY t.created_at DESC LIMIT ? OFFSET ?"
            params.extend([per_page, (page - 1) * per_page])
            
            cursor.execute(base_query, params)
            
            tenants = []
            for row in cursor.fetchall():
                tenants.append({
                    'id': row[0],
                    'tenant_id': row[1],
                    'business_name': row[2],
                    'owner_name': row[3],
                    'email': row[4],
                    'phone': row[5],
                    'address': row[6],
                    'username': row[7],
                    'plan_type': row[9],
                    'plan_expiry_date': row[10],
                    'subscription_status': row[11],
                    'status': row[12],
                    'is_active': bool(row[13]),
                    'created_by': row[14],
                    'last_login': row[15],
                    'login_count': row[16],
                    'failed_login_attempts': row[17],
                    'created_at': row[18],
                    'updated_at': row[19],
                    'user_count': row[20],
                    'product_count': row[21],
                    'bill_count': row[22],
                    'total_revenue': float(row[23])
                })
            
            return {
                'success': True,
                'tenants': tenants,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total_count,
                    'pages': (total_count + per_page - 1) // per_page
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting tenants: {e}")
            return {
                'success': False,
                'message': f'Error getting tenants: {str(e)}'
            }
        finally:
            self.close_connection()
    
    def get_tenant_details(self, tenant_id):
        """Get detailed tenant information"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get tenant info
            cursor.execute('SELECT * FROM tenants WHERE tenant_id = ?', (tenant_id,))
            tenant_row = cursor.fetchone()
            
            if not tenant_row:
                return {
                    'success': False,
                    'message': 'Tenant not found'
                }
            
            # Get tenant users
            cursor.execute('''
                SELECT id, full_name, email, username, role, department, 
                       is_active, last_login, created_at
                FROM tenant_users 
                WHERE tenant_id = ?
                ORDER BY created_at DESC
            ''', (tenant_id,))
            
            users = []
            for row in cursor.fetchall():
                users.append({
                    'id': row[0],
                    'full_name': row[1],
                    'email': row[2],
                    'username': row[3],
                    'role': row[4],
                    'department': row[5],
                    'is_active': bool(row[6]),
                    'last_login': row[7],
                    'created_at': row[8]
                })
            
            # Get recent activities
            cursor.execute('''
                SELECT 'bill' as type, bill_number as reference, total_amount as amount, created_at
                FROM bills WHERE tenant_id = ?
                UNION ALL
                SELECT 'product' as type, name as reference, price as amount, created_at
                FROM products WHERE tenant_id = ? AND is_active = 1
                ORDER BY created_at DESC
                LIMIT 10
            ''', (tenant_id, tenant_id))
            
            activities = []
            for row in cursor.fetchall():
                activities.append({
                    'type': row[0],
                    'reference': row[1],
                    'amount': row[2],
                    'created_at': row[3]
                })
            
            tenant_data = {
                'id': tenant_row[0],
                'tenant_id': tenant_row[1],
                'business_name': tenant_row[2],
                'owner_name': tenant_row[3],
                'email': tenant_row[4],
                'phone': tenant_row[5],
                'address': tenant_row[6],
                'username': tenant_row[7],
                'plan_type': tenant_row[9],
                'plan_expiry_date': tenant_row[10],
                'subscription_status': tenant_row[11],
                'status': tenant_row[12],
                'is_active': bool(tenant_row[13]),
                'created_by': tenant_row[14],
                'last_login': tenant_row[15],
                'login_count': tenant_row[16],
                'failed_login_attempts': tenant_row[17],
                'created_at': tenant_row[18],
                'updated_at': tenant_row[19],
                'users': users,
                'recent_activities': activities
            }
            
            return {
                'success': True,
                'tenant': tenant_data
            }
            
        except Exception as e:
            logger.error(f"Error getting tenant details: {e}")
            return {
                'success': False,
                'message': f'Error getting tenant details: {str(e)}'
            }
        finally:
            self.close_connection()
    
    def update_tenant(self, tenant_id, data):
        """Update tenant information"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if tenant exists
            cursor.execute('SELECT id FROM tenants WHERE tenant_id = ?', (tenant_id,))
            if not cursor.fetchone():
                return {
                    'success': False,
                    'message': 'Tenant not found'
                }
            
            # Build update query
            update_fields = []
            params = []
            
            updatable_fields = [
                'business_name', 'owner_name', 'email', 'phone', 'address',
                'username', 'plan_type', 'subscription_status', 'status', 'is_active'
            ]
            
            for field in updatable_fields:
                if field in data:
                    update_fields.append(f"{field} = ?")
                    params.append(data[field])
            
            if not update_fields:
                return {
                    'success': False,
                    'message': 'No fields to update'
                }
            
            # Add updated_at
            update_fields.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(tenant_id)
            
            query = f"UPDATE tenants SET {', '.join(update_fields)} WHERE tenant_id = ?"
            cursor.execute(query, params)
            
            conn.commit()
            
            logger.info(f"✅ Tenant updated: {tenant_id}")
            
            return {
                'success': True,
                'message': 'Tenant updated successfully'
            }
            
        except Exception as e:
            logger.error(f"Error updating tenant: {e}")
            if conn:
                conn.rollback()
            return {
                'success': False,
                'message': f'Error updating tenant: {str(e)}'
            }
        finally:
            self.close_connection()
    
    def deactivate_tenant(self, tenant_id):
        """Soft delete tenant (deactivate)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if tenant exists
            cursor.execute('SELECT business_name FROM tenants WHERE tenant_id = ?', (tenant_id,))
            tenant = cursor.fetchone()
            if not tenant:
                return {
                    'success': False,
                    'message': 'Tenant not found'
                }
            
            # Soft delete by setting is_active = 0
            cursor.execute('''
                UPDATE tenants 
                SET is_active = 0, status = 'deactivated', updated_at = ?
                WHERE tenant_id = ?
            ''', (datetime.now().isoformat(), tenant_id))
            
            # Also deactivate all tenant users
            cursor.execute('''
                UPDATE tenant_users 
                SET is_active = 0, updated_at = ?
                WHERE tenant_id = ?
            ''', (datetime.now().isoformat(), tenant_id))
            
            conn.commit()
            
            logger.info(f"✅ Tenant deactivated: {tenant[0]} ({tenant_id})")
            
            return {
                'success': True,
                'message': 'Tenant deactivated successfully'
            }
            
        except Exception as e:
            logger.error(f"Error deactivating tenant: {e}")
            if conn:
                conn.rollback()
            return {
                'success': False,
                'message': f'Error deactivating tenant: {str(e)}'
            }
        finally:
            self.close_connection()
    
    def reset_tenant_password(self, tenant_id, new_password=None):
        """Reset tenant password"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if tenant exists
            cursor.execute('SELECT business_name FROM tenants WHERE tenant_id = ?', (tenant_id,))
            tenant = cursor.fetchone()
            if not tenant:
                return {
                    'success': False,
                    'message': 'Tenant not found'
                }
            
            # Generate new password if not provided
            if not new_password:
                new_password = self.generate_password()
            
            # Update password
            password_hash = hash_password(new_password)
            cursor.execute('''
                UPDATE tenants 
                SET password_hash = ?, failed_login_attempts = 0, updated_at = ?
                WHERE tenant_id = ?
            ''', (password_hash, datetime.now().isoformat(), tenant_id))
            
            conn.commit()
            
            logger.info(f"✅ Password reset for tenant: {tenant[0]} ({tenant_id})")
            
            return {
                'success': True,
                'message': 'Password reset successfully',
                'new_password': new_password
            }
            
        except Exception as e:
            logger.error(f"Error resetting password: {e}")
            if conn:
                conn.rollback()
            return {
                'success': False,
                'message': f'Error resetting password: {str(e)}'
            }
        finally:
            self.close_connection()
    
    def get_tenant_analytics(self):
        """Get tenant analytics summary"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Total tenants
            cursor.execute('SELECT COUNT(*) FROM tenants WHERE is_active = 1')
            total_tenants = cursor.fetchone()[0]
            
            # Inactive tenants
            cursor.execute('SELECT COUNT(*) FROM tenants WHERE is_active = 0')
            inactive_tenants = cursor.fetchone()[0]
            
            # New tenants this month
            cursor.execute('''
                SELECT COUNT(*) FROM tenants 
                WHERE created_at >= date('now', 'start of month')
            ''')
            new_this_month = cursor.fetchone()[0]
            
            # Expired subscriptions
            cursor.execute('''
                SELECT COUNT(*) FROM tenants 
                WHERE plan_expiry_date < date('now') AND is_active = 1
            ''')
            expired_subscriptions = cursor.fetchone()[0]
            
            # Tenants by plan type
            cursor.execute('''
                SELECT plan_type, COUNT(*) as count
                FROM tenants 
                WHERE is_active = 1
                GROUP BY plan_type
                ORDER BY count DESC
            ''')
            plan_types = [{'type': row[0], 'count': row[1]} for row in cursor.fetchall()]
            
            # Recent registrations
            cursor.execute('''
                SELECT business_name, owner_name, email, plan_type, created_at
                FROM tenants
                ORDER BY created_at DESC
                LIMIT 10
            ''')
            recent_registrations = []
            for row in cursor.fetchall():
                recent_registrations.append({
                    'business_name': row[0],
                    'owner_name': row[1],
                    'email': row[2],
                    'plan_type': row[3],
                    'created_at': row[4]
                })
            
            return {
                'success': True,
                'analytics': {
                    'summary': {
                        'total_tenants': total_tenants,
                        'active_tenants': total_tenants,
                        'inactive_tenants': inactive_tenants,
                        'new_this_month': new_this_month,
                        'expired_subscriptions': expired_subscriptions
                    },
                    'plan_types': plan_types,
                    'recent_registrations': recent_registrations
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {
                'success': False,
                'message': f'Error getting analytics: {str(e)}'
            }
        finally:
            self.close_connection()