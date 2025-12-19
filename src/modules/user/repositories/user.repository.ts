import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, FindOptionsWhere } from 'typeorm';
import { User } from '../entities/user.entity';
import { CreateUserDto } from '../dto/create-user.dto';
import { UpdateUserDto } from '../dto/update-user.dto';
import { PaginationParams } from '../../../common/interfaces/base-response.interface';

/**
 * User repository handles all database operations for users.
 * 
 * Why repository pattern:
 * - Encapsulates database query logic
 * - Provides consistent interface for data access
 * - Enables easy mocking for unit tests
 * - Centralizes query optimization and caching
 * - Supports database-agnostic business logic
 */
@Injectable()
export class UserRepository {
  constructor(
    @InjectRepository(User)
    private readonly userRepository: Repository<User>,
  ) {}

  /**
   * Creates a new user with hashed password.
   */
  async create(createDto: CreateUserDto, hashedPassword: string): Promise<User> {
    const user = this.userRepository.create({
      ...createDto,
      password: hashedPassword,
      roles: createDto.roles || ['employee'], // Default role
    });
    
    return await this.userRepository.save(user);
  }

  /**
   * Finds all users within an organization with pagination.
   * Automatically excludes soft-deleted users.
   */
  async findByOrganization(
    organizationId: string,
    params: PaginationParams = {}
  ): Promise<{
    users: User[];
    total: number;
  }> {
    const { page = 1, limit = 10, sortBy = 'createdAt', sortOrder = 'DESC' } = params;
    
    const [users, total] = await this.userRepository.findAndCount({
      where: { organizationId } as FindOptionsWhere<User>,
      relations: ['organization'], // Include organization data
      order: { [sortBy]: sortOrder },
      skip: (page - 1) * limit,
      take: limit,
    });

    return { users, total };
  }

  /**
   * Finds user by ID with organization data.
   */
  async findById(id: string): Promise<User | null> {
    return await this.userRepository.findOne({
      where: { id } as FindOptionsWhere<User>,
      relations: ['organization'],
    });
  }

  /**
   * Finds user by email within specific organization.
   * Used for authentication and email uniqueness validation.
   */
  async findByEmailAndOrganization(email: string, organizationId: string): Promise<User | null> {
    return await this.userRepository.findOne({
      where: { 
        email, 
        organizationId 
      } as FindOptionsWhere<User>,
      relations: ['organization'],
    });
  }

  /**
   * Finds user by email across all organizations.
   * Used for global email uniqueness checks if required.
   */
  async findByEmail(email: string): Promise<User | null> {
    return await this.userRepository.findOne({
      where: { email } as FindOptionsWhere<User>,
      relations: ['organization'],
    });
  }

  /**
   * Updates user information excluding password.
   */
  async update(id: string, updateDto: UpdateUserDto): Promise<User | null> {
    await this.userRepository.update(id, updateDto);
    return await this.findById(id);
  }

  /**
   * Updates user password with timestamp tracking.
   */
  async updatePassword(id: string, hashedPassword: string): Promise<boolean> {
    const result = await this.userRepository.update(id, {
      password: hashedPassword,
      passwordChangedAt: new Date(),
    });
    return result.affected > 0;
  }

  /**
   * Updates last login timestamp for security tracking.
   */
  async updateLastLogin(id: string): Promise<boolean> {
    const result = await this.userRepository.update(id, {
      lastLoginAt: new Date(),
    });
    return result.affected > 0;
  }

  /**
   * Soft deletes user (sets deletedAt timestamp).
   */
  async softDelete(id: string): Promise<boolean> {
    const result = await this.userRepository.softDelete(id);
    return result.affected > 0;
  }

  /**
   * Activates or deactivates user account.
   */
  async setActiveStatus(id: string, isActive: boolean): Promise<boolean> {
    const result = await this.userRepository.update(id, { isActive });
    return result.affected > 0;
  }

  /**
   * Verifies user email address.
   */
  async verifyEmail(id: string): Promise<boolean> {
    const result = await this.userRepository.update(id, {
      isEmailVerified: true,
    });
    return result.affected > 0;
  }

  /**
   * Updates user roles for permission management.
   */
  async updateRoles(id: string, roles: string[]): Promise<boolean> {
    const result = await this.userRepository.update(id, { roles });
    return result.affected > 0;
  }

  /**
   * Updates user permissions for fine-grained access control.
   */
  async updatePermissions(id: string, permissions: Record<string, boolean>): Promise<boolean> {
    const result = await this.userRepository.update(id, { permissions });
    return result.affected > 0;
  }

  /**
   * Finds users by role within organization.
   * Used for role-based notifications and management.
   */
  async findByRole(organizationId: string, role: string): Promise<User[]> {
    return await this.userRepository
      .createQueryBuilder('user')
      .where('user.organizationId = :organizationId', { organizationId })
      .andWhere('user.roles @> :role', { role: JSON.stringify([role]) })
      .andWhere('user.isActive = :isActive', { isActive: true })
      .getMany();
  }

  /**
   * Counts active users in organization for billing purposes.
   */
  async countActiveUsers(organizationId: string): Promise<number> {
    return await this.userRepository.count({
      where: { 
        organizationId, 
        isActive: true 
      } as FindOptionsWhere<User>,
    });
  }
}