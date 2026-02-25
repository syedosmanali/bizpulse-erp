# Implementation Plan: Comprehensive ERP Modules

## Overview

This implementation plan breaks down the development of 22 comprehensive ERP modules into discrete, incremental coding tasks. The system uses Flask (Python) as the backend framework with Supabase (PostgreSQL) as the database, and vanilla JavaScript for the mobile-optimized frontend. Each task builds on previous work, with checkpoints to ensure quality and allow for user feedback.

The implementation follows a phased approach: foundation setup, core modules (authentication, company setup), sales and inventory management, purchase management, CRM and parties, financial management and reporting, administration, and finally mobile optimization and testing.

## Tasks

- [-] 1. Set up project foundation and database schema
  - Create Flask application structure with blueprint architecture
  - Set up Supabase connection and configuration
  - Create all database tables with proper indexes and constraints
  - Implement Row-Level Security (RLS) policies for multi-tenant isolation
  - Set up error handling middleware and response format
  - Configure CORS, session management, and security headers
  - _Requirements: 24.1, 24.2, 24.3, 24.6, 24.7, 24.8_

- [x] 1.1 Write property test for multi-tenant data isolation
  - **Property 30: Multi-Tenant Data Isolation**
  - **Validates: Requirements 24.3**

- [x] 2. Implement authentication and security module
  - [x] 2.1 Create authentication blueprint with login, logout, and password change endpoints
    - Implement bcrypt password hashing for secure storage
    - Create session management with 24-hour token validity
    - Support three user types: Admin, Operator, Business Owner
    - Return appropriate error messages for invalid credentials within 200ms
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.6, 1.7, 1.8_


  - [x] 2.2 Write property tests for authentication
    - **Property 1: Login Credential Validation**
    - **Validates: Requirements 1.2**

  - [x] 2.3 Write property test for password security
    - **Property 2: Password Storage Security**
    - **Validates: Requirements 1.7**

  - [x] 2.4 Implement role-based access control (RBAC) decorator
    - Create permission checking decorator for route protection
    - Implement session validation middleware
    - Handle session expiration with redirect to login
    - _Requirements: 1.5, 1.6_

- [x] 3. Create base UI components and navigation
  - [ ] 3.1 Implement collapsible sidebar navigation
    - Create HTML structure with module/submodule hierarchy
    - Implement CSS styling with blue gradient theme
    - Add JavaScript for toggle functionality and module expansion
    - Make responsive for mobile (transform on small screens)
    - Support swipe gestures to open/close sidebar
    - _Requirements: 23.2, 23.6, 23.7_

  - [ ] 3.2 Create reusable form components
    - Build form builder with validation support
    - Implement touch-optimized input fields (min 44px height)
    - Add date pickers and dropdown with search
    - Implement auto-save to LocalStorage for drafts
    - _Requirements: 23.2, 23.7_

  - [ ] 3.3 Create data table component with mobile responsiveness
    - Build table with pagination (50 items per page)
    - Add search, filter, and sort functionality
    - Implement virtual scrolling for long lists
    - Create card view for mobile screens
    - Add lazy loading for performance
    - _Requirements: 23.3, 23.7_


  - [ ] 3.4 Create dashboard widget components
    - Implement metric cards for key statistics
    - Create chart widgets for trends visualization
    - Build list widgets for recent transactions
    - Add alert widgets for notifications
    - _Requirements: 21.1, 21.2, 21.3, 21.4, 21.5, 21.6, 21.7, 21.8_

- [ ] 4. Checkpoint - Verify foundation and base components
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement company and firm setup module
  - [x] 5.1 Create company setup blueprint and database service
    - Implement GET /api/erp/company endpoint to retrieve company profile
    - Implement POST /api/erp/company endpoint to save/update company details
    - Store company name, address, contact details, GST number, PAN, financial year
    - Support logo upload and storage
    - Configure invoice settings (prefix, starting number)
    - _Requirements: 2.1, 2.2, 2.4, 2.5, 2.6_

  - [x] 5.2 Write property test for GST number validation
    - **Property 3: GST Number Format Validation**
    - **Validates: Requirements 2.3**

  - [x] 5.3 Create company setup UI screen
    - Build form with all company fields
    - Implement GST and PAN number validation
    - Add logo upload with preview
    - Display warning on dashboard if profile incomplete
    - _Requirements: 2.1, 2.2, 2.3, 2.6, 2.7_

