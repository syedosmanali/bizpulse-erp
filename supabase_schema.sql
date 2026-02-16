-- Supabase Database Schema for BizPulse ERP
-- Run this in Supabase SQL Editor to create all tables

-- Products table
CREATE TABLE IF NOT EXISTS products (
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
    business_owner_id VARCHAR(255),
    barcode_data VARCHAR(255) UNIQUE,
    barcode_image TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tenant_id VARCHAR(255),
    user_id VARCHAR(255)
);

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(255),
    address TEXT,
    business_owner_id VARCHAR(255),
    credit_limit NUMERIC(10,2) DEFAULT 0,
    current_balance NUMERIC(10,2) DEFAULT 0,
    total_purchases NUMERIC(10,2) DEFAULT 0,
    customer_type VARCHAR(50) DEFAULT 'regular',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tenant_id VARCHAR(255),
    user_id VARCHAR(255)
);

-- Bills table
CREATE TABLE IF NOT EXISTS bills (
    id VARCHAR(255) PRIMARY KEY,
    bill_number VARCHAR(100) UNIQUE,
    customer_id VARCHAR(255),
    customer_name VARCHAR(255),
    customer_phone VARCHAR(20),
    business_type VARCHAR(50),
    business_owner_id VARCHAR(255),
    user_id VARCHAR(255),
    subtotal NUMERIC(10,2),
    tax_amount NUMERIC(10,2),
    discount_amount NUMERIC(10,2) DEFAULT 0,
    total_amount NUMERIC(10,2),
    payment_status VARCHAR(50) DEFAULT 'paid',
    payment_method VARCHAR(50) DEFAULT 'cash',
    paid_amount NUMERIC(10,2) DEFAULT 0,
    partial_payment_amount NUMERIC(10,2),
    partial_payment_method VARCHAR(50),
    is_credit BOOLEAN DEFAULT FALSE,
    credit_due_date DATE,
    credit_amount NUMERIC(10,2) DEFAULT 0,
    credit_paid_amount NUMERIC(10,2) DEFAULT 0,
    credit_balance NUMERIC(10,2) DEFAULT 0,
    status VARCHAR(50) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    gst_rate NUMERIC(10,2) DEFAULT 18,
    tenant_id VARCHAR(255),
    FOREIGN KEY (customer_id) REFERENCES customers (id)
);

-- Bill items table
CREATE TABLE IF NOT EXISTS bill_items (
    id VARCHAR(255) PRIMARY KEY,
    bill_id VARCHAR(255),
    product_id VARCHAR(255),
    product_name VARCHAR(255),
    quantity INTEGER,
    unit_price NUMERIC(10,2),
    total_price NUMERIC(10,2),
    tax_rate NUMERIC(10,2) DEFAULT 18,
    tenant_id VARCHAR(255),
    user_id VARCHAR(255),
    FOREIGN KEY (bill_id) REFERENCES bills (id),
    FOREIGN KEY (product_id) REFERENCES products (id)
);

-- Payments table
CREATE TABLE IF NOT EXISTS payments (
    id VARCHAR(255) PRIMARY KEY,
    bill_id VARCHAR(255),
    method VARCHAR(50),
    amount NUMERIC(10,2),
    reference VARCHAR(255),
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tenant_id VARCHAR(255),
    user_id VARCHAR(255),
    FOREIGN KEY (bill_id) REFERENCES bills (id)
);

-- Sales table
CREATE TABLE IF NOT EXISTS sales (
    id VARCHAR(255) PRIMARY KEY,
    bill_id VARCHAR(255),
    bill_number VARCHAR(255),
    customer_id VARCHAR(255),
    customer_name VARCHAR(255),
    product_id VARCHAR(255),
    product_name VARCHAR(255),
    category VARCHAR(255),
    quantity INTEGER,
    unit_price NUMERIC(10,2),
    total_price NUMERIC(10,2),
    tax_amount NUMERIC(10,2),
    discount_amount NUMERIC(10,2) DEFAULT 0,
    payment_method VARCHAR(255),
    balance_due NUMERIC(10,2) DEFAULT 0,
    paid_amount NUMERIC(10,2) DEFAULT 0,
    business_owner_id VARCHAR(255),
    sale_date DATE,
    sale_time TIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tenant_id VARCHAR(255),
    user_id VARCHAR(255),
    FOREIGN KEY (bill_id) REFERENCES bills (id),
    FOREIGN KEY (customer_id) REFERENCES customers (id),
    FOREIGN KEY (product_id) REFERENCES products (id)
);

-- Credit Transactions table
CREATE TABLE IF NOT EXISTS credit_transactions (
    id VARCHAR(255) PRIMARY KEY,
    bill_id VARCHAR(255) NOT NULL,
    customer_id VARCHAR(255) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    payment_method VARCHAR(50) DEFAULT 'cash',
    reference_number VARCHAR(255),
    notes TEXT,
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tenant_id VARCHAR(255),
    FOREIGN KEY (bill_id) REFERENCES bills (id),
    FOREIGN KEY (customer_id) REFERENCES customers (id)
);

