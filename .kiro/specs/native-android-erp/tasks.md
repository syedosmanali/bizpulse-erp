# Implementation Plan: Native Android ERP Application

## Overview

This implementation plan breaks down the native Android ERP application into discrete, manageable tasks. Each task builds on previous work and includes specific requirements references. The plan follows a bottom-up approach: core infrastructure first, then data layer, business logic, UI, and finally integration.

## Tasks

- [ ] 1. Project Setup and Core Infrastructure
  - Create new Android Studio project with Kotlin support
  - Configure Gradle with all required dependencies (Hilt, Room, Retrofit, etc.)
  - Set up package structure (data, domain, presentation, di, utils)
  - Configure ProGuard rules for release builds
  - Set up BuildConfig for API URLs
  - _Requirements: 10.1, 10.8_

- [ ] 2. Dependency Injection Setup
  - [ ] 2.1 Create Hilt Application class
    - Annotate with @HiltAndroidApp
    - Initialize application-level components
    - _Requirements: 10.8_
  
  - [ ] 2.2 Create NetworkModule for Retrofit and OkHttp
    - Provide OkHttpClient with logging interceptor
    - Provide Retrofit instance with base URL
    - Provide ApiService interface
    - Add authorization header interceptor
    - _Requirements: 1.1, 1.5_
  
  - [ ] 2.3 Create DatabaseModule for Room
    - Provide AppDatabase instance
    - Provide all DAO instances
    - Configure database builder with fallback strategies
    - _Requirements: 6.1, 6.5_

- [ ] 3. Data Models and Database Schema
  - [ ] 3.1 Create core entity classes
    - User entity with Room annotations
    - Product entity with Room annotations
    - Invoice and InvoiceItem entities
    - Customer entity with Room annotations
    - StockMovement entity with Room annotations
    - Add SyncStatus enum
    - _Requirements: 3.1, 4.1, 5.1, 7.1_
  
  - [ ] 3.2 Create type converters for Room
    - Converter for List<InvoiceItem>
    - Converter for enums (PaymentMethod, InvoiceStatus, SyncStatus)
    - Converter for Date/Long timestamps
    - _Requirements: 4.1_
  
  - [ ] 3.3 Create Room Database class
    - Define AppDatabase with all entities
    - Set version and export schema
    - Add TypeConverters annotation
    - _Requirements: 6.5_
  
  - [ ] 3.4 Create DAO interfaces
    - ProductDao with CRUD operations and search
    - InvoiceDao with CRUD and date filtering
    - CustomerDao with CRUD and search
    - StockDao for stock movements
    - UserDao for user data
    - Add Flow return types for reactive queries
    - _Requirements: 3.1, 4.1, 5.1, 7.1_

- [ ] 3.5 Write property test for database operations
  - **Property 2: Offline Data Consistency**
  - **Validates: Requirements 6.1, 6.5**

- [ ] 4. Network Layer and API Service
  - [ ] 4.1 Create API request/response models
    - LoginRequest and LoginResponse
    - API response wrappers
    - Error response models
    - _Requirements: 1.1_
  
  - [ ] 4.2 Create ApiService interface
    - Auth endpoints (login, logout, me)
    - Product endpoints (CRUD)
    - Invoice endpoints (CRUD, PDF)
    - Customer endpoints (CRUD)
    - Dashboard metrics endpoint
    - Stock endpoints
    - Reports endpoints
    - _Requirements: 1.1, 3.1, 4.1, 5.1, 7.1, 8.1_
  
  - [ ] 4.3 Create Result wrapper class
    - Sealed class with Success, Error, Loading states
    - Extension function for safe API calls
    - _Requirements: 1.3, 6.1_

- [ ] 5. Authentication Module
  - [ ] 5.1 Create TokenManager class
    - Use EncryptedSharedPreferences for token storage
    - Methods: saveToken, getToken, clearToken
    - _Requirements: 1.5_
  
  - [ ] 5.2 Create AuthRepository
    - Implement login with API call
    - Implement logout with token clearing
    - Implement token validation
    - Store user data in Room after login
    - _Requirements: 1.1, 1.4, 1.6_
  
  - [ ] 5.3 Create AuthViewModel
    - LoginState sealed class
    - login() function with validation
    - logout() function
    - checkAuthStatus() function
    - Expose StateFlow for UI observation
    - _Requirements: 1.1, 1.2, 1.3, 1.6_
  
  - [ ] 5.4 Create LoginActivity with XML layout
    - Material Design login form
    - Email and password TextInputLayouts
    - Login button with loading state
    - Remember me checkbox
    - Error message display with Snackbar
    - ViewBinding setup
    - _Requirements: 1.1, 1.2, 1.3_
  
  - [ ] 5.5 Implement login flow in LoginActivity
    - Observe LoginState from ViewModel
    - Handle success navigation to Dashboard
    - Handle error display
    - Show/hide loading indicator
    - _Requirements: 1.1, 1.2, 1.3_

