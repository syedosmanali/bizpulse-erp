# Design Document: Native Android ERP Application

## Overview

This document describes the architecture and design for a native Android ERP application built with Java/Kotlin. The app follows modern Android development best practices including MVVM architecture, Repository pattern, Room database for offline storage, Retrofit for API communication, and Material Design 3 for UI. The application will provide a seamless offline-first experience with automatic background synchronization.

## Architecture

### High-Level Architecture

The application follows the **MVVM (Model-View-ViewModel)** architecture pattern with a **Repository layer** for data management:

```
┌─────────────────────────────────────────────────────────────┐
│                         UI Layer                             │
│  (Activities, Fragments, XML Layouts, Compose)              │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                    ViewModel Layer                           │
│  (Business Logic, UI State Management, LiveData/Flow)       │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   Repository Layer                           │
│  (Data Source Coordination, Caching Strategy)               │
└─────────┬──────────────────────────────────┬────────────────┘
          │                                  │
┌─────────▼──────────┐            ┌─────────▼──────────────┐
│   Local Data       │            │   Remote Data          │
│   (Room Database)  │            │   (Retrofit + API)     │
└────────────────────┘            └────────────────────────┘
```

### Technology Stack

- **Language**: Kotlin (primary), Java (legacy support)
- **UI Framework**: XML Layouts with Material Design 3 components
- **Architecture**: MVVM with Repository pattern
- **Dependency Injection**: Hilt (Dagger)
- **Database**: Room (SQLite wrapper)
- **Networking**: Retrofit + OkHttp
- **Async Operations**: Kotlin Coroutines + Flow
- **Image Loading**: Glide
- **Barcode Scanning**: ML Kit Barcode Scanning
- **PDF Generation**: iText or Android PdfDocument
- **Charts**: MPAndroidChart
- **Minimum SDK**: 24 (Android 7.0)
- **Target SDK**: 34 (Android 14)

## Components and Interfaces

### 1. Authentication Module

#### Components

**LoginActivity**
- Entry point for unauthenticated users
- Material Design login form with email/password fields
- "Remember Me" checkbox for persistent sessions
- Error handling with Snackbar messages

**AuthViewModel**
```kotlin
class AuthViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {
    
    val loginState: StateFlow<LoginState>
    
    fun login(email: String, password: String)
    fun logout()
    fun checkAuthStatus(): Boolean
}

sealed class LoginState {
    object Idle : LoginState()
    object Loading : LoginState()
    data class Success(val user: User) : LoginState()
    data class Error(val message: String) : LoginState()
}
```

**AuthRepository**
```kotlin
interface AuthRepository {
    suspend fun login(email: String, password: String): Result<User>
    suspend fun logout()
    suspend fun getStoredToken(): String?
    suspend fun saveToken(token: String)
    suspend fun getCurrentUser(): User?
}

class AuthRepositoryImpl @Inject constructor(
    private val apiService: ApiService,
    private val tokenManager: TokenManager,
    private val userDao: UserDao
) : AuthRepository {
    // Implementation
}
```

**TokenManager**
```kotlin
class TokenManager @Inject constructor(
    private val encryptedPrefs: SharedPreferences
) {
    fun saveToken(token: String)
    fun getToken(): String?
    fun clearToken()
}
```

#### API Endpoints

- `POST /api/auth/login` - User authentication
- `POST /api/auth/logout` - Session termination
- `GET /api/auth/me` - Get current user info

### 2. Dashboard Module

#### Components

**DashboardActivity**
- Main screen after login
- Bottom navigation for main sections
- Hosts fragments for different modules

**DashboardFragment**
```kotlin
class DashboardFragment : Fragment() {
    private val viewModel: DashboardViewModel by viewModels()
    private var _binding: FragmentDashboardBinding? = null
    private val binding get() = _binding!!
    
    override fun onCreateView(...): View {
        _binding = FragmentDashboardBinding.inflate(inflater, container, false)
        return binding.root
    }
}
```

