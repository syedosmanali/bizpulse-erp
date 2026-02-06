-- ============================================================
-- BizPulse ERP - Supabase PostgreSQL Schema
-- Clean schema for fresh Supabase database
-- ============================================================

-- Drop all existing tables (if any)
DROP TABLE IF EXISTS whatsapp_reports_log CASCADE;
DROP TABLE IF EXISTS stock_alert_log CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS user_sessions CASCADE;
DROP TABLE IF EXISTS user_activity_log CASCADE;
DROP TABLE IF EXISTS user_accounts CASCADE;
DROP TABLE IF EXISTS user_roles CASCADE;
DROP TABLE IF EXISTS staff CASCADE;
DROP TABLE IF EXISTS notification_settings CASCADE;
DROP TABLE IF EXISTS cms_website_content CASCADE;
DROP TABLE IF EXISTS cms_admin_users CASCADE;
DROP TABLE IF EXISTS cms_gallery CASCADE;
DROP TABLE IF EXISTS cms_faqs CASCADE;
DROP TABLE IF EXISTS cms_testimonials CASCADE;
DROP TABLE IF EXISTS cms_pricing_plans CASCADE;
DROP TABLE IF EXISTS cms_features CASCADE;
DROP TABLE IF EXISTS cms_hero_section CASCADE;
DROP TABLE IF EXISTS cms_site_settings CASCADE;
DROP TABLE IF EXISTS invoices CASCADE;
DROP TABLE IF EXISTS companies CASCADE;
DROP TABLE IF EXISTS credit_transactions CASCADE;
DROP TABLE IF EXISTS sales CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS bill_items CASCADE;
DROP TABLE IF EXISTS bills CASCADE;
DROP TABLE IF EXISTS hotel_services CASCADE;
DROP TABLE IF EXISTS hotel_guests CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS clients CASCADE;
DROP TABLE IF EXISTS tenants CASCADE;
DROP TABLE IF EXISTS tenant_users CASCADE;
DROP TABLE IF EXISTS super_admins CASCADE;
DROP TABLE IF EXISTS inventory_movements CASCADE;
DROP TABLE IF EXISTS inventory_items CASCADE;
DROP TABLE IF EXISTS inventory_categories CASCADE;
DROP TABLE IF EXISTS stock_transactions CASCADE;
DROP TABLE IF EXISTS current_stock CASCADE;
DROP TABLE IF EXISTS product_categories CASCADE;
DROP TABLE IF EXISTS product_variants CASCADE;

-- ============================================================
-- CORE TABLES
-- ============================================================

