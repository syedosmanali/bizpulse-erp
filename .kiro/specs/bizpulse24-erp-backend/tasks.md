# Implementation Plan: BizPulse24 ERP Backend System

## Overview

This implementation plan breaks down the BizPulse24 ERP backend system into discrete, actionable tasks. The system is built with Node.js/TypeScript, Express.js, Prisma ORM, and Supabase PostgreSQL. The architecture follows an event-driven pattern where single API operations trigger cascading effects across multiple modules.

## Implementation Approach

1. **Foundation First**: Database schema, core engines, and authentication
2. **Module by Module**: Implement each business module with its APIs
3. **Integration**: Wire modules together with event-driven flows
4. **Testing**: Property-based tests for all 76 correctness properties
5. **Documentation**: OpenAPI specs and deployment guides

## Tasks

### Phase 1: Core Setup and Infrastructure

- [x] 1. Set up project structure and dependencies
  - Initialize Node.js/TypeScript project with Express.js
  - Install dependencies: Prisma, Supabase client, Jest, fast-check, express-validator
  - Configure TypeScript with strict mode and path aliases
  - Set up ESLint and Prettier for code quality
  - Create directory structure: src/{api,services,engines,models,middleware,utils,tests}
  - _Requirements: 20.1, 33.4_

- [-] 2. Configure Supabase connection and authentication
  - Set up Supabase project and obtain connection credentials
  - Configure Prisma schema with Supabase PostgreSQL connection
  - Implement JWT authentication middleware using Supabase Auth
  - Create auth utilities for token validation and user context extraction
  - _Requirements: 3.1, 20.3, 34.1, 34.3_

- [x] 3. Create database schema SQL files for core tables
  - Write SQL for companies, financial_years, user_roles tables
  - Include UUID primary keys, foreign key constraints, and indexes
  - Add audit fields (created_at, updated_at, created_by, updated_by) to all tables
  - Create migration script for core tables
  - _Requirements: 1.1, 1.2, 2.1, 3.1, 19.1, 19.4_

- [-] 4. Implement Row Level Security (RLS) policies for core tables
  - Enable RLS on companies, financial_years, user_roles tables
  - Create SELECT policies based on user_roles.company_id matching
  - Create INSERT/UPDATE policies with role-based restrictions (Owner, Admin, Staff)
  - Create DELETE policies (Owner only)
  - Test RLS policies with different user roles
  - _Requirements: 3.2, 3.3, 3.4, 3.5, 34.4_


- [ ] 5. Implement core engine components
  - [~] 5.1 Create GST_Engine class with calculation logic
    - Implement calculateGST() method for intra-state (CGST+SGST) and inter-state (IGST)
    - Implement createGSTEntries() for invoice line items
    - Implement reverseGSTEntries() for returns
    - Validate GST rates (0, 5, 12, 18, 28)
    - _Requirements: 4.4, 6.4, 16.1, 16.2, 16.3, 16.8_
  
  - [~] 5.2 Write property tests for GST_Engine
    - **Property 19: GST Calculation Correctness**
    - **Validates: Requirements 6.4, 8.4, 16.1, 16.2, 16.8**
    - **Property 65: GST State Classification**
    - **Validates: Requirements 16.3**
  
  - [~] 5.3 Create Ledger_Engine class with double-entry bookkeeping
    - Implement createEntries() ensuring debits = credits
    - Implement createSalesLedgerEntries() for invoices
    - Implement createPurchaseLedgerEntries() for GRN
    - Implement createPaymentReceiptEntries() and createVendorPaymentEntries()
    - Implement getAccountBalance() with running balance calculation
    - _Requirements: 6.7, 15.1, 15.2, 15.3, 15.5_
  
  - [~] 5.4 Write property tests for Ledger_Engine
    - **Property 22: Ledger Entry Double-Entry Invariant**
    - **Validates: Requirements 6.7, 15.3**
    - **Property 64: Account Balance Calculation**
    - **Validates: Requirements 15.5**
  
  - [~] 5.5 Create Audit_Logger class for activity tracking
    - Implement log() method for all CRUD operations
    - Implement logAuthFailure() for authentication failures
    - Implement logPermissionDenied() for authorization failures
    - Implement queryLogs() with filtering by user, module, action, date range
    - Store old and new values as JSONB for change tracking
    - _Requirements: 6.8, 18.1, 18.2, 18.3, 18.4, 18.5_
  
  - [~] 5.6 Write property tests for Audit_Logger
    - **Property 23: Audit Log Creation**
    - **Validates: Requirements 6.8, 18.1**
    - **Property 66: Authentication Failure Audit Logging**
    - **Validates: Requirements 18.4**
    - **Property 67: Permission Denied Audit Logging**
    - **Validates: Requirements 18.5**
    - **Property 68: Audit Log Immutability**
    - **Validates: Requirements 18.7**
  
  - [~] 5.7 Create Stock_Ledger class for inventory tracking
    - Implement recordMovement() for IN/OUT/TRANSFER movements
    - Implement getCurrentStock() with batch number support
    - Implement getMovements() with date range filtering
    - Implement calculateWeightedAvgCost() for cost price updates
    - Implement getEarliestExpiryBatch() for FEFO logic
    - _Requirements: 5.5, 5.6, 5.7, 6.10, 9.4_
  
  - [~] 5.8 Write property tests for Stock_Ledger
    - **Property 14: Stock Movement Ledger Recording**
    - **Validates: Requirements 5.5**
    - **Property 15: Weighted Average Cost Calculation**
    - **Validates: Requirements 5.6, 9.4**
    - **Property 16: FEFO Batch Selection**
    - **Validates: Requirements 5.7**

- [~] 6. Implement database triggers and constraints
  - Create financial year lock enforcement trigger for sales_invoices, goods_receipt_notes, payments
  - Create auto-update timestamp trigger for all tables with updated_at field
  - Create stock alert trigger for low stock detection
  - Add CHECK constraints for GST rates, positive quantities, and amounts
  - Test triggers with various scenarios
  - _Requirements: 2.3, 2.5, 5.4, 19.7, 25.2_

- [~] 7. Checkpoint - Core infrastructure validation
  - Ensure all tests pass, ask the user if questions arise.

### Phase 2: Inventory Module

- [-] 8. Create database schema for Inventory module
  - Write SQL for categories, brands, products, locations, stock, stock_ledger, stock_alerts tables
  - Include unique constraints on SKU and barcode
  - Add indexes on frequently queried fields (SKU, barcode, category, HSN code)
  - Create RLS policies for all Inventory tables
  - Run migration scripts
  - _Requirements: 4.1, 4.2, 4.5, 19.2, 19.3, 22.2_

