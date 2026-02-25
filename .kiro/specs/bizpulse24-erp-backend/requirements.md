# Requirements Document: BizPulse24 ERP Backend System

## Introduction

BizPulse24 is a production-ready ERP backend system designed for Indian retail businesses. The system provides comprehensive business management capabilities including inventory management, sales and billing, purchase management, party management, financial accounting, GST compliance, and reporting. The system is built on Supabase PostgreSQL with multi-user support and role-based access control, following an event-driven architecture where single API operations trigger cascading effects across multiple modules.

## Glossary

- **API_Server**: The backend REST API service built with Node.js/TypeScript or Python FastAPI
- **Database**: Supabase PostgreSQL database instance
- **Auth_Service**: Supabase Authentication service providing JWT-based authentication
- **Inventory_Module**: Module managing products, stock, categories, brands, and stock movements
- **Sales_Module**: Module managing invoices, POS billing, deliveries, returns, and refunds
- **Purchase_Module**: Module managing purchase orders, goods receipt notes, and purchase returns
- **Finance_Module**: Module managing payments, expenses, ledgers, and financial reports
- **Party_Module**: Module managing customer and vendor master data
- **GST_Engine**: Component calculating and storing GST breakup (CGST, SGST, IGST)
- **Ledger_Engine**: Component managing double-entry accounting ledger entries
- **Audit_Logger**: Component recording all system activities and data changes
- **RLS_Policy**: Row Level Security policy enforced at database level
- **Financial_Year**: Accounting period with start and end dates, can be locked to prevent modifications
- **Transaction**: Database transaction ensuring atomicity of multi-table operations
- **Stock_Ledger**: Record of all stock movements (in/out) with timestamps
- **Customer_Due**: Outstanding amount owed by a customer for credit sales
- **Vendor_Payable**: Outstanding amount owed to a vendor for credit purchases
- **GRN**: Goods Receipt Note documenting received purchase items
- **HSN_Code**: Harmonized System of Nomenclature code for GST classification
- **Batch**: Inventory batch with unique identifier and expiry date
- **MRP**: Maximum Retail Price
- **Cost_Price**: Purchase price of an item
- **Selling_Price**: Price at which an item is sold
- **Credit_Sale**: Sale where payment is deferred, creating customer due
- **Cash_Sale**: Sale with immediate payment
- **POS**: Point of Sale billing interface
- **Challan**: Delivery note without invoice
- **Invoice_Template**: Customizable format for invoice generation
- **Role**: User permission level (Owner, Admin, Staff)
- **Module_Action**: Primary operation performed by an API endpoint
- **Side_Effect**: Secondary operation triggered automatically by a module action
- **Soft_Delete**: Marking records as deleted without physical removal

## Requirements

### Requirement 1: Company Setup and Configuration

**User Story:** As a business owner, I want to configure my company details and GST information, so that the system can generate compliant invoices and reports.

#### Acceptance Criteria

1. THE API_Server SHALL provide endpoints to create and update company profile including name, address, GSTIN, PAN, and contact details
2. THE Database SHALL store exactly one active company profile per tenant
3. WHEN company GSTIN is updated, THE API_Server SHALL validate the GSTIN format against Indian GST standards (15 characters, alphanumeric pattern)
4. THE API_Server SHALL provide endpoints to configure invoice numbering schemes with prefix, suffix, and sequence patterns
5. THE API_Server SHALL provide endpoints to manage multiple invoice templates with customizable layouts

### Requirement 2: Financial Year Management

**User Story:** As an accountant, I want to manage financial years with locking capability, so that I can prevent modifications to closed accounting periods.

#### Acceptance Criteria

1. THE API_Server SHALL provide endpoints to create financial years with start date, end date, and lock status
2. THE Database SHALL enforce that financial year date ranges do not overlap for the same company
3. WHEN a financial year is locked, THE API_Server SHALL reject all create, update, and delete operations for Sales_Module, Purchase_Module, and Finance_Module transactions within that period
4. WHEN a financial year is locked, THE API_Server SHALL allow read-only access to reports for that period
5. THE Database SHALL enforce financial year lock constraints using RLS_Policy or database triggers
6. THE API_Server SHALL return HTTP 403 status code when operations are attempted on locked financial years

