"""
Database connection and initialization utilities
UPDATED: Now uses Supabase PostgreSQL for persistent cloud storage
"""

import uuid
import hashlib
from datetime import datetime, timedelta
import os
import json
import sqlite3
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get absolute path to database file (for SQLite fallback only)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'billing.db')

def get_database_url():
    """Get DATABASE_URL from environment variables (Supabase PostgreSQL)"""
    return os.environ.get('DATABASE_URL')

def get_db_type():
    """Determine database type - always PostgreSQL for production"""
    return 'postgresql' if get_database_url() else 'sqlite'

def get_db_connection():
    """
    Get database connection to Supabase PostgreSQL.
    - Production/Supabase: PostgreSQL connection (persistent cloud storage)
    - Local fallback: SQLite (only for development without Supabase)
    """
    db_url = get_database_url()
    
    if db_url:
        # Supabase PostgreSQL connection
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            # Parse DATABASE_URL
            parsed = urlparse(db_url)
            
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                user=parsed.username,
                password=parsed.password,
                database=parsed.path[1:],  # Remove leading '/'
                cursor_factory=RealDictCursor,
                sslmode='require'  # Supabase requires SSL
            )
            conn.autocommit = False
            print("✅ Connected to Supabase PostgreSQL")
            return conn
        except Exception as e:
            print(f"❌ Supabase PostgreSQL connection failed: {e}")
            raise
    else:
        # SQLite fallback (local development only)
        import sqlite3
        print("⚠️  Using SQLite fallback (local development)")
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def generate_id():
    return str(uuid.uuid4())

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_current_client_id():
    """Get the current client ID from session, handling both client and employee sessions"""
    from flask import session
    user_type = session.get('user_type')
    if user_type == 'employee':
        return session.get('client_id')  # For employees, use client_id
    else:
        return session.get('user_id')    # For clients, use user_id

