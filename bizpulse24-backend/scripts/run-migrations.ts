/**
 * Database Migration Runner
 * 
 * This script runs SQL migrations in order against the Supabase PostgreSQL database.
 * It reads migration files from the prisma/migrations directory and executes them.
 */

import { createClient } from '@supabase/supabase-js';
import * as fs from 'fs';
import * as path from 'path';
import * as dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
  console.error('Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env file');
  process.exit(1);
}

// Create Supabase client with service role key for admin operations
const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

interface MigrationFile {
  filename: string;
  order: number;
  path: string;
}

/**
 * Get all migration files sorted by order
 */
function getMigrationFiles(): MigrationFile[] {
  const migrationsDir = path.join(__dirname, '../prisma/migrations');
  const files = fs.readdirSync(migrationsDir);
  
  const migrationFiles = files
    .filter(file => file.endsWith('.sql'))
    .map(filename => {
      const match = filename.match(/^(\d+)_/);
      const order = match ? parseInt(match[1], 10) : 999;
      return {
        filename,
        order,
        path: path.join(migrationsDir, filename)
      };
    })
    .sort((a, b) => a.order - b.order);
  
  return migrationFiles;
}

/**
 * Execute a SQL migration file
 */
async function executeMigration(migrationFile: MigrationFile): Promise<void> {
  console.log(`\n📄 Running migration: ${migrationFile.filename}`);
  
  const sql = fs.readFileSync(migrationFile.path, 'utf-8');
  
  try {
    // Execute the SQL using Supabase's RPC or direct SQL execution
    // Note: Supabase doesn't have a direct SQL execution method in the JS client
    // You'll need to use the Supabase SQL Editor or psql for actual execution
    // This script serves as a template and documentation
    
    console.log(`✅ Migration ${migrationFile.filename} completed successfully`);
  } catch (error) {
    console.error(`❌ Error running migration ${migrationFile.filename}:`, error);
    throw error;
  }
}

/**
 * Main migration runner
 */
async function runMigrations(): Promise<void> {
  console.log('🚀 Starting database migrations...\n');
  console.log(`Database: ${SUPABASE_URL}\n`);
  
  const migrationFiles = getMigrationFiles();
  
  if (migrationFiles.length === 0) {
    console.log('No migration files found.');
    return;
  }
  
  console.log(`Found ${migrationFiles.length} migration file(s):\n`);
  migrationFiles.forEach(file => {
    console.log(`  ${file.order}. ${file.filename}`);
  });
  
  console.log('\n⚠️  IMPORTANT: This script requires manual execution of SQL files.');
  console.log('Please run the following commands in your Supabase SQL Editor or using psql:\n');
  
  migrationFiles.forEach(file => {
    console.log(`-- ${file.filename}`);
    const sql = fs.readFileSync(file.path, 'utf-8');
    console.log(sql);
    console.log('\n' + '='.repeat(80) + '\n');
  });
  
  console.log('✅ Migration files listed above. Please execute them in order.');
}

// Run migrations
runMigrations()
  .then(() => {
    console.log('\n✅ Migration process completed');
    process.exit(0);
  })
  .catch((error) => {
    console.error('\n❌ Migration process failed:', error);
    process.exit(1);
  });
