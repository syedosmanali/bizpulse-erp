"""
Retail service
COPIED AS-IS from app.py
"""

from modules.shared.database import get_db_connection
from datetime import datetime, timedelta

class RetailService:
    
    def get_dashboard_stats(self, user_id=None):
        """Get comprehensive dashboard statistics with real sales/orders data but zero revenue/profit"""
        print("🔍 [DASHBOARD] Starting get_dashboard_stats (real sales/orders, zero revenue mode)")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        from modules.shared.database import get_db_type
        db_type = get_db_type()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Build user filter condition - STRICT ISOLATION
        if db_type == 'postgresql':
            user_filter = ""
            user_params = []
            if user_id:
                user_filter = "AND business_owner_id = %s"
                user_params = [user_id]
        else:
            user_filter = ""
            user_params = []
            if user_id:
                user_filter = "AND business_owner_id = ?"
                user_params = [user_id]
        
        # Today's Sales (ALL bills including credit/partial) - SHOW REAL DATA
        if db_type == 'postgresql':
            today_sales_data = cursor.execute(f'''
                SELECT 
                    COALESCE(SUM(total_amount), 0) as total_sales,
                    COUNT(*) as transactions
                FROM bills 
                WHERE CAST(created_at AS DATE) = %s {user_filter}
            ''', [today] + user_params).fetchone()
        else:
            today_sales_data = cursor.execute(f'''
                SELECT 
                    COALESCE(SUM(total_amount), 0) as total_sales,
                    COUNT(*) as transactions
                FROM bills 
                WHERE DATE(created_at) = ? {user_filter}
            ''', [today] + user_params).fetchone()
        
        today_sales = float(today_sales_data['total_sales'] or 0)
        today_orders = int(today_sales_data['transactions'] or 0)
        
        # BUT keep revenue and profit at zero (no cash payments)
        today_revenue = 0.0
        today_profit = 0.0
        
        # Get recent sales for display
        if db_type == 'postgresql':
            recent_sales_query = '''
                SELECT 
                    bill_number,
                    total_amount,
                    customer_name,
                    created_at
                FROM bills 
                WHERE CAST(created_at AS DATE) = %s {user_filter}
                ORDER BY created_at DESC
                LIMIT 5
            '''
        else:
            recent_sales_query = '''
                SELECT 
                    bill_number,
                    total_amount,
                    customer_name,
                    created_at
                FROM bills 
                WHERE DATE(created_at) = ? {user_filter}
                ORDER BY created_at DESC
                LIMIT 5
            '''
        
        recent_sales_raw = cursor.execute(recent_sales_query.format(user_filter=user_filter), [today] + user_params).fetchall()
        
        recent_sales = []
        for sale in recent_sales_raw:
            # Handle datetime conversion safely
            created_at = sale['created_at']
            if isinstance(created_at, str):
                time_str = datetime.fromisoformat(created_at).strftime('%H:%M')
            else:
                # If it's already a datetime object or timestamp
                time_str = created_at.strftime('%H:%M') if hasattr(created_at, 'strftime') else 'N/A'
            
            recent_sales.append({
                'bill_number': sale['bill_number'],
                'total_amount': str(sale['total_amount']),
                'customer_name': sale['customer_name'] or 'Walk-in Customer',
                'created_at': str(created_at),
                'time': time_str
            })
        
        conn.close()
        
        return {
            'success': True,
            'today_sales': today_sales,
            'today_revenue': today_revenue,
            'today_profit': today_profit,
            'today_orders': today_orders,
            'today_receivable': 0,
            'today_receivable_profit': 0,
            'today_cost': 0,
            'profit_margin': 0,
            'week_revenue': 0,
            'month_revenue': 0,
            'total_products': 0,
            'low_stock': 0,
            'out_of_stock': 0,
            'total_customers': 0,
            'total_receivable': 0,
            'total_pending_bills': 0,
            'total_receivable_profit': 0,
            'sales_change_percent': 0,
            'revenue_change_percent': -100.0,  # Show 100% decrease since no revenue
            'orders_change_percent': 0,
            'profit_change_percent': -100.0,   # Show 100% decrease since no profit
            'profit_margin_percent': 0,
            'recent_sales': recent_sales,
            'top_products': [],
            'timestamp': datetime.now().isoformat(),
            # Nested format for compatibility
            'today': {
                'sales': today_sales,
                'revenue': today_revenue,
                'receivable': 0,
                'transactions': today_orders,
                'profit': today_profit,
                'receivable_profit': 0,
                'cost': 0,
                'profit_margin': 0
            },
            'total': {
                'receivable': 0,
                'receivable_profit': 0,
                'pending_bills': 0
            },
            'week': {
                'revenue': 0
            },
            'month': {
                'revenue': 0
            },
            'inventory': {
                'total_products': 0,
                'low_stock': 0,
                'out_of_stock': 0
            },
            'customers': {
                'total': 0
            }
        }
        
        # Build user filter condition - STRICT ISOLATION
        if db_type == 'postgresql':
            user_filter = ""
            user_params = []
            if user_id:
                user_filter = "AND business_owner_id = %s"
                user_params = [user_id]
        else:
            user_filter = ""
            user_params = []
            if user_id:
                user_filter = "AND business_owner_id = ?"
                user_params = [user_id]
        
        # Today's Sales (ALL bills including credit/partial)
        if db_type == 'postgresql':
            today_sales_data = cursor.execute(f'''
                SELECT 
                    COALESCE(SUM(total_amount), 0) as total_sales,
                    COUNT(*) as transactions
                FROM bills 
                WHERE CAST(created_at AS DATE) = %s {user_filter}
            ''', [today] + user_params).fetchone()
            print(f"🔍 [SALES DEBUG] PostgreSQL sales query result: {today_sales_data}")
        else:
            today_sales_data = cursor.execute(f'''
                SELECT 
                    COALESCE(SUM(total_amount), 0) as total_sales,
                    COUNT(*) as transactions
                FROM bills 
                WHERE DATE(created_at) = ? {user_filter}
            ''', [today] + user_params).fetchone()
            print(f"🔍 [SALES DEBUG] SQLite sales query result: {today_sales_data}")
        
        # Today's Revenue (only ACTUAL PAYMENTS processed TODAY - not billing date)
        # INCLUDES: Cash/Card/UPI bills created today + ALL payments processed today
        # EXCLUDES: Cheque payments that are not yet cleared (payment_status = 'cheque_deposited')
        if db_type == 'postgresql':
            # Get cash/card/upi bills created today (these count as immediate revenue)
            print(f"🔍 [REVENUE DEBUG] Querying cash revenue for {today} with user_filter: {user_filter}")
            print(f"🔍 [REVENUE DEBUG] User params: {user_params}")
            today_cash_revenue = cursor.execute(f'''
                SELECT COALESCE(SUM(total_amount), 0) as cash_revenue
                FROM bills 
                WHERE CAST(created_at AS DATE) = %s 
                AND (is_credit = FALSE OR payment_status = 'paid')
                AND payment_status != 'cheque_deposited'
                {user_filter}
            ''', [today] + user_params).fetchone()
            print(f"🔍 [REVENUE DEBUG] Cash revenue result: {today_cash_revenue}")
            
            # Get ALL payments processed today (including credit payments for old bills)
            # EXCLUDE payments from bills with cheque_deposited status (not yet cleared)
            payment_user_filter = ""
            if user_id:
                payment_user_filter = "AND b.business_owner_id = %s"
            
            print(f"🔍 [REVENUE DEBUG] Querying payment revenue for {today} with payment_user_filter: {payment_user_filter}")
            print(f"🔍 [REVENUE DEBUG] Payment params: {[today] + ([user_id] if user_id else [])}")
            today_payment_revenue = cursor.execute(f'''
                SELECT COALESCE(SUM(p.amount), 0) as payment_revenue
                FROM payments p
                JOIN bills b ON p.bill_id = b.id
                WHERE CAST(p.processed_at AS DATE) = %s
                AND b.payment_status != 'cheque_deposited'
                {payment_user_filter}
            ''', [today] + ([user_id] if user_id else [])).fetchone()
            print(f"🔍 [REVENUE DEBUG] Payment revenue result: {today_payment_revenue}")
            print(f"🔍 [REVENUE DEBUG] Payment revenue value: {today_payment_revenue['payment_revenue'] if today_payment_revenue else 'None'}")
            
            # Use ONLY payment-based revenue to avoid double-counting
            # Cash bills created today will be counted when their payments are processed
            today_revenue = float(today_payment_revenue['payment_revenue'] or 0)
            today_revenue_data = {'revenue': today_revenue}
            print(f"🔍 [REVENUE DEBUG] Final today_revenue: {today_revenue}")
        else:
            # Get cash/card/upi bills created today (these count as immediate revenue)
            # EXCLUDE cheque bills that are not yet cleared
            today_cash_revenue = cursor.execute(f'''
                SELECT COALESCE(SUM(total_amount), 0) as cash_revenue
                FROM bills 
                WHERE DATE(created_at) = ? 
                AND (is_credit = 0 OR payment_status = 'paid')
                AND payment_status != 'cheque_deposited'
                {user_filter}
            ''', [today] + user_params).fetchone()
            
            # Get ALL payments processed today (including credit payments for old bills)
            # EXCLUDE payments from bills with cheque_deposited status (not yet cleared)
            payment_user_filter = ""
            if user_id:
                payment_user_filter = "AND b.business_owner_id = ?"
            
            today_payment_revenue = cursor.execute(f'''
                SELECT COALESCE(SUM(p.amount), 0) as payment_revenue
                FROM payments p
                JOIN bills b ON p.bill_id = b.id
                WHERE DATE(p.processed_at) = ?
                AND b.payment_status != 'cheque_deposited'
                {payment_user_filter}
            ''', [today] + ([user_id] if user_id else [])).fetchone()
            
            # Use ONLY payment-based revenue to avoid double-counting
            # Cash bills created today will be counted when their payments are processed
            today_revenue = float(today_payment_revenue['payment_revenue'] or 0)
            today_revenue_data = {'revenue': today_revenue}
        
        # Revenue is already calculated above - no need for additional credit payments logic
        today_revenue = float(today_revenue_data['revenue'] or 0)
        
        print(f"💰 [DASHBOARD REVENUE] Today's revenue breakdown:")
        print(f"   User ID: {user_id}")
        print(f"   Today's date: {today}")
        print(f"   TOTAL Revenue (payments processed today): ₹{today_revenue:.2f}")
        print(f"=" * 80)
        
        # Today's Receivable (unpaid credit balance) - includes partial payments
        if db_type == 'postgresql':
            today_receivable_data = cursor.execute(f'''
                SELECT 
                    COALESCE(SUM(credit_balance), 0) as receivable
                FROM bills 
                WHERE CAST(created_at AS DATE) = %s {user_filter}
                AND is_credit = TRUE
                AND credit_balance > 0
            ''', [today] + user_params).fetchone()
        else:
            today_receivable_data = cursor.execute(f'''
                SELECT 
                    COALESCE(SUM(credit_balance), 0) as receivable
                FROM bills 
                WHERE DATE(created_at) = ? {user_filter}
                AND is_credit = 1
                AND credit_balance > 0
            ''', [today] + user_params).fetchone()
        
        # 🔥 TOTAL Receivable (ALL pending credit bills - not just today)
        if db_type == 'postgresql':
            total_receivable_data = cursor.execute(f'''
                SELECT 
                    COALESCE(SUM(credit_balance), 0) as total_receivable,
                    COUNT(*) as pending_bills
                FROM bills 
                WHERE is_credit = TRUE
                AND credit_balance > 0 {user_filter}
            ''', user_params).fetchone()
        else:
            total_receivable_data = cursor.execute(f'''
                SELECT 
                    COALESCE(SUM(credit_balance), 0) as total_receivable,
                    COUNT(*) as pending_bills
                FROM bills 
                WHERE is_credit = 1
                AND credit_balance > 0 {user_filter}
            ''', user_params).fetchone()
        
        
        # Yesterday's Sales for comparison
        yesterday_sales_data = cursor.execute(f'''
            SELECT 
                COALESCE(SUM(total_amount), 0) as total_sales
            FROM bills 
            WHERE DATE(created_at) = ? {user_filter}
        ''', [yesterday] + user_params).fetchone()
        
        # Yesterday's Revenue for comparison (payments processed yesterday)
        # EXCLUDE payments from bills with cheque_deposited status
        yesterday_payment_revenue = cursor.execute(f'''
            SELECT COALESCE(SUM(p.amount), 0) as revenue
            FROM payments p
            JOIN bills b ON p.bill_id = b.id
            WHERE DATE(p.processed_at) = ?
            AND b.payment_status != 'cheque_deposited'
            {user_filter.replace("business_owner_id", "b.business_owner_id") if user_filter else ""}
        ''', [yesterday] + ([user_id] if user_id else [])).fetchone()
        yesterday_revenue_data = {'revenue': yesterday_payment_revenue['revenue'] if yesterday_payment_revenue else 0}
        
        # Yesterday's orders for comparison
        yesterday_orders = cursor.execute(f'''
            SELECT COUNT(*) as bills
            FROM bills
            WHERE DATE(created_at) = ? {user_filter}
        ''', [yesterday] + user_params).fetchone()
        
        # Today's Cost & Profit (based on ACTUAL PAYMENTS received today)
        # EXCLUDES: Cheque payments that are not yet cleared
        if db_type == 'postgresql':
            # Get profit from cash/card/upi bills created today (exclude uncashed cheques)
            today_cash_profit = cursor.execute(f'''
                SELECT 
                    COALESCE(SUM(bi.total_price), 0) as total_sales,
                    COALESCE(SUM(bi.quantity * COALESCE(p.cost, 0)), 0) as total_cost
                FROM bill_items bi
                LEFT JOIN products p ON bi.product_id = p.id
                JOIN bills b ON bi.bill_id = b.id
                WHERE CAST(b.created_at AS DATE) = %s 
                AND (b.is_credit = FALSE OR b.payment_status = 'paid')
                AND b.payment_status != 'cheque_deposited'
                {user_filter}
            ''', [today] + user_params).fetchone()
            
            # Get profit from ALL payments processed today (including credit payments)
            # EXCLUDE payments from bills with cheque_deposited status
            payment_profit_user_filter = ""
            if user_id:
                payment_profit_user_filter = "AND b.business_owner_id = %s"
            
            today_payment_profit = cursor.execute(f'''
                SELECT 
                    COALESCE(SUM(
                        CASE 
                            WHEN b.total_amount > 0 THEN 
                                (bi.total_price * p.amount / b.total_amount)
                            ELSE 0
                        END
                    ), 0) as total_sales,
                    COALESCE(SUM(
                        CASE 
                            WHEN b.total_amount > 0 THEN 
                                (bi.quantity * COALESCE(pr.cost, 0) * p.amount / b.total_amount)
                            ELSE 0
                        END
                    ), 0) as total_cost
                FROM payments p
                JOIN bills b ON p.bill_id = b.id
                JOIN bill_items bi ON b.id = bi.bill_id
                LEFT JOIN products pr ON bi.product_id = pr.id
                WHERE CAST(p.processed_at AS DATE) = %s
                AND b.payment_status != 'cheque_deposited'
                {payment_profit_user_filter}
            ''', [today] + ([user_id] if user_id else [])).fetchone()
            
            # Combine both sources
            today_profit_data = {
                'total_sales': float(today_cash_profit['total_sales'] or 0) + float(today_payment_profit['total_sales'] or 0),
                'total_cost': float(today_cash_profit['total_cost'] or 0) + float(today_payment_profit['total_cost'] or 0)
            }
        else:
            # Get profit from cash/card/upi bills created today (exclude uncashed cheques)
            today_cash_profit = cursor.execute(f'''
                SELECT 
                    COALESCE(SUM(bi.total_price), 0) as total_sales,
                    COALESCE(SUM(bi.quantity * COALESCE(p.cost, 0)), 0) as total_cost
                FROM bill_items bi
                LEFT JOIN products p ON bi.product_id = p.id
                JOIN bills b ON bi.bill_id = b.id
                WHERE DATE(b.created_at) = ? 
                AND (b.is_credit = 0 OR b.payment_status = 'paid')
                AND b.payment_status != 'cheque_deposited'
                {user_filter}
            ''', [today] + user_params).fetchone()
            
            # Get profit from ALL payments processed today (including credit payments)
            # EXCLUDE payments from bills with cheque_deposited status
            payment_profit_user_filter = ""
            if user_id:
                payment_profit_user_filter = "AND b.business_owner_id = ?"
            
            today_payment_profit = cursor.execute(f'''
                SELECT 
                    COALESCE(SUM(
                        CASE 
                            WHEN b.total_amount > 0 THEN 
                                (bi.total_price * p.amount / b.total_amount)
                            ELSE 0
                        END
                    ), 0) as total_sales,
                    COALESCE(SUM(
                        CASE 
                            WHEN b.total_amount > 0 THEN 
                                (bi.quantity * COALESCE(pr.cost, 0) * p.amount / b.total_amount)
                            ELSE 0
                        END
                    ), 0) as total_cost
                FROM payments p
                JOIN bills b ON p.bill_id = b.id
                JOIN bill_items bi ON b.id = bi.bill_id
                LEFT JOIN products pr ON bi.product_id = pr.id
                WHERE DATE(p.processed_at) = ?
                AND b.payment_status != 'cheque_deposited'
                {payment_profit_user_filter}
            ''', [today] + ([user_id] if user_id else [])).fetchone()
            
            # Combine both sources
            today_profit_data = {
                'total_sales': float(today_cash_profit['total_sales'] or 0) + float(today_payment_profit['total_sales'] or 0),
                'total_cost': float(today_cash_profit['total_cost'] or 0) + float(today_payment_profit['total_cost'] or 0)
            }
        
        # Receivable Profit (profit from unpaid portion - includes partial payments)
        today_receivable_profit_data = cursor.execute(f'''
            SELECT 
                COALESCE(SUM(
                    CASE 
                        WHEN b.payment_status = 'unpaid' THEN bi.total_price
                        WHEN b.payment_status = 'partial' AND b.total_amount > 0 THEN 
                            (bi.total_price * b.credit_balance / b.total_amount)
                        ELSE 0
                    END
                ), 0) as total_sales,
                COALESCE(SUM(
                    CASE 
                        WHEN b.payment_status = 'unpaid' THEN bi.quantity * COALESCE(p.cost, 0)
                        WHEN b.payment_status = 'partial' AND b.total_amount > 0 THEN 
                            (bi.quantity * COALESCE(p.cost, 0) * b.credit_balance / b.total_amount)
                        ELSE 0
                    END
                ), 0) as total_cost
            FROM bill_items bi
            LEFT JOIN products p ON bi.product_id = p.id
            JOIN bills b ON bi.bill_id = b.id
            WHERE DATE(b.created_at) = ? {user_filter}
            AND b.is_credit = 1
            AND b.credit_balance > 0
        ''', [today] + user_params).fetchone()
        
        # 🔥 TOTAL Receivable Profit (ALL pending credit bills - not just today)
        total_receivable_profit_data = cursor.execute(f'''
            SELECT 
                COALESCE(SUM(
                    CASE 
                        WHEN b.payment_status = 'unpaid' THEN bi.total_price
                        WHEN b.payment_status = 'partial' AND b.total_amount > 0 THEN 
                            (bi.total_price * b.credit_balance / b.total_amount)
                        ELSE 0
                    END
                ), 0) as total_sales,
                COALESCE(SUM(
                    CASE 
                        WHEN b.payment_status = 'unpaid' THEN bi.quantity * COALESCE(p.cost, 0)
                        WHEN b.payment_status = 'partial' AND b.total_amount > 0 THEN 
                            (bi.quantity * COALESCE(p.cost, 0) * b.credit_balance / b.total_amount)
                        ELSE 0
                    END
                ), 0) as total_cost
            FROM bill_items bi
            LEFT JOIN products p ON bi.product_id = p.id
            JOIN bills b ON bi.bill_id = b.id
            WHERE b.is_credit = 1
            AND b.credit_balance > 0 {user_filter}
        ''', user_params).fetchone()
        
        
        # Yesterday's Cost & Profit for comparison (based on payments processed yesterday)
        # EXCLUDE payments from bills with cheque_deposited status
        yesterday_payment_profit = cursor.execute(f'''
            SELECT 
                COALESCE(SUM(
                    CASE 
                        WHEN b.total_amount > 0 THEN 
                            (bi.total_price * p.amount / b.total_amount)
                        ELSE 0
                    END
                ), 0) as total_sales,
                COALESCE(SUM(
                    CASE 
                        WHEN b.total_amount > 0 THEN 
                            (bi.quantity * COALESCE(pr.cost, 0) * p.amount / b.total_amount)
                        ELSE 0
                    END
                ), 0) as total_cost
            FROM payments p
            JOIN bills b ON p.bill_id = b.id
            JOIN bill_items bi ON b.id = bi.bill_id
            LEFT JOIN products pr ON bi.product_id = pr.id
            WHERE DATE(p.processed_at) = ?
            AND b.payment_status != 'cheque_deposited'
            {user_filter.replace("business_owner_id", "b.business_owner_id") if user_filter else ""}
        ''', [yesterday] + ([user_id] if user_id else [])).fetchone()
        
        # Also get profit from cash/card/upi bills created yesterday (exclude uncashed cheques)
        yesterday_cash_profit = cursor.execute(f'''
            SELECT 
                COALESCE(SUM(bi.total_price), 0) as total_sales,
                COALESCE(SUM(bi.quantity * COALESCE(p.cost, 0)), 0) as total_cost
            FROM bill_items bi
            LEFT JOIN products p ON bi.product_id = p.id
            JOIN bills b ON bi.bill_id = b.id
            WHERE DATE(b.created_at) = ? 
            AND (b.is_credit = 0 OR b.payment_status = 'paid')
            AND b.payment_status != 'cheque_deposited'
            {user_filter}
        ''', [yesterday] + user_params).fetchone()
        
        yesterday_profit_data = {
            'total_sales': float(yesterday_cash_profit['total_sales'] or 0) + float(yesterday_payment_profit['total_sales'] or 0),
            'total_cost': float(yesterday_cash_profit['total_cost'] or 0) + float(yesterday_payment_profit['total_cost'] or 0)
        }
        
        total_sales = float(today_profit_data['total_sales'])
        total_cost = float(today_profit_data['total_cost'])
        today_profit = total_sales - total_cost
        profit_margin = (today_profit / total_sales * 100) if total_sales > 0 else 0
        
        # Calculate today's receivable profit
        receivable_sales = float(today_receivable_profit_data['total_sales'])
        receivable_cost = float(today_receivable_profit_data['total_cost'])
        receivable_profit = receivable_sales - receivable_cost
        
        # 🔥 Calculate TOTAL receivable profit (all pending bills)
        total_receivable_sales = float(total_receivable_profit_data['total_sales'])
        total_receivable_cost = float(total_receivable_profit_data['total_cost'])
        total_receivable_profit = total_receivable_sales - total_receivable_cost
        
        yesterday_total_sales = float(yesterday_profit_data['total_sales'])
        yesterday_total_cost = float(yesterday_profit_data['total_cost'])
        yesterday_profit = yesterday_total_sales - yesterday_total_cost
        
        # Calculate percentage changes
        today_sales_value = float(today_sales_data['total_sales'])
        yesterday_sales_value = float(yesterday_sales_data['total_sales'])
        today_revenue_value = today_revenue  # Use the combined revenue
        yesterday_revenue_value = float(yesterday_revenue_data['revenue'])
        today_receivable_value = float(today_receivable_data['receivable'])
        total_receivable_value = float(total_receivable_data['total_receivable'])
        total_pending_bills = int(total_receivable_data['pending_bills'])
        
        # Debug logging (after all variables are defined)
        print(f"📊 [DASHBOARD] Today's Stats:")
        print(f"   Sales (Total): ₹{today_sales_value:.2f}")
        print(f"   Revenue (Paid): ₹{today_revenue_value:.2f}")
        print(f"   Receivable (Today): ₹{today_receivable_value:.2f}")
        print(f"   Receivable (TOTAL): ₹{total_receivable_value:.2f} ({total_pending_bills} bills)")
        print(f"   Profit (on Paid): ₹{today_profit:.2f}")
        print(f"   Receivable Profit (Today): ₹{receivable_profit:.2f}")
        print(f"   Receivable Profit (TOTAL): ₹{total_receivable_profit:.2f}")
        
        sales_change = 0
        if yesterday_sales_value > 0:
            sales_change = ((today_sales_value - yesterday_sales_value) / yesterday_sales_value) * 100
        elif today_sales_value > 0:
            sales_change = 100  # If no sales yesterday but sales today, it's 100% increase
            
        revenue_change = 0
        if yesterday_revenue_value > 0:
            revenue_change = ((today_revenue_value - yesterday_revenue_value) / yesterday_revenue_value) * 100
        elif today_revenue_value > 0:
            revenue_change = 100
            
        profit_change = 0
        if yesterday_profit > 0:
            profit_change = ((today_profit - yesterday_profit) / yesterday_profit) * 100
        elif today_profit > 0:
            profit_change = 100
            
        orders_change = 0
        today_orders_count = int(today_sales_data['transactions'])
        yesterday_orders_count = int(yesterday_orders['bills'])
        
        if yesterday_orders_count > 0:
            orders_change = ((today_orders_count - yesterday_orders_count) / yesterday_orders_count) * 100
        elif today_orders_count > 0:
            orders_change = 100
        
        # Total Products
        if user_id:
            # STRICT ISOLATION: Only count user's own products
            total_products = cursor.execute('''
                SELECT COUNT(*) as count FROM products WHERE is_active = 1 AND user_id = ?
            ''', (user_id,)).fetchone()['count']
            
            # Low Stock Products - STRICT ISOLATION
            low_stock = cursor.execute('''
                SELECT COUNT(*) as count FROM products 
                WHERE stock > 0 AND stock <= min_stock AND is_active = 1 AND user_id = ?
            ''', (user_id,)).fetchone()['count']
            
            # Out of Stock Products - STRICT ISOLATION
            out_of_stock = cursor.execute('''
                SELECT COUNT(*) as count FROM products 
                WHERE stock = 0 AND is_active = 1 AND user_id = ?
            ''', (user_id,)).fetchone()['count']
            
            # Total Customers - STRICT ISOLATION
            total_customers = cursor.execute('''
                SELECT COUNT(*) as count FROM customers WHERE is_active = 1 AND user_id = ?
            ''', (user_id,)).fetchone()['count']
        else:
            # No user_id: count nothing
            total_products = 0
            
            # Low Stock Products (excluding out of stock)
            low_stock = cursor.execute('''
                SELECT COUNT(*) as count FROM products 
                WHERE stock > 0 AND stock <= min_stock AND is_active = 1
            ''').fetchone()['count']
            
            # Out of Stock Products
            out_of_stock = cursor.execute('''
                SELECT COUNT(*) as count FROM products 
                WHERE stock = 0 AND is_active = 1
            ''').fetchone()['count']
            
            # Total Customers - No user_id
            total_customers = 0
        
        # Recent Sales (Last 10)
        recent_sales = cursor.execute(f'''
            SELECT 
                b.bill_number,
                b.total_amount,
                b.created_at,
                COALESCE(c.name, 'Walk-in Customer') as customer_name,
                TO_CHAR(b.created_at, 'HH24:MI') as time
            FROM bills b
            LEFT JOIN customers c ON b.customer_id = c.id
            WHERE CAST(b.created_at AS DATE) = ? {user_filter}
            ORDER BY b.created_at DESC
            LIMIT 10
        ''', [today] + user_params).fetchall()
        
        # Top Selling Products Today
        top_products = cursor.execute(f'''
            SELECT 
                s.product_name,
                SUM(s.quantity) as total_quantity,
                SUM(s.total_price) as total_sales,
                COUNT(DISTINCT s.bill_id) as times_sold
            FROM sales s
            WHERE s.sale_date = ? {user_filter.replace('business_owner_id', 's.business_owner_id')}
            GROUP BY s.product_id, s.product_name
            ORDER BY total_quantity DESC
            LIMIT 5
        ''', [today] + user_params).fetchall()
        
        # This Week's Revenue (based on actual payments, excluding uncashed cheques)
        if db_type == 'postgresql':
            week_revenue = cursor.execute(f'''
                SELECT COALESCE(SUM(p.amount), 0) as revenue
                FROM payments p
                JOIN bills b ON p.bill_id = b.id
                WHERE CAST(p.processed_at AS DATE) >= CURRENT_DATE - EXTRACT(DOW FROM CURRENT_DATE)::INTEGER
                AND b.payment_status != 'cheque_deposited'
                {user_filter.replace("business_owner_id", "b.business_owner_id") if user_filter else ""}
            ''', ([user_id] if user_id else [])).fetchone()['revenue']
        else:
            week_revenue = cursor.execute(f'''
                SELECT COALESCE(SUM(p.amount), 0) as revenue
                FROM payments p
                JOIN bills b ON p.bill_id = b.id
                WHERE DATE(p.processed_at) >= DATE('now', 'weekday 0', '-7 days')
                AND b.payment_status != 'cheque_deposited'
                {user_filter.replace("business_owner_id", "b.business_owner_id") if user_filter else ""}
            ''', ([user_id] if user_id else [])).fetchone()['revenue']
        
        # This Month's Revenue (based on actual payments, excluding uncashed cheques)
        if db_type == 'postgresql':
            month_revenue = cursor.execute(f'''
                SELECT COALESCE(SUM(p.amount), 0) as revenue
                FROM payments p
                JOIN bills b ON p.bill_id = b.id
                WHERE TO_CHAR(p.processed_at, 'YYYY-MM') = TO_CHAR(CURRENT_DATE, 'YYYY-MM')
                AND b.payment_status != 'cheque_deposited'
                {user_filter.replace("business_owner_id", "b.business_owner_id") if user_filter else ""}
            ''', ([user_id] if user_id else [])).fetchone()['revenue']
        else:
            month_revenue = cursor.execute(f'''
                SELECT COALESCE(SUM(p.amount), 0) as revenue
                FROM payments p
                JOIN bills b ON p.bill_id = b.id
                WHERE strftime('%Y-%m', p.processed_at) = strftime('%Y-%m', 'now')
                AND b.payment_status != 'cheque_deposited'
                {user_filter.replace("business_owner_id", "b.business_owner_id") if user_filter else ""}
            ''', ([user_id] if user_id else [])).fetchone()['revenue']
        
        conn.close()
        
        return {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            # Frontend expects these keys
            'today_sales': float(today_sales_value),  # Total sales including credit
            'today_revenue': float(today_revenue_value),  # Only paid amounts
            'today_receivable': float(today_receivable_value),  # TODAY's unpaid credit balance ONLY
            'total_receivable': float(total_receivable_value),  # 🔥 TOTAL receivable (ALL pending bills)
            'total_pending_bills': total_pending_bills,  # 🔥 Count of pending bills
            'today_orders': int(today_sales_data['transactions']),  # Total bills count
            'today_profit': round(today_profit, 2),
            'today_receivable_profit': round(receivable_profit, 2),  # TODAY's profit from unpaid credit ONLY
            'total_receivable_profit': round(total_receivable_profit, 2),  # 🔥 TOTAL receivable profit
            'today_cost': round(total_cost, 2),
            'profit_margin': round(profit_margin, 2),
            'week_revenue': float(week_revenue),
            'month_revenue': float(month_revenue),
            'total_products': total_products,
            'low_stock': low_stock,
            'out_of_stock': out_of_stock,
            'total_customers': total_customers,
            # Percentage changes for dashboard
            'sales_change_percent': round(sales_change, 1),
            'revenue_change_percent': round(revenue_change, 1),
            'orders_change_percent': round(orders_change, 1),
            'profit_change_percent': round(profit_change, 1),
            'profit_margin_percent': round(profit_margin, 1),
            # Also keep nested format for compatibility
            'today': {
                'sales': float(today_sales_value),  # Includes ALL bills
                'revenue': float(today_revenue_value),  # Only PAID amounts
                'receivable': float(today_receivable_value),  # TODAY's unpaid credit balance ONLY
                'transactions': int(today_sales_data['transactions']),
                'profit': round(today_profit, 2),
                'receivable_profit': round(receivable_profit, 2),  # TODAY's profit from unpaid credit ONLY
                'cost': round(total_cost, 2),
                'profit_margin': round(profit_margin, 2)
            },
            'total': {
                'receivable': float(total_receivable_value),  # 🔥 TOTAL receivable (ALL pending bills)
                'receivable_profit': round(total_receivable_profit, 2),  # 🔥 TOTAL receivable profit
                'pending_bills': total_pending_bills  # 🔥 Count of pending bills
            },
            'week': {
                'revenue': float(week_revenue)
            },
            'month': {
                'revenue': float(month_revenue)
            },
            'inventory': {
                'total_products': total_products,
                'low_stock': low_stock,
                'out_of_stock': out_of_stock
            },
            'customers': {
                'total': total_customers
            },
            'recent_sales': [dict(row) for row in recent_sales],
            'top_products': [dict(row) for row in top_products]
        }
    
    def get_recent_activity(self, user_id=None):
        """Get recent activity for dashboard - FORMATTED FOR FRONTEND - Filtered by user"""
        try:
            # Use the dashboard service to get properly formatted activities
            from modules.dashboard.service import DashboardService
            activities = DashboardService.get_recent_activities_only(limit=10, user_id=user_id)
            
            return {
                'success': True,
                'activities': activities,
                'count': len(activities)
            }
        except Exception as e:
            print(f"Error in get_recent_activity: {e}")
            # Fallback to manual formatting if dashboard service fails
            return self._get_recent_activity_fallback(user_id)
    
    def _get_recent_activity_fallback(self, user_id=None):
        """Fallback method to format activities manually - Filtered by user"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        activities = []
        
        # Build query with user filtering and today's date filter to match sales module
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        
        query = '''
            SELECT 
                b.id,
                b.bill_number,
                b.total_amount,
                b.created_at,
                b.payment_method,
                COALESCE(b.customer_name, c.name, 'Walk-in Customer') as customer_name
            FROM bills b
            LEFT JOIN customers c ON b.customer_id = c.id
            WHERE DATE(b.created_at) = ?
        '''
        
        params = [today]
        if user_id:
            query += ' AND b.business_owner_id = ?'
            params.append(user_id)
        
        query += ' ORDER BY b.created_at DESC LIMIT 8'
        
        # Get recent bills and format as activities
        recent_bills = cursor.execute(query, params).fetchall()
        
        for bill in recent_bills:
            amount = float(bill['total_amount']) if bill['total_amount'] else 0
            activities.append({
                'id': f"sale-{bill['id']}",
                'title': 'Sale completed successfully',
                'description': f"₹{amount:,.0f} - {bill['customer_name']}",
                'amount': amount,
                'timestamp': bill['created_at'],
                'type': 'sale',
                'icon': '💰'
            })
        
        # Get recent products and format as activities
        recent_products = cursor.execute('''
            SELECT id, name, price, category, created_at
            FROM products
            WHERE is_active = 1
            ORDER BY created_at DESC
            LIMIT 5
        ''').fetchall()
        
        for product in recent_products:
            price = float(product['price']) if product['price'] else 0
            activities.append({
                'id': f"product-{product['id']}",
                'title': f"New product added: {product['name']}",
                'description': f"{product.get('category', 'General')} - ₹{price:,.0f}",
                'amount': 0,
                'timestamp': product['created_at'],
                'type': 'product',
                'icon': '📦'
            })
        
        # Get recent customers and format as activities
        recent_customers = cursor.execute('''
            SELECT id, name, phone, created_at
            FROM customers
            WHERE is_active = 1
            ORDER BY created_at DESC
            LIMIT 5
        ''').fetchall()
        
        for customer in recent_customers:
            phone_display = f" - {customer['phone']}" if customer['phone'] else ""
            activities.append({
                'id': f"customer-{customer['id']}",
                'title': 'New customer registered',
                'description': f"{customer['name']}{phone_display}",
                'amount': 0,
                'timestamp': customer['created_at'],
                'type': 'customer',
                'icon': '👤'
            })
        
        conn.close()
        
        # Sort by timestamp (most recent first)
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return {
            'success': True,
            'activities': activities[:10],  # Limit to 10 most recent
            'count': len(activities[:10])
        }