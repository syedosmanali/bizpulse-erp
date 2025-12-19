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
import { UserService } from '../services/user.service';
import { CreateUserDto } from '../dto/create-user.dto';
import { UpdateUserDto } from '../dto/update-user.dto';
import { ChangePasswordDto } from '../dto/change-password.dto';
import { User } from '../entities/user.entity';
import { ApiStandardResponse, ApiErrorResponse } from '../../../common/decorators/api-response.decorator';
import { BaseResponse, PaginationParams } from '../../../common/interfaces/base-response.interface';

/**
 * User controller handles HTTP requests for user management.
 * 
 * Why thin controllers:
 * - Controllers only handle HTTP request/response mapping
 * - All business logic is delegated to the service layer
 * - Enables easy testing without HTTP overhead
 * - Supports multiple interfaces (REST, GraphQL) to same business logic
 * - Maintains clear separation of concerns
 */
@ApiTags('users')
@Controller('users')
@ApiBearerAuth() // All endpoints require authentication
export class UserController {
  constructor(private readonly userService: UserService) {}

  /**
   * Creates a new user within an organization.
   */
  @Post()
  @ApiOperation({ 
    summary: 'Create a new user',
    description: 'Creates a new user account within an organization'
  })
  @ApiStandardResponse(User, HttpStatus.CREATED, 'User created successfully')
  @ApiErrorResponse(HttpStatus.BAD_REQUEST, 'Invalid input data')
  @ApiErrorResponse(HttpStatus.CONFLICT, 'User already exists')
  async create(@Body() createDto: CreateUserDto): Promise<BaseResponse<User>> {
    const user = await this.userService.create(createDto);
    
    return {
      success: true,
      data: user,
      message: 'User created successfully',
      meta: {
        timestamp: new Date().toISOString(),
      },
    };
  }

  /**
   * Retrieves paginated list of users within an organization.
   */
  @Get('organization/:organizationId')
  @ApiOperation({ 
    summary: 'Get users by organization',
    description: 'Retrieves paginated list of users within a specific organization'
  })
  @ApiParam({ name: 'organizationId', type: 'string', format: 'uuid', description: 'Organization UUID' })
  @ApiQuery({ name: 'page', required: false, type: Number, description: 'Page number (default: 1)' })
  @ApiQuery({ name: 'limit', required: false, type: Number, description: 'Items per page (default: 10)' })
  @ApiQuery({ name: 'sortBy', required: false, type: String, description: 'Sort field (default: createdAt)' })
  @ApiQuery({ name: 'sortOrder', required: false, enum: ['ASC', 'DESC'], description: 'Sort order (default: DESC)' })
  @ApiStandardResponse(User, HttpStatus.OK, 'Users retrieved successfully')
  async findByOrganization(
    @Param('organizationId', ParseUUIDPipe) organizationId: string,
    @Query() params: PaginationParams,
  ): Promise<BaseResponse<User[]>> {
    const result = await this.userService.findByOrganization(organizationId, params);
    
    return {
      success: true,
      data: result.users,
      message: 'Users retrieved successfully',
      meta: {
        pagination: result.pagination,
        timestamp: new Date().toISOString(),
      },
    };
  }

  /**
   * Retrieves user by ID.
   */
  @Get(':id')
  @ApiOperation({ 
    summary: 'Get user by ID',
    description: 'Retrieves detailed information about a specific user'
  })
  @ApiParam({ name: 'id', type: 'string', format: 'uuid', description: 'User UUID' })
  @ApiStandardResponse(User, HttpStatus.OK, 'User retrieved successfully')
  @ApiErrorResponse(HttpStatus.NOT_FOUND, 'User not found')
  async findById(@Param('id', ParseUUIDPipe) id: string): Promise<BaseResponse<User>> {
    const user = await this.userService.findById(id);
    
    return {
      success: true,
      data: user,
      message: 'User retrieved successfully',
      meta: {
        timestamp: new Date().toISOString(),
      },
    };
  }

  /**
   * Updates user information.
   */
  @Patch(':id')
  @ApiOperation({ 
    summary: 'Update user',
    description: 'Updates user information with partial data support'
  })
  @ApiParam({ name: 'id', type: 'string', format: 'uuid', description: 'User UUID' })
  @ApiStandardResponse(User, HttpStatus.OK, 'User updated successfully')
  @ApiErrorResponse(HttpStatus.NOT_FOUND, 'User not found')
  @ApiErrorResponse(HttpStatus.BAD_REQUEST, 'Invalid input data')
  @ApiErrorResponse(HttpStatus.CONFLICT, 'Email already exists')
  async update(
    @Param('id', ParseUUIDPipe) id: string,
    @Body() updateDto: UpdateUserDto,
  ): Promise<BaseResponse<User>> {
    const user = await this.userService.update(id, updateDto);
    
    return {
      success: true,
      data: user,
      message: 'User updated successfully',
      meta: {
        timestamp: new Date().toISOString(),
      },
    };
  }