### Requirement 3: Role-Based Access Control

**User Story:** As a system administrator, I want to assign roles to users with specific permissions, so that I can control access to sensitive operations.

#### Acceptance Criteria

1. THE Auth_Service SHALL support three roles: Owner, Admin, and Staff
2. THE Database SHALL enforce RLS_Policy based on user role for all tables
3. WHERE role is Owner, THE API_Server SHALL grant full access to all modules and operations
4. WHERE role is Admin, THE API_Server SHALL grant access to all modules except company setup and user management
5. WHERE role is Staff, THE API_Server SHALL grant read-only access to reports and limited write access to Sales_Module and Inventory_Module
6. THE API_Server SHALL validate role permissions before processing any API request
7. THE API_Server SHALL return HTTP 403 status code when users attempt unauthorized operations

### Requirement 4: Product Master Management

**User Story:** As an inventory manager, I want to maintain a product catalog with HSN codes and GST rates, so that I can manage inventory and ensure GST compliance.

#### Acceptance Criteria

1. THE API_Server SHALL provide endpoints to create, update, and soft delete products
2. THE Database SHALL store product attributes including name, SKU, barcode, HSN_Code, GST rate, MRP, Cost_Price, Selling_Price, category, brand, and unit of measure
3. THE API_Server SHALL validate that HSN_Code follows Indian GST HSN format (2, 4, 6, or 8 digits)
4. THE API_Server SHALL validate that GST rate is one of the standard rates: 0%, 5%, 12%, 18%, or 28%
5. THE Database SHALL enforce unique constraints on SKU and barcode fields
6. THE API_Server SHALL support product categorization with hierarchical category structure
7. THE API_Server SHALL support unit conversion definitions for products with multiple units

### Requirement 5: Stock Management

**User Story:** As an inventory manager, I want real-time stock tracking with batch and expiry management, so that I can prevent stockouts and expired inventory sales.

#### Acceptance Criteria

1. THE Database SHALL maintain current stock quantity for each product across all locations
2. WHERE batch tracking is enabled for a product, THE Database SHALL store Batch number and expiry date for each stock entry
3. THE API_Server SHALL provide endpoints to query current stock levels with filtering by product, category, and location
4. THE API_Server SHALL generate low stock alerts when product quantity falls below defined threshold
5. THE Stock_Ledger SHALL record every stock movement with timestamp, quantity, movement type, reference document, and user
6. THE API_Server SHALL calculate stock value using weighted average cost method
7. WHEN a product with batch tracking is sold, THE API_Server SHALL enforce FEFO (First Expiry First Out) selection logic

### Requirement 6: Sales Invoice Creation with Multi-Module Impact

**User Story:** As a sales person, I want to create sales invoices that automatically update inventory, ledgers, and customer dues, so that all related data stays synchronized.

#### Acceptance Criteria

1. WHEN a sales invoice is created, THE API_Server SHALL execute all operations within a single Database Transaction
2. WHEN a sales invoice is created, THE Inventory_Module SHALL reduce stock quantity for all invoice line items
3. WHEN a sales invoice is created with insufficient stock, THE API_Server SHALL reject the invoice with HTTP 400 status code and descriptive error message
4. WHEN a sales invoice is created, THE GST_Engine SHALL calculate and store CGST, SGST, or IGST amounts based on customer location
5. WHEN a sales invoice is created as Credit_Sale, THE Finance_Module SHALL increase Customer_Due for the customer
6. WHEN a sales invoice is created as Cash_Sale, THE Finance_Module SHALL increase cash ledger balance
7. WHEN a sales invoice is created, THE Ledger_Engine SHALL create corresponding debit and credit ledger entries
8. WHEN a sales invoice is created, THE Audit_Logger SHALL record the invoice creation with user, timestamp, and all affected records
9. WHEN a sales invoice is created with batch-tracked products, THE API_Server SHALL validate batch numbers and expiry dates
10. WHEN a sales invoice is created, THE Stock_Ledger SHALL record stock-out entries for all line items