-- Users table
CREATE TABLE IF NOT EXISTS users (
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
CREATE TABLE IF NOT EXISTS clients (
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
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    city VARCHAR(255),
    state VARCHAR(255),
    country VARCHAR(255) DEFAULT 'India',
    login_count INTEGER DEFAULT 0,
    profile_picture TEXT,
    pincode VARCHAR(20),
    pan_number VARCHAR(50),
    website VARCHAR(255),
    date_of_birth VARCHAR(50),
    language VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(100) DEFAULT 'Asia/Kolkata',
    currency VARCHAR(10) DEFAULT 'INR',
    date_format VARCHAR(50) DEFAULT 'DD/MM/YYYY'
);

-- Companies table
CREATE TABLE IF NOT EXISTS companies (
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

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'info',
    message TEXT NOT NULL,
    action_url VARCHAR(255),
    is_read INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tenant_id VARCHAR(255)
);

-- Notification Settings table
CREATE TABLE IF NOT EXISTS notification_settings (
    id VARCHAR(255) PRIMARY KEY,
    client_id VARCHAR(255) NOT NULL UNIQUE,
    low_stock_enabled INTEGER DEFAULT 1,
    low_stock_threshold INTEGER DEFAULT 5,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients (id)
);

-- Stock Alert Log table
CREATE TABLE IF NOT EXISTS stock_alert_log (
    id VARCHAR(255) PRIMARY KEY,
    client_id VARCHAR(255) NOT NULL,
    product_id VARCHAR(255) NOT NULL,
    alert_date DATE NOT NULL,
    stock_level INTEGER NOT NULL,
    threshold_level INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tenant_id VARCHAR(255)
);

-- Inventory Categories table
CREATE TABLE IF NOT EXISTS inventory_categories (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    parent_id VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tenant_id VARCHAR(255)
);

-- Inventory Items table
CREATE TABLE IF NOT EXISTS inventory_items (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(100) UNIQUE,
    category_id VARCHAR(255),
    description TEXT,
    unit VARCHAR(50) DEFAULT 'piece',
    min_stock_level INTEGER DEFAULT 0,
    max_stock_level INTEGER,
    reorder_point INTEGER,
    unit_cost NUMERIC(10,2),
    selling_price NUMERIC(10,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tenant_id VARCHAR(255),
    FOREIGN KEY (category_id) REFERENCES inventory_categories (id)
);

-- Inventory Movements table
CREATE TABLE IF NOT EXISTS inventory_movements (
    id VARCHAR(255) PRIMARY KEY,
    item_id VARCHAR(255) NOT NULL,
    movement_type VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    reference_type VARCHAR(50),
    reference_id VARCHAR(255),
    notes TEXT,
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tenant_id VARCHAR(255),
    FOREIGN KEY (item_id) REFERENCES inventory_items (id)
);

-- Stock Transactions table
CREATE TABLE IF NOT EXISTS stock_transactions (
    id VARCHAR(255) PRIMARY KEY,
    product_id VARCHAR(255) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    reference_type VARCHAR(50),
    reference_id VARCHAR(255),
    notes TEXT,
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tenant_id VARCHAR(255),
    FOREIGN KEY (product_id) REFERENCES products (id)
);

-- Current Stock table
CREATE TABLE IF NOT EXISTS current_stock (
    id VARCHAR(255) PRIMARY KEY,
    product_id VARCHAR(255) NOT NULL UNIQUE,
    quantity INTEGER NOT NULL DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tenant_id VARCHAR(255),
    FOREIGN KEY (product_id) REFERENCES products (id)
);

-- Product Categories table
CREATE TABLE IF NOT EXISTS product_categories (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    parent_id VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tenant_id VARCHAR(255)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode_data);
CREATE INDEX IF NOT EXISTS idx_products_business_owner_id ON products(business_owner_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);
CREATE INDEX IF NOT EXISTS idx_bills_customer_id ON bills(customer_id);
CREATE INDEX IF NOT EXISTS idx_bills_business_owner_id ON bills(business_owner_id);
CREATE INDEX IF NOT EXISTS idx_bills_user_id ON bills(user_id);
CREATE INDEX IF NOT EXISTS idx_customers_business_owner_id ON customers(business_owner_id);
CREATE INDEX IF NOT EXISTS idx_sales_customer_id ON sales(customer_id);
CREATE INDEX IF NOT EXISTS idx_sales_product_id ON sales(product_id);
CREATE INDEX IF NOT EXISTS idx_sales_business_owner_id ON sales(business_owner_id);

-- Success message
SELECT 'Database schema created successfully!' AS status;