- [x] 6. Implement bank management module
  - [x] 6.1 Create bank management blueprint and endpoints
    - Implement GET /api/erp/banks endpoint to list all banks
    - Implement POST /api/erp/banks endpoint to add new bank
    - Implement PUT /api/erp/banks/{id} endpoint to edit bank details
    - Store bank name, account number, IFSC code, branch, account type
    - Support marking one bank as default
    - Prevent deletion of banks with associated transactions
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_


  - [x] 6.2 Write property test for IFSC code validation
    - **Property 4: IFSC Code Format Validation**
    - **Validates: Requirements 3.7**

  - [x] 6.3 Create bank management UI screen
    - Build bank list view with add/edit functionality
    - Implement IFSC code format validation
    - Add default bank selection toggle
    - Display validation errors for invalid formats
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.7_

- [x] 7. Implement product and item master module
  - [x] 7.1 Create product management blueprint and endpoints
    - Implement GET /api/erp/products endpoint with search, filter, sort
    - Implement POST /api/erp/products endpoint to add new product
    - Implement PUT /api/erp/products/{id} endpoint to edit product
    - Implement DELETE /api/erp/products/{id} endpoint for soft deletion
    - Store product code, name, category, brand, HSN code, GST rate, unit, prices
    - Track current stock, minimum stock level, barcode
    - Support batch and expiry tracking flags
    - Enforce unique product codes per user
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.6, 9.7, 9.8, 9.9_

  - [x] 7.2 Write property tests for product management
    - **Property 15: HSN Code Format Validation**
    - **Validates: Requirements 9.5**

  - [x] 7.3 Write property test for product code uniqueness
    - **Property 16: Product Code Uniqueness Per User**
    - **Validates: Requirements 9.8**

  - [x] 7.4 Create product master UI screen
    - Build product list with search, filter by category/brand
    - Create add/edit product form with all fields
    - Implement HSN code validation (4, 6, or 8 digits)
    - Add category and brand management
    - Display current stock levels
    - _Requirements: 9.1, 9.2, 9.3, 9.5, 9.6, 9.7, 9.9_


- [-] 8. Implement inventory and stock management module
  - [x] 8.1 Create stock transaction service and endpoints
    - Implement POST /api/erp/stock/adjustment endpoint for manual adjustments
    - Implement GET /api/erp/stock/current endpoint to view current stock
    - Implement GET /api/erp/stock/low-stock endpoint for alerts
    - Record all stock movements in erp_stock_transactions table
    - Track transaction type (in, out, adjustment), quantity, reference
    - Calculate available stock (current minus reserved)
    - Generate low stock alerts when quantity < min_stock_level
    - Prevent negative stock unless configured to allow
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9_

  - [ ] 8.2 Write property tests for stock management
    - **Property 17: Low Stock Alert Generation**
    - **Validates: Requirements 10.4**

  - [ ] 8.3 Write property test for negative stock prevention
    - **Property 18: Negative Stock Prevention**
    - **Validates: Requirements 10.9**

  - [ ] 8.4 Create stock management UI screens
    - Build current stock view with product list
    - Create stock adjustment form with reason field
    - Display low stock alerts on dashboard
    - Show stock transaction history with filters
    - Add visual indicators for low stock items
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.6, 10.7_

- [ ] 9. Implement batch and expiry management module
  - [ ] 9.1 Create batch management service and endpoints
    - Implement POST /api/erp/batches endpoint to create batch records
    - Implement GET /api/erp/batches endpoint to list batches
    - Implement GET /api/erp/batches/near-expiry endpoint for expiring products
    - Store batch number, manufacturing date, expiry date, quantity
    - Require batch number for products with has_batch_tracking=true
    - Require expiry date for products with has_expiry_tracking=true
    - Implement FEFO (First Expiry First Out) logic for batch selection
    - Flag expired batches and prevent their sale
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8_


  - [ ] 9.2 Write property test for expired batch prevention
    - **Property 19: Expired Batch Sale Prevention**
    - **Validates: Requirements 11.7**

  - [ ] 9.3 Create batch management UI screens
    - Build batch list view with expiry date display
    - Create batch entry form during stock inward
    - Display near-expiry report (30 days)
    - Show batch-wise stock report
    - Add visual alerts for expired batches
    - _Requirements: 11.1, 11.2, 11.4, 11.8_

