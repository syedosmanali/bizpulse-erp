import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';

// Core modules
import { DatabaseModule } from './config/database.module';
import { HealthModule } from './modules/health/health.module';

// Business modules - each module is completely independent
import { AuthModule } from './modules/auth/auth.module';
import { UserModule } from './modules/user/user.module';
import { OrganizationModule } from './modules/organization/organization.module';

/**
 * Root application module that orchestrates all feature modules.
 * 
 * Why this structure:
 * - ConfigModule.forRoot() loads environment variables globally
 * - DatabaseModule encapsulates all database configuration
 * - Each business module is imported independently for loose coupling
 * - Health module provides monitoring capabilities for production
 */
@Module({
  imports: [
    // Global configuration - loads .env files and validates environment variables
    ConfigModule.forRoot({
      isGlobal: true, // Makes ConfigService available throughout the application
      envFilePath: ['.env.local', '.env'], // Load local overrides first
      cache: true, // Cache configuration for performance
    }),

    // Database configuration module
    DatabaseModule,

    // Core system modules
    HealthModule,

    // Business domain modules - strict boundaries, no cross-dependencies
    AuthModule,
    UserModule,
    OrganizationModule,
  ],
})
export class AppModule {}