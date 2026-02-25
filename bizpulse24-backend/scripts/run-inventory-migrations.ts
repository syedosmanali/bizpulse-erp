/**
 * Script to run Inventory module database migrations
 * This script executes the SQL migration files for the Inventory module
 */

import { createClient } from '@supabase/supabase-js';
import * as fs from 'fs';
import * as path from 'path';
import * as dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
  console.error('❌ Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env file');
  process.exit(1);
}

// Create Supabase client with service role key
const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

/**
 * Execute a SQL migration file
 */
async function executeMigration(filePath: string): Promise<void> {
  const fileName = path.basename(filePath);
  console.log(`\n📄 Executing migration: ${fileName}`);

  try {
    // Read the SQL file
    const sql = fs.readFileSync(filePath, 'utf8');

    // Execute the SQL
    const { error } = await supabase.rpc('exec_sql', { sql_query: sql });

    if (error) {
      // If exec_sql function doesn't exist, try direct execution
      // Note: This requires the SQL to be split into individual statements
      console.log('⚠️  exec_sql function not available, attempting direct execution...');
      
      // Split SQL into statements (basic split on semicolons)
      const statements = sql
        .split(';')
        .map(s => s.trim())
        .filter(s => s.length > 0 && !s.startsWith('--'));

      for (const statement of statements) {
        const { error: stmtError } = await supabase.rpc('exec', { 
          query: statement + ';' 
        });
        
        if (stmtError) {
          throw stmtError;
        }
      }
    }

    console.log(`✅ Successfully executed: ${fileName}`);
  } catch (error) {
    console.error(`❌ Error executing ${fileName}:`, error);
    throw error;
  }
}

/**
 * Main migration runner
 */
async function runMigrations(): Promise<void> {
  console.log('🚀 Starting Inventory Module Migrations...\n');
  console.log('📍 Supabase URL:', SUPABASE_URL);

  const migrationsDir = path.join(__dirname, '..', 'prisma', 'migrations');

  // Migration files to run in order
  const migrationFiles = [
    '004_inventory_module.sql',
    '005_inventory_rls_policies.sql',
  ];

  try {
    for (const file of migrationFiles) {
      const filePath = path.join(migrationsDir, file);
      
      if (!fs.existsSync(filePath)) {
        console.error(`❌ Migration file not found: ${file}`);
        process.exit(1);
      }

      await executeMigration(filePath);
    }

    console.log('\n✅ All Inventory module migrations completed successfully!');
    console.log('\n📊 Created tables:');
    console.log('   - categories');
    console.log('   - brands');
    console.log('   - products');
    console.log('   - locations');
    console.log('   - stock');
    console.log('   - stock_ledger');
    console.log('   - stock_alerts');
    console.log('\n🔒 RLS policies applied to all Inventory tables');
    console.log('✨ Indexes created for optimal query performance');

  } catch (error) {
    console.error('\n❌ Migration failed:', error);
    process.exit(1);
  }
}

// Run migrations
runMigrations();