- [ ] 10. Implement barcode management module
  - [ ] 10.1 Create barcode service and endpoints
    - Implement POST /api/erp/products/{id}/barcode endpoint to generate barcode
    - Implement GET /api/erp/products/barcode/{code} endpoint for lookup
    - Generate barcodes in EAN-13 or Code-128 format
    - Store barcode as text and generate image representation
    - Support barcode scanning via device camera
    - Validate barcode uniqueness per user account
    - Complete barcode lookup within 500ms
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8_

  - [ ] 10.2 Write property test for barcode uniqueness
    - **Property 20: Barcode Uniqueness Per User**
    - **Validates: Requirements 12.6**

  - [ ] 10.3 Create barcode UI features
    - Add barcode generation button in product form
    - Implement barcode label printing functionality
    - Create barcode scanner interface using device camera
    - Add manual barcode entry field in billing
    - Support bulk barcode generation for multiple products
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.7_

- [ ] 11. Checkpoint - Verify product and inventory modules
  - Ensure all tests pass, ask the user if questions arise.


- [-] 12. Implement customer management module
  - [x] 12.1 Create customer management blueprint and endpoints
    - Implement GET /api/erp/customers endpoint with search by name/phone
    - Implement POST /api/erp/customers endpoint to add customer
    - Implement PUT /api/erp/customers/{id} endpoint to edit customer
    - Store customer name, phone, email, address, GST number
    - Track credit limit, credit days, outstanding balance, total purchases
    - Support customer categorization (Regular, VIP, Wholesale)
    - Perform phone-based lookup during billing
    - Calculate outstanding as: total credit minus paid amount
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7, 13.8, 13.9_

  - [ ] 12.2 Write property tests for customer management
    - **Property 21: Credit Limit Enforcement**
    - **Validates: Requirements 13.6**

  - [ ] 12.3 Write property test for customer outstanding calculation
    - **Property 22: Customer Outstanding Calculation**
    - **Validates: Requirements 13.8**

  - [ ] 12.4 Create customer management UI screens
    - Build customer list with search functionality
    - Create add/edit customer form with all fields
    - Display customer transaction history
    - Show outstanding balance prominently
    - Add customer quick-lookup in billing screen
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.7_

- [ ] 13. Implement vendor and supplier management module
  - [ ] 13.1 Create vendor management blueprint and endpoints
    - Implement GET /api/erp/vendors endpoint with search
    - Implement POST /api/erp/vendors endpoint to add vendor
    - Implement PUT /api/erp/vendors/{id} endpoint to edit vendor
    - Store vendor name, phone, email, address, GST number, payment terms
    - Track outstanding balance and total purchases
    - Calculate outstanding as: total purchases minus payments made
    - Link purchases to vendor accounts
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7, 14.8_


  - [ ] 13.2 Write property test for supplier outstanding calculation
    - **Property 23: Supplier Outstanding Calculation**
    - **Validates: Requirements 14.5**

  - [ ] 13.3 Create vendor management UI screens
    - Build vendor list with search
    - Create add/edit vendor form
    - Display vendor transaction history
    - Show supplier-wise purchase summary
    - Display outstanding amounts
    - _Requirements: 14.1, 14.2, 14.3, 14.6, 14.7, 14.8_

- [-] 14. Implement invoice and billing module
  - [x] 14.1 Create invoice service with stock and customer updates
    - Implement GET /api/erp/invoices endpoint with pagination, filters
    - Implement POST /api/erp/invoices endpoint to create invoice
    - Implement PUT /api/erp/invoices/{id} endpoint to edit draft invoices
    - Implement DELETE /api/erp/invoices/{id} endpoint for draft deletion
    - Generate unique invoice numbers using prefix and sequence
    - Calculate GST amounts based on product tax rates
    - Support credit invoices with due dates
    - Use database transactions for atomicity (invoice + stock + customer balance)
    - Reduce stock quantities when invoice is created
    - Restore stock quantities when invoice is deleted
    - Update customer outstanding balance
    - Prevent editing of finalized invoices
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.10, 4.11, 4.12, 4.13, 24.6_

  - [ ] 14.2 Write property tests for invoice operations
    - **Property 5: Invoice Number Uniqueness**
    - **Validates: Requirements 4.3**

  - [ ] 14.3 Write property test for invoice stock reduction
    - **Property 6: Invoice Creation Stock Reduction**
    - **Validates: Requirements 4.11**

  - [ ] 14.4 Write property test for invoice deletion round trip
    - **Property 7: Invoice Deletion Stock Restoration**
    - **Validates: Requirements 4.12**


  - [ ] 14.5 Write property test for transaction atomicity
    - **Property 31: Multi-Table Transaction Atomicity**
    - **Validates: Requirements 24.6**

  - [x] 14.6 Implement PDF generation service for invoices
    - Create PDF generation using ReportLab or WeasyPrint
    - Include company logo and GST details
    - Format invoice with items, quantities, rates, taxes
    - Implement GET /api/erp/invoices/{id}/pdf endpoint
    - Generate GST-compliant invoice layout
    - _Requirements: 4.7, 4.8_

  - [x] 14.7 Create invoice UI screens
    - Build invoice list with search, filter, pagination
    - Create invoice form with customer selection and item entry
    - Implement dynamic item rows with add/remove
    - Auto-calculate totals, taxes, and discounts
    - Add payment mode selection (cash, UPI, card, cheque)
    - Support credit invoice toggle with due date
    - Display invoice history with status indicators
    - Add share options (WhatsApp, email, download)
    - _Requirements: 4.1, 4.2, 4.4, 4.5, 4.6, 4.7, 4.8, 4.10, 4.13_

  - [-] 14.8 Implement invoice returns with credit notes
    - Create POST /api/erp/invoices/{id}/return endpoint
    - Generate credit note document
    - Restore stock for returned items
    - Update customer outstanding
    - _Requirements: 4.9_

