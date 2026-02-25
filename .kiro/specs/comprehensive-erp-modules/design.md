# Design Document: Comprehensive ERP Modules

## Overview

This design document specifies the architecture and implementation approach for enhancing a mobile ERP system with 22 comprehensive modules. The system is built using Flask (Python) as the backend framework with Supabase (PostgreSQL) as the database, following a modular blueprint architecture pattern. The frontend uses vanilla JavaScript with a mobile-first responsive design approach.

### System Context

The ERP system replaces basic modules with full-featured enterprise capabilities across:
- Authentication & Security (multi-role access control)
- Company & Financial Setup (GST-compliant configuration)
- Financial Management (invoicing, billing, payments, accounting)
- Inventory Control (stock, batch/expiry, barcode management)
- Purchase Management (PO, GRN, vendor management)
- Customer Relationship Management (leads, follow-ups, customer tracking)
- Reporting & Analytics (comprehensive business intelligence)
- Mobile Performance (optimized for 4G networks, <1s load times)

### Design Goals

1. Maintain existing UI aesthetic (simple blue gradient, no heavy animations)
2. Ensure mobile optimization (responsive 4-7 inch screens, touch-optimized)
3. Implement collapsible sidebar navigation with module/submodule hierarchy
4. Provide GST-compliant invoicing and financial reporting
5. Support multi-tenant data isolation via row-level security
6. Achieve <1 second page load times on 4G connections
7. Enable offline-capable operations with sync on reconnect


## Architecture

### System Architecture

The system follows a modular monolith architecture pattern with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                     Mobile Browser                           │
│  (Vanilla JS + HTML5 + CSS3 + Touch Events)                 │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS/REST API
┌────────────────────▼────────────────────────────────────────┐
│                  Flask Application                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Blueprint Modules (22 ERP Modules)                  │  │
│  │  - auth, company, bank, invoice, purchase, etc.      │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Shared Services Layer                               │  │
│  │  - Authentication, Database, PDF Generation          │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │ SQL/Supabase Client
┌────────────────────▼────────────────────────────────────────┐
│              Supabase (PostgreSQL)                           │
│  - Row-Level Security (RLS) for multi-tenancy               │
│  - Real-time subscriptions for live updates                 │
│  - Authentication & session management                       │
└──────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend:**
- Flask 2.x (Python web framework)
- Flask-CORS (cross-origin resource sharing)
- Supabase Python Client (database connectivity)
- ReportLab/WeasyPrint (PDF generation)
- Bcrypt (password hashing)

**Database:**
- Supabase (managed PostgreSQL)
- Row-Level Security policies for data isolation
- JSONB columns for flexible schema (items, metadata)
- Indexed columns for query performance

**Frontend:**
- Vanilla JavaScript (ES6+)
- HTML5 with semantic markup
- CSS3 with Flexbox/Grid layouts
- Touch event handlers for mobile gestures
- LocalStorage for offline caching

**Infrastructure:**
- Gunicorn (WSGI server)
- Render/Railway (deployment platform)
- CDN for static assets
- SSL/TLS encryption


### Module Architecture Pattern

Each ERP module follows a consistent blueprint pattern:

```python
modules/
  {module_name}/
    __init__.py          # Module initialization
    routes.py            # Flask blueprint with API endpoints
    service.py           # Business logic layer
    models.py            # Data models (optional)
    database.py          # Database initialization (if needed)
```

**Example Module Structure:**
```python
# routes.py
from flask import Blueprint, jsonify, request, session
from .service import ModuleService

module_bp = Blueprint('module', __name__)
service = ModuleService()

@module_bp.route('/api/module/resource', methods=['GET'])
def get_resources():
    user_id = session.get('user_id')
    return jsonify(service.get_resources(user_id))

# service.py
from modules.shared.database import get_db_connection

class ModuleService:
    def get_resources(self, user_id):
        conn = get_db_connection()
        # Business logic
        return results
```

### Navigation Architecture

The collapsible sidebar navigation follows a hierarchical structure:

```
Dashboard (always visible)
├── Authentication
│   ├── Login
│   ├── Change Password
│   └── Logout
├── Setup
│   ├── Company/Firm Setup
│   └── Bank Management
├── Sales
│   ├── Invoice/Billing
│   ├── Challan/Delivery
│   └── Credit Management
├── Purchase
│   ├── Purchase Entry
│   ├── Purchase Order (PO)
│   └── Receive/GRN
├── Inventory
│   ├── Product/Item Master
│   ├── Stock Management
│   ├── Batch & Expiry
│   └── Barcode Management
├── Parties
│   ├── Customer Management
│   └── Vendor/Supplier
├── CRM
│   ├── Leads
│   └── Follow-ups
├── Finance
│   ├── Payment Management
│   ├── Income & Expense
│   └── Basic Accounting
├── Reports
│   ├── Sales Reports
│   ├── Purchase Reports
│   ├── Inventory Reports
│   ├── Financial Reports
│   └── GST Reports
├── Administration
│   ├── Staff & Operator Management
│   └── Backup & Settings
└── Help & Support
```


## Components and Interfaces

### UI Components

#### 1. Collapsible Sidebar Navigation

**Component:** `SidebarNav`

**Structure:**
```html
<div class="sidebar" id="sidebar">
  <div class="sidebar-header">
    <img src="/logo.png" alt="Logo" class="sidebar-logo">
    <button class="sidebar-toggle" onclick="toggleSidebar()">☰</button>
  </div>
  
  <nav class="sidebar-nav">
    <div class="nav-item" onclick="toggleModule('setup')">
      <span class="nav-icon">⚙️</span>
      <span class="nav-label">Setup</span>
      <span class="nav-arrow">▼</span>
    </div>
    <div class="nav-submenu" id="setup-submenu" style="display:none;">
      <a href="/erp/company-setup" class="nav-subitem">Company Setup</a>
      <a href="/erp/bank-management" class="nav-subitem">Bank Management</a>
    </div>
  </nav>
</div>
```

**Styling:**
```css
.sidebar {
  width: 250px;
  background: linear-gradient(180deg, #1e3a8a 0%, #3b82f6 100%);
  color: white;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  transition: transform 0.3s ease;
  z-index: 1000;
}

.sidebar.collapsed {
  transform: translateX(-250px);
}

@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-250px);
  }
  .sidebar.open {
    transform: translateX(0);
  }
}
```

**JavaScript:**
```javascript
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}

function toggleModule(moduleId) {
  const submenu = document.getElementById(`${moduleId}-submenu`);
  const arrow = event.currentTarget.querySelector('.nav-arrow');
  
  if (submenu.style.display === 'none') {
    submenu.style.display = 'block';
    arrow.textContent = '▲';
  } else {
    submenu.style.display = 'none';
    arrow.textContent = '▼';
  }
}
```

#### 2. Dashboard Widgets

**Component:** `DashboardWidget`

**Types:**
- Metric Card (sales, outstanding, stock alerts)
- Chart Widget (sales trends, inventory levels)
- List Widget (recent transactions, pending orders)
- Alert Widget (low stock, expiring products)

**Structure:**
```html
<div class="dashboard-grid">
  <div class="widget metric-card">
    <div class="widget-icon">💰</div>
    <div class="widget-content">
      <h3 class="widget-value">₹45,230</h3>
      <p class="widget-label">Today's Sales</p>
    </div>
  </div>
  
  <div class="widget chart-widget">
    <h3 class="widget-title">Sales Trend (30 Days)</h3>
    <canvas id="salesChart"></canvas>
  </div>
  
  <div class="widget list-widget">
    <h3 class="widget-title">Recent Transactions</h3>
    <ul class="widget-list" id="recentTransactions"></ul>
  </div>
</div>
```

#### 3. Form Components

**Component:** `FormBuilder`

**Features:**
- Input validation (client-side and server-side)
- Auto-save drafts to LocalStorage
- Touch-optimized input fields
- Date pickers for mobile
- Dropdown with search
- Multi-select for items

**Structure:**
```html
<form class="erp-form" id="invoiceForm">
  <div class="form-group">
    <label for="customer">Customer *</label>
    <input type="text" id="customer" class="form-control" 
           list="customerList" required>
    <datalist id="customerList"></datalist>
  </div>
  
  <div class="form-group">
    <label for="invoiceDate">Invoice Date *</label>
    <input type="date" id="invoiceDate" class="form-control" required>
  </div>
  
  <div class="form-section">
    <h3>Items</h3>
    <div id="itemsContainer"></div>
    <button type="button" onclick="addItem()">+ Add Item</button>
  </div>
  
  <div class="form-actions">
    <button type="button" class="btn-secondary" onclick="saveDraft()">
      Save Draft
    </button>
    <button type="submit" class="btn-primary">
      Create Invoice
    </button>
  </div>
</form>
```

#### 4. Data Table Component

**Component:** `DataTable`

**Features:**
- Pagination (50 items per page)
- Search/filter
- Sort by column
- Row actions (edit, delete, view)
- Responsive (cards on mobile)
- Lazy loading

