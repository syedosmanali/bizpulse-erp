# OFFLINE-FIRST SYNC SYSTEM DESIGN

## Overview
A robust offline-first system that ensures your mobile app works seamlessly without internet, with intelligent syncing when connection is available.

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MOBILE APP    │    │   SYNC ENGINE   │    │  SERVER/CLOUD   │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Local SQLite│ │◄──►│ │ Sync Queue  │ │◄──►│ │ Main DB     │ │
│ │ Database    │ │    │ │ Manager     │ │    │ │ (PostgreSQL)│ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Offline UI  │ │    │ │ Conflict    │ │    │ │ Sync API    │ │
│ │ Components  │ │    │ │ Resolver    │ │    │ │ Endpoints   │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 1. LOCAL DATABASE STRUCTURE

### Core Tables
```sql
-- Main business data tables
CREATE TABLE products_local (
    id TEXT PRIMARY KEY,
    name TEXT,
    price REAL,
    stock INTEGER,
    -- Sync metadata
    sync_status TEXT DEFAULT 'synced', -- 'pending', 'synced', 'conflict'
    last_modified INTEGER,
    version INTEGER DEFAULT 1,
    is_deleted INTEGER DEFAULT 0
);

CREATE TABLE sales_local (
    id TEXT PRIMARY KEY,
    customer_name TEXT,
    total_amount REAL,
    sale_date INTEGER,
    -- Sync metadata
    sync_status TEXT DEFAULT 'pending',
    last_modified INTEGER,
    version INTEGER DEFAULT 1,
    is_deleted INTEGER DEFAULT 0
);

-- Sync queue for tracking changes
CREATE TABLE sync_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT,
    record_id TEXT,
    operation TEXT, -- 'INSERT', 'UPDATE', 'DELETE'
    data TEXT, -- JSON data
    timestamp INTEGER,
    retry_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending' -- 'pending', 'syncing', 'synced', 'failed'
);

-- Conflict resolution table
CREATE TABLE sync_conflicts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT,
    record_id TEXT,
    local_data TEXT,
    server_data TEXT,
    conflict_type TEXT,
    created_at INTEGER,
    resolved INTEGER DEFAULT 0
);
```

## 2. SYNC FLOW DIAGRAM

```
USER ACTION → LOCAL DB → SYNC QUEUE → BACKGROUND SYNC → SERVER
     ↓            ↓           ↓              ↓            ↓
   Instant    Immediate   Queued for    When online   Updates
  Response    Storage     sync later                  main DB

OFFLINE FLOW:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ User adds   │───►│ Save to     │───►│ Add to      │
│ new sale    │    │ local DB    │    │ sync queue  │
└─────────────┘    └─────────────┘    └─────────────┘
                           │
                           ▼
                   ┌─────────────┐
                   │ Show success│
                   │ to user     │
                   └─────────────┘

ONLINE SYNC FLOW:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Internet    │───►│ Process     │───►│ Send to     │───►│ Update      │
│ detected    │    │ sync queue  │    │ server      │    │ local status│
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## 3. SYNC QUEUE SYSTEM

### Queue Operations
```javascript
// Add operation to sync queue
function addToSyncQueue(tableName, recordId, operation, data) {
    const queueItem = {
        table_name: tableName,
        record_id: recordId,
        operation: operation,
        data: JSON.stringify(data),
        timestamp: Date.now(),
        status: 'pending'
    };
    
    // Insert into sync_queue table
    insertIntoSyncQueue(queueItem);
}

// Process sync queue when online
async function processSyncQueue() {
    const pendingItems = getPendingQueueItems();
    
    for (const item of pendingItems) {
        try {
            await syncItemToServer(item);
            markItemAsSynced(item.id);
        } catch (error) {
            handleSyncError(item, error);
        }
    }
}
```

### Sync Priority System
```
HIGH PRIORITY (Sync first):
├── Sales transactions
├── Customer payments
└── Stock updates

MEDIUM PRIORITY:
├── Product updates
├── Customer info changes
└── Settings changes

