import { GSTEngine, GSTCalculation } from '../../engines/GSTEngine';
import { fc, test } from 'fast-check';

describe('GSTEngine', () => {
  let gstEngine: GSTEngine;

  beforeEach(() => {
    gstEngine = new GSTEngine();
  });

  afterEach(async () => {
    await gstEngine.disconnect();
  });

  describe('calculateGST', () => {
    test('should calculate CGST and SGST for intra-state transactions', () => {
      const result = gstEngine.calculateGST(1000, 18, 'Maharashtra', 'Maharashtra');
      
      expect(result.taxableAmount).toBe(1000);
      expect(result.gstRate).toBe(18);
      expect(result.cgst).toBe(90); // 180 / 2
      expect(result.sgst).toBe(90); // 180 / 2
      expect(result.igst).toBe(0);
      expect(result.totalGst).toBe(180);
      expect(result.totalAmount).toBe(1180);
    });

    test('should calculate IGST for inter-state transactions', () => {
      const result = gstEngine.calculateGST(1000, 18, 'Maharashtra', 'Karnataka');
      
      expect(result.taxableAmount).toBe(1000);
      expect(result.gstRate).toBe(18);
      expect(result.cgst).toBe(0);
      expect(result.sgst).toBe(0);
      expect(result.igst).toBe(180);
      expect(result.totalGst).toBe(180);
      expect(result.totalAmount).toBe(1180);
    });

    test('should handle zero GST rate', () => {
      const result = gstEngine.calculateGST(1000, 0, 'Maharashtra', 'Maharashtra');
      
      expect(result.taxableAmount).toBe(1000);
      expect(result.gstRate).toBe(0);
      expect(result.cgst).toBe(0);
      expect(result.sgst).toBe(0);
      expect(result.igst).toBe(0);
      expect(result.totalGst).toBe(0);
      expect(result.totalAmount).toBe(1000);
    });

    test('should validate GST rates', () => {
      expect(() => gstEngine.calculateGST(1000, 25, 'Maharashtra', 'Maharashtra'))
        .toThrow('Invalid GST rate: 25');
    });

    test('should handle negative taxable amount', () => {
      expect(() => gstEngine.calculateGST(-1000, 18, 'Maharashtra', 'Maharashtra'))
        .toThrow('Taxable amount cannot be negative');
    });

    test('should handle property-based testing for valid inputs', () => {
      fc.assert(
        fc.property(
          fc.float({ min: 0, max: 1000000, noNaN: true }),
          fc.constantFrom(0, 5, 12, 18, 28),
          fc.string({ minLength: 1, maxLength: 50 }),
          fc.string({ minLength: 1, maxLength: 50 }),
          (amount, rate, customerState, companyState) => {
            const result = gstEngine.calculateGST(amount, rate, customerState, companyState);
            
            // Validate the calculation
            expect(result.taxableAmount).toBe(amount);
            expect(result.gstRate).toBe(rate);
            expect(result.totalGst).toBeCloseTo((amount * rate) / 100, 2);
            expect(result.totalAmount).toBeCloseTo(amount + (amount * rate) / 100, 2);
            
            // Validate GST distribution
            if (customerState.toLowerCase() === companyState.toLowerCase()) {
              // Intra-state
              expect(result.cgst).toBeCloseTo(result.totalGst / 2, 2);
              expect(result.sgst).toBeCloseTo(result.totalGst / 2, 2);
              expect(result.igst).toBe(0);
            } else {
              // Inter-state
              expect(result.cgst).toBe(0);
              expect(result.sgst).toBe(0);
              expect(result.igst).toBe(result.totalGst);
            }
          }
        )
      );
    });
  });

  describe('calculateGSTSummary', () => {
    test('should calculate summary for multiple line items', () => {
      const lineItems = [
        {
          id: '1',
          productId: 'P001',
          quantity: 2,
          rate: 500,
          taxableAmount: 1000,
          gstRate: 18,
          cgst: 90,
          sgst: 90,
          igst: 0,
          totalGst: 180,
          totalAmount: 1180
        },
        {
          id: '2',
          productId: 'P002',
          quantity: 1,
          rate: 800,
          taxableAmount: 800,
          gstRate: 12,
          cgst: 48,
          sgst: 48,
          igst: 0,
          totalGst: 96,
          totalAmount: 896
        }
      ];

      const summary = gstEngine.calculateGSTSummary(lineItems);

      expect(summary.totalTaxableAmount).toBe(1800);
      expect(summary.totalCGST).toBe(138);
      expect(summary.totalSGST).toBe(138);
      expect(summary.totalIGST).toBe(0);
      expect(summary.totalGST).toBe(276);
      expect(summary.totalAmount).toBe(2076);
    });
  });

  describe('getGSTRateForCategory', () => {
    test('should return correct GST rates for categories', () => {
      expect(gstEngine.getGSTRateForCategory('goods')).toBe(18);
      expect(gstEngine.getGSTRateForCategory('food')).toBe(5);
      expect(gstEngine.getGSTRateForCategory('medicines')).toBe(0);
      expect(gstEngine.getGSTRateForCategory('unknown')).toBe(18); // default
    });
  });
});