**DashboardViewModel**
```kotlin
class DashboardViewModel @Inject constructor(
    private val dashboardRepository: DashboardRepository
) : ViewModel() {
    
    val metrics: StateFlow<DashboardMetrics>
    val syncStatus: StateFlow<SyncStatus>
    
    fun refreshMetrics()
    fun triggerSync()
}

data class DashboardMetrics(
    val totalSales: Double,
    val todaySales: Double,
    val totalInvoices: Int,
    val lowStockCount: Int,
    val topProducts: List<Product>
)
```

**DashboardRepository**
```kotlin
interface DashboardRepository {
    suspend fun getMetrics(): Result<DashboardMetrics>
    fun getMetricsFlow(): Flow<DashboardMetrics>
}
```

#### UI Components

- Material Cards for metrics display
- RecyclerView for quick actions
- SwipeRefreshLayout for pull-to-refresh
- MPAndroidChart for sales graphs

### 3. Product Management Module

#### Components

**ProductsFragment**
- RecyclerView with product list
- Search bar with real-time filtering
- FAB (Floating Action Button) for adding products
- Swipe actions for edit/delete

**ProductDetailActivity**
- Displays full product information
- Edit mode with form validation
- Stock adjustment controls
- Barcode display/generation

**AddEditProductActivity**
- Form for creating/editing products
- Image picker for product photos
- Barcode scanner integration
- Input validation

**ProductViewModel**
```kotlin
class ProductViewModel @Inject constructor(
    private val productRepository: ProductRepository
) : ViewModel() {
    
    val products: StateFlow<List<Product>>
    val searchQuery: MutableStateFlow<String>
    
    fun loadProducts()
    fun searchProducts(query: String)
    fun addProduct(product: Product)
    fun updateProduct(product: Product)
    fun deleteProduct(productId: String)
    fun scanBarcode(): Flow<String>
}
```

**ProductRepository**
```kotlin
interface ProductRepository {
    fun getAllProducts(): Flow<List<Product>>
    suspend fun getProductById(id: String): Product?
    suspend fun insertProduct(product: Product): Result<Product>
    suspend fun updateProduct(product: Product): Result<Product>
    suspend fun deleteProduct(id: String): Result<Unit>
    suspend fun searchProducts(query: String): List<Product>
    suspend fun syncProducts()
}
```

#### API Endpoints

- `GET /api/products` - List all products
- `GET /api/products/{id}` - Get product details
- `POST /api/products` - Create product
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product

### 4. Billing and Invoice Module

#### Components

**BillingActivity**
- Product selection with search
- Shopping cart with quantity controls
- Customer selection dropdown
- Payment method selection
- Real-time total calculation with GST

**InvoiceListFragment**
- RecyclerView with invoice history
- Date range filters
- Search by invoice number or customer
- Click to view invoice details

**InvoiceDetailActivity**
- Full invoice display
- PDF preview
- Share options (WhatsApp, Email, Print)
- Reprint functionality

**BillingViewModel**
```kotlin
class BillingViewModel @Inject constructor(
    private val invoiceRepository: InvoiceRepository,
    private val productRepository: ProductRepository
) : ViewModel() {
    
    val cartItems: StateFlow<List<CartItem>>
    val selectedCustomer: MutableStateFlow<Customer?>
    val totalAmount: StateFlow<Double>
    val gstAmount: StateFlow<Double>
    
    fun addToCart(product: Product, quantity: Int)
    fun removeFromCart(productId: String)
    fun updateQuantity(productId: String, quantity: Int)
    fun selectCustomer(customer: Customer)
    fun createInvoice(paymentMethod: PaymentMethod): Flow<Result<Invoice>>
}

data class CartItem(
    val product: Product,
    val quantity: Int,
    val subtotal: Double
)
```

