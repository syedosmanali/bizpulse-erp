import { Injectable, UnauthorizedException } from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';

/**
 * Local authentication guard for login endpoints.
 * 
 * Why separate local guard:
 * - Handles username/password authentication specifically
 * - Provides custom error handling for login failures
 * - Integrates with local strategy for credential validation
 * - Enables consistent authentication flow
 */
@Injectable()
export class LocalAuthGuard extends AuthGuard('local') {
  /**
   * Handles authentication errors during login.
   * 
   * @param err - Authentication error
   * @param user - User object (if authentication succeeded)
   * @param info - Additional authentication information
   * @returns User object or throws UnauthorizedException
   */
  handleRequest(err: any, user: any, info: any) {
    // Handle authentication errors
    if (err || !user) {
      // Provide generic error message for security
      // Don't reveal whether email exists or password is wrong
      throw new UnauthorizedException('Invalid email or password');
    }
    
    return user;
  }
}