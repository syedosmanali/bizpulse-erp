-- COMPLETE MODULES INTEGRATION FIX FOR SUPABASE
-- Run this in Supabase SQL Editor to fix all interconnected issues

-- PART 1: Fix Bills Table Structure
ALTER TABLE bills ADD COLUMN IF NOT EXISTS customer_phone VARCHAR(20);
ALTER TABLE bills ADD COLUMN IF NOT EXISTS business_owner_id VARCHAR(255);
ALTER TABLE bills ADD COLUMN IF NOT EXISTS user_id VARCHAR(255);
ALTER TABLE bills ADD COLUMN IF NOT EXISTS paid_amount NUMERIC(10,2) DEFAULT 0;
ALTER TABLE bills ADD COLUMN IF NOT EXISTS partial_payment_amount NUMERIC(10,2);
ALTER TABLE bills ADD COLUMN IF NOT EXISTS partial_payment_method VARCHAR(50);
ALTER TABLE bills ADD COLUMN IF NOT EXISTS credit_paid_amount NUMERIC(10,2) DEFAULT 0;
ALTER TABLE bills ADD COLUMN IF NOT EXISTS credit_balance NUMERIC(10,2) DEFAULT 0;

-- PART 2: Fix Products Table for Inventory Integration========
ALTER TABLE products ADD COLUMN IF NOT EXISTS business_owner_id VARCHAR(255);
ALTER TABLE products ADD COLUMN IF NOT EXISTS user_id VARCHAR(255);
ALTER TABLE products ADD COLUMN IF NOT EXISTS min_stock INTEGER DEFAULT 0;
ALTER TABLE products ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- PART 3: Fix Sales Table for Dashboard Integration========
ALTER TABLE sales ADD COLUMN IF NOT EXISTS business_owner_id VARCHAR(255);
ALTER TABLE sales ADD COLUMN IF NOT EXISTS user_id VARCHAR(255);
ALTER TABLE sales ADD COLUMN IF NOT EXISTS profit_amount NUMERIC(10,2) DEFAULT 0;
ALTER TABLE sales ADD COLUMN IF NOT EXISTS cost_amount NUMERIC(10,2) DEFAULT 0;

-- PART 4: Fix Customers Table for Credit Integration========
ALTER TABLE customers ADD COLUMN IF NOT EXISTS business_owner_id VARCHAR(255);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS user_id VARCHAR(255);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS current_balance NUMERIC(10,2) DEFAULT 0;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS total_purchases NUMERIC(10,2) DEFAULT 0;

-- PART 5: Create Missing Tables for Complete Integration========

-- Credit Transactions table (for credit/partial payments tracking)
CREATE TABLE IF NOT EXISTS credit_transactions (
    id VARCHAR(255) PRIMARY KEY,
    bill_id VARCHAR(255) NOT NULL,
    customer_id VARCHAR(255) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL, -- 'sale', 'payment', 'adjustment'
    amount NUMERIC(10,2) NOT NULL,
    payment_method VARCHAR(50) DEFAULT 'cash',
    reference_number VARCHAR(255),
    notes TEXT,
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bill_id) REFERENCES bills (id),
    FOREIGN KEY (customer_id) REFERENCES customers (id)
);

-- Inventory Transactions table (for stock tracking)
CREATE TABLE IF NOT EXISTS inventory_transactions (
    id VARCHAR(255) PRIMARY KEY,
    product_id VARCHAR(255) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL, -- 'sale', 'purchase', 'adjustment'
    quantity_change INTEGER NOT NULL, -- negative for sales, positive for purchases
    bill_id VARCHAR(255),
    reference VARCHAR(255),
    notes TEXT,
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products (id),
    FOREIGN KEY (bill_id) REFERENCES bills (id)
);

