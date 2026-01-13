"""
Notifications Module Routes
Handles notification system for the dashboard
"""

from flask import Blueprint, request, jsonify, session
from modules.shared.database import get_db_connection, generate_id
from modules.shared.auth_decorators import require_auth
from datetime import datetime, timedelta
import json

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

@notifications_bp.route('', methods=['GET'])
@require_auth
def get_notifications():
    """Get all notifications for the current user"""
    try:
        user_id = session.get('user_id')
        client_id = session.get('client_id') or user_id  # Handle both client and employee sessions
        
        if not client_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        # Check if requesting recent notifications only
        recent_only = request.args.get('recent') == 'true'
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if recent_only:
            # Get notifications from last 5 minutes for real-time alerts
            cursor.execute("""
                SELECT id, type, message, action_url, is_read, created_at
                FROM notifications 
                WHERE user_id = ? AND datetime(created_at) > datetime('now', '-5 minutes')
                ORDER BY created_at DESC 
                LIMIT 10
            """, (client_id,))
        else:
            # Get all notifications (last 50)
            cursor.execute("""
                SELECT id, type, message, action_url, is_read, created_at
                FROM notifications 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT 50
            """, (client_id,))
        
        notifications = []
        for row in cursor.fetchall():
            notifications.append({
                'id': row[0],
                'type': row[1],
                'message': row[2],
                'action_url': row[3],
                'is_read': bool(row[4]),
                'created_at': row[5]
            })
        
        # Count unread notifications
        cursor.execute("SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0", (client_id,))
        unread_count = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'notifications': notifications,
            'unread_count': unread_count,
            'recent_only': recent_only
        })
        
    except Exception as e:
        print(f"❌ Error getting notifications: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@notifications_bp.route('/<notification_id>/read', methods=['POST'])
@require_auth
def mark_notification_read(notification_id):
    """Mark a specific notification as read"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Mark notification as read
        cursor.execute("""
            UPDATE notifications 
            SET is_read = 1 
            WHERE id = ? AND user_id = ?
        """, (notification_id, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"❌ Error marking notification as read: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@notifications_bp.route('/mark-all-read', methods=['POST'])
@require_auth
def mark_all_notifications_read():
    """Mark all notifications as read for the current user"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Mark all notifications as read
        cursor.execute("""
            UPDATE notifications 
            SET is_read = 1 
            WHERE user_id = ? AND is_read = 0
        """, (user_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"❌ Error marking all notifications as read: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@notifications_bp.route('/settings', methods=['GET'])
@require_auth
def get_notification_settings():
    """Get notification settings for the current client"""
    try:
        user_id = session.get('user_id')
        client_id = session.get('client_id') or user_id  # Handle both client and employee sessions
        
        if not client_id:
            return jsonify({'success': False, 'error': 'Client not authenticated'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get or create default settings for this client
        cursor.execute("""
            SELECT low_stock_enabled, low_stock_threshold, updated_at
            FROM notification_settings 
            WHERE client_id = ?
        """, (client_id,))
        
        settings = cursor.fetchone()
        
        if not settings:
            # Create default settings for new client
            settings_id = generate_id()
            cursor.execute("""
                INSERT INTO notification_settings (id, client_id, low_stock_enabled, low_stock_threshold, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (settings_id, client_id, 1, 5, datetime.now().isoformat()))
            conn.commit()
            
            # Return default settings
            result = {
                'success': True,
                'settings': {
                    'low_stock_enabled': True,
                    'low_stock_threshold': 5,
                    'updated_at': datetime.now().isoformat()
                }
            }
        else:
            result = {
                'success': True,
                'settings': {
                    'low_stock_enabled': bool(settings[0]),
                    'low_stock_threshold': settings[1],
                    'updated_at': settings[2]
                }
            }
        
        conn.close()
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Error getting notification settings: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@notifications_bp.route('/settings', methods=['POST'])
@require_auth
def save_notification_settings():
    """Save notification settings for the current client"""
    try:
        user_id = session.get('user_id')
        client_id = session.get('client_id') or user_id  # Handle both client and employee sessions
        
        if not client_id:
            return jsonify({'success': False, 'error': 'Client not authenticated'}), 401
        
        data = request.get_json()
        low_stock_enabled = bool(data.get('low_stock_enabled', True))
        low_stock_threshold = int(data.get('low_stock_threshold', 5))
        
        # Validate threshold
        if low_stock_threshold < 0:
            return jsonify({'success': False, 'error': 'Threshold must be 0 or greater'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if settings exist for this client
        cursor.execute("SELECT id FROM notification_settings WHERE client_id = ?", (client_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing settings
            cursor.execute("""
                UPDATE notification_settings 
                SET low_stock_enabled = ?, low_stock_threshold = ?, updated_at = ?
                WHERE client_id = ?
            """, (low_stock_enabled, low_stock_threshold, datetime.now().isoformat(), client_id))
        else:
            # Create new settings
            settings_id = generate_id()
            cursor.execute("""
                INSERT INTO notification_settings (id, client_id, low_stock_enabled, low_stock_threshold, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (settings_id, client_id, low_stock_enabled, low_stock_threshold, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        print(f"✅ [NOTIFICATION SETTINGS] Saved for client {client_id}: enabled={low_stock_enabled}, threshold={low_stock_threshold}")
        
        return jsonify({
            'success': True,
            'message': 'Notification settings saved successfully',
            'settings': {
                'low_stock_enabled': low_stock_enabled,
                'low_stock_threshold': low_stock_threshold,
                'updated_at': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        print(f"❌ Error saving notification settings: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
@require_auth
def create_notification():
    """Create a new notification (for testing or internal use)"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        notification_type = data.get('type', 'info')
        message = data.get('message', '')
        action_url = data.get('action_url', '')
        
        if not message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create notification
        cursor.execute("""
            INSERT INTO notifications (user_id, type, message, action_url, is_read, created_at)
            VALUES (?, ?, ?, ?, 0, ?)
        """, (user_id, notification_type, message, action_url, datetime.now().isoformat()))
        
        conn.commit()
        notification_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            'success': True,
            'notification_id': notification_id
        })
        
    except Exception as e:
        print(f"❌ Error creating notification: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def create_notification_for_user(user_id, notification_type, message, action_url=None):
    """Helper function to create notifications programmatically"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        notification_id = generate_id()
        cursor.execute("""
            INSERT INTO notifications (id, user_id, type, message, action_url, is_read, created_at)
            VALUES (?, ?, ?, ?, ?, 0, ?)
        """, (notification_id, user_id, notification_type, message, action_url, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return notification_id
        
    except Exception as e:
        print(f"❌ Error creating notification for user {user_id}: {e}")
        return None

def create_stock_alert_notification(client_id, product_name, current_stock, category=""):
    """Helper function specifically for stock alerts"""
    try:
        if current_stock == 0:
            message = f"Out of Stock: {product_name}"
            if category:
                message += f" ({category})"
        else:
            message = f"Low Stock Alert: {product_name} - Only {current_stock} remaining"
            if category:
                message += f" ({category})"
        
        return create_notification_for_user(
            user_id=client_id,
            notification_type='alert',
            message=message,
            action_url='/retail/products'
        )
        
    except Exception as e:
        print(f"❌ Error creating stock alert for client {client_id}: {e}")
        return None

def create_notification_for_all_users(notification_type, message, action_url=None):
    """Helper function to create notifications for all users"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all user IDs
        cursor.execute("SELECT id FROM users WHERE active = 1")
        user_ids = [row[0] for row in cursor.fetchall()]
        
        # Create notification for each user
        for user_id in user_ids:
            cursor.execute("""
                INSERT INTO notifications (user_id, type, message, action_url, is_read, created_at)
                VALUES (?, ?, ?, ?, 0, ?)
            """, (user_id, notification_type, message, action_url, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return len(user_ids)
        
    except Exception as e:
        print(f"❌ Error creating notifications for all users: {e}")
        return 0

@notifications_bp.route('/create', methods=['POST'])
@require_auth
def create_notification():
    """Create a new notification (for testing or internal use)"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        client_id = session.get('client_id') or user_id  # Handle both client and employee sessions
        
        if not client_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        notification_type = data.get('type', 'info')
        message = data.get('message', '')
        action_url = data.get('action_url', '')
        
        if not message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        
        notification_id = create_notification_for_user(
            user_id=client_id,
            notification_type=notification_type,
            message=message,
            action_url=action_url
        )
        
        if notification_id:
            return jsonify({
                'success': True,
                'notification_id': notification_id,
                'message': 'Notification created successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to create notification'}), 500
        
    except Exception as e:
        print(f"❌ Error creating notification: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500