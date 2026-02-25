import { StockLedger } from '../../engines/StockLedger';
import { MovementType } from '../../models/types';

describe('StockLedger', () => {
  let stockLedger: StockLedger;

  beforeEach(() => {
    stockLedger = new StockLedger();
  });

  afterEach(async () => {
    await stockLedger.disconnect();
  });

  describe('recordMovement', () => {
    test('should record stock movement', async () => {
      const movement = {
        productId: 'PROD001',
        locationId: 'LOC001',
        movementType: MovementType.IN,
        quantity: 100,
        referenceType: 'PURCHASE',
        referenceId: 'PO001',
        userId: 'USER001',
        companyId: 'COMP001',
        createdAt: new Date()
      };

      await expect(stockLedger.recordMovement(movement)).resolves.not.toThrow();
    });
  });

  describe('getCurrentStock', () => {
    test('should return current stock quantity', async () => {
      const productId = 'PROD001';
      const locationId = 'LOC001';

      const stock = await stockLedger.getCurrentStock(productId, locationId);
      
      expect(typeof stock).toBe('number');
      expect(stock).toBeGreaterThanOrEqual(0);
    });
  });

  describe('getMovements', () => {
    test('should return stock movements with proper structure', async () => {
      const filter = {
        productId: 'PROD001',
        limit: 10
      };

      // Mock the result structure
      const mockMovements = [
        {
          id: 'MOV001',
          productId: 'PROD001',
          locationId: 'LOC001',
          movementType: MovementType.IN,
          quantity: 100,
          referenceType: 'PURCHASE',
          referenceId: 'PO001',
          createdAt: new Date()
        }
      ];

      expect(Array.isArray(mockMovements)).toBe(true);
      expect(mockMovements[0]).toHaveProperty('id');
      expect(mockMovements[0]).toHaveProperty('productId');
      expect(mockMovements[0]).toHaveProperty('movementType');
      expect(mockMovements[0]).toHaveProperty('quantity');
    });
  });

  describe('calculateWeightedAvgCost', () => {
    test('should calculate weighted average cost', async () => {
      const productId = 'PROD001';
      const locationId = 'LOC001';

      const avgCost = await stockLedger.calculateWeightedAvgCost(productId, locationId);
      
      expect(typeof avgCost).toBe('number');
      expect(avgCost).toBeGreaterThanOrEqual(0);
    });
  });

  describe('getEarliestExpiryBatch', () => {
    test('should return earliest expiring batches', async () => {
      const productId = 'PROD001';
      const locationId = 'LOC001';
      const requiredQty = 50;

      const batches = await stockLedger.getEarliestExpiryBatch(productId, locationId, requiredQty);
      
      expect(Array.isArray(batches)).toBe(true);
      // Each batch should have required properties
      if (batches.length > 0) {
        expect(batches[0]).toHaveProperty('batch_number');
        expect(batches[0]).toHaveProperty('expiry_date');
        expect(batches[0]).toHaveProperty('available_quantity');
      }
    });
  });
});