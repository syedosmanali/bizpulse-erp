import { 
  Injectable, 
  NotFoundException, 
  ConflictException, 
  BadRequestException,
  UnauthorizedException 
} from '@nestjs/common';
import * as bcrypt from 'bcrypt';
import { UserRepository } from '../repositories/user.repository';
import { OrganizationService } from '../../organization/services/organization.service';
import { CreateUserDto } from '../dto/create-user.dto';
import { UpdateUserDto } from '../dto/update-user.dto';
import { ChangePasswordDto } from '../dto/change-password.dto';
import { User } from '../entities/user.entity';
import { PaginationParams } from '../../../common/interfaces/base-response.interface';

/**
 * User service contains all business logic for user management.
 * 
 * Why service layer:
 * - Encapsulates business rules and validation
 * - Handles password hashing and security concerns
 * - Manages cross-module dependencies (organization validation)
 * - Provides transaction management for complex operations
 * - Enables business logic reuse across different interfaces
 */
@Injectable()
export class UserService {
  private readonly saltRounds = 12; // bcrypt salt rounds for password hashing

  constructor(
    private readonly userRepository: UserRepository,
    private readonly organizationService: OrganizationService,
  ) {}

  /**
   * Creates a new user with business rule validation.
   * 
   * Business rules:
   * - Email must be unique within organization
   * - Organization must exist and be active
   * - Password must be securely hashed
   * - Default role is 'employee' if not specified
   */
  async create(createDto: CreateUserDto): Promise<User> {
    // Validate organization exists and is active
    const organization = await this.organizationService.findById(createDto.organizationId);
    if (!organization.isActive) {
      throw new BadRequestException('Cannot create user for inactive organization');
    }

    // Check email uniqueness within organization
    const existingUser = await this.userRepository.findByEmailAndOrganization(
      createDto.email,
      createDto.organizationId
    );
    if (existingUser) {
      throw new ConflictException('User with this email already exists in the organization');
    }

    // Hash password securely
    const hashedPassword = await bcrypt.hash(createDto.password, this.saltRounds);

    try {
      const user = await this.userRepository.create(createDto, hashedPassword);
      
      // TODO: In future iterations, add:
      // - Welcome email sending
      // - Email verification token generation
      // - Audit log creation
      // - Event publishing for other services
      
      return user;
    } catch (error) {
      // Handle database constraint violations
      if (error.code === '23505') { // PostgreSQL unique violation
        throw new ConflictException('User with this email already exists');
      }
      throw error;
    }
  }

  /**
   * Retrieves paginated users within an organization.
   */
  async findByOrganization(organizationId: string, params: PaginationParams = {}) {
    // Validate organization exists
    await this.organizationService.findById(organizationId);

    const { users, total } = await this.userRepository.findByOrganization(organizationId, params);
    
    const { page = 1, limit = 10 } = params;
    const totalPages = Math.ceil(total / limit);
    
    return {
      users,
      pagination: {
        page,
        limit,
        total,
        totalPages,
      },
    };
  }

  /**
   * Retrieves user by ID with existence validation.
   */
  async findById(id: string): Promise<User> {
    const user = await this.userRepository.findById(id);
    
    if (!user) {
      throw new NotFoundException(`User with ID '${id}' not found`);
    }
    
    return user;
  }

  /**
   * Retrieves user by email and organization for authentication.
   */
  async findByEmailAndOrganization(email: string, organizationId: string): Promise<User> {
    const user = await this.userRepository.findByEmailAndOrganization(email, organizationId);
    
    if (!user) {
      throw new NotFoundException('User not found');
    }
    
    return user;
  }

  /**
   * Updates user information with business rule validation.
   * 
   * Business rules:
   * - Cannot update email to existing one within organization
   * - Cannot change roles without proper permissions
   * - Certain fields may be restricted based on user role
   */
  async update(id: string, updateDto: UpdateUserDto): Promise<User> {
    const existingUser = await this.findById(id);

    // Validate email uniqueness if being updated
    if (updateDto.email && updateDto.email !== existingUser.email) {
      const emailExists = await this.userRepository.findByEmailAndOrganization(
        updateDto.email,
        existingUser.organizationId
      );
      if (emailExists) {
        throw new ConflictException('User with this email already exists in the organization');
      }
    }

    try {
      const updatedUser = await this.userRepository.update(id, updateDto);
      
      // TODO: In future iterations, add:
      // - Change notification emails
      // - Audit log creation
      // - Cache invalidation
      // - Event publishing for dependent services
      
      return updatedUser;
    } catch (error) {
      if (error.code === '23505') {
        throw new ConflictException('User with this information already exists');
      }
      throw error;
    }
  }

