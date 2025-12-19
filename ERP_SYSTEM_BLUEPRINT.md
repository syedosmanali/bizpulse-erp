# COMPLETE ERP SYSTEM BLUEPRINT
## Production-Ready Architecture for Large-Scale Business Management

---

## 1. OVERALL SYSTEM ARCHITECTURE

### **DECISION: MODULAR MONOLITH APPROACH**

**Chosen Architecture:** Modular Monolith with Service-Oriented Components

**Justification:**
- **Simplicity for Teams:** Single codebase easier for new backend engineers to understand
- **Deployment Simplicity:** One application to deploy, monitor, and scale
- **Data Consistency:** ACID transactions across all business operations
- **Performance:** No network latency between modules
- **Cost Effective:** Lower infrastructure costs than microservices
- **Future Migration Path:** Can extract modules to microservices when needed

**Architecture Layers:**
```
┌─────────────────────────────────────────────────────────────┐
│                    API GATEWAY LAYER                        │
│  (Rate Limiting, Authentication, Request Routing)           │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                         │
│  REST APIs (v1, v2) | GraphQL | WebSocket | Mobile APIs    │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                      │
│  Sales | Inventory | Accounting | CRM | Reports | Auth     │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                   DATA ACCESS LAYER                         │
│  Repository Pattern | ORM | Query Builders | Caching       │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                   INFRASTRUCTURE LAYER                      │
│  Database | File Storage | Message Queue | External APIs   │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. BACKEND FOLDER STRUCTURE

```
erp_system/
├── app/                              # Main application package
│   ├── __init__.py                   # App factory pattern
│   ├── config/                       # Configuration management
│   │   ├── __init__.py
│   │   ├── base.py                   # Base configuration
│   │   ├── development.py            # Dev environment
│   │   ├── production.py             # Prod environment
│   │   └── testing.py                # Test environment
│   │
│   ├── core/                         # Core system components
│   │   ├── __init__.py
│   │   ├── database.py               # Database connection & session management
│   │   ├── cache.py                  # Redis/Memcached integration
│   │   ├── security.py               # Security utilities (JWT, encryption)
│   │   ├── exceptions.py             # Custom exception classes
│   │   ├── validators.py             # Input validation utilities
│   │   └── middleware.py             # Custom middleware
│   │
│   ├── models/                       # Database models (SQLAlchemy)
│   │   ├── __init__.py
│   │   ├── base.py                   # Base model with common fields
│   │   ├── user.py                   # User, Role, Permission models
│   │   ├── company.py                # Multi-tenant company models
│   │   ├── inventory.py              # Product, Category, Stock models
│   │   ├── sales.py                  # Order, Invoice, Payment models
│   │   ├── accounting.py             # Account, Transaction, Journal models
│   │   ├── crm.py                    # Customer, Lead, Contact models
│   │   └── audit.py                  # Audit trail models
│   │
│   ├── api/                          # API layer (versioned)
│   │   ├── __init__.py
│   │   ├── v1/                       # API Version 1
│   │   │   ├── __init__.py
│   │   │   ├── auth.py               # Authentication endpoints
│   │   │   ├── users.py              # User management
│   │   │   ├── inventory.py          # Inventory management
│   │   │   ├── sales.py              # Sales operations
│   │   │   ├── accounting.py         # Accounting operations
│   │   │   ├── reports.py            # Reporting endpoints
│   │   │   └── mobile.py             # Mobile-specific endpoints
│   │   │
│   │   ├── v2/                       # API Version 2 (future)
│   │   │   └── __init__.py
│   │   │
│   │   └── common/                   # Shared API utilities
│   │       ├── __init__.py
│   │       ├── decorators.py         # Auth, validation decorators
│   │       ├── serializers.py        # Data serialization
│   │       └── pagination.py         # Pagination utilities
│   │
│   ├── services/                     # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py           # Authentication business logic
│   │   ├── user_service.py           # User management logic
│   │   ├── inventory_service.py      # Inventory business rules
│   │   ├── sales_service.py          # Sales processing logic
│   │   ├── accounting_service.py     # Accounting calculations
│   │   ├── report_service.py         # Report generation
│   │   ├── notification_service.py   # Email/SMS/Push notifications
│   │   └── sync_service.py           # Mobile offline sync logic
│   │
│   ├── repositories/                 # Data access layer
│   │   ├── __init__.py
│   │   ├── base_repository.py        # Base repository pattern
│   │   ├── user_repository.py        # User data access
│   │   ├── inventory_repository.py   # Inventory data access
│   │   ├── sales_repository.py       # Sales data access
│   │   └── accounting_repository.py  # Accounting data access
│   │
│   ├── utils/                        # Utility functions
│   │   ├── __init__.py
│   │   ├── helpers.py                # General helper functions
│   │   ├── date_utils.py             # Date/time utilities
│   │   ├── file_utils.py             # File handling utilities
│   │   ├── email_utils.py            # Email utilities
│   │   └── pdf_generator.py          # PDF generation utilities
│   │
│   └── tasks/                        # Background tasks
│       ├── __init__.py
│       ├── celery_app.py             # Celery configuration
│       ├── email_tasks.py            # Email sending tasks
│       ├── report_tasks.py           # Report generation tasks
│       └── sync_tasks.py             # Data synchronization tasks
│
├── migrations/                       # Database migrations
│   ├── versions/                     # Migration files
│   └── alembic.ini                   # Alembic configuration
│
├── tests/                            # Test suite
│   ├── __init__.py
│   ├── conftest.py                   # Test configuration
│   ├── unit/                         # Unit tests
│   ├── integration/                  # Integration tests
│   └── e2e/                          # End-to-end tests
│
├── docs/                             # Documentation
│   ├── api/                          # API documentation
│   ├── deployment/                   # Deployment guides
│   └── architecture/                 # Architecture documentation
│
├── scripts/                          # Utility scripts
│   ├── setup_db.py                   # Database setup
│   ├── seed_data.py                  # Sample data seeding
│   └── backup_db.py                  # Database backup
│
├── requirements/                     # Dependencies
│   ├── base.txt                      # Base requirements
│   ├── development.txt               # Dev requirements
│   ├── production.txt                # Prod requirements
│   └── testing.txt                   # Test requirements
│
├── docker/                           # Docker configuration
│   ├── Dockerfile                    # Application container
│   ├── docker-compose.yml            # Local development
│   └── docker-compose.prod.yml       # Production setup
│
├── .env.example                      # Environment variables template
├── .gitignore                        # Git ignore rules
├── README.md                         # Project documentation
├── run.py                            # Application entry point
└── wsgi.py                           # WSGI entry point
```

**Key Architectural Decisions:**

1. **Repository Pattern:** Separates data access from business logic
2. **Service Layer:** Contains all business rules and validations
3. **API Versioning:** Ensures backward compatibility
4. **Configuration Management:** Environment-specific settings
5. **Modular Structure:** Each domain has its own models, services, repositories

---

## 3. DATABASE SCHEMA DESIGN

### **Primary Database: PostgreSQL**
**Justification:** ACID compliance, JSON support, excellent performance, mature ecosystem

### **Core Tables Structure:**

```sql
-- ============================================================================
-- MULTI-TENANCY & AUTHENTICATION
-- ============================================================================