- [ ] 5.6 Write property test for authentication
  - **Property 1: Authentication Token Persistence**
  - **Validates: Requirements 1.1, 1.5**

- [ ] 5.7 Write property test for session persistence
  - **Property 9: Session Persistence**
  - **Validates: Requirements 1.4**

- [ ] 6. Dashboard Module
  - [ ] 6.1 Create DashboardMetrics data class
    - Fields for sales, invoices, stock counts
    - Top products list
    - _Requirements: 2.1_
  
  - [ ] 6.2 Create DashboardRepository
    - Fetch metrics from API
    - Cache metrics in Room
    - Return Flow for reactive updates
    - _Requirements: 2.1, 2.5_
  
  - [ ] 6.3 Create DashboardViewModel
    - Load metrics on init
    - Refresh metrics function
    - Expose StateFlow for metrics
    - Handle loading and error states
    - _Requirements: 2.1, 2.2, 2.3_
  
  - [ ] 6.4 Create DashboardActivity with bottom navigation
    - Bottom navigation with 4 tabs
    - Fragment container
    - Toolbar with sync status
    - ViewBinding setup
    - _Requirements: 2.1, 10.2_
  
  - [ ] 6.5 Create DashboardFragment with XML layout
    - Material Cards for metrics display
    - RecyclerView for quick actions
    - SwipeRefreshLayout for pull-to-refresh
    - Chart view for sales graph
    - _Requirements: 2.1, 2.3, 2.4_
  
  - [ ] 6.6 Implement dashboard UI logic
    - Observe metrics from ViewModel
    - Update UI on data changes
    - Handle pull-to-refresh
    - Navigate to quick actions
    - _Requirements: 2.1, 2.2, 2.3, 2.6_

- [ ] 6.7 Write unit tests for DashboardViewModel
  - Test metrics loading
  - Test refresh functionality
  - Test error handling
  - _Requirements: 2.1, 2.2_

- [ ] 7. Product Management Module
  - [ ] 7.1 Create ProductRepository
    - Implement offline-first pattern
    - Fetch products from API and cache in Room
    - CRUD operations with sync status tracking
    - Search products locally
    - _Requirements: 3.1, 3.6, 3.8_
  
  - [ ] 7.2 Create ProductViewModel
    - Load products with Flow
    - Search functionality with debounce
    - Add/update/delete product functions
    - Handle sync status
    - _Requirements: 3.1, 3.2, 3.5, 3.6_
  
  - [ ] 7.3 Create ProductsFragment with XML layout
    - RecyclerView with ProductAdapter
    - Search bar in toolbar
    - FAB for adding products
    - Empty state view
    - _Requirements: 3.1, 3.6_
  
  - [ ] 7.4 Create ProductAdapter for RecyclerView
    - ViewHolder with product item layout
    - Click listener for product details
    - Swipe actions for edit/delete
    - DiffUtil for efficient updates
    - _Requirements: 3.1, 10.7_
  
  - [ ] 7.5 Create AddEditProductActivity with XML layout
    - Form fields for product details
    - Image picker for product photo
    - Barcode scanner button
    - Save button with validation
    - _Requirements: 3.2, 3.3, 3.7_
  
  - [ ] 7.6 Implement barcode scanning
    - Integrate ML Kit Barcode Scanning
    - Camera preview with CameraX
    - Barcode detection callback
    - Auto-fill product form on scan
    - _Requirements: 3.7, 10.5_
  
  - [ ] 7.7 Implement product form validation and save
    - Validate required fields
    - Call ViewModel to save product
    - Handle success/error
    - Navigate back on success
    - _Requirements: 3.2, 3.3, 3.5_

- [ ] 7.8 Write property test for product search
  - **Property 6: Search Filter Correctness**
  - **Validates: Requirements 3.6**