- [ ] 15. Implement challan and delivery note module
  - [ ] 15.1 Create challan management blueprint and endpoints
    - Implement GET /api/erp/challans endpoint with filters
    - Implement POST /api/erp/challans endpoint to create challan
    - Implement PUT /api/erp/challans/{id} endpoint to edit challan
    - Implement POST /api/erp/challans/{id}/convert endpoint for invoice conversion
    - Generate unique challan numbers
    - Store customer and item details without affecting stock
    - Preserve all data during conversion to invoice
    - Mark challan as "Converted" after invoice creation
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.7, 5.8_


  - [ ] 15.2 Write property tests for challan operations
    - **Property 8: Challan to Invoice Conversion Preserves Data**
    - **Validates: Requirements 5.4**

  - [ ] 15.3 Write property test for challan stock behavior
    - **Property 9: Challan Does Not Affect Stock**
    - **Validates: Requirements 5.8**

  - [ ] 15.4 Create challan UI screens
    - Build challan list with status filter
    - Create challan form similar to invoice
    - Add one-click convert to invoice button
    - Generate challan reports by date range
    - Display conversion status
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.6, 5.7_

- [ ] 16. Checkpoint - Verify sales and customer modules
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 17. Implement purchase management module
  - [ ] 17.1 Create purchase entry blueprint and endpoints
    - Implement GET /api/erp/purchases endpoint with filters
    - Implement POST /api/erp/purchases endpoint to record purchase
    - Implement PUT /api/erp/purchases/{id} endpoint to edit purchase
    - Implement POST /api/erp/purchases/{id}/return endpoint for returns
    - Store vendor, bill number, bill date, items, amounts
    - Support bill image/PDF upload
    - Increase stock quantities when purchase is recorded
    - Decrease stock quantities for purchase returns
    - Link purchases to vendor accounts for outstanding tracking
    - Calculate total with taxes
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8_

  - [ ] 17.2 Write property tests for purchase operations
    - **Property 10: Purchase Increases Stock**
    - **Validates: Requirements 6.5**

  - [ ] 17.3 Write property test for purchase returns
    - **Property 11: Purchase Return Decreases Stock**
    - **Validates: Requirements 6.6**


  - [ ] 17.4 Create purchase entry UI screens
    - Build purchase list with search and filters
    - Create purchase entry form with vendor selection
    - Add item entry with quantities and costs
    - Support bill image upload with preview
    - Display purchase history
    - Add purchase return functionality
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.7, 6.8_

- [ ] 18. Implement purchase order (PO) module
  - [ ] 18.1 Create purchase order blueprint and endpoints
    - Implement GET /api/erp/purchase-orders endpoint with status filters
    - Implement POST /api/erp/purchase-orders endpoint to create PO
    - Implement PUT /api/erp/purchase-orders/{id} endpoint to edit draft PO
    - Implement POST /api/erp/purchase-orders/{id}/approve endpoint for approval
    - Generate unique PO numbers
    - Support PO approval workflow (Draft, Pending, Approved, Rejected)
    - Track PO status (Open, Partially Received, Fully Received, Closed)
    - Prevent editing of approved POs
    - Generate PDF format PO documents
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8_

  - [ ] 18.2 Write property test for approved PO immutability
    - **Property 12: Approved Purchase Orders Are Immutable**
    - **Validates: Requirements 7.8**

  - [ ] 18.3 Create purchase order UI screens
    - Build PO list with status filters
    - Create PO form with vendor and item selection
    - Add approval workflow interface
    - Display PO status tracking
    - Generate and download PO PDFs
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_