-- Companies (Multi-tenant support)
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    domain VARCHAR(255),
    subscription_plan VARCHAR(50) DEFAULT 'basic',
    subscription_status VARCHAR(20) DEFAULT 'active',
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Users (Multi-role support)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    avatar_url VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    last_login_at TIMESTAMP WITH TIME ZONE,
    password_changed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Roles & Permissions (RBAC)
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    permissions JSONB DEFAULT '[]',
    is_system_role BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    role_id UUID NOT NULL REFERENCES roles(id),
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    assigned_by UUID REFERENCES users(id),
    UNIQUE(user_id, role_id)
);

-- ============================================================================
-- INVENTORY MANAGEMENT
-- ============================================================================

-- Product Categories
CREATE TABLE product_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES product_categories(id),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Products
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id),
    category_id UUID REFERENCES product_categories(id),
    sku VARCHAR(100) NOT NULL,
    barcode VARCHAR(100),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    unit_of_measure VARCHAR(20) DEFAULT 'piece',
    cost_price DECIMAL(15,4) DEFAULT 0,
    selling_price DECIMAL(15,4) DEFAULT 0,
    tax_rate DECIMAL(5,2) DEFAULT 0,
    track_inventory BOOLEAN DEFAULT true,
    is_active BOOLEAN DEFAULT true,
    attributes JSONB DEFAULT '{}',
    images JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(company_id, sku)
);

-- Inventory Tracking
CREATE TABLE inventory_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id),
    product_id UUID NOT NULL REFERENCES products(id),
    warehouse_id UUID, -- Future: Multi-warehouse support
    quantity_on_hand DECIMAL(15,4) DEFAULT 0,
    quantity_reserved DECIMAL(15,4) DEFAULT 0,
    quantity_available DECIMAL(15,4) GENERATED ALWAYS AS (quantity_on_hand - quantity_reserved) STORED,
    reorder_point DECIMAL(15,4) DEFAULT 0,
    reorder_quantity DECIMAL(15,4) DEFAULT 0,
    last_counted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, product_id, warehouse_id)
);

-- Stock Movements (Audit Trail)
CREATE TABLE stock_movements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id),
    product_id UUID NOT NULL REFERENCES products(id),
    movement_type VARCHAR(50) NOT NULL, -- 'sale', 'purchase', 'adjustment', 'transfer'
    reference_type VARCHAR(50), -- 'order', 'invoice', 'adjustment'
    reference_id UUID,
    quantity_change DECIMAL(15,4) NOT NULL,
    quantity_before DECIMAL(15,4) NOT NULL,
    quantity_after DECIMAL(15,4) NOT NULL,
    unit_cost DECIMAL(15,4),
    notes TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- SALES & ORDER MANAGEMENT
-- ============================================================================

-- Customers
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id),
    customer_number VARCHAR(50),
    type VARCHAR(20) DEFAULT 'individual', -- 'individual', 'business'
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    tax_number VARCHAR(50),
    credit_limit DECIMAL(15,2) DEFAULT 0,
    payment_terms INTEGER DEFAULT 30, -- Days
    billing_address JSONB,
    shipping_address JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Sales Orders
