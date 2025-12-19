import { Module } from '@nestjs/common';
import { JwtModule } from '@nestjs/jwt';
import { PassportModule } from '@nestjs/passport';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { AuthController } from './controllers/auth.controller';
import { AuthService } from './services/auth.service';
import { JwtStrategy } from './strategies/jwt.strategy';
import { LocalStrategy } from './strategies/local.strategy';
import { UserModule } from '../user/user.module';

/**
 * Authentication module encapsulates all authentication-related functionality.
 * 
 * Why module boundaries:
 * - Complete encapsulation of authentication domain logic
 * - Clear dependency management through imports/exports
 * - Enables security-focused development and testing
 * - Facilitates authentication method switching (JWT, OAuth, etc.)
 * - Supports authentication service extraction in the future
 */
@Module({
  imports: [
    // Import UserModule to access UserService for authentication
    UserModule,
    
    // Passport module for authentication strategies
    PassportModule.register({ 
      defaultStrategy: 'jwt',
      session: false, // Stateless authentication with JWT
    }),
    
    // JWT module configuration
    JwtModule.registerAsync({
      imports: [ConfigModule],
      useFactory: async (configService: ConfigService) => ({
        secret: configService.get<string>('JWT_SECRET'),
        signOptions: {
          expiresIn: configService.get<string>('JWT_EXPIRES_IN', '24h'),
          issuer: 'erp-backend',
          audience: 'erp-app',
          algorithm: 'HS256',
        },
        verifyOptions: {
          issuer: 'erp-backend',
          audience: 'erp-app',
          algorithms: ['HS256'],
        },
      }),
      inject: [ConfigService],
    }),
  ],
  controllers: [
    // HTTP layer - handles authentication requests
    AuthController,
  ],
  providers: [
    // Business logic layer
    AuthService,
    
    // Passport strategies
    JwtStrategy,
    LocalStrategy,
  ],
  exports: [
    // Export service for use by other modules
    AuthService,
    
    // Export JWT module for token operations in other modules
    JwtModule,
  ],
})
export class AuthModule {}