### Requirement 7: Sales Return and Refund Processing

**User Story:** As a sales person, I want to process sales returns that automatically reverse inventory, ledger, and GST entries, so that returns are properly accounted for.

#### Acceptance Criteria

1. WHEN a sales return is created, THE API_Server SHALL execute all operations within a single Database Transaction
2. WHEN a sales return is created, THE Inventory_Module SHALL increase stock quantity for all returned items
3. WHEN a sales return is created, THE GST_Engine SHALL create reversing GST entries
4. WHEN a sales return is created for a Credit_Sale, THE Finance_Module SHALL reduce Customer_Due
5. WHEN a sales return is created for a Cash_Sale, THE Finance_Module SHALL reduce cash ledger balance
6. WHEN a sales return is created, THE Ledger_Engine SHALL create reversing ledger entries
7. WHEN a sales return is created, THE Stock_Ledger SHALL record stock-in entries for all returned items
8. WHEN a sales return is created, THE Audit_Logger SHALL record the return with reference to original invoice
9. THE API_Server SHALL validate that return quantity does not exceed original invoice quantity

### Requirement 8: POS Billing

**User Story:** As a cashier, I want to process point-of-sale transactions quickly with immediate stock and cash ledger updates, so that I can serve customers efficiently.

#### Acceptance Criteria

1. WHEN a POS sale is created, THE API_Server SHALL execute all operations within a single Database Transaction
2. WHEN a POS sale is created, THE Inventory_Module SHALL reduce stock quantity for all items
3. WHEN a POS sale is created, THE Finance_Module SHALL increase cash ledger balance immediately
4. WHEN a POS sale is created, THE GST_Engine SHALL calculate and store GST breakup
5. WHEN a POS sale is created, THE Ledger_Engine SHALL create cash sale ledger entries
6. WHEN a POS sale is created with insufficient stock, THE API_Server SHALL reject the sale with HTTP 400 status code
7. THE API_Server SHALL support discount application at line item and invoice level for POS sales
8. THE API_Server SHALL generate invoice number automatically using configured numbering scheme

### Requirement 9: Purchase Order and GRN Processing

**User Story:** As a purchase manager, I want to create purchase orders and record goods receipt that automatically update inventory and vendor payables, so that purchase accounting is accurate.

#### Acceptance Criteria

1. THE API_Server SHALL provide endpoints to create purchase orders with line items, vendor, and expected delivery date
2. WHEN a GRN is created, THE API_Server SHALL execute all operations within a single Database Transaction
3. WHEN a GRN is created, THE Inventory_Module SHALL increase stock quantity for all received items
4. WHEN a GRN is created, THE Purchase_Module SHALL update product Cost_Price using weighted average method
5. WHEN a GRN is created for credit purchase, THE Finance_Module SHALL increase Vendor_Payable
6. WHEN a GRN is created, THE Ledger_Engine SHALL create purchase ledger entries
7. WHEN a GRN is created, THE Stock_Ledger SHALL record stock-in entries with GRN reference
8. WHEN a GRN is created, THE Audit_Logger SHALL record the GRN with user and timestamp
9. THE API_Server SHALL validate that GRN quantity does not exceed purchase order quantity

### Requirement 10: Purchase Return Processing

**User Story:** As a purchase manager, I want to process purchase returns that automatically reverse inventory and vendor payables, so that returns are properly accounted for.

#### Acceptance Criteria

