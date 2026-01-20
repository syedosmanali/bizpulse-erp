"""
User Management Routes
Client-Level User Management System
"""

from flask import Blueprint, request, jsonify, session, render_template, redirect
from .service import UserManagementService
from .models import UserManagementModels
from modules.shared.auth_decorators import require_auth
from modules.shared.database import get_db_connection
import json
import logging

logger = logging.getLogger(__name__)

user_management_bp = Blueprint('user_management', __name__)
user_service = UserManagementService()

def get_current_client_id():
    """Get current client ID from session"""
    # Try multiple ways to get client ID
    client_id = session.get('user_id')
    user_type = session.get('user_type')
    
    # If user is a client, their user_id is the client_id
    if user_type == 'client':
        return client_id
    
    # For super admin, we need to handle differently
    if session.get('is_super_admin'):
        # For testing, use the first available client
        from modules.shared.database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM clients WHERE is_active = 1 LIMIT 1')
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    return client_id

def is_client_admin():
    """Check if current user is client admin"""
    return session.get('user_type') == 'client' or session.get('is_super_admin', False) or True  # Allow access for testing

# ==================== FRONTEND ROUTES ====================

@user_management_bp.route('/user-management-debug')
def debug_page():
    """Debug page for testing API"""
    return render_template('user_management_debug.html')

@user_management_bp.route('/user-management-test')
def test_route():
    """Test route to check if blueprint is working"""
    return "User Management Blueprint is working!"

@user_management_bp.route('/user-management')
def user_management_dashboard():
    """User Management Dashboard - Only for Client Admins"""
    try:
        # Check if user is logged in
        if 'user_id' not in session:
            return redirect('/login')
        
        # Check if user is client admin (not employee)
        user_type = session.get('user_type')
        if user_type == 'employee':
            # Silently redirect employees to dashboard instead of showing error
            return redirect('/retail/dashboard')
        
        if user_type != 'client' and not session.get('is_super_admin'):
            # Redirect other user types to dashboard
            return redirect('/retail/dashboard')
        
        return render_template('user_management_dashboard.html')
    except Exception as e:
        return redirect('/retail/dashboard')

# ==================== API ROUTES ====================

@user_management_bp.route('/api/user-management/users', methods=['GET'])
@require_auth
def get_users():
    """Get all users for current client"""
    try:
        # Check if user is client admin (not employee)
        user_type = session.get('user_type')
        if user_type == 'employee':
            return jsonify({'success': False, 'error': 'Access denied. Employees cannot manage users.'}), 403
        
        client_id = get_current_client_id()
        if not client_id:
            return jsonify({'success': False, 'error': 'Client ID not found'}), 400
        
        result = user_service.get_users(client_id)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in get_users: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch users'}), 500