**InvoiceRepository**
```kotlin
interface InvoiceRepository {
    suspend fun createInvoice(invoice: Invoice): Result<Invoice>
    fun getAllInvoices(): Flow<List<Invoice>>
    suspend fun getInvoiceById(id: String): Invoice?
    suspend fun generatePdf(invoice: Invoice): Result<File>
    suspend fun syncInvoices()
}
```

#### API Endpoints

- `POST /api/invoices` - Create invoice
- `GET /api/invoices` - List invoices
- `GET /api/invoices/{id}` - Get invoice details
- `GET /api/invoices/{id}/pdf` - Generate PDF

### 5. Customer Management Module

#### Components

**CustomersFragment**
- RecyclerView with customer list
- Search functionality
- FAB for adding customers
- Click to view customer details

**CustomerDetailActivity**
- Customer information display
- Purchase history
- Outstanding credit balance
- Edit customer option

**CustomerViewModel**
```kotlin
class CustomerViewModel @Inject constructor(
    private val customerRepository: CustomerRepository
) : ViewModel() {
    
    val customers: StateFlow<List<Customer>>
    
    fun loadCustomers()
    fun searchCustomers(query: String)
    fun addCustomer(customer: Customer)
    fun updateCustomer(customer: Customer)
    fun getCustomerPurchaseHistory(customerId: String): Flow<List<Invoice>>
}
```

**CustomerRepository**
```kotlin
interface CustomerRepository {
    fun getAllCustomers(): Flow<List<Customer>>
    suspend fun getCustomerById(id: String): Customer?
    suspend fun insertCustomer(customer: Customer): Result<Customer>
    suspend fun updateCustomer(customer: Customer): Result<Customer>
    suspend fun searchCustomers(query: String): List<Customer>
    suspend fun syncCustomers()
}
```

### 6. Offline Sync Module

#### Components

**SyncService**
```kotlin
@HiltWorker
class SyncWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val syncRepository: SyncRepository
) : CoroutineWorker(context, params) {
    
    override suspend fun doWork(): Result {
        return try {
            syncRepository.syncAll()
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}
```

**SyncRepository**
```kotlin
interface SyncRepository {
    suspend fun syncAll()
    suspend fun syncProducts()
    suspend fun syncInvoices()
    suspend fun syncCustomers()
    suspend fun syncStock()
    fun getSyncStatus(): Flow<SyncStatus>
    fun getLastSyncTime(): Long
}

data class SyncStatus(
    val isSyncing: Boolean,
    val lastSyncTime: Long,
    val pendingChanges: Int,
    val error: String?
)
```

**SyncManager**
```kotlin
class SyncManager @Inject constructor(
    private val workManager: WorkManager,
    private val syncRepository: SyncRepository
) {
    fun schedulePeriodic
Sync() {
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
            
        val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(
            15, TimeUnit.MINUTES
        ).setConstraints(constraints).build()
        
        workManager.enqueueUniquePeriodicWork(
            "sync_work",
            ExistingPeriodicWorkPolicy.KEEP,
            syncRequest
        )
    }
    
    fun triggerManualSync() {
        val syncRequest = OneTimeWorkRequestBuilder<SyncWorker>().build()
        workManager.enqueue(syncRequest)
    }
}
```

### 7. Stock Management Module

#### Components

**StockFragment**
- RecyclerView with stock levels
- Low stock indicators (red badge)
- Stock adjustment dialog
- Filter by low stock

**StockViewModel**
```kotlin
class StockViewModel @Inject constructor(
    private val stockRepository: StockRepository
) : ViewModel() {
    
    val stockItems: StateFlow<List<StockItem>>
    val lowStockItems: StateFlow<List<StockItem>>
    
    fun loadStock()
    fun adjustStock(productId: String, quantity: Int, reason: String)
    fun getStockHistory(productId: String): Flow<List<StockMovement>>
}

data class StockItem(
    val product: Product,
    val currentQuantity: Int,
    val minQuantity: Int,
    val isLowStock: Boolean
)

data class StockMovement(
    val id: String,
    val productId: String,
    val quantity: Int,
    val type: MovementType,
    val reason: String,
    val timestamp: Long
)

enum class MovementType {
    SALE, PURCHASE, ADJUSTMENT, RETURN
}
```