**Structure:**
```html
<div class="data-table-container">
  <div class="table-controls">
    <input type="search" placeholder="Search..." class="table-search">
    <select class="table-filter">
      <option value="all">All Status</option>
      <option value="pending">Pending</option>
      <option value="completed">Completed</option>
    </select>
  </div>
  
  <table class="data-table">
    <thead>
      <tr>
        <th onclick="sortTable('date')">Date ↕</th>
        <th onclick="sortTable('customer')">Customer ↕</th>
        <th onclick="sortTable('amount')">Amount ↕</th>
        <th>Actions</th>
      </tr>
    </thead>
    <tbody id="tableBody"></tbody>
  </table>
  
  <div class="table-pagination">
    <button onclick="prevPage()">← Previous</button>
    <span id="pageInfo">Page 1 of 10</span>
    <button onclick="nextPage()">Next →</button>
  </div>
</div>
```


### API Interfaces

#### Authentication API

```
POST /api/auth/login
Request: { "email": "user@example.com", "password": "***", "user_type": "admin" }
Response: { "success": true, "user_id": "uuid", "session_token": "token" }

POST /api/auth/change-password
Request: { "old_password": "***", "new_password": "***" }
Response: { "success": true, "message": "Password changed" }

POST /api/auth/logout
Response: { "success": true }
```

#### Company Setup API

```
GET /api/erp/company
Response: { "success": true, "data": { "company_name": "...", "gst_number": "..." } }

POST /api/erp/company
Request: { "company_name": "ABC Ltd", "gst_number": "27AABCU9603R1ZM", ... }
Response: { "success": true, "message": "Company saved" }
```

#### Invoice API

```
GET /api/erp/invoices?page=1&limit=50&status=all
Response: { "success": true, "data": [...], "total": 150, "page": 1 }

POST /api/erp/invoices
Request: { "customer_id": "uuid", "items": [...], "payment_mode": "cash" }
Response: { "success": true, "invoice_id": "uuid", "invoice_number": "INV-001" }

GET /api/erp/invoices/{id}/pdf
Response: PDF file download

DELETE /api/erp/invoices/{id}
Response: { "success": true }
```

#### Product API

```
GET /api/erp/products?search=rice&category=grocery
Response: { "success": true, "data": [...] }

POST /api/erp/products
Request: { "name": "Basmati Rice", "hsn_code": "1006", "price": 120, ... }
Response: { "success": true, "product_id": "uuid" }

PUT /api/erp/products/{id}
Request: { "price": 125, "stock": 50 }
Response: { "success": true }
```

#### Stock API

```
GET /api/erp/stock/current
Response: { "success": true, "data": [{ "product_id": "...", "quantity": 50 }] }

POST /api/erp/stock/adjustment
Request: { "product_id": "uuid", "quantity": 10, "type": "add", "reason": "..." }
Response: { "success": true }

GET /api/erp/stock/low-stock?threshold=10
Response: { "success": true, "data": [...] }
```

#### Payment API

```
GET /api/erp/payments?type=received&date_from=2024-01-01
Response: { "success": true, "data": [...] }

POST /api/erp/payments
Request: { "party_name": "Customer A", "amount": 5000, "payment_mode": "upi", ... }
Response: { "success": true, "payment_id": "uuid" }
```

#### Reports API

```
GET /api/erp/reports/sales?from=2024-01-01&to=2024-01-31
Response: { "success": true, "data": { "total_sales": 150000, "transactions": [...] } }

GET /api/erp/reports/profit-loss?year=2024
Response: { "success": true, "data": { "revenue": 500000, "expenses": 300000, ... } }

GET /api/erp/reports/gst?month=2024-01
Response: { "success": true, "data": { "cgst": 5000, "sgst": 5000, "igst": 0 } }

GET /api/erp/reports/export?type=sales&format=pdf
Response: PDF/Excel file download
```

### Service Layer Interfaces

#### Database Service

```python
class DatabaseService:
    def get_connection(self) -> Connection
    def execute_query(self, query: str, params: tuple) -> List[Dict]
    def execute_update(self, query: str, params: tuple) -> int
    def begin_transaction(self) -> Transaction
    def commit_transaction(self, transaction: Transaction)
    def rollback_transaction(self, transaction: Transaction)
```

#### PDF Generation Service

```python
class PDFService:
    def generate_invoice(self, invoice_data: Dict) -> bytes
    def generate_report(self, report_type: str, data: Dict) -> bytes
    def add_company_logo(self, pdf: PDF, logo_url: str)
    def add_gst_details(self, pdf: PDF, gst_data: Dict)
```

#### Notification Service

```python
class NotificationService:
    def send_low_stock_alert(self, product: Dict, user_id: str)
    def send_payment_reminder(self, customer: Dict, amount: float)
    def send_expiry_alert(self, batch: Dict, days_remaining: int)
```

#### Sync Service

```python
class SyncService:
    def sync_offline_data(self, user_id: str, offline_data: List[Dict])
    def get_pending_sync_items(self, user_id: str) -> List[Dict]
    def mark_synced(self, item_ids: List[str])
```


## Data Models

### Database Schema

#### Core Tables

**users** (existing table)
```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    business_name TEXT,
    user_type TEXT DEFAULT 'business_owner',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**erp_company**
```sql
CREATE TABLE erp_company (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    company_name TEXT NOT NULL,
    gst_number TEXT,
    pan_number TEXT,
    financial_year TEXT,
    invoice_prefix TEXT DEFAULT 'INV',
    invoice_starting_number INTEGER DEFAULT 1,
    address TEXT,
    city TEXT,
    state TEXT,
    pincode TEXT,
    phone TEXT,
    email TEXT,
    logo_url TEXT,
    default_tax_rate NUMERIC DEFAULT 18.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);
```

**erp_banks**
```sql
CREATE TABLE erp_banks (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    bank_name TEXT NOT NULL,
    account_number TEXT NOT NULL,
    ifsc_code TEXT NOT NULL,
    branch TEXT,
    account_type TEXT DEFAULT 'current',
    opening_balance NUMERIC DEFAULT 0,
    current_balance NUMERIC DEFAULT 0,
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_banks_user ON erp_banks(user_id);
CREATE INDEX idx_banks_default ON erp_banks(user_id, is_default);
```

**erp_products**
```sql
CREATE TABLE erp_products (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    product_code TEXT NOT NULL,
    product_name TEXT NOT NULL,
    category TEXT,
    brand TEXT,
    hsn_code TEXT,
    gst_rate NUMERIC DEFAULT 18.0,
    unit TEXT DEFAULT 'pcs',
    cost_price NUMERIC DEFAULT 0,
    selling_price NUMERIC NOT NULL,
    min_stock_level INTEGER DEFAULT 10,
    current_stock INTEGER DEFAULT 0,
    barcode TEXT,
    has_batch_tracking BOOLEAN DEFAULT FALSE,
    has_expiry_tracking BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, product_code)
);

CREATE INDEX idx_products_user ON erp_products(user_id);
CREATE INDEX idx_products_barcode ON erp_products(barcode);
CREATE INDEX idx_products_hsn ON erp_products(hsn_code);
```

**erp_customers**
```sql
CREATE TABLE erp_customers (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    customer_name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    pincode TEXT,
    gst_number TEXT,
    credit_limit NUMERIC DEFAULT 0,
    credit_days INTEGER DEFAULT 0,
    outstanding_balance NUMERIC DEFAULT 0,
    total_purchases NUMERIC DEFAULT 0,
    customer_type TEXT DEFAULT 'regular',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customers_user ON erp_customers(user_id);
CREATE INDEX idx_customers_phone ON erp_customers(phone);
```

**erp_vendors**
```sql
CREATE TABLE erp_vendors (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    vendor_name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    pincode TEXT,
    gst_number TEXT,
    payment_terms TEXT,
    outstanding_balance NUMERIC DEFAULT 0,
    total_purchases NUMERIC DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_vendors_user ON erp_vendors(user_id);
```

**erp_invoices**
```sql
CREATE TABLE erp_invoices (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    invoice_number TEXT NOT NULL,
    customer_id TEXT REFERENCES erp_customers(id),
    customer_name TEXT NOT NULL,
    invoice_date DATE NOT NULL,
    due_date DATE,
    subtotal NUMERIC NOT NULL,
    tax_amount NUMERIC DEFAULT 0,
    discount_amount NUMERIC DEFAULT 0,
    total_amount NUMERIC NOT NULL,
    paid_amount NUMERIC DEFAULT 0,
    balance_amount NUMERIC DEFAULT 0,
    payment_status TEXT DEFAULT 'unpaid',
    payment_mode TEXT,
    items JSONB NOT NULL,
    notes TEXT,
    terms_conditions TEXT,
    status TEXT DEFAULT 'draft',
    is_credit BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, invoice_number)
);

CREATE INDEX idx_invoices_user ON erp_invoices(user_id);
CREATE INDEX idx_invoices_customer ON erp_invoices(customer_id);
CREATE INDEX idx_invoices_date ON erp_invoices(invoice_date);
CREATE INDEX idx_invoices_status ON erp_invoices(payment_status);
```

**erp_challans**
```sql
CREATE TABLE erp_challans (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    challan_number TEXT NOT NULL,
    customer_id TEXT REFERENCES erp_customers(id),
    customer_name TEXT NOT NULL,
    challan_date DATE NOT NULL,
    items JSONB NOT NULL,
    total_quantity INTEGER NOT NULL,
    notes TEXT,
    status TEXT DEFAULT 'pending',
    converted_to_invoice_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, challan_number)
);

