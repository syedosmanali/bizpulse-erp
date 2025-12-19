import { NestFactory } from '@nestjs/core';
import { ValidationPipe, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import { AppModule } from './app.module';

/**
 * Bootstrap function initializes the NestJS application with production-ready configuration.
 * 
 * Why this approach:
 * - Centralized configuration management through ConfigService
 * - Global validation pipes ensure data integrity at API boundaries
 * - Swagger documentation for API discoverability
 * - Proper error handling and logging setup
 */
async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  const configService = app.get(ConfigService);
  const logger = new Logger('Bootstrap');

  // Global validation pipe - ensures all incoming data is validated
  // This prevents invalid data from reaching business logic layers
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true, // Strip properties that don't have decorators
      forbidNonWhitelisted: true, // Throw error if non-whitelisted properties exist
      transform: true, // Automatically transform payloads to DTO instances
      transformOptions: {
        enableImplicitConversion: true, // Allow type coercion (string to number, etc.)
      },
    }),
  );

  // API prefix for versioning - enables backward compatibility
  const apiPrefix = configService.get<string>('API_PREFIX', 'api/v1');
  app.setGlobalPrefix(apiPrefix);

  // CORS configuration for multi-client support (web, mobile, desktop)
  app.enableCors({
    origin: true, // In production, specify exact origins
    credentials: true,
  });

  // Swagger documentation setup - essential for team collaboration
  const config = new DocumentBuilder()
    .setTitle('ERP Backend API')
    .setDescription('Production-ready ERP system with clean architecture')
    .setVersion('1.0')
    .addBearerAuth() // JWT authentication support
    .addTag('auth', 'Authentication endpoints')
    .addTag('users', 'User management')
    .addTag('organizations', 'Organization/Restaurant management')
    .addTag('health', 'Health check endpoints')
    .build();

  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('docs', app, document);

  const port = configService.get<number>('PORT', 3000);
  
  await app.listen(port);
  
  logger.log(`🚀 Application is running on: http://localhost:${port}`);
  logger.log(`📚 API Documentation: http://localhost:${port}/docs`);
  logger.log(`🏥 Health Check: http://localhost:${port}/${apiPrefix}/health`);
}

bootstrap();