- [ ] 9. Implement Product Master Management APIs
  - [ ] 9.1 Create ProductService with CRUD operations
    - Implement createProduct() with validation for HSN code (2/4/6/8 digits) and GST rate
    - Implement updateProduct() with optimistic locking
    - Implement soft delete for products
    - Implement searchProducts() with filtering by category, brand, SKU, barcode
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 22.3_
  
  - [ ] 9.2 Create API endpoints for products
    - POST /api/v1/inventory/products - Create product
    - GET /api/v1/inventory/products - List products with pagination
    - GET /api/v1/inventory/products/:id - Get product details
    - PUT /api/v1/inventory/products/:id - Update product
    - DELETE /api/v1/inventory/products/:id - Soft delete product
    - GET /api/v1/inventory/products/search - Search by barcode or SKU
    - Add input validation middleware using express-validator
    - _Requirements: 4.1, 20.1, 20.2, 20.8, 20.9, 22.3, 22.5_
  
  - [ ] 9.3 Write property tests for Product Management
    - **Property 10: HSN Code Format Validation**
    - **Validates: Requirements 4.3**
    - **Property 11: GST Rate Validation**
    - **Validates: Requirements 4.4**
    - **Property 12: Unique SKU and Barcode Constraint**
    - **Validates: Requirements 4.5, 22.2**
  
  - [ ] 9.4 Write unit tests for Product APIs
    - Test product creation with valid data
    - Test HSN code validation (invalid formats)
    - Test GST rate validation (invalid rates)
    - Test duplicate SKU/barcode rejection
    - Test soft delete functionality

- [ ] 10. Implement Stock Management APIs
  - [ ] 10.1 Create StockService with stock operations
    - Implement getCurrentStock() with location and batch filtering
    - Implement transferStock() between locations with transaction
    - Implement adjustStock() for manual adjustments
    - Implement getLowStockAlerts() and acknowledgeAlert()
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 25.1, 25.3, 25.4, 26.1, 26.2, 26.3_
  
  - [ ] 10.2 Create API endpoints for stock operations
    - GET /api/v1/inventory/stock/current - Query current stock levels
    - POST /api/v1/inventory/stock/transfer - Transfer stock between locations
    - POST /api/v1/inventory/stock/adjust - Manual stock adjustment
    - GET /api/v1/inventory/stock/movements - Stock movement history
    - GET /api/v1/inventory/stock/alerts - Low stock alerts
    - PUT /api/v1/inventory/stock/alerts/:id/acknowledge - Acknowledge alert
    - _Requirements: 5.3, 25.3, 25.4, 26.3, 26.6_
  
  - [ ] 10.3 Write property tests for Stock Management
    - **Property 13: Low Stock Alert Generation**
    - **Validates: Requirements 5.4, 25.2**
    - **Property 24: Batch Validation for Batch-Tracked Products**
    - **Validates: Requirements 6.9**
  
  - [ ] 10.4 Write unit tests for Stock APIs
    - Test stock transfer between locations
    - Test low stock alert generation
    - Test batch tracking for products with has_batch_tracking=true
    - Test stock query with location filtering

- [ ] 11. Implement Category and Brand Management APIs
  - Create CategoryService and BrandService with CRUD operations
  - Support hierarchical category structure with parent_id
  - Create API endpoints: POST/GET/PUT/DELETE for /api/v1/inventory/categories and /brands
  - Add soft delete support
  - _Requirements: 4.6_

- [ ] 12. Checkpoint - Inventory module validation
  - Ensure all tests pass, ask the user if questions arise.

### Phase 3: Party Module

- [ ] 13. Create database schema for Party module
  - Write SQL for customers and vendors tables
  - Add unique constraints on GSTIN and PAN per company
  - Create indexes on GSTIN, phone, and email fields
  - Create RLS policies for customers and vendors tables
  - Run migration scripts
  - _Requirements: 11.1, 11.2, 11.3, 11.7_

- [ ] 14. Implement Customer and Vendor Management APIs
  - [ ] 14.1 Create PartyService for customer and vendor operations
    - Implement createCustomer() and createVendor() with GSTIN validation
    - Implement updateParty() and soft delete
    - Implement getCustomerOutstanding() calculating sum of credit sales minus payments
    - Implement getVendorPayable() calculating sum of credit purchases minus payments
    - Validate GSTIN format (15 alphanumeric characters)
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6_
  
  - [ ] 14.2 Create API endpoints for parties
    - POST /api/v1/parties/customers - Create customer
    - GET /api/v1/parties/customers - List customers with pagination
    - GET /api/v1/parties/customers/:id - Get customer details with outstanding
    - PUT /api/v1/parties/customers/:id - Update customer
    - DELETE /api/v1/parties/customers/:id - Soft delete customer
    - POST /api/v1/parties/vendors - Create vendor
    - GET /api/v1/parties/vendors - List vendors
    - GET /api/v1/parties/vendors/:id - Get vendor details with payable
    - PUT /api/v1/parties/vendors/:id - Update vendor
    - DELETE /api/v1/parties/vendors/:id - Soft delete vendor
    - _Requirements: 11.1, 11.2, 20.1, 20.8_
  
  - [ ] 14.3 Write property tests for Party Management
    - **Property 2: GSTIN Format Validation**
    - **Validates: Requirements 1.3, 11.4**
    - **Property 47: Customer Outstanding Calculation**
    - **Validates: Requirements 11.5**
    - **Property 48: Vendor Payable Calculation**
    - **Validates: Requirements 11.6**
    - **Property 49: Party GSTIN Uniqueness**
    - **Validates: Requirements 11.7**
  
  - [ ] 14.4 Write unit tests for Party APIs
    - Test customer creation with valid GSTIN
    - Test GSTIN format validation (invalid formats)
    - Test duplicate GSTIN rejection
    - Test outstanding calculation for customers
    - Test payable calculation for vendors

- [ ] 15. Create customer_dues and vendor_payables tables
  - Write SQL for customer_dues and vendor_payables tables
  - Add unique constraints on (company_id, customer_id) and (company_id, vendor_id)
  - Create indexes for fast lookups
  - Create RLS policies
  - Run migration scripts
  - _Requirements: 6.5, 9.5, 11.5, 11.6_

- [ ] 16. Checkpoint - Party module validation
  - Ensure all tests pass, ask the user if questions arise.

### Phase 4: Sales Module

- [ ] 17. Create database schema for Sales module
  - Write SQL for sales_invoices, sales_invoice_items, sales_returns, sales_return_items, delivery_challans tables
  - Add unique constraints on invoice_number, return_number, challan_number
  - Create indexes on customer_id, invoice_date, financial_year_id
  - Create RLS policies for all Sales tables
  - Run migration scripts
  - _Requirements: 6.1, 7.1, 8.1, 24.1_