- [ ] 7.9 Write unit tests for ProductViewModel
  - Test product loading
  - Test search functionality
  - Test CRUD operations
  - _Requirements: 3.1, 3.2, 3.5, 3.6_

- [ ] 8. Billing and Invoice Module
  - [ ] 8.1 Create InvoiceRepository
    - Create invoice with API call
    - Save invoice to Room with sync status
    - Fetch invoices with date filtering
    - Generate PDF function
    - _Requirements: 4.3, 4.4, 4.7_
  
  - [ ] 8.2 Create BillingViewModel
    - Cart management (add, remove, update quantity)
    - Customer selection
    - Real-time total calculation with GST
    - Create invoice function
    - Payment method selection
    - _Requirements: 4.1, 4.2, 4.3, 4.6_
  
  - [ ] 8.3 Create BillingActivity with XML layout
    - Product search and selection
    - RecyclerView for cart items
    - Customer selection spinner
    - Payment method radio buttons
    - Total display with GST breakdown
    - Complete invoice button
    - _Requirements: 4.1, 4.2, 4.6_
  
  - [ ] 8.4 Implement cart functionality
    - Add products to cart
    - Update quantities
    - Remove items
    - Calculate totals with GST
    - _Requirements: 4.1, 4.2_
  
  - [ ] 8.5 Implement invoice creation flow
    - Validate cart and customer
    - Call ViewModel to create invoice
    - Update stock quantities
    - Navigate to invoice detail on success
    - _Requirements: 4.3, 4.5_
  
  - [ ] 8.6 Create InvoiceListFragment with XML layout
    - RecyclerView with InvoiceAdapter
    - Date range filter
    - Search by invoice number
    - Click to view details
    - _Requirements: 4.1_
  
  - [ ] 8.7 Create InvoiceDetailActivity with XML layout
    - Display full invoice details
    - PDF preview
    - Share button (WhatsApp, Email)
    - Print button
    - _Requirements: 4.4_
  
  - [ ] 8.8 Implement PDF generation
    - Use iText library
    - Generate invoice PDF with business details
    - Include GST breakdown
    - Save to app storage
    - _Requirements: 4.4_
  
  - [ ] 8.9 Implement share functionality
    - Create share intent with PDF
    - Support WhatsApp and Email
    - Use Android share sheet
    - _Requirements: 4.4, 10.4_

- [ ] 8.10 Write property test for invoice calculation
  - **Property 3: Invoice Total Calculation**
  - **Validates: Requirements 4.2**

- [ ] 8.11 Write property test for stock update
  - **Property 4: Stock Quantity Invariant**
  - **Validates: Requirements 4.5, 7.4**

- [ ] 8.12 Write unit tests for BillingViewModel
  - Test cart operations
  - Test total calculation
  - Test invoice creation
  - _Requirements: 4.1, 4.2, 4.3_

- [ ] 9. Customer Management Module
  - [ ] 9.1 Create CustomerRepository
    - CRUD operations with offline support
    - Search customers
    - Fetch purchase history
    - _Requirements: 5.1, 5.2, 5.4_
  
  - [ ] 9.2 Create CustomerViewModel
    - Load customers with Flow
    - Search functionality
    - Add/update customer functions
    - Get purchase history
    - _Requirements: 5.1, 5.2, 5.4_
  
  - [ ] 9.3 Create CustomersFragment with XML layout
    - RecyclerView with CustomerAdapter
    - Search bar
    - FAB for adding customers
    - Click to view details
    - _Requirements: 5.1, 5.4_
  
  - [ ] 9.4 Create CustomerDetailActivity with XML layout
    - Display customer information
    - Show outstanding credit
    - RecyclerView for purchase history
    - Edit button
    - _Requirements: 5.3_
  
  - [ ] 9.5 Create AddEditCustomerActivity with XML layout
    - Form for customer details
    - Input validation
    - Save button
    - _Requirements: 5.2_

- [ ] 9.6 Write property test for customer credit balance
  - **Property 7: Customer Credit Balance**
  - **Validates: Requirements 5.3**

- [ ] 9.7 Write unit tests for CustomerViewModel
  - Test customer loading
  - Test search
  - Test CRUD operations
  - _Requirements: 5.1, 5.2, 5.4_

