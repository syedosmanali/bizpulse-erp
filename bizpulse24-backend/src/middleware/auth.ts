import { Request, Response, NextFunction } from 'express';
import { AppError } from './errorHandler';
import { UserRole } from '../models/types';
import { extractUserContext, hasRole } from '../utils/auth';

export interface AuthRequest extends Request {
  user?: {
    id: string;
    email: string;
    role: UserRole;
    companyId: string;
  };
}

/**
 * Authentication middleware to validate JWT token
 * @param req Express request object
 * @param res Express response object
 * @param next Express next function
 */
export const authenticate = async (
  req: AuthRequest,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const authHeader = req.headers.authorization;

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      throw new AppError('No token provided', 401);
    }

    const token = authHeader.substring(7);
    
    // Extract user context from token
    const userContext = await extractUserContext(token);
    
    req.user = {
      id: userContext.id,
      email: userContext.email,
      role: userContext.role,
      companyId: userContext.companyId,
    };

    next();
  } catch (error) {
    if (error instanceof Error) {
      next(new AppError(error.message, 401));
    } else {
      next(new AppError('Authentication failed', 401));
    }
  }
};

/**
 * Authorization middleware to check user roles
 * @param roles Allowed roles
 * @returns Middleware function
 */
export const authorize = (...roles: UserRole[]) => {
  return (req: AuthRequest, res: Response, next: NextFunction): void => {
    if (!req.user) {
      throw new AppError('User not authenticated', 401);
    }

    if (!hasRole(req.user.role, roles)) {
      throw new AppError('Insufficient permissions', 403);
    }

    next();
  };
};

/**
 * Company access middleware to ensure user can access requested company data
 * @param req Express request object
 * @param res Express response object
 * @param next Express next function
 */
export const validateCompanyAccess = (
  req: AuthRequest,
  res: Response,
  next: NextFunction
): void => {
  if (!req.user) {
    throw new AppError('User not authenticated', 401);
  }

  const requestedCompanyId = req.params.companyId || req.body.companyId || req.query.companyId;
  
  if (requestedCompanyId && requestedCompanyId !== req.user.companyId) {
    throw new AppError('Access to this company data is not permitted', 403);
  }

  next();
};