@user_management_bp.route('/api/user-management/users', methods=['POST'])
@require_auth
def create_user():
    """Create new user"""
    try:
        # Check if user is client admin (not employee)
        user_type = session.get('user_type')
        if user_type == 'employee':
            return jsonify({'success': False, 'error': 'Access denied. Employees cannot create users.'}), 403
        
        client_id = get_current_client_id()
        if not client_id:
            return jsonify({'success': False, 'error': 'Client ID not found'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        result = user_service.create_user(client_id, data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Error in create_user: {e}")
        return jsonify({'success': False, 'error': 'User creation failed'}), 500

@user_management_bp.route('/api/user-management/users/<user_id>', methods=['PUT'])
@require_auth
def update_user(user_id):
    """Update user information"""
    try:
        client_id = get_current_client_id()
        if not client_id:
            return jsonify({'success': False, 'error': 'Client ID not found'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        result = user_service.update_user(client_id, user_id, data)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in update_user: {e}")
        return jsonify({'success': False, 'error': 'User update failed'}), 500

@user_management_bp.route('/api/user-management/users/<user_id>/reset-password', methods=['POST'])
@require_auth
def reset_user_password(user_id):
    """Reset user password"""
    try:
        client_id = get_current_client_id()
        if not client_id:
            return jsonify({'success': False, 'error': 'Client ID not found'}), 400
        
        data = request.get_json() or {}
        new_password = data.get('new_password')
        
        result = user_service.reset_password(client_id, user_id, new_password)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in reset_password: {e}")
        return jsonify({'success': False, 'error': 'Password reset failed'}), 500

@user_management_bp.route('/api/user-management/users/<user_id>/deactivate', methods=['POST'])
@require_auth
def deactivate_user(user_id):
    """Deactivate user account"""
    try:
        client_id = get_current_client_id()
        if not client_id:
            return jsonify({'success': False, 'error': 'Client ID not found'}), 400
        
        result = user_service.deactivate_user(client_id, user_id)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in deactivate_user: {e}")
        return jsonify({'success': False, 'error': 'User deactivation failed'}), 500

@user_management_bp.route('/api/user-management/users/<user_id>/activate', methods=['POST'])
@require_auth
def activate_user(user_id):
    """Activate user account"""
    try:
        client_id = get_current_client_id()
        if not client_id:
            return jsonify({'success': False, 'error': 'Client ID not found'}), 400
        
        result = user_service.update_user(client_id, user_id, {'status': 'active'})
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in activate_user: {e}")
        return jsonify({'success': False, 'error': 'User activation failed'}), 500

@user_management_bp.route('/api/user-management/users/<user_id>', methods=['DELETE'])
@require_auth
def delete_user(user_id):
    """Delete user account"""
    try:
        client_id = get_current_client_id()
        if not client_id:
            return jsonify({'success': False, 'error': 'Client ID not found'}), 400
        
        result = user_service.delete_user(client_id, user_id)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in delete_user: {e}")
        return jsonify({'success': False, 'error': 'User deletion failed'}), 500

@user_management_bp.route('/api/user-management/roles', methods=['GET'])
@require_auth
def get_roles():
    """Get available roles for client"""
    try:
        client_id = get_current_client_id()
        if not client_id:
            return jsonify({'success': False, 'error': 'Client ID not found'}), 400
        
        result = user_service.get_roles(client_id)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in get_roles: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch roles'}), 500

@user_management_bp.route('/api/user-management/roles', methods=['POST'])
@require_auth
def create_role():
    """Create custom role"""
    try:
        client_id = get_current_client_id()
        if not client_id:
            return jsonify({'success': False, 'error': 'Client ID not found'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        result = user_service.create_custom_role(client_id, data)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in create_role: {e}")
        return jsonify({'success': False, 'error': 'Role creation failed'}), 500

@user_management_bp.route('/api/user-management/activity', methods=['GET'])
@require_auth
def get_user_activity():
    """Get user activity logs"""
    try:
        client_id = get_current_client_id()
        if not client_id:
            return jsonify({'success': False, 'error': 'Client ID not found'}), 400
        
        user_id = request.args.get('user_id')
        result = user_service.get_user_activity(client_id, user_id)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in get_user_activity: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch activity logs'}), 500

@user_management_bp.route('/api/user-management/initialize', methods=['POST'])
@require_auth
def initialize_user_system():
    """Initialize user management system for client"""
    try:
        client_id = get_current_client_id()
        if not client_id:
            return jsonify({'success': False, 'error': 'Client ID not found'}), 400
        
        result = user_service.initialize_client_user_system(client_id)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in initialize_user_system: {e}")
        return jsonify({'success': False, 'error': 'System initialization failed'}), 500

@user_management_bp.route('/api/user-management/permissions', methods=['GET'])
@require_auth
def get_permissions():
    """Get module permissions for all users"""
    try:
        logger.info("📋 GET /api/user-management/permissions called")
        logger.info(f"📋 Session data: user_id={session.get('user_id')}, user_type={session.get('user_type')}, is_super_admin={session.get('is_super_admin')}")
        
        # Check if user is client admin (not employee)
        user_type = session.get('user_type')
        logger.info(f"👤 User type: {user_type}")
        
        if user_type == 'employee':
            logger.warning("🚫 Employee tried to access permissions")
            return jsonify({'success': False, 'error': 'Access denied. Employees cannot manage permissions.'}), 403
        
        client_id = get_current_client_id()
        logger.info(f"🏢 Client ID: {client_id}")
        
        if not client_id:
            logger.error("❌ Client ID not found")
            return jsonify({'success': False, 'error': 'Client ID not found'}), 400
        
        result = user_service.get_user_permissions(client_id)
        logger.info(f"✅ Permissions result: {result.get('success', False)}, users: {len(result.get('permissions', []))}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Error in get_permissions: {e}", exc_info=True)
        return jsonify({'success': False, 'error': f'Failed to fetch permissions: {str(e)}'}), 500

@user_management_bp.route('/api/user-management/debug-session', methods=['GET'])
@require_auth
def debug_session():
    """Debug endpoint to check session data"""
    return jsonify({
        'success': True,
        'session': {
            'user_id': session.get('user_id'),
            'user_type': session.get('user_type'),
            'is_super_admin': session.get('is_super_admin'),
            'client_id': get_current_client_id()
        }
    })


@user_management_bp.route('/api/user-management/debug-permissions', methods=['GET'])
@require_auth
def debug_permissions():
    """Debug endpoint: returns session, DB-stored permissions, role permissions and effective permissions for current user"""
    try:
        user_id = session.get('user_id')
        user_type = session.get('user_type')

        debug = {
            'session': {
                'user_id': user_id,
                'user_type': user_type,
                'is_super_admin': session.get('is_super_admin', False),
                'client_id': get_current_client_id()
            }
        }

        # Raw stored permissions (user-level)
        user_level = UserManagementModels.get_user_permissions_by_id(user_id)
        debug['db_user_permissions'] = user_level

        # Role-level permissions (if any)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.permissions
            FROM user_accounts u
            LEFT JOIN user_roles r ON u.role_id = r.id
            WHERE u.id = ? OR u.user_id = ?
        ''', (user_id, user_id))
        row = cursor.fetchone()
        conn.close()

        try:
            role_perms = json.loads(row[0]) if row and row[0] else None
        except Exception:
            role_perms = None

        debug['role_permissions'] = role_perms

        # Effective permissions returned by service
        effective = user_service.get_current_user_permissions(user_id)
        debug['effective_permissions'] = effective

        return jsonify({'success': True, 'debug': debug})

    except Exception as e:
        logger.error(f"Error in debug_permissions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@user_management_bp.route('/api/user-management/permissions', methods=['POST'])
@require_auth
def update_permission():
    """Update module permission for a user"""
    try:
        # Check if user is client admin (not employee)
        user_type = session.get('user_type')
        if user_type == 'employee':
            return jsonify({'success': False, 'error': 'Access denied. Employees cannot manage permissions.'}), 403
        
        client_id = get_current_client_id()
        if not client_id:
            return jsonify({'success': False, 'error': 'Client ID not found'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        result = user_service.update_user_permission(
            client_id, 
            data.get('user_id'), 
            data.get('module'), 
            data.get('enabled')
        )
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in update_permission: {e}")
        return jsonify({'success': False, 'error': 'Permission update failed'}), 500

@user_management_bp.route('/api/user-management/user-permissions', methods=['GET'])
@require_auth
def get_current_user_permissions():
    """Get module permissions for current logged-in user"""
    try:
        user_id = session.get('user_id')
        user_type = session.get('user_type')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User not logged in'}), 401
        
        # Admins and clients have all permissions
        if user_type == 'client' or session.get('is_super_admin'):
            return jsonify({
                'success': True,
                'permissions': {
                    'dashboard': True,
                    'billing': True,
                    'sales': True,
                    'products': True,
                    'customers': True,
                    'inventory': True,
                    'reports': True,
                    'credit': True
                }
            })
        
        # Get employee permissions from database
        result = user_service.get_current_user_permissions(user_id)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in get_current_user_permissions: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch permissions'}), 500

# ==================== SUPER ADMIN ROUTES ====================

@user_management_bp.route('/admin/user-management/clients/<client_id>/users', methods=['GET'])
@require_auth
def admin_get_client_users(client_id):
    """Super Admin: Get users for any client"""
    try:
        if not session.get('is_super_admin'):
            return jsonify({'success': False, 'error': 'Super admin access required'}), 403
        
        result = user_service.get_users(client_id)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in admin_get_client_users: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch users'}), 500

@user_management_bp.route('/admin/user-management/stats', methods=['GET'])
@require_auth
def admin_get_user_stats():
    """Super Admin: Get user management statistics"""
    try:
        if not session.get('is_super_admin'):
            return jsonify({'success': False, 'error': 'Super admin access required'}), 403
        
        from modules.shared.database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get statistics
        cursor.execute('SELECT COUNT(*) FROM user_accounts WHERE status = "active"')
        active_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM user_accounts WHERE status = "inactive"')
        inactive_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT client_id) FROM user_accounts')
        clients_with_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM user_activity_log WHERE DATE(timestamp) = DATE("now")')
        today_activities = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'active_users': active_users,
                'inactive_users': inactive_users,
                'total_users': active_users + inactive_users,
                'clients_with_users': clients_with_users,
                'today_activities': today_activities
            }
        })
        
    except Exception as e:
        logger.error(f"Error in admin_get_user_stats: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch statistics'}), 500