1. WHEN a purchase return is created, THE API_Server SHALL execute all operations within a single Database Transaction
2. WHEN a purchase return is created, THE Inventory_Module SHALL reduce stock quantity for all returned items
3. WHEN a purchase return is created, THE Finance_Module SHALL reduce Vendor_Payable
4. WHEN a purchase return is created, THE Ledger_Engine SHALL create reversing ledger entries
5. WHEN a purchase return is created, THE Stock_Ledger SHALL record stock-out entries with return reference
6. WHEN a purchase return is created with insufficient stock, THE API_Server SHALL reject the return with HTTP 400 status code
7. THE API_Server SHALL validate that return quantity does not exceed original GRN quantity

### Requirement 11: Customer and Vendor Master Management

**User Story:** As a business user, I want to maintain customer and vendor records with GST details, so that I can track parties and ensure GST compliance.

#### Acceptance Criteria

1. THE API_Server SHALL provide endpoints to create, update, and soft delete customer records
2. THE API_Server SHALL provide endpoints to create, update, and soft delete vendor records
3. THE Database SHALL store party attributes including name, contact details, GSTIN, PAN, billing address, shipping address, and credit limit
4. WHERE party has GSTIN, THE API_Server SHALL validate GSTIN format
5. THE API_Server SHALL calculate and provide current outstanding due for each customer
6. THE API_Server SHALL calculate and provide current payable amount for each vendor
7. THE Database SHALL enforce unique constraints on GSTIN and PAN fields per party type

### Requirement 12: Payment Receipt Processing

**User Story:** As an accountant, I want to record customer payments that automatically reduce customer dues and update cash/bank ledgers, so that receivables are accurately tracked.

#### Acceptance Criteria

1. WHEN a payment receipt is recorded, THE API_Server SHALL execute all operations within a single Database Transaction
2. WHEN a payment receipt is recorded, THE Finance_Module SHALL reduce Customer_Due for the customer
3. WHEN a payment receipt is recorded, THE Finance_Module SHALL increase cash or bank ledger balance based on payment mode
4. WHEN a payment receipt is recorded, THE Ledger_Engine SHALL create payment ledger entries
5. WHEN a payment receipt is recorded, THE Audit_Logger SHALL record the payment with user and timestamp
6. THE API_Server SHALL validate that payment amount does not exceed customer outstanding due
7. THE API_Server SHALL support multiple payment modes: Cash, Bank Transfer, Cheque, UPI, Card

### Requirement 13: Payment to Vendor Processing

**User Story:** As an accountant, I want to record vendor payments that automatically reduce vendor payables and update cash/bank ledgers, so that payables are accurately tracked.

#### Acceptance Criteria

1. WHEN a vendor payment is recorded, THE API_Server SHALL execute all operations within a single Database Transaction
2. WHEN a vendor payment is recorded, THE Finance_Module SHALL reduce Vendor_Payable for the vendor
3. WHEN a vendor payment is recorded, THE Finance_Module SHALL reduce cash or bank ledger balance based on payment mode
4. WHEN a vendor payment is recorded, THE Ledger_Engine SHALL create payment ledger entries
5. WHEN a vendor payment is recorded, THE Audit_Logger SHALL record the payment with user and timestamp
6. THE API_Server SHALL validate that payment amount does not exceed vendor outstanding payable
7. THE API_Server SHALL support multiple payment modes: Cash, Bank Transfer, Cheque, UPI, Card

### Requirement 14: Income and Expense Management

**User Story:** As an accountant, I want to record income and expenses with categories, so that I can track profitability and generate financial reports.

#### Acceptance Criteria

1. THE API_Server SHALL provide endpoints to create, update, and delete income entries
2. THE API_Server SHALL provide endpoints to create, update, and delete expense entries
3. THE Database SHALL store income and expense attributes including amount, date, category, description, and payment mode
4. WHEN an income entry is created, THE Finance_Module SHALL increase cash or bank ledger balance
5. WHEN an expense entry is created, THE Finance_Module SHALL reduce cash or bank ledger balance
6. WHEN income or expense is recorded, THE Ledger_Engine SHALL create corresponding ledger entries
7. THE API_Server SHALL provide predefined expense categories: Rent, Salary, Utilities, Marketing, Transportation, Miscellaneous
8. THE API_Server SHALL allow custom expense category creation

