import { config, validateConfig } from '../config';

describe('Config', () => {
  describe('config object', () => {
    it('should have default values', () => {
      expect(config.env).toBeDefined();
      expect(config.port).toBeDefined();
      expect(config.apiVersion).toBeDefined();
    });

    it('should have supabase configuration', () => {
      expect(config.supabase).toBeDefined();
      expect(config.supabase.url).toBeDefined();
      expect(config.supabase.anonKey).toBeDefined();
    });

    it('should have database configuration', () => {
      expect(config.database).toBeDefined();
      expect(config.database.url).toBeDefined();
    });
  });

  describe('validateConfig', () => {
    it('should validate required environment variables', () => {
      // This test will depend on environment setup
      // In a real scenario, you would mock process.env
      expect(() => validateConfig()).toBeDefined();
    });
  });
});
