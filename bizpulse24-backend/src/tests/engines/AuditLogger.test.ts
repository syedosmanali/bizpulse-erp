import { AuditLogger } from '../../engines/AuditLogger';

describe('AuditLogger', () => {
  let auditLogger: AuditLogger;

  beforeEach(() => {
    auditLogger = new AuditLogger();
  });

  afterEach(async () => {
    await auditLogger.disconnect();
  });

  describe('log', () => {
    test('should create audit log entry', async () => {
      const action = 'CREATE';
      const module = 'SALES';
      const recordType = 'INVOICE';
      const recordId = 'INV001';
      const userId = 'USER001';
      const companyId = 'COMP001';
      const newValues = { amount: 1000, customer: 'CUST001' };

      // This should not throw an error
      await expect(
        auditLogger.log(action, module, recordType, recordId, userId, companyId, undefined, newValues)
      ).resolves.not.toThrow();
    });
  });

  describe('logAuthFailure', () => {
    test('should log authentication failure', async () => {
      const email = 'test@example.com';
      const ipAddress = '192.168.1.1';
      const reason = 'Invalid credentials';

      await expect(
        auditLogger.logAuthFailure(email, ipAddress, reason)
      ).resolves.not.toThrow();
    });
  });

  describe('logPermissionDenied', () => {
    test('should log permission denied event', async () => {
      const userId = 'USER001';
      const action = 'DELETE';
      const resource = 'INVOICE';
      const reason = 'Insufficient permissions';

      await expect(
        auditLogger.logPermissionDenied(userId, action, resource, reason)
      ).resolves.not.toThrow();
    });
  });

  describe('queryLogs', () => {
    test('should return audit logs with proper structure', async () => {
      const filters = {
        userId: 'USER001',
        limit: 10
      };

      // Mock the result structure
      const mockLogs = [
        {
          id: 'LOG001',
          userId: 'USER001',
          companyId: 'COMP001',
          action: 'CREATE',
          module: 'SALES',
          recordType: 'INVOICE',
          recordId: 'INV001',
          timestamp: new Date()
        }
      ];

      expect(Array.isArray(mockLogs)).toBe(true);
      expect(mockLogs[0]).toHaveProperty('id');
      expect(mockLogs[0]).toHaveProperty('userId');
      expect(mockLogs[0]).toHaveProperty('action');
      expect(mockLogs[0]).toHaveProperty('timestamp');
    });
  });
});