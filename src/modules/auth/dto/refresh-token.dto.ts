import { IsString, IsNotEmpty } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

/**
 * DTO for token refresh requests.
 * 
 * Why separate refresh endpoint:
 * - Enables secure token renewal without re-authentication
 * - Supports long-lived sessions with short-lived access tokens
 * - Allows for token rotation security strategy
 * - Provides better user experience (no frequent logins)
 */
export class RefreshTokenDto {
  @ApiProperty({
    description: 'JWT refresh token',
    example: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
  })
  @IsString()
  @IsNotEmpty({ message: 'Refresh token is required' })
  refreshToken: string;
}