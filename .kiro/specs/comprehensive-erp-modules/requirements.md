# Requirements Document

## Introduction

This document specifies the requirements for enhancing a mobile ERP software with 22 comprehensive modules to replace existing basic modules. The system uses Supabase as the database backend and requires a mobile-optimized, performant UI that maintains the existing design aesthetic while providing full-featured ERP functionality across authentication, company setup, financial management, inventory control, customer relationship management, and reporting capabilities.

## Glossary

- **ERP_System**: The mobile Enterprise Resource Planning application
- **Supabase_Database**: PostgreSQL database backend managed by Supabase
- **Mobile_Interface**: Touch-optimized user interface for mobile devices
- **Business_Owner**: Primary user account that owns business data
- **Operator**: Staff user with limited permissions
- **Admin_User**: User with full system access and configuration rights
- **Invoice**: GST-compliant billing document
- **Challan**: Delivery note document that can be converted to invoice
- **Purchase_Order**: Document requesting goods from supplier
- **GRN**: Goods Receipt Note for received inventory
- **HSN_Code**: Harmonized System of Nomenclature code for products
- **GST**: Goods and Services Tax
- **Batch_Number**: Unique identifier for product batch with expiry tracking
- **Barcode**: Machine-readable product identifier
- **Credit_Invoice**: Invoice with deferred payment terms
- **Stock_Adjustment**: Manual correction of inventory quantities
- **Low_Stock_Alert**: Notification when product quantity falls below threshold
- **CRM**: Customer Relationship Management system
- **Lead**: Potential customer in sales pipeline
- **Follow_Up**: Scheduled customer interaction
- **Outstanding**: Unpaid amount owed by customer or to supplier
- **Mixed_Payment**: Payment using multiple payment methods
- **Profit_Loss_Report**: Financial summary of income minus expenses
- **Backup**: Exportable copy of system data
- **Role_Permission**: Access control setting for user types
- **Dashboard_Widget**: Visual data display component
- **Financial_Year**: Accounting period for business operations
- **Default_Bank**: Primary bank account for transactions

## Requirements

### Requirement 1: Authentication & Security

**User Story:** As a business owner, I want secure multi-role authentication, so that different users can access the system with appropriate permissions.

#### Acceptance Criteria

1. THE ERP_System SHALL support three distinct login types: Admin_User, Operator, and Business_Owner
2. WHEN a user attempts login, THE ERP_System SHALL validate credentials against Supabase_Database
3. WHEN login credentials are invalid, THE ERP_System SHALL display an error message within 200ms
4. THE ERP_System SHALL provide a password change function for all user types
5. THE ERP_System SHALL enforce role-based access control for all modules
6. WHEN a user session expires, THE ERP_System SHALL redirect to login screen
7. THE ERP_System SHALL store password hashes using bcrypt or equivalent secure algorithm
8. WHEN a user successfully authenticates, THE ERP_System SHALL create a session token valid for 24 hours

### Requirement 2: Company / Firm Setup

**User Story:** As a business owner, I want to configure my company profile and settings, so that invoices and documents reflect accurate business information.

#### Acceptance Criteria

1. THE ERP_System SHALL allow Admin_User to create and edit company profile
2. THE ERP_System SHALL store company name, address, contact details, and logo
3. THE ERP_System SHALL validate and store GST registration number in format: 2 digits state code + 10 digits PAN + 1 digit entity + 1 digit Z + 1 check digit
4. THE ERP_System SHALL allow Admin_User to configure financial year start and end dates
5. THE ERP_System SHALL provide invoice settings including: prefix, starting number, and format
6. WHEN company profile is incomplete, THE ERP_System SHALL display warning on dashboard
7. THE ERP_System SHALL allow configuration of default tax rates for invoicing

### Requirement 3: Bank Management

**User Story:** As a business owner, I want to manage multiple bank accounts, so that I can track payments across different banks.

#### Acceptance Criteria

1. THE ERP_System SHALL allow Admin_User to add bank account details including: bank name, account number, IFSC code, branch
2. THE ERP_System SHALL allow editing of existing bank account information
3. THE ERP_System SHALL display a list of all configured bank accounts
4. THE ERP_System SHALL allow Admin_User to designate one bank as Default_Bank
5. WHEN a bank account is marked as Default_Bank, THE ERP_System SHALL use it for new transactions
6. THE ERP_System SHALL prevent deletion of bank accounts with associated transactions
7. THE ERP_System SHALL validate IFSC code format: 4 letters + 7 characters

### Requirement 4: Invoice / Billing

