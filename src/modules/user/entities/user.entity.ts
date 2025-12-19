import { Entity, Column, ManyToOne, JoinColumn, Index } from 'typeorm';
import { ApiProperty } from '@nestjs/swagger';
import { Exclude } from 'class-transformer';
import { BaseEntity } from '../../../common/entities/base.entity';
import { Organization } from '../../organization/entities/organization.entity';

/**
 * User entity represents employees, managers, and administrators in the ERP system.
 * 
 * Why this design:
 * - Multi-tenant: Each user belongs to one organization
 * - Role-based: Supports multiple roles per user for flexible permissions
 * - Security: Password is excluded from serialization
 * - Audit: Tracks login activity and account status
 * - Performance: Indexed fields for common queries
 */
@Entity('users')
@Index(['organizationId', 'email'], { unique: true }) // Unique email per organization
@Index(['organizationId', 'isActive']) // Performance index for active user queries
export class User extends BaseEntity {
  @ApiProperty({ 
    description: 'User first name',
    example: 'John' 
  })
  @Column({ type: 'varchar', length: 100 })
  firstName: string;

  @ApiProperty({ 
    description: 'User last name',
    example: 'Doe' 
  })
  @Column({ type: 'varchar', length: 100 })
  lastName: string;

  @ApiProperty({ 
    description: 'User email address (unique per organization)',
    example: 'john.doe@pizzapalace.com' 
  })
  @Column({ type: 'varchar', length: 255 })
  email: string;

  @ApiProperty({ 
    description: 'User phone number',
    example: '+1-555-0123' 
  })
  @Column({ type: 'varchar', length: 20, nullable: true })
  phone?: string;

  /**
   * Password field is excluded from serialization for security.
   * Always use bcrypt hashing before storing.
   */
  @Exclude()
  @Column({ type: 'varchar', length: 255 })
  password: string;

  @ApiProperty({ 
    description: 'User roles within the organization',
    example: ['manager', 'cashier'],
    type: [String]
  })
  @Column({ 
    type: 'jsonb', 
    default: ['employee'],
    comment: 'Array of role names for flexible permission management'
  })
  roles: string[];

  @ApiProperty({ 
    description: 'User permissions (can override role permissions)',
    example: { 
      'products:read': true, 
      'orders:create': true,
      'reports:financial': false 
    }
  })
  @Column({ 
    type: 'jsonb', 
    default: {},
    comment: 'Specific permissions that override role-based permissions'
  })
  permissions: Record<string, boolean>;

  @ApiProperty({ 
    description: 'Whether the user account is active',
    example: true 
  })
  @Column({ 
    type: 'boolean', 
    default: true,
    comment: 'Soft disable flag for user suspension'
  })
  isActive: boolean;

  @ApiProperty({ 
    description: 'Whether the user email is verified',
    example: true 
  })
  @Column({ 
    type: 'boolean', 
    default: false,
    comment: 'Email verification status for security'
  })
  isEmailVerified: boolean;

  @ApiProperty({ 
    description: 'Last login timestamp',
    example: '2024-01-01T12:00:00Z' 
  })
  @Column({ 
    type: 'timestamp with time zone', 
    nullable: true,
    comment: 'Tracks user activity for security and analytics'
  })
  lastLoginAt?: Date;

  @ApiProperty({ 
    description: 'Password last changed timestamp',
    example: '2024-01-01T12:00:00Z' 
  })
  @Column({ 
    type: 'timestamp with time zone', 
    nullable: true,
    comment: 'Tracks password changes for security policies'
  })
  passwordChangedAt?: Date;

  @ApiProperty({ 
    description: 'User avatar/profile picture URL',
    example: 'https://cdn.example.com/avatars/john-doe.jpg' 
  })
  @Column({ type: 'varchar', length: 500, nullable: true })
  avatarUrl?: string;

  @ApiProperty({ 
    description: 'User preferences and settings',
    example: { 
      theme: 'dark', 
      language: 'en',
      notifications: { email: true, push: false }
    }
  })
  @Column({ 
    type: 'jsonb', 
    default: {},
    comment: 'User-specific settings and preferences'
  })
  preferences: Record<string, any>;

  // Relationships

  /**
   * Organization ID for multi-tenant data isolation.
   * Every user must belong to exactly one organization.
   */
  @ApiProperty({ 
    description: 'Organization ID (UUID)',
    example: '123e4567-e89b-12d3-a456-426614174000' 
  })
  @Column({ type: 'uuid' })
  organizationId: string;

  /**
   * Many-to-one relationship with Organization.
   * Enables user queries with organization data.
   */
  @ManyToOne(() => Organization, (organization) => organization.users, {
    onDelete: 'CASCADE', // Delete users when organization is deleted
  })
  @JoinColumn({ name: 'organizationId' })
  organization: Organization;

  // Virtual properties for API responses

  /**
   * Full name computed property for display purposes.
   */
  @ApiProperty({ 
    description: 'User full name',
    example: 'John Doe' 
  })
  get fullName(): string {
    return `${this.firstName} ${this.lastName}`.trim();
  }

  /**
   * Check if user has a specific role.
   */
  hasRole(role: string): boolean {
    return this.roles.includes(role);
  }

  /**
   * Check if user has a specific permission.
   * Checks both role-based and explicit permissions.
   */
  hasPermission(permission: string): boolean {
    // Explicit permission override
    if (this.permissions.hasOwnProperty(permission)) {
      return this.permissions[permission];
    }
    
    // TODO: Implement role-based permission checking
    // This would require a role definition system
    return false;
  }
}