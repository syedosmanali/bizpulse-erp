import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { User } from './entities/user.entity';
import { UserController } from './controllers/user.controller';
import { UserService } from './services/user.service';
import { UserRepository } from './repositories/user.repository';
import { OrganizationModule } from '../organization/organization.module';

/**
 * User module encapsulates all user-related functionality.
 * 
 * Why module boundaries:
 * - Complete encapsulation of user domain logic
 * - Clear dependency management through imports/exports
 * - Enables lazy loading and code splitting
 * - Facilitates testing with isolated module setup
 * - Supports microservice extraction in the future
 */
@Module({
  imports: [
    // Register User entity with TypeORM for this module
    TypeOrmModule.forFeature([User]),
    
    // Import OrganizationModule to access OrganizationService
    // This creates a dependency: User module depends on Organization module
    // This is acceptable because users belong to organizations
    OrganizationModule,
  ],
  controllers: [
    // HTTP layer - handles requests and responses
    UserController,
  ],
  providers: [
    // Business logic layer
    UserService,
    // Data access layer
    UserRepository,
  ],
  exports: [
    // Export service for use by other modules (e.g., Auth module needs user validation)
    UserService,
    // Export repository for advanced use cases in other modules
    UserRepository,
  ],
})
export class UserModule {}