import { SupabaseClient, User } from '@supabase/supabase-js';
import { getSupabaseClient } from './supabase';
import { PrismaClient } from '@prisma/client';
import { UserRole } from '../models/types';

const prisma = new PrismaClient();

export interface UserContext {
  id: string;
  email: string;
  role: UserRole;
  companyId: string;
}

/**
 * Validate JWT token and extract user information
 * @param token JWT token from Authorization header
 * @returns User object from Supabase Auth
 */
export const validateToken = async (token: string): Promise<User> => {
  const supabase: SupabaseClient = getSupabaseClient();
  
  const { data, error } = await supabase.auth.getUser(token);
  
  if (error || !data.user) {
    throw new Error('Invalid or expired token');
  }
  
  return data.user;
};

/**
 * Extract user context (user_id and company_id) from JWT token
 * @param token JWT token from Authorization header
 * @returns UserContext with user ID, email, role, and company ID
 */
export const extractUserContext = async (token: string): Promise<UserContext> => {
  try {
    const user = await validateToken(token);
    
    // Fetch user role and company from database
    const userRole = await prisma.userRole.findFirst({
      where: {
        userId: user.id
      },
      include: {
        company: true
      }
    });
    
    if (!userRole) {
      throw new Error('User role not found');
    }
    
    return {
      id: user.id,
      email: user.email || '',
      role: userRole.role as UserRole,
      companyId: userRole.companyId
    };
  } catch (error) {
    throw new Error(`Failed to extract user context: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
};

/**
 * Check if user has required role
 * @param userRole Current user's role
 * @param requiredRoles Roles that are allowed
 * @returns boolean indicating if user has required role
 */
export const hasRole = (userRole: UserRole, requiredRoles: UserRole[]): boolean => {
  return requiredRoles.includes(userRole);
};

/**
 * Check if user can perform an action based on role
 * @param userRole Current user's role
 * @param action Action to perform (CREATE, READ, UPDATE, DELETE)
 * @returns boolean indicating if user has permission
 */
export const canPerformAction = (userRole: UserRole, action: 'CREATE' | 'READ' | 'UPDATE' | 'DELETE'): boolean => {
  switch (action) {
    case 'CREATE':
    case 'UPDATE':
      return userRole === UserRole.OWNER || userRole === UserRole.ADMIN;
    case 'DELETE':
      return userRole === UserRole.OWNER;
    case 'READ':
      return true; // All roles can read
    default:
      return false;
  }
};