**StockRepository**
```kotlin
interface StockRepository {
    fun getAllStock(): Flow<List<StockItem>>
    fun getLowStock(): Flow<List<StockItem>>
    suspend fun adjustStock(productId: String, quantity: Int, reason: String): Result<Unit>
    suspend fun getStockHistory(productId: String): List<StockMovement>
    suspend fun syncStock()
}
```

### 8. Reports Module

#### Components

**ReportsFragment**
- Date range picker
- Report type selector (Sales, Products, Customers)
- Chart visualization
- Export button

**ReportsViewModel**
```kotlin
class ReportsViewModel @Inject constructor(
    private val reportsRepository: ReportsRepository
) : ViewModel() {
    
    val salesReport: StateFlow<SalesReport>
    val dateRange: MutableStateFlow<DateRange>
    
    fun loadSalesReport(startDate: Long, endDate: Long)
    fun loadProductReport()
    fun loadCustomerReport()
    fun exportReport(format: ExportFormat): Flow<Result<File>>
}

data class SalesReport(
    val totalSales: Double,
    val totalInvoices: Int,
    val averageInvoiceValue: Double,
    val dailySales: List<DailySales>,
    val topProducts: List<ProductSales>,
    val topCustomers: List<CustomerSales>
)

data class DailySales(
    val date: Long,
    val sales: Double,
    val invoiceCount: Int
)

enum class ExportFormat {
    PDF, EXCEL, CSV
}
```

## Data Models

### Core Entities

**User**
```kotlin
@Entity(tableName = "users")
data class User(
    @PrimaryKey val id: String,
    val email: String,
    val name: String,
    val businessName: String,
    val role: String,
    val createdAt: Long,
    val updatedAt: Long
)
```

**Product**
```kotlin
@Entity(tableName = "products")
data class Product(
    @PrimaryKey val id: String,
    val name: String,
    val description: String?,
    val barcode: String?,
    val price: Double,
    val costPrice: Double?,
    val gstRate: Double,
    val category: String?,
    val imageUrl: String?,
    val unit: String,
    val minStock: Int,
    val createdAt: Long,
    val updatedAt: Long,
    val syncStatus: SyncStatus = SyncStatus.SYNCED
)
```

**Invoice**
```kotlin
@Entity(tableName = "invoices")
data class Invoice(
    @PrimaryKey val id: String,
    val invoiceNumber: String,
    val customerId: String?,
    val customerName: String?,
    val items: List<InvoiceItem>,
    val subtotal: Double,
    val gstAmount: Double,
    val totalAmount: Double,
    val paymentMethod: PaymentMethod,
    val status: InvoiceStatus,
    val createdAt: Long,
    val syncStatus: SyncStatus = SyncStatus.SYNCED
)

data class InvoiceItem(
    val productId: String,
    val productName: String,
    val quantity: Int,
    val price: Double,
    val gstRate: Double,
    val subtotal: Double
)

enum class PaymentMethod {
    CASH, CARD, UPI, CREDIT
}

enum class InvoiceStatus {
    DRAFT, COMPLETED, CANCELLED
}

enum class SyncStatus {
    SYNCED, PENDING, FAILED
}
```

**Customer**
```kotlin
@Entity(tableName = "customers")
data class Customer(
    @PrimaryKey val id: String,
    val name: String,
    val phone: String?,
    val email: String?,
    val address: String?,
    val gstNumber: String?,
    val creditLimit: Double,
    val outstandingBalance: Double,
    val createdAt: Long,
    val updatedAt: Long,
    val syncStatus: SyncStatus = SyncStatus.SYNCED
)
```

### Database Schema

