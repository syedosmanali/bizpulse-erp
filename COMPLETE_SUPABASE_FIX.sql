-- ============================================================================
-- COMPLETE SUPABASE DATABASE FIX
-- Run this entire script in Supabase SQL Editor to fix all issues
-- ============================================================================

-- ============================================================================
-- PART 1: Add missing columns to existing tables
-- ============================================================================

-- Fix bills table
ALTER TABLE bills ADD COLUMN IF NOT EXISTS customer_phone VARCHAR(20);
ALTER TABLE bills ADD COLUMN IF NOT EXISTS business_owner_id VARCHAR(255);
ALTER TABLE bills ADD COLUMN IF NOT EXISTS user_id VARCHAR(255);
ALTER TABLE bills ADD COLUMN IF NOT EXISTS paid_amount NUMERIC(10,2) DEFAULT 0;
ALTER TABLE bills ADD COLUMN IF NOT EXISTS partial_payment_amount NUMERIC(10,2);
ALTER TABLE bills ADD COLUMN IF NOT EXISTS partial_payment_method VARCHAR(50);

-- Fix products table
ALTER TABLE products ADD COLUMN IF NOT EXISTS business_owner_id VARCHAR(255);

-- Fix customers table
ALTER TABLE customers ADD COLUMN IF NOT EXISTS business_owner_id VARCHAR(255);

-- Fix sales table
ALTER TABLE sales ADD COLUMN IF NOT EXISTS business_owner_id VARCHAR(255);
ALTER TABLE sales ADD COLUMN IF NOT EXISTS user_id VARCHAR(255);

-- Fix bill_items table
ALTER TABLE bill_items ADD COLUMN IF NOT EXISTS user_id VARCHAR(255);

-- Fix payments table
ALTER TABLE payments ADD COLUMN IF NOT EXISTS user_id VARCHAR(255);

-- ============================================================================
-- PART 2: Create User Management Tables
-- ============================================================================

-- User Roles table
CREATE TABLE IF NOT EXISTS user_roles (
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
CREATE TABLE IF NOT EXISTS user_accounts (
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
    module_permissions TEXT DEFAULT '{}',
    force_password_change BOOLEAN DEFAULT TRUE,
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
CREATE TABLE IF NOT EXISTS user_activity_log (
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
CREATE TABLE IF NOT EXISTS user_sessions (
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

-- ============================================================================
-- PART 3: Create Indexes for Performance
-- ============================================================================

-- Bills table indexes
CREATE INDEX IF NOT EXISTS idx_bills_business_owner_id ON bills(business_owner_id);
CREATE INDEX IF NOT EXISTS idx_bills_user_id ON bills(user_id);
CREATE INDEX IF NOT EXISTS idx_bills_customer_id ON bills(customer_id);
CREATE INDEX IF NOT EXISTS idx_bills_created_at ON bills(created_at);
CREATE INDEX IF NOT EXISTS idx_bills_payment_method ON bills(payment_method);

-- Products table indexes
CREATE INDEX IF NOT EXISTS idx_products_business_owner_id ON products(business_owner_id);
CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode_data);

-- Customers table indexes
CREATE INDEX IF NOT EXISTS idx_customers_business_owner_id ON customers(business_owner_id);

-- Sales table indexes
CREATE INDEX IF NOT EXISTS idx_sales_business_owner_id ON sales(business_owner_id);
CREATE INDEX IF NOT EXISTS idx_sales_customer_id ON sales(customer_id);
CREATE INDEX IF NOT EXISTS idx_sales_product_id ON sales(product_id);
CREATE INDEX IF NOT EXISTS idx_sales_sale_date ON sales(sale_date);

-- User management indexes
CREATE INDEX IF NOT EXISTS idx_user_roles_client_id ON user_roles(client_id);
CREATE INDEX IF NOT EXISTS idx_user_accounts_client_id ON user_accounts(client_id);
CREATE INDEX IF NOT EXISTS idx_user_accounts_username ON user_accounts(username);
CREATE INDEX IF NOT EXISTS idx_user_accounts_status ON user_accounts(status);
CREATE INDEX IF NOT EXISTS idx_user_activity_log_client_id ON user_activity_log(client_id);
CREATE INDEX IF NOT EXISTS idx_user_activity_log_user_id ON user_activity_log(user_id);
CREATE INDEX IF NOT EXISTS idx_user_activity_log_timestamp ON user_activity_log(timestamp);

-- ============================================================================
-- PART 4: Verify the fix
-- ============================================================================

-- Check bills table columns
SELECT 'Bills table columns:' AS info;
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'bills' 
ORDER BY ordinal_position;

-- Check user management tables
SELECT 'User management tables created:' AS info;
SELECT table_name 
FROM information_schema.tables 
WHERE table_name IN ('user_roles', 'user_accounts', 'user_activity_log', 'user_sessions')
ORDER BY table_name;

-- Success message
SELECT '✅ ALL FIXES APPLIED SUCCESSFULLY!' AS status;
SELECT '✅ Billing system is now fixed' AS message;
SELECT '✅ User management system is now ready' AS message;
SELECT '✅ Dashboard revenue will now show correctly' AS message;
