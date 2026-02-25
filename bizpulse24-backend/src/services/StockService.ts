import { PrismaClient } from '@prisma/client';
import { StockLedger } from '../engines/StockLedger';
import { AuditLogger } from '../engines/AuditLogger';
import { MovementType } from '../models/types';

// Interface for stock transfer
export interface StockTransferInput {
  productId: string;
  fromLocationId: string;
  toLocationId: string;
  quantity: number;
  batchNumber?: string;
  remarks?: string;
}

// Interface for stock adjustment
export interface StockAdjustmentInput {
  productId: string;
  locationId: string;
  quantity: number;
  batchNumber?: string;
  expiryDate?: Date;
  remarks?: string;
  referenceType: string;
  referenceId: string;
}

// Interface for stock filters
export interface StockFilters {
  productId?: string;
  locationId?: string;
  batchNumber?: string;
  hasStock?: boolean;
  page?: number;
  limit?: number;
}

/**
 * Stock Service for Stock Management Operations
 * Handles stock transfers, adjustments, and queries
 */
export class StockService {
  private prisma: PrismaClient;
  private stockLedger: StockLedger;
  private auditLogger: AuditLogger;

  constructor() {
    this.prisma = new PrismaClient();
    this.stockLedger = new StockLedger();
    this.auditLogger = new AuditLogger();
  }

