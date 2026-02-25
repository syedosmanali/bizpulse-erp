import { PrismaClient } from '@prisma/client';

// Interface for audit log entry
export interface AuditLogEntry {
  id?: string;
  userId: string;
  companyId: string;
  action: string;
  module: string;
  recordType: string;
  recordId: string;
  oldValues?: any;
  newValues?: any;
  ipAddress?: string;
  userAgent?: string;
  timestamp: Date;
}

// Interface for log filters
export interface LogFilters {
  userId?: string;
  companyId?: string;
  action?: string;
  module?: string;
  recordType?: string;
  startDate?: Date;
  endDate?: Date;
  limit?: number;
  offset?: number;
}

/**
 * Audit Logger for tracking all system activities
 * Provides comprehensive logging for security, compliance, and debugging
 */
export class AuditLogger {
  private prisma: PrismaClient;

  constructor() {
    this.prisma = new PrismaClient();
  }

  /**
   * Log a generic audit event
   * @param action Action performed (CREATE, UPDATE, DELETE, READ, LOGIN, LOGOUT, etc.)
   * @param module Module where action occurred (SALES, PURCHASE, INVENTORY, etc.)
   * @param recordType Type of record (INVOICE, PRODUCT, CUSTOMER, etc.)
   * @param recordId ID of the record
   * @param userId User who performed the action
   * @param companyId Company ID
   * @param oldValues Previous values (for UPDATE/DELETE)
   * @param newValues New values (for CREATE/UPDATE)
   * @param tx Prisma transaction object
   */
  public async log(
    action: string,
    module: string,
    recordType: string,
    recordId: string,
    userId: string,
    companyId: string,
    oldValues?: any,
    newValues?: any,
    tx?: PrismaClient
  ): Promise<void> {
    const client = tx || this.prisma;

    try {
      await client.$executeRaw`
        INSERT INTO audit_logs (
          id, user_id, company_id, action, module, record_type, record_id,
          old_values, new_values, ip_address, user_agent, created_at
        ) VALUES (
          gen_random_uuid(), ${userId}, ${companyId}, ${action}, ${module}, ${recordType}, ${recordId},
          ${oldValues ? JSON.stringify(oldValues) : null},
          ${newValues ? JSON.stringify(newValues) : null},
          ${this.getIpAddress()},
          ${this.getUserAgent()},
          NOW()
        )
      `;
    } catch (error) {
      // Don't throw error for audit logging failures as it shouldn't break business logic
      console.error('Failed to log audit entry:', error instanceof Error ? error.message : 'Unknown error');
    }
  }

  /**
   * Log authentication failure attempts
   * @param email User email that failed authentication
   * @param ipAddress IP address of the request
   * @param reason Reason for failure
   * @param tx Prisma transaction object
   */
  public async logAuthFailure(
    email: string,
    ipAddress: string,
    reason: string,
    tx?: PrismaClient
  ): Promise<void> {
    const client = tx || this.prisma;

    try {
      await client.$executeRaw`
        INSERT INTO auth_logs (
          id, email, ip_address, action, reason, success, created_at
        ) VALUES (
          gen_random_uuid(), ${email}, ${ipAddress}, 'LOGIN_ATTEMPT', ${reason}, false, NOW()
        )
      `;
    } catch (error) {
      console.error('Failed to log auth failure:', error instanceof Error ? error.message : 'Unknown error');
    }
  }

  /**
   * Log successful authentication
   * @param userId User ID
   * @param email User email
   * @param ipAddress IP address of the request
   * @param tx Prisma transaction object
   */
  public async logAuthSuccess(
    userId: string,
    email: string,
    ipAddress: string,
    tx?: PrismaClient
  ): Promise<void> {
    const client = tx || this.prisma;

    try {
      await client.$executeRaw`
        INSERT INTO auth_logs (
          id, user_id, email, ip_address, action, reason, success, created_at
        ) VALUES (
          gen_random_uuid(), ${userId}, ${email}, ${ipAddress}, 'LOGIN', 'Success', true, NOW()
        )
      `;
    } catch (error) {
      console.error('Failed to log auth success:', error instanceof Error ? error.message : 'Unknown error');
    }
  }

  /**
   * Log permission denied attempts
   * @param userId User ID
   * @param action Action that was denied
   * @param resource Resource that was accessed
   * @param reason Reason for denial
   * @param tx Prisma transaction object
   */
  public async logPermissionDenied(
    userId: string,
    action: string,
    resource: string,
    reason: string,
    tx?: PrismaClient
  ): Promise<void> {
    const client = tx || this.prisma;

    try {
      await client.$executeRaw`
        INSERT INTO permission_logs (
          id, user_id, action, resource, reason, created_at
        ) VALUES (
          gen_random_uuid(), ${userId}, ${action}, ${resource}, ${reason}, NOW()
        )
      `;
    } catch (error) {
      console.error('Failed to log permission denied:', error instanceof Error ? error.message : 'Unknown error');
    }
  }

