/**
 * Standard response interface for all API endpoints.
 * 
 * Why standardized responses:
 * - Consistent client-side handling across all endpoints
 * - Easier error handling and debugging
 * - Clear success/failure indication
 * - Metadata support for pagination and additional info
 */
export interface BaseResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: {
    code: string;
    message: string;
    details?: Record<string, any>;
  };
  meta?: {
    pagination?: {
      page: number;
      limit: number;
      total: number;
      totalPages: number;
    };
    timestamp: string;
    requestId?: string;
  };
}

/**
 * Pagination parameters interface for consistent pagination across modules.
 */
export interface PaginationParams {
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'ASC' | 'DESC';
}

/**
 * Base entity interface that all entities should extend.
 * Provides common fields for audit trails and soft deletes.
 */
export interface BaseEntity {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  deletedAt?: Date;
}