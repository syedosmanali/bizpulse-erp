import { PrismaClient } from '@prisma/client';
import { MovementType } from '../models/types';

// Interface for stock movement
export interface StockMovement {
  id?: string;
  productId: string;
  locationId: string;
  movementType: MovementType;
  quantity: number;
  batchNumber?: string;
  expiryDate?: Date;
  referenceType: string;
  referenceId: string;
  userId: string;
  companyId: string;
  remarks?: string;
  createdAt: Date;
}

// Interface for stock balance
export interface StockBalance {
  productId: string;
  locationId: string;
  batchNumber?: string;
  quantity: number;
  expiryDate?: Date;
  lastUpdated: Date;
}

// Interface for stock movement filter
export interface MovementFilter {
  productId?: string;
  locationId?: string;
  batchNumber?: string;
  movementType?: MovementType;
  startDate?: Date;
  endDate?: Date;
  referenceType?: string;
  limit?: number;
  offset?: number;
}

/**
 * Stock Ledger for inventory management
 * Handles stock movements, balances, and batch tracking
 */
export class StockLedger {
  private prisma: PrismaClient;

  constructor() {
    this.prisma = new PrismaClient();
  }

  /**
   * Record stock movement
   * @param movement Stock movement details
   * @param tx Prisma transaction object
   */
  public async recordMovement(movement: StockMovement, tx?: PrismaClient): Promise<void> {
    const client = tx || this.prisma;

    try {
      // Insert stock movement record
      await client.$executeRaw`
        INSERT INTO stock_movements (
          id, product_id, location_id, movement_type, quantity,
          batch_number, expiry_date, reference_type, reference_id,
          user_id, company_id, remarks, created_at
        ) VALUES (
          gen_random_uuid(), ${movement.productId}, ${movement.locationId},
          ${movement.movementType}, ${movement.quantity},
          ${movement.batchNumber || null}, ${movement.expiryDate || null},
          ${movement.referenceType}, ${movement.referenceId},
          ${movement.userId}, ${movement.companyId}, ${movement.remarks || null},
          NOW()
        )
      `;

      // Update stock balance
      await this.updateStockBalance(movement, client);
    } catch (error) {
      throw new Error(`Failed to record stock movement: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get current stock balance for a product at a location
   * @param productId Product ID
   * @param locationId Location ID
   * @param batchNumber Optional batch number
   * @param tx Prisma transaction object
   * @returns Current stock quantity
   */
  public async getCurrentStock(
    productId: string,
    locationId: string,
    batchNumber?: string,
    tx?: PrismaClient
  ): Promise<number> {
    const client = tx || this.prisma;

    try {
      let query = `
        SELECT COALESCE(SUM(
          CASE 
            WHEN movement_type = 'IN' THEN quantity
            WHEN movement_type = 'OUT' THEN -quantity
            ELSE 0
          END
        ), 0) as balance
        FROM stock_movements
        WHERE product_id = $1 AND location_id = $2 AND company_id = $3
      `;
      
      const params: any[] = [productId, locationId, process.env.COMPANY_ID || 'default'];

      if (batchNumber) {
        query += ` AND batch_number = $${params.length + 1}`;
        params.push(batchNumber);
      }

      const result = await client.$queryRawUnsafe(query, ...params);
      return Number(result[0]?.balance || 0);
    } catch (error) {
      throw new Error(`Failed to get current stock: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get stock movements with filters
   * @param filter Movement filters
   * @param tx Prisma transaction object
   * @returns Array of stock movements
   */
  public async getMovements(filter: MovementFilter, tx?: PrismaClient): Promise<StockMovement[]> {
    const client = tx || this.prisma;
    const limit = filter.limit || 100;
    const offset = filter.offset || 0;

    try {
      let query = `
        SELECT 
          id, product_id, location_id, movement_type, quantity,
          batch_number, expiry_date, reference_type, reference_id,
          user_id, company_id, remarks, created_at
        FROM stock_movements
        WHERE 1=1
      `;

      const params: any[] = [];

      if (filter.productId) {
        query += ` AND product_id = $${params.length + 1}`;
        params.push(filter.productId);
      }

      if (filter.locationId) {
        query += ` AND location_id = $${params.length + 1}`;
        params.push(filter.locationId);
      }

      if (filter.batchNumber) {
        query += ` AND batch_number = $${params.length + 1}`;
        params.push(filter.batchNumber);
      }

      if (filter.movementType) {
        query += ` AND movement_type = $${params.length + 1}`;
        params.push(filter.movementType);
      }

      if (filter.startDate) {
        query += ` AND created_at >= $${params.length + 1}`;
        params.push(filter.startDate);
      }

      if (filter.endDate) {
        query += ` AND created_at <= $${params.length + 1}`;
        params.push(filter.endDate);
      }

      if (filter.referenceType) {
        query += ` AND reference_type = $${params.length + 1}`;
        params.push(filter.referenceType);
      }

      query += ` ORDER BY created_at DESC LIMIT $${params.length + 1} OFFSET $${params.length + 2}`;
      params.push(limit, offset);

      const result = await client.$queryRawUnsafe(query, ...params);
      return result as StockMovement[];
    } catch (error) {
      throw new Error(`Failed to get stock movements: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Calculate weighted average cost for a product at a location
   * @param productId Product ID
   * @param locationId Location ID
   * @param tx Prisma transaction object
   * @returns Weighted average cost
   */
  public async calculateWeightedAvgCost(
    productId: string,
    locationId: string,
    tx?: PrismaClient
  ): Promise<number> {
    const client = tx || this.prisma;

    try {
      const result = await client.$queryRaw<any[]>`
        WITH inventory_transactions AS (
          SELECT 
            sm.quantity,
            sm.movement_type,
            COALESCE(p.cost_price, 0) as unit_cost
          FROM stock_movements sm
          LEFT JOIN products p ON sm.product_id = p.id
          WHERE sm.product_id = ${productId}
            AND sm.location_id = ${locationId}
            AND sm.movement_type IN ('IN', 'OUT')
        )
        SELECT 
          CASE 
            WHEN SUM(CASE WHEN movement_type = 'IN' THEN quantity ELSE 0 END) > 0 THEN
              SUM(CASE WHEN movement_type = 'IN' THEN quantity * unit_cost ELSE 0 END) /
              SUM(CASE WHEN movement_type = 'IN' THEN quantity ELSE 0 END)
            ELSE 0
          END as weighted_avg_cost
        FROM inventory_transactions
      `;

      return Number(result[0]?.weighted_avg_cost || 0);
    } catch (error) {
      throw new Error(`Failed to calculate weighted average cost: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get earliest expiring batches for a product
   * @param productId Product ID
   * @param locationId Location ID
   * @param requiredQty Required quantity
   * @param tx Prisma transaction object
   * @returns Array of batch information
   */
  public async getEarliestExpiryBatch(
    productId: string,
    locationId: string,
    requiredQty: number,
    tx?: PrismaClient
  ): Promise<any[]> {
    const client = tx || this.prisma;

    try {
      const result = await client.$queryRaw<any[]>`
        SELECT 
          batch_number,
          expiry_date,
          SUM(CASE 
            WHEN movement_type = 'IN' THEN quantity
            WHEN movement_type = 'OUT' THEN -quantity
            ELSE 0
          END) as available_quantity
        FROM stock_movements
        WHERE product_id = ${productId}
          AND location_id = ${locationId}
          AND batch_number IS NOT NULL
          AND expiry_date IS NOT NULL
          AND expiry_date >= NOW()
        GROUP BY batch_number, expiry_date
        HAVING SUM(CASE 
          WHEN movement_type = 'IN' THEN quantity
          WHEN movement_type = 'OUT' THEN -quantity
          ELSE 0
        END) > 0
        ORDER BY expiry_date ASC, batch_number ASC
      `;

      // Filter batches to meet required quantity
      let totalQty = 0;
      const selectedBatches = [];
      
      for (const batch of result) {
        if (totalQty >= requiredQty) break;
        
        const qtyToTake = Math.min(batch.available_quantity, requiredQty - totalQty);
        selectedBatches.push({
          ...batch,
          quantity: qtyToTake
        });
        
        totalQty += qtyToTake;
      }

      return selectedBatches;
    } catch (error) {
      throw new Error(`Failed to get earliest expiry batches: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get stock balance report for all products at a location
   * @param locationId Location ID
   * @param tx Prisma transaction object
   * @returns Stock balance report
   */
  public async getStockBalanceReport(
    locationId: string,
    tx?: PrismaClient
  ): Promise<StockBalance[]> {
    const client = tx || this.prisma;

    try {
      const result = await client.$queryRaw<any[]>`
        SELECT 
          product_id,
          location_id,
          batch_number,
          expiry_date,
          SUM(CASE 
            WHEN movement_type = 'IN' THEN quantity
            WHEN movement_type = 'OUT' THEN -quantity
            ELSE 0
          END) as quantity,
          MAX(created_at) as last_updated
        FROM stock_movements
        WHERE location_id = ${locationId}
        GROUP BY product_id, location_id, batch_number, expiry_date
        HAVING SUM(CASE 
          WHEN movement_type = 'IN' THEN quantity
          WHEN movement_type = 'OUT' THEN -quantity
          ELSE 0
        END) > 0
        ORDER BY product_id, batch_number
      `;

      return result as StockBalance[];
    } catch (error) {
      throw new Error(`Failed to get stock balance report: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Check for low stock alerts
   * @param companyId Company ID
   * @param threshold Minimum stock threshold
   * @param tx Prisma transaction object
   * @returns Products with low stock
   */
  public async getLowStockAlerts(
    companyId: string,
    threshold: number = 10,
    tx?: PrismaClient
  ): Promise<any[]> {
    const client = tx || this.prisma;

    try {
      const result = await client.$queryRaw<any[]>`
        WITH current_stock AS (
          SELECT 
            product_id,
            location_id,
            SUM(CASE 
              WHEN movement_type = 'IN' THEN quantity
              WHEN movement_type = 'OUT' THEN -quantity
              ELSE 0
            END) as current_quantity
          FROM stock_movements
          WHERE company_id = ${companyId}
          GROUP BY product_id, location_id
        )
        SELECT 
          cs.product_id,
          cs.location_id,
          cs.current_quantity,
          p.name as product_name,
          p.min_stock_level
        FROM current_stock cs
        JOIN products p ON cs.product_id = p.id
        WHERE cs.current_quantity <= LEAST(${threshold}, COALESCE(p.min_stock_level, ${threshold}))
          AND cs.current_quantity > 0
        ORDER BY cs.current_quantity ASC
      `;

      return result;
    } catch (error) {
      throw new Error(`Failed to get low stock alerts: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Update stock balance after movement
   * @param movement Stock movement
   * @param tx Prisma transaction object
   */
  private async updateStockBalance(movement: StockMovement, tx: PrismaClient): Promise<void> {
    // This method would typically update a stock_balance table for better performance
    // For now, we're calculating balances on-the-fly from movements
    // In production, you'd want to maintain a separate stock_balance table
  }

  /**
   * Close the database connection
   */
  public async disconnect(): Promise<void> {
    await this.prisma.$disconnect();
  }
}