**User Story:** As an operator, I want to create and manage GST-compliant invoices, so that I can bill customers accurately and legally.

#### Acceptance Criteria

1. THE ERP_System SHALL allow creation of new invoices with customer, items, quantities, and prices
2. THE ERP_System SHALL automatically calculate GST amounts based on configured tax rates
3. THE ERP_System SHALL generate unique invoice numbers using configured prefix and sequence
4. THE ERP_System SHALL allow editing of draft invoices
5. THE ERP_System SHALL prevent editing of finalized invoices
6. THE ERP_System SHALL allow deletion of draft invoices only
7. THE ERP_System SHALL generate PDF format invoices with company logo and GST details
8. THE ERP_System SHALL provide invoice sharing via WhatsApp, email, or download
9. THE ERP_System SHALL support invoice returns with credit note generation
10. THE ERP_System SHALL support Credit_Invoice creation with due date
11. WHEN an invoice is created, THE ERP_System SHALL reduce product stock quantities in Supabase_Database
12. WHEN an invoice is deleted, THE ERP_System SHALL restore product stock quantities
13. THE ERP_System SHALL display invoice history with search and filter capabilities

### Requirement 5: Challan / Delivery Note

**User Story:** As an operator, I want to create delivery challans, so that I can track goods sent without immediate invoicing.

#### Acceptance Criteria

1. THE ERP_System SHALL allow creation of delivery challans with customer and item details
2. THE ERP_System SHALL generate unique challan numbers
3. THE ERP_System SHALL allow editing of challans before conversion to invoice
4. THE ERP_System SHALL provide one-click conversion of challan to Invoice
5. WHEN challan is converted to invoice, THE ERP_System SHALL preserve all item details and quantities
6. THE ERP_System SHALL generate challan reports filtered by date range
7. THE ERP_System SHALL mark challan as "Converted" after invoice creation
8. WHEN challan is created, THE ERP_System SHALL NOT reduce stock quantities until conversion

### Requirement 6: Purchase Management

**User Story:** As an operator, I want to record purchases from suppliers, so that I can track inventory inflow and costs.

#### Acceptance Criteria

1. THE ERP_System SHALL allow entry of purchase records with supplier, items, quantities, and costs
2. THE ERP_System SHALL allow editing of purchase entries
3. THE ERP_System SHALL support purchase returns with quantity and amount adjustments
4. THE ERP_System SHALL allow upload of supplier bill images or PDFs
5. WHEN purchase is recorded, THE ERP_System SHALL increase product stock quantities
6. WHEN purchase return is recorded, THE ERP_System SHALL decrease product stock quantities
7. THE ERP_System SHALL calculate and display total purchase amount including taxes
8. THE ERP_System SHALL link purchases to supplier accounts for Outstanding tracking

### Requirement 7: Purchase Order (PO)

**User Story:** As an operator, I want to create purchase orders, so that I can formally request goods from suppliers.

#### Acceptance Criteria

1. THE ERP_System SHALL allow creation of Purchase_Order with supplier, items, quantities, and expected prices
2. THE ERP_System SHALL generate unique PO numbers
3. THE ERP_System SHALL allow editing of Purchase_Order in "Draft" status
4. THE ERP_System SHALL support PO approval workflow with status: Draft, Pending, Approved, Rejected
5. WHEN Purchase_Order is approved, THE ERP_System SHALL change status to "Approved"
6. THE ERP_System SHALL track Purchase_Order status: Open, Partially Received, Fully Received, Closed
7. THE ERP_System SHALL generate PDF format Purchase_Order documents
8. THE ERP_System SHALL prevent editing of approved Purchase_Order

### Requirement 8: Receive / GRN (Goods Receipt Note)

**User Story:** As an operator, I want to record received goods against purchase orders, so that I can update inventory accurately.

#### Acceptance Criteria

1. THE ERP_System SHALL allow creation of GRN linked to Purchase_Order
2. THE ERP_System SHALL display pending Purchase_Order items for receiving
3. THE ERP_System SHALL allow partial receipt of Purchase_Order items
4. WHEN GRN is created, THE ERP_System SHALL increase product stock quantities by received amount
5. THE ERP_System SHALL update Purchase_Order status based on received quantities
6. THE ERP_System SHALL record GRN date, time, and receiving user
7. THE ERP_System SHALL maintain mapping between Purchase_Order and GRN records
8. THE ERP_System SHALL prevent receiving quantities exceeding Purchase_Order quantities

### Requirement 9: Product / Item Master

**User Story:** As an admin, I want to maintain a comprehensive product catalog, so that I can manage inventory items with complete details.

