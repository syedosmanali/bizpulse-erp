#!/usr/bin/env node

/**
 * API Contract Generator
 * 
 * Generates complete OpenAPI specification from our API contract.
 * This ensures our documentation stays in sync with our implementation.
 */

const fs = require('fs');
const path = require('path');

// OpenAPI specification structure
const openApiSpec = {
  openapi: '3.0.3',
  info: {
    title: 'ERP Backend API',
    description: 'Production-ready ERP system with clean architecture',
    version: '1.0.0',
    contact: {
      name: 'ERP Team',
      email: 'api@erp-system.com'
    },
    license: {
      name: 'MIT',
      url: 'https://opensource.org/licenses/MIT'
    }
  },
  servers: [
    {
      url: 'https://api.erp-system.com/v1',
      description: 'Production server'
    },
    {
      url: 'https://staging-api.erp-system.com/v1',
      description: 'Staging server'
    },
    {
      url: 'http://localhost:3000/api/v1',
      description: 'Development server'
    }
  ],
  security: [
    { BearerAuth: [] }
  ],
  components: {
    securitySchemes: {
      BearerAuth: {
        type: 'http',
        scheme: 'bearer',
        bearerFormat: 'JWT',
        description: 'JWT access token for authentication'
      }
    },
    schemas: {
      // Standard Response Schemas
      SuccessResponse: {
        type: 'object',
        required: ['success', 'data', 'message', 'meta'],
        properties: {
          success: { type: 'boolean', example: true },
          data: { type: 'object', description: 'Response payload' },
          message: { type: 'string', example: 'Operation completed successfully' },
          meta: { $ref: '#/components/schemas/ResponseMeta' }
        }
      },
      ErrorResponse: {
        type: 'object',
        required: ['success', 'error', 'meta'],
        properties: {
          success: { type: 'boolean', example: false },
          error: { $ref: '#/components/schemas/ErrorDetails' },
          meta: { $ref: '#/components/schemas/ResponseMeta' }
        }
      },
      ResponseMeta: {
        type: 'object',
        required: ['timestamp', 'version'],
        properties: {
          timestamp: { type: 'string', format: 'date-time', example: '2024-01-01T12:00:00Z' },
          version: { type: 'string', example: 'v1' },
          requestId: { type: 'string', example: 'req_123456789' },
          pagination: { $ref: '#/components/schemas/PaginationMeta' }
        }
      },
      PaginationMeta: {
        type: 'object',
        required: ['page', 'limit', 'total', 'totalPages'],
        properties: {
          page: { type: 'integer', minimum: 1, example: 1 },
          limit: { type: 'integer', minimum: 1, maximum: 100, example: 10 },
          total: { type: 'integer', minimum: 0, example: 100 },
          totalPages: { type: 'integer', minimum: 0, example: 10 }
        }
      },
      ErrorDetails: {
        type: 'object',
        required: ['code', 'message'],
        properties: {
          code: { type: 'string', example: 'VALIDATION_ERROR' },
          message: { type: 'string', example: 'Invalid input data' },
          details: {
            type: 'object',
            additionalProperties: {
              type: 'array',
              items: { type: 'string' }
            },
            example: {
              email: ['Email is required'],
              password: ['Password must be at least 8 characters']
            }
          }
        }
      }
    }
  },
  paths: {
    // Health endpoints
    '/health': {
      get: {
        tags: ['Health'],
        summary: 'System health check',
        description: 'Comprehensive health check for load balancers and monitoring',
        security: [],
        responses: {
          '200': {
            description: 'System is healthy',
            content: {
              'application/json': {
                schema: {
                  allOf: [
                    { $ref: '#/components/schemas/SuccessResponse' },
                    {
                      type: 'object',
                      properties: {
                        data: {
                          type: 'object',
                          properties: {
                            status: { type: 'string', example: 'ok' },
                            uptime: { type: 'integer', example: 86400 },
                            version: { type: 'string', example: '1.0.0' }
                          }
                        }
                      }
                    }
                  ]
                }
              }
            }
          }
        }
      }
    },
    // Auth endpoints
    '/auth/login': {
      post: {
        tags: ['Authentication'],
        summary: 'User login',
        description: 'Authenticate user with email/password and return JWT tokens',
        security: [],
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: {
                type: 'object',
                required: ['email', 'password', 'organizationId'],
                properties: {
                  email: { type: 'string', format: 'email', example: 'user@example.com' },
                  password: { type: 'string', example: 'SecurePass123!' },
                  organizationId: { type: 'string', format: 'uuid', example: '123e4567-e89b-12d3-a456-426614174000' }
                }
              }
            }
          }
        },
        responses: {
          '200': {
            description: 'Login successful',
            content: {
              'application/json': {
                schema: {
                  allOf: [
                    { $ref: '#/components/schemas/SuccessResponse' },
                    {
                      type: 'object',
                      properties: {
                        data: {
                          type: 'object',
                          properties: {
                            accessToken: { type: 'string', example: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' },
                            refreshToken: { type: 'string', example: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' },
                            tokenType: { type: 'string', example: 'Bearer' },
                            expiresIn: { type: 'integer', example: 86400 }
                          }
                        }
                      }
                    }
                  ]
                }
              }
            }
          },
          '401': {
            description: 'Invalid credentials',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/ErrorResponse' }
              }
            }
          }
        }
      }
    }
  },
  tags: [
    { name: 'Health', description: 'System health and monitoring endpoints' },
    { name: 'Authentication', description: 'User authentication and authorization' },
    { name: 'Users', description: 'User management operations' },
    { name: 'Organizations', description: 'Organization/Restaurant management' }
  ]
};

// Generate the OpenAPI spec file
function generateOpenApiSpec() {
  const outputPath = path.join(__dirname, 'openapi-spec-v1.json');
  
  try {
    fs.writeFileSync(outputPath, JSON.stringify(openApiSpec, null, 2));
    console.log('✅ OpenAPI specification generated successfully!');
    console.log(`📄 File: ${outputPath}`);
    console.log('🔗 Import this file into Swagger Editor or Postman');
    
    // Also generate YAML version
    const yaml = require('js-yaml');
    const yamlPath = path.join(__dirname, 'openapi-spec-v1.yaml');
    fs.writeFileSync(yamlPath, yaml.dump(openApiSpec));
    console.log(`📄 YAML version: ${yamlPath}`);
    
  } catch (error) {
    console.error('❌ Error generating OpenAPI spec:', error.message);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  generateOpenApiSpec();
}

module.exports = { generateOpenApiSpec, openApiSpec };