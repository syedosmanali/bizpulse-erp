# Inventory Management Modules - Redesign Plan

## Already Completed ✅
1. **Categories & Brands** - Clean tab-based interface with table view
2. **Low Stock Alerts** - 3 tabs (Alerts, Reorder List, Settings) with proper tables
3. **Unit Conversion** - 3 tabs (Quick Converter, Manage Conversions, Common Units)

## Remaining Modules to Redesign

### Priority 1 - Core Inventory (DOING NOW)
1. **Products Management** (erp_products.html)
   - Tabs: All Products, Add Product, Import/Export, Bulk Operations
   - Table view with search, filter, pagination
   - Quick actions: Edit, Delete, Duplicate, View Details

2. **Stock Management** (erp_stock.html)
   - Tabs: Current Stock, Stock Adjustments, Transactions, Reports
   - Real-time stock levels
   - Stock in/out tracking
   - Warehouse management

3. **Batch & Expiry** (erp_batch_expiry.html)
   - Tabs: All Batches, Expiring Soon, Expired, Quality Control
   - Calendar view for expiry dates
   - Batch operations (merge, split, transfer)
   - Alerts and notifications

### Priority 2 - Supporting Modules
4. **Barcode Management** (erp_barcode.html)
   - Tabs: Generate Barcodes, Scan & Lookup, Print Labels, Settings
   - Bulk barcode generation
   - QR code support
   - Label templates

5. **HSN/GST Codes** (erp_hsn_gst.html)
   - Tabs: HSN Codes, GST Rates, Mapping, Import
   - Search HSN codes
   - Assign to products
   - Tax calculation

6. **MRP & Selling Price** (erp_mrp_selling_price.html)
   - Tabs: Price List, Bulk Update, Price Rules, History
   - Margin calculator
   - Discount rules
   - Price comparison

## Design Pattern (Consistent Across All)
- Clean tab navigation
- Table-based data display
- Search and filter options
- Modal forms for add/edit
- Stats cards at top
- Export functionality
- Responsive design
- Wine color theme

## Implementation Order
1. Products Management (Most Critical)
2. Stock Management
3. Batch & Expiry
4. Barcode Management
5. HSN/GST Codes
6. MRP & Selling Price
