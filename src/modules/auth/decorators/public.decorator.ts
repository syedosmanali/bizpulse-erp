import { SetMetadata } from '@nestjs/common';

/**
 * Public decorator to mark routes that don't require authentication.
 * 
 * Why public decorator:
 * - Provides clean way to exclude routes from global authentication
 * - Enables selective authentication on controller methods
 * - Improves code readability and maintainability
 * - Supports mixed public/private endpoints in same controller
 */
export const IS_PUBLIC_KEY = 'isPublic';

/**
 * Marks a route as public (no authentication required).
 * 
 * Usage:
 * @Public()
 * @Get('health')
 * healthCheck() { ... }
 */
export const Public = () => SetMetadata(IS_PUBLIC_KEY, true);