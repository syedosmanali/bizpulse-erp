# BizPulse24 ERP Backend - Setup Instructions

## Prerequisites

Before setting up the project, ensure you have the following installed:

- **Node.js**: Version 18.0.0 or higher
- **npm**: Version 9.0.0 or higher
- **PostgreSQL**: Supabase account with a project created

## Step 1: Install Dependencies

Run the setup script for your operating system:

### On Linux/Mac:
```bash
chmod +x setup.sh
./setup.sh
```

### On Windows:
```cmd
setup.bat
```

### Manual Installation:
```bash
npm install
```

## Step 2: Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and configure the following variables:

   ```env
   # Supabase Configuration
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

   # Database Configuration
   DATABASE_URL=postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
   ```

   You can find these values in your Supabase project settings:
   - Go to Settings > API
   - Copy the Project URL and anon/service_role keys
   - Go to Settings > Database
   - Copy the Connection String (URI format)

## Step 3: Generate Prisma Client

```bash
npm run prisma:generate
```

## Step 4: Run Database Migrations

```bash
npm run prisma:migrate
```

## Step 5: Start Development Server

```bash
npm run dev
```

The server will start on `http://localhost:3000`

## Verify Installation

Test the health endpoint:
```bash
curl http://localhost:3000/health
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

## Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm test` - Run tests
- `npm run test:watch` - Run tests in watch mode
- `npm run test:coverage` - Run tests with coverage report
- `npm run lint` - Lint code
- `npm run lint:fix` - Lint and fix code
- `npm run format` - Format code with Prettier
- `npm run prisma:generate` - Generate Prisma client
- `npm run prisma:migrate` - Run database migrations
- `npm run prisma:studio` - Open Prisma Studio

## Troubleshooting

### Issue: "Cannot find module" errors
**Solution**: Run `npm install` again

### Issue: Prisma client errors
**Solution**: Run `npm run prisma:generate`

### Issue: Database connection errors
**Solution**: Verify your DATABASE_URL in .env file

### Issue: Port already in use
**Solution**: Change PORT in .env file or stop the process using port 3000

## Next Steps

After successful setup:

1. Review the project structure in `README.md`
2. Explore the API endpoints documentation
3. Run the test suite to ensure everything works
4. Start implementing features according to the task list

## Support

For issues or questions, refer to:
- Project README.md
- Prisma documentation: https://www.prisma.io/docs
- Supabase documentation: https://supabase.com/docs
- Express.js documentation: https://expressjs.com