CREATE TABLE sales_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id),
    order_number VARCHAR(100) NOT NULL,
    customer_id UUID REFERENCES customers(id),
    status VARCHAR(20) DEFAULT 'draft', -- 'draft', 'confirmed', 'shipped', 'delivered', 'cancelled'
    order_date DATE NOT NULL,
    required_date DATE,
    shipped_date DATE,
    subtotal DECIMAL(15,2) DEFAULT 0,
    tax_amount DECIMAL(15,2) DEFAULT 0,
    discount_amount DECIMAL(15,2) DEFAULT 0,
    shipping_amount DECIMAL(15,2) DEFAULT 0,
    total_amount DECIMAL(15,2) DEFAULT 0,
    notes TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, order_number)
);

-- Sales Order Items
CREATE TABLE sales_order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES sales_orders(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id),
    quantity DECIMAL(15,4) NOT NULL,
    unit_price DECIMAL(15,4) NOT NULL,
    discount_percent DECIMAL(5,2) DEFAULT 0,
    tax_rate DECIMAL(5,2) DEFAULT 0,
    line_total DECIMAL(15,2) GENERATED ALWAYS AS (
        quantity * unit_price * (1 - discount_percent/100) * (1 + tax_rate/100)
    ) STORED,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Invoices
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id),
    invoice_number VARCHAR(100) NOT NULL,
    order_id UUID REFERENCES sales_orders(id),
    customer_id UUID REFERENCES customers(id),
    status VARCHAR(20) DEFAULT 'draft', -- 'draft', 'sent', 'paid', 'overdue', 'cancelled'
    invoice_date DATE NOT NULL,
    due_date DATE NOT NULL,
    subtotal DECIMAL(15,2) DEFAULT 0,
    tax_amount DECIMAL(15,2) DEFAULT 0,
    discount_amount DECIMAL(15,2) DEFAULT 0,
    total_amount DECIMAL(15,2) DEFAULT 0,
    paid_amount DECIMAL(15,2) DEFAULT 0,
    balance_due DECIMAL(15,2) GENERATED ALWAYS AS (total_amount - paid_amount) STORED,
    notes TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, invoice_number)
);

-- Invoice Items
CREATE TABLE invoice_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id),
    description TEXT,
    quantity DECIMAL(15,4) NOT NULL,
    unit_price DECIMAL(15,4) NOT NULL,
    discount_percent DECIMAL(5,2) DEFAULT 0,
    tax_rate DECIMAL(5,2) DEFAULT 0,
    line_total DECIMAL(15,2) GENERATED ALWAYS AS (
        quantity * unit_price * (1 - discount_percent/100) * (1 + tax_rate/100)
    ) STORED,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```
-- ============================================================================
-- PAYMENT & ACCOUNTING
-- ============================================================================

-- Chart of Accounts
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id),
    account_code VARCHAR(20) NOT NULL,
    account_name VARCHAR(255) NOT NULL,
    account_type VARCHAR(50) NOT NULL, -- 'asset', 'liability', 'equity', 'revenue', 'expense'
    parent_id UUID REFERENCES accounts(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, account_code)
);

-- Journal Entries
CREATE TABLE journal_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id),
    entry_number VARCHAR(100) NOT NULL,
    entry_date DATE NOT NULL,
    reference_type VARCHAR(50), -- 'invoice', 'payment', 'adjustment'
    reference_id UUID,
    description TEXT,
    total_debit DECIMAL(15,2) DEFAULT 0,
    total_credit DECIMAL(15,2) DEFAULT 0,
    is_posted BOOLEAN DEFAULT false,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, entry_number)
);

-- Journal Entry Lines
CREATE TABLE journal_entry_lines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entry_id UUID NOT NULL REFERENCES journal_entries(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES accounts(id),
    description TEXT,
    debit_amount DECIMAL(15,2) DEFAULT 0,
    credit_amount DECIMAL(15,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Payments
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id),
    payment_number VARCHAR(100) NOT NULL,
    customer_id UUID REFERENCES customers(id),
    payment_method VARCHAR(50) NOT NULL, -- 'cash', 'card', 'bank_transfer', 'check'
    payment_date DATE NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    reference_number VARCHAR(100),
    notes TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, payment_number)
);

-- Payment Allocations (Link payments to invoices)
CREATE TABLE payment_allocations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_id UUID NOT NULL REFERENCES payments(id) ON DELETE CASCADE,
    invoice_id UUID NOT NULL REFERENCES invoices(id),
    allocated_amount DECIMAL(15,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- AUDIT & SYSTEM TABLES
-- ============================================================================

-- Audit Trail
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    user_id UUID REFERENCES users(id),
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    action VARCHAR(20) NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE'
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- System Settings
CREATE TABLE system_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    setting_key VARCHAR(100) NOT NULL,
    setting_value JSONB,
    description TEXT,
    is_system BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, setting_key)
);

-- API Tokens (For mobile apps and integrations)
CREATE TABLE api_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    token_name VARCHAR(100) NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    permissions JSONB DEFAULT '[]',
    expires_at TIMESTAMP WITH TIME ZONE,
    last_used_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### **Key Database Design Principles:**

1. **Multi-Tenancy:** Every table has `company_id` for data isolation
2. **Soft Deletes:** Important records use `deleted_at` instead of hard deletes
3. **Audit Trail:** Complete change tracking for compliance
4. **UUID Primary Keys:** Better for distributed systems and security
5. **JSONB Fields:** Flexible storage for settings and metadata
6. **Generated Columns:** Automatic calculations for derived values
7. **Proper Indexing:** Performance optimization for common queries

### **Essential Indexes:**

```sql
-- Performance Indexes
CREATE INDEX idx_users_company_email ON users(company_id, email);
CREATE INDEX idx_products_company_sku ON products(company_id, sku);
CREATE INDEX idx_invoices_company_status ON invoices(company_id, status);
CREATE INDEX idx_inventory_company_product ON inventory_items(company_id, product_id);
CREATE INDEX idx_stock_movements_product_date ON stock_movements(product_id, created_at);
CREATE INDEX idx_audit_logs_table_record ON audit_logs(table_name, record_id);

