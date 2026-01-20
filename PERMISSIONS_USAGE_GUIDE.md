# User Permissions - Usage Guide

## Quick Start

### Step 1: Access Permissions Management
1. Login as **Client Admin** (not employee)
2. Navigate to **User Management** from the sidebar
3. Click on **Permissions** in the left menu

### Step 2: View Current Permissions
You'll see a table with:
- **Left Column**: All your users (name, username, role)
- **Top Row**: All available modules
- **Cells**: Toggle switches for each user-module combination

### Step 3: Enable/Disable Modules
- **Toggle ON** (blue): User can access this module
- **Toggle OFF** (gray): User cannot access this module
- Changes save automatically
- Success message appears after each change

## Example Scenarios

### Scenario 1: Cashier (Limited Access)
**Enable**: Dashboard, Billing, Customers
**Disable**: Sales, Products, Inventory, Reports, Credit

**Result**: Cashier can only:
- View dashboard
- Create bills
- Manage customers

### Scenario 2: Store Manager (Full Access)
**Enable**: All modules

**Result**: Manager has complete access to all features

### Scenario 3: Accountant (Reports Only)
**Enable**: Dashboard, Reports, Credit
**Disable**: Billing, Sales, Products, Inventory, Customers

**Result**: Accountant can only:
- View dashboard
- Access reports
- Manage credit

### Scenario 4: Inventory Manager
**Enable**: Dashboard, Products, Inventory
**Disable**: Billing, Sales, Customers, Reports, Credit

**Result**: Inventory manager can only:
- View dashboard
- Manage products
- Control inventory

## What Employees See

### Before Permission Changes
Employee sees all modules in navigation:
```
📊 Dashboard
💰 Sales
💳 Credit Management
🧾 Billing
📦 Products
📦 Inventory
👥 Customers
📈 Reports
```

### After Disabling Some Modules
Employee only sees enabled modules:
```
📊 Dashboard
🧾 Billing
👥 Customers
```

**Note**: Disabled modules are completely hidden - no "access denied" messages.

## Important Notes

### Who Can Manage Permissions?
✅ **Client Admins** (Business Owners)
❌ **Employees** (Cannot access permissions page)

### Default Behavior
- New users have **all modules enabled** by default
- You must manually disable modules you want to restrict

### Real-Time Updates
- Permission changes apply **immediately**
- Employee must refresh their browser to see changes
- No need to logout/login

### Cannot Be Restricted
These features are always available to everyone:
- Settings
- Profile
- Logout

## Troubleshooting

### Employee Still Sees Disabled Module
**Solution**: Ask employee to refresh their browser (F5 or Ctrl+R)

### Cannot Access Permissions Page
**Check**: Are you logged in as Client Admin?
**Note**: Employees cannot access this page

### Toggle Not Working
**Check**: 
1. Are you connected to internet?
2. Is the server running?
3. Check browser console for errors

### All Modules Showing for Employee
**Reason**: No permissions have been set yet
**Solution**: Set at least one module to disabled, then all others will follow the permission rules

## Best Practices

### 1. Start with Minimal Access
- Enable only essential modules for each role
- Add more permissions as needed
- Easier to grant than revoke access

### 2. Use Role-Based Permissions
- Group users by role (Cashier, Manager, etc.)
- Apply same permissions to users with same role
- Maintain consistency

### 3. Regular Audits
- Review permissions monthly
- Remove access for inactive users
- Update permissions when roles change

### 4. Document Your Setup
- Keep a list of which roles have which permissions
- Document reasons for special cases
- Makes training new admins easier

## Permission Matrix Template

| Role | Dashboard | Billing | Sales | Products | Customers | Inventory | Reports | Credit |
|------|-----------|---------|-------|----------|-----------|-----------|---------|--------|
| Cashier | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Biller | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ |
| Manager | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Accountant | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Store Keeper | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ |

Copy this template and customize for your business needs!
