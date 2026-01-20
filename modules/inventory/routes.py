"""
Comprehensive Inventory Management System
Handles all types of inventory: Assets, Equipment, Supplies, Products, etc.
"""

from flask import Blueprint, request, jsonify, session, render_template
from modules.shared.database import get_db_connection, generate_id
from modules.shared.auth_decorators import require_auth
from datetime import datetime
import json

inventory_bp = Blueprint('inventory', __name__, url_prefix='/api/inventory')

def get_user_id_from_session():
    """Get user_id from session for filtering data"""
    user_type = session.get('user_type')
    if user_type == 'employee':
        return session.get('client_id')
    else:
        return session.get('user_id')

# ==================== INVENTORY CATEGORIES ====================

@inventory_bp.route('/categories', methods=['GET'])
@require_auth
def get_inventory_categories():
    """Get all inventory categories"""
    try:
        user_id = get_user_id_from_session()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get default categories + custom categories for this user
        cursor.execute("""
            SELECT id, name, description, icon, color, is_default, created_at
            FROM inventory_categories 
            WHERE is_default = 1 OR user_id = ?
            ORDER BY is_default DESC, name ASC
        """, (user_id,))
        
        categories = []
        for row in cursor.fetchall():
            categories.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'icon': row[3],
                'color': row[4],
                'is_default': bool(row[5]),
                'created_at': row[6]
            })
        
        conn.close()
        return jsonify({'success': True, 'categories': categories})
        
    except Exception as e:
        print(f"❌ Error getting inventory categories: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@inventory_bp.route('/categories', methods=['POST'])
@require_auth
def create_inventory_category():
    """Create a new inventory category"""
    try:
        user_id = get_user_id_from_session()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        data = request.get_json()
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        icon = data.get('icon', '📦')
        color = data.get('color', '#732C3F')
        
        if not name:
            return jsonify({'success': False, 'error': 'Category name is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if category already exists for this user
        cursor.execute("""
            SELECT id FROM inventory_categories 
            WHERE name = ? AND (user_id = ? OR is_default = 1)
        """, (name, user_id))
        
        if cursor.fetchone():
            return jsonify({'success': False, 'error': 'Category already exists'}), 400
        
        # Create new category
        category_id = generate_id()
        cursor.execute("""
            INSERT INTO inventory_categories (
                id, name, description, icon, color, user_id, is_default, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, 0, ?)
        """, (category_id, name, description, icon, color, user_id, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Category created successfully',
            'category_id': category_id
        })
        
    except Exception as e:
        print(f"❌ Error creating inventory category: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== INVENTORY ITEMS ====================

@inventory_bp.route('/items', methods=['GET'])
@require_auth
def get_inventory_items():
    """Get all inventory items with filtering options"""
    try:
        user_id = get_user_id_from_session()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get query parameters for filtering
        category_id = request.args.get('category_id')
        item_type = request.args.get('item_type')
        status = request.args.get('status')
        search = request.args.get('search', '').strip()
        limit = request.args.get('limit', type=int)
        
        # Build query with filters
        query = """
            SELECT i.*, c.name as category_name, c.icon as category_icon
            FROM inventory_items i
            LEFT JOIN inventory_categories c ON i.category_id = c.id
            WHERE i.user_id = ? AND i.is_active = 1
        """
        params = [user_id]
        
        if category_id:
            query += " AND i.category_id = ?"
            params.append(category_id)
        
        if item_type:
            query += " AND i.item_type = ?"
            params.append(item_type)
        
        if status:
            query += " AND i.status = ?"
            params.append(status)
        
        if search:
            query += " AND (i.name LIKE ? OR i.description LIKE ?)"
            params.extend([f'%{search}%', f'%{search}%'])
        
        query += " ORDER BY i.created_at DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        
        items = []
        for row in cursor.fetchall():
            items.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'item_type': row[3],
                'category_id': row[4],
                'serial_number': row[5],
                'barcode': row[6],
                'quantity': row[7],
                'unit': row[8],
                'purchase_price': row[9],
                'current_value': row[10],
                'location': row[11],
                'supplier': row[12],
                'purchase_date': row[13],
                'warranty_expiry': row[14],
                'status': row[15],
                'condition': row[16],
                'notes': row[17],
                'user_id': row[18],
                'is_active': row[19],
                'created_at': row[20],
                'updated_at': row[21],
                'category_name': row[22],
                'category_icon': row[23]
            })
        
        conn.close()
        return jsonify({'success': True, 'items': items})
        
    except Exception as e:
        print(f"❌ Error getting inventory items: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@inventory_bp.route('/items', methods=['POST'])
@require_auth
def create_inventory_item():
    """Create a new inventory item"""
    try:
        user_id = get_user_id_from_session()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        data = request.get_json()
        
        # Required fields
        name = data.get('name', '').strip()
        item_type = data.get('item_type', '').strip()
        
        if not name:
            return jsonify({'success': False, 'error': 'Item name is required'}), 400
        
        if not item_type:
            return jsonify({'success': False, 'error': 'Item type is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create new item
        item_id = generate_id()
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO inventory_items (
                id, name, description, item_type, category_id, serial_number, barcode,
                quantity, unit, purchase_price, current_value, location, supplier,
                purchase_date, warranty_expiry, status, condition, notes,
                user_id, is_active, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
        """, (
            item_id,
            name,
            data.get('description', ''),
            item_type,
            data.get('category_id'),
            data.get('serial_number', ''),
            data.get('barcode', ''),
            data.get('quantity', 1),
            data.get('unit', 'piece'),
            data.get('purchase_price', 0.0),
            data.get('current_value', 0.0),
            data.get('location', ''),
            data.get('supplier', ''),
            data.get('purchase_date'),
            data.get('warranty_expiry'),
            data.get('status', 'active'),
            data.get('condition', 'good'),
            data.get('notes', ''),
            user_id,
            now,
            now
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Item created successfully',
            'item_id': item_id
        })
        
    except Exception as e:
        print(f"❌ Error creating inventory item: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@inventory_bp.route('/items/<item_id>', methods=['PUT'])
@require_auth
def update_inventory_item(item_id):
    """Update an inventory item"""
    try:
        user_id = get_user_id_from_session()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if item exists and belongs to user
        cursor.execute("SELECT id FROM inventory_items WHERE id = ? AND user_id = ?", (item_id, user_id))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Item not found'}), 404
        
        # Update item
        now = datetime.now().isoformat()
        
        cursor.execute("""
            UPDATE inventory_items SET
                name = ?, description = ?, item_type = ?, category_id = ?,
                serial_number = ?, barcode = ?, quantity = ?, unit = ?,
                purchase_price = ?, current_value = ?, location = ?, supplier = ?,
                purchase_date = ?, warranty_expiry = ?, status = ?, condition = ?,
                notes = ?, updated_at = ?
            WHERE id = ? AND user_id = ?
        """, (
            data.get('name', ''),
            data.get('description', ''),
            data.get('item_type', ''),
            data.get('category_id'),
            data.get('serial_number', ''),
            data.get('barcode', ''),
            data.get('quantity', 1),
            data.get('unit', 'piece'),
            data.get('purchase_price', 0.0),
            data.get('current_value', 0.0),
            data.get('location', ''),
            data.get('supplier', ''),
            data.get('purchase_date'),
            data.get('warranty_expiry'),
            data.get('status', 'active'),
            data.get('condition', 'good'),
            data.get('notes', ''),
            now,
            item_id,
            user_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Item updated successfully'})
        
    except Exception as e:
        print(f"❌ Error updating inventory item: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@inventory_bp.route('/items/<item_id>', methods=['DELETE'])
@require_auth
def delete_inventory_item(item_id):
    """Delete (deactivate) an inventory item"""
    try:
        user_id = get_user_id_from_session()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if item exists and belongs to user
        cursor.execute("SELECT id FROM inventory_items WHERE id = ? AND user_id = ?", (item_id, user_id))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Item not found'}), 404
        
        # Soft delete (deactivate)
        now = datetime.now().isoformat()
        cursor.execute("""
            UPDATE inventory_items SET is_active = 0, updated_at = ?
            WHERE id = ? AND user_id = ?
        """, (now, item_id, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Item deleted successfully'})
        
    except Exception as e:
        print(f"❌ Error deleting inventory item: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== INVENTORY MOVEMENTS ====================

@inventory_bp.route('/movements', methods=['GET'])
@require_auth
def get_inventory_movements():
    """Get inventory movements with optional item filter"""
    try:
        user_id = get_user_id_from_session()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        item_id = request.args.get('item_id')
        limit = request.args.get('limit', 50, type=int)
        
        if item_id:
            # Get movements for specific item
            cursor.execute("""
                SELECT m.*, i.name as item_name
                FROM inventory_movements m
                JOIN inventory_items i ON m.item_id = i.id
                WHERE m.item_id = ? AND i.user_id = ?
                ORDER BY m.created_at DESC
                LIMIT ?
            """, (item_id, user_id, limit))
        else:
            # Get all movements for user's items
            cursor.execute("""
                SELECT m.*, i.name as item_name
                FROM inventory_movements m
                JOIN inventory_items i ON m.item_id = i.id
                WHERE i.user_id = ?
                ORDER BY m.created_at DESC
                LIMIT ?
            """, (user_id, limit))
        
        movements = []
        for row in cursor.fetchall():
            movements.append({
                'id': row[0],
                'item_id': row[1],
                'movement_type': row[2],
                'quantity': row[3],
                'from_location': row[4],
                'to_location': row[5],
                'reason': row[6],
                'notes': row[7],
                'created_by': row[8],
                'created_at': row[9],
                'item_name': row[10]
            })
        
        conn.close()
        return jsonify({'success': True, 'movements': movements})
        
    except Exception as e:
        print(f"❌ Error getting inventory movements: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@inventory_bp.route('/movements', methods=['POST'])
@require_auth
def create_inventory_movement():
    """Record a new inventory movement and update item quantity"""
    try:
        user_id = get_user_id_from_session()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        data = request.get_json()
        
        # Required fields
        item_id = data.get('item_id', '').strip()
        movement_type = data.get('movement_type', '').strip()
        quantity = data.get('quantity', 0)
        reason = data.get('reason', '').strip()
        
        if not item_id or not movement_type or not quantity or not reason:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if item exists and belongs to user
        cursor.execute("SELECT quantity FROM inventory_items WHERE id = ? AND user_id = ?", (item_id, user_id))
        item_row = cursor.fetchone()
        if not item_row:
            return jsonify({'success': False, 'error': 'Item not found'}), 404
        
        current_quantity = item_row[0]
        
        # Calculate new quantity based on movement type
        if movement_type in ['in']:
            new_quantity = current_quantity + quantity
        elif movement_type in ['out', 'transfer', 'maintenance', 'disposal']:
            new_quantity = max(0, current_quantity - quantity)
        elif movement_type == 'adjustment':
            new_quantity = quantity  # Direct set
        else:
            return jsonify({'success': False, 'error': 'Invalid movement type'}), 400
        
        # Record movement
        movement_id = generate_id()
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO inventory_movements (
                id, item_id, movement_type, quantity, from_location, to_location,
                reason, notes, created_by, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            movement_id,
            item_id,
            movement_type,
            quantity,
            data.get('from_location', ''),
            data.get('to_location', ''),
            reason,
            data.get('notes', ''),
            user_id,
            now
        ))
        
        # Update item quantity
        cursor.execute("""
            UPDATE inventory_items SET quantity = ?, updated_at = ?
            WHERE id = ? AND user_id = ?
        """, (new_quantity, now, item_id, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Movement recorded successfully',
            'movement_id': movement_id,
            'new_quantity': new_quantity
        })
        
    except Exception as e:
        print(f"❌ Error creating inventory movement: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== INVENTORY REPORTS ====================

@inventory_bp.route('/reports/summary', methods=['GET'])
@require_auth
def get_inventory_summary():
    """Get comprehensive inventory summary report"""
    try:
        user_id = get_user_id_from_session()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total items and value
        cursor.execute("""
            SELECT 
                COUNT(*) as total_items,
                SUM(current_value * quantity) as total_value,
                SUM(CASE WHEN quantity <= 5 THEN 1 ELSE 0 END) as low_stock_count
            FROM inventory_items 
            WHERE user_id = ? AND is_active = 1
        """, (user_id,))
        
        summary_row = cursor.fetchone()
        total_items = summary_row[0] if summary_row else 0
        total_value = summary_row[1] if summary_row and summary_row[1] else 0
        low_stock_count = summary_row[2] if summary_row else 0
        
        # Get categories with item counts
        cursor.execute("""
            SELECT 
                c.id, c.name, c.icon, c.color,
                COUNT(i.id) as item_count
            FROM inventory_categories c
            LEFT JOIN inventory_items i ON c.id = i.category_id AND i.user_id = ? AND i.is_active = 1
            WHERE c.is_default = 1 OR c.user_id = ?
            GROUP BY c.id, c.name, c.icon, c.color
            HAVING item_count > 0
            ORDER BY item_count DESC
        """, (user_id, user_id))
        
        categories = []
        for row in cursor.fetchall():
            categories.append({
                'id': row[0],
                'name': row[1],
                'icon': row[2],
                'color': row[3],
                'item_count': row[4]
            })
        
        # Get low stock items
        cursor.execute("""
            SELECT name, quantity, unit
            FROM inventory_items 
            WHERE user_id = ? AND is_active = 1 AND quantity <= 5
            ORDER BY quantity ASC
            LIMIT 10
        """, (user_id,))
        
        low_stock = []
        for row in cursor.fetchall():
            low_stock.append({
                'name': row[0],
                'quantity': row[1],
                'unit': row[2]
            })
        
        # Get status breakdown
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM inventory_items 
            WHERE user_id = ? AND is_active = 1
            GROUP BY status
        """, (user_id,))
        
        status_breakdown = {}
        for row in cursor.fetchall():
            status_breakdown[row[0]] = row[1]
        
        # Get condition breakdown
        cursor.execute("""
            SELECT condition, COUNT(*) as count
            FROM inventory_items 
            WHERE user_id = ? AND is_active = 1
            GROUP BY condition
        """, (user_id,))
        
        condition_breakdown = {}
        for row in cursor.fetchall():
            condition_breakdown[row[0]] = row[1]
        
        conn.close()
        
        summary = {
            'total_items': total_items,
            'total_value': total_value,
            'low_stock_count': low_stock_count,
            'categories': categories,
            'low_stock': low_stock,
            'status_breakdown': status_breakdown,
            'condition_breakdown': condition_breakdown
        }
        
        return jsonify({'success': True, 'summary': summary})
        
    except Exception as e:
        print(f"❌ Error getting inventory summary: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== INVENTORY EXPORT ====================

@inventory_bp.route('/export', methods=['GET'])
@require_auth
def export_inventory():
    """Export inventory data as CSV"""
    try:
        user_id = get_user_id_from_session()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all items with category names
        cursor.execute("""
            SELECT 
                i.name, i.description, i.item_type, c.name as category_name,
                i.serial_number, i.barcode, i.quantity, i.unit,
                i.purchase_price, i.current_value, i.location, i.supplier,
                i.purchase_date, i.warranty_expiry, i.status, i.condition,
                i.notes, i.created_at
            FROM inventory_items i
            LEFT JOIN inventory_categories c ON i.category_id = c.id
            WHERE i.user_id = ? AND i.is_active = 1
            ORDER BY i.name
        """, (user_id,))
        
        items = cursor.fetchall()
        conn.close()
        
        # Create CSV content
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Name', 'Description', 'Type', 'Category', 'Serial Number', 'Barcode',
            'Quantity', 'Unit', 'Purchase Price', 'Current Value', 'Location',
            'Supplier', 'Purchase Date', 'Warranty Expiry', 'Status', 'Condition',
            'Notes', 'Created At'
        ])
        
        # Write data
        for item in items:
            writer.writerow(item)
        
        output.seek(0)
        
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=inventory_export.csv'}
        )
        
    except Exception as e:
        print(f"❌ Error exporting inventory: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== INVENTORY ITEMS ====================

