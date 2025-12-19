# ERP Backend API Contract v1.0.0

**Version**: 1.0.0  
**Base URL**: `https://api.erp-system.com/v1`  
**Authentication**: Bearer Token (JWT)  
**Content-Type**: `application/json`

---

## 🔒 **API VERSIONING POLICY**

### **CRITICAL RULES:**
1. **v1 API is IMMUTABLE** - Once published, v1 endpoints can NEVER be changed
2. **Backward Compatibility** - v1 must remain functional for minimum 2 years
3. **New Features** - All new features and changes go to v2
4. **Deprecation** - 6-month notice before any version retirement
5. **Breaking Changes** - Only allowed in new major versions

---

## 📋 **STANDARD RESPONSE FORMAT**

All API responses follow this consistent structure:

### **Success Response**
```json
{
  "success": true,
  "data": {}, // Response payload
  "message": "Operation completed successfully",
  "meta": {
    "timestamp": "2024-01-01T12:00:00Z",
    "version": "v1",
    "pagination": { // Only for paginated responses
      "page": 1,
      "limit": 10,
      "total": 100,
      "totalPages": 10
    }
  }
}
```

### **Error Response**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {
      "field": ["Specific validation errors"]
    }
  },
  "meta": {
    "timestamp": "2024-01-01T12:00:00Z",
    "version": "v1",
    "requestId": "req_123456789"
  }
}
```

---

## 🏥 **HEALTH CHECK API**

### **GET /health**
System health check for load balancers and monitoring.

**Request**: No parameters

**Response**: `200 OK`
```json
{
  "success": true,
  "data": {
    "status": "ok",
    "checks": {
      "database": { "status": "up", "responseTime": "12ms" },
      "memory": { "status": "up", "usage": "45%" },
      "disk": { "status": "up", "usage": "23%" }
    },
    "uptime": 86400,
    "version": "1.0.0"
  },
  "message": "System is healthy"
}
```

**Error Codes**:
- `503` - Service Unavailable (system unhealthy)

### **GET /health/live**
Kubernetes liveness probe.

**Response**: `200 OK`
```json
{
  "success": true,
  "data": {
    "status": "ok",
    "timestamp": "2024-01-01T12:00:00Z",
    "uptime": 86400
  }
}
```

### **GET /health/ready**
Kubernetes readiness probe.

**Response**: `200 OK` / `503 Service Unavailable`
```json
{
  "success": true,
  "data": {
    "status": "ready",
    "database": "connected"
  }
}
```

---

## 🔐 **AUTHENTICATION API**

### **POST /auth/login**
User authentication with organization context.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "organizationId": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Validation Rules**:
- `email`: Valid email format, required
- `password`: String, 1-255 characters, required
- `organizationId`: Valid UUID v4, required

**Response**: `200 OK`
```json
{
  "success": true,
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "tokenType": "Bearer",
    "expiresIn": 86400,
    "user": {
      "id": "user-uuid",
      "firstName": "John",
      "lastName": "Doe",
      "email": "user@example.com",
      "roles": ["manager", "cashier"],
      "organizationId": "org-uuid",
      "organization": {
        "id": "org-uuid",
        "name": "Pizza Palace",
        "slug": "pizza-palace"
      },
      "isActive": true,
      "isEmailVerified": true,
      "lastLoginAt": "2024-01-01T12:00:00Z",
      "createdAt": "2024-01-01T00:00:00Z"
    }
  },
  "message": "Login successful"
}
```

**Error Codes**:
- `400` - `VALIDATION_ERROR`: Invalid input data
- `401` - `INVALID_CREDENTIALS`: Wrong email/password
- `401` - `ACCOUNT_DEACTIVATED`: User account disabled
- `401` - `ORGANIZATION_INACTIVE`: Organization disabled
- `429` - `RATE_LIMIT_EXCEEDED`: Too many login attempts

### **POST /auth/refresh**
Refresh access token using refresh token.

**Request Body**:
```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response**: `200 OK` (Same structure as login)

**Error Codes**:
- `400` - `VALIDATION_ERROR`: Missing refresh token
- `401` - `INVALID_REFRESH_TOKEN`: Token invalid/expired
- `401` - `ACCOUNT_DEACTIVATED`: User account disabled

### **GET /auth/me**
Get current authenticated user profile.