- [ ] 18. Implement Sales Invoice Creation with multi-module orchestration
  - [ ] 18.1 Create SalesService.createInvoice() method
    - Start database transaction
    - Validate financial year is not locked
    - Validate customer credit limit if sale type is CREDIT
    - Check stock availability for all line items
    - Create sales_invoices record with auto-generated invoice number
    - Create sales_invoice_items records for all line items
    - Call GST_Engine.createGSTEntries() to calculate and store GST breakup
    - Call Stock_Ledger.recordMovement() for each line item (movement type OUT)
    - Update stock quantities in stock table
    - Call Ledger_Engine.createSalesLedgerEntries() for double-entry bookkeeping
    - Update customer_dues if sale type is CREDIT
    - Update cash/bank ledger if sale type is CASH
    - Call Audit_Logger.log() to record invoice creation
    - Commit transaction or rollback on any error
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 6.10, 21.1, 27.3_
  
  - [ ] 18.2 Create API endpoint for invoice creation
    - POST /api/v1/sales/invoices - Create sales invoice
    - Validate input: customer_id, line items (product_id, quantity, unit_price)
    - Return HTTP 400 for insufficient stock with descriptive error
    - Return HTTP 403 for locked financial year
    - Return HTTP 400 for credit limit exceeded
    - Return invoice with all calculated fields (GST breakup, totals)
    - _Requirements: 6.1, 6.3, 20.1, 20.2, 20.4, 27.3_
  
  - [ ] 18.3 Write property tests for Sales Invoice Creation
    - **Property 17: Sales Invoice Stock Reduction**
    - **Validates: Requirements 6.2, 8.2**
    - **Property 18: Insufficient Stock Rejection**
    - **Validates: Requirements 6.3, 8.6**
    - **Property 20: Credit Sale Customer Due Increase**
    - **Validates: Requirements 6.5**
    - **Property 21: Cash Sale Ledger Increase**
    - **Validates: Requirements 6.6, 8.3**
    - **Property 25: Stock Ledger Entry Creation**
    - **Validates: Requirements 6.10**
    - **Property 73: Transaction Rollback on Failure**
    - **Validates: Requirements 21.6**
    - **Property 74: Credit Limit Enforcement**
    - **Validates: Requirements 27.3**
  
  - [ ] 18.4 Write unit tests for Sales Invoice APIs
    - Test invoice creation with valid data (cash and credit)
    - Test insufficient stock rejection
    - Test locked financial year rejection
    - Test credit limit exceeded rejection
    - Test GST calculation for intra-state and inter-state sales
    - Test batch-tracked product validation
    - Test transaction rollback on stock update failure

- [ ] 19. Implement Sales Return Processing
  - [ ] 19.1 Create SalesService.createReturn() method
    - Start database transaction
    - Validate financial year is not locked
    - Validate return quantities do not exceed original invoice quantities
    - Create sales_returns record
    - Create sales_return_items records
    - Call GST_Engine.reverseGSTEntries() to create reversing GST entries
    - Call Stock_Ledger.recordMovement() for each return item (movement type IN)
    - Update stock quantities in stock table
    - Call Ledger_Engine with reversing entries (opposite debit/credit)
    - Update customer_dues (reduce) if original sale was CREDIT
    - Update cash/bank ledger (reduce) if original sale was CASH
    - Call Audit_Logger.log() with reference to original invoice
    - Commit transaction or rollback on any error
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 21.2_
  
  - [ ] 19.2 Create API endpoint for sales returns
    - POST /api/v1/sales/returns - Create sales return
    - Validate input: original_invoice_id, return items (product_id, quantity)
    - Return HTTP 400 if return quantity exceeds original quantity
    - Return HTTP 403 for locked financial year
    - _Requirements: 7.1, 7.9, 20.1, 20.2_
  
  - [ ] 19.3 Write property tests for Sales Returns
    - **Property 26: Sales Return Stock Increase**
    - **Validates: Requirements 7.2**
    - **Property 27: Sales Return GST Reversal**
    - **Validates: Requirements 7.3**
    - **Property 28: Credit Sale Return Due Reduction**
    - **Validates: Requirements 7.4**
    - **Property 29: Cash Sale Return Ledger Reduction**
    - **Validates: Requirements 7.5**
    - **Property 30: Sales Return Ledger Reversal**
    - **Validates: Requirements 7.6**
    - **Property 31: Sales Return Stock Ledger Entry**
    - **Validates: Requirements 7.7**
    - **Property 32: Sales Return Audit Logging**
    - **Validates: Requirements 7.8**
    - **Property 33: Return Quantity Validation**
    - **Validates: Requirements 7.9**
  
  - [ ] 19.4 Write unit tests for Sales Return APIs
    - Test return creation with valid data
    - Test return quantity validation
    - Test stock restoration
    - Test ledger reversal
    - Test customer due reduction for credit sales

- [ ] 20. Implement POS Billing
  - [ ] 20.1 Create SalesService.createPOSSale() method
    - Reuse createInvoice() logic with sale_type='POS'
    - Auto-generate invoice number using configured scheme
    - Apply discount rules automatically based on products and date
    - Ensure immediate cash ledger update
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 23.3_
  
  - [ ] 20.2 Create API endpoint for POS sales
    - POST /api/v1/sales/pos - Create POS sale
    - Support line-item and invoice-level discounts
    - Return HTTP 400 for insufficient stock
    - _Requirements: 8.1, 8.7, 20.1_
  
  - [ ] 20.3 Write property tests for POS Billing
    - **Property 34: Automatic Invoice Number Generation**
    - **Validates: Requirements 8.8**
  
  - [ ] 20.4 Write unit tests for POS APIs
    - Test POS sale creation
    - Test discount application
    - Test invoice number generation
    - Test insufficient stock rejection

- [ ] 21. Implement Delivery Challan Management
  - [ ] 21.1 Create SalesService for challan operations
    - Implement createChallan() with stock reduction
    - Implement convertChallanToInvoice() without additional stock reduction
    - Implement cancelChallan() with stock restoration
    - _Requirements: 24.1, 24.2, 24.3, 24.4, 24.6_
  
  - [ ] 21.2 Create API endpoints for challans
    - POST /api/v1/sales/challans - Create challan
    - POST /api/v1/sales/challans/:id/convert - Convert to invoice
    - DELETE /api/v1/sales/challans/:id - Cancel challan
    - _Requirements: 24.1, 24.3, 24.6, 20.1_
  
  - [ ] 21.3 Write unit tests for Challan APIs
    - Test challan creation with stock reduction
    - Test challan to invoice conversion
    - Test challan cancellation with stock restoration

- [ ] 22. Implement Discount Rules Management
  - Create DiscountService with CRUD operations for discount rules
  - Implement automatic discount application logic in invoice creation
  - Create API endpoints: POST/GET/PUT/DELETE for /api/v1/sales/discount-rules
  - Validate discount amount does not exceed line item or invoice total
  - _Requirements: 23.1, 23.2, 23.3, 23.4, 23.5_

- [ ] 23. Implement Invoice Query and PDF Generation APIs
  - GET /api/v1/sales/invoices - List invoices with pagination and filtering
  - GET /api/v1/sales/invoices/:id - Get invoice details
  - GET /api/v1/sales/invoices/:id/pdf - Generate invoice PDF using template
  - Support filtering by customer, date range, sale type
  - _Requirements: 20.1, 20.8, 20.9, 30.5_

