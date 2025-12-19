import { 
  IsString, 
  IsEmail, 
  IsOptional, 
  IsArray, 
  IsUUID, 
  Length, 
  Matches,
  IsUrl,
  ArrayNotEmpty,
  IsIn
} from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

/**
 * DTO for creating a new user.
 * 
 * Why strict validation:
 * - Ensures data integrity at the API boundary
 * - Prevents security vulnerabilities from malformed input
 * - Provides clear error messages for API consumers
 * - Validates business rules before reaching service layer
 */
export class CreateUserDto {
  @ApiProperty({
    description: 'User first name',
    example: 'John',
    minLength: 1,
    maxLength: 100,
  })
  @IsString()
  @Length(1, 100, { message: 'First name must be between 1 and 100 characters' })
  firstName: string;

  @ApiProperty({
    description: 'User last name',
    example: 'Doe',
    minLength: 1,
    maxLength: 100,
  })
  @IsString()
  @Length(1, 100, { message: 'Last name must be between 1 and 100 characters' })
  lastName: string;

  @ApiProperty({
    description: 'User email address (must be unique within organization)',
    example: 'john.doe@pizzapalace.com',
  })
  @IsEmail({}, { message: 'Please provide a valid email address' })
  email: string;

  @ApiPropertyOptional({
    description: 'User phone number',
    example: '+1-555-0123',
  })
  @IsOptional()
  @IsString()
  @Length(1, 20, { message: 'Phone number must be between 1 and 20 characters' })
  phone?: string;

  @ApiProperty({
    description: 'User password (minimum 8 characters, must contain uppercase, lowercase, number)',
    example: 'SecurePass123!',
    minLength: 8,
  })
  @IsString()
  @Length(8, 255, { message: 'Password must be at least 8 characters long' })
  @Matches(
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
    { 
      message: 'Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character' 
    }
  )
  password: string;

  @ApiProperty({
    description: 'Organization ID that the user belongs to',
    example: '123e4567-e89b-12d3-a456-426614174000',
  })
  @IsUUID(4, { message: 'Organization ID must be a valid UUID' })
  organizationId: string;

  @ApiPropertyOptional({
    description: 'User roles within the organization',
    example: ['manager', 'cashier'],
    type: [String],
  })
  @IsOptional()
  @IsArray()
  @ArrayNotEmpty({ message: 'At least one role must be specified' })
  @IsString({ each: true, message: 'Each role must be a string' })
  @IsIn(['admin', 'manager', 'employee', 'cashier', 'inventory_clerk'], { 
    each: true, 
    message: 'Role must be one of: admin, manager, employee, cashier, inventory_clerk' 
  })
  roles?: string[];

  @ApiPropertyOptional({
    description: 'User avatar/profile picture URL',
    example: 'https://cdn.example.com/avatars/john-doe.jpg',
  })
  @IsOptional()
  @IsUrl({}, { message: 'Avatar URL must be a valid URL' })
  avatarUrl?: string;

  @ApiPropertyOptional({
    description: 'User preferences and settings',
    example: { 
      theme: 'dark', 
      language: 'en',
      notifications: { email: true, push: false }
    },
  })
  @IsOptional()
  preferences?: Record<string, any>;
}