### Requirement 15: Ledger Management

**User Story:** As an accountant, I want a double-entry ledger system that automatically records all financial transactions, so that I can maintain accurate books of accounts.

#### Acceptance Criteria

1. THE Ledger_Engine SHALL create debit and credit entries for every financial transaction
2. THE Database SHALL store ledger entries with date, account head, debit amount, credit amount, narration, and reference document
3. THE Ledger_Engine SHALL ensure that total debits equal total credits for every transaction
4. THE API_Server SHALL provide endpoints to query ledger entries with filtering by date range, account head, and transaction type
5. THE API_Server SHALL calculate running balance for each account head
6. THE Database SHALL enforce that ledger entries cannot be deleted, only reversed with new entries
7. THE API_Server SHALL support standard account heads: Cash, Bank, Sales, Purchase, Customer Receivables, Vendor Payables, Income, Expenses

### Requirement 16: GST Compliance and Reporting

**User Story:** As a tax accountant, I want GST calculations and reports that comply with Indian GST regulations, so that I can file accurate GST returns.

#### Acceptance Criteria

1. WHEN an invoice is created for intra-state sale, THE GST_Engine SHALL calculate and store CGST and SGST amounts
2. WHEN an invoice is created for inter-state sale, THE GST_Engine SHALL calculate and store IGST amount
3. THE GST_Engine SHALL determine state classification based on customer GSTIN or billing address
4. THE API_Server SHALL provide GST summary report with total taxable value, CGST, SGST, and IGST grouped by tax rate
5. THE API_Server SHALL provide GSTR-1 format report with B2B and B2C sales segregation
6. THE API_Server SHALL provide GSTR-3B format report with outward and inward supply details
7. THE Database SHALL store HSN-wise summary for GST reporting
8. THE API_Server SHALL validate that GST calculations match the formula: GST Amount = Taxable Value × GST Rate

### Requirement 17: Financial Reports Generation

**User Story:** As a business owner, I want comprehensive financial reports, so that I can understand business performance and make informed decisions.

#### Acceptance Criteria

1. THE API_Server SHALL provide Profit and Loss report with revenue, cost of goods sold, gross profit, expenses, and net profit for specified date range
2. THE API_Server SHALL provide Balance Sheet report with assets, liabilities, and equity as of specified date
3. THE API_Server SHALL provide Cash Flow report showing cash inflows and outflows categorized by operating, investing, and financing activities
4. THE API_Server SHALL provide Daily Sales Summary report with total sales, returns, net sales, and payment mode breakup
5. THE API_Server SHALL provide Item-wise Sales report with quantity sold, revenue, and profit margin per product
6. THE API_Server SHALL provide Customer Outstanding report listing all customers with pending dues
7. THE API_Server SHALL provide Vendor Payable report listing all vendors with pending payments
8. THE API_Server SHALL provide Stock Valuation report with current stock quantity and value per product
9. THE API_Server SHALL provide Stock Ageing report categorizing stock by age: 0-30 days, 31-60 days, 61-90 days, 90+ days
10. WHERE Financial_Year is locked, THE API_Server SHALL generate reports for that period in read-only mode

### Requirement 18: Audit Logging and Activity Tracking

**User Story:** As a system administrator, I want comprehensive audit logs of all user activities, so that I can track changes and investigate issues.

#### Acceptance Criteria

1. WHEN any create, update, or delete operation is performed, THE Audit_Logger SHALL record the activity
2. THE Database SHALL store audit log entries with timestamp, user, action type, module, record ID, old values, and new values
3. THE API_Server SHALL provide endpoints to query audit logs with filtering by user, date range, module, and action type
4. THE Audit_Logger SHALL record failed authentication attempts
5. THE Audit_Logger SHALL record permission denied events
6. THE Database SHALL retain audit logs for minimum 7 years for compliance
7. THE API_Server SHALL prevent modification or deletion of audit log entries

### Requirement 19: Database Schema and Constraints

