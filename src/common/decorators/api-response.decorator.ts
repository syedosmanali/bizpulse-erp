import { applyDecorators, Type } from '@nestjs/common';
import { ApiResponse, getSchemaPath } from '@nestjs/swagger';

/**
 * Custom decorator for standardized API responses across all endpoints.
 * 
 * Why this decorator:
 * - Ensures consistent response format across all APIs
 * - Reduces boilerplate code in controllers
 * - Provides clear documentation for API consumers
 * - Enables automatic OpenAPI schema generation
 */
export const ApiStandardResponse = <TModel extends Type<any>>(
  model: TModel,
  status: number = 200,
  description?: string,
) => {
  return applyDecorators(
    ApiResponse({
      status,
      description: description || 'Success',
      schema: {
        properties: {
          success: {
            type: 'boolean',
            example: true,
          },
          data: {
            $ref: getSchemaPath(model),
          },
          message: {
            type: 'string',
            example: 'Operation completed successfully',
          },
          timestamp: {
            type: 'string',
            format: 'date-time',
            example: '2024-01-01T12:00:00Z',
          },
        },
      },
    }),
  );
};

/**
 * Decorator for error responses with consistent format.
 */
export const ApiErrorResponse = (status: number, description: string) => {
  return applyDecorators(
    ApiResponse({
      status,
      description,
      schema: {
        properties: {
          success: {
            type: 'boolean',
            example: false,
          },
          error: {
            type: 'object',
            properties: {
              code: {
                type: 'string',
                example: 'VALIDATION_ERROR',
              },
              message: {
                type: 'string',
                example: 'Invalid input data',
              },
              details: {
                type: 'object',
                example: {
                  email: ['Email is required'],
                },
              },
            },
          },
          timestamp: {
            type: 'string',
            format: 'date-time',
            example: '2024-01-01T12:00:00Z',
          },
        },
      },
    }),
  );
};