**Room Database**
```kotlin
@Database(
    entities = [
        User::class,
        Product::class,
        Invoice::class,
        Customer::class,
        StockMovement::class
    ],
    version = 1,
    exportSchema = true
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
    abstract fun productDao(): ProductDao
    abstract fun invoiceDao(): InvoiceDao
    abstract fun customerDao(): CustomerDao
    abstract fun stockDao(): StockDao
}
```

### DAOs (Data Access Objects)

**ProductDao**
```kotlin
@Dao
interface ProductDao {
    @Query("SELECT * FROM products ORDER BY name ASC")
    fun getAllProducts(): Flow<List<Product>>
    
    @Query("SELECT * FROM products WHERE id = :id")
    suspend fun getProductById(id: String): Product?
    
    @Query("SELECT * FROM products WHERE name LIKE '%' || :query || '%' OR barcode LIKE '%' || :query || '%'")
    suspend fun searchProducts(query: String): List<Product>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertProduct(product: Product)
    
    @Update
    suspend fun updateProduct(product: Product)
    
    @Delete
    suspend fun deleteProduct(product: Product)
    
    @Query("SELECT * FROM products WHERE syncStatus = :status")
    suspend fun getProductsBySyncStatus(status: SyncStatus): List<Product>
}
```

## Networking Layer

### API Service

**ApiService**
```kotlin
interface ApiService {
    
    // Auth
    @POST("api/auth/login")
    suspend fun login(@Body request: LoginRequest): Response<LoginResponse>
    
    @POST("api/auth/logout")
    suspend fun logout(): Response<Unit>
    
    @GET("api/auth/me")
    suspend fun getCurrentUser(): Response<User>
    
    // Products
    @GET("api/products")
    suspend fun getProducts(): Response<List<Product>>
    
    @GET("api/products/{id}")
    suspend fun getProduct(@Path("id") id: String): Response<Product>
    
    @POST("api/products")
    suspend fun createProduct(@Body product: Product): Response<Product>
    
    @PUT("api/products/{id}")
    suspend fun updateProduct(@Path("id") id: String, @Body product: Product): Response<Product>
    
    @DELETE("api/products/{id}")
    suspend fun deleteProduct(@Path("id") id: String): Response<Unit>
    
    // Invoices
    @POST("api/invoices")
    suspend fun createInvoice(@Body invoice: Invoice): Response<Invoice>
    
    @GET("api/invoices")
    suspend fun getInvoices(
        @Query("start_date") startDate: Long?,
        @Query("end_date") endDate: Long?
    ): Response<List<Invoice>>
    
    @GET("api/invoices/{id}")
    suspend fun getInvoice(@Path("id") id: String): Response<Invoice>
    
    // Customers
    @GET("api/customers")
    suspend fun getCustomers(): Response<List<Customer>>
    
    @POST("api/customers")
    suspend fun createCustomer(@Body customer: Customer): Response<Customer>
    
    @PUT("api/customers/{id}")
    suspend fun updateCustomer(@Path("id") id: String, @Body customer: Customer): Response<Customer>
    
    // Dashboard
    @GET("api/dashboard/metrics")
    suspend fun getDashboardMetrics(): Response<DashboardMetrics>
    
    // Stock
    @GET("api/stock")
    suspend fun getStock(): Response<List<StockItem>>
    
    @POST("api/stock/adjust")
    suspend fun adjustStock(@Body request: StockAdjustmentRequest): Response<Unit>
    
    // Reports
    @GET("api/reports/sales")
    suspend fun getSalesReport(
        @Query("start_date") startDate: Long,
        @Query("end_date") endDate: Long
    ): Response<SalesReport>
}
```