- [ ] 24. Checkpoint - Sales module validation
  - Ensure all tests pass, ask the user if questions arise.

### Phase 5: Purchase Module

- [ ] 25. Create database schema for Purchase module
  - Write SQL for purchase_orders, purchase_order_items, goods_receipt_notes, grn_items, purchase_returns, purchase_return_items tables
  - Add unique constraints on po_number, grn_number, return_number
  - Create indexes on vendor_id, po_date, grn_date
  - Create RLS policies for all Purchase tables
  - Run migration scripts
  - _Requirements: 9.1, 10.1_

- [ ] 26. Implement Purchase Order Management
  - [ ] 26.1 Create PurchaseService.createPurchaseOrder() method
    - Create purchase_orders record with auto-generated PO number
    - Create purchase_order_items records
    - Set status to PENDING
    - _Requirements: 9.1_
  
  - [ ] 26.2 Create API endpoints for purchase orders
    - POST /api/v1/purchase/orders - Create purchase order
    - GET /api/v1/purchase/orders - List purchase orders
    - GET /api/v1/purchase/orders/:id - Get PO details
    - PUT /api/v1/purchase/orders/:id - Update PO
    - _Requirements: 9.1, 20.1_
  
  - [ ] 26.3 Write unit tests for Purchase Order APIs
    - Test PO creation with valid data
    - Test PO status tracking

- [ ] 27. Implement GRN Processing with multi-module orchestration
  - [ ] 27.1 Create PurchaseService.createGRN() method
    - Start database transaction
    - Validate financial year is not locked
    - Validate GRN quantities do not exceed PO quantities if linked to PO
    - Create goods_receipt_notes record
    - Create grn_items records
    - Call Stock_Ledger.recordMovement() for each GRN item (movement type IN)
    - Update stock quantities in stock table
    - Update product cost_price using weighted average method
    - Call Ledger_Engine.createPurchaseLedgerEntries() for double-entry bookkeeping
    - Update vendor_payables if purchase type is CREDIT
    - Update cash/bank ledger if purchase type is CASH
    - Call Audit_Logger.log() to record GRN creation
    - Update purchase_order status if linked to PO
    - Commit transaction or rollback on any error
    - _Requirements: 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8, 9.9, 21.3_
  
  - [ ] 27.2 Create API endpoint for GRN creation
    - POST /api/v1/purchase/grn - Create GRN
    - Validate input: vendor_id, GRN items (product_id, quantity, unit_price)
    - Return HTTP 400 if GRN quantity exceeds PO quantity
    - Return HTTP 403 for locked financial year
    - _Requirements: 9.2, 9.9, 20.1, 20.2_
  
  - [ ] 27.3 Write property tests for GRN Processing
    - **Property 35: GRN Stock Increase**
    - **Validates: Requirements 9.3**
    - **Property 36: Credit Purchase Vendor Payable Increase**
    - **Validates: Requirements 9.5**
    - **Property 37: GRN Ledger Entry Creation**
    - **Validates: Requirements 9.6**
    - **Property 38: GRN Stock Ledger Entry**
    - **Validates: Requirements 9.7**
    - **Property 39: GRN Audit Logging**
    - **Validates: Requirements 9.8**
    - **Property 40: GRN Quantity Validation**
    - **Validates: Requirements 9.9**
  
  - [ ] 27.4 Write unit tests for GRN APIs
    - Test GRN creation with valid data
    - Test stock increase and cost price update
    - Test vendor payable increase for credit purchases
    - Test GRN quantity validation against PO
    - Test locked financial year rejection

- [ ] 28. Implement Purchase Return Processing
  - [ ] 28.1 Create PurchaseService.createPurchaseReturn() method
    - Start database transaction
    - Validate financial year is not locked
    - Validate return quantities do not exceed original GRN quantities
    - Check stock availability for return items
    - Create purchase_returns record
    - Create purchase_return_items records
    - Call Stock_Ledger.recordMovement() for each return item (movement type OUT)
    - Update stock quantities in stock table
    - Call Ledger_Engine with reversing entries
    - Update vendor_payables (reduce)
    - Call Audit_Logger.log() with reference to original GRN
    - Commit transaction or rollback on any error
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 21.4_
  
  - [ ] 28.2 Create API endpoint for purchase returns
    - POST /api/v1/purchase/returns - Create purchase return
    - Validate input: original_grn_id, return items (product_id, quantity)
    - Return HTTP 400 if return quantity exceeds original quantity or insufficient stock
    - Return HTTP 403 for locked financial year
    - _Requirements: 10.1, 10.6, 10.7, 20.1_
  
  - [ ] 28.3 Write property tests for Purchase Returns
    - **Property 41: Purchase Return Stock Reduction**
    - **Validates: Requirements 10.2**
    - **Property 42: Purchase Return Payable Reduction**
    - **Validates: Requirements 10.3**
    - **Property 43: Purchase Return Ledger Reversal**
    - **Validates: Requirements 10.4**
    - **Property 44: Purchase Return Stock Ledger Entry**
    - **Validates: Requirements 10.5**
    - **Property 45: Purchase Return Insufficient Stock Rejection**
    - **Validates: Requirements 10.6**
    - **Property 46: Purchase Return Quantity Validation**
    - **Validates: Requirements 10.7**
  
  - [ ] 28.4 Write unit tests for Purchase Return APIs
    - Test return creation with valid data
    - Test return quantity validation
    - Test insufficient stock rejection
    - Test vendor payable reduction

- [ ] 29. Implement Purchase Query APIs
  - GET /api/v1/purchase/orders - List purchase orders with pagination
  - GET /api/v1/purchase/grn - List GRNs with filtering by vendor, date range
  - GET /api/v1/purchase/returns - List purchase returns
  - _Requirements: 20.1, 20.8, 20.9_

- [ ] 30. Checkpoint - Purchase module validation
  - Ensure all tests pass, ask the user if questions arise.

### Phase 6: Finance Module

- [ ] 31. Create database schema for Finance module
  - Write SQL for payments, income_entries, expense_entries, ledger_entries tables
  - Add unique constraints on payment_number
  - Create indexes on party_id, entry_date, account_head
  - Create RLS policies for all Finance tables
  - Add CHECK constraint for ledger_entries (debit XOR credit)
  - Run migration scripts
  - _Requirements: 12.1, 13.1, 14.1, 14.2, 15.1_