CREATE INDEX idx_challans_user ON erp_challans(user_id);
CREATE INDEX idx_challans_status ON erp_challans(status);
```


**erp_purchases**
```sql
CREATE TABLE erp_purchases (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    vendor_id TEXT REFERENCES erp_vendors(id),
    vendor_name TEXT NOT NULL,
    bill_number TEXT,
    bill_date DATE NOT NULL,
    bill_image_url TEXT,
    subtotal NUMERIC NOT NULL,
    tax_amount NUMERIC DEFAULT 0,
    total_amount NUMERIC NOT NULL,
    paid_amount NUMERIC DEFAULT 0,
    balance_amount NUMERIC DEFAULT 0,
    payment_status TEXT DEFAULT 'unpaid',
    items JSONB NOT NULL,
    notes TEXT,
    status TEXT DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_purchases_user ON erp_purchases(user_id);
CREATE INDEX idx_purchases_vendor ON erp_purchases(vendor_id);
CREATE INDEX idx_purchases_date ON erp_purchases(bill_date);
```

**erp_purchase_orders**
```sql
CREATE TABLE erp_purchase_orders (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    po_number TEXT NOT NULL,
    vendor_id TEXT REFERENCES erp_vendors(id),
    vendor_name TEXT NOT NULL,
    po_date DATE NOT NULL,
    expected_delivery_date DATE,
    total_amount NUMERIC NOT NULL,
    items JSONB NOT NULL,
    notes TEXT,
    status TEXT DEFAULT 'open',
    approval_status TEXT DEFAULT 'pending',
    approved_by TEXT,
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, po_number)
);

CREATE INDEX idx_po_user ON erp_purchase_orders(user_id);
CREATE INDEX idx_po_status ON erp_purchase_orders(status);
```

**erp_grn**
```sql
CREATE TABLE erp_grn (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    grn_number TEXT NOT NULL,
    po_id TEXT REFERENCES erp_purchase_orders(id),
    vendor_name TEXT NOT NULL,
    grn_date DATE NOT NULL,
    total_quantity INTEGER NOT NULL,
    items JSONB NOT NULL,
    notes TEXT,
    received_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, grn_number)
);

CREATE INDEX idx_grn_user ON erp_grn(user_id);
CREATE INDEX idx_grn_po ON erp_grn(po_id);
```

**erp_stock_transactions**
```sql
CREATE TABLE erp_stock_transactions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    product_id TEXT NOT NULL REFERENCES erp_products(id),
    transaction_type TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    reference_type TEXT,
    reference_id TEXT,
    batch_number TEXT,
    notes TEXT,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_stock_trans_user ON erp_stock_transactions(user_id);
CREATE INDEX idx_stock_trans_product ON erp_stock_transactions(product_id);
CREATE INDEX idx_stock_trans_date ON erp_stock_transactions(created_at);
```

**erp_batches**
```sql
CREATE TABLE erp_batches (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    product_id TEXT NOT NULL REFERENCES erp_products(id),
    product_name TEXT NOT NULL,
    batch_number TEXT NOT NULL,
    manufacturing_date DATE,
    expiry_date DATE,
    quantity INTEGER NOT NULL,
    cost_price NUMERIC,
    is_expired BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, product_id, batch_number)
);