### Network Module (Hilt)

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    
    @Provides
    @Singleton
    fun provideOkHttpClient(
        tokenManager: TokenManager
    ): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor { chain ->
                val request = chain.request().newBuilder()
                tokenManager.getToken()?.let { token ->
                    request.addHeader("Authorization", "Bearer $token")
                }
                chain.proceed(request.build())
            }
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            })
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build()
    }
    
    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://bizpulse24.com/")
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }
    
    @Provides
    @Singleton
    fun provideApiService(retrofit: Retrofit): ApiService {
        return retrofit.create(ApiService::class.java)
    }
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Authentication Token Persistence

*For any* successful login, storing the authentication token and then retrieving it should return the same token value.

**Validates: Requirements 1.1, 1.5**

### Property 2: Offline Data Consistency

*For any* data modification made while offline, after successful sync, querying the server should return data equivalent to the local modification.

**Validates: Requirements 6.1, 6.2**

### Property 3: Invoice Total Calculation

*For any* invoice with items, the total amount should equal the sum of (item price × quantity × (1 + GST rate)) for all items.

**Validates: Requirements 4.2**

### Property 4: Stock Quantity Invariant

*For any* product, after creating an invoice with that product, the stock quantity should decrease by the invoice quantity.

**Validates: Requirements 4.5, 7.4**

### Property 5: Sync Idempotence

*For any* synced data, performing sync multiple times should result in the same server state as syncing once.

**Validates: Requirements 6.2**

### Property 6: Search Filter Correctness

*For any* search query on products, all returned products should have names or barcodes containing the query string (case-insensitive).

**Validates: Requirements 3.6**

### Property 7: Customer Credit Balance

*For any* customer, the outstanding balance should equal the sum of all unpaid invoice amounts for that customer.

**Validates: Requirements 5.3**

### Property 8: Low Stock Detection

*For any* product, if current quantity is less than minimum threshold, the product should appear in the low stock list.

**Validates: Requirements 7.2**

### Property 9: Session Persistence

*For any* valid stored session token, launching the app should navigate directly to Dashboard without requiring login.

**Validates: Requirements 1.4**

### Property 10: Data Sync Queue Ordering

*For any* sequence of offline modifications, syncing should apply changes in the same chronological order they were made locally.

**Validates: Requirements 6.2**

## Error Handling

### Network Errors

**Strategy**: Graceful degradation with offline mode

- All network calls wrapped in try-catch with Result type
- Network failures trigger offline mode automatically
- User notified via Snackbar with retry option
- Failed requests queued for retry when connectivity restored

**Implementation**:
```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val exception: Exception, val message: String) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

suspend fun <T> safeApiCall(
    apiCall: suspend () -> Response<T>
): Result<T> {
    return try {
        val response = apiCall()
        if (response.isSuccessful && response.body() != null) {
            Result.Success(response.body()!!)
        } else {
            Result.Error(
                HttpException(response),
                response.message() ?: "Unknown error"
            )
        }
    } catch (e: IOException) {
        Result.Error(e, "Network error. Working offline.")
    } catch (e: Exception) {
        Result.Error(e, e.message ?: "Unknown error")
    }
}
```

### Database Errors

**Strategy**: Transaction rollback with user notification

- All database operations in transactions
- Constraint violations caught and reported
- Automatic retry for transient failures
- Data integrity checks before commits

### Sync Conflicts

**Strategy**: Server-wins with user notification

- Server data always takes precedence
- Local changes backed up before overwrite
- User notified of conflicts with option to review
- Conflict log maintained for audit

### Validation Errors

**Strategy**: Immediate feedback with clear messages

- Input validation before API calls
- Real-time validation on form fields
- Clear error messages in Material Design style
- Focus on first invalid field

## Testing Strategy

### Unit Tests

**Focus Areas**:
- ViewModel business logic
- Repository data coordination
- Utility functions (calculations, formatting)
- Data model validation

