# GST Calculation Fix - Documentation

## Problem
The GST calculation was applying discount **before** calculating GST, which resulted in incorrect totals.

### Example of Wrong Calculation:
```
Product Price: ₹100
Discount: -₹9
After Discount: ₹91
CGST (9%): ₹8.19
SGST (9%): ₹8.19
Grand Total: ₹107.38 ❌ WRONG
```

### Expected Correct Calculation:
```
Product Price: ₹100
CGST (9%): ₹9.00
SGST (9%): ₹9.00
Subtotal with GST: ₹118
Discount: -₹9
Grand Total: ₹109.00 ✅ CORRECT
```

## Solution
Changed the calculation order to:
1. Calculate GST on **original subtotal** (before discount)
2. Add GST to subtotal
3. Apply discount on **total amount** (including GST)

## Files Modified

### 1. `frontend/screens/templates/retail_billing.html`
**Changed:**
- Line ~988: GST calculation logic in `updateCartTotals()` function
- Line ~1156: GST calculation logic in checkout function

**Old Code:**
```javascript
const subtotalAfterDiscount = subtotal - discountAmount;
const cgst = subtotalAfterDiscount * 0.09;
const sgst = subtotalAfterDiscount * 0.09;
const grandTotal = subtotalAfterDiscount + cgst + sgst;
```

**New Code:**
```javascript
const cgst = subtotal * 0.09;
const sgst = subtotal * 0.09;
const subtotalWithGst = subtotal + cgst + sgst;
const grandTotal = subtotalWithGst - discountAmount;
```

### 2. `frontend/assets/static/js/billing-premium.js`
**Changed:**
- Line ~606: GST calculation logic in `updateBillingSummary()` method

**Old Code:**
```javascript
const taxableAmount = this.subtotal + additionalCharges - this.discountAmount;
const cgst = Math.round(taxableAmount * 0.09);
const sgst = Math.round(taxableAmount * 0.09);
const totalGst = cgst + sgst;
const grandTotal = taxableAmount + totalGst;
```

**New Code:**
```javascript
const taxableAmount = this.subtotal + additionalCharges;
const cgst = Math.round(taxableAmount * 0.09);
const sgst = Math.round(taxableAmount * 0.09);
const totalGst = cgst + sgst;
const subtotalWithGst = taxableAmount + totalGst;
const grandTotal = subtotalWithGst - this.discountAmount;
```

## Test Cases

### Test Case 1: Simple Product
- **Product Price:** ₹100
- **Discount:** ₹9
- **Expected Result:**
  - CGST: ₹9.00
  - SGST: ₹9.00
  - Grand Total: ₹109.00

### Test Case 2: From Screenshot
- **Product Price:** ₹450
- **Discount:** ₹31
- **Expected Result:**
  - CGST: ₹40.50
  - SGST: ₹40.50
  - Grand Total: ₹500.00

### Test Case 3: Percentage Discount
- **Product Price:** ₹1000
- **Discount:** 10% (₹118 on total)
- **Expected Result:**
  - CGST: ₹90.00
  - SGST: ₹90.00
  - Grand Total: ₹1062.00

## Impact
- ✅ GST now calculated correctly on original amount
- ✅ Discount applied on final amount (including GST)
- ✅ Both fixed amount and percentage discounts work correctly
- ✅ Works for both retail billing and premium billing

## Testing
1. Open billing page
2. Add a product worth ₹100
3. Apply discount of ₹9
4. Verify:
   - CGST shows ₹9.00
   - SGST shows ₹9.00
   - Grand Total shows ₹109.00

## Notes
- This follows standard GST calculation practice where tax is calculated on the base amount
- Discount is a reduction on the final invoice amount (including taxes)
- Both CGST and SGST are calculated at 9% each (total 18% GST)
