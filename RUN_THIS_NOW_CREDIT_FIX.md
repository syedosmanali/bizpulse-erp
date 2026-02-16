# 🚨 URGENT: Fix Credit & Partial Payment Billing

## 🐛 Current Error:
```
table credit_transactions has no column named amount
```

## ✅ THE FIX (Takes 1 minute):

### Step 1: Open Supabase SQL Editor
1. Go to: **https://supabase.com/dashboard**
2. Select your **BizPulse project**
3. Click **SQL Editor** → **New Query**

### Step 2: Copy and Run This SQL

```sql
-- Create credit_transactions table if it doesn't exist
CREATE TABLE IF NOT EXISTS credit_transactions (
    id VARCHAR(255) PRIMARY KEY,
    bill_id VARCHAR(255) NOT NULL,
    customer_id VARCHAR(255) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    amount NUMERIC(10,2) NOT NULL DEFAULT 0,
    payment_method VARCHAR(50) DEFAULT 'cash',
    reference_number VARCHAR(255),
    notes TEXT,
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tenant_id VARCHAR(255),
    FOREIGN KEY (bill_id) REFERENCES bills (id),
    FOREIGN KEY (customer_id) REFERENCES customers (id)
);

-- Add missing amount column (this fixes the error)
ALTER TABLE credit_transactions ADD COLUMN IF NOT EXISTS amount NUMERIC(10,2) NOT NULL DEFAULT 0;

-- Add other missing columns
ALTER TABLE credit_transactions ADD COLUMN IF NOT EXISTS payment_method VARCHAR(50) DEFAULT 'cash';
ALTER TABLE credit_transactions ADD COLUMN IF NOT EXISTS reference_number VARCHAR(255);
ALTER TABLE credit_transactions ADD COLUMN IF NOT EXISTS notes TEXT;
ALTER TABLE credit_transactions ADD COLUMN IF NOT EXISTS created_by VARCHAR(255);
ALTER TABLE credit_transactions ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255);

-- Ensure bills table has credit columns
ALTER TABLE bills ADD COLUMN IF NOT EXISTS is_credit BOOLEAN DEFAULT FALSE;
ALTER TABLE bills ADD COLUMN IF NOT EXISTS credit_amount NUMERIC(10,2) DEFAULT 0;
ALTER TABLE bills ADD COLUMN IF NOT EXISTS credit_paid_amount NUMERIC(10,2) DEFAULT 0;
ALTER TABLE bills ADD COLUMN IF NOT EXISTS credit_balance NUMERIC(10,2) DEFAULT 0;
ALTER TABLE bills ADD COLUMN IF NOT EXISTS credit_due_date DATE;
ALTER TABLE bills ADD COLUMN IF NOT EXISTS partial_payment_amount NUMERIC(10,2);
ALTER TABLE bills ADD COLUMN IF NOT EXISTS partial_payment_method VARCHAR(50);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_credit_transactions_bill_id ON credit_transactions(bill_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_customer_id ON credit_transactions(customer_id);

-- Success message
SELECT '✅ Credit & Partial Payment Billing Fixed!' AS status;
```

### Step 3: Click "RUN"
- Wait 5 seconds
- You should see: "✅ Credit & Partial Payment Billing Fixed!"

### Step 4: Test Immediately
1. Go to: **https://bizpulse24.com/retail/billing**
2. Create a bill with **Credit** payment method
3. Create a bill with **Partial Payment**
4. Both should work now!

---

## 🎯 What This Fixes:

✅ Credit bills will work
✅ Partial payment bills will work
✅ credit_transactions table will have all required columns
✅ No more "amount column missing" error

---

## ⏰ DO THIS NOW!

This is a 1-minute fix. Just run the SQL in Supabase and test immediately!

🚀 No deployment needed - works instantly after running SQL!