- [ ] 19. Implement goods receipt note (GRN) module
  - [ ] 19.1 Create GRN blueprint and endpoints
    - Implement GET /api/erp/grn endpoint to list GRNs
    - Implement GET /api/erp/purchase-orders/{id}/pending endpoint for pending items
    - Implement POST /api/erp/grn endpoint to create GRN
    - Link GRN to purchase order
    - Support partial receipt of PO items
    - Increase stock quantities by received amount
    - Update PO status based on received quantities
    - Prevent receiving quantities exceeding PO quantities
    - Record GRN date, time, and receiving user
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_


  - [ ] 19.2 Write property tests for GRN operations
    - **Property 13: GRN Increases Stock**
    - **Validates: Requirements 8.4**

  - [ ] 19.3 Write property test for GRN quantity validation
    - **Property 14: GRN Cannot Exceed PO Quantities**
    - **Validates: Requirements 8.8**

  - [ ] 19.4 Create GRN UI screens
    - Build GRN list view
    - Create GRN form linked to PO
    - Display pending PO items for receiving
    - Support partial quantity entry
    - Show GRN history with PO mapping
    - _Requirements: 8.1, 8.2, 8.3, 8.6, 8.7_

- [ ] 20. Implement CRM (leads and follow-ups) module
  - [ ] 20.1 Create CRM blueprint and endpoints
    - Implement GET /api/erp/leads endpoint with status filters
    - Implement POST /api/erp/leads endpoint to add lead
    - Implement PUT /api/erp/leads/{id} endpoint to update lead
    - Implement POST /api/erp/leads/{id}/convert endpoint to convert to customer
    - Support lead status (New, Contacted, Qualified, Converted, Lost)
    - Store lead name, phone, email, source, notes
    - Schedule follow-ups with date and time
    - Create reminder notifications for follow-up dates
    - Maintain customer interaction history
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7, 15.8_

  - [ ] 20.2 Create CRM UI screens
    - Build lead pipeline view with status-wise counts
    - Create lead entry form with all fields
    - Add follow-up scheduling interface
    - Display follow-up calendar and reminders
    - Implement lead conversion to customer
    - Show customer interaction history
    - Add filters by date range and status
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7, 15.8_

- [ ] 21. Checkpoint - Verify purchase and CRM modules
  - Ensure all tests pass, ask the user if questions arise.


- [-] 22. Implement payment management module
  - [x] 22.1 Create payment management blueprint and endpoints
    - Implement GET /api/erp/payments endpoint with filters (type, date range)
    - Implement POST /api/erp/payments endpoint to record payment
    - Support payment types: received (from customer), paid (to vendor)
    - Support payment methods: Cash, UPI, Card, Cheque, Bank Transfer
    - Support mixed payments using multiple methods (store in JSONB)
    - Record reference numbers for digital payments
    - Track payment status (Pending, Completed, Failed)
    - Update customer or supplier outstanding when payment recorded
    - Link payments to specific invoices or bills
    - Generate payment receipt in PDF format
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7, 16.8_

  - [ ] 22.2 Write property test for payment outstanding update
    - **Property 24: Payment Updates Outstanding Balance**
    - **Validates: Requirements 16.5**

  - [ ] 22.3 Create payment management UI screens
    - Build payment list with type and date filters
    - Create payment entry form with party selection
    - Support single and mixed payment mode entry
    - Add reference number field for digital payments
    - Link payment to specific invoice/bill
    - Generate and download payment receipts
    - Display payment history
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.6, 16.7, 16.8_

- [ ] 23. Implement income and expense tracking module
  - [ ] 23.1 Create income/expense blueprint and endpoints
    - Implement GET /api/erp/transactions endpoint with type filter
    - Implement POST /api/erp/transactions endpoint to record transaction
    - Support transaction types: income, expense
    - Support income categories: Sales, Services, Other Income
    - Support expense categories: Rent, Utilities, Salaries, Supplies, Other
    - Allow custom category creation
    - Store amount, category, date, description, payment mode
    - Calculate net income as: total income minus total expenses
    - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7, 17.8_


  - [ ] 23.2 Write property test for net income calculation
    - **Property 25: Net Income Calculation**
    - **Validates: Requirements 17.8**

  - [ ] 23.3 Create income/expense UI screens
    - Build transaction list with type filter
    - Create income entry form with categories
    - Create expense entry form with categories
    - Add custom category management
    - Generate income report by date range and category
    - Generate expense report by date range and category
    - Display net income summary
    - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7_

