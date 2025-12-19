import { Injectable, UnauthorizedException } from '@nestjs/common';
import { PassportStrategy } from '@nestjs/passport';
import { ConfigService } from '@nestjs/config';
import { ExtractJwt, Strategy } from 'passport-jwt';
import { UserService } from '../../user/services/user.service';
import { JwtPayload } from '../interfaces/jwt-payload.interface';
import { User } from '../../user/entities/user.entity';

/**
 * JWT strategy for validating JWT tokens in protected routes.
 * 
 * Why JWT strategy:
 * - Stateless authentication suitable for distributed systems
 * - Enables horizontal scaling without session storage
 * - Supports mobile and web clients equally
 * - Provides built-in token expiration and security
 * - Integrates seamlessly with NestJS guards
 */
@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
  constructor(
    private readonly configService: ConfigService,
    private readonly userService: UserService,
  ) {
    super({
      // Extract JWT from Authorization header as Bearer token
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      
      // Don't ignore token expiration - expired tokens are rejected
      ignoreExpiration: false,
      
      // Secret key for token verification
      secretOrKey: configService.get<string>('JWT_SECRET'),
      
      // Additional validation options
      algorithms: ['HS256'], // Only allow HMAC SHA-256 algorithm
      issuer: 'erp-backend', // Verify token issuer
      audience: 'erp-app', // Verify token audience
    });
  }

  /**
   * Validates JWT payload and returns user object.
   * This method is called automatically by Passport after JWT verification.
   * 
   * @param payload - Decoded JWT payload
   * @returns User object if valid, throws UnauthorizedException if invalid
   */
  async validate(payload: JwtPayload): Promise<User> {
    // Verify token type is access token
    if (payload.tokenType !== 'access') {
      throw new UnauthorizedException('Invalid token type');
    }

    try {
      // Fetch user from database to ensure account is still active
      const user = await this.userService.findById(payload.sub);
      
      // Additional security checks
      if (!user.isActive) {
        throw new UnauthorizedException('User account is deactivated');
      }
      
      if (!user.organization.isActive) {
        throw new UnauthorizedException('Organization is deactivated');
      }
      
      // Verify organization context matches token
      if (user.organizationId !== payload.organizationId) {
        throw new UnauthorizedException('Invalid organization context');
      }
      
      // Update last login timestamp for security tracking
      // Note: This is done asynchronously to avoid blocking the request
      this.userService.updateLastLogin(user.id).catch(() => {
        // Log error but don't fail the request
        console.error(`Failed to update last login for user ${user.id}`);
      });
      
      return user;
    } catch (error) {
      // User not found or other database errors
      throw new UnauthorizedException('Invalid token or user not found');
    }
  }
}