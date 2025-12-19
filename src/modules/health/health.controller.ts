import { Controller, Get } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import {
  HealthCheckService,
  HealthCheck,
  TypeOrmHealthIndicator,
  MemoryHealthIndicator,
  DiskHealthIndicator,
} from '@nestjs/terminus';

/**
 * Health controller provides comprehensive system health monitoring.
 * 
 * Why multiple health indicators:
 * - Database connectivity is critical for ERP operations
 * - Memory usage monitoring prevents OOM crashes
 * - Disk space monitoring prevents data loss
 * - Separate endpoints allow granular monitoring
 */
@ApiTags('health')
@Controller('health')
export class HealthController {
  constructor(
    private health: HealthCheckService,
    private db: TypeOrmHealthIndicator,
    private memory: MemoryHealthIndicator,
    private disk: DiskHealthIndicator,
  ) {}

  /**
   * Comprehensive health check covering all critical system components.
   * Used by load balancers and monitoring systems.
   */
  @Get()
  @ApiOperation({ summary: 'Complete system health check' })
  @HealthCheck()
  check() {
    return this.health.check([
      // Database connectivity check - critical for ERP functionality
      () => this.db.pingCheck('database'),
      
      // Memory usage check - prevents application crashes
      () => this.memory.checkHeap('memory_heap', 150 * 1024 * 1024), // 150MB limit
      () => this.memory.checkRSS('memory_rss', 150 * 1024 * 1024),
      
      // Disk space check - prevents data loss
      () => this.disk.checkStorage('storage', { 
        path: '/', 
        thresholdPercent: 0.9 // Alert when 90% full
      }),
    ]);
  }

  /**
   * Database-only health check for database-specific monitoring.
   */
  @Get('database')
  @ApiOperation({ summary: 'Database connectivity check' })
  @HealthCheck()
  checkDatabase() {
    return this.health.check([
      () => this.db.pingCheck('database'),
    ]);
  }

  /**
   * Simple liveness probe for container orchestration.
   * Returns 200 OK if the application is running.
   */
  @Get('live')
  @ApiOperation({ summary: 'Liveness probe for containers' })
  live() {
    return {
      status: 'ok',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
    };
  }

  /**
   * Readiness probe for container orchestration.
   * Checks if the application is ready to receive traffic.
   */
  @Get('ready')
  @ApiOperation({ summary: 'Readiness probe for containers' })
  @HealthCheck()
  ready() {
    return this.health.check([
      () => this.db.pingCheck('database'),
    ]);
  }
}