#### Acceptance Criteria

1. THE ERP_System SHALL allow adding products with: name, code, category, brand, HSN_Code, GST rate, unit, cost, price
2. THE ERP_System SHALL allow editing of product details
3. THE ERP_System SHALL allow soft deletion of products (marking as inactive)
4. THE ERP_System SHALL prevent deletion of products with transaction history
5. THE ERP_System SHALL validate HSN_Code format: 4, 6, or 8 digits
6. THE ERP_System SHALL support product categorization with hierarchical categories
7. THE ERP_System SHALL support brand management for products
8. THE ERP_System SHALL enforce unique product codes within Business_Owner account
9. THE ERP_System SHALL display product list with search, filter, and sort capabilities

### Requirement 10: Inventory / Stock Management

**User Story:** As an operator, I want to track inventory movements, so that I can maintain accurate stock levels.

#### Acceptance Criteria

1. THE ERP_System SHALL record stock inward transactions with quantity and reference
2. THE ERP_System SHALL record stock outward transactions with quantity and reference
3. THE ERP_System SHALL allow Stock_Adjustment with reason notes
4. THE ERP_System SHALL generate Low_Stock_Alert when product quantity falls below minimum threshold
5. WHEN Low_Stock_Alert is generated, THE ERP_System SHALL create notification for Admin_User
6. THE ERP_System SHALL display current stock levels for all products
7. THE ERP_System SHALL maintain stock transaction history with date, time, type, and user
8. THE ERP_System SHALL calculate available stock as: current stock minus reserved quantities
9. THE ERP_System SHALL prevent negative stock unless configured to allow

### Requirement 11: Batch & Expiry Management

**User Story:** As an operator, I want to track product batches and expiry dates, so that I can manage perishable inventory.

#### Acceptance Criteria

1. WHERE product has batch tracking enabled, THE ERP_System SHALL require Batch_Number during stock inward
2. WHERE product has expiry tracking enabled, THE ERP_System SHALL require expiry date during stock inward
3. THE ERP_System SHALL maintain separate stock quantities for each Batch_Number
4. THE ERP_System SHALL generate near-expiry report for products expiring within 30 days
5. WHEN product batch expires, THE ERP_System SHALL flag it in inventory list
6. THE ERP_System SHALL use FEFO (First Expiry First Out) for batch selection during sales
7. THE ERP_System SHALL prevent sale of expired batches
8. THE ERP_System SHALL display batch-wise stock report with expiry dates

### Requirement 12: Barcode Management

**User Story:** As an operator, I want to use barcodes for products, so that I can speed up billing and inventory operations.

#### Acceptance Criteria

1. THE ERP_System SHALL generate Barcode for products using EAN-13 or Code-128 format
2. THE ERP_System SHALL allow printing of Barcode labels
3. THE ERP_System SHALL support Barcode scanning during billing using device camera
4. WHEN Barcode is scanned, THE ERP_System SHALL identify product and add to bill within 500ms
5. THE ERP_System SHALL allow manual Barcode entry via keyboard
6. THE ERP_System SHALL validate Barcode uniqueness within Business_Owner account
7. THE ERP_System SHALL support bulk Barcode generation for multiple products
8. THE ERP_System SHALL store Barcode as both text and image format

### Requirement 13: Customer (Client) Management

**User Story:** As an operator, I want to maintain customer records, so that I can track customer transactions and credit limits.

#### Acceptance Criteria

1. THE ERP_System SHALL allow adding customers with: name, phone, email, address, credit limit
2. THE ERP_System SHALL allow editing of customer details
3. THE ERP_System SHALL display customer list with search by name or phone
4. THE ERP_System SHALL perform phone-based customer lookup during billing
5. THE ERP_System SHALL track customer total purchases and current balance
6. THE ERP_System SHALL prevent credit sales exceeding customer credit limit
7. THE ERP_System SHALL maintain customer transaction history
8. THE ERP_System SHALL calculate customer Outstanding as: total credit minus paid amount
9. THE ERP_System SHALL support customer categorization: Regular, VIP, Wholesale

### Requirement 14: Vendor / Supplier Management

**User Story:** As an operator, I want to maintain supplier records, so that I can track purchases and payments.

#### Acceptance Criteria

1. THE ERP_System SHALL allow adding suppliers with: name, phone, email, address, payment terms
2. THE ERP_System SHALL allow editing of supplier details
3. THE ERP_System SHALL display supplier list with search capabilities
4. THE ERP_System SHALL track supplier Outstanding amounts
5. THE ERP_System SHALL calculate supplier Outstanding as: total purchases minus payments made
6. THE ERP_System SHALL maintain supplier transaction history
7. THE ERP_System SHALL link purchase entries to supplier accounts
8. THE ERP_System SHALL display supplier-wise purchase summary