**Headers**: `Authorization: Bearer <access-token>`

**Response**: `200 OK`
```json
{
  "success": true,
  "data": {
    "id": "user-uuid",
    "firstName": "John",
    "lastName": "Doe",
    "fullName": "John Doe",
    "email": "user@example.com",
    "phone": "+1-555-0123",
    "roles": ["manager", "cashier"],
    "permissions": {
      "products:read": true,
      "orders:create": true
    },
    "organizationId": "org-uuid",
    "organization": {
      "id": "org-uuid",
      "name": "Pizza Palace",
      "slug": "pizza-palace"
    },
    "isActive": true,
    "isEmailVerified": true,
    "lastLoginAt": "2024-01-01T12:00:00Z",
    "avatarUrl": "https://cdn.example.com/avatar.jpg",
    "preferences": {
      "theme": "dark",
      "language": "en"
    },
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-01-01T12:00:00Z"
  },
  "message": "User profile retrieved successfully"
}
```

**Error Codes**:
- `401` - `AUTHENTICATION_REQUIRED`: Missing/invalid token
- `401` - `TOKEN_EXPIRED`: Access token expired

### **POST /auth/logout**
User logout (client-side token removal).

**Headers**: `Authorization: Bearer <access-token>`

**Response**: `200 OK`
```json
{
  "success": true,
  "data": null,
  "message": "Logout successful. Please remove tokens from client storage."
}
```

### **GET /auth/validate**
Validate current JWT token.

**Headers**: `Authorization: Bearer <access-token>`

**Response**: `200 OK`
```json
{
  "success": true,
  "data": {
    "valid": true,
    "user": {
      "id": "user-uuid",
      "email": "user@example.com",
      "organizationId": "org-uuid",
      "roles": ["manager"]
    }
  },
  "message": "Token is valid"
}
```

---

## 👥 **USER MANAGEMENT API**

### **POST /users**
Create a new user within an organization.

**Headers**: `Authorization: Bearer <access-token>`

**Request Body**:
```json
{
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@pizzapalace.com",
  "phone": "+1-555-0123",
  "password": "SecurePass123!",
  "organizationId": "123e4567-e89b-12d3-a456-426614174000",
  "roles": ["manager", "cashier"],
  "avatarUrl": "https://cdn.example.com/avatar.jpg",
  "preferences": {
    "theme": "dark",
    "language": "en"
  }
}
```

**Validation Rules**:
- `firstName`: String, 1-100 chars, required
- `lastName`: String, 1-100 chars, required
- `email`: Valid email, required, unique per organization
- `phone`: String, 1-20 chars, optional
- `password`: String, min 8 chars, must contain uppercase, lowercase, number, special char
- `organizationId`: Valid UUID v4, required
- `roles`: Array of strings, optional, defaults to ["employee"]
- `avatarUrl`: Valid URL, optional
- `preferences`: Object, optional

**Response**: `201 Created`
```json
{
  "success": true,
  "data": {
    "id": "user-uuid",
    "firstName": "John",
    "lastName": "Doe",
    "fullName": "John Doe",
    "email": "john.doe@pizzapalace.com",
    "phone": "+1-555-0123",
    "roles": ["manager", "cashier"],
    "permissions": {},
    "organizationId": "org-uuid",
    "organization": {
      "id": "org-uuid",
      "name": "Pizza Palace"
    },
    "isActive": true,
    "isEmailVerified": false,
    "lastLoginAt": null,
    "avatarUrl": "https://cdn.example.com/avatar.jpg",
    "preferences": {
      "theme": "dark",
      "language": "en"
    },
    "createdAt": "2024-01-01T12:00:00Z",
    "updatedAt": "2024-01-01T12:00:00Z"
  },
  "message": "User created successfully"
}
```

**Error Codes**:
- `400` - `VALIDATION_ERROR`: Invalid input data
- `401` - `AUTHENTICATION_REQUIRED`: Missing/invalid token
- `403` - `INSUFFICIENT_PERMISSIONS`: No permission to create users
- `404` - `ORGANIZATION_NOT_FOUND`: Invalid organization ID
- `409` - `EMAIL_ALREADY_EXISTS`: Email taken in organization
- `409` - `ORGANIZATION_INACTIVE`: Cannot create user for inactive org

### **GET /users/organization/{organizationId}**
Get paginated list of users within an organization.

