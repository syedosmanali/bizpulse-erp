"""
Stock Management Routes
Simple interface for shop owners to manage stock
"""

from flask import Blueprint, request, jsonify, session, render_template
from modules.shared.auth_decorators import require_auth
from modules.stock.service import StockService
from modules.stock.database import get_current_stock, init_stock_tables, migrate_existing_stock_data
from modules.shared.database import get_db_connection

stock_bp = Blueprint('stock', __name__, url_prefix='/api/stock')

def get_user_id_from_session():
    """Get user_id from session"""
    user_type = session.get('user_type')
    if user_type == 'employee':
        return session.get('client_id')
    else:
        return session.get('user_id')

# Initialize stock service
stock_service = StockService()

# ==================== STOCK INFORMATION ====================

@stock_bp.route('/current/<product_id>', methods=['GET'])
@require_auth
def get_product_current_stock(product_id):
    """Get current stock for a specific product"""
    try:
        user_id = get_user_id_from_session()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        current_stock = get_current_stock(product_id, user_id)
        
        return jsonify({
            'success': True,
            'product_id': product_id,
            'current_stock': current_stock
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@stock_bp.route('/summary', methods=['GET'])
@require_auth
def get_stock_summary():
    """Get overall stock summary"""
    try:
        user_id = get_user_id_from_session()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        summary = stock_service.get_stock_summary(user_id)
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@stock_bp.route('/low-stock', methods=['GET'])
@require_auth
def get_low_stock_products():
    """Get products with low or zero stock"""
    try:
        user_id = get_user_id_from_session()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        low_stock_products = stock_service.get_low_stock_products(user_id)
        
        return jsonify({
            'success': True,
            'products': low_stock_products
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== STOCK TRANSACTIONS ====================

@stock_bp.route('/history', methods=['GET'])
@require_auth
def get_stock_history():
    """Get stock transaction history"""
    try:
        user_id = get_user_id_from_session()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        product_id = request.args.get('product_id')
        limit = request.args.get('limit', 50, type=int)
        
        history = stock_service.get_stock_history(product_id, user_id, limit)
        
        return jsonify({
            'success': True,
            'transactions': history
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== ADD STOCK (PURCHASE) ====================

@stock_bp.route('/add-purchase', methods=['POST'])
@require_auth
def add_stock_purchase():
    """Add stock from purchase - SIMPLE INTERFACE"""
    try:
        user_id = get_user_id_from_session()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 0)
        unit_cost = data.get('unit_cost', 0)
        supplier_name = data.get('supplier_name', '').strip()
        notes = data.get('notes', '').strip()
        
        # Validation
        if not product_id:
            return jsonify({'success': False, 'error': 'Product ID is required'}), 400
        
        if quantity <= 0:
            return jsonify({'success': False, 'error': 'Quantity must be greater than 0'}), 400
        
        # Add stock
        result = stock_service.add_stock_purchase(
            product_id=product_id,
            quantity=quantity,
            unit_cost=unit_cost,
            supplier_name=supplier_name,
            notes=notes,
            created_by=user_id,
            business_owner_id=user_id
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': f'Added {quantity} units to stock',
                'new_stock': result['new_stock'],
                'transaction_id': result['transaction_id']
            })
        else:
            return jsonify({'success': False, 'error': result['error']}), 400
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== STOCK ADJUSTMENT ====================

@stock_bp.route('/adjust', methods=['POST'])
@require_auth
def adjust_stock():
    """Adjust stock - ONE BUTTON SOLUTION"""
    try:
        user_id = get_user_id_from_session()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        data = request.get_json()
        product_id = data.get('product_id')
        new_quantity = data.get('new_quantity', 0)
        adjustment_type = data.get('adjustment_type', 'correction')  # damage, expired, correction, found
        reason = data.get('reason', '').strip()
        notes = data.get('notes', '').strip()
        
        # Validation
        if not product_id:
            return jsonify({'success': False, 'error': 'Product ID is required'}), 400
        
        if new_quantity < 0:
            return jsonify({'success': False, 'error': 'Stock quantity cannot be negative'}), 400
        
        # Adjust stock
        result = stock_service.adjust_stock(
            product_id=product_id,
            adjustment_type=adjustment_type,
            new_quantity=new_quantity,
            reason=reason,
            notes=notes,
            created_by=user_id,
            business_owner_id=user_id
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'new_stock': result.get('new_stock', new_quantity)
            })
        else:
            return jsonify({'success': False, 'error': result['error']}), 400
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== BULK OPERATIONS ====================

@stock_bp.route('/bulk-adjust', methods=['POST'])
@require_auth
def bulk_adjust_stock():
    """Bulk stock adjustment for multiple products"""
    try:
        user_id = get_user_id_from_session()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        data = request.get_json()
        adjustments = data.get('adjustments', [])
        
        if not adjustments:
            return jsonify({'success': False, 'error': 'No adjustments provided'}), 400
        
        results = []
        success_count = 0
        
        for adjustment in adjustments:
            product_id = adjustment.get('product_id')
            new_quantity = adjustment.get('new_quantity', 0)
            adjustment_type = adjustment.get('adjustment_type', 'correction')
            reason = adjustment.get('reason', 'Bulk adjustment')
            
            if product_id and new_quantity >= 0:
                result = stock_service.adjust_stock(
                    product_id=product_id,
                    adjustment_type=adjustment_type,
                    new_quantity=new_quantity,
                    reason=reason,
                    created_by=user_id,
                    business_owner_id=user_id
                )
                
                if result['success']:
                    success_count += 1
                
                results.append({
                    'product_id': product_id,
                    'success': result['success'],
                    'message': result.get('message', result.get('error', ''))
                })
        
        return jsonify({
            'success': True,
            'message': f'Processed {len(adjustments)} adjustments, {success_count} successful',
            'results': results
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== MIGRATION & SETUP ====================

@stock_bp.route('/migrate', methods=['POST'])
@require_auth
def migrate_stock_data():
    """Migrate existing stock data to new system - ONE TIME ONLY"""
    try:
        user_id = get_user_id_from_session()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        # Check if migration already done
        conn = get_db_connection()
        existing_transactions = conn.execute("""
            SELECT COUNT(*) as count FROM stock_transactions 
            WHERE reference_type = 'opening' AND business_owner_id = ?
        """, (user_id,)).fetchone()
        conn.close()
        
        if existing_transactions and existing_transactions[0] > 0:
            return jsonify({
                'success': False,
                'error': 'Migration already completed for this user'
            }), 400
        
        # Initialize tables
        init_stock_tables()
        
        # Migrate data
        migrated_count = migrate_existing_stock_data()
        
        return jsonify({
            'success': True,
            'message': f'Migration completed successfully! {migrated_count} products migrated.',
            'migrated_count': migrated_count
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@stock_bp.route('/init', methods=['POST'])
@require_auth
def initialize_stock_system():
    """Initialize stock system tables"""
    try:
        init_stock_tables()
        
        return jsonify({
            'success': True,
            'message': 'Stock system initialized successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== FRONTEND ROUTES ====================

@stock_bp.route('/manage', methods=['GET'])
@require_auth
def stock_management_page():
    """Stock management frontend page"""
    from flask import render_template
    return render_template('stock_management.html')