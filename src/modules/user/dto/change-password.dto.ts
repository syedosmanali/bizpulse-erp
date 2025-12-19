import { IsString, Length, Matches } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

/**
 * DTO for changing user password.
 * 
 * Why separate DTO:
 * - Password changes require current password verification
 * - Different validation rules than user creation
 * - Enhanced security through separate endpoint
 * - Audit trail for password changes
 */
export class ChangePasswordDto {
  @ApiProperty({
    description: 'Current password for verification',
    example: 'CurrentPass123!',
  })
  @IsString()
  currentPassword: string;

  @ApiProperty({
    description: 'New password (minimum 8 characters, must contain uppercase, lowercase, number, special character)',
    example: 'NewSecurePass123!',
    minLength: 8,
  })
  @IsString()
  @Length(8, 255, { message: 'New password must be at least 8 characters long' })
  @Matches(
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
    { 
      message: 'New password must contain at least one uppercase letter, one lowercase letter, one number, and one special character' 
    }
  )
  newPassword: string;

  @ApiProperty({
    description: 'Confirm new password (must match newPassword)',
    example: 'NewSecurePass123!',
  })
  @IsString()
  confirmPassword: string;
}