**Headers**: `Authorization: Bearer <access-token>`

**Path Parameters**:
- `organizationId`: UUID v4, required

**Query Parameters**:
- `page`: Integer, min 1, default 1
- `limit`: Integer, min 1, max 100, default 10
- `sortBy`: String, default "createdAt"
- `sortOrder`: Enum ["ASC", "DESC"], default "DESC"

**Response**: `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": "user-uuid",
      "firstName": "John",
      "lastName": "Doe",
      "fullName": "John Doe",
      "email": "john.doe@pizzapalace.com",
      "phone": "+1-555-0123",
      "roles": ["manager"],
      "organizationId": "org-uuid",
      "organization": {
        "id": "org-uuid",
        "name": "Pizza Palace"
      },
      "isActive": true,
      "isEmailVerified": true,
      "lastLoginAt": "2024-01-01T11:00:00Z",
      "createdAt": "2024-01-01T00:00:00Z",
      "updatedAt": "2024-01-01T11:00:00Z"
    }
  ],
  "message": "Users retrieved successfully",
  "meta": {
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 25,
      "totalPages": 3
    }
  }
}
```

**Error Codes**:
- `400` - `VALIDATION_ERROR`: Invalid query parameters
- `401` - `AUTHENTICATION_REQUIRED`: Missing/invalid token
- `403` - `INSUFFICIENT_PERMISSIONS`: No permission to view users
- `404` - `ORGANIZATION_NOT_FOUND`: Invalid organization ID

### **GET /users/{id}**
Get user by ID.

**Headers**: `Authorization: Bearer <access-token>`

**Path Parameters**:
- `id`: UUID v4, required

**Response**: `200 OK` (Same user object structure as create)

**Error Codes**:
- `401` - `AUTHENTICATION_REQUIRED`: Missing/invalid token
- `403` - `INSUFFICIENT_PERMISSIONS`: No permission to view user
- `404` - `USER_NOT_FOUND`: User doesn't exist

### **PATCH /users/{id}**
Update user information (partial update).

**Headers**: `Authorization: Bearer <access-token>`

**Path Parameters**:
- `id`: UUID v4, required

**Request Body** (all fields optional):
```json
{
  "firstName": "Jane",
  "lastName": "Smith",
  "email": "jane.smith@pizzapalace.com",
  "phone": "+1-555-0124",
  "roles": ["employee"],
  "avatarUrl": "https://cdn.example.com/new-avatar.jpg",
  "preferences": {
    "theme": "light",
    "language": "es"
  }
}
```

**Response**: `200 OK` (Updated user object)

**Error Codes**:
- `400` - `VALIDATION_ERROR`: Invalid input data
- `401` - `AUTHENTICATION_REQUIRED`: Missing/invalid token
- `403` - `INSUFFICIENT_PERMISSIONS`: No permission to update user
- `404` - `USER_NOT_FOUND`: User doesn't exist
- `409` - `EMAIL_ALREADY_EXISTS`: Email taken in organization

### **PATCH /users/{id}/password**
Change user password.

**Headers**: `Authorization: Bearer <access-token>`

**Path Parameters**:
- `id`: UUID v4, required

**Request Body**:
```json
{
  "currentPassword": "CurrentPass123!",
  "newPassword": "NewSecurePass123!",
  "confirmPassword": "NewSecurePass123!"
}
```

**Response**: `200 OK`
```json
{
  "success": true,
  "data": null,
  "message": "Password changed successfully"
}
```

**Error Codes**:
- `400` - `VALIDATION_ERROR`: Invalid password format
- `400` - `PASSWORD_MISMATCH`: New password and confirmation don't match
- `400` - `SAME_PASSWORD`: New password same as current
- `401` - `AUTHENTICATION_REQUIRED`: Missing/invalid token
- `401` - `INVALID_CURRENT_PASSWORD`: Current password incorrect
- `403` - `INSUFFICIENT_PERMISSIONS`: No permission to change password
- `404` - `USER_NOT_FOUND`: User doesn't exist

### **PATCH /users/{id}/status**
Activate or deactivate user account.

**Headers**: `Authorization: Bearer <access-token>`

**Request Body**:
```json
{
  "isActive": false
}
```

**Response**: `200 OK` (Updated user object)

