import {
  Controller,
  Get,
  Post,
  Body,
  Patch,
  Param,
  Delete,
  Query,
  HttpStatus,
  ParseUUIDPipe,
} from '@nestjs/common';
import {
  ApiTags,
  ApiOperation,
  ApiParam,
  ApiQuery,
  ApiBearerAuth,
} from '@nestjs/swagger';
import { OrganizationService } from '../services/organization.service';
import { CreateOrganizationDto } from '../dto/create-organization.dto';
import { UpdateOrganizationDto } from '../dto/update-organization.dto';
import { Organization } from '../entities/organization.entity';
import { ApiStandardResponse, ApiErrorResponse } from '../../../common/decorators/api-response.decorator';
import { BaseResponse, PaginationParams } from '../../../common/interfaces/base-response.interface';

/**
 * Organization controller handles HTTP requests for organization management.
 * 
 * Why thin controllers:
 * - Controllers only handle HTTP concerns (request/response mapping)
 * - All business logic is delegated to the service layer
 * - Enables easy testing of business logic without HTTP overhead
 * - Allows for multiple interfaces (REST, GraphQL, gRPC) to same business logic
 * - Maintains clear separation of concerns
 */
@ApiTags('organizations')
@Controller('organizations')
@ApiBearerAuth() // All endpoints require authentication
export class OrganizationController {
  constructor(private readonly organizationService: OrganizationService) {}

  /**
   * Creates a new organization.
   * Only system administrators should access this endpoint.
   */
  @Post()
  @ApiOperation({ 
    summary: 'Create a new organization',
    description: 'Creates a new restaurant/business organization in the system'
  })
  @ApiStandardResponse(Organization, HttpStatus.CREATED, 'Organization created successfully')
  @ApiErrorResponse(HttpStatus.BAD_REQUEST, 'Invalid input data')
  @ApiErrorResponse(HttpStatus.CONFLICT, 'Organization already exists')
  async create(@Body() createDto: CreateOrganizationDto): Promise<BaseResponse<Organization>> {
    const organization = await this.organizationService.create(createDto);
    
    return {
      success: true,
      data: organization,
      message: 'Organization created successfully',
      meta: {
        timestamp: new Date().toISOString(),
      },
    };
  }

  /**
   * Retrieves paginated list of organizations.
   * Supports filtering and sorting for admin dashboards.
   */
  @Get()
  @ApiOperation({ 
    summary: 'Get all organizations',
    description: 'Retrieves paginated list of organizations with optional filtering'
  })
  @ApiQuery({ name: 'page', required: false, type: Number, description: 'Page number (default: 1)' })
  @ApiQuery({ name: 'limit', required: false, type: Number, description: 'Items per page (default: 10)' })
  @ApiQuery({ name: 'sortBy', required: false, type: String, description: 'Sort field (default: createdAt)' })
  @ApiQuery({ name: 'sortOrder', required: false, enum: ['ASC', 'DESC'], description: 'Sort order (default: DESC)' })
  @ApiStandardResponse(Organization, HttpStatus.OK, 'Organizations retrieved successfully')
  async findAll(@Query() params: PaginationParams): Promise<BaseResponse<Organization[]>> {
    const result = await this.organizationService.findAll(params);
    
    return {
      success: true,
      data: result.organizations,
      message: 'Organizations retrieved successfully',
      meta: {
        pagination: result.pagination,
        timestamp: new Date().toISOString(),
      },
    };
  }

  /**
   * Retrieves organization by ID.
   * Used for organization details and management.
   */
  @Get(':id')
  @ApiOperation({ 
    summary: 'Get organization by ID',
    description: 'Retrieves detailed information about a specific organization'
  })
  @ApiParam({ name: 'id', type: 'string', format: 'uuid', description: 'Organization UUID' })
  @ApiStandardResponse(Organization, HttpStatus.OK, 'Organization retrieved successfully')
  @ApiErrorResponse(HttpStatus.NOT_FOUND, 'Organization not found')
  async findById(@Param('id', ParseUUIDPipe) id: string): Promise<BaseResponse<Organization>> {
    const organization = await this.organizationService.findById(id);
    
    return {
      success: true,
      data: organization,
      message: 'Organization retrieved successfully',
      meta: {
        timestamp: new Date().toISOString(),
      },
    };
  }