  /**
   * Changes user password with current password verification.
   */
  @Patch(':id/password')
  @ApiOperation({ 
    summary: 'Change user password',
    description: 'Changes user password with current password verification'
  })
  @ApiParam({ name: 'id', type: 'string', format: 'uuid', description: 'User UUID' })
  @ApiStandardResponse(null, HttpStatus.OK, 'Password changed successfully')
  @ApiErrorResponse(HttpStatus.NOT_FOUND, 'User not found')
  @ApiErrorResponse(HttpStatus.BAD_REQUEST, 'Invalid password data')
  @ApiErrorResponse(HttpStatus.UNAUTHORIZED, 'Current password is incorrect')
  async changePassword(
    @Param('id', ParseUUIDPipe) id: string,
    @Body() changePasswordDto: ChangePasswordDto,
  ): Promise<BaseResponse<null>> {
    await this.userService.changePassword(id, changePasswordDto);
    
    return {
      success: true,
      data: null,
      message: 'Password changed successfully',
      meta: {
        timestamp: new Date().toISOString(),
      },
    };
  }

  /**
   * Activates or deactivates user account.
   */
  @Patch(':id/status')
  @ApiOperation({ 
    summary: 'Update user active status',
    description: 'Activates or deactivates user account'
  })
  @ApiParam({ name: 'id', type: 'string', format: 'uuid', description: 'User UUID' })
  @ApiStandardResponse(User, HttpStatus.OK, 'User status updated successfully')
  @ApiErrorResponse(HttpStatus.NOT_FOUND, 'User not found')
  async setActiveStatus(
    @Param('id', ParseUUIDPipe) id: string,
    @Body() body: { isActive: boolean },
  ): Promise<BaseResponse<User>> {
    const user = await this.userService.setActiveStatus(id, body.isActive);
    
    return {
      success: true,
      data: user,
      message: `User ${body.isActive ? 'activated' : 'deactivated'} successfully`,
      meta: {
        timestamp: new Date().toISOString(),
      },
    };
  }

  /**
   * Verifies user email address.
   */
  @Patch(':id/verify-email')
  @ApiOperation({ 
    summary: 'Verify user email',
    description: 'Marks user email as verified'
  })
  @ApiParam({ name: 'id', type: 'string', format: 'uuid', description: 'User UUID' })
  @ApiStandardResponse(User, HttpStatus.OK, 'Email verified successfully')
  @ApiErrorResponse(HttpStatus.NOT_FOUND, 'User not found')
  async verifyEmail(@Param('id', ParseUUIDPipe) id: string): Promise<BaseResponse<User>> {
    const user = await this.userService.verifyEmail(id);
    
    return {
      success: true,
      data: user,
      message: 'Email verified successfully',
      meta: {
        timestamp: new Date().toISOString(),
      },
    };
  }

  /**
   * Updates user roles.
   */
  @Patch(':id/roles')
  @ApiOperation({ 
    summary: 'Update user roles',
    description: 'Updates user roles for permission management'
  })
  @ApiParam({ name: 'id', type: 'string', format: 'uuid', description: 'User UUID' })
  @ApiStandardResponse(User, HttpStatus.OK, 'User roles updated successfully')
  @ApiErrorResponse(HttpStatus.NOT_FOUND, 'User not found')
  @ApiErrorResponse(HttpStatus.BAD_REQUEST, 'Invalid roles')
  async updateRoles(
    @Param('id', ParseUUIDPipe) id: string,
    @Body() body: { roles: string[] },
  ): Promise<BaseResponse<User>> {
    const user = await this.userService.updateRoles(id, body.roles);
    
    return {
      success: true,
      data: user,
      message: 'User roles updated successfully',
      meta: {
        timestamp: new Date().toISOString(),
      },
    };
  }

  /**
   * Soft deletes user.
   */
  @Delete(':id')
  @ApiOperation({ 
    summary: 'Delete user',
    description: 'Soft deletes user (preserves data for audit trails)'
  })
  @ApiParam({ name: 'id', type: 'string', format: 'uuid', description: 'User UUID' })
  @ApiStandardResponse(null, HttpStatus.OK, 'User deleted successfully')
  @ApiErrorResponse(HttpStatus.NOT_FOUND, 'User not found')
  async remove(@Param('id', ParseUUIDPipe) id: string): Promise<BaseResponse<null>> {
    await this.userService.remove(id);
    
    return {
      success: true,
      data: null,
      message: 'User deleted successfully',
      meta: {
        timestamp: new Date().toISOString(),
      },
    };
  }

  /**
   * Finds users by role within organization.
   */
  @Get('organization/:organizationId/role/:role')
  @ApiOperation({ 
    summary: 'Get users by role',
    description: 'Retrieves users with specific role within an organization'
  })
  @ApiParam({ name: 'organizationId', type: 'string', format: 'uuid', description: 'Organization UUID' })
  @ApiParam({ name: 'role', type: 'string', description: 'User role' })
  @ApiStandardResponse(User, HttpStatus.OK, 'Users retrieved successfully')
  async findByRole(
    @Param('organizationId', ParseUUIDPipe) organizationId: string,
    @Param('role') role: string,
  ): Promise<BaseResponse<User[]>> {
    const users = await this.userService.findByRole(organizationId, role);
    
    return {
      success: true,
      data: users,
      message: 'Users retrieved successfully',
      meta: {
        timestamp: new Date().toISOString(),
      },
    };
  }
}