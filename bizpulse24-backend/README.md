# BizPulse24 ERP Backend

Production-ready ERP backend system for Indian retail businesses built with Node.js, TypeScript, Express.js, Prisma ORM, and Supabase PostgreSQL.

## Features

- Inventory Management
- Sales and Billing (POS)
- Purchase Management
- Party Management (Customers & Vendors)
- Financial Accounting
- GST Compliance
- Comprehensive Reporting
- Multi-user with Role-Based Access Control
- Event-Driven Architecture
- Audit Logging

## Technology Stack

- **Runtime**: Node.js 18+
- **Language**: TypeScript
- **Framework**: Express.js
- **Database**: Supabase PostgreSQL
- **ORM**: Prisma
- **Authentication**: Supabase Auth (JWT)
- **Testing**: Jest, fast-check
- **Code Quality**: ESLint, Prettier

## Project Structure

```
bizpulse24-backend/
├── src/
│   ├── api/          # Express route handlers
│   ├── services/     # Business logic and transaction orchestration
│   ├── engines/      # GST, Ledger, Audit engines
│   ├── models/       # TypeScript interfaces and types
│   ├── middleware/   # Express middleware
│   ├── utils/        # Utility functions
│   └── tests/        # Unit and property-based tests
├── prisma/
│   └── schema.prisma # Database schema
└── dist/             # Compiled JavaScript output
```

## Getting Started

### Prerequisites

- Node.js 18 or higher
- npm 9 or higher
- PostgreSQL database (Supabase)

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Configure your .env file with Supabase credentials

# Generate Prisma client
npm run prisma:generate

# Run database migrations
npm run prisma:migrate
```

### Development

```bash
# Start development server with hot reload
npm run dev

# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Lint code
npm run lint

# Format code
npm run format
```

### Build and Production

```bash
# Build for production
npm run build

# Start production server
npm start
```

## API Documentation

API endpoints are organized by module:

- `/api/v1/inventory` - Product catalog, stock management
- `/api/v1/sales` - Invoices, POS billing, returns
- `/api/v1/purchase` - Purchase orders, GRN, returns
- `/api/v1/finance` - Payments, expenses, ledgers
- `/api/v1/parties` - Customers and vendors
- `/api/v1/reports` - GST and financial reports
- `/api/v1/company` - Company profile and configuration

## Environment Variables

See `.env.example` for required environment variables.

## License

MIT
