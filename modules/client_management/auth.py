"""
Client Management Authentication & Authorization
Role-based access control for tenant management
"""

from functools import wraps
from flask import session, redirect, url_for, jsonify, request
from modules.shared.database import get_db_connection
import logging

logger = logging.getLogger(__name__)

# Role definitions
ROLES = {
    'SUPER_ADMIN': 'SUPER_ADMIN',
    'CLIENT_ADMIN': 'CLIENT_ADMIN', 
    'CLIENT_USER': 'CLIENT_USER'
}

def get_current_user_role():
    """Get current user's role from session"""
    return session.get('user_role', 'CLIENT_USER')

def get_current_tenant_id():
    """Get current user's tenant ID from session"""
    return session.get('tenant_id')

def is_super_admin():
    """Check if current user is super admin"""
    user_role = get_current_user_role()
    user_email = session.get('email', '').lower()
    
    # Check role or email-based super admin
    return (user_role == ROLES['SUPER_ADMIN'] or 
            user_email in ['admin@bizpulse.com', 'bizpulse.erp@gmail.com'] or
            session.get('is_super_admin', False))

def require_super_admin(f):
    """Decorator to require super admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_super_admin():
            logger.warning(f"Unauthorized access attempt to {request.endpoint} by user {session.get('email')}")
            
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'error': 'Access denied. Super admin privileges required.',
                    'code': 'INSUFFICIENT_PRIVILEGES'
                }), 403
            else:
                return redirect(url_for('main.login'))
        
        return f(*args, **kwargs)
    return decorated_function

def require_client_admin(f):
    """Decorator to require client admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_role = get_current_user_role()
        
        if user_role not in [ROLES['SUPER_ADMIN'], ROLES['CLIENT_ADMIN']]:
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'error': 'Access denied. Admin privileges required.',
                    'code': 'INSUFFICIENT_PRIVILEGES'
                }), 403
            else:
                return redirect(url_for('main.login'))
        
        return f(*args, **kwargs)
    return decorated_function

def require_tenant_access(f):
    """Decorator to ensure user has access to tenant data"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if is_super_admin():
            # Super admin can access all tenants
            return f(*args, **kwargs)
        
        user_tenant_id = get_current_tenant_id()
        if not user_tenant_id:
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'error': 'No tenant access',
                    'code': 'NO_TENANT_ACCESS'
                }), 403
            else:
                return redirect(url_for('main.login'))
        
        return f(*args, **kwargs)
    return decorated_function

def filter_by_tenant(query, tenant_id_param='tenant_id'):
    """Add tenant filter to database queries"""
    if is_super_admin():
        # Super admin sees all data
        return query
    
    user_tenant_id = get_current_tenant_id()
    if user_tenant_id:
        return f"{query} AND {tenant_id_param} = '{user_tenant_id}'"
    else:
        # No tenant access - return empty result
        return f"{query} AND 1=0"

def get_tenant_context():
    """Get current tenant context for queries"""
    if is_super_admin():
        return None  # No filtering for super admin
    
    return get_current_tenant_id()

def validate_tenant_access(tenant_id):
    """Validate if current user can access specific tenant"""
    if is_super_admin():
        return True
    
    user_tenant_id = get_current_tenant_id()
    return user_tenant_id == tenant_id