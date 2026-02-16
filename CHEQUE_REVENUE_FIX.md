# Cheque Revenue Fix

## Problem
The dashboard was showing revenue and net profit for uncashed cheques (cheques with `payment_status = 'cheque_deposited'`). This is incorrect because revenue should only be counted when the cheque is actually cleared and the money is received.

## Solution
Modified the revenue and profit calculations in `modules/retail/service.py` to exclude payments from bills with `payment_status = 'cheque_deposited'`.

## Changes Made

### 1. Today's Revenue Calculation
- **PostgreSQL**: Added condition `AND b.payment_status != 'cheque_deposited'` to payment revenue query
- **SQLite**: Added condition `AND b.payment_status != 'cheque_deposited'` to payment revenue query

### 2. Today's Profit Calculation
- **PostgreSQL**: Added condition `AND b.payment_status != 'cheque_deposited'` to both cash profit and payment profit queries
- **SQLite**: Added condition `AND b.payment_status != 'cheque_deposited'` to both cash profit and payment profit queries

### 3. Yesterday's Revenue & Profit (for comparison)
- Added the same exclusion condition to yesterday's calculations for consistency

### 4. Week's Revenue
- Changed from counting `total_amount` from bills to counting actual payments
- Added condition `AND b.payment_status != 'cheque_deposited'`

### 5. Month's Revenue
- Changed from counting `total_amount` from bills to counting actual payments
- Added condition `AND b.payment_status != 'cheque_deposited'`

## Expected Behavior

### Before Clearing Cheque
- **Revenue**: ₹0 (cheque not yet cleared)
- **Profit**: ₹0 (cheque not yet cleared)
- **Sales**: Shows total amount (includes credit/cheque bills)
- **Receivable**: Shows the pending cheque amount

### After Clearing Cheque
When you call the `/api/credit/cheque-cleared` endpoint with `action: 'cleared'`:
- Bill `payment_status` changes from `'cheque_deposited'` to `'paid'`
- **Revenue**: Now includes the cheque amount
- **Profit**: Now includes the profit from the cheque bill

### If Cheque Bounces
When you call the `/api/credit/cheque-cleared` endpoint with `action: 'bounced'`:
- Bill `payment_status` changes to `'cheque_bounced'`
- **Revenue**: Remains ₹0
- **Receivable**: Shows the bounced amount as pending

## Testing
Run the test script to verify the fix:
```bash
python test_cheque_revenue_fix.py
```

## Files Modified
- `modules/retail/service.py` - Updated `get_dashboard_stats()` method