-- Multi-tenant Security Indexes
CREATE INDEX idx_companies_slug ON companies(slug);
CREATE INDEX idx_user_roles_user ON user_roles(user_id);
CREATE INDEX idx_api_tokens_hash ON api_tokens(token_hash);
```

---

## 4. API DESIGN & VERSIONING STRATEGY

### **RESTful API Design Principles:**

```
Base URL: https://api.bizpulse.com/v1/
Authentication: Bearer Token (JWT)
Content-Type: application/json
```

### **API Versioning Strategy:**

1. **URL Versioning:** `/v1/`, `/v2/` in the path
2. **Backward Compatibility:** Maintain older versions for 2 years
3. **Deprecation Policy:** 6-month notice before version retirement
4. **Feature Flags:** Gradual rollout of new features

### **Core API Endpoints:**

```yaml
# Authentication & User Management
POST   /v1/auth/login                    # User login
POST   /v1/auth/logout                   # User logout
POST   /v1/auth/refresh                  # Refresh JWT token
GET    /v1/auth/me                       # Current user info
POST   /v1/auth/forgot-password          # Password reset request
POST   /v1/auth/reset-password           # Password reset confirmation

# User Management
GET    /v1/users                         # List users (paginated)
POST   /v1/users                         # Create user
GET    /v1/users/{id}                    # Get user details
PUT    /v1/users/{id}                    # Update user
DELETE /v1/users/{id}                    # Soft delete user
POST   /v1/users/{id}/roles              # Assign roles
DELETE /v1/users/{id}/roles/{role_id}    # Remove role

# Product Management
GET    /v1/products                      # List products (with filters)
POST   /v1/products                      # Create product
GET    /v1/products/{id}                 # Get product details
PUT    /v1/products/{id}                 # Update product
DELETE /v1/products/{id}                 # Soft delete product
GET    /v1/products/{id}/inventory       # Get inventory levels
POST   /v1/products/{id}/stock-adjustment # Adjust stock levels

# Customer Management
GET    /v1/customers                     # List customers
POST   /v1/customers                     # Create customer
GET    /v1/customers/{id}                # Get customer details
PUT    /v1/customers/{id}                # Update customer
DELETE /v1/customers/{id}                # Soft delete customer
GET    /v1/customers/{id}/invoices       # Customer invoices
GET    /v1/customers/{id}/payments       # Customer payments

# Sales Order Management
GET    /v1/orders                        # List orders
POST   /v1/orders                        # Create order
GET    /v1/orders/{id}                   # Get order details
PUT    /v1/orders/{id}                   # Update order
DELETE /v1/orders/{id}                   # Cancel order
POST   /v1/orders/{id}/confirm           # Confirm order
POST   /v1/orders/{id}/ship              # Mark as shipped
POST   /v1/orders/{id}/deliver           # Mark as delivered

# Invoice Management
GET    /v1/invoices                      # List invoices
POST   /v1/invoices                      # Create invoice
GET    /v1/invoices/{id}                 # Get invoice details
PUT    /v1/invoices/{id}                 # Update invoice
DELETE /v1/invoices/{id}                 # Cancel invoice
POST   /v1/invoices/{id}/send            # Send invoice to customer
GET    /v1/invoices/{id}/pdf             # Download PDF
POST   /v1/invoices/{id}/payments        # Record payment

# Payment Management
GET    /v1/payments                      # List payments
POST   /v1/payments                      # Record payment
GET    /v1/payments/{id}                 # Get payment details
PUT    /v1/payments/{id}                 # Update payment
DELETE /v1/payments/{id}                 # Void payment

# Inventory Management
GET    /v1/inventory                     # Inventory summary
GET    /v1/inventory/low-stock           # Low stock items
GET    /v1/inventory/movements           # Stock movement history
POST   /v1/inventory/adjustments        # Stock adjustments
GET    /v1/inventory/valuation          # Inventory valuation

# Reporting
GET    /v1/reports/sales                 # Sales reports
GET    /v1/reports/inventory             # Inventory reports
GET    /v1/reports/financial            # Financial reports
GET    /v1/reports/customers            # Customer reports
POST   /v1/reports/custom               # Custom report generation

# Mobile-Specific Endpoints
GET    /v1/mobile/sync                   # Data synchronization
POST   /v1/mobile/sync                   # Upload offline changes
GET    /v1/mobile/dashboard              # Mobile dashboard data
POST   /v1/mobile/quick-sale             # Quick sale creation
GET    /v1/mobile/offline-data           # Offline data package
```
### **API Response Standards:**

```json
// Success Response
{
  "success": true,
  "data": {
    // Response data
  },
  "meta": {
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 100,
      "total_pages": 5
    }
  }
}