LOW PRIORITY:
├── Reports generation
├── Backup data
└── Analytics data
```

## 4. CONFLICT RESOLUTION RULES

### Conflict Types & Resolution
```
CONFLICT TYPE 1: Same record updated on both sides
┌─────────────────┐    ┌─────────────────┐
│ LOCAL VERSION   │    │ SERVER VERSION  │
│ Product: Rice   │ VS │ Product: Rice   │
│ Price: ₹50      │    │ Price: ₹55      │
│ Modified: 10:30 │    │ Modified: 10:45 │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────┬───────────────┘
                 ▼
    RESOLUTION: Server wins (latest timestamp)
    + Keep local as backup in conflicts table

CONFLICT TYPE 2: Record deleted on server, updated locally
┌─────────────────┐    ┌─────────────────┐
│ LOCAL VERSION   │    │ SERVER VERSION  │
│ Product: Wheat  │ VS │ Product: DELETED│
│ Stock: 100      │    │ Status: Removed │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────┬───────────────┘
                 ▼
    RESOLUTION: Ask user to decide
    + Show conflict resolution UI

CONFLICT TYPE 3: New record with same ID
┌─────────────────┐    ┌─────────────────┐
│ LOCAL VERSION   │    │ SERVER VERSION  │
│ Sale ID: S001   │ VS │ Sale ID: S001   │
│ Amount: ₹1000   │    │ Amount: ₹1500   │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────┬───────────────┘
                 ▼
    RESOLUTION: Generate new ID for local
    + Sync both records separately
```

### Resolution Algorithm
```javascript
function resolveConflict(localData, serverData, conflictType) {
    switch (conflictType) {
        case 'UPDATE_UPDATE':
            // Server wins, backup local
            return {
                action: 'accept_server',
                backup_local: true,
                notify_user: false
            };
            
        case 'DELETE_UPDATE':
            // Ask user
            return {
                action: 'ask_user',
                options: ['keep_local', 'accept_delete'],
                backup_local: true
            };
            
        case 'ID_COLLISION':
            // Generate new ID for local
            return {
                action: 'generate_new_id',
                sync_both: true
            };
    }
}
```

## 5. PARTIAL SYNC SUPPORT

### Sync Strategies
```
FULL SYNC (First time):
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Download    │───►│ Download    │───►│ Download    │
│ Products    │    │ Customers   │    │ Settings    │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           ▼
                   ┌─────────────┐
                   │ Mark as     │
                   │ fully synced│
                   └─────────────┘

INCREMENTAL SYNC (Regular):
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Check last  │───►│ Download    │───►│ Upload      │
│ sync time   │    │ changes     │    │ local queue │
└─────────────┘    └─────────────┘    └─────────────┘

SELECTIVE SYNC (User choice):
┌─────────────┐
│ User selects│
│ what to sync│
└──────┬──────┘
       │
   ┌───▼────┐  ┌─────────┐  ┌──────────┐
   │Products│  │Customers│  │Sales Only│
   └────────┘  └─────────┘  └──────────┘
```

### Sync Configuration
```javascript
const syncConfig = {
    // What to sync
    tables: {
        products: { priority: 'high', partial: true },
        sales: { priority: 'high', partial: false },
        customers: { priority: 'medium', partial: true },
        reports: { priority: 'low', partial: true }
    },
    
    // When to sync
    triggers: {
        app_start: true,
        internet_available: true,
        user_manual: true,
        scheduled: '*/30 * * * *' // Every 30 minutes
    },
    
    // How much to sync
    limits: {
        max_records_per_batch: 100,
        max_sync_time: 30000, // 30 seconds
        retry_attempts: 3
    }
};
```

## 6. IMPLEMENTATION STEPS

### Step 1: Setup Local Database
```javascript
// Initialize SQLite database
function initializeLocalDB() {
    const db = SQLite.openDatabase('bizpulse_local.db');
    
    // Create tables with sync metadata
    db.transaction(tx => {
        tx.executeSql(CREATE_PRODUCTS_TABLE);
        tx.executeSql(CREATE_SALES_TABLE);
        tx.executeSql(CREATE_SYNC_QUEUE_TABLE);
        tx.executeSql(CREATE_CONFLICTS_TABLE);
    });
    
    return db;
}
```

### Step 2: Implement Offline Operations
```javascript
// Save data locally with sync queue entry
function saveProductOffline(productData) {
    // 1. Save to local database
    const result = insertProduct(productData);
    
    // 2. Add to sync queue
    addToSyncQueue('products', result.id, 'INSERT', productData);
    
    // 3. Return success immediately
    return { success: true, id: result.id, offline: true };
}
```

### Step 3: Background Sync Service
```javascript
// Background sync service
class SyncService {
    constructor() {
        this.isOnline = false;
        this.syncInProgress = false;
    }
    