- [ ] 32. Implement Payment Receipt Processing
  - [ ] 32.1 Create FinanceService.recordPaymentReceipt() method
    - Start database transaction
    - Validate financial year is not locked
    - Validate payment amount does not exceed customer outstanding due
    - Create payments record with payment_type='RECEIPT'
    - Update customer_dues (reduce by payment amount)
    - Update cash or bank ledger based on payment_mode
    - Call Ledger_Engine.createPaymentReceiptEntries() (Debit: Cash/Bank, Credit: Customer Receivables)
    - Call Audit_Logger.log() to record payment
    - Commit transaction or rollback on any error
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 21.5_
  
  - [ ] 32.2 Create API endpoint for payment receipts
    - POST /api/v1/finance/payments/receipts - Record payment receipt
    - Validate input: customer_id, amount, payment_mode
    - Return HTTP 400 if payment exceeds outstanding due
    - Return HTTP 403 for locked financial year
    - Support multiple payment modes: CASH, BANK, CHEQUE, UPI, CARD
    - _Requirements: 12.1, 12.6, 12.7, 20.1_
  
  - [ ] 32.3 Write property tests for Payment Receipts
    - **Property 50: Payment Receipt Due Reduction**
    - **Validates: Requirements 12.2**
    - **Property 51: Payment Receipt Ledger Increase**
    - **Validates: Requirements 12.3**
    - **Property 52: Payment Receipt Ledger Entry Creation**
    - **Validates: Requirements 12.4**
    - **Property 53: Payment Receipt Audit Logging**
    - **Validates: Requirements 12.5**
    - **Property 54: Payment Receipt Amount Validation**
    - **Validates: Requirements 12.6**
  
  - [ ] 32.4 Write unit tests for Payment Receipt APIs
    - Test payment receipt with valid data
    - Test payment amount validation (exceeds due)
    - Test customer due reduction
    - Test cash/bank ledger increase
    - Test different payment modes

- [ ] 33. Implement Vendor Payment Processing
  - [ ] 33.1 Create FinanceService.recordVendorPayment() method
    - Start database transaction
    - Validate financial year is not locked
    - Validate payment amount does not exceed vendor outstanding payable
    - Create payments record with payment_type='PAYMENT'
    - Update vendor_payables (reduce by payment amount)
    - Update cash or bank ledger based on payment_mode
    - Call Ledger_Engine.createVendorPaymentEntries() (Debit: Vendor Payables, Credit: Cash/Bank)
    - Call Audit_Logger.log() to record payment
    - Commit transaction or rollback on any error
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 21.5_
  
  - [ ] 33.2 Create API endpoint for vendor payments
    - POST /api/v1/finance/payments/vendor-payments - Record vendor payment
    - Validate input: vendor_id, amount, payment_mode
    - Return HTTP 400 if payment exceeds outstanding payable
    - Return HTTP 403 for locked financial year
    - Support multiple payment modes: CASH, BANK, CHEQUE, UPI, CARD
    - _Requirements: 13.1, 13.6, 13.7, 20.1_
  
  - [ ] 33.3 Write property tests for Vendor Payments
    - **Property 55: Vendor Payment Payable Reduction**
    - **Validates: Requirements 13.2**
    - **Property 56: Vendor Payment Ledger Reduction**
    - **Validates: Requirements 13.3**
    - **Property 57: Vendor Payment Ledger Entry Creation**
    - **Validates: Requirements 13.4**
    - **Property 58: Vendor Payment Audit Logging**
    - **Validates: Requirements 13.5**
    - **Property 59: Vendor Payment Amount Validation**
    - **Validates: Requirements 13.6**
  
  - [ ] 33.4 Write unit tests for Vendor Payment APIs
    - Test vendor payment with valid data
    - Test payment amount validation (exceeds payable)
    - Test vendor payable reduction
    - Test cash/bank ledger reduction
    - Test different payment modes

- [ ] 34. Implement Income and Expense Management
  - [ ] 34.1 Create FinanceService for income and expense operations
    - Implement recordIncome() with cash/bank ledger increase
    - Implement recordExpense() with cash/bank ledger reduction
    - Call Ledger_Engine for both income and expense entries
    - Support predefined categories: Rent, Salary, Utilities, Marketing, Transportation, Miscellaneous
    - Support custom category creation
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7, 14.8_
  
  - [ ] 34.2 Create API endpoints for income and expenses
    - POST /api/v1/finance/income - Record income entry
    - GET /api/v1/finance/income - List income entries
    - PUT /api/v1/finance/income/:id - Update income entry
    - DELETE /api/v1/finance/income/:id - Delete income entry
    - POST /api/v1/finance/expenses - Record expense entry
    - GET /api/v1/finance/expenses - List expense entries with category filtering
    - PUT /api/v1/finance/expenses/:id - Update expense entry
    - DELETE /api/v1/finance/expenses/:id - Delete expense entry
    - _Requirements: 14.1, 14.2, 20.1_
  
  - [ ] 34.3 Write property tests for Income and Expenses
    - **Property 60: Income Entry Ledger Increase**
    - **Validates: Requirements 14.4**
    - **Property 61: Expense Entry Ledger Reduction**
    - **Validates: Requirements 14.5**
    - **Property 62: Income and Expense Ledger Entry Creation**
    - **Validates: Requirements 14.6**
  
  - [ ] 34.4 Write unit tests for Income and Expense APIs
    - Test income entry creation
    - Test expense entry creation
    - Test ledger updates for income and expenses
    - Test category filtering

- [ ] 35. Implement Ledger Query APIs
  - [ ] 35.1 Create LedgerService for ledger queries
    - Implement queryLedgerEntries() with filtering by date range, account head, transaction type
    - Implement getAccountBalance() with running balance calculation
    - Implement getLedgerSummary() for all account heads
    - _Requirements: 15.4, 15.5_
  
  - [ ] 35.2 Create API endpoints for ledger queries
    - GET /api/v1/finance/ledgers - Query ledger entries with filters
    - GET /api/v1/finance/ledgers/balance/:accountHead - Get account balance
    - GET /api/v1/finance/ledgers/summary - Get summary for all accounts
    - _Requirements: 15.4, 20.1, 20.9_
  
  - [ ] 35.3 Write property tests for Ledger Queries
    - **Property 63: Ledger Entry Immutability**
    - **Validates: Requirements 15.6**
  
  - [ ] 35.4 Write unit tests for Ledger APIs
    - Test ledger query with date range filtering
    - Test account balance calculation
    - Test ledger entry immutability (update/delete should fail)

- [ ] 36. Checkpoint - Finance module validation
  - Ensure all tests pass, ask the user if questions arise.

### Phase 7: Reports Module

- [ ] 37. Implement GST Reports
  - [ ] 37.1 Create ReportService for GST reports
    - Implement getGSTSummary() with total taxable value, CGST, SGST, IGST grouped by tax rate
    - Implement getGSTR1Report() with B2B and B2C sales segregation
    - Implement getGSTR3BReport() with outward and inward supply details
    - Implement getHSNSummary() for HSN-wise summary
    - _Requirements: 16.4, 16.5, 16.6, 16.7_
  
  - [ ] 37.2 Create API endpoints for GST reports
    - GET /api/v1/reports/gst/summary - GST summary report
    - GET /api/v1/reports/gst/gstr1 - GSTR-1 format report
    - GET /api/v1/reports/gst/gstr3b - GSTR-3B format report
    - GET /api/v1/reports/gst/hsn-summary - HSN-wise summary
    - Support date range filtering
    - _Requirements: 16.4, 16.5, 16.6, 16.7, 20.1_
  
  - [ ] 37.3 Write unit tests for GST Reports
    - Test GST summary calculation
    - Test GSTR-1 report format
    - Test GSTR-3B report format
    - Test HSN summary grouping