-- Products table
CREATE TABLE products (
    id VARCHAR(255) PRIMARY KEY,
    code VARCHAR(100) UNIQUE,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    price NUMERIC(10,2),
    cost NUMERIC(10,2),
    stock INTEGER DEFAULT 0,
    min_stock INTEGER DEFAULT 0,
    unit VARCHAR(50) DEFAULT 'piece',
    business_type VARCHAR(50) DEFAULT 'both',
    barcode_data VARCHAR(255) UNIQUE,
    barcode_image TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    user_id VARCHAR(255),
    tenant_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customers table
CREATE TABLE customers (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(255),
    address TEXT,
    credit_limit NUMERIC(10,2) DEFAULT 0,
    current_balance NUMERIC(10,2) DEFAULT 0,
    total_purchases NUMERIC(10,2) DEFAULT 0,
    customer_type VARCHAR(50) DEFAULT 'regular',
    is_active BOOLEAN DEFAULT TRUE,
    user_id VARCHAR(255),
    tenant_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bills table
CREATE TABLE bills (
    id VARCHAR(255) PRIMARY KEY,
    bill_number VARCHAR(100) UNIQUE,
    customer_id VARCHAR(255),
    customer_name VARCHAR(255),
    business_type VARCHAR(50),
    subtotal NUMERIC(10,2),
    tax_amount NUMERIC(10,2),
    discount_amount NUMERIC(10,2) DEFAULT 0,
    total_amount NUMERIC(10,2),
    payment_status VARCHAR(50) DEFAULT 'paid',
    payment_method VARCHAR(50) DEFAULT 'cash',
    is_credit BOOLEAN DEFAULT FALSE,
    credit_due_date DATE,
    credit_amount NUMERIC(10,2) DEFAULT 0,
    credit_paid_amount NUMERIC(10,2) DEFAULT 0,
    credit_balance NUMERIC(10,2) DEFAULT 0,
    status VARCHAR(50) DEFAULT 'completed',
    gst_rate NUMERIC(10,2) DEFAULT 18,
    tenant_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers (id)
);

-- Bill items table
CREATE TABLE bill_items (
    id VARCHAR(255) PRIMARY KEY,
    bill_id VARCHAR(255),
    product_id VARCHAR(255),
    product_name VARCHAR(255),
    quantity INTEGER,
    unit_price NUMERIC(10,2),
    total_price NUMERIC(10,2),
    tax_rate NUMERIC(10,2) DEFAULT 18,
    tenant_id VARCHAR(255),
    FOREIGN KEY (bill_id) REFERENCES bills (id),
    FOREIGN KEY (product_id) REFERENCES products (id)
);

-- Payments table
CREATE TABLE payments (
    id VARCHAR(255) PRIMARY KEY,
    bill_id VARCHAR(255),
    method VARCHAR(50),
    amount NUMERIC(10,2),
    reference VARCHAR(255),
    tenant_id VARCHAR(255),
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bill_id) REFERENCES bills (id)
);

-- Credit Transactions table
CREATE TABLE credit_transactions (
    id VARCHAR(255) PRIMARY KEY,
    bill_id VARCHAR(255) NOT NULL,
    customer_id VARCHAR(255) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    payment_method VARCHAR(50) DEFAULT 'cash',
    reference_number VARCHAR(255),
    notes TEXT,
    created_by VARCHAR(255),
    tenant_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bill_id) REFERENCES bills (id),
    FOREIGN KEY (customer_id) REFERENCES customers (id)
);

-- Sales table
CREATE TABLE sales (
    id VARCHAR(255) PRIMARY KEY,
    bill_id VARCHAR(255),
    bill_number VARCHAR(255),
    customer_id VARCHAR(255),
    customer_name VARCHAR(255),
    product_id VARCHAR(255),
    product_name VARCHAR(255),
    category VARCHAR(100),
    quantity INTEGER,
    unit_price NUMERIC(10,2),
    total_price NUMERIC(10,2),
    tax_amount NUMERIC(10,2),
    discount_amount NUMERIC(10,2) DEFAULT 0,
    payment_method VARCHAR(50),
    balance_due NUMERIC(10,2) DEFAULT 0,
    paid_amount NUMERIC(10,2) DEFAULT 0,
    sale_date DATE,
    sale_time TIME,
    tenant_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bill_id) REFERENCES bills (id),
    FOREIGN KEY (customer_id) REFERENCES customers (id),
    FOREIGN KEY (product_id) REFERENCES products (id)
);

-- ============================================================
-- HOTEL MANAGEMENT
-- ============================================================