    startMonitoring() {
        // Monitor internet connection
        NetInfo.addEventListener(state => {
            if (state.isConnected && !this.syncInProgress) {
                this.startSync();
            }
        });
    }
    
    async startSync() {
        this.syncInProgress = true;
        
        try {
            // 1. Download server changes
            await this.downloadChanges();
            
            // 2. Upload local changes
            await this.uploadChanges();
            
            // 3. Resolve conflicts
            await this.resolveConflicts();
            
        } catch (error) {
            console.log('Sync failed:', error);
        } finally {
            this.syncInProgress = false;
        }
    }
}
```

### Step 4: Conflict Resolution UI
```javascript
// Show conflict resolution to user
function showConflictResolution(conflict) {
    return new Promise((resolve) => {
        Alert.alert(
            'Data Conflict Found',
            `${conflict.table_name} has been changed on both devices.`,
            [
                {
                    text: 'Keep Local Version',
                    onPress: () => resolve('keep_local')
                },
                {
                    text: 'Use Server Version',
                    onPress: () => resolve('use_server')
                },
                {
                    text: 'Merge Both',
                    onPress: () => resolve('merge')
                }
            ]
        );
    });
}
```

## 7. SYNC STATUS INDICATORS

### UI Status Display
```
SYNC STATUS INDICATORS:
┌─────────────────────────────────────┐
│ ● Online & Synced    (Green)        │
│ ◐ Syncing...         (Yellow)       │
│ ○ Offline Mode       (Gray)         │
│ ⚠ Sync Conflicts     (Orange)       │
│ ✗ Sync Failed        (Red)          │
└─────────────────────────────────────┘

RECORD-LEVEL INDICATORS:
┌─────────────────────────────────────┐
│ Sale #001            ✓ Synced       │
│ Sale #002            ⏳ Pending     │
│ Sale #003            ⚠ Conflict     │
│ Sale #004            ✗ Failed       │
└─────────────────────────────────────┘
```

## 8. PERFORMANCE OPTIMIZATION

### Sync Optimization Strategies
```
BATCH OPERATIONS:
├── Group similar operations together
├── Compress data before sending
└── Use delta sync (only changes)

SMART SCHEDULING:
├── Sync during low usage times
├── Prioritize critical data first
└── Pause sync during heavy app usage

BANDWIDTH MANAGEMENT:
├── Detect connection type (WiFi/Mobile)
├── Adjust sync frequency accordingly
└── Allow user to set data usage limits
```

## 9. ERROR HANDLING & RECOVERY

### Error Recovery Flow
```
SYNC ERROR OCCURS
        │
        ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Retry with  │───►│ Exponential │───►│ Mark as     │
│ backoff     │    │ delay       │    │ failed      │
└─────────────┘    └─────────────┘    └─────────────┘
        │                                     │
        ▼                                     ▼
┌─────────────┐                      ┌─────────────┐
│ Log error   │                      │ Notify user │
│ details     │                      │ & allow     │
└─────────────┘                      │ manual retry│
                                     └─────────────┘
```

## 10. TESTING STRATEGY

### Test Scenarios
```javascript
// Test offline functionality
function testOfflineMode() {
    // 1. Disconnect internet
    // 2. Perform CRUD operations
    // 3. Verify local storage
    // 4. Check sync queue entries
}

// Test sync conflicts
function testConflictResolution() {
    // 1. Create same record on both sides
    // 2. Modify differently
    // 3. Trigger sync
    // 4. Verify conflict detection
    // 5. Test resolution options
}

// Test partial sync
function testPartialSync() {
    // 1. Configure selective sync
    // 2. Verify only selected data syncs
    // 3. Test sync interruption/resume
}
```

This offline-first sync system ensures your mobile app works seamlessly without internet while providing robust synchronization when connectivity is available. The system handles conflicts intelligently and gives users control over their data.