def init_db():
    """Initialize database - supports both SQLite and PostgreSQL"""
    db_type = get_db_type()
    print(f"📁 Initializing {db_type.upper()} database...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Helper function to get appropriate SQL syntax
    def get_sql_type(sqlite_type, postgres_type):
        return postgres_type if db_type == 'postgresql' else sqlite_type
    
    def get_autoincrement():
        return 'SERIAL PRIMARY KEY' if db_type == 'postgresql' else 'INTEGER PRIMARY KEY AUTOINCREMENT'
    
    def get_text_pk():
        return 'VARCHAR(255) PRIMARY KEY' if db_type == 'postgresql' else 'TEXT PRIMARY KEY'
    
    def get_boolean_default(value):
        return str(value).upper() if db_type == 'postgresql' else str(int(value))
    
    # Products table
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS products (
            id {get_text_pk()},
            code VARCHAR(100) UNIQUE,
            name VARCHAR(255) NOT NULL,
            category VARCHAR(100),
            price {get_sql_type('REAL', 'NUMERIC(10,2)')},
            cost {get_sql_type('REAL', 'NUMERIC(10,2)')},
            stock INTEGER DEFAULT 0,
            min_stock INTEGER DEFAULT 0,
            unit VARCHAR(50) DEFAULT 'piece',
            business_type VARCHAR(50) DEFAULT 'both',
            barcode_data VARCHAR(255) UNIQUE,
            barcode_image TEXT,
            is_active BOOLEAN DEFAULT {get_boolean_default(True)},
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Customers table
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS customers (
            id {get_text_pk()},
            name VARCHAR(255) NOT NULL,
            phone VARCHAR(20),
            email VARCHAR(255),
            address TEXT,
            credit_limit {get_sql_type('REAL', 'NUMERIC(10,2)')} DEFAULT 0,
            current_balance {get_sql_type('REAL', 'NUMERIC(10,2)')} DEFAULT 0,
            total_purchases {get_sql_type('REAL', 'NUMERIC(10,2)')} DEFAULT 0,
            customer_type VARCHAR(50) DEFAULT 'regular',
            is_active BOOLEAN DEFAULT {get_boolean_default(True)},
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Bills table
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS bills (
            id {get_text_pk()},
            bill_number VARCHAR(100) UNIQUE,
            customer_id VARCHAR(255),
            customer_name VARCHAR(255),
            business_type VARCHAR(50),
            subtotal {get_sql_type('REAL', 'NUMERIC(10,2)')},
            tax_amount {get_sql_type('REAL', 'NUMERIC(10,2)')},
            discount_amount {get_sql_type('REAL', 'NUMERIC(10,2)')} DEFAULT 0,
            total_amount {get_sql_type('REAL', 'NUMERIC(10,2)')},
            payment_status VARCHAR(50) DEFAULT 'paid',
            payment_method VARCHAR(50) DEFAULT 'cash',
            is_credit BOOLEAN DEFAULT {get_boolean_default(False)},
            credit_due_date DATE,
            credit_amount {get_sql_type('REAL', 'NUMERIC(10,2)')} DEFAULT 0,
            credit_paid_amount {get_sql_type('REAL', 'NUMERIC(10,2)')} DEFAULT 0,
            credit_balance {get_sql_type('REAL', 'NUMERIC(10,2)')} DEFAULT 0,
            status VARCHAR(50) DEFAULT 'completed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    ''')
    
    # Credit Transactions table - for tracking credit payments
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS credit_transactions (
            id TEXT PRIMARY KEY,
            bill_id TEXT NOT NULL,
            customer_id TEXT NOT NULL,
            transaction_type TEXT NOT NULL, -- 'payment', 'adjustment', 'interest'
            amount REAL NOT NULL,
            payment_method TEXT DEFAULT 'cash',
            reference_number TEXT,
            notes TEXT,
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bill_id) REFERENCES bills (id),
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    ''')
    
    # Bill items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bill_items (
            id TEXT PRIMARY KEY,
            bill_id TEXT,
            product_id TEXT,
            product_name TEXT,
            quantity INTEGER,
            unit_price REAL,
            total_price REAL,
            tax_rate REAL DEFAULT 18,
            FOREIGN KEY (bill_id) REFERENCES bills (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Payments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id TEXT PRIMARY KEY,
            bill_id TEXT,
            method TEXT,
            amount REAL,
            reference TEXT,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bill_id) REFERENCES bills (id)
        )
    ''')
    
    # Sales table - for tracking all sales transactions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id TEXT PRIMARY KEY,
            bill_id TEXT,
            bill_number TEXT,
            customer_id TEXT,
            customer_name TEXT,
            product_id TEXT,
            product_name TEXT,
            category TEXT,
            quantity INTEGER,
            unit_price REAL,
            total_price REAL,
            tax_amount REAL,
            discount_amount REAL DEFAULT 0,
            payment_method TEXT,
            balance_due REAL DEFAULT 0,
            paid_amount REAL DEFAULT 0,
            sale_date DATE,
            sale_time TIME,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bill_id) REFERENCES bills (id),
            FOREIGN KEY (customer_id) REFERENCES customers (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Hotel guests table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hotel_guests (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT,
            id_proof TEXT,
            room_number TEXT,
            room_type TEXT,
            check_in_date DATE,
            check_out_date DATE,
            guest_count INTEGER DEFAULT 1,
            total_bill REAL DEFAULT 0,
            status TEXT DEFAULT 'booked',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Hotel services table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hotel_services (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            rate REAL,
            description TEXT,
            tax_rate REAL DEFAULT 18,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Users table for authentication
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            business_name TEXT,
            business_address TEXT,
            business_type TEXT DEFAULT 'retail',
            gst_number TEXT,
            phone TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # ==================== CLIENT MANAGEMENT TABLES ====================
    
    # Tenants table - Main client accounts managed by super admin
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tenants (
            id TEXT PRIMARY KEY,
            tenant_id TEXT UNIQUE NOT NULL,
            business_name TEXT NOT NULL,
            owner_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            address TEXT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            plan_type TEXT DEFAULT 'basic',
            plan_expiry_date DATE,
            subscription_status TEXT DEFAULT 'active',
            status TEXT DEFAULT 'active',
            is_active BOOLEAN DEFAULT 1,
            created_by TEXT,
            last_login TIMESTAMP,
            login_count INTEGER DEFAULT 0,
            failed_login_attempts INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tenant Users table - Users created by tenant admins
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tenant_users (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'USER',
            department TEXT,
            phone TEXT,
            is_active BOOLEAN DEFAULT 1,
            permissions TEXT DEFAULT '{}',
            last_login TIMESTAMP,
            created_by TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tenant_id) REFERENCES tenants (tenant_id)
        )
    ''')
    
    # Super Admin Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS super_admins (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT DEFAULT 'SUPER_ADMIN',
            is_active BOOLEAN DEFAULT 1,
            last_login TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # ==================== NEW USER MANAGEMENT SYSTEM ====================
    
    # Initialize user management tables
    from modules.user_management.models import UserManagementModels
    UserManagementModels.create_user_tables()
    
    # Add permissions column if it doesn't exist
    UserManagementModels.add_permissions_column()
    
    # Clients table - for client management system
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id TEXT PRIMARY KEY,
            company_name TEXT NOT NULL,
            contact_email TEXT UNIQUE NOT NULL,
            contact_name TEXT,
            phone_number TEXT,
            whatsapp_number TEXT,
            business_address TEXT,
            business_type TEXT DEFAULT 'retail',
            gst_number TEXT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            last_login TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add password_plain column if it doesn't exist (for existing databases)
    if db_type == 'sqlite':
        try:
            cursor.execute('ALTER TABLE client_users ADD COLUMN password_plain TEXT')
        except sqlite3.OperationalError:
            # Column already exists
            pass
        except Exception:
            # Table doesn't exist yet
            pass
    else:
        try:
            cursor.execute('ALTER TABLE client_users ADD COLUMN password_plain TEXT')
        except Exception:
            # Column already exists or table doesn't exist
            pass
    
    # Add tenant_id column to existing tables if they don't exist
    tables_to_add_tenant_id = [
        'products', 'customers', 'bills', 'bill_items', 'payments', 'sales',
        'hotel_guests', 'hotel_services', 'credit_transactions', 'invoices',
        'notifications', 'inventory_items', 'inventory_categories', 'inventory_movements'
    ]
    
    for table in tables_to_add_tenant_id:
        try:
            if db_type == 'sqlite':
                cursor.execute(f'ALTER TABLE {table} ADD COLUMN tenant_id TEXT')
            else:
                cursor.execute(f'ALTER TABLE {table} ADD COLUMN tenant_id VARCHAR(255)')
            print(f"✅ Added tenant_id to {table}")
        except Exception:
            # Column already exists or table doesn't exist
            pass
    
    # Add user_id column to existing tables if they don't exist (for backward compatibility)
    try:
        if db_type == 'sqlite':
            cursor.execute('ALTER TABLE products ADD COLUMN user_id TEXT')
        else:
            cursor.execute('ALTER TABLE products ADD COLUMN user_id VARCHAR(255)')
    except Exception:
        pass
    
    try:
        if db_type == 'sqlite':
            cursor.execute('ALTER TABLE customers ADD COLUMN user_id TEXT')
        else:
            cursor.execute('ALTER TABLE customers ADD COLUMN user_id VARCHAR(255)')
    except Exception:
        pass
    
    # Add additional columns to clients table if they don't exist
    try:
        cursor.execute('ALTER TABLE clients ADD COLUMN city TEXT')
        cursor.execute('ALTER TABLE clients ADD COLUMN state TEXT')
        cursor.execute('ALTER TABLE clients ADD COLUMN country TEXT DEFAULT "India"')
        cursor.execute('ALTER TABLE clients ADD COLUMN login_count INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        # Columns already exist
        pass
        pass
    
    # Add profile_picture column to clients table if it doesn't exist
    try:
        cursor.execute('ALTER TABLE clients ADD COLUMN profile_picture TEXT')
    except sqlite3.OperationalError:
        # Column already exists
        pass
    
    # Add additional profile columns to clients table if they don't exist
    additional_client_columns = [
        ('city', 'TEXT'),
        ('state', 'TEXT'),
        ('pincode', 'TEXT'),
        ('country', 'TEXT DEFAULT "India"'),
        ('pan_number', 'TEXT'),
        ('website', 'TEXT'),
        ('date_of_birth', 'TEXT'),
        ('language', 'TEXT DEFAULT "en"'),
        ('timezone', 'TEXT DEFAULT "Asia/Kolkata"'),
        ('currency', 'TEXT DEFAULT "INR"'),
        ('date_format', 'TEXT DEFAULT "DD/MM/YYYY"'),
        ('last_login', 'TIMESTAMP'),
        ('login_count', 'INTEGER DEFAULT 0')
    ]
    
    for column_name, column_type in additional_client_columns:
        try:
            cursor.execute(f'ALTER TABLE clients ADD COLUMN {column_name} {column_type}')
        except sqlite3.OperationalError:
            # Column already exists
            pass
    
    # Add missing columns to existing tables if they don't exist
    try:
        cursor.execute('ALTER TABLE bills ADD COLUMN customer_name TEXT')
    except sqlite3.OperationalError:
        # Column already exists
        pass
    
    try:
        cursor.execute('ALTER TABLE bills ADD COLUMN gst_rate REAL DEFAULT 18')
    except sqlite3.OperationalError:
        # Column already exists
        pass
    
    try:
        cursor.execute('ALTER TABLE sales ADD COLUMN balance_due REAL DEFAULT 0')
    except sqlite3.OperationalError:
        # Column already exists
        pass
    
    try:
        cursor.execute('ALTER TABLE sales ADD COLUMN paid_amount REAL DEFAULT 0')
    except sqlite3.OperationalError:
        # Column already exists
        pass
    
    # Add barcode fields to products table if they don't exist
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN barcode_data TEXT UNIQUE')
    except sqlite3.OperationalError:
        pass
    
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN barcode_image TEXT')
    except sqlite3.OperationalError:
        pass
    
    # Create index on barcode_data for fast lookups
    try:
        cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode_data)')
    except sqlite3.OperationalError:
        pass
    
    # CMS Tables for Content Management
    
    # Site Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cms_site_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site_name TEXT DEFAULT 'BizPulse ERP',
            logo_url TEXT,
            favicon_url TEXT,
            primary_color TEXT DEFAULT '#732C3F',
            secondary_color TEXT DEFAULT '#F7E8EC',
            contact_email TEXT,
            contact_phone TEXT,
            address TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Hero Section table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cms_hero_section (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT DEFAULT 'Welcome to BizPulse',
            subtitle TEXT DEFAULT 'Complete Business Management Solution',
            button_text TEXT DEFAULT 'Get Started',
            button_link TEXT DEFAULT '/register',
            background_image_url TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Features table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cms_features (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            icon_image_url TEXT,
            display_order INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Pricing Plans table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cms_pricing_plans (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price_per_month REAL NOT NULL,
            description TEXT,
            features TEXT,
            is_popular BOOLEAN DEFAULT 0,
            display_order INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Testimonials table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cms_testimonials (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            role TEXT,
            company TEXT,
            message TEXT NOT NULL,
            avatar_image_url TEXT,
            rating INTEGER DEFAULT 5,
            display_order INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # FAQs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cms_faqs (
            id TEXT PRIMARY KEY,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            category TEXT DEFAULT 'General',
            display_order INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Gallery Images table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cms_gallery (
            id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            image_url TEXT NOT NULL,
            category TEXT DEFAULT 'General',
            display_order INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # CMS Admin Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cms_admin_users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            full_name TEXT,
            is_active BOOLEAN DEFAULT 1,
            last_login TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Website Content table - stores edited website HTML
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cms_website_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_name TEXT DEFAULT 'index',
            content_html TEXT NOT NULL,
            edited_by TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Companies table - for multi-tenant support and WhatsApp reports
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id TEXT PRIMARY KEY,
            business_name TEXT NOT NULL,
            phone_number TEXT,
            whatsapp_number TEXT,
            email TEXT,
            address TEXT,
            send_daily_report BOOLEAN DEFAULT 1,
            report_time TIME DEFAULT '23:55:00',
            timezone TEXT DEFAULT 'Asia/Kolkata',
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Update invoices table to include company_id and cost tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id TEXT PRIMARY KEY,
            company_id TEXT DEFAULT 'default_company',
            invoice_number TEXT UNIQUE,
            customer_id TEXT,
            invoice_date DATE DEFAULT CURRENT_DATE,
            due_date DATE,
            subtotal REAL DEFAULT 0,
            tax_amount REAL DEFAULT 0,
            discount_amount REAL DEFAULT 0,
            total_amount REAL DEFAULT 0,
            total_cost REAL DEFAULT 0,
            profit_amount REAL DEFAULT 0,
            payment_status TEXT DEFAULT 'pending',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id),
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    ''')
    
    # WhatsApp Reports Log table - track sent reports
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS whatsapp_reports_log (
            id TEXT PRIMARY KEY,
            company_id TEXT NOT NULL,
            report_date DATE NOT NULL,
            report_type TEXT DEFAULT 'daily_sales',
            whatsapp_number TEXT,
            pdf_filename TEXT,
            media_id TEXT,
            message_id TEXT,
            status TEXT DEFAULT 'pending',
            total_sales REAL DEFAULT 0,
            total_profit REAL DEFAULT 0,
            total_invoices INTEGER DEFAULT 0,
            error_message TEXT,
            sent_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    ''')
    

    
    # Initialize default CMS data
    cursor.execute('SELECT COUNT(*) FROM cms_site_settings')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO cms_site_settings (site_name, primary_color, secondary_color)
            VALUES ('BizPulse ERP', '#732C3F', '#F7E8EC')
        ''')
    
    cursor.execute('SELECT COUNT(*) FROM cms_hero_section')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO cms_hero_section (title, subtitle, button_text, button_link)
            VALUES ('Welcome to BizPulse', 'Complete Business Management Solution', 'Get Started', '/register')
        ''')
    
    # Initialize default CMS admin user
    cursor.execute('SELECT COUNT(*) FROM cms_admin_users')
    if cursor.fetchone()[0] == 0:
        # Default credentials: username=admin, password=admin123
        default_password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute('''
            INSERT INTO cms_admin_users (id, username, password_hash, email, full_name)
            VALUES (?, ?, ?, ?, ?)
        ''', (generate_id(), 'admin', default_password_hash, 'admin@bizpulse.com', 'CMS Administrator'))
    
    # Staff table for business owners to add their staff
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS staff (
            id TEXT PRIMARY KEY,
            business_owner_id TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            role TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (business_owner_id) REFERENCES clients (id)
        )
    ''')

    # Notifications table for user notifications
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            type TEXT NOT NULL DEFAULT 'info',
            message TEXT NOT NULL,
            action_url TEXT,
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create index for faster notification queries
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at)')
    except sqlite3.OperationalError:
        pass

    # Notification Settings table for client-specific notification preferences
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notification_settings (
            id TEXT PRIMARY KEY,
            client_id TEXT NOT NULL UNIQUE,
            low_stock_enabled INTEGER DEFAULT 1,
            low_stock_threshold INTEGER DEFAULT 5,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients (id)
        )
    ''')
    
    # Stock Alert Log table to track sent alerts (prevent duplicate alerts)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_alert_log (
            id TEXT PRIMARY KEY,
            client_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            alert_date DATE NOT NULL,
            stock_level INTEGER NOT NULL,
            threshold_level INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients (id),
            FOREIGN KEY (product_id) REFERENCES products (id),
            UNIQUE(client_id, product_id, alert_date)
        )
    ''')
    
    # Create indexes for performance
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notification_settings_client_id ON notification_settings(client_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_alert_log_client_product_date ON stock_alert_log(client_id, product_id, alert_date)')
    except sqlite3.OperationalError:
        pass

    # Initialize default company
    cursor.execute('SELECT COUNT(*) FROM companies')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO companies (id, business_name, phone_number, whatsapp_number, email, address, send_daily_report, report_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('default_company', 'BizPulse Demo Store', '7093635305', '7093635305', 'bizpulse.erp@gmail.com', 'Hyderabad, Telangana, India', 1, '23:55:00'))
    
    # Add BizPulse admin user if not exists
    if db_type == 'sqlite':
        cursor.execute('SELECT COUNT(*) FROM users WHERE email = ?', ('bizpulse.erp@gmail.com',))
    else:
        cursor.execute('SELECT COUNT(*) FROM users WHERE email = %s', ('bizpulse.erp@gmail.com',))
    
    if cursor.fetchone()[0] == 0:
        if db_type == 'sqlite':
            cursor.execute('''
                INSERT INTO users (id, first_name, last_name, email, business_name, business_type, password_hash, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', ('admin-bizpulse', 'BizPulse', 'Admin', 'bizpulse.erp@gmail.com', 'BizPulse ERP', 'software', hash_password('demo123'), 1, datetime.now().isoformat()))
        else:
            cursor.execute('''
                INSERT INTO users (id, first_name, last_name, email, business_name, business_type, password_hash, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', ('admin-bizpulse', 'BizPulse', 'Admin', 'bizpulse.erp@gmail.com', 'BizPulse ERP', 'software', hash_password('demo123'), True, datetime.now().isoformat()))
    
    # Add sample data
    if db_type == 'sqlite':
        cursor.execute('SELECT COUNT(*) FROM products')
    else:
        cursor.execute('SELECT COUNT(*) FROM products')
    
    if cursor.fetchone()[0] == 0:
        # Sample products
        sample_products = [
            ('prod-1', 'P001', 'Rice (1kg)', 'Groceries', 80.0, 70.0, 100, 10, 'kg', 'retail'),
            ('prod-2', 'P002', 'Wheat Flour (1kg)', 'Groceries', 45.0, 40.0, 50, 5, 'kg', 'retail'),
            ('prod-3', 'P003', 'Sugar (1kg)', 'Groceries', 55.0, 50.0, 30, 5, 'kg', 'retail'),
            ('prod-4', 'P004', 'Tea Powder (250g)', 'Beverages', 120.0, 100.0, 25, 3, 'packet', 'retail'),
            ('prod-5', 'P005', 'Cooking Oil (1L)', 'Groceries', 150.0, 140.0, 20, 2, 'liter', 'retail'),
            ('prod-6', 'P006', 'Milk (1L)', 'Dairy', 60.0, 55.0, 15, 2, 'liter', 'retail'),
            ('prod-7', 'P007', 'Bread', 'Bakery', 25.0, 20.0, 40, 5, 'piece', 'retail'),
            ('prod-8', 'P008', 'Eggs (12 pcs)', 'Dairy', 84.0, 75.0, 30, 3, 'dozen', 'retail'),
            ('prod-9', 'P009', 'Onions (1kg)', 'Vegetables', 35.0, 30.0, 50, 5, 'kg', 'retail'),
            ('prod-10', 'P010', 'Potatoes (1kg)', 'Vegetables', 25.0, 20.0, 60, 10, 'kg', 'retail')
        ]
        
        placeholder = '?' if db_type == 'sqlite' else '%s'
        for product in sample_products:
            cursor.execute(f'''
                INSERT INTO products (id, code, name, category, price, cost, stock, min_stock, unit, business_type)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            ''', product)
    
    # Sample customers
    if db_type == 'sqlite':
        cursor.execute('SELECT COUNT(*) FROM customers')
    else:
        cursor.execute('SELECT COUNT(*) FROM customers')
        
    if cursor.fetchone()[0] == 0:
        sample_customers = [
            ('cust-1', 'Rajesh Kumar', '+91 9876543210', 'rajesh@email.com', '123 Main Street, City', 5000.0),
            ('cust-2', 'Priya Sharma', '+91 9876543211', 'priya@email.com', '456 Park Avenue, City', 3000.0),
            ('cust-3', 'Amit Singh', '+91 9876543212', 'amit@email.com', '789 Garden Road, City', 2000.0),
            ('cust-4', 'Sunita Devi', '+91 9876543213', 'sunita@email.com', '321 Market Street, City', 4000.0),
            ('cust-5', 'Vikram Patel', '+91 9876543214', 'vikram@email.com', '654 Commercial Area, City', 6000.0)
        ]
        
        placeholder = '?' if db_type == 'sqlite' else '%s'
        for customer in sample_customers:
            cursor.execute(f'''
                INSERT INTO customers (id, name, phone, email, address, credit_limit)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            ''', customer)
    
    conn.commit()
    conn.close()
    
    print(f"✅ {db_type.upper()} database initialized successfully!")