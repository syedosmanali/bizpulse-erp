# Complete ERP SaaS Software Development Prompt for Replit AI

Create a comprehensive ERP (Enterprise Resource Planning) SaaS software called "BizPulse ERP" with both desktop and mobile versions. This should be a complete business management solution with the following specifications:

## Core Technology Stack:
- **Backend**: Python Flask with SQLite database
- **Frontend**: HTML, CSS, JavaScript (responsive design)
- **Mobile**: Progressive Web App (PWA) optimized for mobile devices
- **Authentication**: Multi-level user authentication system
- **Styling**: Modern gradient-based UI with professional color scheme (#732C3F primary, #F7E8EC secondary)

## Database Schema & Tables:
Create SQLite database with these tables:
1. **products** - id, code, name, category, price, cost, stock, min_stock, unit, business_type, is_active, created_at
2. **customers** - id, name, phone, email, address, credit_limit, current_balance, total_purchases, customer_type, is_active, created_at
3. **bills** - id, bill_number, customer_id, business_type, subtotal, tax_amount, discount_amount, total_amount, status, created_at
4. **bill_items** - id, bill_id, product_id, product_name, quantity, unit_price, total_price, tax_rate
5. **payments** - id, bill_id, method, amount, reference, processed_at
6. **sales** - id, bill_id, bill_number, customer_id, customer_name, product_id, product_name, category, quantity, unit_price, total_price, tax_amount, discount_amount, payment_method, sale_date, sale_time, created_at
7. **users** - id, email, password_hash, business_name, business_address, business_type, gst_number, phone, is_active, created_at
8. **clients** - id, company_name, contact_email, contact_name, phone_number, whatsapp_number, business_address, business_type, gst_number, username, password_hash, is_active, last_login, created_at, updated_at
9. **client_users** - id, client_id, full_name, email, username, password_hash, password_plain, role, department, phone_number, is_active, permissions, last_login, created_by, created_at, updated_at
10. **staff** - id, business_owner_id, name, email, phone, role, username, password_hash, is_active, last_login, created_at, updated_at
11. **hotel_guests** - id, name, phone, email, address, id_proof, room_number, room_type, check_in_date, check_out_date, guest_count, total_bill, status, created_at
12. **hotel_services** - id, name, category, rate, description, tax_rate, is_active, created_at
13. **companies** - id, business_name, phone_number, whatsapp_number, email, address, send_daily_report, report_time, timezone, is_active, created_at, updated_at
14. **invoices** - id, company_id, invoice_number, customer_id, invoice_date, due_date, subtotal, tax_amount, discount_amount, total_amount, total_cost, profit_amount, payment_status, notes, created_at, updated_at
15. **whatsapp_reports_log** - id, company_id, report_date, report_type, whatsapp_number, pdf_filename, media_id, message_id, status, total_sales, total_profit, total_invoices, error_message, sent_at, created_at

## CMS (Content Management System) Tables:
16. **cms_site_settings** - id, site_name, logo_url, favicon_url, primary_color, secondary_color, contact_email, contact_phone, address, updated_at
17. **cms_hero_section** - id, title, subtitle, button_text, button_link, background_image_url, updated_at
18. **cms_features** - id, title, description, icon_image_url, display_order, is_active, created_at
19. **cms_pricing_plans** - id, name, price_per_month, description, features, is_popular, display_order, is_active, created_at
20. **cms_testimonials** - id, name, role, company, message, avatar_image_url, rating, display_order, is_active, created_at
21. **cms_faqs** - id, question, answer, category, display_order, is_active, created_at
22. **cms_gallery** - id, title, description, image_url, category, display_order, is_active, created_at
23. **cms_admin_users** - id, username, password_hash, email, full_name, is_active, last_login, created_at, updated_at
24. **cms_website_content** - id, page_name, content_html, edited_by, is_active, created_at, updated_at

## Core Modules & Features:

### 1. Dashboard Module
- **Desktop Dashboard**: Modern cards layout with statistics
- **Mobile Dashboard**: Touch-optimized cards with swipe gestures
- **Real-time Statistics**: Today's sales, weekly sales, monthly sales, total customers, total products, low stock alerts
- **Quick Actions**: Add Product, Add Customer, Create Bill, View Reports
- **Recent Activity**: Last 10 transactions with customer names and amounts
- **Charts**: Sales trends, category-wise breakdown, hourly sales data
- **Widgets**: Revenue cards, transaction counters, inventory status, profit margins

### 2. Products Management Module
- **Product List**: Searchable table with filters (category, stock status, business type)
- **Add Product Form**: Code, Name, Category dropdown, Price, Cost, Stock, Min Stock, Unit, Business Type (retail/hotel/both)
- **Edit Product**: Inline editing with validation
- **Stock Management**: Update stock levels, set minimum stock alerts
- **Categories**: Dynamic category management
- **Barcode Support**: Generate and scan product barcodes
- **Bulk Import**: CSV import functionality
- **Low Stock Alerts**: Automatic notifications when stock is below minimum
- **Product Performance**: Sales analytics per product

### 3. Customers Management Module
- **Customer List**: Searchable table with contact details
- **Add Customer Form**: Name, Phone, Email, Address, Credit Limit
- **Customer Profile**: Purchase history, outstanding balance, loyalty points
- **Customer Analytics**: Top customers, purchase patterns, lifetime value
- **Credit Management**: Track credit limits and outstanding amounts
- **Customer Categories**: Regular, VIP, Wholesale customers
- **Communication**: SMS/Email integration for notifications

### 4. Billing & Sales Module
- **Point of Sale (POS)**: Touch-friendly interface for quick billing
- **Product Search**: Real-time search with barcode scanning
- **Cart Management**: Add/remove items, quantity adjustment, discounts
- **Customer Selection**: Quick customer lookup or walk-in customer option
- **Payment Methods**: Cash, Card, UPI, Credit options
- **Tax Calculation**: Automatic GST/tax calculation
- **Discount System**: Item-wise or bill-wise discounts
- **Bill Preview**: Print preview before finalizing
- **Receipt Generation**: Thermal printer support
- **Return/Exchange**: Handle returns and exchanges
- **Split Billing**: Multiple payment methods for single bill

### 5. Inventory Management Module
- **Stock Overview**: Current stock levels, valuation
- **Stock Movements**: Track all stock in/out transactions
- **Purchase Orders**: Create and manage supplier orders
- **Stock Adjustments**: Manual stock corrections
- **Reorder Points**: Automatic reorder suggestions
- **Supplier Management**: Vendor details and purchase history
- **Stock Reports**: Aging analysis, fast/slow moving items
- **Physical Stock**: Stock counting and reconciliation

### 6. Reports & Analytics Module
- **Sales Reports**: Daily, weekly, monthly, custom date ranges
- **Product Reports**: Best sellers, slow movers, category analysis
- **Customer Reports**: Top customers, purchase patterns
- **Financial Reports**: Profit/loss, revenue trends, tax reports
- **Inventory Reports**: Stock valuation, movement analysis
- **Export Options**: PDF, Excel, CSV formats
- **Visual Charts**: Bar charts, pie charts, line graphs using Chart.js
- **Date Filters**: Quick filters (Today, Yesterday, This Week, This Month, Custom)
- **Comparison Reports**: Period-over-period analysis

### 7. User Management & Authentication
- **Multi-level Authentication**: Super Admin, Business Owner, Staff, Employees
- **Role-based Permissions**: Granular access control
- **User Registration**: Business owner signup with company details
- **Staff Management**: Add employees with specific roles
- **Session Management**: Secure login/logout with session isolation
- **Password Management**: Reset, change password functionality
- **User Activity Logs**: Track user actions and login history

### 8. Hotel Management Module (Optional)
- **Guest Registration**: Check-in/check-out management
- **Room Management**: Room types, availability, pricing
- **Service Billing**: Additional services and charges
- **Guest History**: Previous stays and preferences
- **Occupancy Reports**: Room utilization analytics

### 9. WhatsApp Integration Module
- **Daily Reports**: Automated WhatsApp reports
- **Sales Notifications**: Real-time sales updates
- **Low Stock Alerts**: WhatsApp notifications for inventory
- **Customer Communication**: Order confirmations, payment reminders
- **Report Scheduling**: Customizable report timing

### 10. CMS & Website Builder
- **Website Management**: Edit company website content
- **Content Editor**: WYSIWYG editor for pages
- **Image Gallery**: Upload and manage images
- **SEO Settings**: Meta tags, descriptions
- **Contact Forms**: Lead generation forms
- **Testimonials**: Customer reviews management

## Mobile App Specifications:

### Mobile Interface Features:
- **Responsive Design**: Works on all screen sizes
- **Touch Optimized**: Large buttons, swipe gestures
- **Offline Capability**: PWA with offline functionality
- **Fast Loading**: Optimized for mobile networks
- **Native Feel**: App-like experience in browser

### Mobile-Specific Modules:
1. **Mobile Dashboard**: Card-based layout with key metrics
2. **Quick Billing**: Simplified POS for mobile devices
3. **Product Scanner**: Camera-based barcode scanning
4. **Customer Lookup**: Quick customer search and selection
5. **Sales Entry**: Touch-friendly sales form
6. **Reports View**: Mobile-optimized charts and tables
7. **Inventory Check**: Quick stock level viewing
8. **Notifications**: Push notifications for important alerts

### Mobile Navigation:
- **Hamburger Menu**: Collapsible side navigation
- **Bottom Navigation**: Quick access to main modules
- **Search Bar**: Global search functionality
- **Back Buttons**: Proper navigation flow
- **Breadcrumbs**: Location awareness

## UI/UX Design Requirements:

### Color Scheme:
- **Primary Color**: #732C3F (Deep burgundy)
- **Secondary Color**: #F7E8EC (Light pink)
- **Accent Colors**: #4CAF50 (Success), #2196F3 (Info), #FF9800 (Warning), #f44336 (Error)
- **Background**: Linear gradients, white cards with shadows

### Design Elements:
- **Modern Cards**: Rounded corners, subtle shadows
- **Icons**: Font Awesome or similar icon library
- **Typography**: Clean, readable fonts (Inter, Roboto)
- **Buttons**: Gradient backgrounds, hover effects
- **Forms**: Floating labels, validation feedback
- **Tables**: Striped rows, sortable columns, pagination
- **Charts**: Interactive charts with tooltips
- **Loading States**: Spinners and skeleton screens

### Responsive Breakpoints:
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

## API Endpoints Structure:
Create RESTful APIs for all operations:
- **Authentication**: /api/auth/login, /api/auth/logout, /api/auth/register
- **Products**: /api/products (GET, POST, PUT, DELETE)
- **Customers**: /api/customers (GET, POST, PUT, DELETE)
- **Bills**: /api/bills (GET, POST, PUT, DELETE)
- **Reports**: /api/reports/sales, /api/reports/products, /api/reports/customers
- **Dashboard**: /api/dashboard/stats, /api/dashboard/charts
- **Inventory**: /api/inventory/stock, /api/inventory/movements

## Sample Data:
Include sample data for testing:
- 10+ sample products across different categories
- 5+ sample customers with contact details
- Sample bills and transactions
- Demo user accounts with different roles

## Security Features:
- **Password Hashing**: SHA-256 or bcrypt
- **Session Management**: Secure session handling
- **Input Validation**: Server-side validation for all inputs
- **SQL Injection Protection**: Parameterized queries
- **XSS Protection**: Input sanitization
- **CSRF Protection**: Token-based protection

## Additional Features:
- **Multi-language Support**: English and Hindi
- **Print Support**: Receipt and report printing
- **Backup/Restore**: Database backup functionality
- **Import/Export**: CSV/Excel data exchange
- **Audit Trail**: Track all data changes
- **Email Integration**: Automated email notifications
- **SMS Integration**: Customer notifications
- **Cloud Sync**: Optional cloud backup

## File Structure:
```
/
├── app.py (Main Flask application)
├── requirements.txt (Python dependencies)
├── billing.db (SQLite database)
├── static/
│   ├── css/ (Stylesheets)
│   ├── js/ (JavaScript files)
│   ├── images/ (Images and icons)
│   └── uploads/ (User uploaded files)
├── templates/
│   ├── index.html (Main website)
│   ├── login.html (Login page)
│   ├── dashboard.html (Desktop dashboard)
│   ├── mobile_simple_working.html (Mobile app)
│   ├── products.html (Product management)
│   ├── customers.html (Customer management)
│   ├── billing.html (POS interface)
│   ├── reports.html (Reports dashboard)
│   └── ... (other templates)
└── translations/ (Language files)
```

## Deployment Requirements:
- **Development Server**: Flask development server
- **Production Ready**: WSGI compatible
- **Environment Variables**: Configuration management
- **Error Handling**: Comprehensive error pages
- **Logging**: Application and error logging

Create this as a complete, production-ready ERP system that can handle real business operations. The system should be intuitive, fast, and reliable with proper error handling and user feedback throughout the application.

Make sure to include all the mentioned modules, features, and functionality. The mobile version should be fully functional with the same capabilities as the desktop version but optimized for touch interfaces and smaller screens.

Include proper documentation and comments in the code for easy maintenance and future enhancements.