  /**
   * Retrieves organization by slug.
   * Used for public-facing organization pages and subdomain routing.
   */
  @Get('slug/:slug')
  @ApiOperation({ 
    summary: 'Get organization by slug',
    description: 'Retrieves organization information using URL-friendly slug'
  })
  @ApiParam({ name: 'slug', type: 'string', description: 'Organization slug' })
  @ApiStandardResponse(Organization, HttpStatus.OK, 'Organization retrieved successfully')
  @ApiErrorResponse(HttpStatus.NOT_FOUND, 'Organization not found')
  async findBySlug(@Param('slug') slug: string): Promise<BaseResponse<Organization>> {
    const organization = await this.organizationService.findBySlug(slug);
    
    return {
      success: true,
      data: organization,
      message: 'Organization retrieved successfully',
      meta: {
        timestamp: new Date().toISOString(),
      },
    };
  }

  /**
   * Updates organization information.
   * Supports partial updates for flexible organization management.
   */
  @Patch(':id')
  @ApiOperation({ 
    summary: 'Update organization',
    description: 'Updates organization information with partial data support'
  })
  @ApiParam({ name: 'id', type: 'string', format: 'uuid', description: 'Organization UUID' })
  @ApiStandardResponse(Organization, HttpStatus.OK, 'Organization updated successfully')
  @ApiErrorResponse(HttpStatus.NOT_FOUND, 'Organization not found')
  @ApiErrorResponse(HttpStatus.BAD_REQUEST, 'Invalid input data')
  @ApiErrorResponse(HttpStatus.CONFLICT, 'Slug already exists')
  async update(
    @Param('id', ParseUUIDPipe) id: string,
    @Body() updateDto: UpdateOrganizationDto,
  ): Promise<BaseResponse<Organization>> {
    const organization = await this.organizationService.update(id, updateDto);
    
    return {
      success: true,
      data: organization,
      message: 'Organization updated successfully',
      meta: {
        timestamp: new Date().toISOString(),
      },
    };
  }

  /**
   * Soft deletes organization.
   * Preserves data for audit trails while marking as inactive.
   */
  @Delete(':id')
  @ApiOperation({ 
    summary: 'Delete organization',
    description: 'Soft deletes organization (preserves data for audit trails)'
  })
  @ApiParam({ name: 'id', type: 'string', format: 'uuid', description: 'Organization UUID' })
  @ApiStandardResponse(null, HttpStatus.OK, 'Organization deleted successfully')
  @ApiErrorResponse(HttpStatus.NOT_FOUND, 'Organization not found')
  async remove(@Param('id', ParseUUIDPipe) id: string): Promise<BaseResponse<null>> {
    await this.organizationService.remove(id);
    
    return {
      success: true,
      data: null,
      message: 'Organization deleted successfully',
      meta: {
        timestamp: new Date().toISOString(),
      },
    };
  }

  /**
   * Validates slug availability.
   * Used by frontend for real-time slug validation during organization creation/editing.
   */
  @Get('validate/slug/:slug')
  @ApiOperation({ 
    summary: 'Validate slug availability',
    description: 'Checks if a slug is available for use'
  })
  @ApiParam({ name: 'slug', type: 'string', description: 'Slug to validate' })
  @ApiQuery({ name: 'excludeId', required: false, type: 'string', description: 'Organization ID to exclude from check' })
  async validateSlug(
    @Param('slug') slug: string,
    @Query('excludeId') excludeId?: string,
  ): Promise<BaseResponse<{ available: boolean }>> {
    const available = await this.organizationService.validateSlug(slug, excludeId);
    
    return {
      success: true,
      data: { available },
      message: available ? 'Slug is available' : 'Slug is already taken',
      meta: {
        timestamp: new Date().toISOString(),
      },
    };
  }
}