**Error Codes**:
- `401` - `AUTHENTICATION_REQUIRED`: Missing/invalid token
- `403` - `INSUFFICIENT_PERMISSIONS`: No permission to change status
- `404` - `USER_NOT_FOUND`: User doesn't exist

### **PATCH /users/{id}/verify-email**
Mark user email as verified.

**Headers**: `Authorization: Bearer <access-token>`

**Response**: `200 OK` (Updated user object)

### **PATCH /users/{id}/roles**
Update user roles.

**Headers**: `Authorization: Bearer <access-token>`

**Request Body**:
```json
{
  "roles": ["manager", "inventory_clerk"]
}
```

**Response**: `200 OK` (Updated user object)

### **DELETE /users/{id}**
Soft delete user (preserves data for audit).

**Headers**: `Authorization: Bearer <access-token>`

**Response**: `200 OK`
```json
{
  "success": true,
  "data": null,
  "message": "User deleted successfully"
}
```

### **GET /users/organization/{organizationId}/role/{role}**
Get users by role within organization.

**Headers**: `Authorization: Bearer <access-token>`

**Path Parameters**:
- `organizationId`: UUID v4, required
- `role`: String, required

**Response**: `200 OK` (Array of user objects)

---

## 🏢 **ORGANIZATION MANAGEMENT API**

### **POST /organizations**
Create a new organization.

**Headers**: `Authorization: Bearer <access-token>`

**Request Body**:
```json
{
  "name": "Pizza Palace Downtown",
  "slug": "pizza-palace-downtown",
  "email": "contact@pizzapalace.com",
  "phone": "+1-555-0123",
  "address": "123 Main St, Downtown, NY 10001",
  "taxNumber": "TAX123456789",
  "logoUrl": "https://cdn.example.com/logo.png",
  "website": "https://pizzapalace.com"
}
```

**Validation Rules**:
- `name`: String, 2-255 chars, required
- `slug`: String, 2-100 chars, lowercase/numbers/hyphens only, optional (auto-generated)
- `email`: Valid email, optional
- `phone`: String, 1-20 chars, optional
- `address`: String, 1-500 chars, optional
- `taxNumber`: String, 1-50 chars, optional
- `logoUrl`: Valid URL, optional
- `website`: Valid URL, optional

**Response**: `201 Created`
```json
{
  "success": true,
  "data": {
    "id": "org-uuid",
    "name": "Pizza Palace Downtown",
    "slug": "pizza-palace-downtown",
    "email": "contact@pizzapalace.com",
    "phone": "+1-555-0123",
    "address": "123 Main St, Downtown, NY 10001",
    "taxNumber": "TAX123456789",
    "subscriptionPlan": "basic",
    "subscriptionStatus": "active",
    "settings": {},
    "logoUrl": "https://cdn.example.com/logo.png",
    "website": "https://pizzapalace.com",
    "isActive": true,
    "createdAt": "2024-01-01T12:00:00Z",
    "updatedAt": "2024-01-01T12:00:00Z"
  },
  "message": "Organization created successfully"
}
```

**Error Codes**:
- `400` - `VALIDATION_ERROR`: Invalid input data
- `401` - `AUTHENTICATION_REQUIRED`: Missing/invalid token
- `403` - `INSUFFICIENT_PERMISSIONS`: No permission to create organizations
- `409` - `SLUG_ALREADY_EXISTS`: Slug is taken
- `409` - `ORGANIZATION_ALREADY_EXISTS`: Organization with info exists

### **GET /organizations**
Get paginated list of organizations.

**Headers**: `Authorization: Bearer <access-token>`

**Query Parameters**:
- `page`: Integer, min 1, default 1
- `limit`: Integer, min 1, max 100, default 10
- `sortBy`: String, default "createdAt"
- `sortOrder`: Enum ["ASC", "DESC"], default "DESC"

**Response**: `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": "org-uuid",
      "name": "Pizza Palace Downtown",
      "slug": "pizza-palace-downtown",
      "email": "contact@pizzapalace.com",
      "subscriptionPlan": "basic",
      "subscriptionStatus": "active",
      "isActive": true,
      "createdAt": "2024-01-01T00:00:00Z",
      "updatedAt": "2024-01-01T12:00:00Z"
    }
  ],
  "message": "Organizations retrieved successfully",
  "meta": {
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 5,
      "totalPages": 1
    }
  }
}
```

### **GET /organizations/{id}**
Get organization by ID.