- [ ] 38. Implement Financial Reports
  - [ ] 38.1 Create ReportService for financial reports
    - Implement getProfitAndLoss() with revenue, COGS, gross profit, expenses, net profit
    - Implement getBalanceSheet() with assets, liabilities, equity as of date
    - Implement getCashFlow() with operating, investing, financing activities
    - _Requirements: 17.1, 17.2, 17.3_
  
  - [ ] 38.2 Create API endpoints for financial reports
    - GET /api/v1/reports/financial/profit-loss - Profit and Loss report
    - GET /api/v1/reports/financial/balance-sheet - Balance Sheet report
    - GET /api/v1/reports/financial/cash-flow - Cash Flow report
    - Support date range filtering
    - Support locked financial year read-only access
    - _Requirements: 17.1, 17.2, 17.3, 17.10, 20.1_
  
  - [ ] 38.3 Write unit tests for Financial Reports
    - Test P&L calculation
    - Test Balance Sheet calculation
    - Test Cash Flow categorization
    - Test locked financial year read access

- [ ] 39. Implement Sales and Inventory Reports
  - [ ] 39.1 Create ReportService for sales and inventory reports
    - Implement getDailySalesSummary() with total sales, returns, net sales, payment mode breakup
    - Implement getItemWiseSales() with quantity sold, revenue, profit margin per product
    - Implement getStockValuation() with current stock quantity and value per product
    - Implement getStockAgeing() categorizing stock by age: 0-30, 31-60, 61-90, 90+ days
    - _Requirements: 17.4, 17.5, 17.8, 17.9_
  
  - [ ] 39.2 Create API endpoints for sales and inventory reports
    - GET /api/v1/reports/sales/daily-summary - Daily sales summary
    - GET /api/v1/reports/sales/item-wise - Item-wise sales report
    - GET /api/v1/reports/inventory/stock-valuation - Stock valuation report
    - GET /api/v1/reports/inventory/stock-ageing - Stock ageing report
    - Support date range and product filtering
    - _Requirements: 17.4, 17.5, 17.8, 17.9, 20.1_
  
  - [ ] 39.3 Write unit tests for Sales and Inventory Reports
    - Test daily sales summary calculation
    - Test item-wise sales with profit margin
    - Test stock valuation using weighted average cost
    - Test stock ageing categorization

- [ ] 40. Implement Party Outstanding Reports
  - [ ] 40.1 Create ReportService for party reports
    - Implement getCustomerOutstandingReport() listing all customers with pending dues
    - Implement getVendorPayableReport() listing all vendors with pending payments
    - Include ageing analysis: 0-30, 31-60, 61-90, 90+ days
    - _Requirements: 17.6, 17.7_
  
  - [ ] 40.2 Create API endpoints for party reports
    - GET /api/v1/reports/parties/customer-outstanding - Customer outstanding report
    - GET /api/v1/reports/parties/vendor-payable - Vendor payable report
    - Support sorting by outstanding amount and ageing
    - _Requirements: 17.6, 17.7, 20.1_
  
  - [ ] 40.3 Write unit tests for Party Reports
    - Test customer outstanding calculation
    - Test vendor payable calculation
    - Test ageing analysis

- [ ] 41. Implement Report Export Functionality
  - [ ] 41.1 Create ExportService for data export
    - Implement exportToCSV() for all reports
    - Implement exportToPDF() for invoices and reports
    - Implement exportProductMaster() for bulk editing
    - Ensure UTF-8 encoding for CSV exports
    - _Requirements: 29.1, 29.2, 29.3_
  
  - [ ] 41.2 Create API endpoints for exports
    - GET /api/v1/reports/{reportType}/export?format=csv - Export report to CSV
    - GET /api/v1/reports/{reportType}/export?format=pdf - Export report to PDF
    - GET /api/v1/inventory/products/export - Export product master to CSV
    - _Requirements: 29.1, 29.2, 29.3, 20.1_
  
  - [ ] 41.3 Write unit tests for Export functionality
    - Test CSV export format
    - Test PDF generation
    - Test UTF-8 encoding preservation

- [ ] 42. Checkpoint - Reports module validation
  - Ensure all tests pass, ask the user if questions arise.

### Phase 8: Company Setup and Admin Module

- [ ] 43. Implement Company Profile Management
  - [ ] 43.1 Create CompanyService for company operations
    - Implement createCompany() with GSTIN validation
    - Implement updateCompany() with single active profile constraint
    - Implement getCompanyProfile()
    - _Requirements: 1.1, 1.2, 1.3_
  
  - [ ] 43.2 Create API endpoints for company management
    - POST /api/v1/company/profile - Create company profile
    - GET /api/v1/company/profile - Get company profile
    - PUT /api/v1/company/profile - Update company profile
    - Restrict access to Owner role only
    - _Requirements: 1.1, 20.1_
  
  - [ ] 43.3 Write property tests for Company Management
    - **Property 1: Single Company Profile Per Tenant**
    - **Validates: Requirements 1.2**
  
  - [ ] 43.4 Write unit tests for Company APIs
    - Test company creation with valid GSTIN
    - Test single company profile constraint
    - Test GSTIN format validation
    - Test Owner role restriction

- [ ] 44. Implement Invoice Numbering and Template Management
  - [ ] 44.1 Create TemplateService for invoice templates
    - Implement createTemplate() with layout configuration
    - Implement updateTemplate() and setDefaultTemplate()
    - Implement generateInvoiceNumber() using configured scheme (prefix, suffix, sequence)
    - Implement generateInvoicePDF() using template variables
    - _Requirements: 1.4, 1.5, 30.1, 30.2, 30.3, 30.4, 30.5_
  
  - [ ] 44.2 Create API endpoints for templates
    - POST /api/v1/company/templates - Create invoice template
    - GET /api/v1/company/templates - List templates
    - PUT /api/v1/company/templates/:id - Update template
    - PUT /api/v1/company/templates/:id/set-default - Set as default
    - _Requirements: 1.5, 30.1, 20.1_
  
  - [ ] 44.3 Write unit tests for Template Management
    - Test template creation
    - Test invoice number generation with scheme
    - Test PDF generation with template variables

