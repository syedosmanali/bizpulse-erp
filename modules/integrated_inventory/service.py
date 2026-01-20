"""
Integrated Inventory Service Layer
Business logic for Product Master, Inventory Control, and Purchase Entry
"""

from modules.shared.database import get_db_connection, generate_id
from modules.integrated_inventory.database import get_current_stock, update_stock_alerts
from datetime import datetime, timedelta
import json

class IntegratedInventoryService:
    """Service class for integrated inventory management"""
    
    def __init__(self):
        self.conn = None
    
    def get_db_connection(self):
        """Get database connection"""
        return get_db_connection()
    
    # ==================== PRODUCT MASTER SERVICES ====================
    
    def create_product_with_inventory(self, product_data, user_id):
        """Create a new product with inventory tracking setup"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Generate unique SKU if not provided
            sku = product_data.get('sku')
            if not sku:
                sku = f"SKU{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Check if SKU already exists
            cursor.execute("SELECT id FROM products WHERE sku = ? AND user_id = ?", (sku, user_id))
            if cursor.fetchone():
                return {'success': False, 'error': 'SKU already exists'}
            
            # Create product
            product_id = generate_id()
            now = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO products (
                    id, name, description, category, price, stock, unit, sku, 
                    barcode_data, image_url, is_active, user_id, created_at, updated_at,
                    min_stock, max_stock, hsn_code, gst_rate, mrp, purchase_price, selling_price
                ) VALUES (?, ?, ?, ?, ?, 0, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_id,
                product_data.get('name'),
                product_data.get('description', ''),
                product_data.get('category'),
                product_data.get('selling_price', 0),
                product_data.get('unit', 'piece'),
                sku,
                product_data.get('barcode', ''),
                product_data.get('image_url', ''),
                user_id,
                now,
                now,
                product_data.get('min_stock', 0),
                product_data.get('max_stock', 0),
                product_data.get('hsn_code', ''),
                product_data.get('gst_rate', 18),
                product_data.get('mrp', 0),
                product_data.get('purchase_price', 0),
                product_data.get('selling_price', 0)
            ))
            
            # Create initial stock transaction (opening balance)
            transaction_id = generate_id()
            cursor.execute("""
                INSERT INTO stock_transactions (
                    id, product_id, transaction_type, quantity, unit_cost, total_cost,
                    reference_type, reference_id, notes, created_by, business_owner_id, created_at
                ) VALUES (?, ?, 'opening', 0, ?, 0, 'product_creation', ?, 'Product created', ?, ?, ?)
            """, (
                transaction_id, product_id, product_data.get('purchase_price', 0),
                product_id, user_id, user_id, now
            ))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'product_id': product_id,
                'sku': sku,
                'message': 'Product created successfully'
            }
            
        except Exception as e:
            if conn:
                conn.rollback()
                conn.close()
            return {'success': False, 'error': str(e)}
    
    def update_product_pricing(self, product_id, pricing_data, user_id):
        """Update product pricing information"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Verify product belongs to user
            cursor.execute("SELECT id FROM products WHERE id = ? AND user_id = ?", (product_id, user_id))
            if not cursor.fetchone():
                return {'success': False, 'error': 'Product not found'}
            
            # Update pricing
            now = datetime.now().isoformat()
            cursor.execute("""
                UPDATE products SET
                    mrp = ?, purchase_price = ?, selling_price = ?, 
                    gst_rate = ?, updated_at = ?
                WHERE id = ? AND user_id = ?
            """, (
                pricing_data.get('mrp'),
                pricing_data.get('purchase_price'),
                pricing_data.get('selling_price'),
                pricing_data.get('gst_rate', 18),
                now,
                product_id,
                user_id
            ))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'message': 'Pricing updated successfully'}
            
        except Exception as e:
            if conn:
                conn.rollback()
                conn.close()
            return {'success': False, 'error': str(e)}
    
    def bulk_import_products(self, products_data, user_id):
        """Bulk import products from CSV/Excel data"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            imported_count = 0
            errors = []
            
            for i, product_data in enumerate(products_data):
                try:
                    # Generate SKU if not provided
                    sku = product_data.get('sku')
                    if not sku:
                        sku = f"SKU{datetime.now().strftime('%Y%m%d%H%M%S')}{i:03d}"
                    
                    # Check if SKU already exists
                    cursor.execute("SELECT id FROM products WHERE sku = ? AND user_id = ?", (sku, user_id))
                    if cursor.fetchone():
                        errors.append(f"Row {i+1}: SKU {sku} already exists")
                        continue
                    
                    # Create product
                    product_id = generate_id()
                    now = datetime.now().isoformat()
                    
                    cursor.execute("""
                        INSERT INTO products (
                            id, name, description, category, price, stock, unit, sku, 
                            barcode_data, is_active, user_id, created_at, updated_at,
                            min_stock, max_stock, hsn_code, gst_rate, mrp, purchase_price, selling_price
                        ) VALUES (?, ?, ?, ?, ?, 0, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        product_id,
                        product_data.get('name'),
                        product_data.get('description', ''),
                        product_data.get('category', 'other'),
                        product_data.get('selling_price', 0),
                        product_data.get('unit', 'piece'),
                        sku,
                        product_data.get('barcode', ''),
                        user_id,
                        now,
                        now,
                        product_data.get('min_stock', 0),
                        product_data.get('max_stock', 0),
                        product_data.get('hsn_code', ''),
                        product_data.get('gst_rate', 18),
                        product_data.get('mrp', 0),
                        product_data.get('purchase_price', 0),
                        product_data.get('selling_price', 0)
                    ))
                    
                    # Create initial stock transaction
                    transaction_id = generate_id()
                    cursor.execute("""
                        INSERT INTO stock_transactions (
                            id, product_id, transaction_type, quantity, unit_cost, total_cost,
                            reference_type, reference_id, notes, created_by, business_owner_id, created_at
                        ) VALUES (?, ?, 'opening', 0, ?, 0, 'bulk_import', ?, 'Bulk import', ?, ?, ?)
                    """, (
                        transaction_id, product_id, product_data.get('purchase_price', 0),
                        product_id, user_id, user_id, now
                    ))
                    
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {i+1}: {str(e)}")
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'imported_count': imported_count,
                'errors': errors,
                'message': f'Successfully imported {imported_count} products'
            }
            
        except Exception as e:
            if conn:
                conn.rollback()
                conn.close()
            return {'success': False, 'error': str(e)}
    
    # ==================== INVENTORY CONTROL SERVICES ====================
    
    def get_real_time_stock_summary(self, user_id):
        """Get real-time stock summary with status classification"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Get products with calculated stock levels
            cursor.execute("""
                SELECT 
                    p.id, p.name, p.category, p.sku, p.unit, p.min_stock, p.selling_price,
                    COALESCE(s.current_stock, 0) as current_stock,
                    COALESCE(s.last_updated, p.created_at) as last_updated,
                    CASE 
                        WHEN COALESCE(s.current_stock, 0) = 0 THEN 'out-of-stock'
                        WHEN COALESCE(s.current_stock, 0) <= p.min_stock AND p.min_stock > 0 THEN 'low-stock'
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
            stats = {
                'total_products': 0,
                'in_stock': 0,
                'low_stock': 0,
                'out_of_stock': 0,
                'total_value': 0
            }
            
            for row in cursor.fetchall():
                product = {
                    'id': row[0],
                    'name': row[1],
                    'category': row[2],
                    'sku': row[3],
                    'unit': row[4],
                    'min_stock': row[5],
                    'selling_price': row[6],
                    'current_stock': row[7],
                    'last_updated': row[8],
                    'status': row[9]
                }
                products.append(product)
                
                # Update statistics
                stats['total_products'] += 1
                stats['total_value'] += product['current_stock'] * product['selling_price']
                
                if product['status'] == 'in-stock':
                    stats['in_stock'] += 1
                elif product['status'] == 'low-stock':
                    stats['low_stock'] += 1
                elif product['status'] == 'out-of-stock':
                    stats['out_of_stock'] += 1
            
            conn.close()
            
            return {
                'success': True,
                'products': products,
                'stats': stats
            }
            
        except Exception as e:
            if conn:
                conn.close()
            return {'success': False, 'error': str(e)}
    
    def get_stock_ledger(self, product_id, user_id, limit=50):
        """Get detailed stock transaction history for a product"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Verify product belongs to user
            cursor.execute("SELECT name, unit FROM products WHERE id = ? AND user_id = ?", (product_id, user_id))
            product = cursor.fetchone()
            if not product:
                return {'success': False, 'error': 'Product not found'}
            
            # Get transaction history with running balance
            cursor.execute("""
                SELECT 
                    transaction_type, quantity, unit_cost, total_cost,
                    reference_type, supplier_name, customer_name, notes, created_at
                FROM stock_transactions
                WHERE product_id = ? AND business_owner_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (product_id, user_id, limit))
            
            transactions = []
            running_balance = get_current_stock(product_id, user_id)
            
            for row in cursor.fetchall():
                transaction = {
                    'type': row[0],
                    'quantity': row[1],
                    'unit_cost': row[2],
                    'total_cost': row[3],
                    'reference_type': row[4],
                    'supplier_name': row[5],
                    'customer_name': row[6],
                    'notes': row[7],
                    'created_at': row[8],
                    'balance_after': running_balance
                }
                
                # Calculate balance before this transaction
                if transaction['type'] == 'in':
                    running_balance -= transaction['quantity']
                else:
                    running_balance += transaction['quantity']
                
                transaction['balance_before'] = running_balance
                transactions.append(transaction)
            
            conn.close()
            
            return {
                'success': True,
                'product_name': product[0],
                'product_unit': product[1],
                'current_stock': get_current_stock(product_id, user_id),
                'transactions': transactions
            }
            
        except Exception as e:
            if conn:
                conn.close()
            return {'success': False, 'error': str(e)}
    
    # ==================== PURCHASE ENTRY SERVICES ====================
    
    def create_purchase_entry(self, purchase_data, user_id):
        """Create a complete purchase entry with multiple items"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            items = purchase_data.get('items', [])
            if not items:
                return {'success': False, 'error': 'No items provided'}
            
            # Create purchase entry record
            purchase_id = generate_id()
            now = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO purchase_entries (
                    id, supplier, total_amount, total_items, notes, 
                    created_by, business_owner_id, created_at
                ) VALUES (?, ?, 0, ?, ?, ?, ?, ?)
            """, (
                purchase_id,
                purchase_data.get('supplier', ''),
                len(items),
                purchase_data.get('notes', ''),
                user_id,
                user_id,
                now
            ))
            
            total_amount = 0
            updated_products = []
            
            # Process each item
            for item in items:
                product_id = item.get('product_id')
                quantity = item.get('quantity', 0)
                unit_cost = item.get('unit_cost', 0)
                
                if not product_id or quantity <= 0:
                    continue
                
                # Verify product exists and belongs to user
                cursor.execute("""
                    SELECT name, unit FROM products 
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
                    purchase_id, purchase_data.get('supplier', ''),
                    item.get('batch_number', ''), item.get('expiry_date'),
                    item.get('notes', ''), user_id, user_id, now
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
                    'unit_cost': unit_cost,
                    'new_stock': get_current_stock(product_id, user_id) + quantity
                })
            
            # Update purchase entry total
            cursor.execute("""
                UPDATE purchase_entries SET total_amount = ?
                WHERE id = ?
            """, (total_amount, purchase_id))
            
            conn.commit()
            conn.close()
            
            # Update stock alerts
            update_stock_alerts(user_id)
            
            return {
                'success': True,
                'purchase_id': purchase_id,
                'total_amount': total_amount,
                'updated_products': updated_products,
                'message': f'Purchase entry created successfully. {len(updated_products)} products updated.'
            }
            
        except Exception as e:
            if conn:
                conn.rollback()
                conn.close()
            return {'success': False, 'error': str(e)}
    
    def record_stock_adjustment(self, adjustment_data, user_id):
        """Record manual stock adjustments"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            product_id = adjustment_data.get('product_id')
            adjustment_type = adjustment_data.get('adjustment_type', 'correction')
            quantity_change = adjustment_data.get('quantity_change', 0)
            reason = adjustment_data.get('reason', '')
            notes = adjustment_data.get('notes', '')
            
            if not product_id or quantity_change == 0:
                return {'success': False, 'error': 'Product ID and quantity change are required'}
            
            # Verify product exists and belongs to user
            cursor.execute("SELECT name FROM products WHERE id = ? AND user_id = ?", (product_id, user_id))
            product = cursor.fetchone()
            if not product:
                return {'success': False, 'error': 'Product not found'}
            
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
                f"{adjustment_type}_{transaction_id}", f"{adjustment_type}: {reason} - {notes}".strip(' -'),
                user_id, user_id, now
            ))
            
            conn.commit()
            conn.close()
            
            # Update stock alerts
            update_stock_alerts(user_id)
            
            new_stock = get_current_stock(product_id, user_id)
            
            return {
                'success': True,
                'transaction_id': transaction_id,
                'new_stock': new_stock,
                'message': f'Stock adjustment recorded for {product[0]}'
            }
            
        except Exception as e:
            if conn:
                conn.rollback()
                conn.close()
            return {'success': False, 'error': str(e)}
    
    # ==================== REPORTING SERVICES ====================
    
    def get_reorder_report(self, user_id):
        """Get products that need reordering"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    p.id, p.name, p.category, p.sku, p.unit, p.min_stock, p.purchase_price,
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
                AND p.min_stock > 0
                ORDER BY 
                    CASE WHEN COALESCE(s.current_stock, 0) = 0 THEN 1 ELSE 2 END,
                    (p.min_stock - COALESCE(s.current_stock, 0)) DESC
            """, (user_id, user_id))
            
            reorder_items = []
            total_estimated_cost = 0
            
            for row in cursor.fetchall():
                shortage = max(0, row[8])  # Ensure shortage is not negative
                estimated_cost = shortage * row[6]  # shortage * purchase_price
                total_estimated_cost += estimated_cost
                
                reorder_items.append({
                    'id': row[0],
                    'name': row[1],
                    'category': row[2],
                    'sku': row[3],
                    'unit': row[4],
                    'min_stock': row[5],
                    'purchase_price': row[6],
                    'current_stock': row[7],
                    'shortage': shortage,
                    'estimated_cost': estimated_cost,
                    'priority': 'urgent' if row[7] == 0 else 'high' if shortage > 10 else 'medium'
                })
            
            conn.close()
            
            return {
                'success': True,
                'reorder_items': reorder_items,
                'total_items': len(reorder_items),
                'total_estimated_cost': total_estimated_cost
            }
            
        except Exception as e:
            if conn:
                conn.close()
            return {'success': False, 'error': str(e)}
    
    def get_stock_valuation_report(self, user_id):
        """Get stock valuation report"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    p.category,
                    COUNT(*) as product_count,
                    SUM(COALESCE(s.current_stock, 0)) as total_quantity,
                    SUM(COALESCE(s.current_stock, 0) * p.purchase_price) as purchase_value,
                    SUM(COALESCE(s.current_stock, 0) * p.selling_price) as selling_value
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
                GROUP BY p.category
                ORDER BY selling_value DESC
            """, (user_id, user_id))
            
            categories = []
            total_purchase_value = 0
            total_selling_value = 0
            total_products = 0
            total_quantity = 0
            
            for row in cursor.fetchall():
                category_data = {
                    'category': row[0],
                    'product_count': row[1],
                    'total_quantity': row[2],
                    'purchase_value': row[3],
                    'selling_value': row[4],
                    'potential_profit': row[4] - row[3]
                }
                categories.append(category_data)
                
                total_products += row[1]
                total_quantity += row[2]
                total_purchase_value += row[3]
                total_selling_value += row[4]
            
            conn.close()
            
            return {
                'success': True,
                'categories': categories,
                'summary': {
                    'total_products': total_products,
                    'total_quantity': total_quantity,
                    'total_purchase_value': total_purchase_value,
                    'total_selling_value': total_selling_value,
                    'potential_profit': total_selling_value - total_purchase_value
                }
            }
            
        except Exception as e:
            if conn:
                conn.close()
            return {'success': False, 'error': str(e)}

# Global service instance
integrated_inventory_service = IntegratedInventoryService()