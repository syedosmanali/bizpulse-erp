# Client-Level User Management System Documentation

## Overview

A comprehensive multi-tenant user management system for BizPulse ERP that allows client administrators to create, manage, and control user access within their organization while maintaining complete data isolation between clients.

## Key Features

### 🔐 Security & Access Control
- **Multi-tenant isolation**: Complete data separation between clients
- **Role-based access control (RBAC)**: Granular permissions system
- **Secure password management**: bcrypt hashing with temporary passwords
- **Session management**: Secure session handling with automatic logout
- **Activity logging**: Complete audit trail of all user actions

### 👥 User Hierarchy
1. **Super Admin (BizPulse Team)**
   - Can view all clients and their users (read-only)
   - Can disable clients if needed
   - Access to system-wide statistics

2. **Client Admin (Shop Owner)**
   - Full user management capabilities
   - Can create, edit, deactivate, and delete users
   - Can reset passwords and manage roles
   - Can create custom roles with specific permissions

3. **Client Users (Staff)**
   - Predefined roles: Cashier, Biller, Manager, Accountant, Supervisor, Store Keeper, Sales Executive
   - Custom roles can be created by Client Admin
   - Role-based access to ERP modules

### 🛠 Core Functionality

#### User Management
- **Create Users**: Auto-generated user IDs and temporary passwords
- **Edit Users**: Update profile information, roles, and status
- **Password Reset**: Generate new temporary passwords
- **Deactivate/Activate**: Soft disable without data loss
- **Delete Users**: Only allowed if no transaction history

#### Role Management
- **System Roles**: 7 predefined roles with appropriate permissions
- **Custom Roles**: Client admins can create tailored roles
- **Permission Matrix**: Module-level permissions (view, create, edit, delete, export)

#### Activity Tracking
- **User Actions**: All user activities logged with timestamps
- **Security Events**: Login attempts, password changes, role modifications
- **Audit Trail**: Complete history for compliance and monitoring

## Database Schema

### Core Tables

#### `user_roles`
```sql
CREATE TABLE user_roles (
    id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL,
    role_name TEXT NOT NULL,
    display_name TEXT NOT NULL,
    permissions TEXT NOT NULL DEFAULT '{}',
    is_system_role BOOLEAN DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_by TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(client_id, role_name)
);
```

#### `user_accounts`
```sql
CREATE TABLE user_accounts (
    id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL,
    user_id TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    email TEXT,
    mobile TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    temp_password TEXT,
    role_id TEXT NOT NULL,
    department TEXT,
    status TEXT DEFAULT 'active',
    force_password_change BOOLEAN DEFAULT 1,
    last_login TIMESTAMP,
    login_count INTEGER DEFAULT 0,
    failed_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    created_by TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients (id),
    FOREIGN KEY (role_id) REFERENCES user_roles (id)
);
```