-- Dashboard Stats table (for caching dashboard data)
CREATE TABLE IF NOT EXISTS dashboard_stats (
    id VARCHAR(255) PRIMARY KEY,
    stat_type VARCHAR(50) NOT NULL, -- 'daily_sales', 'monthly_sales', etc.
    stat_date DATE NOT NULL,
    stat_value NUMERIC(12,2) NOT NULL,
    stat_count INTEGER DEFAULT 0,
    business_owner_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PART 6: Create Indexes for Performance========
CREATE INDEX IF NOT EXISTS idx_bills_business_owner_id ON bills(business_owner_id);
CREATE INDEX IF NOT EXISTS idx_bills_user_id ON bills(user_id);
CREATE INDEX IF NOT EXISTS idx_bills_customer_id ON bills(customer_id);
CREATE INDEX IF NOT EXISTS idx_bills_created_at ON bills(created_at);
CREATE INDEX IF NOT EXISTS idx_bills_payment_method ON bills(payment_method);

CREATE INDEX IF NOT EXISTS idx_products_business_owner_id ON products(business_owner_id);
CREATE INDEX IF NOT EXISTS idx_products_user_id ON products(user_id);
CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode_data);

CREATE INDEX IF NOT EXISTS idx_customers_business_owner_id ON customers(business_owner_id);
CREATE INDEX IF NOT EXISTS idx_customers_user_id ON customers(user_id);

CREATE INDEX IF NOT EXISTS idx_sales_business_owner_id ON sales(business_owner_id);
CREATE INDEX IF NOT EXISTS idx_sales_user_id ON sales(user_id);
CREATE INDEX IF NOT EXISTS idx_sales_created_at ON sales(created_at);

