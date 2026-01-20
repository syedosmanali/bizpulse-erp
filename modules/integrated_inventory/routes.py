"""
Integrated Inventory Management System Routes
Connects Product Master, Inventory Control, and Purchase Entry
"""

from flask import Blueprint, request, jsonify, session, render_template
from modules.shared.auth_decorators import require_auth
from modules.shared.database import get_db_connection, generate_id
from datetime import datetime
import json

integrated_inventory_bp = Blueprint('integrated_inventory', __name__, url_prefix='/inventory')

def get_user_id_from_session():
    """Get user_id from session for filtering data"""
    user_type = session.get('user_type')
    if user_type == 'employee':
        return session.get('client_id')
    else:
        return session.get('user_id')

# ==================== FRONTEND ROUTES ====================

@integrated_inventory_bp.route('/product-master')
@require_auth
def product_master_page():
    """Product Master UI - Setup Screen"""
    return render_template('product_master_redesign.html')

@integrated_inventory_bp.route('/control')
@require_auth
def inventory_control_page():
    """Inventory Control UI - Real-time Stock Management"""
    return render_template('inventory_control_redesign_new.html')

@integrated_inventory_bp.route('/purchase-entry')
@require_auth
def purchase_entry_page():
    """Purchase Entry UI - Stock In Management"""
    return render_template('purchase_entry_screen.html')

# ==================== PRODUCT MASTER API ====================

