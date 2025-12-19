import { IsEmail, IsString, IsUUID, Length } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

/**
 * DTO for user login authentication.
 * 
 * Why organization-scoped login:
 * - Multi-tenant architecture requires organization context
 * - Same email can exist in different organizations
 * - Enables organization-specific authentication policies
 * - Supports subdomain-based organization routing
 */
export class LoginDto {
  @ApiProperty({
    description: 'User email address',
    example: 'john.doe@pizzapalace.com',
  })
  @IsEmail({}, { message: 'Please provide a valid email address' })
  email: string;

  @ApiProperty({
    description: 'User password',
    example: 'SecurePass123!',
  })
  @IsString()
  @Length(1, 255, { message: 'Password is required' })
  password: string;

  @ApiProperty({
    description: 'Organization ID for multi-tenant authentication',
    example: '123e4567-e89b-12d3-a456-426614174000',
  })
  @IsUUID(4, { message: 'Organization ID must be a valid UUID' })
  organizationId: string;
}