CREATE INDEX idx_batches_user ON erp_batches(user_id);
CREATE INDEX idx_batches_product ON erp_batches(product_id);
CREATE INDEX idx_batches_expiry ON erp_batches(expiry_date);
```

**erp_leads**
```sql
CREATE TABLE erp_leads (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    lead_name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    source TEXT,
    status TEXT DEFAULT 'new',
    notes TEXT,
    follow_up_date DATE,
    converted_to_customer_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_leads_user ON erp_leads(user_id);
CREATE INDEX idx_leads_status ON erp_leads(status);
CREATE INDEX idx_leads_followup ON erp_leads(follow_up_date);
```

**erp_payments**
```sql
CREATE TABLE erp_payments (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    payment_type TEXT NOT NULL,
    party_type TEXT NOT NULL,
    party_id TEXT,
    party_name TEXT NOT NULL,
    amount NUMERIC NOT NULL,
    payment_mode TEXT NOT NULL,
    payment_modes JSONB,
    reference_number TEXT,
    reference_type TEXT,
    reference_id TEXT,
    payment_date DATE NOT NULL,
    bank_id TEXT REFERENCES erp_banks(id),
    status TEXT DEFAULT 'completed',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_payments_user ON erp_payments(user_id);
CREATE INDEX idx_payments_party ON erp_payments(party_id);
CREATE INDEX idx_payments_date ON erp_payments(payment_date);
```

**erp_transactions**
```sql
CREATE TABLE erp_transactions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    transaction_type TEXT NOT NULL,
    category TEXT NOT NULL,
    amount NUMERIC NOT NULL,
    description TEXT,
    transaction_date DATE NOT NULL,
    payment_mode TEXT,
    reference_number TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transactions_user ON erp_transactions(user_id);
CREATE INDEX idx_transactions_type ON erp_transactions(transaction_type);
CREATE INDEX idx_transactions_date ON erp_transactions(transaction_date);
```

**erp_staff**
```sql
CREATE TABLE erp_staff (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    staff_name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    role TEXT NOT NULL,
    username TEXT,
    password_hash TEXT,
    salary NUMERIC DEFAULT 0,
    joining_date DATE,
    permissions JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, username)
);

CREATE INDEX idx_staff_user ON erp_staff(user_id);
CREATE INDEX idx_staff_username ON erp_staff(username);
```


### Data Models (Python)

```python
from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional, Dict

@dataclass
class Company:
    id: str
    user_id: str
    company_name: str
    gst_number: Optional[str]
    financial_year: str
    invoice_prefix: str
    address: str
    phone: str
    email: str
    logo_url: Optional[str]
    created_at: datetime
    updated_at: datetime

@dataclass
class Product:
    id: str
    user_id: str
    product_code: str
    product_name: str
    category: str
    brand: str
    hsn_code: str
    gst_rate: float
    unit: str
    cost_price: float
    selling_price: float
    min_stock_level: int
    current_stock: int
    barcode: Optional[str]
    has_batch_tracking: bool
    has_expiry_tracking: bool
    is_active: bool

@dataclass
class InvoiceItem:
    product_id: str
    product_name: str
    hsn_code: str
    quantity: int
    unit: str
    rate: float
    discount: float
    tax_rate: float
    tax_amount: float
    total: float
    batch_number: Optional[str]

@dataclass
class Invoice:
    id: str
    user_id: str
    invoice_number: str
    customer_id: str
    customer_name: str
    invoice_date: date
    due_date: Optional[date]
    items: List[InvoiceItem]
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    paid_amount: float
    balance_amount: float
    payment_status: str
    payment_mode: Optional[str]
    is_credit: bool
    status: str

@dataclass
class Customer:
    id: str
    user_id: str
    customer_name: str
    phone: str
    email: Optional[str]
    address: str
    gst_number: Optional[str]
    credit_limit: float
    credit_days: int
    outstanding_balance: float
    total_purchases: float
    customer_type: str
    is_active: bool

@dataclass
class StockTransaction:
    id: str
    user_id: str
    product_id: str
    transaction_type: str  # 'in', 'out', 'adjustment'
    quantity: int
    reference_type: Optional[str]  # 'invoice', 'purchase', 'grn'
    reference_id: Optional[str]
    batch_number: Optional[str]
    notes: Optional[str]
    created_by: str
    created_at: datetime

@dataclass
class Payment:
    id: str
    user_id: str
    payment_type: str  # 'received', 'paid'
    party_type: str  # 'customer', 'vendor'
    party_id: str
    party_name: str
    amount: float
    payment_mode: str  # 'cash', 'upi', 'card', 'cheque', 'bank_transfer'
    payment_modes: Optional[Dict]  # For mixed payments
    reference_number: Optional[str]
    payment_date: date
    bank_id: Optional[str]
    status: str
    notes: Optional[str]
```

### JSONB Schema Examples

**Invoice Items (JSONB):**
```json
[
  {
    "product_id": "uuid",
    "product_name": "Basmati Rice 5kg",
    "hsn_code": "1006",
    "quantity": 10,
    "unit": "bag",
    "rate": 450.00,
    "discount": 0,
    "tax_rate": 5.0,
    "tax_amount": 22.50,
    "total": 472.50,
    "batch_number": "BATCH001"
  }
]
```

**Mixed Payment Modes (JSONB):**
```json
{
  "cash": 2000.00,
  "upi": 3000.00,
  "card": 5000.00
}
```

**Staff Permissions (JSONB):**
```json
{
  "modules": ["billing", "inventory", "reports"],
  "actions": {
    "billing": ["create", "view", "edit"],
    "inventory": ["view"],
    "reports": ["view", "export"]
  }
}
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Login Credential Validation

*For any* login attempt with credentials, the system should validate against the database and return success only when credentials match a valid user record.

**Validates: Requirements 1.2**

### Property 2: Password Storage Security

*For any* user password stored in the database, the stored value should be a bcrypt hash, not plaintext.

**Validates: Requirements 1.7**

### Property 3: GST Number Format Validation

*For any* GST registration number input, the system should accept only strings matching the format: 2 digits + 10 alphanumeric (PAN) + 1 digit + 1 letter Z + 1 check digit (total 15 characters).

**Validates: Requirements 2.3**

### Property 4: IFSC Code Format Validation

*For any* IFSC code input, the system should accept only strings matching the format: 4 letters followed by 7 alphanumeric characters (total 11 characters).

**Validates: Requirements 3.7**

### Property 5: Invoice Number Uniqueness

*For any* business owner account, all generated invoice numbers should be unique within that account.

**Validates: Requirements 4.3**

### Property 6: Invoice Creation Stock Reduction

*For any* invoice created with product items, the stock quantity for each product should decrease by the invoiced quantity.

**Validates: Requirements 4.11**

### Property 7: Invoice Deletion Stock Restoration (Round Trip)

*For any* invoice, creating it then deleting it should restore product stock quantities to their original values.

**Validates: Requirements 4.12**

### Property 8: Challan to Invoice Conversion Preserves Data

*For any* challan converted to invoice, all item details (products, quantities, prices) should be preserved exactly in the resulting invoice.

**Validates: Requirements 5.4**

### Property 9: Challan Does Not Affect Stock

*For any* challan created, product stock quantities should remain unchanged until the challan is converted to an invoice.

**Validates: Requirements 5.8**

### Property 10: Purchase Increases Stock

*For any* purchase entry with product items, the stock quantity for each product should increase by the purchased quantity.

**Validates: Requirements 6.5**

### Property 11: Purchase Return Decreases Stock

*For any* purchase return recorded, the stock quantity for each returned product should decrease by the return quantity.

**Validates: Requirements 6.6**

### Property 12: Approved Purchase Orders Are Immutable

*For any* purchase order with approval_status='approved', edit attempts should be rejected by the system.

**Validates: Requirements 7.8**

### Property 13: GRN Increases Stock

*For any* GRN (Goods Receipt Note) created, the stock quantity for each received product should increase by the received quantity.

**Validates: Requirements 8.4**

### Property 14: GRN Cannot Exceed PO Quantities

*For any* purchase order, the total received quantity across all GRNs for each product cannot exceed the ordered quantity for that product.

**Validates: Requirements 8.8**

### Property 15: HSN Code Format Validation

*For any* HSN code input, the system should accept only numeric strings of exactly 4, 6, or 8 digits.

**Validates: Requirements 9.5**

### Property 16: Product Code Uniqueness Per User

*For any* business owner account, all product codes should be unique within that account.

**Validates: Requirements 9.8**

### Property 17: Low Stock Alert Generation

*For any* product where current_stock < min_stock_level, a low stock alert should be generated for the business owner.

**Validates: Requirements 10.4**

### Property 18: Negative Stock Prevention

*For any* stock transaction that would result in negative stock (when negative stock is not allowed), the transaction should be rejected.

**Validates: Requirements 10.9**

### Property 19: Expired Batch Sale Prevention

*For any* product batch where expiry_date < current_date, sale attempts using that batch should be rejected.

**Validates: Requirements 11.7**

### Property 20: Barcode Uniqueness Per User

*For any* business owner account, all product barcodes should be unique within that account.

**Validates: Requirements 12.6**

### Property 21: Credit Limit Enforcement

*For any* customer with a credit limit, the total outstanding balance cannot exceed the credit limit when creating new credit sales.

**Validates: Requirements 13.6**

### Property 22: Customer Outstanding Calculation

*For any* customer, the outstanding balance should always equal: (sum of credit invoice amounts) minus (sum of payments received).

**Validates: Requirements 13.8**

### Property 23: Supplier Outstanding Calculation

*For any* supplier, the outstanding balance should always equal: (sum of purchase amounts) minus (sum of payments made).

**Validates: Requirements 14.5**

### Property 24: Payment Updates Outstanding Balance

*For any* payment recorded against a customer or supplier, their outstanding balance should decrease by the payment amount.

**Validates: Requirements 16.5**

### Property 25: Net Income Calculation

*For any* date range, net income should equal: (sum of income transactions) minus (sum of expense transactions).

**Validates: Requirements 17.8**

### Property 26: Gross Profit Calculation

*For any* date range, gross profit should equal: (total sales revenue) minus (total cost of goods sold).

**Validates: Requirements 18.4**

### Property 27: Net Profit Calculation

*For any* date range, net profit should equal: (gross profit) minus (total expenses).

**Validates: Requirements 18.5**

### Property 28: Staff Username Uniqueness Per User

*For any* business owner account, all staff usernames should be unique within that account.

**Validates: Requirements 19.6**

### Property 29: Backup File Integrity Validation

*For any* backup file submitted for restore, the system should validate JSON structure and required fields before allowing restore.

**Validates: Requirements 22.10**

### Property 30: Multi-Tenant Data Isolation

*For any* user query, the returned data should only include records where user_id matches the authenticated user's ID, never exposing other users' data.

**Validates: Requirements 24.3**

### Property 31: Multi-Table Transaction Atomicity

*For any* operation affecting multiple tables (e.g., invoice creation updating invoices, stock, and customer balance), either all changes should succeed or all should be rolled back.

**Validates: Requirements 24.6**


## Error Handling

### Error Handling Strategy

The system implements a layered error handling approach:

1. **Client-Side Validation** (JavaScript)
   - Input format validation (email, phone, GST, IFSC)
   - Required field checks
   - Range validations (credit limit, stock quantities)
   - Immediate user feedback without server round-trip

2. **Server-Side Validation** (Flask)
   - Re-validate all client inputs
   - Business rule enforcement (credit limits, stock availability)
   - Database constraint checks
   - Authentication and authorization

3. **Database Constraints** (PostgreSQL)
   - Primary key uniqueness
   - Foreign key integrity
   - Check constraints (non-negative amounts)
   - Unique constraints (invoice numbers, product codes)

### Error Response Format

All API endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Human-readable error message",
  "error_code": "ERROR_CODE",
  "field": "field_name",
  "details": {}
}
```

### Error Categories

#### 1. Validation Errors (400 Bad Request)

```python
# Example: Invalid GST format
{
  "success": false,
  "error": "Invalid GST number format. Expected: 2 digits + 10 alphanumeric + 1 digit + Z + 1 digit",
  "error_code": "INVALID_GST_FORMAT",
  "field": "gst_number"
}
```

#### 2. Business Logic Errors (422 Unprocessable Entity)

```python
# Example: Insufficient stock
{
  "success": false,
  "error": "Insufficient stock for product 'Basmati Rice'. Available: 5, Required: 10",
  "error_code": "INSUFFICIENT_STOCK",
  "field": "items",
  "details": {
    "product_id": "uuid",
    "available": 5,
    "required": 10
  }
}

# Example: Credit limit exceeded
{
  "success": false,
  "error": "Credit limit exceeded. Customer limit: ₹50,000, Current outstanding: ₹45,000, New sale: ₹10,000",
  "error_code": "CREDIT_LIMIT_EXCEEDED",
  "field": "customer_id",
  "details": {
    "credit_limit": 50000,
    "current_outstanding": 45000,
    "new_amount": 10000
  }
}
```

#### 3. Authentication Errors (401 Unauthorized)

```python
{
  "success": false,
  "error": "Invalid credentials",
  "error_code": "INVALID_CREDENTIALS"
}

{
  "success": false,
  "error": "Session expired. Please login again",
  "error_code": "SESSION_EXPIRED"
}
```

#### 4. Authorization Errors (403 Forbidden)

```python
{
  "success": false,
  "error": "You do not have permission to access this resource",
  "error_code": "PERMISSION_DENIED",
  "details": {
    "required_permission": "billing.delete",
    "user_role": "operator"
  }
}
```

#### 5. Not Found Errors (404 Not Found)

```python
{
  "success": false,
  "error": "Invoice not found",
  "error_code": "INVOICE_NOT_FOUND",
  "details": {
    "invoice_id": "uuid"
  }
}
```

#### 6. Database Errors (500 Internal Server Error)

```python
{
  "success": false,
  "error": "Database connection failed. Please try again",
  "error_code": "DATABASE_ERROR"
}
```

### Error Handling Implementation

```python
# Service layer error handling
class ERPException(Exception):
    def __init__(self, message, error_code, status_code=400, field=None, details=None):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.field = field
        self.details = details or {}

# Route layer error handling
@erp_bp.errorhandler(ERPException)
def handle_erp_exception(error):
    response = {
        'success': False,
        'error': error.message,
        'error_code': error.error_code
    }
    if error.field:
        response['field'] = error.field
    if error.details:
        response['details'] = error.details
    return jsonify(response), error.status_code

# Usage in service
def create_invoice(invoice_data, user_id):
    # Check stock availability
    for item in invoice_data['items']:
        product = get_product(item['product_id'])
        if product['current_stock'] < item['quantity']:
            raise ERPException(
                f"Insufficient stock for product '{product['product_name']}'",
                'INSUFFICIENT_STOCK',
                422,
                'items',
                {
                    'product_id': item['product_id'],
                    'available': product['current_stock'],
                    'required': item['quantity']
                }
            )
