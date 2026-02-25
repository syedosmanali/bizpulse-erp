"""
ERP Modules Database Initialization
Creates all tables for the comprehensive ERP system with proper indexes and constraints
Supports both SQLite (development) and PostgreSQL (production)
"""

from modules.shared.database import get_db_connection, get_db_type, generate_id
import logging

logger = logging.getLogger(__name__)

def init_erp_tables():
    """Initialize all ERP module tables"""
    db_type = get_db_type()
    logger.info(f"Initializing ERP tables for {db_type.upper()}...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Helper functions for SQL syntax
    def get_text_pk():
        return 'VARCHAR(255) PRIMARY KEY' if db_type == 'postgresql' else 'TEXT PRIMARY KEY'
    
    def get_boolean_default(value):
        return str(value).upper() if db_type == 'postgresql' else str(int(value))
    
    def get_numeric():
        return 'NUMERIC(10,2)' if db_type == 'postgresql' else 'REAL'
    
    def get_jsonb():
        return 'JSONB' if db_type == 'postgresql' else 'TEXT'
    
    try:
        # ==================== COMPANY SETUP ====================
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS erp_company (
                id {get_text_pk()},
                user_id VARCHAR(255) NOT NULL,
                company_name VARCHAR(255) NOT NULL,
                gst_number VARCHAR(15),
                pan_number VARCHAR(10),
                financial_year VARCHAR(20),
                invoice_prefix VARCHAR(10) DEFAULT 'INV',
                invoice_starting_number INTEGER DEFAULT 1,
                address TEXT,
                city VARCHAR(100),
                state VARCHAR(100),
                pincode VARCHAR(10),
                phone VARCHAR(20),
                email VARCHAR(255),
                logo_url TEXT,
                default_tax_rate {get_numeric()} DEFAULT 18.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id)
            )
        ''')
        
        # ==================== BANK MANAGEMENT ====================
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS erp_banks (
                id {get_text_pk()},
                user_id VARCHAR(255) NOT NULL,
                bank_name VARCHAR(255) NOT NULL,
                account_number VARCHAR(50) NOT NULL,
                ifsc_code VARCHAR(11) NOT NULL,
                branch VARCHAR(255),
                account_type VARCHAR(50) DEFAULT 'current',
                opening_balance {get_numeric()} DEFAULT 0,
                current_balance {get_numeric()} DEFAULT 0,
                is_default BOOLEAN DEFAULT {get_boolean_default(False)},
                is_active BOOLEAN DEFAULT {get_boolean_default(True)},
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for banks
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_banks_user ON erp_banks(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_banks_default ON erp_banks(user_id, is_default)')
        
        # ==================== PRODUCTS (Enhanced) ====================
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS erp_products (
                id {get_text_pk()},
                user_id VARCHAR(255) NOT NULL,
                product_code VARCHAR(50) NOT NULL,
                product_name VARCHAR(255) NOT NULL,
                category VARCHAR(100),
                brand VARCHAR(100),
                hsn_code VARCHAR(8),
                gst_rate {get_numeric()} DEFAULT 18.0,
                unit VARCHAR(20) DEFAULT 'pcs',
                cost_price {get_numeric()} DEFAULT 0,
                selling_price {get_numeric()} NOT NULL,
                min_stock_level INTEGER DEFAULT 10,
                current_stock INTEGER DEFAULT 0,
                barcode VARCHAR(255),
                has_batch_tracking BOOLEAN DEFAULT {get_boolean_default(False)},
                has_expiry_tracking BOOLEAN DEFAULT {get_boolean_default(False)},
                is_active BOOLEAN DEFAULT {get_boolean_default(True)},
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, product_code)
            )
        ''')
        
        # Create indexes for products
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_user ON erp_products(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_barcode ON erp_products(barcode)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_hsn ON erp_products(hsn_code)')
        
        # ==================== CUSTOMERS ====================
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS erp_customers (
                id {get_text_pk()},
                user_id VARCHAR(255) NOT NULL,
                customer_name VARCHAR(255) NOT NULL,
                phone VARCHAR(20),
                email VARCHAR(255),
                address TEXT,
                city VARCHAR(100),
                state VARCHAR(100),
                pincode VARCHAR(10),
                gst_number VARCHAR(15),
                credit_limit {get_numeric()} DEFAULT 0,
                credit_days INTEGER DEFAULT 0,
                outstanding_balance {get_numeric()} DEFAULT 0,
                total_purchases {get_numeric()} DEFAULT 0,
                customer_type VARCHAR(50) DEFAULT 'regular',
                is_active BOOLEAN DEFAULT {get_boolean_default(True)},
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for customers
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_customers_user ON erp_customers(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_customers_phone ON erp_customers(phone)')
        
        # ==================== VENDORS/SUPPLIERS ====================
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS erp_vendors (
                id {get_text_pk()},
                user_id VARCHAR(255) NOT NULL,
                vendor_name VARCHAR(255) NOT NULL,
                phone VARCHAR(20),
                email VARCHAR(255),
                address TEXT,
                city VARCHAR(100),
                state VARCHAR(100),
                pincode VARCHAR(10),
                gst_number VARCHAR(15),
                payment_terms TEXT,
                outstanding_balance {get_numeric()} DEFAULT 0,
                total_purchases {get_numeric()} DEFAULT 0,
                is_active BOOLEAN DEFAULT {get_boolean_default(True)},
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create index for vendors
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_vendors_user ON erp_vendors(user_id)')
        
        # ==================== INVOICES ====================
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS erp_invoices (
                id {get_text_pk()},
                user_id VARCHAR(255) NOT NULL,
                invoice_number VARCHAR(50) NOT NULL,
                customer_id VARCHAR(255),
                customer_name VARCHAR(255) NOT NULL,
                invoice_date DATE NOT NULL,
                due_date DATE,
                subtotal {get_numeric()} NOT NULL,
                tax_amount {get_numeric()} DEFAULT 0,
                discount_amount {get_numeric()} DEFAULT 0,
                total_amount {get_numeric()} NOT NULL,
                paid_amount {get_numeric()} DEFAULT 0,
                balance_amount {get_numeric()} DEFAULT 0,
                payment_status VARCHAR(50) DEFAULT 'unpaid',
                payment_mode VARCHAR(50),
                items {get_jsonb()} NOT NULL,
                notes TEXT,
                terms_conditions TEXT,
                status VARCHAR(50) DEFAULT 'draft',
                is_credit BOOLEAN DEFAULT {get_boolean_default(False)},
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, invoice_number)
            )
        ''')
        
        # Create indexes for invoices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_invoices_user ON erp_invoices(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_invoices_customer ON erp_invoices(customer_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_invoices_date ON erp_invoices(invoice_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_invoices_status ON erp_invoices(payment_status)')
        
        # ==================== CHALLANS ====================
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS erp_challans (
                id {get_text_pk()},
                user_id VARCHAR(255) NOT NULL,
                challan_number VARCHAR(50) NOT NULL,
                customer_id VARCHAR(255),
                customer_name VARCHAR(255) NOT NULL,
                challan_date DATE NOT NULL,
                items {get_jsonb()} NOT NULL,
                total_quantity INTEGER NOT NULL,
                notes TEXT,
                status VARCHAR(50) DEFAULT 'pending',
                converted_to_invoice_id VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, challan_number)
            )
        ''')
        
        # Create indexes for challans
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_challans_user ON erp_challans(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_challans_status ON erp_challans(status)')
        
        # ==================== PURCHASES ====================
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS erp_purchases (
                id {get_text_pk()},
                user_id VARCHAR(255) NOT NULL,
                vendor_id VARCHAR(255),
                vendor_name VARCHAR(255) NOT NULL,
                bill_number VARCHAR(50),
                bill_date DATE NOT NULL,
                bill_image_url TEXT,
                subtotal {get_numeric()} NOT NULL,
                tax_amount {get_numeric()} DEFAULT 0,
                total_amount {get_numeric()} NOT NULL,
                paid_amount {get_numeric()} DEFAULT 0,
                balance_amount {get_numeric()} DEFAULT 0,
                payment_status VARCHAR(50) DEFAULT 'unpaid',
                items {get_jsonb()} NOT NULL,
                notes TEXT,
                status VARCHAR(50) DEFAULT 'completed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for purchases
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_purchases_user ON erp_purchases(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_purchases_vendor ON erp_purchases(vendor_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_purchases_date ON erp_purchases(bill_date)')
        
        # ==================== PURCHASE ORDERS ====================
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS erp_purchase_orders (
                id {get_text_pk()},
                user_id VARCHAR(255) NOT NULL,
                po_number VARCHAR(50) NOT NULL,
                vendor_id VARCHAR(255),
                vendor_name VARCHAR(255) NOT NULL,
                po_date DATE NOT NULL,
                expected_delivery_date DATE,
                total_amount {get_numeric()} NOT NULL,
                items {get_jsonb()} NOT NULL,
                notes TEXT,
                status VARCHAR(50) DEFAULT 'open',
                approval_status VARCHAR(50) DEFAULT 'pending',
                approved_by VARCHAR(255),
                approved_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, po_number)
            )
        ''')
        
        # Create indexes for purchase orders
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_po_user ON erp_purchase_orders(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_po_status ON erp_purchase_orders(status)')
        
        # ==================== GRN (Goods Receipt Note) ====================
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS erp_grn (
                id {get_text_pk()},
                user_id VARCHAR(255) NOT NULL,
                grn_number VARCHAR(50) NOT NULL,
                po_id VARCHAR(255),
                vendor_name VARCHAR(255) NOT NULL,
                grn_date DATE NOT NULL,
                total_quantity INTEGER NOT NULL,
                items {get_jsonb()} NOT NULL,
                notes TEXT,
                received_by VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, grn_number)
            )
        ''')
        
        # Create indexes for GRN
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_grn_user ON erp_grn(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_grn_po ON erp_grn(po_id)')
        
        # ==================== STOCK TRANSACTIONS ====================
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS erp_stock_transactions (
                id {get_text_pk()},
                user_id VARCHAR(255) NOT NULL,
                product_id VARCHAR(255) NOT NULL,
                transaction_type VARCHAR(50) NOT NULL,
                quantity INTEGER NOT NULL,
                reference_type VARCHAR(50),
                reference_id VARCHAR(255),
                batch_number VARCHAR(100),
                notes TEXT,
                created_by VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for stock transactions
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_trans_user ON erp_stock_transactions(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_trans_product ON erp_stock_transactions(product_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_trans_date ON erp_stock_transactions(created_at)')
        
        # ==================== BATCHES ====================
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS erp_batches (
                id {get_text_pk()},
                user_id VARCHAR(255) NOT NULL,
                product_id VARCHAR(255) NOT NULL,
                product_name VARCHAR(255) NOT NULL,
                batch_number VARCHAR(100) NOT NULL,
                manufacturing_date DATE,
                expiry_date DATE,
                quantity INTEGER NOT NULL,
                cost_price {get_numeric()},
                is_expired BOOLEAN DEFAULT {get_boolean_default(False)},
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, product_id, batch_number)
            )
        ''')
        
        # Create indexes for batches
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_batches_user ON erp_batches(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_batches_product ON erp_batches(product_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_batches_expiry ON erp_batches(expiry_date)')
        
        # ==================== CRM LEADS ====================
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS erp_leads (
                id {get_text_pk()},
                user_id VARCHAR(255) NOT NULL,
                lead_name VARCHAR(255) NOT NULL,
                phone VARCHAR(20),
                email VARCHAR(255),
                source VARCHAR(100),
                status VARCHAR(50) DEFAULT 'new',
                notes TEXT,
                follow_up_date DATE,
                converted_to_customer_id VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for leads
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_leads_user ON erp_leads(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_leads_status ON erp_leads(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_leads_followup ON erp_leads(follow_up_date)')
        
        # ==================== PAYMENTS ====================
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS erp_payments (
                id {get_text_pk()},
                user_id VARCHAR(255) NOT NULL,
                payment_type VARCHAR(50) NOT NULL,
                party_type VARCHAR(50) NOT NULL,
                party_id VARCHAR(255),
                party_name VARCHAR(255) NOT NULL,
                amount {get_numeric()} NOT NULL,
                payment_mode VARCHAR(50) NOT NULL,
                payment_modes {get_jsonb()},
                reference_number VARCHAR(100),
                reference_type VARCHAR(50),
                reference_id VARCHAR(255),
                payment_date DATE NOT NULL,
                bank_id VARCHAR(255),
                status VARCHAR(50) DEFAULT 'completed',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for payments
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_payments_user ON erp_payments(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_payments_party ON erp_payments(party_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_payments_date ON erp_payments(payment_date)')
        
        # ==================== TRANSACTIONS (Income & Expense) ====================
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS erp_transactions (
                id {get_text_pk()},
                user_id VARCHAR(255) NOT NULL,
                transaction_type VARCHAR(50) NOT NULL,
                category VARCHAR(100) NOT NULL,
                amount {get_numeric()} NOT NULL,
                description TEXT,
                transaction_date DATE NOT NULL,
                payment_mode VARCHAR(50),
                reference_number VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for transactions
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_user ON erp_transactions(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_type ON erp_transactions(transaction_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_date ON erp_transactions(transaction_date)')
        
        # ==================== STAFF & OPERATORS ====================
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS erp_staff (
                id {get_text_pk()},
                user_id VARCHAR(255) NOT NULL,
                staff_name VARCHAR(255) NOT NULL,
                phone VARCHAR(20),
                email VARCHAR(255),
                role VARCHAR(50) NOT NULL,
                username VARCHAR(100),
                password_hash VARCHAR(255),
                salary {get_numeric()} DEFAULT 0,
                joining_date DATE,
                permissions {get_jsonb()},
                is_active BOOLEAN DEFAULT {get_boolean_default(True)},
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, username)
            )
        ''')
        
        # Create indexes for staff
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_staff_user ON erp_staff(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_staff_username ON erp_staff(username)')
        
        conn.commit()
        logger.info("✅ ERP tables initialized successfully")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Failed to initialize ERP tables: {e}")
        raise
    finally:
        conn.close()


def create_rls_policies():
    """
    Create Row-Level Security policies for multi-tenant data isolation
    Only applicable for PostgreSQL
    """
    db_type = get_db_type()
    
    if db_type != 'postgresql':
        logger.info("RLS policies only applicable for PostgreSQL, skipping...")
        return
    
    logger.info("Creating Row-Level Security policies...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # List of ERP tables that need RLS
    erp_tables = [
        'erp_company', 'erp_banks', 'erp_products', 'erp_customers', 'erp_vendors',
        'erp_invoices', 'erp_challans', 'erp_purchases', 'erp_purchase_orders',
        'erp_grn', 'erp_stock_transactions', 'erp_batches', 'erp_leads',
        'erp_payments', 'erp_transactions', 'erp_staff'
    ]
    
    try:
        for table in erp_tables:
            # Enable RLS on table
            cursor.execute(f'ALTER TABLE {table} ENABLE ROW LEVEL SECURITY')
            
            # Create policy for SELECT
            cursor.execute(f'''
                CREATE POLICY {table}_select_policy ON {table}
                FOR SELECT
                USING (user_id = current_setting('app.current_user_id', TRUE)::TEXT)
            ''')
            
            # Create policy for INSERT
            cursor.execute(f'''
                CREATE POLICY {table}_insert_policy ON {table}
                FOR INSERT
                WITH CHECK (user_id = current_setting('app.current_user_id', TRUE)::TEXT)
            ''')
            
            # Create policy for UPDATE
            cursor.execute(f'''
                CREATE POLICY {table}_update_policy ON {table}
                FOR UPDATE
                USING (user_id = current_setting('app.current_user_id', TRUE)::TEXT)
            ''')
            
            # Create policy for DELETE
            cursor.execute(f'''
                CREATE POLICY {table}_delete_policy ON {table}
                FOR DELETE
                USING (user_id = current_setting('app.current_user_id', TRUE)::TEXT)
            ''')
            
            logger.info(f"✅ RLS policies created for {table}")
        
        conn.commit()
        logger.info("✅ All RLS policies created successfully")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Failed to create RLS policies: {e}")
        # Don't raise - RLS is optional enhancement
    finally:
        conn.close()