**Headers**: `Authorization: Bearer <access-token>`

**Response**: `200 OK` (Full organization object)

### **GET /organizations/slug/{slug}**
Get organization by slug.

**Headers**: `Authorization: Bearer <access-token>`

**Response**: `200 OK` (Full organization object)

### **PATCH /organizations/{id}**
Update organization (partial update).

**Headers**: `Authorization: Bearer <access-token>`

**Request Body**: Same as create (all fields optional)

**Response**: `200 OK` (Updated organization object)

### **DELETE /organizations/{id}**
Soft delete organization.

**Headers**: `Authorization: Bearer <access-token>`

**Response**: `200 OK`
```json
{
  "success": true,
  "data": null,
  "message": "Organization deleted successfully"
}
```

### **GET /organizations/validate/slug/{slug}**
Validate slug availability.

**Query Parameters**:
- `excludeId`: UUID v4, optional (exclude from check)

**Response**: `200 OK`
```json
{
  "success": true,
  "data": {
    "available": true
  },
  "message": "Slug is available"
}
```

---

## 📊 **COMMON ERROR CODES**

### **Authentication Errors (401)**
- `AUTHENTICATION_REQUIRED`: Missing or invalid token
- `TOKEN_EXPIRED`: Access token has expired
- `INVALID_CREDENTIALS`: Wrong email/password combination
- `INVALID_REFRESH_TOKEN`: Refresh token invalid/expired
- `ACCOUNT_DEACTIVATED`: User account is disabled
- `ORGANIZATION_INACTIVE`: Organization is disabled

### **Authorization Errors (403)**
- `INSUFFICIENT_PERMISSIONS`: User lacks required permissions
- `ACCESS_DENIED`: Operation not allowed for user role

### **Validation Errors (400)**
- `VALIDATION_ERROR`: Input data validation failed
- `MISSING_REQUIRED_FIELD`: Required field not provided
- `INVALID_FORMAT`: Field format is incorrect
- `PASSWORD_MISMATCH`: Password confirmation doesn't match
- `SAME_PASSWORD`: New password same as current

### **Resource Errors (404)**
- `USER_NOT_FOUND`: User doesn't exist
- `ORGANIZATION_NOT_FOUND`: Organization doesn't exist
- `RESOURCE_NOT_FOUND`: Generic resource not found

### **Conflict Errors (409)**
- `EMAIL_ALREADY_EXISTS`: Email already taken
- `SLUG_ALREADY_EXISTS`: Slug already taken
- `RESOURCE_ALREADY_EXISTS`: Resource with data exists

### **Rate Limiting (429)**
- `RATE_LIMIT_EXCEEDED`: Too many requests

### **Server Errors (500)**
- `INTERNAL_SERVER_ERROR`: Unexpected server error
- `DATABASE_ERROR`: Database operation failed
- `EXTERNAL_SERVICE_ERROR`: External service unavailable

---

## 🔄 **PAGINATION STANDARD**

All paginated endpoints use consistent parameters:

**Query Parameters**:
- `page`: Page number (min: 1, default: 1)
- `limit`: Items per page (min: 1, max: 100, default: 10)
- `sortBy`: Sort field (default: "createdAt")
- `sortOrder`: Sort direction ("ASC" | "DESC", default: "DESC")

**Response Meta**:
```json
{
  "meta": {
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 100,
      "totalPages": 10
    }
  }
}
```

---

## 🔒 **AUTHENTICATION FLOW**

1. **Login**: `POST /auth/login` → Get access + refresh tokens
2. **API Calls**: Include `Authorization: Bearer <access-token>`
3. **Token Refresh**: `POST /auth/refresh` when access token expires
4. **Logout**: `POST /auth/logout` + client removes tokens

**Token Lifetimes**:
- Access Token: 24 hours
- Refresh Token: 7 days

---

## 📝 **CHANGELOG POLICY**

### **Version 1.0.0** (Current)
- Initial API release
- Authentication system
- User management
- Organization management
- Health checks

### **Future Versions**
- **v1.1.0**: Bug fixes and minor enhancements (backward compatible)
- **v2.0.0**: New features and breaking changes
- **v1.x**: Maintained for 2 years minimum

---

**🚨 CRITICAL REMINDER: v1 API is IMMUTABLE once published. All changes must go to v2.**