// Error Response
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "email": ["Email is required"],
      "password": ["Password must be at least 8 characters"]
    }
  },
  "meta": {
    "request_id": "req_123456789",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### **API Security Standards:**

1. **JWT Authentication:** Stateless token-based auth
2. **Rate Limiting:** 1000 requests/hour per user
3. **Input Validation:** Strict validation on all inputs
4. **SQL Injection Prevention:** Parameterized queries only
5. **CORS Configuration:** Restricted to allowed domains
6. **API Versioning:** Backward compatibility maintenance

---

## 5. AUTHENTICATION & ROLE-BASED ACCESS CONTROL

### **Multi-Level Authentication System:**

```
┌─────────────────────────────────────────────────────────────┐
│                    AUTHENTICATION LAYERS                    │
├─────────────────────────────────────────────────────────────┤
│  1. Company-Level Access (Multi-tenant isolation)          │
│  2. User Authentication (JWT tokens)                       │
│  3. Role-Based Permissions (RBAC)                          │
│  4. Resource-Level Authorization (Ownership checks)        │
│  5. API Rate Limiting (Abuse prevention)                   │
└─────────────────────────────────────────────────────────────┘
```

### **Role Hierarchy:**

```yaml
System Roles:
  super_admin:
    description: "System administrator with full access"
    permissions: ["*"]
    
  company_admin:
    description: "Company administrator"
    permissions:
      - "users:*"
      - "settings:*"
      - "reports:read"
      - "all_modules:*"
      
  manager:
    description: "Department manager"
    permissions:
      - "users:read"
      - "inventory:*"
      - "sales:*"
      - "reports:read"
      
  sales_person:
    description: "Sales representative"
    permissions:
      - "customers:*"
      - "orders:*"
      - "invoices:create,read,update"
      - "products:read"
      
  inventory_clerk:
    description: "Inventory management"
    permissions:
      - "products:*"
      - "inventory:*"
      - "stock_movements:*"
      
  accountant:
    description: "Financial management"
    permissions:
      - "invoices:*"
      - "payments:*"
      - "accounts:*"
      - "reports:financial"
      
  cashier:
    description: "Point of sale operations"
    permissions:
      - "pos:*"
      - "customers:read,create"
      - "products:read"
      - "quick_sale:*"
```

### **Permission System:**

```python
# Permission Format: "resource:action"
# Actions: create, read, update, delete, * (all)

PERMISSIONS = {
    # User Management
    "users:create": "Create new users",
    "users:read": "View user information",
    "users:update": "Update user details",
    "users:delete": "Delete users",
    
    # Product Management
    "products:create": "Create new products",
    "products:read": "View product information",
    "products:update": "Update product details",
    "products:delete": "Delete products",
    
    # Inventory Management
    "inventory:read": "View inventory levels",
    "inventory:adjust": "Adjust stock levels",
    "inventory:transfer": "Transfer stock between locations",
    
    # Sales Management
    "orders:create": "Create sales orders",
    "orders:read": "View sales orders",
    "orders:update": "Update sales orders",
    "orders:cancel": "Cancel sales orders",
    
    # Financial Management
    "invoices:create": "Create invoices",
    "invoices:read": "View invoices",
    "invoices:update": "Update invoices",
    "invoices:send": "Send invoices to customers",
    
    # Reporting
    "reports:sales": "View sales reports",
    "reports:inventory": "View inventory reports",
    "reports:financial": "View financial reports",
    
    # System Administration
    "settings:read": "View system settings",
    "settings:update": "Update system settings",
    "audit:read": "View audit logs"
}
```

### **JWT Token Structure:**

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "user_id": "uuid-here",
    "company_id": "uuid-here",
    "email": "user@company.com",
    "roles": ["manager", "sales_person"],
    "permissions": ["products:read", "orders:*"],
    "iat": 1640995200,
    "exp": 1641081600,
    "iss": "bizpulse-api",
    "aud": "bizpulse-app"
  }
}
```

### **Security Implementation:**

```python
# Authentication Decorator Example
def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verify JWT token
            token = get_token_from_request()
            if not token:
                return unauthorized_response()
            
            # Decode and validate token
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            except jwt.InvalidTokenError:
                return unauthorized_response()
            
            # Check permission
            user_permissions = payload.get('permissions', [])
            if not has_permission(user_permissions, permission):
                return forbidden_response()
            
            # Set current user context
            g.current_user = payload
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Usage in API endpoints
@app.route('/api/v1/products', methods=['POST'])
@require_permission('products:create')
def create_product():
    # Implementation here
    pass
```

---

## 6. OFFLINE-FIRST MOBILE SYNC STRATEGY

### **Sync Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│                    MOBILE SYNC STRATEGY                     │
├─────────────────────────────────────────────────────────────┤
│  1. Local SQLite Database (Complete offline capability)    │
│  2. Conflict Resolution Engine (Last-write-wins + manual)  │
│  3. Delta Sync (Only changed data)                         │
│  4. Background Sync (Automatic when online)                │
│  5. Offline Queue (Store actions for later sync)           │
└─────────────────────────────────────────────────────────────┘
```

### **Sync Data Model:**

