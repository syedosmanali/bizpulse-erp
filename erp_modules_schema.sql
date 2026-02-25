-- ERP NEW MODULES - Database Schema
-- Run this in your Supabase SQL editor or local SQLite

-- Company Setup
CREATE TABLE IF NOT EXISTS erp_company (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    company_name TEXT DEFAULT '',
    gst_number TEXT DEFAULT '',
    financial_year TEXT DEFAULT '',
    invoice_prefix TEXT DEFAULT 'INV',
    address TEXT DEFAULT '',
    phone TEXT DEFAULT '',
    email TEXT DEFAULT '',
    logo_url TEXT DEFAULT '',
    created_at TEXT,
    updated_at TEXT
);

-- Bank Management
CREATE TABLE IF NOT EXISTS erp_banks (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    bank_name TEXT DEFAULT '',
    account_number TEXT DEFAULT '',
    ifsc TEXT DEFAULT '',
    branch TEXT DEFAULT '',
    opening_balance NUMERIC DEFAULT 0,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TEXT
);

-- Vendor/Supplier
CREATE TABLE IF NOT EXISTS erp_vendors (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT DEFAULT '',
    phone TEXT DEFAULT '',
    email TEXT DEFAULT '',
    address TEXT DEFAULT '',
    gst_number TEXT DEFAULT '',
    outstanding_balance NUMERIC DEFAULT 0,
    created_at TEXT
);

-- Purchase Entry
CREATE TABLE IF NOT EXISTS erp_purchases (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    vendor_id TEXT DEFAULT '',
    vendor_name TEXT DEFAULT '',
    bill_number TEXT DEFAULT '',
    total_amount NUMERIC DEFAULT 0,
    tax_amount NUMERIC DEFAULT 0,
    status TEXT DEFAULT 'pending',
    items TEXT DEFAULT '[]',
    notes TEXT DEFAULT '',
    created_at TEXT
);

-- Purchase Orders
CREATE TABLE IF NOT EXISTS erp_purchase_orders (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    po_number TEXT DEFAULT '',
    vendor_id TEXT DEFAULT '',
    vendor_name TEXT DEFAULT '',
    total_amount NUMERIC DEFAULT 0,
    status TEXT DEFAULT 'pending',
    approval_status TEXT DEFAULT 'pending',
    items TEXT DEFAULT '[]',
    notes TEXT DEFAULT '',
    created_at TEXT
);

-- GRN (Goods Received Note)
CREATE TABLE IF NOT EXISTS erp_grn (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    grn_number TEXT DEFAULT '',
    po_id TEXT DEFAULT '',
    vendor_name TEXT DEFAULT '',
    total_quantity NUMERIC DEFAULT 0,
    items TEXT DEFAULT '[]',
    notes TEXT DEFAULT '',
    created_at TEXT
);

-- Batch & Expiry
CREATE TABLE IF NOT EXISTS erp_batches (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    product_id TEXT DEFAULT '',
    product_name TEXT DEFAULT '',
    batch_number TEXT DEFAULT '',
    expiry_date TEXT DEFAULT '',
    quantity NUMERIC DEFAULT 0,
    created_at TEXT
);

-- CRM Leads
CREATE TABLE IF NOT EXISTS erp_leads (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT DEFAULT '',
    phone TEXT DEFAULT '',
    email TEXT DEFAULT '',
    source TEXT DEFAULT '',
    status TEXT DEFAULT 'new',
    notes TEXT DEFAULT '',
    follow_up_date TEXT DEFAULT '',
    created_at TEXT
);

-- Payments Log
CREATE TABLE IF NOT EXISTS erp_payments_log (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    party_name TEXT DEFAULT '',
    amount NUMERIC DEFAULT 0,
    payment_mode TEXT DEFAULT 'cash',
    reference TEXT DEFAULT '',
    status TEXT DEFAULT 'completed',
    notes TEXT DEFAULT '',
    created_at TEXT
);

-- Income & Expense Transactions
CREATE TABLE IF NOT EXISTS erp_transactions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    type TEXT DEFAULT 'income',
    category TEXT DEFAULT 'Other',
    amount NUMERIC DEFAULT 0,
    description TEXT DEFAULT '',
    date TEXT DEFAULT '',
    created_at TEXT
);

