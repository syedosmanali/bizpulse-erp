import {
  Controller,
  Post,
  Body,
  UseGuards,
  HttpStatus,
  Get,
} from '@nestjs/common';
import {
  ApiTags,
  ApiOperation,
  ApiBearerAuth,
} from '@nestjs/swagger';
import { AuthService } from '../services/auth.service';
import { LoginDto } from '../dto/login.dto';
import { RefreshTokenDto } from '../dto/refresh-token.dto';
import { AuthResponseDto } from '../dto/auth-response.dto';
import { LocalAuthGuard } from '../guards/local-auth.guard';
import { JwtAuthGuard } from '../guards/jwt-auth.guard';
import { Public } from '../decorators/public.decorator';
import { CurrentUser } from '../decorators/current-user.decorator';
import { User } from '../../user/entities/user.entity';
import { ApiStandardResponse, ApiErrorResponse } from '../../../common/decorators/api-response.decorator';
import { BaseResponse } from '../../../common/interfaces/base-response.interface';

/**
 * Authentication controller handles user authentication endpoints.
 * 
 * Why thin controllers:
 * - Controllers only handle HTTP request/response mapping
 * - All authentication logic is delegated to the service layer
 * - Enables easy testing without HTTP overhead
 * - Supports multiple interfaces (REST, GraphQL) to same auth logic
 * - Maintains clear separation of concerns
 */
@ApiTags('auth')
@Controller('auth')
export class AuthController {
  constructor(private readonly authService: AuthService) {}

  /**
   * User login endpoint with email/password authentication.
   */
  @Public() // This endpoint doesn't require authentication
  @UseGuards(LocalAuthGuard) // Uses local strategy for credential validation
  @Post('login')
  @ApiOperation({ 
    summary: 'User login',
    description: 'Authenticates user with email/password and returns JWT tokens'
  })
  @ApiStandardResponse(AuthResponseDto, HttpStatus.OK, 'Login successful')
  @ApiErrorResponse(HttpStatus.UNAUTHORIZED, 'Invalid credentials')
  @ApiErrorResponse(HttpStatus.BAD_REQUEST, 'Invalid input data')
  async login(@Body() loginDto: LoginDto): Promise<BaseResponse<AuthResponseDto>> {
    const authResponse = await this.authService.login(loginDto);
    
    return {
      success: true,
      data: authResponse,
      message: 'Login successful',
      meta: {
        timestamp: new Date().toISOString(),
      },
    };
  }

  /**
   * Token refresh endpoint for renewing access tokens.
   */
  @Public() // This endpoint doesn't require authentication (uses refresh token)
  @Post('refresh')
  @ApiOperation({ 
    summary: 'Refresh access token',
    description: 'Generates new access token using valid refresh token'
  })
  @ApiStandardResponse(AuthResponseDto, HttpStatus.OK, 'Token refreshed successfully')
  @ApiErrorResponse(HttpStatus.UNAUTHORIZED, 'Invalid refresh token')
  @ApiErrorResponse(HttpStatus.BAD_REQUEST, 'Invalid input data')
  async refresh(@Body() refreshTokenDto: RefreshTokenDto): Promise<BaseResponse<AuthResponseDto>> {
    const authResponse = await this.authService.refreshTokens(refreshTokenDto.refreshToken);
    
    return {
      success: true,
      data: authResponse,
      message: 'Token refreshed successfully',
      meta: {
        timestamp: new Date().toISOString(),
      },
    };
  }

  /**
   * Get current user profile information.
   */
  @UseGuards(JwtAuthGuard) // Requires valid JWT token
  @Get('me')
  @ApiBearerAuth()
  @ApiOperation({ 
    summary: 'Get current user profile',
    description: 'Returns authenticated user information'
  })
  @ApiStandardResponse(User, HttpStatus.OK, 'User profile retrieved successfully')
  @ApiErrorResponse(HttpStatus.UNAUTHORIZED, 'Authentication required')
  async getProfile(@CurrentUser() user: User): Promise<BaseResponse<User>> {
    return {
      success: true,
      data: user,
      message: 'User profile retrieved successfully',
      meta: {
        timestamp: new Date().toISOString(),
      },
    };
  }

  /**
   * User logout endpoint (client-side token invalidation).
   * Note: JWT tokens are stateless, so logout is handled client-side by removing tokens.
   * For enhanced security, implement token blacklisting in future iterations.
   */
  @UseGuards(JwtAuthGuard)
  @Post('logout')
  @ApiBearerAuth()
  @ApiOperation({ 
    summary: 'User logout',
    description: 'Logs out user (client should remove tokens)'
  })
  @ApiStandardResponse(null, HttpStatus.OK, 'Logout successful')
  @ApiErrorResponse(HttpStatus.UNAUTHORIZED, 'Authentication required')
  async logout(@CurrentUser() user: User): Promise<BaseResponse<null>> {
    // TODO: In future iterations, implement:
    // - Token blacklisting for enhanced security
    // - Audit log for logout events
    // - Notification to other sessions
    
    return {
      success: true,
      data: null,
      message: 'Logout successful. Please remove tokens from client storage.',
      meta: {
        timestamp: new Date().toISOString(),
      },
    };
  }

  /**
   * Token validation endpoint for client-side token verification.
   */
  @UseGuards(JwtAuthGuard)
  @Get('validate')
  @ApiBearerAuth()
  @ApiOperation({ 
    summary: 'Validate token',
    description: 'Validates current JWT token and returns user context'
  })
  @ApiStandardResponse(User, HttpStatus.OK, 'Token is valid')
  @ApiErrorResponse(HttpStatus.UNAUTHORIZED, 'Invalid or expired token')
  async validateToken(@CurrentUser() user: User): Promise<BaseResponse<{
    valid: boolean;
    user: User;
  }>> {
    return {
      success: true,
      data: {
        valid: true,
        user,
      },
      message: 'Token is valid',
      meta: {
        timestamp: new Date().toISOString(),
      },
    };
  }
}