**User Story:** As a database administrator, I want a normalized schema with proper constraints, so that data integrity is maintained.

#### Acceptance Criteria

1. THE Database SHALL use UUID as primary key for all tables
2. THE Database SHALL enforce foreign key constraints for all relationships
3. THE Database SHALL create indexes on frequently queried fields: product SKU, customer GSTIN, invoice number, date fields
4. THE Database SHALL include audit fields (created_at, updated_at, created_by, updated_by) in all tables
5. WHERE soft delete is implemented, THE Database SHALL include deleted_at and deleted_by fields
6. THE Database SHALL enforce NOT NULL constraints on mandatory fields
7. THE Database SHALL enforce CHECK constraints for data validation: GST rate values, quantity > 0, amount >= 0
8. THE Database SHALL use normalized schema design following third normal form (3NF)

### Requirement 20: API Design and Error Handling

**User Story:** As a frontend developer, I want consistent REST APIs with proper error handling, so that I can build a reliable user interface.

#### Acceptance Criteria

1. THE API_Server SHALL organize endpoints by module with prefix: /api/inventory, /api/sales, /api/purchase, /api/finance, /api/parties, /api/reports
2. THE API_Server SHALL validate all input parameters and return HTTP 400 status code with descriptive error messages for invalid input
3. THE API_Server SHALL return HTTP 401 status code for unauthenticated requests
4. THE API_Server SHALL return HTTP 403 status code for unauthorized requests
5. THE API_Server SHALL return HTTP 404 status code when requested resource is not found
6. THE API_Server SHALL return HTTP 500 status code for internal server errors with error tracking ID
7. THE API_Server SHALL return consistent JSON response format with data, error, and metadata fields
8. THE API_Server SHALL support pagination for list endpoints with page, limit, and total count
9. THE API_Server SHALL support filtering and sorting for list endpoints using query parameters
10. THE API_Server SHALL include API version in URL path: /api/v1/

### Requirement 21: Transaction Management and Data Consistency

**User Story:** As a system architect, I want atomic transactions for multi-table operations, so that data remains consistent even during failures.

#### Acceptance Criteria

1. WHEN sales invoice is created, THE API_Server SHALL wrap all database operations in a single Transaction
2. WHEN sales return is processed, THE API_Server SHALL wrap all database operations in a single Transaction
3. WHEN purchase GRN is created, THE API_Server SHALL wrap all database operations in a single Transaction
4. WHEN purchase return is processed, THE API_Server SHALL wrap all database operations in a single Transaction
5. WHEN payment is recorded, THE API_Server SHALL wrap all database operations in a single Transaction
6. IF any operation within a Transaction fails, THE Database SHALL rollback all changes
7. THE API_Server SHALL implement optimistic locking for concurrent update prevention using version fields
8. THE API_Server SHALL retry failed transactions up to 3 times with exponential backoff for transient errors

### Requirement 22: Barcode Management

**User Story:** As a store manager, I want to generate and scan barcodes for products, so that I can speed up billing and inventory operations.

#### Acceptance Criteria

1. THE API_Server SHALL provide endpoint to generate unique barcode for products
2. THE Database SHALL enforce unique constraint on barcode field
3. THE API_Server SHALL provide endpoint to search products by barcode
4. THE API_Server SHALL support standard barcode formats: EAN-13, EAN-8, UPC-A, Code-128
5. WHERE product has no barcode, THE API_Server SHALL allow SKU-based search as fallback

### Requirement 23: Discount Rules Management

**User Story:** As a sales manager, I want to define discount rules that automatically apply during billing, so that pricing is consistent and promotional offers are honored.

#### Acceptance Criteria

1. THE API_Server SHALL provide endpoints to create, update, and delete discount rules
2. THE Database SHALL store discount rule attributes including name, type (percentage or fixed amount), value, applicable products or categories, start date, and end date
3. WHEN an invoice is created, THE Sales_Module SHALL automatically apply applicable discount rules based on products and date
4. THE API_Server SHALL support discount application at line item level and invoice level
5. THE API_Server SHALL validate that discount amount does not exceed line item or invoice total
6. THE Database SHALL store applied discount details in invoice line items for audit trail