```

### Offline Error Handling

When the mobile app is offline:

1. Queue operations in LocalStorage
2. Display "Offline Mode" indicator
3. Show pending sync count
4. On reconnect, attempt to sync queued operations
5. Handle sync conflicts (e.g., stock changed while offline)

```javascript
// Offline queue management
function queueOfflineOperation(operation) {
  const queue = JSON.parse(localStorage.getItem('offline_queue') || '[]');
  queue.push({
    id: generateUUID(),
    operation: operation,
    timestamp: new Date().toISOString(),
    retries: 0
  });
  localStorage.setItem('offline_queue', JSON.stringify(queue));
  updateOfflineIndicator(queue.length);
}

// Sync on reconnect
window.addEventListener('online', async () => {
  const queue = JSON.parse(localStorage.getItem('offline_queue') || '[]');
  for (const item of queue) {
    try {
      await syncOperation(item);
      removeFromQueue(item.id);
    } catch (error) {
      if (item.retries < 3) {
        item.retries++;
      } else {
        showSyncError(item, error);
      }
    }
  }
});
```

### Transaction Rollback

For multi-table operations, use database transactions:

```python
def create_invoice_with_stock_update(invoice_data, user_id):
    conn = get_db_connection()
    try:
        conn.execute('BEGIN')
        
        # Insert invoice
        invoice_id = insert_invoice(conn, invoice_data, user_id)
        
        # Update stock for each item
        for item in invoice_data['items']:
            update_stock(conn, item['product_id'], -item['quantity'], 
                        'invoice', invoice_id)
        
        # Update customer outstanding
        update_customer_outstanding(conn, invoice_data['customer_id'], 
                                    invoice_data['total_amount'])
        
        conn.execute('COMMIT')
        return invoice_id
        
    except Exception as e:
        conn.execute('ROLLBACK')
        raise ERPException(
            'Failed to create invoice. All changes have been rolled back.',
            'TRANSACTION_FAILED',
            500,
            details={'original_error': str(e)}
        )
```


## Testing Strategy

### Dual Testing Approach

The testing strategy employs both unit tests and property-based tests to ensure comprehensive coverage:

**Unit Tests:**
- Specific examples and edge cases
- Integration points between modules
- Error conditions and boundary cases
- UI component behavior
- API endpoint responses

**Property-Based Tests:**
- Universal properties across all inputs
- Comprehensive input coverage through randomization
- Business rule validation
- Data integrity constraints
- Calculation correctness

### Property-Based Testing Configuration

**Library:** Hypothesis (Python)

**Configuration:**
- Minimum 100 iterations per property test
- Each test references its design document property
- Tag format: `# Feature: comprehensive-erp-modules, Property {number}: {property_text}`

**Example Property Test:**

```python
from hypothesis import given, strategies as st
import pytest

# Feature: comprehensive-erp-modules, Property 6: Invoice Creation Stock Reduction
@given(
    product_stock=st.integers(min_value=10, max_value=1000),
    invoice_quantity=st.integers(min_value=1, max_value=10)
)
def test_invoice_creation_reduces_stock(product_stock, invoice_quantity):
    """
    For any invoice created with product items, the stock quantity 
    for each product should decrease by the invoiced quantity.
    """
    # Setup
    product = create_test_product(initial_stock=product_stock)
    customer = create_test_customer()
    
    # Create invoice
    invoice_data = {
        'customer_id': customer['id'],
        'items': [{
            'product_id': product['id'],
            'quantity': invoice_quantity,
            'rate': 100
        }]
    }
    
    invoice = create_invoice(invoice_data, test_user_id)
    
    # Verify stock reduction
    updated_product = get_product(product['id'])
    expected_stock = product_stock - invoice_quantity
    
    assert updated_product['current_stock'] == expected_stock, \
        f"Stock should be {expected_stock}, but got {updated_product['current_stock']}"
    
    # Cleanup
    cleanup_test_data(invoice['id'], product['id'], customer['id'])
```

### Unit Test Examples

#### 1. Authentication Tests

```python
def test_login_with_valid_credentials():
    """Test successful login with valid credentials"""
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'ValidPass123',
        'user_type': 'business_owner'
    })
    assert response.status_code == 200
    assert response.json['success'] == True
    assert 'user_id' in response.json

def test_login_with_invalid_password():
    """Test login failure with wrong password"""
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'WrongPassword',
        'user_type': 'business_owner'
    })
    assert response.status_code == 401
    assert response.json['success'] == False
    assert response.json['error_code'] == 'INVALID_CREDENTIALS'

def test_password_stored_as_hash():
    """Test that passwords are stored as bcrypt hashes"""
    user = create_test_user('test@example.com', 'MyPassword123')
    stored_password = get_user_password_hash(user['id'])
    
    assert stored_password != 'MyPassword123'
    assert stored_password.startswith('$2b$')  # bcrypt prefix
    assert len(stored_password) == 60  # bcrypt hash length
```

#### 2. Invoice Tests

```python
def test_create_invoice_generates_unique_number():
    """Test that each invoice gets a unique number"""
    customer = create_test_customer()
    
    invoice1 = create_invoice({'customer_id': customer['id'], 'items': [...]})
    invoice2 = create_invoice({'customer_id': customer['id'], 'items': [...]})
    
    assert invoice1['invoice_number'] != invoice2['invoice_number']

def test_invoice_deletion_restores_stock():
    """Test round-trip: create invoice (stock decreases), delete (stock restores)"""
    product = create_test_product(initial_stock=100)
    original_stock = product['current_stock']
    
    # Create invoice
    invoice = create_invoice({
        'customer_id': test_customer_id,
        'items': [{'product_id': product['id'], 'quantity': 10, 'rate': 100}]
    })
    
    # Verify stock decreased
    product_after_invoice = get_product(product['id'])
    assert product_after_invoice['current_stock'] == 90
    
    # Delete invoice
    delete_invoice(invoice['id'])
    
    # Verify stock restored
    product_after_delete = get_product(product['id'])
    assert product_after_delete['current_stock'] == original_stock
```

#### 3. Validation Tests

```python
def test_gst_number_validation():
    """Test GST number format validation"""
    valid_gst = '27AABCU9603R1ZM'
    invalid_gst_short = '27AABCU9603'
    invalid_gst_format = '27-AABCU-9603-R1ZM'
    
    assert validate_gst_number(valid_gst) == True
    assert validate_gst_number(invalid_gst_short) == False
    assert validate_gst_number(invalid_gst_format) == False

def test_ifsc_code_validation():
    """Test IFSC code format validation"""
    valid_ifsc = 'SBIN0001234'
    invalid_ifsc_short = 'SBIN001'
    invalid_ifsc_format = 'SB1N0001234'
    
    assert validate_ifsc_code(valid_ifsc) == True
    assert validate_ifsc_code(invalid_ifsc_short) == False
    assert validate_ifsc_code(invalid_ifsc_format) == False

def test_hsn_code_validation():
    """Test HSN code format validation (4, 6, or 8 digits)"""
    assert validate_hsn_code('1006') == True      # 4 digits
    assert validate_hsn_code('100630') == True    # 6 digits
    assert validate_hsn_code('10063010') == True  # 8 digits
    assert validate_hsn_code('10') == False       # too short
    assert validate_hsn_code('100630101') == False  # too long
    assert validate_hsn_code('10A6') == False     # contains letter
```

#### 4. Business Logic Tests

```python
def test_credit_limit_enforcement():
    """Test that credit sales cannot exceed customer credit limit"""
    customer = create_test_customer(credit_limit=50000, outstanding=45000)
    
    # Attempt sale that would exceed limit
    with pytest.raises(ERPException) as exc_info:
        create_invoice({
            'customer_id': customer['id'],
            'is_credit': True,
            'total_amount': 10000,
            'items': [...]
        })
    
    assert exc_info.value.error_code == 'CREDIT_LIMIT_EXCEEDED'

def test_negative_stock_prevention():
    """Test that stock cannot go negative"""
    product = create_test_product(initial_stock=5)
    
    # Attempt to sell more than available
    with pytest.raises(ERPException) as exc_info:
        create_invoice({
            'customer_id': test_customer_id,
            'items': [{'product_id': product['id'], 'quantity': 10, 'rate': 100}]
        })
    
    assert exc_info.value.error_code == 'INSUFFICIENT_STOCK'

def test_expired_batch_sale_prevention():
    """Test that expired batches cannot be sold"""
    from datetime import date, timedelta
    
    expired_batch = create_test_batch(
        expiry_date=(date.today() - timedelta(days=1)).isoformat()
    )
    
    with pytest.raises(ERPException) as exc_info:
        create_invoice({
            'customer_id': test_customer_id,
            'items': [{
                'product_id': expired_batch['product_id'],
                'batch_number': expired_batch['batch_number'],
                'quantity': 1,
                'rate': 100
            }]
        })
    
    assert exc_info.value.error_code == 'EXPIRED_BATCH'
```