**Example**:
```kotlin
@Test
fun `invoice total calculation is correct`() {
    val items = listOf(
        InvoiceItem("1", "Product A", 2, 100.0, 0.18, 200.0),
        InvoiceItem("2", "Product B", 1, 50.0, 0.18, 50.0)
    )
    val invoice = Invoice(
        id = "inv1",
        invoiceNumber = "INV001",
        customerId = null,
        customerName = null,
        items = items,
        subtotal = 250.0,
        gstAmount = 45.0,
        totalAmount = 295.0,
        paymentMethod = PaymentMethod.CASH,
        status = InvoiceStatus.COMPLETED,
        createdAt = System.currentTimeMillis()
    )
    
    val calculatedTotal = invoice.items.sumOf { 
        it.price * it.quantity * (1 + it.gstRate) 
    }
    
    assertEquals(295.0, calculatedTotal, 0.01)
}
```

### Property-Based Tests

**Framework**: Kotest Property Testing

**Configuration**: Minimum 100 iterations per property test

**Test Tags**: Each test tagged with `Feature: native-android-erp, Property {number}: {property_text}`

**Example**:
```kotlin
@Test
@Tag("Feature: native-android-erp, Property 3: Invoice Total Calculation")
fun `property test - invoice total equals sum of item totals`() = runTest {
    checkAll(100, Arb.list(Arb.invoiceItem(), 1..10)) { items ->
        val subtotal = items.sumOf { it.price * it.quantity }
        val gstAmount = items.sumOf { it.price * it.quantity * it.gstRate }
        val expectedTotal = subtotal + gstAmount
        
        val invoice = createInvoice(items)
        
        assertEquals(expectedTotal, invoice.totalAmount, 0.01)
    }
}
```

### Integration Tests

**Focus Areas**:
- Repository + DAO interactions
- API + Repository coordination
- Sync service end-to-end
- Database migrations

### UI Tests (Espresso)

**Focus Areas**:
- Login flow
- Product creation flow
- Invoice creation flow
- Navigation between screens

**Example**:
```kotlin
@Test
fun loginFlow_withValidCredentials_navigatesToDashboard() {
    onView(withId(R.id.emailEditText))
        .perform(typeText("test@example.com"))
    
    onView(withId(R.id.passwordEditText))
        .perform(typeText("password123"))
    
    onView(withId(R.id.loginButton))
        .perform(click())
    
    onView(withId(R.id.dashboardLayout))
        .check(matches(isDisplayed()))
}
```

### Manual Testing Checklist

- [ ] Offline mode functionality
- [ ] Barcode scanning accuracy
- [ ] PDF generation quality
- [ ] Print functionality
- [ ] Share intents (WhatsApp, Email)
- [ ] Dark mode appearance
- [ ] Different screen sizes
- [ ] Android back button behavior
- [ ] App lifecycle (background/foreground)
- [ ] Notification display

## UI/UX Design Guidelines

### Material Design 3

- Use Material 3 components from `com.google.android.material`
- Follow Material Design color system with dynamic colors
- Implement proper elevation and shadows
- Use Material motion for transitions

### Navigation

- Bottom Navigation for main sections (Dashboard, Products, Invoices, More)
- Navigation Drawer for secondary options
- Proper back stack management
- Deep linking support for notifications

### Accessibility

- Content descriptions for all images and icons
- Minimum touch target size of 48dp
- Sufficient color contrast ratios
- Support for TalkBack screen reader
- Scalable text sizes

### Responsive Design

- Support for phones and tablets
- Landscape orientation support
- Adaptive layouts using ConstraintLayout
- Different layouts for different screen sizes

## Performance Optimization

### Database

- Indexed columns for frequent queries
- Pagination for large lists (Paging 3 library)
- Background thread for all database operations
- Database query optimization

### Networking

- Request caching with OkHttp
- Image caching with Glide
- Batch API requests where possible
- Request deduplication

### Memory

- ViewBinding instead of findViewById
- Proper lifecycle management
- Bitmap recycling for images
- Avoid memory leaks with WeakReferences

### Battery

- WorkManager for background tasks
- Doze mode compatibility
- Efficient sync scheduling
- Wake lock management

## Security Considerations

### Data Storage