-- Hotel guests table
CREATE TABLE hotel_guests (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(255),
    address TEXT,
    id_proof VARCHAR(255),
    room_number VARCHAR(50),
    room_type VARCHAR(50),
    check_in_date DATE,
    check_out_date DATE,
    guest_count INTEGER DEFAULT 1,
    total_bill NUMERIC(10,2) DEFAULT 0,
    status VARCHAR(50) DEFAULT 'booked',
    tenant_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Hotel services table
CREATE TABLE hotel_services (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    rate NUMERIC(10,2),
    description TEXT,
    tax_rate NUMERIC(10,2) DEFAULT 18,
    is_active BOOLEAN DEFAULT TRUE,
    tenant_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- USER MANAGEMENT
-- ============================================================

-- Users table (authentication)
CREATE TABLE users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    business_name VARCHAR(255),
    business_address TEXT,
    business_type VARCHAR(50) DEFAULT 'retail',
    gst_number VARCHAR(100),
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Clients table
CREATE TABLE clients (
    id VARCHAR(255) PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255) UNIQUE NOT NULL,
    contact_name VARCHAR(255),
    phone_number VARCHAR(20),
    whatsapp_number VARCHAR(20),
    business_address TEXT,
    business_type VARCHAR(50) DEFAULT 'retail',
    gst_number VARCHAR(100),
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    profile_picture TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(20),
    country VARCHAR(100) DEFAULT 'India',
    pan_number VARCHAR(50),
    website VARCHAR(255),
    date_of_birth VARCHAR(50),
    language VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(100) DEFAULT 'Asia/Kolkata',
    currency VARCHAR(10) DEFAULT 'INR',
    date_format VARCHAR(50) DEFAULT 'DD/MM/YYYY',
    last_login TIMESTAMP,
    login_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Roles table
CREATE TABLE user_roles (
    id VARCHAR(255) PRIMARY KEY,
    client_id VARCHAR(255) NOT NULL,
    role_name VARCHAR(100) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    permissions TEXT NOT NULL DEFAULT '{}',
    is_system_role BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(client_id, role_name),
    FOREIGN KEY (client_id) REFERENCES clients (id)
);

-- User Accounts table
CREATE TABLE user_accounts (
    id VARCHAR(255) PRIMARY KEY,
    client_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    mobile VARCHAR(20) NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    temp_password VARCHAR(255),
    role_id VARCHAR(255) NOT NULL,
    department VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active',
    force_password_change BOOLEAN DEFAULT TRUE,
    module_permissions TEXT DEFAULT '{}',
    last_login TIMESTAMP,
    login_count INTEGER DEFAULT 0,
    failed_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients (id),
    FOREIGN KEY (role_id) REFERENCES user_roles (id)
);

-- User Activity Log table
CREATE TABLE user_activity_log (
    id VARCHAR(255) PRIMARY KEY,
    client_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    module VARCHAR(100) NOT NULL,
    action VARCHAR(100) NOT NULL,
    details TEXT,
    ip_address VARCHAR(50),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients (id),
    FOREIGN KEY (user_id) REFERENCES user_accounts (id)
);

-- User Sessions table
CREATE TABLE user_sessions (
    id VARCHAR(255) PRIMARY KEY,
    client_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(50),
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients (id),
    FOREIGN KEY (user_id) REFERENCES user_accounts (id)
);

-- Staff table
CREATE TABLE staff (
    id VARCHAR(255) PRIMARY KEY,
    business_owner_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(100) NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (business_owner_id) REFERENCES clients (id)
);

-- ============================================================
-- TENANT MANAGEMENT
-- ============================================================

-- Tenants table
CREATE TABLE tenants (
    id VARCHAR(255) PRIMARY KEY,
    tenant_id VARCHAR(255) UNIQUE NOT NULL,
    business_name VARCHAR(255) NOT NULL,
    owner_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    plan_type VARCHAR(50) DEFAULT 'basic',
    plan_expiry_date DATE,
    subscription_status VARCHAR(50) DEFAULT 'active',
    status VARCHAR(50) DEFAULT 'active',
    is_active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(255),
    last_login TIMESTAMP,
    login_count INTEGER DEFAULT 0,
    failed_login_attempts INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tenant Users table
CREATE TABLE tenant_users (
    id VARCHAR(255) PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'USER',
    department VARCHAR(100),
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    permissions TEXT DEFAULT '{}',
    last_login TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants (tenant_id)
);

-- Super Admin Users table
CREATE TABLE super_admins (
    id VARCHAR(255) PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'SUPER_ADMIN',
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- CMS TABLES
-- ============================================================

-- CMS Site Settings table
CREATE TABLE cms_site_settings (
    id SERIAL PRIMARY KEY,
    site_name VARCHAR(255) DEFAULT 'BizPulse ERP',
    logo_url TEXT,
    favicon_url TEXT,
    primary_color VARCHAR(50) DEFAULT '#732C3F',
    secondary_color VARCHAR(50) DEFAULT '#F7E8EC',
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    address TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CMS Hero Section table
CREATE TABLE cms_hero_section (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) DEFAULT 'Welcome to BizPulse',
    subtitle VARCHAR(255) DEFAULT 'Complete Business Management Solution',
    button_text VARCHAR(100) DEFAULT 'Get Started',
    button_link VARCHAR(255) DEFAULT '/register',
    background_image_url TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CMS Features table
CREATE TABLE cms_features (
    id VARCHAR(255) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    icon_image_url TEXT,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CMS Pricing Plans table
CREATE TABLE cms_pricing_plans (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price_per_month NUMERIC(10,2) NOT NULL,
    description TEXT,
    features TEXT,
    is_popular BOOLEAN DEFAULT FALSE,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CMS Testimonials table
CREATE TABLE cms_testimonials (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(100),
    company VARCHAR(255),
    message TEXT NOT NULL,
    avatar_image_url TEXT,
    rating INTEGER DEFAULT 5,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CMS FAQs table
CREATE TABLE cms_faqs (
    id VARCHAR(255) PRIMARY KEY,
    question VARCHAR(500) NOT NULL,
    answer TEXT NOT NULL,
    category VARCHAR(100) DEFAULT 'General',
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CMS Gallery table
CREATE TABLE cms_gallery (
    id VARCHAR(255) PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    image_url TEXT NOT NULL,
    category VARCHAR(100) DEFAULT 'General',
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CMS Admin Users table
CREATE TABLE cms_admin_users (
    id VARCHAR(255) PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CMS Website Content table
CREATE TABLE cms_website_content (
    id SERIAL PRIMARY KEY,
    page_name VARCHAR(100) DEFAULT 'index',
    content_html TEXT NOT NULL,
    edited_by VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- COMPANIES & INVOICES
-- ============================================================

-- Companies table
CREATE TABLE companies (
    id VARCHAR(255) PRIMARY KEY,
    business_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    whatsapp_number VARCHAR(20),
    email VARCHAR(255),
    address TEXT,
    send_daily_report BOOLEAN DEFAULT TRUE,
    report_time TIME DEFAULT '23:55:00',
    timezone VARCHAR(100) DEFAULT 'Asia/Kolkata',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Invoices table
CREATE TABLE invoices (
    id VARCHAR(255) PRIMARY KEY,
    company_id VARCHAR(255) DEFAULT 'default_company',
    invoice_number VARCHAR(100) UNIQUE,
    customer_id VARCHAR(255),
    invoice_date DATE DEFAULT CURRENT_DATE,
    due_date DATE,
    subtotal NUMERIC(10,2) DEFAULT 0,
    tax_amount NUMERIC(10,2) DEFAULT 0,
    discount_amount NUMERIC(10,2) DEFAULT 0,
    total_amount NUMERIC(10,2) DEFAULT 0,
    total_cost NUMERIC(10,2) DEFAULT 0,
    profit_amount NUMERIC(10,2) DEFAULT 0,
    payment_status VARCHAR(50) DEFAULT 'pending',
    notes TEXT,
    tenant_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies (id),
    FOREIGN KEY (customer_id) REFERENCES customers (id)
);

-- WhatsApp Reports Log table
CREATE TABLE whatsapp_reports_log (
    id VARCHAR(255) PRIMARY KEY,
    company_id VARCHAR(255) NOT NULL,
    report_date DATE NOT NULL,
    report_type VARCHAR(50) DEFAULT 'daily_sales',
    whatsapp_number VARCHAR(20),
    pdf_filename VARCHAR(255),
    media_id VARCHAR(255),
    message_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    total_sales NUMERIC(10,2) DEFAULT 0,
    total_profit NUMERIC(10,2) DEFAULT 0,
    total_invoices INTEGER DEFAULT 0,
    error_message TEXT,
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies (id)
);

-- ============================================================
-- NOTIFICATIONS
-- ============================================================

-- Notifications table
CREATE TABLE notifications (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'info',
    message TEXT NOT NULL,
    action_url TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    tenant_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Notification Settings table
CREATE TABLE notification_settings (
    id VARCHAR(255) PRIMARY KEY,
    client_id VARCHAR(255) NOT NULL UNIQUE,
    low_stock_enabled BOOLEAN DEFAULT TRUE,
    low_stock_threshold INTEGER DEFAULT 5,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients (id)
);

-- Stock Alert Log table
CREATE TABLE stock_alert_log (
    id VARCHAR(255) PRIMARY KEY,
    client_id VARCHAR(255) NOT NULL,
    product_id VARCHAR(255) NOT NULL,
    alert_date DATE NOT NULL,
    stock_level INTEGER NOT NULL,
    threshold_level INTEGER NOT NULL,
    tenant_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients (id),
    FOREIGN KEY (product_id) REFERENCES products (id)
);

-- ============================================================
-- INVENTORY MANAGEMENT
-- ============================================================

-- Inventory Categories table
CREATE TABLE inventory_categories (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    parent_id VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    tenant_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inventory Items table
CREATE TABLE inventory_items (
    id VARCHAR(255) PRIMARY KEY,
    category_id VARCHAR(255),
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(100) UNIQUE,
    description TEXT,
    unit VARCHAR(50) DEFAULT 'piece',
    current_stock NUMERIC(10,2) DEFAULT 0,
    min_stock NUMERIC(10,2) DEFAULT 0,
    max_stock NUMERIC(10,2),
    unit_cost NUMERIC(10,2) DEFAULT 0,
    unit_price NUMERIC(10,2) DEFAULT 0,
    location VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    tenant_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES inventory_categories (id)
);

-- Inventory Movements table
CREATE TABLE inventory_movements (
    id VARCHAR(255) PRIMARY KEY,
    item_id VARCHAR(255) NOT NULL,
    movement_type VARCHAR(50) NOT NULL,
    quantity NUMERIC(10,2) NOT NULL,
    unit_cost NUMERIC(10,2),
    reference_type VARCHAR(50),
    reference_id VARCHAR(255),
    notes TEXT,
    created_by VARCHAR(255),
    tenant_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES inventory_items (id)
);

-- ============================================================
-- ADDITIONAL TABLES
-- ============================================================

-- Stock Transactions table
CREATE TABLE stock_transactions (
    id VARCHAR(255) PRIMARY KEY,
    product_id VARCHAR(255) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    reference_type VARCHAR(50),
    reference_id VARCHAR(255),
    notes TEXT,
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products (id)
);

-- Current Stock table
CREATE TABLE current_stock (
    id VARCHAR(255) PRIMARY KEY,
    product_id VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products (id)
);

-- Product Categories table
CREATE TABLE product_categories (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    parent_id VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product Variants table
CREATE TABLE product_variants (
    id VARCHAR(255) PRIMARY KEY,
    product_id VARCHAR(255) NOT NULL,
    variant_name VARCHAR(255) NOT NULL,
    sku VARCHAR(100) UNIQUE,
    price NUMERIC(10,2),
    cost NUMERIC(10,2),
    stock INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products (id)
);

-- ============================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================

CREATE INDEX idx_products_code ON products(code);
CREATE INDEX idx_products_barcode ON products(barcode_data);
CREATE INDEX idx_customers_phone ON customers(phone);
CREATE INDEX idx_bills_bill_number ON bills(bill_number);
CREATE INDEX idx_bills_customer_id ON bills(customer_id);
CREATE INDEX idx_bills_created_at ON bills(created_at);
CREATE INDEX idx_sales_sale_date ON sales(sale_date);
CREATE INDEX idx_sales_customer_id ON sales(customer_id);
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_user_accounts_client_id ON user_accounts(client_id);
CREATE INDEX idx_user_accounts_username ON user_accounts(username);

-- ============================================================
-- INITIAL DATA
-- ============================================================

-- Insert default CMS settings
INSERT INTO cms_site_settings (site_name, primary_color, secondary_color)
VALUES ('BizPulse ERP', '#732C3F', '#F7E8EC');

-- Insert default CMS hero section
INSERT INTO cms_hero_section (title, subtitle, button_text, button_link)
VALUES ('Welcome to BizPulse', 'Complete Business Management Solution', 'Get Started', '/register');

-- Insert default CMS admin user (username: admin, password: admin123)
INSERT INTO cms_admin_users (id, username, password_hash, email, full_name)
VALUES (
    'cms-admin-1',
    'admin',
    '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',
    'admin@bizpulse.com',
    'CMS Administrator'
);

-- ============================================================
-- SCHEMA CREATION COMPLETE
-- ============================================================

SELECT 'Schema created successfully!' AS status;