#### `user_activity_log`
```sql
CREATE TABLE user_activity_log (
    id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    module TEXT NOT NULL,
    action TEXT NOT NULL,
    details TEXT,
    ip_address TEXT,
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints

### User Management
- `GET /api/user-management/users` - Get all users for client
- `POST /api/user-management/users` - Create new user
- `PUT /api/user-management/users/{id}` - Update user
- `DELETE /api/user-management/users/{id}` - Delete user
- `POST /api/user-management/users/{id}/reset-password` - Reset password
- `POST /api/user-management/users/{id}/deactivate` - Deactivate user
- `POST /api/user-management/users/{id}/activate` - Activate user

### Role Management
- `GET /api/user-management/roles` - Get available roles
- `POST /api/user-management/roles` - Create custom role

### Activity & Monitoring
- `GET /api/user-management/activity` - Get activity logs
- `POST /api/user-management/initialize` - Initialize system for client

### Super Admin Endpoints
- `GET /admin/user-management/clients/{id}/users` - Get users for any client
- `GET /admin/user-management/stats` - Get system statistics

## Default Roles & Permissions

### 1. Cashier
- **Sales**: View, Create
- **Customers**: View, Create
- **Products**: View
- **Billing**: View, Create
- **Reports**: View

### 2. Biller
- **Sales**: View, Create, Edit
- **Customers**: View, Create, Edit
- **Products**: View
- **Billing**: View, Create, Edit
- **Invoices**: View, Create
- **Reports**: View

### 3. Manager
- **Sales**: View, Create, Edit, Delete
- **Customers**: View, Create, Edit, Delete
- **Products**: View, Create, Edit
- **Billing**: View, Create, Edit, Delete
- **Invoices**: View, Create, Edit
- **Inventory**: View, Create, Edit
- **Reports**: View, Export
- **Settings**: View

### 4. Accountant
- **Sales**: View
- **Customers**: View
- **Billing**: View
- **Invoices**: View, Create, Edit
- **Reports**: View, Export
- **Earnings**: View
- **Credit**: View, Create, Edit

### 5. Supervisor
- **Sales**: View, Create, Edit
- **Customers**: View, Create, Edit
- **Products**: View, Create, Edit
- **Billing**: View, Create, Edit
- **Inventory**: View, Create, Edit
- **Reports**: View, Export

### 6. Store Keeper
- **Products**: View, Create, Edit
- **Inventory**: View, Create, Edit, Delete
- **Reports**: View

### 7. Sales Executive
- **Sales**: View, Create, Edit
- **Customers**: View, Create, Edit
- **Products**: View
- **Billing**: View, Create
- **Reports**: View

## Security Features

### Password Security
- **bcrypt Hashing**: Industry-standard password hashing
- **Temporary Passwords**: Auto-generated secure passwords
- **Force Password Change**: Users must change password on first login
- **Password Strength**: Validation for strong passwords

### Account Security
- **Account Locking**: Automatic lockout after 5 failed attempts
- **Session Management**: Secure session tokens
- **Activity Logging**: All actions tracked with IP and user agent
- **Input Sanitization**: Protection against injection attacks

### Access Control
- **Client Isolation**: Complete data separation between tenants
- **Permission Checking**: Module-level permission validation
- **Session Validation**: Every request validates user permissions
- **Role-based Access**: Granular control over feature access

## Frontend Features

### User Management Dashboard
- **Modern UI**: Clean, responsive design with Bootstrap 5
- **Real-time Updates**: Dynamic loading and filtering
- **Search & Filter**: Find users by name, role, or status
- **Bulk Operations**: Manage multiple users efficiently

### User Cards
- **Profile Information**: Name, role, contact details
- **Status Indicators**: Active/inactive badges
- **Quick Actions**: Edit, reset password, deactivate, delete
- **Activity Indicators**: Last login, login count

### Role Management
- **Visual Permissions**: Clear display of role capabilities
- **Custom Role Creation**: Easy role builder interface
- **Permission Matrix**: Checkbox-based permission assignment

## Installation & Setup

### 1. Database Migration
```bash
python migrate_user_system.py
```

### 2. Install Dependencies
```bash
pip install bcrypt
```

### 3. Access User Management
- Navigate to `/user-management` (Client Admins only)
- System automatically initializes for new clients

## Usage Guide

### For Client Admins

#### Creating a User
1. Click "Add New User" button
2. Fill in required information:
   - Full Name (required)
   - Mobile Number (required)
   - Username (required)
   - Email (optional)
   - Role (required)
   - Department (optional)
3. System generates temporary password
4. User receives credentials and must change password on first login

#### Managing Users
- **Edit**: Click edit icon to modify user details
- **Reset Password**: Generate new temporary password
- **Deactivate**: Temporarily disable user access
- **Delete**: Permanently remove user (only if no transactions)

#### Role Management
- View existing roles and their permissions
- Create custom roles with specific permissions
- Assign roles to users during creation or editing

### For Super Admins
- View all clients and their user counts
- Access read-only user information across all clients
- Monitor system-wide user activity and statistics

## Security Best Practices

### For Administrators
1. **Regular Password Resets**: Encourage periodic password changes
2. **Role Review**: Regularly audit user roles and permissions
3. **Activity Monitoring**: Check activity logs for suspicious behavior
4. **Account Cleanup**: Remove unused accounts promptly

### For Users
1. **Strong Passwords**: Use complex passwords when changing from temporary
2. **Secure Login**: Always log out when finished
3. **Report Issues**: Notify admin of any suspicious activity

## Troubleshooting

### Common Issues

#### User Cannot Login
1. Check if account is active
2. Verify username/password
3. Check if account is locked (failed attempts)
4. Reset password if needed

#### Permission Denied
1. Verify user role has required permissions
2. Check if user is assigned to correct role
3. Ensure client admin has proper access

#### Database Errors
1. Run migration script if tables missing
2. Check database permissions
3. Verify foreign key relationships

## API Response Examples

### Create User Success
```json
{
    "success": true,
    "user_id": "usr_123456",
    "username": "john_doe",
    "temp_password": "TempPass123!"
}
```

### Get Users Response
```json
{
    "success": true,
    "users": [
        {
            "id": "usr_123456",
            "full_name": "John Doe",
            "username": "john_doe",
            "email": "john@example.com",
            "mobile": "9876543210",
            "role_name": "Cashier",
            "department": "Sales",
            "status": "active",
            "last_login": "2024-01-14T10:30:00",
            "force_password_change": false
        }
    ]
}
```

### Error Response
```json
{
    "success": false,
    "error": "Username already exists",
    "errors": ["Username must be at least 3 characters"]
}
```

## Migration Notes

### Existing Data
- All existing `client_users` data is automatically migrated
- Users are assigned to "Cashier" role by default during migration
- Temporary passwords are preserved if they exist
- All user statuses and creation dates are maintained

### Backward Compatibility
- Old authentication methods continue to work
- Existing sessions remain valid
- Legacy password hashes are supported

## Future Enhancements

### Planned Features
1. **Two-Factor Authentication**: SMS/Email OTP support
2. **Advanced Permissions**: Field-level access control
3. **User Groups**: Organize users into departments/teams
4. **Bulk Import**: CSV import for multiple users
5. **Advanced Reporting**: Detailed user analytics
6. **Mobile App Integration**: Native mobile user management

### Performance Optimizations
1. **Database Indexing**: Optimize query performance
2. **Caching**: Redis integration for session management
3. **Pagination**: Handle large user lists efficiently
4. **Background Jobs**: Async operations for bulk actions

## Support

For technical support or feature requests:
- Email: support@bizpulse.com
- Documentation: Internal wiki
- Issue Tracking: GitHub repository

---

**Version**: 1.0.0  
**Last Updated**: January 14, 2025  
**Author**: BizPulse Development Team