  /**
   * Transfer stock between locations
   * @param transferData Transfer details
   * @param userId User performing the transfer
   * @param companyId Company ID
   */
  public async transferStock(
    transferData: StockTransferInput,
    userId: string,
    companyId: string
  ): Promise<void> {
    try {
      const { productId, fromLocationId, toLocationId, quantity, batchNumber, remarks } = transferData;

      // Validate locations exist and belong to company
      const [fromLocation, toLocation] = await Promise.all([
        this.prisma.location.findFirst({
          where: { id: fromLocationId, companyId }
        }),
        this.prisma.location.findFirst({
          where: { id: toLocationId, companyId }
        })
      ]);

      if (!fromLocation) throw new Error('Source location not found');
      if (!toLocation) throw new Error('Destination location not found');
      if (fromLocationId === toLocationId) throw new Error('Cannot transfer to the same location');

      // Check stock availability
      const currentStock = await this.stockLedger.getCurrentStock(productId, fromLocationId, batchNumber);
      if (currentStock < quantity) {
        throw new Error(`Insufficient stock. Available: ${currentStock}, Required: ${quantity}`);
      }

      // Start transaction
      await this.prisma.$transaction(async (tx) => {
        // Record OUT movement from source location
        const outMovement = {
          productId,
          locationId: fromLocationId,
          movementType: MovementType.OUT,
          quantity,
          batchNumber,
          referenceType: 'STOCK_TRANSFER',
          referenceId: `TRANSFER_${Date.now()}`,
          userId,
          companyId,
          remarks: remarks ? `Transfer OUT: ${remarks}` : 'Stock transfer OUT'
        };

        await this.stockLedger.recordMovement(outMovement, tx);

        // Record IN movement to destination location
        const inMovement = {
          ...outMovement,
          locationId: toLocationId,
          movementType: MovementType.IN,
          remarks: remarks ? `Transfer IN: ${remarks}` : 'Stock transfer IN'
        };

        await this.stockLedger.recordMovement(inMovement, tx);

        // Log audit entry
        await this.auditLogger.log(
          'TRANSFER',
          'INVENTORY',
          'STOCK',
          `TRANSFER_${productId}_${fromLocationId}_to_${toLocationId}`,
          userId,
          companyId,
          undefined,
          {
            productId,
            fromLocationId,
            toLocationId,
            quantity,
            batchNumber,
            remarks
          },
          tx
        );
      });
    } catch (error) {
      throw new Error(`Failed to transfer stock: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Adjust stock manually (increase or decrease)
   * @param adjustmentData Adjustment details
   * @param userId User performing the adjustment
   * @param companyId Company ID
   */
  public async adjustStock(
    adjustmentData: StockAdjustmentInput,
    userId: string,
    companyId: string
  ): Promise<void> {
    try {
      const { productId, locationId, quantity, batchNumber, expiryDate, remarks, referenceType, referenceId } = adjustmentData;

      // Validate location exists
      const location = await this.prisma.location.findFirst({
        where: { id: locationId, companyId }
      });

      if (!location) throw new Error('Location not found');

      // Validate product exists
      const product = await this.prisma.product.findFirst({
        where: { id: productId, companyId }
      });

      if (!product) throw new Error('Product not found');

      // Determine movement type based on quantity sign
      const movementType = quantity >= 0 ? MovementType.IN : MovementType.OUT;
      const absoluteQuantity = Math.abs(quantity);

      // Start transaction
      await this.prisma.$transaction(async (tx) => {
        const movement = {
          productId,
          locationId,
          movementType,
          quantity: absoluteQuantity,
          batchNumber,
          expiryDate,
          referenceType,
          referenceId,
          userId,
          companyId,
          remarks: remarks || `Manual stock adjustment (${quantity >= 0 ? 'IN' : 'OUT'})`
        };

        await this.stockLedger.recordMovement(movement, tx);

        // Log audit entry
        await this.auditLogger.log(
          'ADJUST',
          'INVENTORY',
          'STOCK',
          referenceId,
          userId,
          companyId,
          undefined,
          adjustmentData,
          tx
        );
      });
    } catch (error) {
      throw new Error(`Failed to adjust stock: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get current stock levels
   * @param filters Stock filters
   * @param companyId Company ID
   * @returns Stock levels with pagination
   */
  public async getCurrentStock(
    filters: StockFilters,
    companyId: string
  ): Promise<{ stock: any[]; total: number; page: number; limit: number }> {
    try {
      const page = filters.page || 1;
      const limit = filters.limit || 20;
      const skip = (page - 1) * limit;

      const whereConditions: any = {
        companyId
      };

      if (filters.productId) {
        whereConditions.productId = filters.productId;
      }

      if (filters.locationId) {
        whereConditions.locationId = filters.locationId;
      }

      if (filters.batchNumber) {
        whereConditions.batchNumber = filters.batchNumber;
      }

      if (filters.hasStock !== undefined) {
        whereConditions.quantity = filters.hasStock ? { gt: 0 } : { equals: 0 };
      }

      const [stock, total] = await Promise.all([
        this.prisma.stock.findMany({
          where: whereConditions,
          include: {
            product: {
              select: {
                name: true,
                sku: true,
                unit: true
              }
            },
            location: {
              select: {
                name: true,
                code: true
              }
            }
          },
          orderBy: { lastUpdated: 'desc' },
          skip,
          take: limit
        }),
        this.prisma.stock.count({ where: whereConditions })
      ]);

      return {
        stock,
        total,
        page,
        limit
      };
    } catch (error) {
      throw new Error(`Failed to get current stock: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get stock movement history
   * @param productId Product ID
   * @param locationId Location ID
   * @param startDate Start date
   * @param endDate End date
   * @param companyId Company ID
   * @returns Stock movement history
   */
  public async getStockMovements(
    productId: string,
    locationId: string,
    startDate?: Date,
    endDate?: Date,
    companyId?: string
  ): Promise<any[]> {
    try {
      const filters: any = {
        productId,
        locationId
      };

      if (companyId) {
        filters.companyId = companyId;
      }

      if (startDate) {
        filters.createdAt = { ...filters.createdAt, gte: startDate };
      }

      if (endDate) {
        filters.createdAt = { ...filters.createdAt, lte: endDate };
      }

      const movements = await this.prisma.stockLedger.findMany({
        where: filters,
        include: {
          product: {
            select: {
              name: true,
              sku: true
            }
          },
          location: {
            select: {
              name: true
            }
          }
        },
        orderBy: { createdAt: 'desc' },
        take: 100 // Limit to 100 most recent movements
      });

      return movements;
    } catch (error) {
      throw new Error(`Failed to get stock movements: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get low stock alerts
   * @param companyId Company ID
   * @param threshold Minimum stock threshold
   * @returns Low stock alerts
   */
  public async getLowStockAlerts(companyId: string, threshold: number = 10): Promise<any[]> {
    try {
      return await this.stockLedger.getLowStockAlerts(companyId, threshold);
    } catch (error) {
      throw new Error(`Failed to get low stock alerts: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Acknowledge stock alert
   * @param alertId Alert ID
   * @param userId User acknowledging the alert
   * @param companyId Company ID
   */
  public async acknowledgeAlert(alertId: string, userId: string, companyId: string): Promise<void> {
    try {
      const alert = await this.prisma.stockAlert.findFirst({
        where: {
          id: alertId,
          companyId
        }
      });

      if (!alert) throw new Error('Alert not found');

      await this.prisma.stockAlert.update({
        where: { id: alertId },
        data: {
          isAcknowledged: true,
          acknowledgedBy: userId,
          acknowledgedAt: new Date()
        }
      });

      // Log audit entry
      await this.auditLogger.log(
        'ACKNOWLEDGE',
        'INVENTORY',
        'STOCK_ALERT',
        alertId,
        userId,
        companyId,
        undefined,
        { isAcknowledged: true }
      );
    } catch (error) {
      throw new Error(`Failed to acknowledge alert: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Close database connections
   */
  public async disconnect(): Promise<void> {
    await this.prisma.$disconnect();
    await this.stockLedger.disconnect();
    await this.auditLogger.disconnect();
  }
}