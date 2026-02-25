import { CustomerService, VendorService } from '../../src/services/PartyService';

describe('CustomerService', () => {
  let customerService: CustomerService;

  beforeAll(() => {
    customerService = new CustomerService();
  });

  afterAll(async () => {
    await customerService.disconnect();
  });

  describe('GSTIN Validation', () => {
    test('should validate correct GSTIN format', () => {
      const validGSTIN = '22AAAAA0000A1Z5';
      expect(CustomerService.validateGSTIN(validGSTIN)).toBe(true);
    });

    test('should reject invalid GSTIN format', () => {
      const invalidGSTINs = [
        '123456789012345', // All numbers
        'AAAAAAAAAAAAAAA', // All letters
        '22AAAAA0000A1Z',  // Too short
        '22AAAAA0000A1Z56' // Too long
      ];

      invalidGSTINs.forEach(gstin => {
        expect(CustomerService.validateGSTIN(gstin)).toBe(false);
      });
    });

    test('should allow empty GSTIN', () => {
      expect(CustomerService.validateGSTIN('')).toBe(true);
      expect(CustomerService.validateGSTIN(null as any)).toBe(true);
      expect(CustomerService.validateGSTIN(undefined as any)).toBe(true);
    });
  });

  describe('PAN Validation', () => {
    test('should validate correct PAN format', () => {
      const validPAN = 'ABCDE1234F';
      expect(CustomerService.validatePAN(validPAN)).toBe(true);
    });

    test('should reject invalid PAN format', () => {
      const invalidPANs = [
        '1234567890', // All numbers
        'ABCDEFGHIJ', // All letters
        'ABCDE1234',  // Too short
        'ABCDE1234FG' // Too long
      ];

      invalidPANs.forEach(pan => {
        expect(CustomerService.validatePAN(pan)).toBe(false);
      });
    });

    test('should allow empty PAN', () => {
      expect(CustomerService.validatePAN('')).toBe(true);
      expect(CustomerService.validatePAN(null as any)).toBe(true);
      expect(CustomerService.validatePAN(undefined as any)).toBe(true);
    });
  });

  describe('Customer CRUD Operations', () => {
    // Note: These tests would require a test database setup
    // For now, we'll test the structure and validation logic

    test('should have createCustomer method', () => {
      expect(typeof customerService.createCustomer).toBe('function');
    });

    test('should have getCustomerById method', () => {
      expect(typeof customerService.getCustomerById).toBe('function');
    });

    test('should have updateCustomer method', () => {
      expect(typeof customerService.updateCustomer).toBe('function');
    });

    test('should have deleteCustomer method', () => {
      expect(typeof customerService.deleteCustomer).toBe('function');
    });

    test('should have listCustomers method', () => {
      expect(typeof customerService.listCustomers).toBe('function');
    });

    test('should have searchCustomerByGSTIN method', () => {
      expect(typeof customerService.searchCustomerByGSTIN).toBe('function');
    });

    test('should have updateCustomerDue method', () => {
      expect(typeof customerService.updateCustomerDue).toBe('function');
    });
  });
});

describe('VendorService', () => {
  let vendorService: VendorService;

  beforeAll(() => {
    vendorService = new VendorService();
  });

  afterAll(async () => {
    await vendorService.disconnect();
  });

  describe('GSTIN Validation', () => {
    test('should validate correct GSTIN format', () => {
      const validGSTIN = '22AAAAA0000A1Z5';
      expect(VendorService.validateGSTIN(validGSTIN)).toBe(true);
    });

    test('should reject invalid GSTIN format', () => {
      const invalidGSTIN = '123456789012345';
      expect(VendorService.validateGSTIN(invalidGSTIN)).toBe(false);
    });

    test('should allow empty GSTIN', () => {
      expect(VendorService.validateGSTIN('')).toBe(true);
    });
  });

  describe('PAN Validation', () => {
    test('should validate correct PAN format', () => {
      const validPAN = 'ABCDE1234F';
      expect(VendorService.validatePAN(validPAN)).toBe(true);
    });

    test('should reject invalid PAN format', () => {
      const invalidPAN = '1234567890';
      expect(VendorService.validatePAN(invalidPAN)).toBe(false);
    });

    test('should allow empty PAN', () => {
      expect(VendorService.validatePAN('')).toBe(true);
    });
  });

  describe('Vendor CRUD Operations', () => {
    test('should have createVendor method', () => {
      expect(typeof vendorService.createVendor).toBe('function');
    });

    test('should have getVendorById method', () => {
      expect(typeof vendorService.getVendorById).toBe('function');
    });

    test('should have updateVendor method', () => {
      expect(typeof vendorService.updateVendor).toBe('function');
    });

    test('should have deleteVendor method', () => {
      expect(typeof vendorService.deleteVendor).toBe('function');
    });

    test('should have listVendors method', () => {
      expect(typeof vendorService.listVendors).toBe('function');
    });

    test('should have searchVendorByGSTIN method', () => {
      expect(typeof vendorService.searchVendorByGSTIN).toBe('function');
    });

    test('should have updateVendorPayable method', () => {
      expect(typeof vendorService.updateVendorPayable).toBe('function');
    });
  });
});