- [ ] 24. Implement basic accounting module
  - [ ] 24.1 Create accounting reports service and endpoints
    - Implement GET /api/erp/reports/sales-summary endpoint
    - Implement GET /api/erp/reports/purchase-summary endpoint
    - Implement GET /api/erp/reports/profit-loss endpoint
    - Calculate sales summary: total sales, tax collected, payment breakdown
    - Calculate purchase summary: total purchases, tax paid, supplier breakdown
    - Calculate gross profit: sales revenue minus cost of goods sold
    - Calculate net profit: gross profit minus expenses
    - Support date range filtering for all reports
    - Display month-wise and year-wise comparisons
    - Export reports in PDF and Excel formats
    - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 18.7, 18.8_

  - [ ] 24.2 Write property tests for accounting calculations
    - **Property 26: Gross Profit Calculation**
    - **Validates: Requirements 18.4**

  - [ ] 24.3 Write property test for net profit calculation
    - **Property 27: Net Profit Calculation**
    - **Validates: Requirements 18.5**

  - [ ] 24.4 Create accounting reports UI screens
    - Build sales summary report with filters
    - Create purchase summary report
    - Display profit & loss statement
    - Add month-wise and year-wise comparison views
    - Implement export to PDF and Excel
    - _Requirements: 18.1, 18.2, 18.3, 18.6, 18.7, 18.8_


- [ ] 25. Implement comprehensive reporting module
  - [ ] 25.1 Create reporting service and endpoints
    - Implement GET /api/erp/reports/sales endpoint with filters
    - Implement GET /api/erp/reports/purchase endpoint with filters
    - Implement GET /api/erp/reports/inventory endpoint
    - Implement GET /api/erp/reports/financial endpoint
    - Implement GET /api/erp/reports/customer-outstanding endpoint with aging
    - Implement GET /api/erp/reports/supplier-outstanding endpoint
    - Implement GET /api/erp/reports/gst endpoint with tax breakdown
    - Implement GET /api/erp/reports/export endpoint for PDF/Excel/CSV
    - Support filters: date range, customer, product, supplier, category
    - Calculate aging analysis: 0-30, 31-60, 61-90, 90+ days
    - Generate GST report with CGST, SGST, IGST breakdown
    - Support report scheduling for automatic generation
    - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.5, 20.6, 20.7, 20.8, 20.9_

  - [ ] 25.2 Create reporting UI screens
    - Build sales report with multiple filters
    - Create purchase report with filters
    - Display inventory report with stock value
    - Show financial report with income/expenses
    - Create customer outstanding report with aging
    - Display supplier outstanding report
    - Generate GST report with tax breakdown
    - Add graphical charts for trends
    - Implement export functionality (PDF, Excel, CSV)
    - Add report scheduling interface
    - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.5, 20.6, 20.7, 20.8, 20.9, 20.10_

- [ ] 26. Implement dashboard with widgets
  - [ ] 26.1 Create dashboard data aggregation service
    - Implement GET /api/erp/dashboard/metrics endpoint
    - Calculate today's sales amount
    - Calculate total customer outstanding
    - Count low stock items
    - Count pending purchase orders
    - Identify top selling products
    - Generate sales trend data for last 30 days
    - Fetch recent transactions list
    - Identify expiring products
    - _Requirements: 21.1, 21.2, 21.3, 21.4, 21.5, 21.6, 21.7, 21.8_


  - [ ] 26.2 Create dashboard UI with widgets
    - Build metric cards for key statistics
    - Create sales trend chart widget
    - Display recent transactions list widget
    - Show low stock alerts widget
    - Display pending PO count widget
    - Show top selling products widget
    - Add expiring products alert widget
    - Implement widget refresh on navigation
    - Allow widget visibility customization
    - _Requirements: 21.1, 21.2, 21.3, 21.4, 21.5, 21.6, 21.7, 21.8, 21.9, 21.10_

