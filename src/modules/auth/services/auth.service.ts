import { Injectable, UnauthorizedException } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { ConfigService } from '@nestjs/config';
import { UserService } from '../../user/services/user.service';
import { User } from '../../user/entities/user.entity';
import { LoginDto } from '../dto/login.dto';
import { AuthResponseDto } from '../dto/auth-response.dto';
import { JwtPayload } from '../interfaces/jwt-payload.interface';

/**
 * Authentication service handles user authentication and JWT token management.
 * 
 * Why service layer for auth:
 * - Encapsulates authentication business logic
 * - Manages JWT token generation and validation
 * - Handles password verification securely
 * - Provides consistent authentication interface
 * - Enables authentication method switching (JWT, OAuth, etc.)
 */
@Injectable()
export class AuthService {
  constructor(
    private readonly userService: UserService,
    private readonly jwtService: JwtService,
    private readonly configService: ConfigService,
  ) {}

  /**
   * Validates user credentials for authentication.
   * 
   * @param email - User email address
   * @param password - User password
   * @param organizationId - Organization context
   * @returns User object if valid, null if invalid
   */
  async validateUser(email: string, password: string, organizationId: string): Promise<User | null> {
    try {
      // Find user by email and organization
      const user = await this.userService.findByEmailAndOrganization(email, organizationId);
      
      // Verify user account is active
      if (!user.isActive) {
        throw new UnauthorizedException('User account is deactivated');
      }
      
      // Verify organization is active
      if (!user.organization.isActive) {
        throw new UnauthorizedException('Organization is deactivated');
      }
      
      // Validate password
      const isPasswordValid = await this.userService.validatePassword(user, password);
      if (!isPasswordValid) {
        return null; // Invalid password
      }
      
      return user;
    } catch (error) {
      // User not found or other errors
      return null;
    }
  }

  /**
   * Authenticates user and generates JWT tokens.
   * 
   * @param loginDto - Login credentials
   * @returns Authentication response with tokens and user info
   */
  async login(loginDto: LoginDto): Promise<AuthResponseDto> {
    // Validate user credentials
    const user = await this.validateUser(loginDto.email, loginDto.password, loginDto.organizationId);
    
    if (!user) {
      throw new UnauthorizedException('Invalid email or password');
    }
    
    // Generate JWT tokens
    const tokens = await this.generateTokens(user);
    
    // Update last login timestamp
    await this.userService.updateLastLogin(user.id);
    
    return {
      ...tokens,
      user,
    };
  }

  /**
   * Refreshes access token using refresh token.
   * 
   * @param refreshToken - Valid refresh token
   * @returns New authentication response with fresh tokens
   */
  async refreshTokens(refreshToken: string): Promise<AuthResponseDto> {
    try {
      // Verify refresh token
      const payload = await this.jwtService.verifyAsync<JwtPayload>(refreshToken, {
        secret: this.configService.get<string>('JWT_REFRESH_SECRET'),
      });
      
      // Verify token type
      if (payload.tokenType !== 'refresh') {
        throw new UnauthorizedException('Invalid token type');
      }
      
      // Get user and verify account is still active
      const user = await this.userService.findById(payload.sub);
      
      if (!user.isActive || !user.organization.isActive) {
        throw new UnauthorizedException('User or organization is deactivated');
      }
      
      // Generate new tokens
      const tokens = await this.generateTokens(user);
      
      return {
        ...tokens,
        user,
      };
    } catch (error) {
      throw new UnauthorizedException('Invalid refresh token');
    }
  }

  /**
   * Generates access and refresh JWT tokens for user.
   * 
   * @param user - Authenticated user
   * @returns Token pair with expiration info
   */
  private async generateTokens(user: User): Promise<{
    accessToken: string;
    refreshToken: string;
    tokenType: string;
    expiresIn: number;
  }> {
    // Base payload for both tokens
    const basePayload: Omit<JwtPayload, 'tokenType'> = {
      sub: user.id,
      email: user.email,
      organizationId: user.organizationId,
      roles: user.roles,
      iss: 'erp-backend',
      aud: 'erp-app',
    };
    
    // Generate access token
    const accessTokenPayload: JwtPayload = {
      ...basePayload,
      tokenType: 'access',
    };
    
    const accessToken = await this.jwtService.signAsync(accessTokenPayload, {
      secret: this.configService.get<string>('JWT_SECRET'),
      expiresIn: this.configService.get<string>('JWT_EXPIRES_IN', '24h'),
    });
    
    // Generate refresh token
    const refreshTokenPayload: JwtPayload = {
      ...basePayload,
      tokenType: 'refresh',
    };
    
    const refreshToken = await this.jwtService.signAsync(refreshTokenPayload, {
      secret: this.configService.get<string>('JWT_REFRESH_SECRET'),
      expiresIn: this.configService.get<string>('JWT_REFRESH_EXPIRES_IN', '7d'),
    });
    
    // Calculate expiration time in seconds
    const expiresIn = this.parseExpirationTime(
      this.configService.get<string>('JWT_EXPIRES_IN', '24h')
    );
    
    return {
      accessToken,
      refreshToken,
      tokenType: 'Bearer',
      expiresIn,
    };
  }

  /**
   * Parses JWT expiration time string to seconds.
   * 
   * @param expiresIn - Expiration string (e.g., '24h', '7d', '3600s')
   * @returns Expiration time in seconds
   */
  private parseExpirationTime(expiresIn: string): number {
    const unit = expiresIn.slice(-1);
    const value = parseInt(expiresIn.slice(0, -1), 10);
    
    switch (unit) {
      case 's': return value;
      case 'm': return value * 60;
      case 'h': return value * 60 * 60;
      case 'd': return value * 60 * 60 * 24;
      default: return 86400; // Default to 24 hours
    }
  }

  /**
   * Validates JWT token and returns payload.
   * Used for token introspection and validation.
   * 
   * @param token - JWT token to validate
   * @returns JWT payload if valid
   */
  async validateToken(token: string): Promise<JwtPayload> {
    try {
      return await this.jwtService.verifyAsync<JwtPayload>(token, {
        secret: this.configService.get<string>('JWT_SECRET'),
      });
    } catch (error) {
      throw new UnauthorizedException('Invalid token');
    }
  }
}