### Integration Tests

```python
def test_complete_invoice_workflow():
    """Test complete invoice creation workflow with stock and customer updates"""
    # Setup
    product = create_test_product(initial_stock=100, cost_price=80, selling_price=100)
    customer = create_test_customer(outstanding=0)
    
    # Create invoice
    invoice = create_invoice({
        'customer_id': customer['id'],
        'is_credit': True,
        'items': [{
            'product_id': product['id'],
            'quantity': 10,
            'rate': 100
        }]
    })
    
    # Verify invoice created
    assert invoice['invoice_number'] is not None
    assert invoice['total_amount'] == 1000
    
    # Verify stock reduced
    updated_product = get_product(product['id'])
    assert updated_product['current_stock'] == 90
    
    # Verify customer outstanding increased
    updated_customer = get_customer(customer['id'])
    assert updated_customer['outstanding_balance'] == 1000
    
    # Record payment
    payment = create_payment({
        'party_type': 'customer',
        'party_id': customer['id'],
        'amount': 500,
        'payment_mode': 'cash'
    })
    
    # Verify outstanding reduced
    customer_after_payment = get_customer(customer['id'])
    assert customer_after_payment['outstanding_balance'] == 500
```

### Performance Tests

```python
def test_page_load_performance():
    """Test that pages load within 1 second"""
    import time
    
    start = time.time()
    response = client.get('/erp/dashboard')
    end = time.time()
    
    load_time = end - start
    assert load_time < 1.0, f"Page load took {load_time}s, expected < 1s"

def test_barcode_scan_performance():
    """Test that barcode lookup completes within 500ms"""
    import time
    
    product = create_test_product(barcode='1234567890123')
    
    start = time.time()
    result = lookup_product_by_barcode('1234567890123')
    end = time.time()
    
    lookup_time = (end - start) * 1000  # Convert to ms
    assert lookup_time < 500, f"Barcode lookup took {lookup_time}ms, expected < 500ms"
```

### Test Data Generators

```python
from hypothesis import strategies as st

# Product generator
@st.composite
def product_strategy(draw):
    return {
        'product_code': draw(st.text(min_size=3, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Nd')))),
        'product_name': draw(st.text(min_size=5, max_size=100)),
        'hsn_code': draw(st.sampled_from(['1006', '100630', '10063010'])),
        'gst_rate': draw(st.sampled_from([0, 5, 12, 18, 28])),
        'cost_price': draw(st.floats(min_value=1, max_value=10000)),
        'selling_price': draw(st.floats(min_value=1, max_value=10000)),
        'current_stock': draw(st.integers(min_value=0, max_value=10000))
    }

# Invoice generator
@st.composite
def invoice_strategy(draw):
    num_items = draw(st.integers(min_value=1, max_value=10))
    items = [
        {
            'product_id': draw(st.uuids()),
            'quantity': draw(st.integers(min_value=1, max_value=100)),
            'rate': draw(st.floats(min_value=1, max_value=1000))
        }
        for _ in range(num_items)
    ]
    return {
        'customer_id': draw(st.uuids()),
        'items': items,
        'payment_mode': draw(st.sampled_from(['cash', 'upi', 'card', 'cheque']))
    }
```

### Test Coverage Goals

- Unit test coverage: > 80%
- Property test coverage: All 31 correctness properties
- Integration test coverage: All critical workflows
- Performance test coverage: All performance requirements

### Continuous Integration

Tests run automatically on:
- Every commit (unit tests)
- Pull requests (unit + integration tests)
- Nightly builds (full test suite including property tests)
- Pre-deployment (smoke tests + critical path tests)


## Mobile Optimization Strategies

### Performance Optimization

#### 1. Code Splitting and Lazy Loading

```javascript
// Load modules on demand
const loadModule = async (moduleName) => {
  const module = await import(`./modules/${moduleName}.js`);
  return module.default;
};

// Lazy load dashboard widgets
document.addEventListener('DOMContentLoaded', async () => {
  const visibleWidgets = getVisibleWidgets();
  for (const widget of visibleWidgets) {
    await loadWidget(widget);
  }
});
```

#### 2. Data Caching Strategy

```javascript
// Cache frequently accessed data
class DataCache {
  constructor() {
    this.cache = new Map();
    this.ttl = 5 * 60 * 1000; // 5 minutes
  }
  
  set(key, value) {
    this.cache.set(key, {
      value: value,
      timestamp: Date.now()
    });
  }
  
  get(key) {
    const item = this.cache.get(key);
    if (!item) return null;
    
    if (Date.now() - item.timestamp > this.ttl) {
      this.cache.delete(key);
      return null;
    }
    
    return item.value;
  }
}

// Usage
const cache = new DataCache();

async function getProducts() {
  const cached = cache.get('products');
  if (cached) return cached;
  
  const products = await fetchProducts();
  cache.set('products', products);
  return products;
}
```

#### 3. Image Optimization

```html
<!-- Responsive images with lazy loading -->
<img 
  src="placeholder.jpg" 
  data-src="product-image.jpg"
  data-srcset="product-image-320w.jpg 320w,
               product-image-640w.jpg 640w,
               product-image-1024w.jpg 1024w"
  sizes="(max-width: 320px) 280px,
         (max-width: 640px) 600px,
         1024px"
  loading="lazy"
  alt="Product Image"
>
```

#### 4. Virtual Scrolling for Long Lists

```javascript
class VirtualScroller {
  constructor(container, itemHeight, renderItem) {
    this.container = container;
    this.itemHeight = itemHeight;
    this.renderItem = renderItem;
    this.visibleItems = Math.ceil(window.innerHeight / itemHeight) + 2;
    this.scrollTop = 0;
    
    this.container.addEventListener('scroll', () => this.onScroll());
  }
  
  setData(data) {
    this.data = data;
    this.container.style.height = `${data.length * this.itemHeight}px`;
    this.render();
  }
  
  onScroll() {
    this.scrollTop = this.container.scrollTop;
    this.render();
  }
  
  render() {
    const startIndex = Math.floor(this.scrollTop / this.itemHeight);
    const endIndex = Math.min(startIndex + this.visibleItems, this.data.length);
    
    const fragment = document.createDocumentFragment();
    for (let i = startIndex; i < endIndex; i++) {
      const item = this.renderItem(this.data[i]);
      item.style.transform = `translateY(${i * this.itemHeight}px)`;
      fragment.appendChild(item);
    }
    
    this.container.innerHTML = '';
    this.container.appendChild(fragment);
  }
}
```

### Touch Optimization

#### 1. Touch Event Handlers

```javascript
// Swipe gesture detection
class SwipeDetector {
  constructor(element, onSwipe) {
    this.element = element;
    this.onSwipe = onSwipe;
    this.startX = 0;
    this.startY = 0;
    
    element.addEventListener('touchstart', (e) => this.handleStart(e));
    element.addEventListener('touchend', (e) => this.handleEnd(e));
  }
  
  handleStart(e) {
    this.startX = e.touches[0].clientX;
    this.startY = e.touches[0].clientY;
  }
  
  handleEnd(e) {
    const endX = e.changedTouches[0].clientX;
    const endY = e.changedTouches[0].clientY;
    
    const deltaX = endX - this.startX;
    const deltaY = endY - this.startY;
    
    if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
      this.onSwipe(deltaX > 0 ? 'right' : 'left');
    }
  }
}

// Usage: Swipe to open/close sidebar
new SwipeDetector(document.body, (direction) => {
  if (direction === 'right') {
    openSidebar();
  } else if (direction === 'left') {
    closeSidebar();
  }
});
```

#### 2. Touch-Friendly UI Elements

```css
/* Minimum touch target size: 44x44px */
.btn, .nav-item, .form-control {
  min-height: 44px;
  min-width: 44px;
  padding: 12px 16px;
}

/* Prevent text selection during touch */
.no-select {
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

/* Remove tap highlight */
* {
  -webkit-tap-highlight-color: transparent;
}

/* Custom tap feedback */
.btn:active {
  transform: scale(0.98);
  opacity: 0.8;
}
```

### Offline Support

#### 1. Service Worker for Offline Caching

```javascript
// service-worker.js
const CACHE_NAME = 'erp-v1';
const urlsToCache = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js',
  '/static/images/logo.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        if (response) {
          return response;
        }
        return fetch(event.request);
      })
  );
});
```

#### 2. Offline Data Sync

```javascript
// Offline queue manager
class OfflineQueue {
  constructor() {
    this.queue = this.loadQueue();
  }
  
  loadQueue() {
    const stored = localStorage.getItem('offline_queue');
    return stored ? JSON.parse(stored) : [];
  }
  
  saveQueue() {
    localStorage.setItem('offline_queue', JSON.stringify(this.queue));
  }
  
  add(operation) {
    this.queue.push({
      id: generateUUID(),
      operation: operation,
      timestamp: new Date().toISOString(),
      retries: 0,
      status: 'pending'
    });
    this.saveQueue();
  }
  
  async sync() {
    if (!navigator.onLine) return;
    
    for (const item of this.queue) {
      if (item.status === 'pending') {
        try {
          await this.syncItem(item);
          item.status = 'completed';
        } catch (error) {
          item.retries++;
          if (item.retries >= 3) {
            item.status = 'failed';
          }
        }
      }
    }
    
    this.queue = this.queue.filter(item => item.status !== 'completed');
    this.saveQueue();
  }
  
  async syncItem(item) {
    const response = await fetch(item.operation.url, {
      method: item.operation.method,
      headers: item.operation.headers,
      body: JSON.stringify(item.operation.data)
    });
    
    if (!response.ok) {
      throw new Error('Sync failed');
    }
  }
}

// Auto-sync when online
window.addEventListener('online', () => {
  const queue = new OfflineQueue();
  queue.sync();
});
```