  /**
   * Changes user password with current password verification.
   * 
   * Security measures:
   * - Verifies current password before change
   * - Ensures new password confirmation matches
   * - Updates password change timestamp
   * - Hashes new password securely
   */
  async changePassword(id: string, changePasswordDto: ChangePasswordDto): Promise<void> {
    const { currentPassword, newPassword, confirmPassword } = changePasswordDto;

    // Verify new password confirmation
    if (newPassword !== confirmPassword) {
      throw new BadRequestException('New password and confirmation do not match');
    }

    // Get user with password for verification
    const user = await this.userRepository.findById(id);
    if (!user) {
      throw new NotFoundException('User not found');
    }

    // Verify current password
    const isCurrentPasswordValid = await bcrypt.compare(currentPassword, user.password);
    if (!isCurrentPasswordValid) {
      throw new UnauthorizedException('Current password is incorrect');
    }

    // Ensure new password is different from current
    const isSamePassword = await bcrypt.compare(newPassword, user.password);
    if (isSamePassword) {
      throw new BadRequestException('New password must be different from current password');
    }

    // Hash new password and update
    const hashedNewPassword = await bcrypt.hash(newPassword, this.saltRounds);
    await this.userRepository.updatePassword(id, hashedNewPassword);

    // TODO: In future iterations, add:
    // - Password change notification email
    // - Security audit log
    // - Force re-authentication on all devices
  }

  /**
   * Soft deletes user with dependency checks.
   * 
   * Business rules:
   * - Cannot delete user with pending transactions
   * - Cannot delete last admin user in organization
   * - Must transfer ownership of created records
   */
  async remove(id: string): Promise<void> {
    const user = await this.findById(id);

    // TODO: Add business rule validations:
    // - Check for pending transactions
    // - Ensure not last admin user
    // - Handle data ownership transfer
    
    const deleted = await this.userRepository.softDelete(id);
    
    if (!deleted) {
      throw new NotFoundException(`User with ID '${id}' not found`);
    }
    
    // TODO: In future iterations, add:
    // - Cleanup scheduled tasks
    // - Notification to user and admins
    // - Data export for compliance
    // - Event publishing for cleanup services
  }

  /**
   * Activates or deactivates user account.
   */
  async setActiveStatus(id: string, isActive: boolean): Promise<User> {
    await this.findById(id); // Verify exists
    
    const updated = await this.userRepository.setActiveStatus(id, isActive);
    
    if (!updated) {
      throw new NotFoundException(`User with ID '${id}' not found`);
    }
    
    return await this.findById(id);
  }

  /**
   * Verifies user email address.
   */
  async verifyEmail(id: string): Promise<User> {
    await this.findById(id); // Verify exists
    
    const updated = await this.userRepository.verifyEmail(id);
    
    if (!updated) {
      throw new NotFoundException(`User with ID '${id}' not found`);
    }
    
    return await this.findById(id);
  }

  /**
   * Updates user roles with permission validation.
   */
  async updateRoles(id: string, roles: string[]): Promise<User> {
    await this.findById(id); // Verify exists
    
    // TODO: Add role validation logic
    // - Verify roles exist in system
    // - Check permission to assign roles
    // - Validate role combinations
    
    const updated = await this.userRepository.updateRoles(id, roles);
    
    if (!updated) {
      throw new NotFoundException(`User with ID '${id}' not found`);
    }
    
    return await this.findById(id);
  }

  /**
   * Updates last login timestamp for security tracking.
   */
  async updateLastLogin(id: string): Promise<void> {
    await this.userRepository.updateLastLogin(id);
  }

  /**
   * Validates password for authentication.
   */
  async validatePassword(user: User, password: string): Promise<boolean> {
    return await bcrypt.compare(password, user.password);
  }

  /**
   * Finds users by role within organization.
   */
  async findByRole(organizationId: string, role: string): Promise<User[]> {
    return await this.userRepository.findByRole(organizationId, role);
  }
}