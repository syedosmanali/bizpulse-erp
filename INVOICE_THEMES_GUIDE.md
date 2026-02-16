# 📄 Invoice Themes Guide

## 🎨 Three Professional Invoice Themes

### 1. 📄 Standard Theme
**Best for:** Professional businesses, B2B transactions
**Features:**
- Wine/burgundy color scheme
- Complete GST structure with CGST/SGST/IGST breakdown
- Professional layout with clear sections
- Company branding prominent
- A4 size compatible

**Use when:** You need a formal, professional invoice for business clients

---

### 2. 🧾 Thermal Theme
**Best for:** Restaurants, retail shops, quick service
**Features:**
- Black & white design (like biryani hotel receipts)
- Narrow 300px format (thermal printer compatible)
- Monospace font (Courier Prime)
- Compact layout
- Minimal ink usage

**Use when:** You need a simple receipt for walk-in customers or thermal printing

---

### 3. ✨ Premium Theme
**Best for:** Luxury brands, high-end services, premium clients
**Features:**
- Dark theme with gold accents
- Elegant gradient backgrounds
- Sophisticated typography
- Premium feel
- Stands out from standard invoices

**Use when:** You want to impress high-value clients or luxury customers

---

## 🔧 How to Use

### Switching Themes:
1. Open any invoice (click "View Receipt" from invoice list)
2. You'll see 3 theme buttons at the top
3. Click any button to switch themes instantly
4. Your preference is automatically saved

### Theme Persistence:
- Selected theme is saved in browser localStorage
- Next time you open an invoice, it will use your last selected theme
- Each user can have their own theme preference

### Printing:
- All themes are print-friendly
- Theme selector buttons are hidden when printing
- Colors are preserved in print (for Standard and Premium themes)
- Thermal theme is optimized for black & white printing

---

## 📋 Invoice Structure (All Themes)

### Header Section:
- Company logo and name
- Company address, phone, email
- GSTIN and State Code
- Invoice title: "TAX INVOICE"

### Invoice Metadata:
- Invoice Number
- Invoice Date
- Due Date
- Payment Mode
- Status (PAID/UNPAID/DUE/CANCELLED)

### Bill To Section:
- Customer Name
- Customer Address
- Customer Phone
- Customer Email
- Customer GSTIN
- Place of Supply

### Product Table:
- Sr No
- Product/Service Name
- HSN/SAC Code
- Quantity
- Rate (₹)
- Tax %
- CGST Amount
- SGST Amount
- IGST Amount
- Line Total

### Tax Summary:
- Subtotal (Before Tax)
- CGST Total
- SGST Total
- IGST Total
- Discount
- Round Off
- **Grand Total** (highlighted)

### Amount in Words:
Example: "Rupees Eight Hundred Sixty and Twenty Six Paise Only"

### Footer:
- Terms & Conditions
- "Computer-generated invoice" note
- Authorized Signatory

---

## 🛡️ Safe Fallbacks

All fields have safe fallbacks to prevent blank spaces:
- Missing customer name → "N/A"
- Missing address → "N/A"
- Missing phone → "N/A"
- Missing email → "N/A"
- Missing GSTIN → "N/A"
- Missing HSN code → "N/A"

This ensures the invoice always looks professional, even with incomplete data.

---

## 🖨️ Print Tips

### For Standard & Premium Themes:
- Use color printer for best results
- A4 paper size
- Portrait orientation
- Margins: 0.5 inch

### For Thermal Theme:
- Use thermal printer (80mm width)
- Black & white only
- No margins needed
- Continuous paper feed

---

## 🎯 Quick Access

**Local Development:**
```
http://localhost:5000/retail/invoices
```

**Production:**
```
https://bizpulse-erp.onrender.com/retail/invoices
```

**Direct Invoice URL:**
```
/retail/invoice/{invoice_id}
```

---

## 💡 Pro Tips

1. **Theme Selection:** Choose theme based on your business type and customer expectations
2. **Consistency:** Stick to one theme for all invoices to maintain brand consistency
3. **Printing:** Test print once to ensure colors and layout are correct
4. **Mobile:** All themes are responsive and work on mobile devices
5. **PDF Export:** Use browser's "Print to PDF" feature to save invoices

---

**Need help?** Contact support or check the documentation.