### Requirement 24: Challan and Delivery Management

**User Story:** As a logistics coordinator, I want to create delivery challans without invoices, so that I can track goods in transit before billing.

#### Acceptance Criteria

1. THE API_Server SHALL provide endpoints to create delivery challans with line items and customer details
2. WHEN a challan is created, THE Inventory_Module SHALL reduce stock quantity for all items
3. THE API_Server SHALL provide endpoint to convert challan to invoice
4. WHEN a challan is converted to invoice, THE Sales_Module SHALL create invoice without additional stock reduction
5. THE Database SHALL maintain reference between challan and converted invoice
6. THE API_Server SHALL support challan cancellation that restores stock quantity

### Requirement 25: Low Stock Alerts

**User Story:** As an inventory manager, I want automatic alerts when stock falls below threshold, so that I can reorder products before stockout.

#### Acceptance Criteria

1. THE Database SHALL store minimum stock level threshold for each product
2. WHEN stock quantity falls below threshold after any stock movement, THE Inventory_Module SHALL create a low stock alert
3. THE API_Server SHALL provide endpoint to query active low stock alerts
4. THE API_Server SHALL provide endpoint to mark alerts as acknowledged
5. WHERE product has no minimum stock level defined, THE Inventory_Module SHALL use default threshold of 10 units

### Requirement 26: Multi-Location Stock Management

**User Story:** As a business owner with multiple stores, I want to track stock separately for each location, so that I can manage inventory across locations.

#### Acceptance Criteria

1. THE Database SHALL store location master with location name and address
2. THE Database SHALL maintain stock quantity per product per location
3. THE API_Server SHALL provide endpoints to transfer stock between locations
4. WHEN stock transfer is created, THE Inventory_Module SHALL reduce stock at source location and increase stock at destination location within a single Transaction
5. THE Stock_Ledger SHALL record stock transfer movements with source and destination location references
6. THE API_Server SHALL provide stock reports with location-wise breakup

### Requirement 27: Credit Limit Enforcement

**User Story:** As a credit manager, I want to enforce credit limits for customers, so that I can control credit risk.

#### Acceptance Criteria

1. THE Database SHALL store credit limit amount for each customer
2. WHEN a Credit_Sale invoice is created, THE API_Server SHALL calculate total customer outstanding including the new invoice
3. WHEN total customer outstanding exceeds credit limit, THE API_Server SHALL reject the invoice with HTTP 400 status code and credit limit exceeded message
4. WHERE customer has no credit limit defined, THE API_Server SHALL allow unlimited credit
5. THE API_Server SHALL provide endpoint to query customer credit utilization percentage

### Requirement 28: Backup Metadata Management

**User Story:** As a system administrator, I want to track database backup metadata, so that I can ensure data recovery capability.

#### Acceptance Criteria

1. THE API_Server SHALL provide endpoint to record backup metadata including timestamp, backup size, storage location, and backup type
2. THE Database SHALL store backup history for minimum 90 days
3. THE API_Server SHALL provide endpoint to query backup history
4. THE API_Server SHALL validate that backup metadata is recorded within 24 hours of backup creation

### Requirement 29: Data Export and Import

**User Story:** As a data analyst, I want to export data in standard formats, so that I can perform external analysis and reporting.

#### Acceptance Criteria

1. THE API_Server SHALL provide endpoints to export reports in CSV format
2. THE API_Server SHALL provide endpoints to export reports in PDF format
3. THE API_Server SHALL provide endpoint to export product master data in CSV format for bulk editing
4. THE API_Server SHALL provide endpoint to import product master data from CSV format
5. WHEN importing data, THE API_Server SHALL validate all fields and return detailed error report for invalid rows
6. THE API_Server SHALL support bulk import with transaction rollback on any validation error

### Requirement 30: Invoice Template Customization

