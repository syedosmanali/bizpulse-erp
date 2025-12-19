import { ApiProperty } from '@nestjs/swagger';
import { User } from '../../user/entities/user.entity';

/**
 * DTO for authentication response containing tokens and user information.
 * 
 * Why separate response DTO:
 * - Standardizes authentication response format
 * - Excludes sensitive user information
 * - Provides clear API documentation
 * - Enables consistent token structure
 */
export class AuthResponseDto {
  @ApiProperty({
    description: 'JWT access token for API authentication',
    example: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
  })
  accessToken: string;

  @ApiProperty({
    description: 'JWT refresh token for token renewal',
    example: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
  })
  refreshToken: string;

  @ApiProperty({
    description: 'Token type (always Bearer)',
    example: 'Bearer',
  })
  tokenType: string;

  @ApiProperty({
    description: 'Access token expiration time in seconds',
    example: 86400,
  })
  expiresIn: number;

  @ApiProperty({
    description: 'Authenticated user information',
    type: User,
  })
  user: User;
}