-- Staff & Operators
CREATE TABLE IF NOT EXISTS erp_staff (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT DEFAULT '',
    phone TEXT DEFAULT '',
    email TEXT DEFAULT '',
    role TEXT DEFAULT 'staff',
    salary NUMERIC DEFAULT 0,
    joining_date TEXT DEFAULT '',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TEXT
);


-- Invoices
CREATE TABLE IF NOT EXISTS erp_invoices (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    invoice_number TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    invoice_date TEXT DEFAULT '',
    due_date TEXT DEFAULT '',
    subtotal NUMERIC DEFAULT 0,
    tax_amount NUMERIC DEFAULT 0,
    discount_amount NUMERIC DEFAULT 0,
    total_amount NUMERIC DEFAULT 0,
    paid_amount NUMERIC DEFAULT 0,
    balance_amount NUMERIC DEFAULT 0,
    payment_status TEXT DEFAULT 'pending',
    payment_type TEXT DEFAULT 'cash',
    status TEXT DEFAULT 'draft',
    items TEXT DEFAULT '[]',
    notes TEXT DEFAULT '',
    created_at TEXT,
    updated_at TEXT,
    UNIQUE(user_id, invoice_number)
);

-- Customers (Enhanced for invoicing)
CREATE TABLE IF NOT EXISTS erp_customers (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT DEFAULT '',
    phone TEXT DEFAULT '',
    email TEXT DEFAULT '',
    address TEXT DEFAULT '',
    gst_number TEXT DEFAULT '',
    pan_number TEXT DEFAULT '',
    credit_limit NUMERIC DEFAULT 0,
    credit_days INTEGER DEFAULT 0,
    category TEXT DEFAULT 'Regular',
    outstanding_balance NUMERIC DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
);

-- Products (Enhanced for invoicing)
CREATE TABLE IF NOT EXISTS erp_products (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    product_code TEXT DEFAULT '',
    product_name TEXT DEFAULT '',
    category TEXT DEFAULT '',
    brand TEXT DEFAULT '',
    hsn_code TEXT DEFAULT '',
    gst_rate NUMERIC DEFAULT 18.0,
    unit TEXT DEFAULT 'piece',
    cost_price NUMERIC DEFAULT 0,
    selling_price NUMERIC DEFAULT 0,
    min_stock_level NUMERIC DEFAULT 0,
    current_stock NUMERIC DEFAULT 0,
    barcode TEXT DEFAULT '',
    has_batch_tracking BOOLEAN DEFAULT FALSE,
    has_expiry_tracking BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TEXT,
    updated_at TEXT
);

-- Stock Transactions
CREATE TABLE IF NOT EXISTS erp_stock_transactions (
    id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    transaction_type TEXT DEFAULT '',
    quantity NUMERIC DEFAULT 0,
    reason TEXT DEFAULT '',
    description TEXT DEFAULT '',
    created_at TEXT
);

-- Payments (for invoice payments)
CREATE TABLE IF NOT EXISTS erp_payments (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    invoice_id TEXT DEFAULT '',
    customer_id TEXT DEFAULT '',
    bank_id TEXT DEFAULT '',
    amount NUMERIC DEFAULT 0,
    payment_method TEXT DEFAULT 'cash',
    payment_date TEXT DEFAULT '',
    reference_number TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    created_at TEXT
);

-- Invoice Sequence Tracking
CREATE TABLE IF NOT EXISTS erp_invoice_sequences (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL UNIQUE,
    last_invoice_number INTEGER DEFAULT 0,
    updated_at TEXT
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_erp_invoices_user_id ON erp_invoices(user_id);
CREATE INDEX IF NOT EXISTS idx_erp_invoices_customer_id ON erp_invoices(customer_id);
CREATE INDEX IF NOT EXISTS idx_erp_invoices_invoice_date ON erp_invoices(invoice_date);
CREATE INDEX IF NOT EXISTS idx_erp_invoices_status ON erp_invoices(status);
CREATE INDEX IF NOT EXISTS idx_erp_customers_user_id ON erp_customers(user_id);
CREATE INDEX IF NOT EXISTS idx_erp_products_user_id ON erp_products(user_id);
CREATE INDEX IF NOT EXISTS idx_erp_stock_transactions_product_id ON erp_stock_transactions(product_id);
CREATE INDEX IF NOT EXISTS idx_erp_payments_invoice_id ON erp_payments(invoice_id);
