import { IsString, IsEmail, IsOptional, IsUrl, Length, Matches } from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

/**
 * DTO for creating a new organization.
 * 
 * Why strict validation:
 * - Prevents invalid data from entering the system
 * - Ensures data consistency across the application
 * - Provides clear error messages for API consumers
 * - Validates business rules at the API boundary
 */
export class CreateOrganizationDto {
  @ApiProperty({
    description: 'Organization name (restaurant/business name)',
    example: 'Pizza Palace Downtown',
    minLength: 2,
    maxLength: 255,
  })
  @IsString()
  @Length(2, 255, { message: 'Organization name must be between 2 and 255 characters' })
  name: string;

  @ApiProperty({
    description: 'Unique slug for URL-friendly identification (auto-generated if not provided)',
    example: 'pizza-palace-downtown',
    minLength: 2,
    maxLength: 100,
  })
  @IsOptional()
  @IsString()
  @Length(2, 100, { message: 'Slug must be between 2 and 100 characters' })
  @Matches(/^[a-z0-9-]+$/, { 
    message: 'Slug must contain only lowercase letters, numbers, and hyphens' 
  })
  slug?: string;

  @ApiPropertyOptional({
    description: 'Business email address',
    example: 'contact@pizzapalace.com',
  })
  @IsOptional()
  @IsEmail({}, { message: 'Please provide a valid email address' })
  email?: string;

  @ApiPropertyOptional({
    description: 'Business phone number',
    example: '+1-555-0123',
  })
  @IsOptional()
  @IsString()
  @Length(1, 20, { message: 'Phone number must be between 1 and 20 characters' })
  phone?: string;

  @ApiPropertyOptional({
    description: 'Business address',
    example: '123 Main St, Downtown, NY 10001',
  })
  @IsOptional()
  @IsString()
  @Length(1, 500, { message: 'Address must be between 1 and 500 characters' })
  address?: string;

  @ApiPropertyOptional({
    description: 'Tax identification number',
    example: 'TAX123456789',
  })
  @IsOptional()
  @IsString()
  @Length(1, 50, { message: 'Tax number must be between 1 and 50 characters' })
  taxNumber?: string;

  @ApiPropertyOptional({
    description: 'Organization logo URL',
    example: 'https://cdn.example.com/logos/pizza-palace.png',
  })
  @IsOptional()
  @IsUrl({}, { message: 'Please provide a valid URL for the logo' })
  logoUrl?: string;

  @ApiPropertyOptional({
    description: 'Organization website URL',
    example: 'https://pizzapalace.com',
  })
  @IsOptional()
  @IsUrl({}, { message: 'Please provide a valid URL for the website' })
  website?: string;
}