- [ ] 27. Checkpoint - Verify financial and reporting modules
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 28. Implement staff and operator management module
  - [ ] 28.1 Create staff management blueprint and endpoints
    - Implement GET /api/erp/staff endpoint to list staff
    - Implement POST /api/erp/staff endpoint to create operator account
    - Implement PUT /api/erp/staff/{id} endpoint to edit staff details
    - Implement POST /api/erp/staff/{id}/activate endpoint to activate/deactivate
    - Store staff name, username, password (hashed), role, salary, joining date
    - Support role-based permissions stored in JSONB
    - Track login history with date and time
    - Enforce unique usernames per business owner account
    - Require password change on first login
    - Log operator actions for audit trail
    - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5, 19.6, 19.7, 19.8_

  - [ ] 28.2 Write property test for staff username uniqueness
    - **Property 28: Staff Username Uniqueness Per User**
    - **Validates: Requirements 19.6**

  - [ ] 28.3 Create staff management UI screens
    - Build staff list with status indicators
    - Create add/edit staff form with role selection
    - Implement permission configuration interface
    - Display login history
    - Add activate/deactivate toggle
    - Show audit trail of operator actions
    - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5, 19.8_


- [ ] 29. Implement backup and settings module
  - [ ] 29.1 Create backup service and endpoints
    - Implement GET /api/erp/backup/export endpoint to generate backup
    - Implement POST /api/erp/backup/restore endpoint to restore from backup
    - Generate backup in JSON format with timestamp
    - Include all user data tables in backup
    - Validate backup file integrity before restore
    - Display warning about data overwrite during restore
    - _Requirements: 22.1, 22.2, 22.3, 22.4, 22.10_

  - [ ] 29.2 Write property test for backup integrity validation
    - **Property 29: Backup File Integrity Validation**
    - **Validates: Requirements 22.10**

  - [ ] 29.3 Create settings management endpoints
    - Implement GET /api/erp/settings endpoint to retrieve settings
    - Implement POST /api/erp/settings endpoint to save settings
    - Support invoice template settings (header, footer, terms)
    - Configure default values (payment method, tax rate, currency)
    - Support theme configuration (light/dark mode)
    - Configure date format and timezone
    - Manage notification preferences
    - _Requirements: 22.5, 22.6, 22.7, 22.8, 22.9_

  - [ ] 29.4 Create backup and settings UI screens
    - Build backup/restore interface with download button
    - Add restore file upload with validation
    - Display data overwrite warning
    - Create settings form for invoice templates
    - Add default values configuration
    - Implement theme toggle
    - Configure date format and timezone
    - Manage notification preferences
    - _Requirements: 22.1, 22.2, 22.3, 22.4, 22.5, 22.6, 22.7, 22.8, 22.9_

- [ ] 30. Implement mobile optimization and performance enhancements
  - [ ] 30.1 Implement code splitting and lazy loading
    - Split JavaScript into module-specific bundles
    - Implement dynamic module loading on demand
    - Lazy load dashboard widgets
    - Minimize JavaScript bundle size to under 2MB
    - _Requirements: 23.1, 23.8_


  - [ ] 30.2 Implement caching and offline support
    - Create data caching service with 5-minute TTL
    - Implement LocalStorage caching for frequently accessed data
    - Create service worker for offline asset caching
    - Build offline queue manager for pending operations
    - Implement auto-sync when network is restored
    - Display offline indicator and pending sync count
    - Handle sync conflicts gracefully
    - _Requirements: 23.4, 23.9, 23.10_

  - [ ] 30.3 Optimize images and assets
    - Implement responsive image loading with srcset
    - Add lazy loading for images
    - Compress and optimize logo and product images
    - Use CDN for static assets
    - _Requirements: 23.1_

  - [ ] 30.4 Implement touch optimizations
    - Add swipe gesture detection for sidebar
    - Ensure minimum 44px touch targets for all interactive elements
    - Remove tap highlight and add custom feedback
    - Optimize touch event handlers
    - _Requirements: 23.2, 23.7_

  - [ ] 30.5 Implement performance monitoring
    - Add page load time tracking
    - Monitor API response times
    - Track barcode scan performance (<500ms)
    - Ensure page renders within 1 second on 4G
    - Add loading indicators for data fetch operations
    - _Requirements: 23.1, 23.5_

- [ ] 31. Implement security enhancements
  - [ ] 31.1 Add security middleware and configurations
    - Configure Flask session with secure cookies (HTTPS only, HttpOnly)
    - Implement CORS with allowed origins
    - Add rate limiting to sensitive endpoints (5 login attempts per minute)
    - Force HTTPS in production with Talisman
    - Implement Content Security Policy headers
    - _Requirements: 1.7, 24.8_


  - [ ] 31.2 Implement input validation and sanitization
    - Create sanitization functions for text, email, phone, GST, IFSC
    - Remove HTML tags to prevent XSS attacks
    - Use parameterized queries for all database operations
    - Validate all user inputs on server side
    - _Requirements: 24.8_

  - [ ] 31.3 Implement audit logging
    - Create audit_log table for security events
    - Log all critical actions (create, edit, delete)
    - Record user ID, action, resource type, IP address, user agent
    - Implement audit log viewing for admins
    - _Requirements: 19.8_

  - [ ] 31.4 Implement sensitive data encryption
    - Set up encryption key management
    - Encrypt bank account numbers before storage
    - Decrypt data when retrieving for authorized users
    - _Requirements: 3.1_

