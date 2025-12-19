import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, FindOptionsWhere } from 'typeorm';
import { Organization } from '../entities/organization.entity';
import { CreateOrganizationDto } from '../dto/create-organization.dto';
import { UpdateOrganizationDto } from '../dto/update-organization.dto';
import { PaginationParams } from '../../../common/interfaces/base-response.interface';

/**
 * Organization repository handles all database operations for organizations.
 * 
 * Why repository pattern:
 * - Separates data access logic from business logic
 * - Enables easy testing with mock repositories
 * - Provides consistent interface for database operations
 * - Allows for database-agnostic business logic
 * - Centralizes query optimization and caching
 */
@Injectable()
export class OrganizationRepository {
  constructor(
    @InjectRepository(Organization)
    private readonly organizationRepository: Repository<Organization>,
  ) {}

  /**
   * Creates a new organization with automatic slug generation if not provided.
   */
  async create(createDto: CreateOrganizationDto): Promise<Organization> {
    // Generate slug from name if not provided
    if (!createDto.slug) {
      createDto.slug = this.generateSlug(createDto.name);
    }

    const organization = this.organizationRepository.create(createDto);
    return await this.organizationRepository.save(organization);
  }

  /**
   * Finds all organizations with pagination and soft delete filtering.
   */
  async findAll(params: PaginationParams = {}): Promise<{
    organizations: Organization[];
    total: number;
  }> {
    const { page = 1, limit = 10, sortBy = 'createdAt', sortOrder = 'DESC' } = params;
    
    const [organizations, total] = await this.organizationRepository.findAndCount({
      order: { [sortBy]: sortOrder },
      skip: (page - 1) * limit,
      take: limit,
      // Automatically excludes soft-deleted records
    });

    return { organizations, total };
  }

  /**
   * Finds organization by ID with error handling for not found cases.
   */
  async findById(id: string): Promise<Organization | null> {
    return await this.organizationRepository.findOne({
      where: { id } as FindOptionsWhere<Organization>,
    });
  }

  /**
   * Finds organization by slug for URL-based lookups.
   */
  async findBySlug(slug: string): Promise<Organization | null> {
    return await this.organizationRepository.findOne({
      where: { slug } as FindOptionsWhere<Organization>,
    });
  }

  /**
   * Updates organization with optimistic locking protection.
   */
  async update(id: string, updateDto: UpdateOrganizationDto): Promise<Organization | null> {
    await this.organizationRepository.update(id, updateDto);
    return await this.findById(id);
  }

  /**
   * Soft deletes organization (sets deletedAt timestamp).
   * Preserves data for audit trails and potential recovery.
   */
  async softDelete(id: string): Promise<boolean> {
    const result = await this.organizationRepository.softDelete(id);
    return result.affected > 0;
  }

  /**
   * Checks if slug is available for use (not taken by another organization).
   */
  async isSlugAvailable(slug: string, excludeId?: string): Promise<boolean> {
    const whereCondition: FindOptionsWhere<Organization> = { slug };
    
    if (excludeId) {
      // Exclude current organization when updating
      whereCondition.id = excludeId;
    }

    const existing = await this.organizationRepository.findOne({
      where: whereCondition,
    });

    return !existing;
  }

  /**
   * Generates URL-friendly slug from organization name.
   * Handles special characters and ensures uniqueness.
   */
  private generateSlug(name: string): string {
    return name
      .toLowerCase()
      .trim()
      .replace(/[^\w\s-]/g, '') // Remove special characters
      .replace(/[\s_-]+/g, '-') // Replace spaces and underscores with hyphens
      .replace(/^-+|-+$/g, ''); // Remove leading/trailing hyphens
  }

  /**
   * Finds organizations by subscription status for billing operations.
   */
  async findBySubscriptionStatus(status: string): Promise<Organization[]> {
    return await this.organizationRepository.find({
      where: { subscriptionStatus: status } as FindOptionsWhere<Organization>,
    });
  }

  /**
   * Updates subscription status for billing integration.
   */
  async updateSubscriptionStatus(id: string, status: string): Promise<boolean> {
    const result = await this.organizationRepository.update(id, {
      subscriptionStatus: status,
    });
    return result.affected > 0;
  }
}