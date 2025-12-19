import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ConfigModule, ConfigService } from '@nestjs/config';

// Entity imports - centralized for dependency management
import { User } from '../modules/user/entities/user.entity';
import { Organization } from '../modules/organization/entities/organization.entity';

/**
 * Database module handles all TypeORM configuration and entity registration.
 * 
 * Why separate database module:
 * - Centralizes database configuration logic
 * - Manages entity registration in one place
 * - Enables easy database switching for different environments
 * - Provides connection pooling and performance optimization
 */
@Module({
  imports: [
    TypeOrmModule.forRootAsync({
      imports: [ConfigModule],
      useFactory: async (configService: ConfigService) => ({
        type: 'postgres',
        host: configService.get<string>('DB_HOST'),
        port: configService.get<number>('DB_PORT'),
        username: configService.get<string>('DB_USERNAME'),
        password: configService.get<string>('DB_PASSWORD'),
        database: configService.get<string>('DB_NAME'),
        
        // Entity registration - all entities must be listed here
        entities: [
          User,
          Organization,
        ],
        
        // Development settings - NEVER use synchronize in production
        synchronize: configService.get<string>('NODE_ENV') === 'development',
        logging: configService.get<string>('NODE_ENV') === 'development',
        
        // Connection pool settings for production performance
        extra: {
          connectionLimit: 10, // Maximum number of connections
          acquireTimeout: 60000, // Maximum time to wait for connection
          timeout: 60000, // Query timeout
        },
        
        // Retry logic for connection failures
        retryAttempts: 3,
        retryDelay: 3000,
      }),
      inject: [ConfigService],
    }),
  ],
})
export class DatabaseModule {}