- [ ] 32. Wire all modules together and integrate navigation
  - [ ] 32.1 Register all blueprints in main Flask application
    - Import and register all module blueprints
    - Configure blueprint URL prefixes
    - Set up shared services (database, PDF, notifications)
    - Configure error handlers globally
    - _Requirements: All modules_

  - [ ] 32.2 Complete sidebar navigation with all modules
    - Add all 22 modules to sidebar hierarchy
    - Implement module expansion/collapse state persistence
    - Add active state highlighting for current page
    - Ensure mobile responsiveness
    - _Requirements: All modules_

  - [ ] 32.3 Implement cross-module integrations
    - Link invoice creation to stock updates
    - Connect payments to customer/vendor outstanding
    - Integrate challan conversion to invoice
    - Link GRN to purchase orders and stock
    - Connect CRM lead conversion to customer creation
    - _Requirements: 4.11, 4.12, 5.4, 8.4, 15.5, 16.5_


- [ ] 33. Checkpoint - Verify complete system integration
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 34. Create deployment configuration
  - [ ] 34.1 Set up production environment configuration
    - Create gunicorn.conf.py with worker configuration
    - Set up environment variables for production
    - Configure Nginx as reverse proxy with SSL
    - Set up load balancing for multiple app servers
    - Configure static file serving with caching
    - _Requirements: 24.1, 24.2_

  - [ ] 34.2 Implement logging and monitoring
    - Configure rotating file handler for application logs
    - Set up error logging with stack traces
    - Implement performance monitoring
    - Add health check endpoint
    - _Requirements: 24.9_

  - [ ] 34.3 Create database migration scripts
    - Write SQL scripts for initial schema setup
    - Create RLS policies for all tables
    - Add indexes for query performance
    - Create audit log table
    - _Requirements: 24.3, 24.7_

- [ ] 35. Final testing and quality assurance
  - [ ] 35.1 Run complete property-based test suite
    - Execute all 31 property tests with 100+ iterations each
    - Verify all correctness properties pass
    - Document any edge cases discovered
    - _Requirements: All correctness properties_

  - [ ] 35.2 Run integration tests for critical workflows
    - Test complete invoice creation workflow
    - Test purchase order to GRN workflow
    - Test challan to invoice conversion
    - Test payment recording and outstanding updates
    - Test lead conversion to customer
    - _Requirements: 4.11, 5.4, 8.4, 15.5, 16.5_


  - [ ] 35.3 Run performance tests
    - Verify page load times <1 second on 4G
    - Test barcode scan performance <500ms
    - Verify virtual scrolling for lists >50 items
    - Test offline mode and sync functionality
    - Measure JavaScript bundle size <2MB
    - _Requirements: 23.1, 23.3, 23.8, 23.9, 23.10_

  - [ ] 35.4 Run security tests
    - Verify RLS policies prevent cross-user data access
    - Test SQL injection prevention
    - Verify XSS protection
    - Test rate limiting on login endpoint
    - Verify HTTPS enforcement
    - Test session expiration and timeout
    - _Requirements: 1.6, 24.3, 24.8_

  - [ ] 35.5 Run mobile responsiveness tests
    - Test on 4-inch to 7-inch screen sizes
    - Verify touch target sizes (min 44px)
    - Test swipe gestures for sidebar
    - Verify responsive layouts (mobile/tablet/desktop)
    - Test offline functionality
    - _Requirements: 23.2, 23.6, 23.7, 23.9_

- [ ] 36. Final checkpoint - Complete system verification
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional testing tasks and can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation and allow for user feedback
- Property tests validate universal correctness properties across all inputs
- Integration tests validate end-to-end workflows across multiple modules
- The implementation uses Python/Flask backend with Supabase PostgreSQL database
- Frontend uses vanilla JavaScript with mobile-first responsive design
- All modules follow consistent blueprint architecture pattern
- Database transactions ensure atomicity for multi-table operations
- Row-Level Security (RLS) ensures multi-tenant data isolation