### Requirement 15: CRM (Customer Relationship Management)

**User Story:** As a sales operator, I want to manage leads and follow-ups, so that I can convert prospects into customers.

#### Acceptance Criteria

1. THE ERP_System SHALL allow entry of Lead with: name, phone, email, source, status
2. THE ERP_System SHALL support Lead status: New, Contacted, Qualified, Converted, Lost
3. THE ERP_System SHALL allow scheduling of Follow_Up with date, time, and notes
4. WHEN Follow_Up date arrives, THE ERP_System SHALL create reminder notification
5. THE ERP_System SHALL allow conversion of Lead to customer account
6. THE ERP_System SHALL maintain customer interaction history
7. THE ERP_System SHALL display Lead pipeline with status-wise counts
8. THE ERP_System SHALL allow filtering of Follow_Up by date range and status

### Requirement 16: Payment Management

**User Story:** As an operator, I want to record payments flexibly, so that I can handle various payment scenarios.

#### Acceptance Criteria

1. THE ERP_System SHALL support payment methods: Cash, UPI, Card, Cheque, Bank Transfer
2. THE ERP_System SHALL allow Mixed_Payment using multiple payment methods for single transaction
3. THE ERP_System SHALL record payment reference numbers for digital payments
4. THE ERP_System SHALL track payment status: Pending, Completed, Failed
5. WHEN payment is recorded, THE ERP_System SHALL update customer or supplier Outstanding
6. THE ERP_System SHALL link payments to specific invoices or bills
7. THE ERP_System SHALL generate payment receipt in PDF format
8. THE ERP_System SHALL maintain payment history with date, time, method, and amount

### Requirement 17: Income & Expense Tracking

**User Story:** As a business owner, I want to track income and expenses, so that I can monitor business profitability.

#### Acceptance Criteria

1. THE ERP_System SHALL allow entry of income records with: amount, category, date, description
2. THE ERP_System SHALL allow entry of expense records with: amount, category, date, description
3. THE ERP_System SHALL support income categories: Sales, Services, Other Income
4. THE ERP_System SHALL support expense categories: Rent, Utilities, Salaries, Supplies, Other
5. THE ERP_System SHALL allow custom category creation
6. THE ERP_System SHALL generate income report filtered by date range and category
7. THE ERP_System SHALL generate expense report filtered by date range and category
8. THE ERP_System SHALL calculate net income as: total income minus total expenses

### Requirement 18: Basic Accounting

**User Story:** As a business owner, I want basic accounting reports, so that I can understand financial performance.

#### Acceptance Criteria

1. THE ERP_System SHALL generate sales summary report with: total sales, tax collected, payment method breakdown
2. THE ERP_System SHALL generate purchase summary report with: total purchases, tax paid, supplier breakdown
3. THE ERP_System SHALL generate Profit_Loss_Report showing: revenue, cost of goods sold, gross profit, expenses, net profit
4. THE ERP_System SHALL calculate gross profit as: sales revenue minus cost of goods sold
5. THE ERP_System SHALL calculate net profit as: gross profit minus expenses
6. THE ERP_System SHALL support date range filtering for all accounting reports
7. THE ERP_System SHALL display month-wise and year-wise financial comparisons
8. THE ERP_System SHALL export accounting reports in PDF and Excel formats

### Requirement 19: Staff & Operator Management

**User Story:** As an admin, I want to manage staff and operator accounts, so that I can control system access.

#### Acceptance Criteria

1. THE ERP_System SHALL allow Admin_User to create Operator accounts with: name, username, password, role
2. THE ERP_System SHALL allow Admin_User to edit Operator details
3. THE ERP_System SHALL support role-based permissions for modules: Billing, Inventory, Reports, Settings
4. THE ERP_System SHALL allow Admin_User to activate or deactivate Operator accounts
5. THE ERP_System SHALL track Operator login history with date and time
6. THE ERP_System SHALL enforce unique usernames within Business_Owner account
7. THE ERP_System SHALL require password change on first login for new Operator accounts
8. THE ERP_System SHALL log Operator actions for audit trail

### Requirement 20: Reporting

**User Story:** As a business owner, I want comprehensive reports, so that I can make informed business decisions.

#### Acceptance Criteria

