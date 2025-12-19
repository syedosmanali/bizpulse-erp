import { Injectable, NotFoundException, ConflictException } from '@nestjs/common';
import { OrganizationRepository } from '../repositories/organization.repository';
import { CreateOrganizationDto } from '../dto/create-organization.dto';
import { UpdateOrganizationDto } from '../dto/update-organization.dto';
import { Organization } from '../entities/organization.entity';
import { PaginationParams } from '../../../common/interfaces/base-response.interface';

/**
 * Organization service contains all business logic for organization management.
 * 
 * Why service layer:
 * - Encapsulates business rules and validation logic
 * - Provides transaction management for complex operations
 * - Handles cross-cutting concerns (logging, caching, events)
 * - Enables business logic reuse across different controllers
 * - Maintains separation between HTTP concerns and business logic
 */
@Injectable()
export class OrganizationService {
  constructor(
    private readonly organizationRepository: OrganizationRepository,
  ) {}

  /**
   * Creates a new organization with business rule validation.
   * 
   * Business rules:
   * - Organization name must be unique within the system
   * - Slug must be unique and URL-friendly
   * - Default subscription plan is 'basic'
   * - Default status is 'active'
   */
  async create(createDto: CreateOrganizationDto): Promise<Organization> {
    // Validate slug uniqueness if provided
    if (createDto.slug) {
      const isSlugAvailable = await this.organizationRepository.isSlugAvailable(createDto.slug);
      if (!isSlugAvailable) {
        throw new ConflictException(`Slug '${createDto.slug}' is already taken`);
      }
    }

    try {
      const organization = await this.organizationRepository.create(createDto);
      
      // TODO: In future iterations, add:
      // - Welcome email sending
      // - Default settings initialization
      // - Audit log creation
      // - Event publishing for other services
      
      return organization;
    } catch (error) {
      // Handle database constraint violations
      if (error.code === '23505') { // PostgreSQL unique violation
        throw new ConflictException('Organization with this information already exists');
      }
      throw error;
    }
  }

  /**
   * Retrieves paginated list of organizations with filtering.
   */
  async findAll(params: PaginationParams = {}) {
    const { organizations, total } = await this.organizationRepository.findAll(params);
    
    const { page = 1, limit = 10 } = params;
    const totalPages = Math.ceil(total / limit);
    
    return {
      organizations,
      pagination: {
        page,
        limit,
        total,
        totalPages,
      },
    };
  }

  /**
   * Retrieves organization by ID with existence validation.
   */
  async findById(id: string): Promise<Organization> {
    const organization = await this.organizationRepository.findById(id);
    
    if (!organization) {
      throw new NotFoundException(`Organization with ID '${id}' not found`);
    }
    
    return organization;
  }

  /**
   * Retrieves organization by slug for public-facing URLs.
   */
  async findBySlug(slug: string): Promise<Organization> {
    const organization = await this.organizationRepository.findBySlug(slug);
    
    if (!organization) {
      throw new NotFoundException(`Organization with slug '${slug}' not found`);
    }
    
    return organization;
  }

  /**
   * Updates organization with business rule validation.
   * 
   * Business rules:
   * - Cannot update slug to an existing one
   * - Subscription changes require additional validation
   * - Certain fields may be restricted based on subscription plan
   */
  async update(id: string, updateDto: UpdateOrganizationDto): Promise<Organization> {
    // Verify organization exists
    await this.findById(id);
    
    // Validate slug uniqueness if being updated
    if (updateDto.slug) {
      const isSlugAvailable = await this.organizationRepository.isSlugAvailable(
        updateDto.slug,
        id,
      );
      if (!isSlugAvailable) {
        throw new ConflictException(`Slug '${updateDto.slug}' is already taken`);
      }
    }

    try {
      const updatedOrganization = await this.organizationRepository.update(id, updateDto);
      
      // TODO: In future iterations, add:
      // - Change notification emails
      // - Audit log creation
      // - Cache invalidation
      // - Event publishing for dependent services
      
      return updatedOrganization;
    } catch (error) {
      if (error.code === '23505') {
        throw new ConflictException('Organization with this information already exists');
      }
      throw error;
    }
  }

  /**
   * Soft deletes organization with dependency checks.
   * 
   * Business rules:
   * - Cannot delete organization with active users
   * - Cannot delete organization with pending transactions
   * - Must handle subscription cancellation
   */
  async remove(id: string): Promise<void> {
    // Verify organization exists
    await this.findById(id);
    
    // TODO: Add business rule validations:
    // - Check for active users
    // - Check for pending orders/transactions
    // - Handle subscription cancellation
    // - Archive related data
    
    const deleted = await this.organizationRepository.softDelete(id);
    
    if (!deleted) {
      throw new NotFoundException(`Organization with ID '${id}' not found`);
    }
    
    // TODO: In future iterations, add:
    // - Cleanup scheduled tasks
    // - Notification to organization admins
    // - Data export for compliance
    // - Event publishing for cleanup services
  }

  /**
   * Updates organization subscription status.
   * Used by billing service for subscription management.
   */
  async updateSubscriptionStatus(id: string, status: string): Promise<Organization> {
    await this.findById(id); // Verify exists
    
    const updated = await this.organizationRepository.updateSubscriptionStatus(id, status);
    
    if (!updated) {
      throw new NotFoundException(`Organization with ID '${id}' not found`);
    }
    
    return await this.findById(id);
  }

  /**
   * Validates slug availability for frontend validation.
   */
  async validateSlug(slug: string, excludeId?: string): Promise<boolean> {
    return await this.organizationRepository.isSlugAvailable(slug, excludeId);
  }
}