- [ ] 45. Implement Financial Year Management
  - [ ] 45.1 Create FinancialYearService
    - Implement createFinancialYear() with non-overlapping date validation
    - Implement lockFinancialYear() to set is_locked=true
    - Implement getActiveFinancialYear() based on current date
    - _Requirements: 2.1, 2.2, 2.3_
  
  - [ ] 45.2 Create API endpoints for financial years
    - POST /api/v1/financial-years - Create financial year
    - GET /api/v1/financial-years - List financial years
    - PUT /api/v1/financial-years/:id/lock - Lock financial year
    - Restrict access to Owner and Admin roles
    - _Requirements: 2.1, 20.1_
  
  - [ ] 45.3 Write property tests for Financial Year Management
    - **Property 3: Financial Year Non-Overlapping**
    - **Validates: Requirements 2.2**
    - **Property 4: Locked Financial Year Rejection**
    - **Validates: Requirements 2.3, 2.6**
    - **Property 5: Locked Financial Year Read Access**
    - **Validates: Requirements 2.4**
  
  - [ ] 45.4 Write unit tests for Financial Year APIs
    - Test financial year creation
    - Test non-overlapping date validation
    - Test financial year locking
    - Test locked year transaction rejection


- [ ] 46. Implement User Role Management
  - [ ] 46.1 Create UserRoleService
    - Implement assignRole() to create user_roles entries
    - Implement updateRole() and removeRole()
    - Implement getUsersByRole() for listing users
    - Validate role values: OWNER, ADMIN, STAFF
    - _Requirements: 3.1, 3.2_
  
  - [ ] 46.2 Create API endpoints for user roles
    - POST /api/v1/admin/users/:userId/roles - Assign role to user
    - PUT /api/v1/admin/users/:userId/roles - Update user role
    - DELETE /api/v1/admin/users/:userId/roles - Remove user role
    - GET /api/v1/admin/users - List users with roles
    - Restrict access to Owner role only
    - _Requirements: 3.1, 20.1_
  
  - [ ] 46.3 Write property tests for User Role Management
    - **Property 6: Owner Role Full Access**
    - **Validates: Requirements 3.3**
    - **Property 7: Admin Role Restricted Access**
    - **Validates: Requirements 3.4**
    - **Property 8: Staff Role Limited Access**
    - **Validates: Requirements 3.5**
    - **Property 9: Unauthorized Operation Rejection**
    - **Validates: Requirements 3.7, 20.4**
  
  - [ ] 46.4 Write unit tests for User Role APIs
    - Test role assignment
    - Test role-based access control
    - Test Owner full access
    - Test Admin restricted access
    - Test Staff limited access

- [ ] 47. Implement Audit Log Query APIs
  - [ ] 47.1 Create AuditService for audit log queries
    - Implement queryAuditLogs() with filtering by user, module, action, date range
    - Implement pagination for large result sets
    - Ensure audit logs cannot be modified or deleted
    - _Requirements: 18.3, 18.7_
  
  - [ ] 47.2 Create API endpoints for audit logs
    - GET /api/v1/audit/logs - Query audit logs with filters
    - Support pagination with page and limit parameters
    - Restrict access to Owner and Admin roles
    - _Requirements: 18.3, 20.1, 20.8_
  
  - [ ] 47.3 Write unit tests for Audit Log APIs
    - Test audit log query with filters
    - Test pagination
    - Test immutability (update/delete should fail)

- [ ] 48. Implement Data Import Functionality
  - [ ] 48.1 Create ImportService for data import
    - Implement importProductMaster() from CSV with validation
    - Validate all fields and return detailed error report for invalid rows
    - Support bulk import with transaction rollback on any validation error
    - Preserve data types, decimal precision, and special characters
    - _Requirements: 29.4, 29.5, 29.6, 31.2, 31.3, 31.4, 31.5_
  
  - [ ] 48.2 Create API endpoint for imports
    - POST /api/v1/inventory/products/import - Import product master from CSV
    - Return detailed error report with row numbers and error messages
    - Validate CSV format and UTF-8 encoding
    - _Requirements: 29.4, 29.5, 31.4, 20.1_
  
  - [ ] 48.3 Write property tests for Import functionality
    - **Property 76: Export-Import Round Trip**
    - **Validates: Requirements 31.1**
  
  - [ ] 48.4 Write unit tests for Import functionality
    - Test product import with valid CSV
    - Test validation error reporting
    - Test transaction rollback on validation error
    - Test round-trip (export then import)

- [ ] 49. Implement Backup Metadata Management
  - Create BackupService for backup metadata operations
  - Create API endpoints: POST/GET for /api/v1/admin/backups
  - Store backup timestamp, size, location, and type
  - Validate backup metadata recorded within 24 hours
  - _Requirements: 28.1, 28.2, 28.3, 28.4_

- [ ] 50. Checkpoint - Admin module validation
  - Ensure all tests pass, ask the user if questions arise.

### Phase 9: Security, Performance, and Monitoring

- [ ] 51. Implement Authentication and Authorization Middleware
  - [ ] 51.1 Create authentication middleware
    - Validate JWT token on every request
    - Extract user ID and company ID from token
    - Set user context for RLS policies
    - Return HTTP 401 for invalid or missing tokens
    - _Requirements: 20.3, 34.3_
  
  - [ ] 51.2 Create authorization middleware
    - Check user role permissions before processing requests
    - Return HTTP 403 for unauthorized operations
    - Log permission denied events using Audit_Logger
    - _Requirements: 3.6, 3.7, 20.4_
  
  - [ ] 51.3 Write property tests for Authentication and Authorization
    - **Property 70: Unauthenticated Request Rejection**
    - **Validates: Requirements 20.3**
  
  - [ ] 51.4 Write unit tests for Auth Middleware
    - Test JWT validation
    - Test role-based permission checks
    - Test HTTP 401 for missing token
    - Test HTTP 403 for insufficient permissions

- [ ] 52. Implement Input Validation and Error Handling
  - [ ] 52.1 Create validation middleware using express-validator
    - Validate all input parameters for each endpoint
    - Sanitize inputs to prevent SQL injection
    - Return HTTP 400 with descriptive error messages for invalid input
    - _Requirements: 20.2, 34.5_
  
  - [ ] 52.2 Create global error handler middleware
    - Catch all errors and return consistent JSON format
    - Return HTTP 500 with tracking ID for internal errors
    - Log all errors with stack trace and context
    - Integrate with error tracking service
    - _Requirements: 20.6, 20.7, 35.4_
  
  - [ ] 52.3 Write property tests for Error Handling
    - **Property 69: Invalid Input Error Response**
    - **Validates: Requirements 20.2**
    - **Property 71: Resource Not Found Response**
    - **Validates: Requirements 20.5**
    - **Property 72: Consistent Response Format**
    - **Validates: Requirements 20.7**
  
  - [ ] 52.4 Write unit tests for Error Handling
    - Test validation error responses
    - Test 404 error responses
    - Test 500 error responses with tracking ID
    - Test consistent error format