1. THE ERP_System SHALL generate sales report with: date range, customer, product, quantity, amount filters
2. THE ERP_System SHALL generate purchase report with: date range, supplier, product, quantity, amount filters
3. THE ERP_System SHALL generate inventory report showing: product, current stock, value, movement
4. THE ERP_System SHALL generate financial report showing: income, expenses, profit, Outstanding
5. THE ERP_System SHALL generate customer Outstanding report with aging analysis: 0-30, 31-60, 61-90, 90+ days
6. THE ERP_System SHALL generate supplier Outstanding report
7. THE ERP_System SHALL generate GST report with: taxable value, CGST, SGST, IGST breakdown
8. THE ERP_System SHALL export all reports in PDF, Excel, and CSV formats
9. THE ERP_System SHALL allow report scheduling for automatic generation
10. THE ERP_System SHALL display graphical charts for sales trends and inventory levels

### Requirement 21: Dashboard

**User Story:** As a business owner, I want a visual dashboard, so that I can quickly understand business status.

#### Acceptance Criteria

1. THE ERP_System SHALL display Dashboard_Widget for today's sales amount
2. THE ERP_System SHALL display Dashboard_Widget for total Outstanding from customers
3. THE ERP_System SHALL display Dashboard_Widget for low stock items count
4. THE ERP_System SHALL display Dashboard_Widget for pending Purchase_Order count
5. THE ERP_System SHALL display Dashboard_Widget for top selling products
6. THE ERP_System SHALL display Dashboard_Widget for sales trend graph for last 30 days
7. THE ERP_System SHALL display Dashboard_Widget for recent transactions list
8. THE ERP_System SHALL display Dashboard_Widget for expiring products alert
9. THE ERP_System SHALL refresh Dashboard_Widget data when user navigates to dashboard
10. THE ERP_System SHALL allow customization of Dashboard_Widget visibility

### Requirement 22: Backup & Settings

**User Story:** As an admin, I want to backup data and configure system settings, so that I can protect business data and customize system behavior.

#### Acceptance Criteria

1. THE ERP_System SHALL provide manual Backup function to export all data
2. THE ERP_System SHALL generate Backup in JSON format with timestamp
3. THE ERP_System SHALL allow restore from Backup file
4. WHEN restore is initiated, THE ERP_System SHALL display warning about data overwrite
5. THE ERP_System SHALL provide invoice template settings: header, footer, terms and conditions
6. THE ERP_System SHALL allow configuration of default values: payment method, tax rate, currency
7. THE ERP_System SHALL allow configuration of Mobile_Interface theme: light or dark mode
8. THE ERP_System SHALL allow configuration of date format and timezone
9. THE ERP_System SHALL allow configuration of notification preferences
10. THE ERP_System SHALL validate Backup file integrity before restore

### Requirement 23: Mobile Interface Performance

**User Story:** As a mobile user, I want a responsive interface, so that I can work efficiently without lag.

#### Acceptance Criteria

1. THE Mobile_Interface SHALL render all screens within 1 second on 4G connection
2. THE Mobile_Interface SHALL support touch gestures: tap, swipe, pinch-to-zoom
3. THE Mobile_Interface SHALL use lazy loading for long lists exceeding 50 items
4. THE Mobile_Interface SHALL cache frequently accessed data locally
5. THE Mobile_Interface SHALL display loading indicators during data fetch operations
6. THE Mobile_Interface SHALL maintain existing UI design patterns for consistency
7. THE Mobile_Interface SHALL be responsive to screen sizes from 4 inches to 7 inches
8. THE Mobile_Interface SHALL minimize JavaScript bundle size to under 2MB
9. WHEN network is unavailable, THE Mobile_Interface SHALL display offline message
10. THE Mobile_Interface SHALL synchronize local changes when network is restored

### Requirement 24: Supabase Integration

**User Story:** As a developer, I want seamless Supabase integration, so that all modules work with the existing database.

#### Acceptance Criteria

1. THE ERP_System SHALL use Supabase_Database for all data persistence
2. THE ERP_System SHALL use Supabase authentication for user session management
3. THE ERP_System SHALL implement row-level security policies for multi-tenant data isolation
4. THE ERP_System SHALL use Supabase real-time subscriptions for live data updates
5. THE ERP_System SHALL handle Supabase connection errors gracefully with retry logic
6. THE ERP_System SHALL use database transactions for multi-table operations
7. THE ERP_System SHALL implement proper indexing for query performance
8. THE ERP_System SHALL use prepared statements to prevent SQL injection
9. THE ERP_System SHALL log database errors for debugging
10. THE ERP_System SHALL maintain backward compatibility with existing schema

