"""
Production-Grade Invoice Service
Clean invoice management with proper business logic
"""

from datetime import datetime
from modules.shared.database import get_db_connection
import uuid
from typing import Dict, List, Optional, Tuple
from .billing_service import BillingService


class InvoiceService:
    """
    Professional invoice service built on top of billing service
    Invoice is the source of truth for all transactions
    """
    
    def __init__(self, db_path: str = None):
        # db_path parameter kept for backward compatibility but not used
        # Connection is now managed by get_db_connection()
        pass
        self.billing_service = BillingService(db_path)
    
    def _get_connection(self):
        """Get database connection - supports both SQLite and PostgreSQL"""
        return get_db_connection()
    
    def _generate_id(self) -> str:
        """Generate unique ID"""
        return str(uuid.uuid4())
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format (IST timezone safe)"""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def create_invoice(self, data: Dict) -> Tuple[bool, Dict]:
        """
        Create invoice - this is the main entry point for all transactions
        Invoice creation automatically creates bill, sales, and updates inventory
        Returns: (success, result_data)
        """
        # Use billing service to create the transaction
        success, result = self.billing_service.create_bill(data)
        
        if success:
            # Transform response to invoice format
            return True, {
                "success": True,
                "message": "Invoice created successfully",
                "invoice_id": result["bill_id"],
                "invoice_number": result["bill_number"],
                "total_amount": result["total_amount"],
                "items_count": result["items_count"],
                "created_at": result["created_at"]
            }
        else:
            return False, {
                "success": False,
                "message": result.get("error", "Invoice creation failed")
            }
    
    def get_invoices(self, filters: Dict = None) -> Tuple[bool, Dict]:
        """
        Get invoices with comprehensive filtering and pagination
        Returns: (success, result_data)
        """
        conn = self._get_connection()
        
        try:
            # Get query parameters with defaults
            page = filters.get('page', 1) if filters else 1
            limit = filters.get('limit', 20) if filters else 20
            offset = (page - 1) * limit
            
            # Base query with payment status calculation
            base_query = '''
                SELECT b.*, 
                       COALESCE(c.name, 'Walk-in Customer') as customer_name, 
                       c.phone as customer_phone,
                       c.email as customer_email,
                       DATE(b.created_at) as invoice_date,
                       TIME(b.created_at) as invoice_time,
                       COALESCE(SUM(p.amount), 0) as paid_amount,
                       CASE 
                           WHEN COALESCE(SUM(p.amount), 0) = 0 THEN 'unpaid'
                           WHEN COALESCE(SUM(p.amount), 0) < b.total_amount THEN 'partial'
                           WHEN COALESCE(SUM(p.amount), 0) >= b.total_amount THEN 'paid'
                           ELSE 'unpaid'
                       END as payment_status
                FROM bills b
                LEFT JOIN customers c ON b.customer_id = c.id
                LEFT JOIN payments p ON b.id = p.bill_id
            '''
            
            # Build WHERE conditions
            conditions = []
            params = []
            
            if filters:
                # Date filtering
                if filters.get('date_filter') == 'today':
                    conditions.append("DATE(b.created_at) = DATE('now', 'localtime')")
                elif filters.get('date_filter') == 'yesterday':
                    conditions.append("DATE(b.created_at) = DATE('now', 'localtime', '-1 day')")
                elif filters.get('date_filter') == 'week':
                    conditions.append("DATE(b.created_at) >= DATE('now', 'localtime', '-7 days')")
                elif filters.get('date_filter') == 'month':
                    conditions.append("DATE(b.created_at) >= DATE('now', 'localtime', '-30 days')")
                elif filters.get('date_filter') == 'custom' and filters.get('custom_date'):
                    conditions.append("DATE(b.created_at) = ?")
                    params.append(filters['custom_date'])
                
                # Date range filtering
                if filters.get('date_from'):
                    conditions.append('DATE(b.created_at) >= ?')
                    params.append(filters['date_from'])
                
                if filters.get('date_to'):
                    conditions.append('DATE(b.created_at) <= ?')
                    params.append(filters['date_to'])
            
            # Add WHERE clause if conditions exist
            if conditions:
                base_query += ' WHERE ' + ' AND '.join(conditions)
            
            # Group by bill to aggregate payments
            base_query += ' GROUP BY b.id'
            
            # Add payment status filter after GROUP BY
            if filters and filters.get('status') and filters['status'] != 'all':
                base_query += f''' HAVING payment_status = '{filters["status"]}' '''
            
            # Order by creation date (newest first)
            base_query += ' ORDER BY b.created_at DESC'
            
            # Get total count for pagination
            count_query = f'''
                SELECT COUNT(*) as total FROM (
                    {base_query}
                )
            '''
            total_count = conn.execute(count_query, params).fetchone()['total']
            
            # Add pagination
            base_query += ' LIMIT ? OFFSET ?'
            params.extend([limit, offset])
            
            # Execute main query
            bills = conn.execute(base_query, params).fetchall()
            
            # Format invoices
            invoices = []
            for bill in bills:
                invoice = dict(bill)
                
                # Rename fields for invoice context
                invoice["invoice_id"] = invoice["id"]
                invoice["invoice_number"] = invoice["bill_number"]
                
                # Format dates
                if invoice['invoice_date']:
                    try:
                        from datetime import datetime
                        date_obj = datetime.strptime(invoice['invoice_date'], '%Y-%m-%d')
                        invoice['formatted_date'] = date_obj.strftime('%d/%m/%Y')
                        invoice['display_date'] = date_obj.strftime('%d %b %Y')
                    except:
                        invoice['formatted_date'] = invoice['invoice_date']
                        invoice['display_date'] = invoice['invoice_date']
                
                # Calculate balance due
                paid_amount = invoice.get('paid_amount', 0) or 0
                total_amount = invoice.get('total_amount', 0) or 0
                invoice['balance_due'] = max(0, total_amount - paid_amount)
                
                # Add status badge color
                status_colors = {
                    'paid': 'success',
                    'partial': 'warning', 
                    'unpaid': 'danger'
                }
                invoice['status_color'] = status_colors.get(invoice['payment_status'], 'secondary')
                
                invoices.append(invoice)
            
            # Calculate pagination info
            total_pages = (total_count + limit - 1) // limit
            
            return True, {
                "success": True,
                "invoices": invoices,
                "pagination": {
                    "current_page": page,
                    "total_pages": total_pages,
                    "total_records": total_count,
                    "per_page": limit,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                }
            }
            
        except Exception as e:
            return False, {
                "success": False,
                "message": str(e)
            }
            
        finally:
            conn.close()
    
    def get_invoice_by_id(self, invoice_id: str, user_id: str = None) -> Tuple[bool, Dict]:
        """
        Get invoice details by ID
        Returns: (success, result_data)
        """
        conn = self._get_connection()
        
        try:
            # Build query with optional user filtering
            query = '''
                SELECT b.*, 
                       COALESCE(c.name, 'Walk-in Customer') as customer_name, 
                       c.phone as customer_phone,
                       c.email as customer_email,
                       c.address as customer_address
                FROM bills b
                LEFT JOIN customers c ON b.customer_id = c.id
                WHERE b.id = ?
            '''
            params = [invoice_id]
            
            # Add user filter if provided - handle NULL user_id in database
            if user_id:
                query += ' AND (b.user_id = ? OR b.user_id IS NULL OR b.business_owner_id = ?)'
                params.extend([user_id, user_id])
            
            # Get bill details
            bill = conn.execute(query, params).fetchone()
            
            if not bill:
                return False, {
                    "success": False,
                    "error": "Invoice not found"
                }
            
            # Get bill items
            items = conn.execute('''
                SELECT * FROM bill_items WHERE bill_id = ?
            ''', (invoice_id,)).fetchall()
            
            # Get payments
            payments = conn.execute('''
                SELECT * FROM payments WHERE bill_id = ?
            ''', (invoice_id,)).fetchall()
            
            # Transform bill to invoice format
            invoice = dict(bill)
            invoice["invoice_id"] = invoice["id"]
            invoice["invoice_number"] = invoice["bill_number"]
            
            return True, {
                "success": True,
                "invoice": invoice,
                "items": [dict(row) for row in items],
                "payments": [dict(row) for row in payments]
            }
            
        except Exception as e:
            return False, {
                "success": False,
                "error": str(e)
            }
            
        finally:
            conn.close()
    
    def delete_invoice(self, invoice_id: str) -> Tuple[bool, Dict]:
        """
        Delete invoice and revert all changes
        This deletes the bill, reverts inventory, and removes sales records
        Returns: (success, result_data)
        """
        success, result = self.billing_service.delete_bill(invoice_id)
        
        if success:
            return True, {
                "success": True,
                "message": result["message"],
                "reverted_items": result["reverted_items"]
            }
        else:
            return False, {
                "success": False,
                "message": result.get("error", "Invoice deletion failed")
            }
    
    def get_invoice_summary(self, filters: Dict = None) -> Tuple[bool, Dict]:
        """
        Get invoice summary statistics
        Returns: (success, result_data)
        """
        conn = self._get_connection()
        
        try:
            # Build date filter
            date_condition = "1=1"
            params = []
            
            if filters:
                if filters.get('date_from'):
                    date_condition += " AND DATE(created_at) >= ?"
                    params.append(filters['date_from'])
                
                if filters.get('date_to'):
                    date_condition += " AND DATE(created_at) <= ?"
                    params.append(filters['date_to'])
            
            # Get summary statistics
            summary = conn.execute(f'''
                SELECT 
                    COUNT(*) as total_invoices,
                    COALESCE(SUM(total_amount), 0) as total_value,
                    COALESCE(AVG(total_amount), 0) as avg_value,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_count,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_count
                FROM bills
                WHERE {date_condition}
            ''', params).fetchone()
            
            return True, {
                "success": True,
                "summary": dict(summary) if summary else {}
            }
            
        except Exception as e:
            return False, {
                "success": False,
                "message": str(e)
            }
            
        finally:
            conn.close()