- [ ] 53. Implement Security Features
  - [ ] 53.1 Implement JWT token management
    - Set token expiration to 24 hours
    - Implement token refresh mechanism
    - Log all authentication failures
    - _Requirements: 34.1, 34.2, 34.8_
  
  - [ ] 53.2 Implement rate limiting
    - Add rate limiting middleware (100 requests per minute per user)
    - Return HTTP 429 for rate limit exceeded
    - _Requirements: 34.6_
  
  - [ ] 53.3 Implement database field encryption
    - Encrypt sensitive fields: GSTIN, PAN, bank account numbers
    - Use Supabase encryption features or application-level encryption
    - _Requirements: 34.7_
  
  - [ ] 53.4 Write unit tests for Security Features
    - Test token expiration
    - Test token refresh
    - Test rate limiting
    - Test authentication failure logging

- [ ] 54. Implement Performance Optimizations
  - [ ] 54.1 Configure database connection pooling
    - Set minimum 10 and maximum 100 connections
    - Configure connection timeout and idle timeout
    - _Requirements: 33.4_
  
  - [ ] 54.2 Implement query result caching
    - Cache frequently accessed reference data (categories, brands, locations)
    - Set cache TTL to 5 minutes
    - Invalidate cache on data updates
    - _Requirements: 33.5_
  
  - [ ] 54.3 Optimize database queries
    - Add indexes on frequently queried fields (already in schema)
    - Implement query pagination for large result sets
    - Use database partitioning for large tables (invoices, ledger entries, stock ledger)
    - _Requirements: 33.1, 33.2, 33.6_
  
  - [ ] 54.4 Write performance tests
    - Test product search response time (<200ms for 100k products)
    - Test invoice creation response time (<500ms)
    - Test concurrent transaction handling

- [ ] 55. Implement Health Check and Monitoring
  - [ ] 55.1 Create health check endpoints
    - GET /health - Return HTTP 200 when system is operational
    - GET /health/db - Check database connectivity
    - GET /metrics - Expose request count, response time, error rate
    - _Requirements: 35.1, 35.2, 35.3_
  
  - [ ] 55.2 Implement error logging and monitoring
    - Log all errors with stack trace and context
    - Integrate with error tracking service (e.g., Sentry)
    - Set up alerts for critical errors
    - _Requirements: 35.4, 35.5_
  
  - [ ] 55.3 Write unit tests for Health Check
    - Test health endpoint response
    - Test database connectivity check
    - Test metrics endpoint

- [ ] 56. Checkpoint - Security and monitoring validation
  - Ensure all tests pass, ask the user if questions arise.

### Phase 10: API Documentation and Testing

- [ ] 57. Create OpenAPI (Swagger) Documentation
  - [ ] 57.1 Generate OpenAPI specification for all endpoints
    - Document all request and response schemas
    - Include authentication and authorization requirements
    - Document error codes and error response formats
    - Include request and response examples
    - _Requirements: 32.1, 32.3, 32.4, 32.5_
  
  - [ ] 57.2 Document multi-module dependencies
    - Explicitly declare primary module for each endpoint
    - Document secondary modules affected by each operation
    - Document database tables touched by each operation
    - Document side effects and transaction boundaries
    - _Requirements: 32.2, 32.6_
  
  - [ ] 57.3 Set up Swagger UI
    - Integrate Swagger UI for interactive API documentation
    - Host at /api-docs endpoint
    - Enable "Try it out" functionality for testing

- [ ] 58. Complete Property-Based Test Suite
  - [ ] 58.1 Review all 76 correctness properties
    - Ensure each property has a corresponding property test
    - Verify all property tests reference design document property numbers
    - Configure all property tests to run 100 iterations minimum
    - _Requirements: All requirements_
  
  - [ ] 58.2 Run complete property test suite
    - Execute all property tests
    - Fix any failing tests
    - Achieve 100% property coverage
  
  - [ ] 58.3 Property tests for remaining properties
    - **Property 75: Unlimited Credit for No Limit**
    - **Validates: Requirements 27.4**

- [ ] 59. Complete Unit and Integration Test Suite
  - [ ] 59.1 Review unit test coverage
    - Ensure minimum 80% code coverage
    - Cover all edge cases and error conditions
    - Test all API endpoints
  
  - [ ] 59.2 Write integration tests for multi-module workflows
    - Test complete sales flow (invoice → stock → ledger → due → audit)
    - Test complete purchase flow (GRN → stock → cost → payable → audit)
    - Test complete payment flow (receipt → due → ledger → audit)
    - Test complete return flow (return → stock → ledger → due → audit)
  
  - [ ] 59.3 Run complete test suite
    - Execute all unit tests, property tests, and integration tests
    - Fix any failing tests
    - Generate coverage report

- [ ] 60. Checkpoint - Testing and documentation validation
  - Ensure all tests pass, ask the user if questions arise.

### Phase 11: Deployment and Final Integration

- [ ] 61. Create database migration scripts
  - Organize all SQL files in migrations directory
  - Create migration runner script with version tracking
  - Test migrations on clean database
  - Create rollback scripts for each migration
  - _Requirements: 19.1_

- [ ] 62. Set up environment configuration
  - Create .env.example with all required environment variables
  - Document Supabase connection settings
  - Document JWT secret configuration
  - Document database connection pool settings
  - Create separate configs for development, staging, production

- [ ] 63. Create deployment documentation
  - Write README.md with project overview and setup instructions
  - Document API endpoints and usage examples
  - Document database schema and relationships
  - Document event-driven architecture and multi-module flows
  - Create deployment guide for production

- [ ] 64. Set up CI/CD pipeline
  - Configure automated testing on every commit
  - Run linting and type checking
  - Run all unit tests, property tests, and integration tests
  - Generate and track coverage reports
  - Block merges on test failures

- [ ] 65. Perform end-to-end system testing
  - Test complete business workflows from UI perspective
  - Test all multi-module cascading effects
  - Test financial year locking enforcement
  - Test role-based access control across all modules
  - Test transaction rollback scenarios
  - Test concurrent user operations

- [ ] 66. Final checkpoint - Production readiness
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional property-based and unit tests that can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at module boundaries
- Property tests validate universal correctness properties across all inputs
- Unit tests validate specific examples, edge cases, and error conditions
- The implementation follows an event-driven architecture where single API operations trigger cascading effects across multiple modules
- All multi-table operations execute within database transactions to ensure atomicity
- Financial year locking is enforced at database level using triggers
- Row Level Security (RLS) ensures multi-tenancy and role-based access control

## Implementation Guidelines

1. **Transaction Management**: Always wrap multi-module operations in database transactions
2. **Error Handling**: Return descriptive error messages with appropriate HTTP status codes
3. **Audit Logging**: Log all create, update, delete operations using Audit_Logger
4. **Input Validation**: Validate all inputs before processing using express-validator
5. **Role-Based Access**: Check user permissions before executing operations
6. **Financial Year Lock**: Validate financial year is not locked before transactional operations
7. **Stock Validation**: Check stock availability before sales and returns
8. **GST Compliance**: Use GST_Engine for all GST calculations
9. **Double-Entry Bookkeeping**: Use Ledger_Engine for all financial transactions
10. **Testing**: Write property tests for universal properties and unit tests for specific scenarios
