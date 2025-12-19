import { Entity, Column, OneToMany } from 'typeorm';
import { ApiProperty } from '@nestjs/swagger';
import { BaseEntity } from '../../../common/entities/base.entity';
import { User } from '../../user/entities/user.entity';

/**
 * Organization entity represents a restaurant/business in the multi-tenant ERP system.
 * 
 * Why this design:
 * - Multi-tenancy: Each organization is completely isolated
 * - Subscription management: Tracks plan and billing status
 * - Settings flexibility: JSONB allows custom configuration per organization
 * - Audit trail: Inherits created/updated timestamps from BaseEntity
 */
@Entity('organizations')
export class Organization extends BaseEntity {
  @ApiProperty({ 
    description: 'Organization name (restaurant/business name)',
    example: 'Pizza Palace Downtown' 
  })
  @Column({ type: 'varchar', length: 255 })
  name: string;

  @ApiProperty({ 
    description: 'Unique slug for URL-friendly identification',
    example: 'pizza-palace-downtown' 
  })
  @Column({ type: 'varchar', length: 100, unique: true })
  slug: string;

  @ApiProperty({ 
    description: 'Business email address',
    example: 'contact@pizzapalace.com' 
  })
  @Column({ type: 'varchar', length: 255, nullable: true })
  email?: string;

  @ApiProperty({ 
    description: 'Business phone number',
    example: '+1-555-0123' 
  })
  @Column({ type: 'varchar', length: 20, nullable: true })
  phone?: string;

  @ApiProperty({ 
    description: 'Business address',
    example: '123 Main St, Downtown, NY 10001' 
  })
  @Column({ type: 'text', nullable: true })
  address?: string;

  @ApiProperty({ 
    description: 'Tax identification number',
    example: 'TAX123456789' 
  })
  @Column({ type: 'varchar', length: 50, nullable: true })
  taxNumber?: string;

  @ApiProperty({ 
    description: 'Subscription plan type',
    example: 'premium',
    enum: ['basic', 'premium', 'enterprise'] 
  })
  @Column({ 
    type: 'varchar', 
    length: 50, 
    default: 'basic',
    comment: 'Subscription plan: basic, premium, enterprise'
  })
  subscriptionPlan: string;

  @ApiProperty({ 
    description: 'Current subscription status',
    example: 'active',
    enum: ['active', 'suspended', 'cancelled'] 
  })
  @Column({ 
    type: 'varchar', 
    length: 20, 
    default: 'active',
    comment: 'Subscription status: active, suspended, cancelled'
  })
  subscriptionStatus: string;

  @ApiProperty({ 
    description: 'Organization-specific settings and configuration',
    example: { 
      currency: 'USD', 
      timezone: 'America/New_York',
      features: ['pos', 'inventory', 'reports']
    }
  })
  @Column({ 
    type: 'jsonb', 
    default: {},
    comment: 'Flexible settings storage for organization customization'
  })
  settings: Record<string, any>;

  @ApiProperty({ 
    description: 'Organization logo URL',
    example: 'https://cdn.example.com/logos/pizza-palace.png' 
  })
  @Column({ type: 'varchar', length: 500, nullable: true })
  logoUrl?: string;

  @ApiProperty({ 
    description: 'Organization website URL',
    example: 'https://pizzapalace.com' 
  })
  @Column({ type: 'varchar', length: 255, nullable: true })
  website?: string;

  @ApiProperty({ 
    description: 'Whether the organization is currently active',
    example: true 
  })
  @Column({ 
    type: 'boolean', 
    default: true,
    comment: 'Soft disable flag for organization suspension'
  })
  isActive: boolean;

  // Relationships

  /**
   * One-to-many relationship with users.
   * Each organization can have multiple users (employees, managers, etc.)
   */
  @OneToMany(() => User, (user) => user.organization)
  users: User[];
}