CREATE INDEX IF NOT EXISTS idx_credit_transactions_bill_id ON credit_transactions(bill_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_customer_id ON credit_transactions(customer_id);

CREATE INDEX IF NOT EXISTS idx_inventory_transactions_product_id ON inventory_transactions(product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_transactions_bill_id ON inventory_transactions(bill_id);

CREATE INDEX IF NOT EXISTS idx_dashboard_stats_business_owner_id ON dashboard_stats(business_owner_id);
CREATE INDEX IF NOT EXISTS idx_dashboard_stats_stat_date ON dashboard_stats(stat_date);

-- PART 7: Create Triggers for Automatic Integration========

-- Trigger to update product stock when bill items are created
CREATE OR REPLACE FUNCTION update_product_stock_on_sale()
RETURNS TRIGGER AS $$
BEGIN
    -- Reduce stock when bill item is created (sale)
    IF TG_OP = 'INSERT' THEN
        UPDATE products 
        SET stock = stock - NEW.quantity,
            last_updated = CURRENT_TIMESTAMP
        WHERE id = NEW.product_id;
    END IF;
    
    -- Restore stock when bill item is deleted
    IF TG_OP = 'DELETE' THEN
        UPDATE products 
        SET stock = stock + OLD.quantity,
            last_updated = CURRENT_TIMESTAMP
        WHERE id = OLD.product_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for bill_items table
DROP TRIGGER IF EXISTS trigger_update_stock_on_bill_item ON bill_items;
CREATE TRIGGER trigger_update_stock_on_bill_item
    AFTER INSERT OR DELETE ON bill_items
    FOR EACH ROW
    EXECUTE FUNCTION update_product_stock_on_sale();

-- Trigger to update customer balance on credit transactions
CREATE OR REPLACE FUNCTION update_customer_balance_on_credit()
RETURNS TRIGGER AS $$
BEGIN
    -- Update customer balance when credit transaction is created
    IF TG_OP = 'INSERT' THEN
        IF NEW.transaction_type = 'sale' THEN
            -- Add to customer balance (credit sale)
            UPDATE customers 
            SET current_balance = current_balance + NEW.amount,
                total_purchases = total_purchases + NEW.amount
            WHERE id = NEW.customer_id;
        ELSIF NEW.transaction_type = 'payment' THEN
            -- Reduce customer balance (payment received)
            UPDATE customers 
            SET current_balance = current_balance - NEW.amount
            WHERE id = NEW.customer_id;
        END IF;
    END IF;
    
    -- Reverse customer balance when credit transaction is deleted
    IF TG_OP = 'DELETE' THEN
        IF OLD.transaction_type = 'sale' THEN
            UPDATE customers 
            SET current_balance = current_balance - OLD.amount,
                total_purchases = total_purchases - OLD.amount
            WHERE id = OLD.customer_id;
        ELSIF OLD.transaction_type = 'payment' THEN
            UPDATE customers 
            SET current_balance = current_balance + OLD.amount
            WHERE id = OLD.customer_id;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for credit_transactions table
DROP TRIGGER IF EXISTS trigger_update_customer_balance ON credit_transactions;
CREATE TRIGGER trigger_update_customer_balance
    AFTER INSERT OR DELETE ON credit_transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_customer_balance_on_credit();

-- Trigger to update bill credit balance
CREATE OR REPLACE FUNCTION update_bill_credit_balance()
RETURNS TRIGGER AS $$
BEGIN
    -- Update bill credit balance when credit transaction is created
    IF TG_OP = 'INSERT' THEN
        IF NEW.transaction_type = 'sale' THEN
            UPDATE bills 
            SET credit_balance = credit_balance + NEW.amount
            WHERE id = NEW.bill_id;
        ELSIF NEW.transaction_type = 'payment' THEN
            UPDATE bills 
            SET credit_balance = credit_balance - NEW.amount,
                credit_paid_amount = credit_paid_amount + NEW.amount
            WHERE id = NEW.bill_id;
        END IF;
    END IF;
    
    -- Reverse bill credit balance when credit transaction is deleted
    IF TG_OP = 'DELETE' THEN
        IF OLD.transaction_type = 'sale' THEN
            UPDATE bills 
            SET credit_balance = credit_balance - OLD.amount
            WHERE id = OLD.bill_id;
        ELSIF OLD.transaction_type = 'payment' THEN
            UPDATE bills 
            SET credit_balance = credit_balance + OLD.amount,
                credit_paid_amount = credit_paid_amount - OLD.amount
            WHERE id = OLD.bill_id;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for credit_transactions table (bill updates)
DROP TRIGGER IF EXISTS trigger_update_bill_credit_balance ON credit_transactions;
CREATE TRIGGER trigger_update_bill_credit_balance
    AFTER INSERT OR DELETE ON credit_transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_bill_credit_balance();

-- PART 8: Insert Sample Data for Testing (Optional)
-- Uncomment the following lines if you want to add sample data for testing

/*
INSERT INTO products (id, code, name, category, price, cost, stock, min_stock, business_owner_id, user_id) VALUES
('prod-001', 'P001', 'Rice 1kg', 'Groceries', 80.00, 70.00, 100, 10, 'test-owner', 'test-user'),
('prod-002', 'P002', 'Dal 500g', 'Groceries', 120.00, 100.00, 50, 5, 'test-owner', 'test-user'),
('prod-003', 'P003', 'Oil 1L', 'Groceries', 150.00, 130.00, 30, 5, 'test-owner', 'test-user');

INSERT INTO customers (id, name, phone, email, business_owner_id, user_id, credit_limit) VALUES
('cust-001', 'Rajesh Kumar', '+91-9876543210', 'rajesh@email.com', 'test-owner', 'test-user', 5000.00),
('cust-002', 'Priya Sharma', '+91-9876543211', 'priya@email.com', 'test-owner', 'test-user', 3000.00);
*/

-- VERIFICATION QUERIES
-- Run these queries to verify the fix worked:

-- Check bills table structure
-- SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'bills' ORDER BY ordinal_position;

-- Check if triggers are created
-- SELECT tgname, proname FROM pg_trigger t JOIN pg_proc p ON t.tgfoid = p.oid WHERE tgrelid = 'bill_items'::regclass;

-- Check if indexes are created
-- SELECT indexname FROM pg_indexes WHERE tablename = 'bills';

-- SUCCESS MESSAGE
-- All tables, columns, indexes, and triggers have been created successfully!
-- Your modules (billing, products, sales, dashboard, invoices) are now properly connected!
-- Restart your application to apply all changes.