import { Injectable, ExecutionContext, UnauthorizedException } from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';
import { Reflector } from '@nestjs/core';

/**
 * JWT authentication guard that protects routes requiring authentication.
 * 
 * Why custom JWT guard:
 * - Extends Passport's AuthGuard with custom logic
 * - Supports public route decoration with @Public()
 * - Provides consistent error handling
 * - Enables role-based access control integration
 * - Supports custom authentication logic
 */
@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {
  constructor(private reflector: Reflector) {
    super();
  }

  /**
   * Determines if the current request should be authenticated.
   * 
   * @param context - Execution context containing request information
   * @returns boolean indicating if authentication is required
   */
  canActivate(context: ExecutionContext) {
    // Check if route is marked as public
    const isPublic = this.reflector.getAllAndOverride<boolean>('isPublic', [
      context.getHandler(),
      context.getClass(),
    ]);
    
    // Skip authentication for public routes
    if (isPublic) {
      return true;
    }
    
    // Proceed with JWT authentication
    return super.canActivate(context);
  }

  /**
   * Handles authentication errors with custom error messages.
   * 
   * @param err - Authentication error
   * @param user - User object (if authentication succeeded)
   * @param info - Additional authentication information
   * @returns User object or throws UnauthorizedException
   */
  handleRequest(err: any, user: any, info: any) {
    // Handle authentication errors
    if (err || !user) {
      // Provide specific error messages based on JWT errors
      if (info?.name === 'TokenExpiredError') {
        throw new UnauthorizedException('Token has expired');
      }
      
      if (info?.name === 'JsonWebTokenError') {
        throw new UnauthorizedException('Invalid token');
      }
      
      if (info?.name === 'NotBeforeError') {
        throw new UnauthorizedException('Token not active yet');
      }
      
      // Generic authentication error
      throw new UnauthorizedException('Authentication required');
    }
    
    return user;
  }
}