```sql
-- Mobile Sync Tables
CREATE TABLE sync_metadata (
    id UUID PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    last_sync_at TIMESTAMP WITH TIME ZONE,
    sync_version INTEGER DEFAULT 1,
    is_deleted BOOLEAN DEFAULT false,
    conflict_resolution VARCHAR(20) DEFAULT 'server_wins',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(table_name, record_id)
);

CREATE TABLE sync_conflicts (
    id UUID PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    local_data JSONB NOT NULL,
    server_data JSONB NOT NULL,
    conflict_type VARCHAR(50) NOT NULL, -- 'update_conflict', 'delete_conflict'
    resolution_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'resolved', 'ignored'
    resolved_by UUID REFERENCES users(id),
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE offline_actions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    action_type VARCHAR(50) NOT NULL, -- 'create', 'update', 'delete'
    table_name VARCHAR(100) NOT NULL,
    record_id UUID,
    action_data JSONB NOT NULL,
    sync_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'synced', 'failed'
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### **Sync API Endpoints:**

```yaml
# Initial Data Download
GET /v1/mobile/sync/initial
  - Downloads complete dataset for offline use
  - Includes: products, customers, basic settings
  - Compressed JSON response
  - Pagination for large datasets

# Delta Sync (Incremental Updates)
GET /v1/mobile/sync/delta?since=timestamp
  - Returns only changed records since last sync
  - Includes deleted records (soft deletes)
  - Conflict detection and resolution

# Upload Local Changes
POST /v1/mobile/sync/upload
  - Uploads offline actions to server
  - Batch processing for efficiency
  - Conflict detection and resolution
  - Returns sync results and conflicts

# Conflict Resolution
GET /v1/mobile/sync/conflicts
  - Lists unresolved conflicts
POST /v1/mobile/sync/conflicts/{id}/resolve
  - Resolves specific conflict
  - Options: accept_local, accept_server, merge
```

### **Conflict Resolution Strategy:**

```python
class ConflictResolver:
    def resolve_conflict(self, conflict_type, local_data, server_data):
        """
        Conflict Resolution Rules:
        1. Timestamp-based (last write wins)
        2. Field-level merging for non-conflicting fields
        3. Manual resolution for critical conflicts
        4. Business rule-based resolution
        """
        
        if conflict_type == 'update_conflict':
            return self.resolve_update_conflict(local_data, server_data)
        elif conflict_type == 'delete_conflict':
            return self.resolve_delete_conflict(local_data, server_data)
        
    def resolve_update_conflict(self, local_data, server_data):
        # Compare timestamps
        local_updated = local_data.get('updated_at')
        server_updated = server_data.get('updated_at')
        
        if local_updated > server_updated:
            return 'accept_local'
        elif server_updated > local_updated:
            return 'accept_server'
        else:
            # Same timestamp - merge non-conflicting fields
            return self.merge_fields(local_data, server_data)
```

### **Mobile Offline Capabilities:**

1. **Complete POS Operations:** Sales, payments, customer creation
2. **Inventory Checks:** View stock levels, low stock alerts
3. **Customer Management:** View, create, update customer information
4. **Report Generation:** Basic sales and inventory reports
5. **Data Entry:** All forms work offline with local validation
---

## 7. ERROR HANDLING & LOGGING STRATEGY

### **Error Handling Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│                    ERROR HANDLING LAYERS                    │
├─────────────────────────────────────────────────────────────┤
│  1. Input Validation (Request level)                       │ystems.class ERP sng world-ldibuin for tiosolid founda provides a nts andnvironmeroduction eed** in pest*battle-thas been *itecture 

This archededes when necroservic to mi**ration pathdual mig**
5. **GraecsPI sptation and Acumeniled do **Deta
4.nitoring**g and modlinanerror ht **Robuslevels
3. y** at all trateging sestrehensive t **Comprs
2.layeoss all  acr concerns**n ofaratioar sep
1. **Cle Factors:** Successey

**Koductivity. prpery and develo qualit codeningaintaile mically whi grow organ system tothey, allowing calabiliticity and stween simpllance** beba**perfect vides the roach pronolith app mo
The modular
 pers loor new deve** fardinges easy onbo✅ **Enablmpliance  
 co** forit trails audrehensiveompvides c**Pron  
✅ tiotenant isola multi-y** withcuritseres data su*En
✅ *  st sync robu withobile apps**first ms offline-*Support  
✅ *I versioningAPough ty** thriliibpatcomckward ins banta)  
✅ **Mairs use (0 to 1M+se** to enterpristartupom *Scales fr

✅ *t:em thasystle ERP a large-scare** for itectuchready artion-duc**pro a t providesueprinN

This bl# CONCLUSIO

#
---
ationumentng and docensive testi Compreh ]ing
- [ and cachtionza optimincePerforma] - [ ystems
party ss for third- APIration
- [ ] Integport suparehouse] Multi-w[ ytics
- ing and anald report ] Advance*
- [)* 10-12ures (Monthsnced FeatAdva4: **Phase 
### ations
ush notific ] Add pents
- [onomped UI cptimizle-oate mobi Cre ]
- [inengsolution eict reild confl- [ ] Buem
st sync systline-fir offlement ] Impts
- [PI endpoinp mobile A- [ ] Develo**
ths 7-9)c (Monyne & Sobilase 3: M**Ph## res

#eatucurity fand segging it lo Add aud ]- [ system
portingate basic re ] Cre [payments
-and generation t invoice men ] Implessing
- [ proceorder sales ] Buildtem
- [ nt sysageme mannventoryplete i
- [ ] Com-6)**hs 4ures (MontatFe 2: Core ase
### **Phtation
nd documen a versioningent APImplem I- [ ]ies
ntit core eor fIsD APbasic CRU Create stem
- [ ]on syhorizatiand autentication uthld auima
- [ ] Be schee databasorement c [ ] Impland CI/CD
-ment onent envirlopmup deve [ ] Set )**
-hs 1-3n (Montdatioounhase 1: F*P### *P

ROADMAMENTATION 

## IMPLE

---
```ActionsGitHub itLab CI or  - CI/CD: Grometheus
  P: Jaeger +ty Observabili: Vault
  -urationonfig - Csul
 covery: Conervice Dises
  - SKubernetation: r Orchestr Containe  -tive:
