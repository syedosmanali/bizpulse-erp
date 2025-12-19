import { createParamDecorator, ExecutionContext } from '@nestjs/common';
import { User } from '../../user/entities/user.entity';

/**
 * Current user decorator to inject authenticated user into controller methods.
 * 
 * Why current user decorator:
 * - Provides clean access to authenticated user in controllers
 * - Eliminates need to extract user from request object manually
 * - Improves type safety with User type annotation
 * - Enables consistent user access pattern across controllers
 */
export const CurrentUser = createParamDecorator(
  (data: unknown, ctx: ExecutionContext): User => {
    const request = ctx.switchToHttp().getRequest();
    
    // User is attached to request by JWT strategy after successful authentication
    return request.user;
  },
);