import { Injectable, UnauthorizedException } from '@nestjs/common';
import { PassportStrategy } from '@nestjs/passport';
import { Strategy } from 'passport-local';
import { AuthService } from '../services/auth.service';
import { User } from '../../user/entities/user.entity';

/**
 * Local strategy for username/password authentication.
 * 
 * Why local strategy:
 * - Handles traditional email/password login
 * - Integrates with Passport.js ecosystem
 * - Provides consistent authentication interface
 * - Enables easy switching between authentication methods
 * - Supports custom validation logic
 */
@Injectable()
export class LocalStrategy extends PassportStrategy(Strategy) {
  constructor(private readonly authService: AuthService) {
    super({
      // Use email instead of username
      usernameField: 'email',
      passwordField: 'password',
      
      // Pass the entire request to validate method
      // This allows access to organizationId from request body
      passReqToCallback: true,
    });
  }

  /**
   * Validates user credentials during login.
   * This method is called automatically by Passport during authentication.
   * 
   * @param request - HTTP request object containing organizationId
   * @param email - User email address
   * @param password - User password
   * @returns User object if valid, throws UnauthorizedException if invalid
   */
  async validate(request: any, email: string, password: string): Promise<User> {
    // Extract organizationId from request body
    const organizationId = request.body?.organizationId;
    
    if (!organizationId) {
      throw new UnauthorizedException('Organization ID is required');
    }

    try {
      // Validate user credentials through auth service
      const user = await this.authService.validateUser(email, password, organizationId);
      
      if (!user) {
        throw new UnauthorizedException('Invalid credentials');
      }
      
      return user;
    } catch (error) {
      // Re-throw UnauthorizedException or wrap other errors
      if (error instanceof UnauthorizedException) {
        throw error;
      }
      
      throw new UnauthorizedException('Authentication failed');
    }
  }
}