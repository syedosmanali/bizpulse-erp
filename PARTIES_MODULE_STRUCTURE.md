# Parties Module - Redesigned Structure

## Overview
The Parties module has been completely redesigned with a clean, hierarchical structure. All duplicate routes have been removed and organized under a unified `/erp/parties` namespace.

## Main Dashboard
- `/erp/parties` - Main parties management dashboard

## Sub-modules

### 1. CUSTOMERS Sub-module (`/erp/parties/customers`)
**Main Routes:**
- `/erp/parties/customers` - Customer master list
- `/erp/parties/customers/add` - Add new customer
- `/erp/parties/customers/import` - Import customers from CSV/Excel
- `/erp/parties/customers/groups` - Customer groups/categories
- `/erp/parties/customers/credit-limits` - Manage customer credit limits
- `/erp/parties/customers/outstanding` - Customer outstanding balances
- `/erp/parties/customers/statements` - Customer account statements

**API Endpoints:**
- `GET /api/erp/customers` - Get all customers (with pagination & filters)
- `POST /api/erp/customers` - Create new customer
- `GET /api/erp/customers/<customer_id>` - Get single customer
- `PUT /api/erp/customers/<customer_id>` - Update customer
- `DELETE /api/erp/customers/<customer_id>` - Delete customer (soft delete)
- `GET /api/erp/customers/<customer_id>/transactions` - Get customer transactions

### 2. VENDORS Sub-module (`/erp/parties/vendors`)
**Main Routes:**
- `/erp/parties/vendors` - Vendor master list
- `/erp/parties/vendors/add` - Add new vendor
- `/erp/parties/vendors/import` - Import vendors from CSV/Excel
- `/erp/parties/vendors/categories` - Vendor categories
- `/erp/parties/vendors/payables` - Vendor payables/outstanding
- `/erp/parties/vendors/performance` - Vendor performance tracking
- `/erp/parties/vendors/statements` - Vendor account statements

**API Endpoints:**
- `GET /api/erp/vendors` - Get all vendors (with pagination & filters)
- `POST /api/erp/vendors` - Create new vendor
- `GET /api/erp/vendors/<vendor_id>` - Get single vendor
- `PUT /api/erp/vendors/<vendor_id>` - Update vendor
- `DELETE /api/erp/vendors/<vendor_id>` - Delete vendor (soft delete)
- `GET /api/erp/vendors/<vendor_id>/transactions` - Get vendor transactions

### 3. CRM & LEADS Sub-module (`/erp/parties/crm`)
**Main Routes:**
- `/erp/parties/crm` - CRM leads dashboard
- `/erp/parties/crm/leads` - All CRM leads
- `/erp/parties/crm/leads/add` - Add new lead
- `/erp/parties/crm/leads/import` - Import leads
- `/erp/parties/crm/pipeline` - Sales pipeline view
- `/erp/parties/crm/follow-ups` - Follow-up reminders
- `/erp/parties/crm/conversions` - Lead conversion tracking
- `/erp/parties/crm/activities` - CRM activity log

**API Endpoints:**
- `GET /api/erp/crm-leads` - Get all CRM leads (with pagination & filters)
- `POST /api/erp/crm-leads` - Create new lead
- `GET /api/erp/crm-leads/<lead_id>` - Get single lead
- `PUT /api/erp/crm-leads/<lead_id>` - Update lead
- `DELETE /api/erp/crm-leads/<lead_id>` - Delete lead (soft delete)
- `POST /api/erp/crm-leads/<lead_id>/convert` - Convert lead to customer

### 4. PARTY REPORTS Sub-module (`/erp/parties/reports`)
**Main Routes:**
- `/erp/parties/reports` - Party management reports
- `/erp/parties/reports/customer-analysis` - Customer analysis report
- `/erp/parties/reports/vendor-analysis` - Vendor analysis report
- `/erp/parties/reports/aging` - Aging report (receivables/payables)
- `/erp/parties/reports/top-customers` - Top customers by sales
- `/erp/parties/reports/top-vendors` - Top vendors by purchase

**API Endpoints:**
- `GET /api/erp/parties/stats` - Get party management statistics

### 5. PARTY SETTINGS Sub-module (`/erp/parties/settings`)
**Main Routes:**
- `/erp/parties/settings` - Party management settings
- `/erp/parties/settings/fields` - Custom fields configuration
- `/erp/parties/settings/templates` - Party templates

## Legacy Routes (Backward Compatibility)
The following legacy routes are maintained for backward compatibility and redirect to the new structure:
- `/erp/customer-master` → `erp_parties_customers.html`
- `/erp/vendor-master` → `erp_parties_vendors.html`
- `/erp/crm-leads` → `erp_parties_crm.html`
- `/erp/vendor` → `erp_parties_vendors.html`
- `/erp/crm` → `erp_parties_crm.html`
- `/erp/customers` → `erp_parties_customers.html`

## Key Improvements
1. ✅ **No Duplicates** - All duplicate customer, vendor, and CRM routes removed
2. ✅ **Hierarchical Structure** - Clear parent-child relationship with `/erp/parties` as root
3. ✅ **Consistent Naming** - All routes follow `parties/<submodule>/<feature>` pattern
4. ✅ **Organized APIs** - All API endpoints consolidated under PARTY MANAGEMENT section
5. ✅ **Backward Compatible** - Legacy routes maintained for existing integrations
6. ✅ **Scalable** - Easy to add new sub-modules or features

## Template Files Required
The following template files need to be created/updated:
- `erp_parties_dashboard.html` - Main parties dashboard
- `erp_parties_customers.html` - Customer management
- `erp_parties_vendors.html` - Vendor management
- `erp_parties_crm.html` - CRM & leads
- `erp_parties_reports.html` - Party reports
- `erp_parties_settings.html` - Party settings
