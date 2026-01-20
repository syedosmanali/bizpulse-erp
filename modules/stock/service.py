"""
Stock Management Service
Handles all stock transactions and movements
"""

from modules.shared.database import get_db_connection, generate_id
from modules.stock.database import get_current_stock, update_current_stock
from datetime import datetime

class StockService:
    
    def create_stock_transaction(self, product_id, transaction_type, quantity, reference_type=None, 
                               reference_id=None, notes=None, created_by=None, business_owner_id=None):
        """
        Create a stock transaction
        
        Args:
            product_id: Product ID
            transaction_type: 'IN', 'OUT', 'ADJUSTMENT'
            quantity: Positive for IN, Negative for OUT
            reference_type: 'sale', 'purchase', 'adjustment', 'opening'
            reference_id: bill_id, purchase_id, etc.
            notes: Additional notes
            created_by: User who created the transaction
            business_owner_id: For multi-tenant isolation
        """
        conn = get_db_connection()
        
        try:
            # Validate stock for OUT transactions
            if transaction_type == 'OUT' and quantity > 0:
                current_stock = get_current_stock(product_id, business_owner_id)
                if current_stock < quantity:
                    return {
                        'success': False,
                        'error': f'Insufficient stock. Available: {current_stock}, Requested: {quantity}'
                    }
                # Make quantity negative for OUT transactions
                quantity = -quantity
            
            # Create transaction record
            transaction_id = generate_id()
            conn.execute("""
                INSERT INTO stock_transactions (
                    id, product_id, transaction_type, quantity, reference_type, 
                    reference_id, notes, created_by, business_owner_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transaction_id,
                product_id,
                transaction_type,
                quantity,
                reference_type,
                reference_id,
                notes,
                created_by,
                business_owner_id,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            
            # Update current stock
            new_stock = update_current_stock(product_id, business_owner_id)
            
            conn.commit()
            
            return {
                'success': True,
                'transaction_id': transaction_id,
                'new_stock': new_stock,
                'message': f'Stock transaction created successfully'
            }
            
        except Exception as e:
            conn.rollback()
            return {
                'success': False,
                'error': f'Failed to create stock transaction: {str(e)}'
            }
        finally:
            conn.close()
    
    def add_stock_purchase(self, product_id, quantity, unit_cost=0, supplier_name=None, 
                          notes=None, created_by=None, business_owner_id=None):
        """Add stock from purchase"""
        
        # Get product name for notes
        conn = get_db_connection()
        product = conn.execute("SELECT name FROM products WHERE id = ?", (product_id,)).fetchone()
        product_name = product[0] if product else "Unknown Product"
        conn.close()
        
        purchase_notes = f"Purchase: {product_name}"
        if supplier_name:
            purchase_notes += f" from {supplier_name}"
        if unit_cost > 0:
            purchase_notes += f" @ ₹{unit_cost} per unit"
        if notes:
            purchase_notes += f" - {notes}"
        
        return self.create_stock_transaction(
            product_id=product_id,
            transaction_type='IN',
            quantity=quantity,
            reference_type='purchase',
            notes=purchase_notes,
            created_by=created_by,
            business_owner_id=business_owner_id
        )
    
    def adjust_stock(self, product_id, adjustment_type, new_quantity, reason=None, 
                    notes=None, created_by=None, business_owner_id=None):
        """
        Adjust stock to a specific quantity
        
        Args:
            adjustment_type: 'damage', 'expired', 'correction', 'found'
            new_quantity: Target quantity
        """
        current_stock = get_current_stock(product_id, business_owner_id)
        difference = new_quantity - current_stock
        
        if difference == 0:
            return {
                'success': True,
                'message': 'No adjustment needed - stock is already correct',
                'current_stock': current_stock
            }
        
        # Get product name for notes
        conn = get_db_connection()
        product = conn.execute("SELECT name FROM products WHERE id = ?", (product_id,)).fetchone()
        product_name = product[0] if product else "Unknown Product"
        conn.close()
        
        # Create adjustment record
        conn = get_db_connection()
        adjustment_id = generate_id()
        conn.execute("""
            INSERT INTO stock_adjustments (
                id, product_id, adjustment_type, old_quantity, new_quantity, 
                difference, reason, notes, created_by, business_owner_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            adjustment_id,
            product_id,
            adjustment_type,
            current_stock,
            new_quantity,
            difference,
            reason,
            notes,
            created_by,
            business_owner_id,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        conn.commit()
        conn.close()
        
        # Create stock transaction
        adjustment_notes = f"Stock adjustment: {product_name} - {adjustment_type}"
        if reason:
            adjustment_notes += f" ({reason})"
        if notes:
            adjustment_notes += f" - {notes}"
        
        transaction_type = 'IN' if difference > 0 else 'OUT'
        quantity = abs(difference)
        
        return self.create_stock_transaction(
            product_id=product_id,
            transaction_type=transaction_type,
            quantity=quantity,
            reference_type='adjustment',
            reference_id=adjustment_id,
            notes=adjustment_notes,
            created_by=created_by,
            business_owner_id=business_owner_id
        )
    
    def create_sale_transaction(self, product_id, quantity, bill_id, bill_number, 
                              created_by=None, business_owner_id=None):
        """Create stock OUT transaction for sale"""
        
        # Get product name for notes
        conn = get_db_connection()
        product = conn.execute("SELECT name FROM products WHERE id = ?", (product_id,)).fetchone()
        product_name = product[0] if product else "Unknown Product"
        conn.close()
        
        sale_notes = f"Sale: {product_name} - Bill #{bill_number}"
        
        return self.create_stock_transaction(
            product_id=product_id,
            transaction_type='OUT',
            quantity=quantity,
            reference_type='sale',
            reference_id=bill_id,
            notes=sale_notes,
            created_by=created_by,
            business_owner_id=business_owner_id
        )
    
    def get_stock_history(self, product_id=None, business_owner_id=None, limit=50):
        """Get stock transaction history"""
        conn = get_db_connection()
        
        if product_id:
            # Get history for specific product
            query = """
                SELECT st.*, p.name as product_name
                FROM stock_transactions st
                LEFT JOIN products p ON st.product_id = p.id
                WHERE st.product_id = ? AND st.business_owner_id = ? AND st.is_active = 1
                ORDER BY st.created_at DESC
                LIMIT ?
            """
            params = [product_id, business_owner_id, limit]
        else:
            # Get history for all products
            query = """
                SELECT st.*, p.name as product_name
                FROM stock_transactions st
                LEFT JOIN products p ON st.product_id = p.id
                WHERE st.business_owner_id = ? AND st.is_active = 1
                ORDER BY st.created_at DESC
                LIMIT ?
            """
            params = [business_owner_id, limit]
        
        transactions = conn.execute(query, params).fetchall()
        conn.close()
        
        return [dict(row) for row in transactions]
    
    def get_low_stock_products(self, business_owner_id, threshold=None):
        """Get products with low stock"""
        conn = get_db_connection()
        
        query = """
            SELECT p.id, p.name, p.min_stock, cs.current_quantity,
                   CASE 
                       WHEN cs.current_quantity = 0 THEN 'out_of_stock'
                       WHEN cs.current_quantity <= p.min_stock THEN 'low_stock'
                       ELSE 'normal'
                   END as stock_status
            FROM products p
            LEFT JOIN current_stock cs ON p.id = cs.product_id
            WHERE p.user_id = ? AND p.is_active = 1
            AND (cs.current_quantity = 0 OR cs.current_quantity <= p.min_stock)
            ORDER BY cs.current_quantity ASC, p.name ASC
        """
        
        products = conn.execute(query, (business_owner_id,)).fetchall()
        conn.close()
        
        return [dict(row) for row in products]
    
    def get_stock_summary(self, business_owner_id):
        """Get overall stock summary"""
        conn = get_db_connection()
        
        # Get total products and stock value
        summary = conn.execute("""
            SELECT 
                COUNT(DISTINCT p.id) as total_products,
                COALESCE(SUM(cs.current_quantity), 0) as total_stock_units,
                COALESCE(SUM(cs.current_quantity * p.cost), 0) as total_stock_value,
                COUNT(CASE WHEN cs.current_quantity = 0 THEN 1 END) as out_of_stock_count,
                COUNT(CASE WHEN cs.current_quantity <= p.min_stock AND cs.current_quantity > 0 THEN 1 END) as low_stock_count
            FROM products p
            LEFT JOIN current_stock cs ON p.id = cs.product_id
            WHERE p.user_id = ? AND p.is_active = 1
        """, (business_owner_id,)).fetchone()
        
        conn.close()
        
        return dict(summary) if summary else {
            'total_products': 0,
            'total_stock_units': 0,
            'total_stock_value': 0,
            'out_of_stock_count': 0,
            'low_stock_count': 0
        }