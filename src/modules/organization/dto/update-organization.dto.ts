import { PartialType } from '@nestjs/swagger';
import { CreateOrganizationDto } from './create-organization.dto';

/**
 * DTO for updating an existing organization.
 * 
 * Why PartialType:
 * - Inherits all validation rules from CreateOrganizationDto
 * - Makes all fields optional for partial updates
 * - Maintains type safety and validation consistency
 * - Reduces code duplication between create and update operations
 */
export class UpdateOrganizationDto extends PartialType(CreateOrganizationDto) {}