- [ ] 10. Stock Management Module
  - [ ] 10.1 Create StockRepository
    - Fetch stock levels from API
    - Get low stock items
    - Adjust stock with reason
    - Fetch stock history
    - _Requirements: 7.1, 7.2, 7.3, 7.5_
  
  - [ ] 10.2 Create StockViewModel
    - Load stock items
    - Filter low stock
    - Adjust stock function
    - Get stock history
    - _Requirements: 7.1, 7.2, 7.3, 7.5_
  
  - [ ] 10.3 Create StockFragment with XML layout
    - RecyclerView with StockAdapter
    - Low stock filter toggle
    - Click to adjust stock
    - Low stock indicators (red badge)
    - _Requirements: 7.1, 7.2_
  
  - [ ] 10.4 Create stock adjustment dialog
    - Input for quantity adjustment
    - Reason dropdown
    - Confirm button
    - _Requirements: 7.3_
  
  - [ ] 10.5 Implement stock adjustment logic
    - Validate input
    - Call ViewModel to adjust stock
    - Update UI on success
    - _Requirements: 7.3, 7.4_

- [ ] 10.6 Write property test for low stock detection
  - **Property 8: Low Stock Detection**
  - **Validates: Requirements 7.2**

- [ ] 10.7 Write unit tests for StockViewModel
  - Test stock loading
  - Test low stock filtering
  - Test stock adjustment
  - _Requirements: 7.1, 7.2, 7.3_

- [ ] 11. Offline Sync Module
  - [ ] 11.1 Create SyncRepository
    - Sync all entities (products, invoices, customers, stock)
    - Handle sync conflicts (server-wins strategy)
    - Track sync status
    - Get last sync time
    - _Requirements: 6.2, 6.3, 6.4, 6.6_
  
  - [ ] 11.2 Create SyncWorker with WorkManager
    - Implement doWork() to call SyncRepository
    - Handle retry on failure
    - Post notification on sync completion
    - _Requirements: 6.2, 6.6_
  
  - [ ] 11.3 Create SyncManager
    - Schedule periodic sync (15 minutes)
    - Trigger manual sync
    - Configure network constraints
    - _Requirements: 6.2, 6.6_
  
  - [ ] 11.4 Implement sync status UI
    - Display last sync time in toolbar
    - Show sync indicator during sync
    - Manual sync button
    - _Requirements: 6.3_
  
  - [ ] 11.5 Implement conflict resolution
    - Server data takes precedence
    - Notify user of conflicts
    - Log conflicts for audit
    - _Requirements: 6.4_

- [ ] 11.6 Write property test for sync idempotence
  - **Property 5: Sync Idempotence**
  - **Validates: Requirements 6.2**

- [ ] 11.7 Write property test for sync queue ordering
  - **Property 10: Data Sync Queue Ordering**
  - **Validates: Requirements 6.2**

- [ ] 11.8 Write integration tests for sync
  - Test full sync flow
  - Test conflict resolution
  - Test offline queue
  - _Requirements: 6.2, 6.4, 6.6_

- [ ] 12. Reports Module
  - [ ] 12.1 Create ReportsRepository
    - Fetch sales report from API
    - Fetch product report
    - Fetch customer report
    - Export report to PDF/Excel
    - _Requirements: 8.1, 8.2, 8.4_
  
  - [ ] 12.2 Create ReportsViewModel
    - Load sales report with date range
    - Load product report
    - Load customer report
    - Export report function
    - _Requirements: 8.1, 8.2, 8.4_
  
  - [ ] 12.3 Create ReportsFragment with XML layout
    - Date range picker
    - Report type tabs
    - Chart view (MPAndroidChart)
    - Export button
    - _Requirements: 8.1, 8.2, 8.5_
  
  - [ ] 12.4 Implement chart visualization
    - Line chart for daily sales
    - Bar chart for top products
    - Pie chart for payment methods
    - _Requirements: 8.3, 8.5_
  
  - [ ] 12.5 Implement report export
    - Generate PDF report
    - Generate Excel report
    - Share exported file
    - _Requirements: 8.4_

- [ ] 12.6 Write unit tests for ReportsViewModel
  - Test report loading
  - Test date filtering
  - Test export functionality
  - _Requirements: 8.1, 8.2, 8.4_