### Network Optimization

#### 1. Request Batching

```javascript
// Batch multiple API requests
class RequestBatcher {
  constructor(batchDelay = 50) {
    this.batchDelay = batchDelay;
    this.queue = [];
    this.timer = null;
  }
  
  add(request) {
    return new Promise((resolve, reject) => {
      this.queue.push({ request, resolve, reject });
      
      if (this.timer) {
        clearTimeout(this.timer);
      }
      
      this.timer = setTimeout(() => this.flush(), this.batchDelay);
    });
  }
  
  async flush() {
    if (this.queue.length === 0) return;
    
    const batch = this.queue.splice(0);
    const requests = batch.map(item => item.request);
    
    try {
      const response = await fetch('/api/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ requests })
      });
      
      const results = await response.json();
      
      batch.forEach((item, index) => {
        item.resolve(results[index]);
      });
    } catch (error) {
      batch.forEach(item => item.reject(error));
    }
  }
}
```

#### 2. Compression

```python
# Enable gzip compression in Flask
from flask import Flask
from flask_compress import Compress

app = Flask(__name__)
Compress(app)

# Configure compression
app.config['COMPRESS_MIMETYPES'] = [
    'text/html',
    'text/css',
    'text/javascript',
    'application/json',
    'application/javascript'
]
app.config['COMPRESS_LEVEL'] = 6
app.config['COMPRESS_MIN_SIZE'] = 500
```

### Responsive Design

```css
/* Mobile-first responsive design */

/* Base styles for mobile (320px - 767px) */
.container {
  width: 100%;
  padding: 0 16px;
}

.sidebar {
  width: 100%;
  transform: translateX(-100%);
}

.data-table {
  display: none;
}

.data-cards {
  display: block;
}

/* Tablet (768px - 1023px) */
@media (min-width: 768px) {
  .container {
    max-width: 720px;
    margin: 0 auto;
  }
  
  .sidebar {
    width: 250px;
  }
  
  .dashboard-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Desktop (1024px+) */
@media (min-width: 1024px) {
  .container {
    max-width: 960px;
  }
  
  .data-table {
    display: table;
  }
  
  .data-cards {
    display: none;
  }
  
  .dashboard-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
```


## Security Considerations

### Authentication & Authorization

#### 1. Session Management

```python
from flask import session
from datetime import timedelta

# Configure session
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent XSS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection

# Session validation middleware
@app.before_request
def validate_session():
    if request.endpoint and request.endpoint != 'auth.login':
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Refresh session on activity
        session.modified = True
```

#### 2. Role-Based Access Control (RBAC)

```python
from functools import wraps

def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id')
            user_type = session.get('user_type')
            
            if user_type == 'business_owner':
                # Business owners have all permissions
                return f(*args, **kwargs)
            
            # Check staff permissions
            staff = get_staff_by_user_id(user_id)
            if not staff or not staff.get('is_active'):
                return jsonify({'error': 'Access denied'}), 403
            
            permissions = staff.get('permissions', {})
            if permission not in permissions.get('actions', {}):
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Usage
@erp_bp.route('/api/erp/invoices', methods=['DELETE'])
@require_permission('billing.delete')
def delete_invoice(invoice_id):
    # Delete logic
    pass
```

### Data Security

#### 1. Row-Level Security (RLS) in Supabase

```sql
-- Enable RLS on all tables
ALTER TABLE erp_invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE erp_products ENABLE ROW LEVEL SECURITY;
ALTER TABLE erp_customers ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their own data
CREATE POLICY user_isolation_policy ON erp_invoices
  FOR ALL
  USING (user_id = current_setting('app.user_id')::TEXT);

CREATE POLICY user_isolation_policy ON erp_products
  FOR ALL
  USING (user_id = current_setting('app.user_id')::TEXT);

-- Set user context in application
def set_user_context(conn, user_id):
    conn.execute(f"SET app.user_id = '{user_id}'")
```

#### 2. SQL Injection Prevention

```python
# Always use parameterized queries
def get_invoices(user_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # CORRECT: Parameterized query
    query = "SELECT * FROM erp_invoices WHERE user_id = %s AND status = %s"
    cursor.execute(query, (user_id, status))
    
    # WRONG: String concatenation (vulnerable to SQL injection)
    # query = f"SELECT * FROM erp_invoices WHERE user_id = '{user_id}'"
    
    return cursor.fetchall()
```

#### 3. Input Validation & Sanitization

```python
from bleach import clean
import re

def sanitize_input(value, input_type='text'):
    """Sanitize user input to prevent XSS and injection attacks"""
    if value is None:
        return None
    
    # Remove HTML tags
    value = clean(str(value), tags=[], strip=True)
    
    if input_type == 'email':
        # Validate email format
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            raise ValueError('Invalid email format')
    
    elif input_type == 'phone':
        # Remove non-numeric characters
        value = re.sub(r'[^0-9+]', '', value)
    
    elif input_type == 'gst':
        # Validate GST format
        if not re.match(r'^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}$', value):
            raise ValueError('Invalid GST format')
    
    return value

# Usage in routes
@erp_bp.route('/api/erp/company', methods=['POST'])
def save_company():
    data = request.json
    
    company_data = {
        'company_name': sanitize_input(data.get('company_name'), 'text'),
        'gst_number': sanitize_input(data.get('gst_number'), 'gst'),
        'email': sanitize_input(data.get('email'), 'email'),
        'phone': sanitize_input(data.get('phone'), 'phone')
    }
    
    # Save to database
    save_company_data(company_data)
```

### API Security

#### 1. Rate Limiting

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Apply rate limiting to sensitive endpoints
@erp_bp.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # Login logic
    pass

@erp_bp.route('/api/erp/invoices', methods=['POST'])
@limiter.limit("100 per hour")
def create_invoice():
    # Invoice creation logic
    pass
```

#### 2. CORS Configuration

```python
from flask_cors import CORS

# Configure CORS for mobile app
CORS(app, 
     origins=['https://yourdomain.com', 'capacitor://localhost'],
     methods=['GET', 'POST', 'PUT', 'DELETE'],
     allow_headers=['Content-Type', 'Authorization'],
     supports_credentials=True)
```

#### 3. HTTPS Enforcement

```python
from flask_talisman import Talisman

# Force HTTPS in production
if app.config['ENV'] == 'production':
    Talisman(app, 
             force_https=True,
             strict_transport_security=True,
             content_security_policy={
                 'default-src': "'self'",
                 'script-src': ["'self'", "'unsafe-inline'"],
                 'style-src': ["'self'", "'unsafe-inline'"]
             })
```

### Data Encryption

#### 1. Sensitive Data Encryption

```python
from cryptography.fernet import Fernet
import os

# Generate encryption key (store securely, not in code)
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
cipher = Fernet(ENCRYPTION_KEY.encode())

def encrypt_sensitive_data(data):
    """Encrypt sensitive data like bank account numbers"""
    return cipher.encrypt(data.encode()).decode()

def decrypt_sensitive_data(encrypted_data):
    """Decrypt sensitive data"""
    return cipher.decrypt(encrypted_data.encode()).decode()

# Usage
def save_bank_account(bank_data):
    bank_data['account_number'] = encrypt_sensitive_data(bank_data['account_number'])
    # Save to database
```

#### 2. Password Hashing

```python
import bcrypt