  /**
   * Query audit logs with filters
   * @param filters Filter criteria
   * @param tx Prisma transaction object
   * @returns Array of audit log entries
   */
  public async queryLogs(filters: LogFilters, tx?: PrismaClient): Promise<AuditLogEntry[]> {
    const client = tx || this.prisma;
    const limit = filters.limit || 100;
    const offset = filters.offset || 0;

    try {
      let query = `
        SELECT 
          id, user_id, company_id, action, module, record_type, record_id,
          old_values, new_values, ip_address, user_agent, created_at as timestamp
        FROM audit_logs
        WHERE 1=1
      `;

      const params: any[] = [];

      if (filters.userId) {
        query += ` AND user_id = $${params.length + 1}`;
        params.push(filters.userId);
      }

      if (filters.companyId) {
        query += ` AND company_id = $${params.length + 1}`;
        params.push(filters.companyId);
      }

      if (filters.action) {
        query += ` AND action = $${params.length + 1}`;
        params.push(filters.action);
      }

      if (filters.module) {
        query += ` AND module = $${params.length + 1}`;
        params.push(filters.module);
      }

      if (filters.recordType) {
        query += ` AND record_type = $${params.length + 1}`;
        params.push(filters.recordType);
      }

      if (filters.startDate) {
        query += ` AND created_at >= $${params.length + 1}`;
        params.push(filters.startDate);
      }

      if (filters.endDate) {
        query += ` AND created_at <= $${params.length + 1}`;
        params.push(filters.endDate);
      }

      query += ` ORDER BY created_at DESC LIMIT $${params.length + 1} OFFSET $${params.length + 2}`;
      params.push(limit, offset);

      const result = await client.$queryRawUnsafe(query, ...params);
      return result as AuditLogEntry[];
    } catch (error) {
      throw new Error(`Failed to query audit logs: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get authentication logs
   * @param filters Filter criteria
   * @param tx Prisma transaction object
   * @returns Array of authentication logs
   */
  public async getAuthLogs(
    filters: { 
      email?: string; 
      userId?: string; 
      success?: boolean; 
      startDate?: Date; 
      endDate?: Date;
      limit?: number;
      offset?: number;
    },
    tx?: PrismaClient
  ): Promise<any[]> {
    const client = tx || this.prisma;
    const limit = filters.limit || 100;
    const offset = filters.offset || 0;

    try {
      let query = `
        SELECT 
          id, user_id, email, ip_address, action, reason, success, created_at
        FROM auth_logs
        WHERE 1=1
      `;

      const params: any[] = [];

      if (filters.email) {
        query += ` AND email = $${params.length + 1}`;
        params.push(filters.email);
      }

      if (filters.userId) {
        query += ` AND user_id = $${params.length + 1}`;
        params.push(filters.userId);
      }

      if (filters.success !== undefined) {
        query += ` AND success = $${params.length + 1}`;
        params.push(filters.success);
      }

      if (filters.startDate) {
        query += ` AND created_at >= $${params.length + 1}`;
        params.push(filters.startDate);
      }

      if (filters.endDate) {
        query += ` AND created_at <= $${params.length + 1}`;
        params.push(filters.endDate);
      }

      query += ` ORDER BY created_at DESC LIMIT $${params.length + 1} OFFSET $${params.length + 2}`;
      params.push(limit, offset);

      const result = await client.$queryRawUnsafe(query, ...params);
      return result as any[];
    } catch (error) {
      throw new Error(`Failed to get auth logs: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get system activity summary
   * @param companyId Company ID
   * @param days Number of days to look back
   * @param tx Prisma transaction object
   * @returns Activity summary
   */
  public async getActivitySummary(
    companyId: string,
    days: number = 30,
    tx?: PrismaClient
  ): Promise<any> {
    const client = tx || this.prisma;
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);

    try {
      const [totalActions, userActivity, moduleActivity] = await Promise.all([
        // Total actions
        client.$queryRaw<any[]>`
          SELECT COUNT(*) as count FROM audit_logs 
          WHERE company_id = ${companyId} AND created_at >= ${startDate}
        `,
        
        // User activity
        client.$queryRaw<any[]>`
          SELECT 
            user_id,
            COUNT(*) as action_count,
            MAX(created_at) as last_activity
          FROM audit_logs 
          WHERE company_id = ${companyId} AND created_at >= ${startDate}
          GROUP BY user_id
          ORDER BY action_count DESC
          LIMIT 10
        `,
        
        // Module activity
        client.$queryRaw<any[]>`
          SELECT 
            module,
            COUNT(*) as action_count
          FROM audit_logs 
          WHERE company_id = ${companyId} AND created_at >= ${startDate}
          GROUP BY module
          ORDER BY action_count DESC
        `
      ]);

      return {
        totalActions: totalActions[0]?.count || 0,
        userActivity,
        moduleActivity,
        periodDays: days
      };
    } catch (error) {
      throw new Error(`Failed to get activity summary: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get IP address from request context
   * @returns IP address string
   */
  private getIpAddress(): string {
    // This would typically come from the request context
    // For now, returning a placeholder
    return '127.0.0.1';
  }

  /**
   * Get user agent from request context
   * @returns User agent string
   */
  private getUserAgent(): string {
    // This would typically come from the request context
    // For now, returning a placeholder
    return 'Unknown';
  }

  /**
   * Close the database connection
   */
  public async disconnect(): Promise<void> {
    await this.prisma.$disconnect();
  }
}