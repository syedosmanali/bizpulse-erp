"""
Role-Based Access Control (RBAC) decorators and session validation utilities.
Implements Task 2.4: Implement RBAC decorator and session validation
"""

from functools import wraps
from flask import session, jsonify, request, g
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Union

logger = logging.getLogger(__name__)


def session_required(f):
    """
    Decorator to ensure user session is valid and active.
    Checks for required session keys and validates session expiration.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in
        if 'user_id' not in session or not session.get('user_id'):
            logger.warning(f"Session validation failed: No user_id in session for {request.endpoint}")
            return jsonify({
                'success': False, 
                'message': 'Authentication required',
                'error_code': 'UNAUTHORIZED'
            }), 401
        
        # Check if user type is present
        user_type = session.get('user_type')
        if not user_type:
            logger.warning(f"Session validation failed: No user_type in session for {request.endpoint}")
            return jsonify({
                'success': False, 
                'message': 'Invalid session',
                'error_code': 'INVALID_SESSION'
            }), 401
        
        # Store user info in g for access in route functions
        g.current_user = {
            'user_id': session.get('user_id'),
            'user_type': user_type,
            'user_name': session.get('user_name'),
            'email': session.get('email'),
            'username': session.get('username'),
            'is_super_admin': session.get('is_super_admin', False),
            'permissions': session.get('permissions', [])
        }
        
        # Log successful session validation
        logger.info(f"✅ Session validation passed for user {session.get('user_id')} ({user_type}) accessing {request.endpoint}")
        
        return f(*args, **kwargs)
    
    return decorated_function


def rbac_required(required_permissions: Optional[Union[str, List[str]]] = None, 
                 allowed_user_types: Optional[List[str]] = None):
    """
    RBAC decorator to check user permissions and roles.
    
    Args:
        required_permissions: Permission(s) required to access the resource.
                             Can be a single permission string or list of permissions.
                             If None, only user type validation is performed.
        allowed_user_types: List of user types allowed to access the resource.
                           If None, all user types are allowed (permission-based only).
    """
    if required_permissions and isinstance(required_permissions, str):
        required_permissions = [required_permissions]
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # First check if session is valid
            if 'user_id' not in session or not session.get('user_id'):
                logger.warning(f"RBAC validation failed: No user_id in session for {request.endpoint}")
                return jsonify({
                    'success': False, 
                    'message': 'Authentication required',
                    'error_code': 'UNAUTHORIZED'
                }), 401
            
            user_type = session.get('user_type')
            user_id = session.get('user_id')
            is_super_admin = session.get('is_super_admin', False)
            user_permissions = session.get('permissions', [])
            
            # Check if user type is allowed
            if allowed_user_types and user_type not in allowed_user_types:
                logger.warning(f"RBAC validation failed: User type '{user_type}' not allowed for {request.endpoint}. "
                              f"Allowed types: {allowed_user_types}")
                return jsonify({
                    'success': False,
                    'message': 'Access denied: Insufficient privileges',
                    'error_code': 'FORBIDDEN_USER_TYPE'
                }), 403
            
            # Super admins bypass permission checks
            if is_super_admin:
                logger.info(f"Super admin access granted for user {user_id} to {request.endpoint}")
            else:
                # Check permissions if required
                if required_permissions:
                    # Convert user permissions to a flat list if they're nested
                    if isinstance(user_permissions, dict):
                        # If permissions are stored as a dict with modules/operations
                        user_perms_list = []
                        for module_perms in user_permissions.values():
                            if isinstance(module_perms, list):
                                user_perms_list.extend(module_perms)
                            elif isinstance(module_perms, dict):
                                user_perms_list.extend(list(module_perms.keys()))
                    elif isinstance(user_permissions, list):
                        user_perms_list = user_permissions
                    else:
                        user_perms_list = []
                    
                    # Check if user has any of the required permissions
                    has_permission = False
                    for perm in required_permissions:
                        if perm in user_perms_list:
                            has_permission = True
                            break
                    
                    if not has_permission:
                        logger.warning(f"RBAC validation failed: User {user_id} lacks required permissions "
                                      f"{required_permissions}. User has: {user_perms_list}")
                        return jsonify({
                            'success': False,
                            'message': 'Access denied: Insufficient permissions',
                            'required_permissions': required_permissions,
                            'user_permissions': user_perms_list,
                            'error_code': 'INSUFFICIENT_PERMISSIONS'
                        }), 403
            
            # Store user info in g for access in route functions
            g.current_user = {
                'user_id': user_id,
                'user_type': user_type,
                'user_name': session.get('user_name'),
                'email': session.get('email'),
                'username': session.get('username'),
                'is_super_admin': is_super_admin,
                'permissions': user_permissions
            }
            
            logger.info(f"✅ RBAC validation passed for user {user_id} ({user_type}) accessing {request.endpoint}")
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def validate_session_timeout():
    """
    Helper function to validate session timeout.
    Can be used to check if session has expired based on last activity.
    """
    if 'last_activity' in session:
        last_activity = datetime.fromisoformat(session['last_activity'])
        now = datetime.now()
        
        # Session timeout after 24 hours of inactivity
        if now - last_activity > timedelta(hours=24):
            session.clear()
            return False
    
    # Update last activity timestamp
    session['last_activity'] = datetime.now().isoformat()
    return True


def get_current_user():
    """
    Get current user information from session or g object.
    """
    if hasattr(g, 'current_user'):
        return g.current_user
    
    if 'user_id' in session:
        return {
            'user_id': session.get('user_id'),
            'user_type': session.get('user_type'),
            'user_name': session.get('user_name'),
            'email': session.get('email'),
            'username': session.get('username'),
            'is_super_admin': session.get('is_super_admin', False),
            'permissions': session.get('permissions', [])
        }
    
    return None


def has_permission(permission: str) -> bool:
    """
    Check if current user has a specific permission.
    
    Args:
        permission: The permission to check
        
    Returns:
        bool: True if user has permission, False otherwise
    """
    current_user = get_current_user()
    if not current_user:
        return False
    
    # Super admins have all permissions
    if current_user.get('is_super_admin', False):
        return True
    
    user_permissions = current_user.get('permissions', [])
    
    # Handle different permission storage formats
    if isinstance(user_permissions, dict):
        # If permissions are stored as a dict with modules/operations
        for module_perms in user_permissions.values():
            if isinstance(module_perms, list) and permission in module_perms:
                return True
            elif isinstance(module_perms, dict) and permission in module_perms:
                return True
    elif isinstance(user_permissions, list):
        if permission in user_permissions:
            return True
    
    return False


# Common permission constants
PERMISSIONS = {
    # Company/Firm Setup
    'company_view': 'View company information',
    'company_edit': 'Edit company information',
    
    # Bank Management
    'bank_view': 'View bank information',
    'bank_create': 'Create bank records',
    'bank_edit': 'Edit bank records',
    'bank_delete': 'Delete bank records',
    
    # Product Management
    'product_view': 'View products',
    'product_create': 'Create products',
    'product_edit': 'Edit products',
    'product_delete': 'Delete products',
    
    # Stock Management
    'stock_view': 'View stock',
    'stock_adjust': 'Adjust stock',
    'stock_transaction_view': 'View stock transactions',
    
    # Batch Management
    'batch_view': 'View batches',
    'batch_create': 'Create batches',
    'batch_edit': 'Edit batches',
    
    # Customer Management
    'customer_view': 'View customers',
    'customer_create': 'Create customers',
    'customer_edit': 'Edit customers',
    'customer_delete': 'Delete customers',
    
    # Vendor Management
    'vendor_view': 'View vendors',
    'vendor_create': 'Create vendors',
    'vendor_edit': 'Edit vendors',
    'vendor_delete': 'Delete vendors',
    
    # Invoice/Billing
    'invoice_view': 'View invoices',
    'invoice_create': 'Create invoices',
    'invoice_edit': 'Edit invoices',
    'invoice_delete': 'Delete invoices',
    
    # Purchase Management
    'purchase_view': 'View purchases',
    'purchase_create': 'Create purchases',
    'purchase_edit': 'Edit purchases',
    'purchase_delete': 'Delete purchases',
    
    # Purchase Orders
    'po_view': 'View purchase orders',
    'po_create': 'Create purchase orders',
    'po_edit': 'Edit purchase orders',
    'po_approve': 'Approve purchase orders',
    
    # GRN
    'grn_view': 'View GRNs',
    'grn_create': 'Create GRNs',
    'grn_edit': 'Edit GRNs',
    
    # Challan
    'challan_view': 'View challans',
    'challan_create': 'Create challans',
    'challan_edit': 'Edit challans',
    
    # Payment Management
    'payment_view': 'View payments',
    'payment_create': 'Create payments',
    'payment_edit': 'Edit payments',
    
    # Income/Expense
    'transaction_view': 'View transactions',
    'transaction_create': 'Create transactions',
    'transaction_edit': 'Edit transactions',
    
    # Reports
    'report_view': 'View reports',
    'report_export': 'Export reports',
    
    # Staff Management
    'staff_view': 'View staff',
    'staff_create': 'Create staff',
    'staff_edit': 'Edit staff',
    'staff_delete': 'Delete staff',
    
    # Settings/Backup
    'settings_view': 'View settings',
    'settings_edit': 'Edit settings',
    'backup_create': 'Create backups',
    'backup_restore': 'Restore backups'
}


# Common user type constants
USER_TYPES = {
    'admin': 'System Administrator',
    'client': 'Business Owner',
    'employee': 'Employee/User',
    'staff': 'Staff Member',
    'operator': 'Operator'
}


def register_rbac_routes(app):
    """
    Register RBAC-related utility routes.
    """
    @app.route('/api/auth/session-status', methods=['GET'])
    @session_required
    def session_status():
        """Check current session status and user info."""
        current_user = get_current_user()
        
        return jsonify({
            'success': True,
            'session_valid': True,
            'user': {
                'user_id': current_user['user_id'],
                'user_type': current_user['user_type'],
                'user_name': current_user['user_name'],
                'email': current_user['email'],
                'is_super_admin': current_user['is_super_admin'],
                'has_permissions': bool(current_user['permissions'])
            },
            'permissions': current_user['permissions']
        })
    
    @app.route('/api/auth/check-permission', methods=['POST'])
    def check_permission():
        """Check if current user has a specific permission."""
        if 'user_id' not in session:
            return jsonify({'has_permission': False}), 401
        
        data = request.get_json()
        permission = data.get('permission')
        
        if not permission:
            return jsonify({'error': 'Permission parameter required'}), 400
        
        has_perm = has_permission(permission)
        
        return jsonify({
            'has_permission': has_perm,
            'permission': permission
        })