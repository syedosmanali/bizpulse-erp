import { Module } from '@nestjs/common';
import { TerminusModule } from '@nestjs/terminus';
import { TypeOrmModule } from '@nestjs/typeorm';
import { HealthController } from './health.controller';

/**
 * Health module provides system monitoring and health check endpoints.
 * 
 * Why health checks are critical:
 * - Enables load balancer health monitoring
 * - Provides early warning for system issues
 * - Essential for container orchestration (Kubernetes, Docker Swarm)
 * - Helps with automated deployment rollbacks
 */
@Module({
  imports: [
    TerminusModule, // NestJS health check framework
    TypeOrmModule, // For database health checks
  ],
  controllers: [HealthController],
})
export class HealthModule {}