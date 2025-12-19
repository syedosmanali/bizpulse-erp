/**
 * JWT payload interface defining the structure of JWT token claims.
 * 
 * Why structured payload:
 * - Ensures consistent token structure across the application
 * - Provides type safety for JWT operations
 * - Enables easy access to user context in guards and decorators
 * - Supports role-based and permission-based authorization
 */
export interface JwtPayload {
  /** User unique identifier */
  sub: string; // Subject (user ID)
  
  /** User email address */
  email: string;
  
  /** Organization ID for multi-tenant context */
  organizationId: string;
  
  /** User roles for authorization */
  roles: string[];
  
  /** Token issued at timestamp */
  iat?: number;
  
  /** Token expiration timestamp */
  exp?: number;
  
  /** Token issuer */
  iss?: string;
  
  /** Token audience */
  aud?: string;
  
  /** Token type (access or refresh) */
  tokenType: 'access' | 'refresh';
}