e 3 Cloud Naas

Phssadorong or Ambaway: KAPI Gate
  - esh: IstioService M  -  Kafka
cheus: Apaage B  - Messfor logs)
 + MongoDB (QLreSbase: Postg - Data
 etesrn Kuber ++ DockestAPI Fa: 
  - Backendervices:se 2 Microsafana

Phametheus + Gr ProMonitoring:Q
  - bitMQueue: Rabluster
  - e: Redis Cachlicas
  - Ch read repeSQL witse: Postgr
  - Databac support)astAPI (asynckend: Fs:
  - Bavement Impro
Phase 1/JS
ontend: HTML
  - Frueue: Celery - Q
 e: RedisL
  - CachPostgreSQbase: 
  - Datathon/Flask Backend: Pyck:
  -rrent Sta```yaml
Cuath:**

tion PEvoluchnology ### **Te.5%
```

e: 99 rat successMobile sync.9%
  - y: 99abilitvail
  - API ality: 99.95%ilabiase ava Datab
  -ear)owntime/y d6 hours: 99.9% (8.7ystem uptime:
  - Sy Targetsbilit
Availa0 MB/s
oads: 10 upl- Filet
  encurrcon: 1,000 ionsnnectase co - Datab000
 t users: 50,rren  - Concusts/second
0,000 requeuests: 1
  - API reqt Targets:hpuThrougonds

 sec 3p: < app startu Mobilends
  -: < 2 secoad time- Page lotile)
  h percen95t< 100ms (es: abase queriDat
  - percentile)(95th ts: < 200ms oinPI endps:
  - A Time Targetl
Response**

```yams:getance Tarerform*P

### *data
```r public responses fo
  - API umentsd docages anuct imod)
  - PrJSS, ages, CSc assets (im- Statiche:
   Cavel 3 - CDNevels)