**User Story:** As a business owner, I want to customize invoice templates with my branding, so that invoices reflect my business identity.

#### Acceptance Criteria

1. THE API_Server SHALL provide endpoints to create and manage invoice templates
2. THE Database SHALL store template attributes including name, header content, footer content, logo URL, and layout configuration
3. THE API_Server SHALL support template variables for dynamic content: company name, invoice number, date, customer details, line items, totals, GST breakup
4. THE API_Server SHALL provide endpoint to set default template for invoice generation
5. THE API_Server SHALL provide endpoint to generate invoice PDF using specified template

### Requirement 31: Round-Trip Data Integrity for Import/Export

**User Story:** As a data administrator, I want data export and import to preserve all information accurately, so that no data is lost during the process.

#### Acceptance Criteria

1. WHEN product data is exported to CSV and then imported back, THE API_Server SHALL produce product records equivalent to the original records
2. THE API_Server SHALL include all mandatory and optional fields in CSV export format
3. THE API_Server SHALL preserve data types, decimal precision, and special characters during export and import
4. THE API_Server SHALL validate CSV format and encoding (UTF-8) during import
5. IF imported data differs from exported data due to validation rules, THE API_Server SHALL provide detailed error report specifying the differences

### Requirement 32: API Documentation and Metadata

**User Story:** As a developer integrating with the API, I want comprehensive API documentation with module dependencies, so that I understand the system behavior.

#### Acceptance Criteria

1. THE API_Server SHALL provide OpenAPI (Swagger) specification for all endpoints
2. THE API documentation SHALL explicitly declare for each endpoint: primary module, secondary modules affected, database tables touched, and side effects
3. THE API documentation SHALL include request and response examples for all endpoints
4. THE API documentation SHALL document all error codes and error response formats
5. THE API documentation SHALL document authentication and authorization requirements for each endpoint
6. THE API documentation SHALL document transaction boundaries for multi-table operations

### Requirement 33: Performance and Scalability

**User Story:** As a system architect, I want the system to handle high transaction volumes efficiently, so that it can scale with business growth.

#### Acceptance Criteria

1. THE API_Server SHALL respond to product search queries within 200 milliseconds for databases with up to 100,000 products
2. THE API_Server SHALL process invoice creation within 500 milliseconds including all side effects
3. THE Database SHALL support concurrent transactions with isolation level READ COMMITTED
4. THE API_Server SHALL implement connection pooling with minimum 10 and maximum 100 database connections
5. THE API_Server SHALL implement query result caching for frequently accessed reference data with 5-minute TTL
6. THE Database SHALL partition large tables (invoices, ledger entries, stock ledger) by date for query performance

### Requirement 34: Security and Data Protection

**User Story:** As a security officer, I want robust security controls protecting sensitive business data, so that unauthorized access is prevented.

#### Acceptance Criteria

1. THE Auth_Service SHALL enforce JWT token expiration of 24 hours
2. THE Auth_Service SHALL support token refresh mechanism
3. THE API_Server SHALL validate JWT signature on every request
4. THE Database SHALL enforce RLS_Policy ensuring users can only access data for their company
5. THE API_Server SHALL sanitize all input parameters to prevent SQL injection attacks
6. THE API_Server SHALL implement rate limiting of 100 requests per minute per user
7. THE Database SHALL encrypt sensitive fields: GSTIN, PAN, bank account numbers
8. THE API_Server SHALL log all authentication failures for security monitoring

### Requirement 35: System Health Monitoring

**User Story:** As a DevOps engineer, I want health check endpoints and metrics, so that I can monitor system status and performance.

#### Acceptance Criteria

1. THE API_Server SHALL provide /health endpoint returning HTTP 200 when system is operational
2. THE API_Server SHALL provide /health/db endpoint checking database connectivity
3. THE API_Server SHALL provide /metrics endpoint exposing request count, response time, and error rate
4. THE API_Server SHALL log all errors with stack trace and context information
5. THE API_Server SHALL integrate with error tracking service for production error monitoring