- Encrypted SharedPreferences for tokens
- Android Keystore for sensitive data
- Room database encryption (SQLCipher)
- Secure file storage

### Network

- HTTPS only (certificate pinning optional)
- Token-based authentication
- Request signing for critical operations
- Timeout configurations

### Code

- ProGuard/R8 obfuscation for release builds
- Root detection (optional)
- Tamper detection
- Secure coding practices

## Build Configuration

### Gradle Setup

```kotlin
android {
    namespace = "com.bizpulse.erp"
    compileSdk = 34
    
    defaultConfig {
        applicationId = "com.bizpulse.erp"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"
        
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }
    
    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            buildConfigField("String", "API_BASE_URL", "\"https://bizpulse24.com/\"")
        }
        debug {
            buildConfigField("String", "API_BASE_URL", "\"https://bizpulse24.com/\"")
        }
    }
    
    buildFeatures {
        viewBinding = true
        buildConfig = true
    }
    
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    
    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    // Core Android
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    
    // Architecture Components
    implementation("androidx.lifecycle:lifecycle-viewmodel-ktx:2.7.0")
    implementation("androidx.lifecycle:lifecycle-livedata-ktx:2.7.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.7.0")
    
    // Navigation
    implementation("androidx.navigation:navigation-fragment-ktx:2.7.6")
    implementation("androidx.navigation:navigation-ui-ktx:2.7.6")
    
    // Room Database
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    kapt("androidx.room:room-compiler:2.6.1")
    
    // Retrofit & OkHttp
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")
    
    // Hilt Dependency Injection
    implementation("com.google.dagger:hilt-android:2.50")
    kapt("com.google.dagger:hilt-compiler:2.50")
    
    // WorkManager
    implementation("androidx.work:work-runtime-ktx:2.9.0")
    implementation("androidx.hilt:hilt-work:1.1.0")
    kapt("androidx.hilt:hilt-compiler:1.1.0")
    
    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    
    // Image Loading
    implementation("com.github.bumptech.glide:glide:4.16.0")
    kapt("com.github.bumptech.glide:compiler:4.16.0")
    
    // Barcode Scanning
    implementation("com.google.mlkit:barcode-scanning:17.2.0")
    implementation("androidx.camera:camera-camera2:1.3.1")
    implementation("androidx.camera:camera-lifecycle:1.3.1")
    implementation("androidx.camera:camera-view:1.3.1")
    
    // Charts
    implementation("com.github.PhilJay:MPAndroidChart:v3.1.0")
    
    // PDF Generation
    implementation("com.itextpdf:itext7-core:7.2.5")
    
    // Testing
    testImplementation("junit:junit:4.13.2")
    testImplementation("io.kotest:kotest-runner-junit5:5.8.0")
    testImplementation("io.kotest:kotest-assertions-core:5.8.0")
    testImplementation("io.kotest:kotest-property:5.8.0")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")
    testImplementation("androidx.arch.core:core-testing:2.2.0")
    
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
    androidTestImplementation("androidx.test:runner:1.5.2")
    androidTestImplementation("androidx.test:rules:1.5.0")
}
```

## Deployment Strategy

### Release Process

1. **Version Bump**: Update versionCode and versionName
2. **Testing**: Run full test suite
3. **Build**: Generate signed APK/AAB
4. **QA**: Manual testing on multiple devices
5. **Release**: Upload to Google Play Console
6. **Monitor**: Track crashes and ANRs

### CI/CD Pipeline

- GitHub Actions for automated builds
- Unit tests run on every PR
- Automated APK generation for releases
- Crash reporting with Firebase Crashlytics

## Future Enhancements

- Multi-language support (Hindi, regional languages)
- Voice commands for hands-free operation
- Biometric authentication
- Cloud backup and restore
- Multi-store support
- Advanced analytics with ML insights
- Integration with payment gateways
- Loyalty program management
- Employee attendance tracking
- Expense management