Le(inventory lata -time dg
  - Realhinponse cacAPI res  - ults
se query resabae:
  - Datchis Cavel 2 - Red
Leings
ration settonfigu - Cns
 nd permissions aio - User sesssed data
 tly accesueneqing for frch-memory ca
  - Ine:on Cachatipplic- Al 1 `yaml
Leve``
trategy:**
**Caching S
### 
```
──────┘──────────────────────────────────────────────────────)      │
└─abasespecific dat(Service-ssistence  Per 5. Polyglot       │
│      )        + usersusters (200K Clegioni-R
│  4. Mult          │s)         00K user50K-2arding (ontal Sh. Horiz │
│  3         rs)     use0K-50K cation (1RepliSlave er-2. Mast  │
│                        ers)L (0-10K usostgreSQle P
│  1. Sing───────┤──────────────────────────────────────────────────────       │
├         G PATH    SE SCALINATABA        D            ──────┐
│─────────────────────────────────────────────────┌──────
```
egy:**
ng StratcaliDatabase S# **
##``
ice
`s Serv  - Analytice
ervicuration S Config -rvice
 Se- Audit 
  age Servicetor
  - File Support):(S Services Priority 3vice

Seration - NotificService
  rting 
  - Repoervicenagement Sstomer Ma  - Cuice
erv Sntanagemeentory M InvLogic):
  -ess (Busins icerity 2 ServPrioe

vicer- Payment Svice
  ocessing Ser PrOrderervice
  -  SlogProduct Cata  - vice
tion Seruthentica
  - A:h Traffic)rvices (Hig1 Seriority 
```yaml
P:**
ion Planices Extract*Microserv```

### * balancing
 Global load
└──tingcompuge ── Edstrategy
├ation ic─ Data replibution
├─c distr Geographi├──K+ users)
00-Region (2ultiPhase 4: M

ectureriven archit└── Event-dsh (Istio)
ce me
├── Serviementationateway impl API Gs
├──leic modutraffact high-
├── Extrusers)n (50K-200K Migratioices 3: Microservhase 

Pion optimizat
└── Queryngoliection po├── Connting
plit sriteRead/wtup
├── ase seabe datslav── Master- users)
├s (10K-50K ReplicaRead 2: 
Phasencer setup
la ba── Loadassets
└ic atN for st CD
├──dis)ion (Relementat layer imp
├── Cachingindexingn and atiomizoptie ├── Databas)
0-10K userstimization (olith Op 1: Mon
```
Phaserategy:**
Stcaling ntal S **Horizo

###BILITY PLANSCALA. FUTURE ## 8

---

```]
urity_team"on: ["sec  notificatirning"
  y: "wa
    severitminutes"over 5 lures > 50  "auth_faiion:
    conditlures:ation_faiauthentic
    
  "slack"], "sms", ["email"ion: ficat    noticritical"
: "erity sev"
   ute1 min > 10 over errorsbase_"datandition:   coailure:
  nnection_fdatabase_co
    
  "]ack: ["slication   notif
 "warning": veritys"
    seminutems over 10  > 2000onse_timerespon: "avg_ditime:
    con_tiw_response  
  slock"]
   "sla["email",tion: tifica
    no""criticalseverity: utes"
     over 5 min_rate > 5%: "errorcondition   r_rate:
 rro high_eles:
  RuAlertl
`yaming:**

``& Alerting Monitor
### **e
or compliancs fa changes:** Datogdit L6. **Ausponses
d re analls API c** Externalon Logs:ratiIntege
5. **memory usaggh ries, hiw que* Sloogs:*nce Lmafor
4. **Per failuresthorizationn, aunticatio* Authe Logs:*rityecunges
3. **Sentory chaents, invym* Sales, paent Logs:*ess Ev*Busin. *h timing
2ponses witesests/r HTTP requ** All*API Logs:

1. *ories:**og Categ **L
```

###og_data))umps(lror(json.derself.logger. }
        ()
       at_exck.form": tracebacack_trace"st  
          xt or {},: conteontext"     "c    
   (error),sage": stresror_m        "er    ame__,
).__n type(error":ype_t   "error  ",
       ion_errorcat": "appli     "type  ",
      "ERROR"level":           ),
 format(isocnow().ime.ut datet":timestamp        "ta = {
    og_da    le):
    xt=Nonor, conte, errerror(selfdef log_   
    
 s(log_data))ump.do(jsonlogger.inf    self.    }
 
       ta": da"data    
        event_type,e": vent_typ"e     
       ent",business_evtype": "  "
          INFO",vel": " "le         ,
  soformat().icnow()ime.ut: datetmestamp""ti      
      og_data = {  l
      ype, data):_t(self, evententusiness_evlog_bdef    
    
 ta))das(log_son.dumpgger.info(jelf.lo   s   }
        t')
  'User-Agenrs.get(st.heade": requeser_agent   "u       e_addr,
  .remotequestdress": rip_ad"   
          None),',idpany_quest, 'comre": getattr(ompany_id    "c
        e),er_id', Nont, 'usestattr(requ: ge"r_iduse     "
       uration, dms":ion_     "durat       ,
tus_codesponse.sta: re"tus_code"sta            t.path,
uespath": req         "ethod,
   uest.mreqhod":   "met     ,
     quest": "api_re   "type"       O",
  NF"I "level":         (),
   ().isoformatetime.utcnow": dattampes "tim          {
 log_data = 
        uration):sponse, drerequest, st(self, og_api_reque
    def l  e)
      er(namg.getLogg= loggin.logger elf       sname):
 _(self, ef __init_:
    dLoggeredurss Structme

cla datetimportm datetime i
fromport jsont logging
i
impor```python
tegy:**
ng StraLoggi
### **`
  }
}
``"
ST: "PO  "method"
  products",1/i/v": "/ap"path  
  :00Z",1T12:00-0024-01"2": estamp
    "tim456",eq_abc123def "r":est_idqu {
    "remeta": },
  "gain"
 d try alds an fiee input check th "Pleaseggestion":su},
    "
    "]n 0 tha be greaterice must": ["Prprice    "alid"],
  rmat is inv foilEmamail": ["     "e {
 ails":   "detded",
 ta provilid input danvasage": "I"mes
    ERROR",DATION_de": "VALI"co{
    "error": : false,
  uccess"
{
  "sonjs*

```esponse:*Error Ructured 
### **Str"
```
SSEDY_PROCELREAD"PAYMENT_A= _PROCESSED DYENT_ALREA
    PAYM"Y_SHIPPEDADR_ALRE"ORDEPPED = ALREADY_SHIORDER_ICE"
    ID_PR "INVAL_PRICE =INVALID    KU"
E_S "DUPLICATATE_SKU =  DUPLICCEEDED"
  IT_EXT_LIMD = "CREDIDEEE_EXCMITEDIT_LIK"
    CRT_STOCUFFICIEN"INS_STOCK = IENTUFFICINSs:
    ssErrorine Bus3

class   # 50ABLE" UNAVAILSERVICE_ILABLE = "ERVICE_UNAVA S 502
         #OR"AL_API_ERRXTERNR = "EERROERNAL_API_  EXT# 500
               ASE_ERROR" "DATAB_ERROR =  DATABASE0
      # 50           OR"ERRNAL_= "INTER_ERROR INTERNALxx)
    ors (5er Err Serv # 
   # 429
           R"  _ERRO"RATE_LIMITROR = _ERLIMIT   RATE_409
          # OR"     _ERRICT"CONFLRROR = ICT_E    CONFL4
# 40    OR"        ND_ERR_FOU = "NOTOR_ERRNDFOU   NOT_ 403
 "     #_ERRORORIZATIONAUTHR = "RROIZATION_EOR AUTH  # 401
   " RRORION_EENTICAT "AUTHTION_ERROR =  AUTHENTICA   # 400
  R"        TION_ERRO "VALIDAION_ERROR =  VALIDATrs (4xx)
  roient Er:
    # Cls ErrorTypesthon
clas

```pycation:** Classifi
### **Error```
─────┘
────────────────────────────────────────────────────└────    │
             level)(IntegrationI Errors ternal AP Ex    │
│  5.        l)       ucture leverastrrors (Infm Eryste  │
│  4. S                  el) tory lev (Reposise Errors. Databa  │
│  3                 level)(Servicec Errors ness Logiusi
│  2. B