- [ ] 13. Settings Module
  - [ ] 13.1 Create SettingsFragment with XML layout
    - Business configuration section
    - GST rate settings
    - Invoice template settings
    - Language selection
    - Sync preferences
    - Dark mode toggle
    - _Requirements: 9.1, 9.2, 9.3, 9.4_
  
  - [ ] 13.2 Implement settings persistence
    - Use SharedPreferences for settings
    - Sync settings to server
    - Apply settings immediately
    - _Requirements: 9.5_
  
  - [ ] 13.3 Implement language switching
    - Support English and Hindi
    - Update app locale
    - Restart activity on language change
    - _Requirements: 9.3_
  
  - [ ] 13.4 Implement dark mode
    - Follow system setting
    - Manual override option
    - Update theme dynamically
    - _Requirements: 10.9_

- [ ] 14. Native Android Features Integration
  - [ ] 14.1 Implement notification system
    - Create notification channels
    - Show sync status notifications
    - Show low stock alerts
    - Handle notification clicks
    - _Requirements: 10.3_
  
  - [ ] 14.2 Implement print functionality
    - Use Android Print Framework
    - Create print adapter for invoices
    - Handle print job status
    - _Requirements: 10.6_
  
  - [ ] 14.3 Implement proper back navigation
    - Handle back button in all activities
    - Proper back stack management
    - Confirm exit on back from main screen
    - _Requirements: 10.2_
  
  - [ ] 14.4 Implement Activity lifecycle management
    - Save/restore instance state
    - Handle configuration changes
    - Proper resource cleanup
    - _Requirements: 10.8_

- [ ] 15. UI Polish and Material Design
  - [ ] 15.1 Apply Material Design 3 theme
    - Define color scheme
    - Configure dynamic colors
    - Set up typography
    - Configure shapes and elevation
    - _Requirements: 10.1_
  
  - [ ] 15.2 Add animations and transitions
    - Activity transitions
    - Fragment transitions
    - RecyclerView item animations
    - Button ripple effects
    - _Requirements: 10.1_
  
  - [ ] 15.3 Implement responsive layouts
    - Support different screen sizes
    - Landscape orientation layouts
    - Tablet-specific layouts
    - _Requirements: 10.1_
  
  - [ ] 15.4 Add accessibility features
    - Content descriptions for all images
    - Minimum touch targets (48dp)
    - Color contrast compliance
    - TalkBack support
    - _Requirements: 10.1_

- [ ] 16. Testing and Quality Assurance
  - [ ] 16.1 Write UI tests with Espresso
    - Test login flow
    - Test product creation flow
    - Test invoice creation flow
    - Test navigation
    - _Requirements: 1.1, 3.2, 4.3_
  
  - [ ] 16.2 Run all property-based tests
    - Verify all 10 properties pass
    - Fix any failing tests
    - Ensure 100+ iterations per test
    - _Requirements: All_
  
  - [ ] 16.3 Perform manual testing
    - Test offline mode
    - Test barcode scanning
    - Test PDF generation
    - Test print functionality
    - Test on multiple devices
    - _Requirements: 3.7, 4.4, 6.1, 10.6_

- [ ] 17. Build and Release Preparation
  - [ ] 17.1 Configure ProGuard rules
    - Keep rules for Retrofit
    - Keep rules for Room
    - Keep rules for Gson
    - Test release build
    - _Requirements: 10.1_
  
  - [ ] 17.2 Generate signed APK/AAB
    - Create keystore
    - Configure signing in Gradle
    - Build release APK
    - Build release AAB for Play Store
    - _Requirements: 10.1_
  
  - [ ] 17.3 Prepare app store assets
    - App icon (all sizes)
    - Screenshots (phone and tablet)
    - Feature graphic
    - App description
    - Privacy policy
    - _Requirements: 10.1_

- [ ] 18. Final Integration and Testing
  - Ensure all modules work together seamlessly
  - Test complete user workflows end-to-end
  - Verify offline-to-online sync works correctly
  - Test on minimum SDK version (Android 7.0)
  - Performance testing and optimization
  - _Requirements: All_

## Notes

- All tasks are required for comprehensive implementation
- Each task references specific requirements for traceability
- Build incrementally: complete each module before moving to the next
- Test frequently during development
- Use Android Studio's built-in tools (Layout Inspector, Profiler, Logcat)
- Follow Kotlin coding conventions and Android best practices
- Commit code regularly with meaningful commit messages