@integrated_inventory_bp.route('/api/products', methods=['GET'])
@require_auth
def get_products_for_inventory():
    """Get all products with inventory information"""
    try:
        user_id = get_user_id_from_session()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get products with current stock information
        cursor.execute("""
            SELECT 
                p.*,
                COALESCE(s.current_stock, p.stock) as current_stock,
                COALESCE(s.last_updated, p.updated_at) as stock_last_updated
            FROM products p
            LEFT JOIN (
                SELECT 
                    product_id,
                    SUM(CASE WHEN transaction_type = 'in' THEN quantity ELSE -quantity END) as current_stock,
                    MAX(created_at) as last_updated
                FROM stock_transactions 
                WHERE business_owner_id = ?
                GROUP BY product_id
            ) s ON p.id = s.product_id
            WHERE p.user_id = ? AND p.is_active = 1
            ORDER BY p.name
        """, (user_id, user_id))
        
        products = []
        for row in cursor.fetchall():
            products.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'category': row[3],
                'price': row[4],
                'stock': row[5],
                'unit': row[6],
                'sku': row[7],
                'barcode_data': row[8],
                'image_url': row[9],
                'is_active': row[10],
                'user_id': row[11],
                'created_at': row[12],
                'updated_at': row[13],
                'min_stock': row[14],
                'max_stock': row[15],
                'hsn_code': row[16],
                'gst_rate': row[17],
                'mrp': row[18],
                'purchase_price': row[19],
                'selling_price': row[20],
                'current_stock': row[21] or row[5],  # Use calculated stock or fallback to product stock
                'stock_last_updated': row[22] or row[13]
            })
        
        conn.close()
        return jsonify({'success': True, 'products': products})
        
    except Exception as e:
        print(f"❌ Error getting products for inventory: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@integrated_inventory_bp.route('/api/products', methods=['POST'])
@require_auth
def create_product():
    """Create new product with inventory tracking"""
    try:
        user_id = get_user_id_from_session()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        data = request.get_json()
        
        # Required fields
        name = data.get('name', '').strip()
        category = data.get('category', '').strip()
        gst_rate = data.get('gst_rate', 18)
        uom = data.get('uom', 'piece')
        mrp = data.get('mrp', 0)
        purchase_price = data.get('purchase_price', 0)
        selling_price = data.get('selling_price', 0)
        
        if not name or not category:
            return jsonify({'success': False, 'error': 'Name and category are required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Generate SKU if not provided
        sku = data.get('sku') or f"SKU{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Check if SKU already exists
        cursor.execute("SELECT id FROM products WHERE sku = ? AND user_id = ?", (sku, user_id))
        if cursor.fetchone():
            return jsonify({'success': False, 'error': 'SKU already exists'}), 400
        
        # Create product
        product_id = generate_id()
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO products (
                id, name, description, category, price, stock, unit, sku, 
                barcode_data, image_url, is_active, user_id, created_at, updated_at,
                min_stock, max_stock, hsn_code, gst_rate, mrp, purchase_price, selling_price
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product_id, name, data.get('description', ''), category, selling_price, 0, uom, sku,
            data.get('barcode', ''), data.get('image_url', ''), user_id, now, now,
            data.get('min_stock', 0), data.get('max_stock', 0), data.get('hsn_code', ''),
            gst_rate, mrp, purchase_price, selling_price
        ))
        
        # Initialize stock transaction record
        cursor.execute("""
            INSERT INTO stock_transactions (
                id, product_id, transaction_type, quantity, unit_cost, total_cost,
                reference_type, reference_id, notes, created_by, business_owner_id, created_at
            ) VALUES (?, ?, 'opening', 0, ?, 0, 'product_creation', ?, 'Initial product creation', ?, ?, ?)
        """, (
            generate_id(), product_id, purchase_price, product_id, user_id, user_id, now
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Product created successfully',
            'product_id': product_id,
            'sku': sku
        })
        
    except Exception as e:
        print(f"❌ Error creating product: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== INVENTORY CONTROL API ====================

@integrated_inventory_bp.route('/api/stock-summary', methods=['GET'])
@require_auth
def get_stock_summary():
    """Get real-time stock summary for inventory control"""
    try:
        user_id = get_user_id_from_session()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get stock summary with status classification
        cursor.execute("""
            SELECT 
                p.id,
                p.name,
                p.category,
                p.sku,
                p.unit,
                p.min_stock,
                COALESCE(s.current_stock, 0) as current_stock,
                COALESCE(s.last_updated, p.created_at) as last_updated,
                CASE 
                    WHEN COALESCE(s.current_stock, 0) = 0 THEN 'out-of-stock'
                    WHEN COALESCE(s.current_stock, 0) <= p.min_stock THEN 'low-stock'
                    ELSE 'in-stock'
                END as status
            FROM products p
            LEFT JOIN (
                SELECT 
                    product_id,
                    SUM(CASE WHEN transaction_type = 'in' THEN quantity ELSE -quantity END) as current_stock,
                    MAX(created_at) as last_updated
                FROM stock_transactions 
                WHERE business_owner_id = ?
                GROUP BY product_id
            ) s ON p.id = s.product_id
            WHERE p.user_id = ? AND p.is_active = 1
            ORDER BY 
                CASE 
                    WHEN COALESCE(s.current_stock, 0) = 0 THEN 1
                    WHEN COALESCE(s.current_stock, 0) <= p.min_stock THEN 2
                    ELSE 3
                END,
                p.name
        """, (user_id, user_id))
        
        products = []
        total_products = 0
        low_stock_count = 0
        out_of_stock_count = 0
        total_value = 0
        
        for row in cursor.fetchall():
            product = {
                'id': row[0],
                'name': row[1],
                'category': row[2],
                'sku': row[3],
                'unit': row[4],
                'min_stock': row[5],
                'current_stock': row[6],
                'last_updated': row[7],
                'status': row[8]
            }
            products.append(product)
            
            total_products += 1
            if product['status'] == 'low-stock':
                low_stock_count += 1
            elif product['status'] == 'out-of-stock':
                out_of_stock_count += 1
        
        # Calculate total inventory value
        cursor.execute("""
            SELECT SUM(
                COALESCE(s.current_stock, 0) * p.purchase_price
            ) as total_value
            FROM products p
            LEFT JOIN (
                SELECT 
                    product_id,
                    SUM(CASE WHEN transaction_type = 'in' THEN quantity ELSE -quantity END) as current_stock
                FROM stock_transactions 
                WHERE business_owner_id = ?
                GROUP BY product_id
            ) s ON p.id = s.product_id
            WHERE p.user_id = ? AND p.is_active = 1
        """, (user_id, user_id))
        
        total_value_row = cursor.fetchone()
        total_value = total_value_row[0] if total_value_row and total_value_row[0] else 0
        
        conn.close()
        
        return jsonify({
            'success': True,
            'products': products,
            'summary': {
                'total_products': total_products,
                'low_stock_count': low_stock_count,
                'out_of_stock_count': out_of_stock_count,
                'total_value': total_value
            }
        })
        
    except Exception as e:
        print(f"❌ Error getting stock summary: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@integrated_inventory_bp.route('/api/stock-ledger/<product_id>', methods=['GET'])
@require_auth
def get_stock_ledger(product_id):
    """Get stock transaction history for a specific product"""
    try:
        user_id = get_user_id_from_session()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify product belongs to user
        cursor.execute("SELECT name FROM products WHERE id = ? AND user_id = ?", (product_id, user_id))
        product = cursor.fetchone()
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        # Get transaction history
        cursor.execute("""
            SELECT 
                transaction_type,
                quantity,
                unit_cost,
                total_cost,
                reference_type,
                notes,
                created_at
            FROM stock_transactions
            WHERE product_id = ? AND business_owner_id = ?
            ORDER BY created_at DESC
            LIMIT 50
        """, (product_id, user_id))
        
        transactions = []
        for row in cursor.fetchall():
            transactions.append({
                'type': row[0],
                'quantity': row[1],
                'unit_cost': row[2],
                'total_cost': row[3],
                'reference_type': row[4],
                'notes': row[5],
                'created_at': row[6]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'product_name': product[0],
            'transactions': transactions
        })
        
    except Exception as e:
        print(f"❌ Error getting stock ledger: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== PURCHASE ENTRY API ====================

@integrated_inventory_bp.route('/api/purchase-entry', methods=['POST'])
@require_auth
def create_purchase_entry():
    """Create purchase entry and update stock levels"""
    try:
        user_id = get_user_id_from_session()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        data = request.get_json()
        items = data.get('items', [])
        supplier = data.get('supplier', '')
        notes = data.get('notes', '')
        
        if not items:
            return jsonify({'success': False, 'error': 'No items provided'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create purchase entry record
        purchase_id = generate_id()
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO purchase_entries (
                id, supplier, total_amount, total_items, notes, 
                created_by, business_owner_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            purchase_id, supplier, 0, len(items), notes, user_id, user_id, now
        ))
        
        total_amount = 0
        updated_products = []
        
        # Process each item
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 0)
            unit_cost = item.get('unit_cost', 0)
            batch_number = item.get('batch_number', '')
            expiry_date = item.get('expiry_date')
            item_notes = item.get('notes', '')
            
            if not product_id or quantity <= 0:
                continue
            
            # Verify product exists and belongs to user
            cursor.execute("""
                SELECT name, unit, purchase_price FROM products 
                WHERE id = ? AND user_id = ?
            """, (product_id, user_id))
            
            product = cursor.fetchone()
            if not product:
                continue
            
            item_total = quantity * unit_cost
            total_amount += item_total
            
            # Create stock transaction
            transaction_id = generate_id()
            cursor.execute("""
                INSERT INTO stock_transactions (
                    id, product_id, transaction_type, quantity, unit_cost, total_cost,
                    reference_type, reference_id, supplier_name, batch_number, expiry_date,
                    notes, created_by, business_owner_id, created_at
                ) VALUES (?, ?, 'in', ?, ?, ?, 'purchase', ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transaction_id, product_id, quantity, unit_cost, item_total,
                purchase_id, supplier, batch_number, expiry_date,
                item_notes, user_id, user_id, now
            ))
            
            # Update product's last purchase price
            cursor.execute("""
                UPDATE products SET purchase_price = ?, updated_at = ?
                WHERE id = ? AND user_id = ?
            """, (unit_cost, now, product_id, user_id))
            
            updated_products.append({
                'product_id': product_id,
                'name': product[0],
                'quantity_added': quantity,
                'unit_cost': unit_cost
            })
        
        # Update purchase entry total
        cursor.execute("""
            UPDATE purchase_entries SET total_amount = ?
            WHERE id = ?
        """, (total_amount, purchase_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Purchase entry created successfully. {len(updated_products)} products updated.',
            'purchase_id': purchase_id,
            'total_amount': total_amount,
            'updated_products': updated_products
        })
        
    except Exception as e:
        print(f"❌ Error creating purchase entry: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@integrated_inventory_bp.route('/api/product-search', methods=['GET'])
@require_auth
def search_products():
    """Search products for purchase entry"""
    try:
        user_id = get_user_id_from_session()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        query = request.args.get('q', '').strip()
        if len(query) < 2:
            return jsonify({'success': True, 'products': []})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Search by name, SKU, or barcode
        cursor.execute("""
            SELECT 
                p.id, p.name, p.sku, p.unit, p.purchase_price,
                COALESCE(s.current_stock, 0) as current_stock
            FROM products p
            LEFT JOIN (
                SELECT 
                    product_id,
                    SUM(CASE WHEN transaction_type = 'in' THEN quantity ELSE -quantity END) as current_stock
                FROM stock_transactions 
                WHERE business_owner_id = ?
                GROUP BY product_id
            ) s ON p.id = s.product_id
            WHERE p.user_id = ? AND p.is_active = 1
            AND (p.name LIKE ? OR p.sku LIKE ? OR p.barcode_data LIKE ?)
            ORDER BY p.name
            LIMIT 10
        """, (user_id, user_id, f'%{query}%', f'%{query}%', f'%{query}%'))
        
        products = []
        for row in cursor.fetchall():
            products.append({
                'id': row[0],
                'name': row[1],
                'sku': row[2],
                'unit': row[3],
                'last_purchase_price': row[4],
                'current_stock': row[5]
            })
        
        conn.close()
        return jsonify({'success': True, 'products': products})
        
    except Exception as e:
        print(f"❌ Error searching products: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== STOCK ADJUSTMENT API ====================

@integrated_inventory_bp.route('/api/stock-adjustment', methods=['POST'])
@require_auth
def stock_adjustment():
    """Manual stock adjustment for damage, theft, or counting corrections"""
    try:
        user_id = get_user_id_from_session()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        data = request.get_json()
        product_id = data.get('product_id')
        adjustment_type = data.get('adjustment_type', 'correction')  # correction, damage, theft, found
        quantity_change = data.get('quantity_change', 0)  # positive or negative
        reason = data.get('reason', '')
        notes = data.get('notes', '')
        
        if not product_id or quantity_change == 0:
            return jsonify({'success': False, 'error': 'Product ID and quantity change are required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify product exists and belongs to user
        cursor.execute("SELECT name FROM products WHERE id = ? AND user_id = ?", (product_id, user_id))
        product = cursor.fetchone()
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        # Create adjustment transaction
        transaction_id = generate_id()
        now = datetime.now().isoformat()
        transaction_type = 'in' if quantity_change > 0 else 'out'
        abs_quantity = abs(quantity_change)
        
        cursor.execute("""
            INSERT INTO stock_transactions (
                id, product_id, transaction_type, quantity, unit_cost, total_cost,
                reference_type, reference_id, notes, created_by, business_owner_id, created_at
            ) VALUES (?, ?, ?, ?, 0, 0, 'adjustment', ?, ?, ?, ?, ?)
        """, (
            transaction_id, product_id, transaction_type, abs_quantity,
            f"{adjustment_type}: {reason}", f"{reason} - {notes}".strip(' -'),
            user_id, user_id, now
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Stock adjustment recorded for {product[0]}',
            'transaction_id': transaction_id
        })
        
    except Exception as e:
        print(f"❌ Error recording stock adjustment: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== REPORTS API ====================

@integrated_inventory_bp.route('/api/reorder-report', methods=['GET'])
@require_auth
def get_reorder_report():
    """Get products that need reordering (below minimum stock level)"""
    try:
        user_id = get_user_id_from_session()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                p.id, p.name, p.category, p.sku, p.unit, p.min_stock,
                COALESCE(s.current_stock, 0) as current_stock,
                (p.min_stock - COALESCE(s.current_stock, 0)) as shortage
            FROM products p
            LEFT JOIN (
                SELECT 
                    product_id,
                    SUM(CASE WHEN transaction_type = 'in' THEN quantity ELSE -quantity END) as current_stock
                FROM stock_transactions 
                WHERE business_owner_id = ?
                GROUP BY product_id
            ) s ON p.id = s.product_id
            WHERE p.user_id = ? AND p.is_active = 1
            AND COALESCE(s.current_stock, 0) <= p.min_stock
            ORDER BY 
                CASE WHEN COALESCE(s.current_stock, 0) = 0 THEN 1 ELSE 2 END,
                (p.min_stock - COALESCE(s.current_stock, 0)) DESC
        """, (user_id, user_id))
        
        reorder_items = []
        for row in cursor.fetchall():
            reorder_items.append({
                'id': row[0],
                'name': row[1],
                'category': row[2],
                'sku': row[3],
                'unit': row[4],
                'min_stock': row[5],
                'current_stock': row[6],
                'shortage': row[7],
                'priority': 'urgent' if row[6] == 0 else 'high' if row[7] > 10 else 'medium'
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'reorder_items': reorder_items,
            'total_items': len(reorder_items)
        })
        
    except Exception as e:
        print(f"❌ Error getting reorder report: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
