import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Organization } from './entities/organization.entity';
import { OrganizationController } from './controllers/organization.controller';
import { OrganizationService } from './services/organization.service';
import { OrganizationRepository } from './repositories/organization.repository';

/**
 * Organization module encapsulates all organization-related functionality.
 * 
 * Why module boundaries:
 * - Complete encapsulation of organization domain logic
 * - Clear dependency management through imports/exports
 * - Enables lazy loading and code splitting
 * - Facilitates testing with isolated module setup
 * - Supports microservice extraction in the future
 */
@Module({
  imports: [
    // Register Organization entity with TypeORM for this module
    TypeOrmModule.forFeature([Organization]),
  ],
  controllers: [
    // HTTP layer - handles requests and responses
    OrganizationController,
  ],
  providers: [
    // Business logic layer
    OrganizationService,
    // Data access layer
    OrganizationRepository,
  ],
  exports: [
    // Export service for use by other modules (e.g., User module needs organization validation)
    OrganizationService,
    // Export repository for advanced use cases in other modules
    OrganizationRepository,
  ],
})
export class OrganizationModule {}