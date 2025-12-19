import { PartialType, OmitType } from '@nestjs/swagger';
import { CreateUserDto } from './create-user.dto';

/**
 * DTO for updating an existing user.
 * 
 * Why omit certain fields:
 * - organizationId: Users cannot change organizations after creation
 * - password: Password updates should use a separate endpoint for security
 * - Other fields inherit validation from CreateUserDto but become optional
 */
export class UpdateUserDto extends PartialType(
  OmitType(CreateUserDto, ['password', 'organizationId'] as const)
) {}