def hash_password(password):
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password, hashed):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode(), hashed.encode())
```

### Audit Logging

```python
def log_audit_event(user_id, action, resource_type, resource_id, details=None):
    """Log security-relevant events for audit trail"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO audit_log (id, user_id, action, resource_type, resource_id, 
                               details, ip_address, user_agent, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        str(uuid.uuid4()),
        user_id,
        action,
        resource_type,
        resource_id,
        json.dumps(details) if details else None,
        request.remote_addr,
        request.user_agent.string,
        datetime.now().isoformat()
    ))
    
    conn.commit()

# Usage
@erp_bp.route('/api/erp/invoices/<invoice_id>', methods=['DELETE'])
def delete_invoice(invoice_id):
    user_id = session.get('user_id')
    
    # Delete invoice
    delete_invoice_from_db(invoice_id)
    
    # Log audit event
    log_audit_event(user_id, 'DELETE', 'invoice', invoice_id, {
        'invoice_number': invoice['invoice_number'],
        'amount': invoice['total_amount']
    })
    
    return jsonify({'success': True})
```

## Deployment Architecture

### Production Environment

```
┌─────────────────────────────────────────────────────────────┐
│                     Load Balancer (Nginx)                    │
│                  SSL Termination (Let's Encrypt)             │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────┐       ┌───────▼────────┐
│  App Server 1  │       │  App Server 2  │
│  (Gunicorn)    │       │  (Gunicorn)    │
│  Flask App     │       │  Flask App     │
└───────┬────────┘       └───────┬────────┘
        │                         │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   Supabase PostgreSQL   │
        │   (Managed Database)    │
        └─────────────────────────┘
```

### Deployment Configuration

**Gunicorn Configuration (gunicorn.conf.py):**
```python
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
preload_app = True
accesslog = "-"
errorlog = "-"
loglevel = "info"
```

**Nginx Configuration:**
```nginx
upstream flask_app {
    server app1:5000;
    server app2:5000;
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    client_max_body_size 16M;
    
    location / {
        proxy_pass http://flask_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static {
        alias /app/frontend/assets/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### Environment Variables

```bash
# .env.production
FLASK_ENV=production
SECRET_KEY=<strong-random-key>
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=<your-supabase-key>
ENCRYPTION_KEY=<encryption-key>
ALLOWED_ORIGINS=https://yourdomain.com
```

### Monitoring & Logging

```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
if app.config['ENV'] == 'production':
    handler = RotatingFileHandler('logs/app.log', maxBytes=10000000, backupCount=5)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
```


## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Core Infrastructure:**
- Set up database schema in Supabase
- Implement authentication system with multi-role support
- Create base UI components (sidebar, forms, tables)
- Establish API structure and error handling

**Deliverables:**
- Working authentication (login, logout, password change)
- Database tables created with RLS policies
- Base UI framework with responsive sidebar navigation
- API error handling middleware

### Phase 2: Setup Modules (Weeks 3-4)

**Company & Bank Setup:**
- Company profile management
- GST number validation
- Bank account management
- Financial year configuration

**Deliverables:**
- Company setup screen with logo upload
- Bank management with default bank selection
- Settings persistence in Supabase
- Validation for GST and IFSC codes

### Phase 3: Core Sales (Weeks 5-7)

**Invoice & Billing:**
- Invoice creation with GST calculation
- PDF generation with company branding
- Payment recording (cash, UPI, card, cheque)
- Credit invoice management

**Challan Management:**
- Delivery challan creation
- Challan to invoice conversion
- Challan tracking and reports

**Deliverables:**
- Complete invoicing workflow
- GST-compliant invoice PDFs
- Challan management system
- Payment tracking

### Phase 4: Inventory (Weeks 8-10)

**Product Management:**
- Product master with HSN codes
- Category and brand management
- Barcode generation and scanning
- Stock level tracking

**Stock Management:**
- Stock inward/outward transactions
- Stock adjustments
- Low stock alerts
- Batch and expiry tracking

**Deliverables:**
- Product catalog with search/filter
- Real-time stock tracking
- Barcode scanning functionality
- Automated low stock notifications

### Phase 5: Purchase (Weeks 11-12)

**Purchase Management:**
- Purchase entry with vendor selection
- Purchase returns
- Bill image upload

**Purchase Orders & GRN:**
- PO creation and approval workflow
- GRN against PO
- PO status tracking

**Deliverables:**
- Complete purchase workflow
- PO approval system
- GRN with stock updates
- Vendor outstanding tracking

### Phase 6: Parties & CRM (Weeks 13-14)

**Customer Management:**
- Customer profiles with credit limits
- Outstanding balance tracking
- Customer categorization

**Vendor Management:**
- Vendor profiles
- Payment terms
- Outstanding tracking

**CRM:**
- Lead management
- Follow-up scheduling
- Lead conversion to customer

**Deliverables:**
- Customer and vendor management
- CRM with lead pipeline
- Follow-up reminders
- Outstanding reports

### Phase 7: Finance & Reports (Weeks 15-16)

**Financial Management:**
- Income and expense tracking
- Payment management with mixed modes
- Basic accounting reports

**Reporting:**
- Sales reports with filters
- Purchase reports
- Inventory reports
- GST reports
- Profit & loss statements

**Deliverables:**
- Comprehensive reporting system
- Financial dashboards
- Export to PDF/Excel
- GST compliance reports

### Phase 8: Administration (Week 17)

**Staff Management:**
- Staff/operator accounts
- Role-based permissions
- Login history tracking

**Backup & Settings:**
- Data backup/restore
- System settings
- Notification preferences

**Deliverables:**
- Staff management with RBAC
- Backup/restore functionality
- System configuration

### Phase 9: Mobile Optimization (Week 18)

**Performance:**
- Code splitting and lazy loading
- Image optimization
- Virtual scrolling for lists
- Caching strategy

**Offline Support:**
- Service worker implementation
- Offline queue management
- Sync on reconnect

**Deliverables:**
- <1s page load times
- Offline-capable app
- Touch-optimized UI
- PWA capabilities

### Phase 10: Testing & Deployment (Weeks 19-20)

**Testing:**
- Unit tests for all modules
- Property-based tests for correctness
- Integration tests for workflows
- Performance testing

**Deployment:**
- Production environment setup
- SSL configuration
- Monitoring and logging
- Documentation

**Deliverables:**
- >80% test coverage
- Production deployment
- User documentation
- Admin documentation

## Database Migration Scripts

### Initial Schema Setup

```sql
-- Run this in Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create all tables (see Data Models section for complete schema)

-- Enable Row-Level Security
ALTER TABLE erp_company ENABLE ROW LEVEL SECURITY;
ALTER TABLE erp_banks ENABLE ROW LEVEL SECURITY;
ALTER TABLE erp_products ENABLE ROW LEVEL SECURITY;
ALTER TABLE erp_customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE erp_vendors ENABLE ROW LEVEL SECURITY;
ALTER TABLE erp_invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE erp_challans ENABLE ROW LEVEL SECURITY;
ALTER TABLE erp_purchases ENABLE ROW LEVEL SECURITY;
ALTER TABLE erp_purchase_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE erp_grn ENABLE ROW LEVEL SECURITY;
ALTER TABLE erp_stock_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE erp_batches ENABLE ROW LEVEL SECURITY;
ALTER TABLE erp_leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE erp_payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE erp_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE erp_staff ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY user_isolation ON erp_company
  FOR ALL USING (user_id = current_setting('app.user_id', true)::TEXT);

CREATE POLICY user_isolation ON erp_banks
  FOR ALL USING (user_id = current_setting('app.user_id', true)::TEXT);

-- Repeat for all tables...

-- Create indexes for performance
CREATE INDEX idx_invoices_user_date ON erp_invoices(user_id, invoice_date DESC);
CREATE INDEX idx_products_user_code ON erp_products(user_id, product_code);
CREATE INDEX idx_customers_user_phone ON erp_customers(user_id, phone);
CREATE INDEX idx_stock_trans_product_date ON erp_stock_transactions(product_id, created_at DESC);

-- Create audit log table
CREATE TABLE audit_log (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT,
    details JSONB,
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_user_date ON audit_log(user_id, created_at DESC);
```

## Diagrams

### System Context Diagram

```mermaid
graph TB
    User[Business Owner/Operator]
    Mobile[Mobile Browser]
    Flask[Flask Application]
    Supabase[(Supabase PostgreSQL)]
    
    User -->|Interacts| Mobile
    Mobile -->|HTTPS/REST| Flask
    Flask -->|SQL Queries| Supabase
    Flask -->|Authentication| Supabase
    Supabase -->|Real-time Updates| Flask
```

### Invoice Creation Flow

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Mobile UI
    participant API as Flask API
    participant DB as Supabase DB
    
    U->>UI: Fill invoice form
    UI->>UI: Validate inputs
    UI->>API: POST /api/erp/invoices
    API->>API: Validate business rules
    API->>DB: BEGIN TRANSACTION
    API->>DB: INSERT invoice
    API->>DB: UPDATE stock quantities
    API->>DB: UPDATE customer outstanding
    API->>DB: COMMIT TRANSACTION
    DB-->>API: Success
    API-->>UI: Invoice created
    UI-->>U: Show success + PDF
```

### Data Flow Diagram

```mermaid
graph LR
    A[User Input] --> B[Client Validation]
    B --> C[API Request]
    C --> D[Server Validation]
    D --> E[Business Logic]
    E --> F[Database Transaction]
    F --> G[Response]
    G --> H[UI Update]
    H --> I[User Feedback]
```

## Conclusion

This design document provides a comprehensive blueprint for implementing 22 full-featured ERP modules in a mobile-optimized Flask/Supabase application. The design emphasizes:

1. **Modularity**: Clear separation of concerns with Flask blueprints
2. **Performance**: <1s load times through caching, lazy loading, and optimization
3. **Security**: Multi-layer security with RLS, RBAC, and encryption
4. **Correctness**: 31 testable properties ensuring business logic integrity
5. **Mobile-First**: Touch-optimized UI with offline support
6. **Scalability**: Stateless architecture supporting horizontal scaling
7. **Maintainability**: Consistent patterns and comprehensive testing

The implementation roadmap provides a structured 20-week plan to deliver all modules incrementally, with each phase building on the previous foundation. The design supports the existing UI aesthetic while providing enterprise-grade functionality for small to medium businesses.

