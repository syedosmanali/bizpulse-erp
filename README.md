# ERP Backend Foundation

A production-ready ERP backend built with Node.js, NestJS, and PostgreSQL following clean architecture principles.

## 🏗️ Architecture Overview

This backend follows **Clean Architecture** with strict module boundaries:

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
│  Controllers (HTTP) → Services (Business Logic) → Repos    │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                     │
│  Services contain ALL business rules and validation         │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                    DATA ACCESS LAYER                        │
│  Repositories handle database operations only               │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Features

### ✅ Implemented Modules
- **Health Check API** - System monitoring and health endpoints
- **Authentication Module** - JWT-based auth with refresh tokens
- **User Module** - Complete user management with RBAC
- **Organization Module** - Multi-tenant restaurant/business management

### 🔐 Security Features
- JWT authentication with access/refresh tokens
- Password hashing with bcrypt (12 salt rounds)
- Multi-tenant data isolation
- Role-based access control (RBAC)
- Input validation with class-validator
- SQL injection prevention with TypeORM

### 📊 Database Design
- PostgreSQL with TypeORM
- Multi-tenant architecture (organization-scoped data)
- Soft deletes for audit trails
- UUID primary keys for security
- Proper indexing for performance
- JSONB fields for flexible settings

## 🛠️ Tech Stack

- **Runtime**: Node.js 18+
- **Framework**: NestJS 10
- **Database**: PostgreSQL 14+
- **ORM**: TypeORM 0.3
- **Authentication**: JWT with Passport.js
- **Validation**: class-validator + class-transformer
- **Documentation**: Swagger/OpenAPI
- **Testing**: Jest

## 📁 Project Structure

```
src/
├── config/                    # Configuration modules
│   └── database.module.ts     # Database configuration
├── common/                    # Shared utilities
│   ├── decorators/           # Custom decorators
│   ├── entities/             # Base entity classes
│   └── interfaces/           # Common interfaces
├── modules/                  # Business modules
│   ├── auth/                 # Authentication module
│   │   ├── controllers/      # HTTP controllers
│   │   ├── services/         # Business logic
│   │   ├── strategies/       # Passport strategies
│   │   ├── guards/           # Auth guards
│   │   ├── decorators/       # Auth decorators
│   │   └── dto/              # Data transfer objects
│   ├── user/                 # User management module
│   │   ├── controllers/      # User HTTP endpoints
│   │   ├── services/         # User business logic
│   │   ├── repositories/     # User data access
│   │   ├── entities/         # User database model
│   │   └── dto/              # User DTOs
│   ├── organization/         # Organization module
│   │   ├── controllers/      # Organization endpoints
│   │   ├── services/         # Organization logic
│   │   ├── repositories/     # Organization data access
│   │   ├── entities/         # Organization model
│   │   └── dto/              # Organization DTOs
│   └── health/               # Health check module
├── app.module.ts             # Root application module
└── main.ts                   # Application bootstrap
```

## 🚦 Getting Started

### Prerequisites
- Node.js 18+ and npm
- PostgreSQL 14+
- Git

### Installation

1. **Clone and install dependencies**
```bash
git clone <repository-url>
cd erp-backend-foundation
npm install
```

2. **Environment setup**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

3. **Database setup**
```bash
# Create PostgreSQL database
createdb erp_database

# Run migrations (auto-sync in development)
npm run start:dev
```

4. **Start development server**
```bash
npm run start:dev
```

## 📚 API Documentation

Once running, access the interactive API documentation:
- **Swagger UI**: http://localhost:3000/docs
- **Health Check**: http://localhost:3000/api/v1/health

## 🔑 Authentication Flow

### 1. Login
```bash
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "organizationId": "uuid-here"
}
```

### 2. Use Access Token
```bash
GET /api/v1/auth/me
Authorization: Bearer <access-token>
```

### 3. Refresh Token
```bash
POST /api/v1/auth/refresh
{
  "refreshToken": "<refresh-token>"
}
```

## 🏢 Multi-Tenant Architecture

Each organization is completely isolated:
- Users belong to one organization
- Data is scoped by `organizationId`
- Authentication requires organization context
- Database queries automatically filter by organization

## 🧪 Testing

```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e

# Test coverage
npm run test:cov
```

## 📦 Available Scripts

```bash
npm run start:dev      # Development server with hot reload
npm run start:prod     # Production server
npm run build          # Build for production
npm run lint           # ESLint code checking
npm run format         # Prettier code formatting
```

## 🔒 Security Best Practices

### Implemented
- ✅ JWT tokens with expiration
- ✅ Password hashing with bcrypt
- ✅ Input validation and sanitization
- ✅ SQL injection prevention
- ✅ Multi-tenant data isolation
- ✅ CORS configuration
- ✅ Rate limiting ready

### TODO (Future Iterations)
- [ ] Token blacklisting for logout
- [ ] Rate limiting implementation
- [ ] API key authentication
- [ ] OAuth2 integration
- [ ] Audit logging
- [ ] Email verification

## 🚀 Deployment

### Environment Variables
```bash
NODE_ENV=production
PORT=3000
DB_HOST=your-db-host
DB_PORT=5432
DB_USERNAME=your-db-user
DB_PASSWORD=your-db-password
DB_NAME=your-db-name
JWT_SECRET=your-super-secret-key
JWT_REFRESH_SECRET=your-refresh-secret
```

### Production Checklist
- [ ] Set strong JWT secrets
- [ ] Configure database connection pooling
- [ ] Enable HTTPS
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline

## 🤝 Contributing

1. Follow the established architecture patterns
2. Write tests for new features
3. Update documentation
4. Follow the code style (ESLint + Prettier)
5. Create meaningful commit messages

## 📋 Module Development Guidelines

### Creating New Modules
1. **Follow the pattern**: Controller → Service → Repository
2. **No business logic in controllers** - only HTTP handling
3. **Services contain all business rules** and validation
4. **Repositories handle database operations** only
5. **Use DTOs for input validation** with class-validator
6. **Export services** for use by other modules
7. **Write comprehensive tests** for each layer

### Module Independence
- Each module should be **completely independent**
- Import other modules only through their **exported services**
- **No direct database access** from other modules
- **No circular dependencies** between modules

## 🎯 Next Steps

Ready to add more modules? Follow the established patterns:

1. **Inventory Module** - Product and stock management
2. **Sales Module** - Orders and transactions
3. **Billing Module** - Invoicing and payments
4. **Reports Module** - Analytics and reporting

Each module should follow the same clean architecture principles demonstrated in the existing modules.

---

**Built with ❤️ for production-ready ERP systems**