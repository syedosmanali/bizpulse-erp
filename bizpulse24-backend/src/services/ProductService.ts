import { PrismaClient } from '@prisma/client';
import { GSTEngine } from '../engines/GSTEngine';
import { AuditLogger } from '../engines/AuditLogger';

// Interface for product creation/update
export interface ProductInput {
  sku: string;
  barcode?: string;
  name: string;
  description?: string;
  categoryId?: string;
  brandId?: string;
  hsnCode?: string;
  gstRate: number;
  unit: string;
  costPrice: number;
  sellingPrice: number;
  mrp?: number;
  minStockLevel?: number;
  maxStockLevel?: number;
  reorderLevel?: number;
  hasBatchTracking?: boolean;
  hasExpiryTracking?: boolean;
  isActive?: boolean;
}

// Interface for product search filters
export interface ProductSearchFilters {
  categoryId?: string;
  brandId?: string;
  search?: string;
  isActive?: boolean;
  hasBatchTracking?: boolean;
  hasExpiryTracking?: boolean;
  page?: number;
  limit?: number;
}

/**
 * Product Service for Product Master Management
 * Handles CRUD operations for products with validation and business rules
 */
export class ProductService {
  private prisma: PrismaClient;
  private gstEngine: GSTEngine;
  private auditLogger: AuditLogger;

  constructor() {
    this.prisma = new PrismaClient();
    this.gstEngine = new GSTEngine();
    this.auditLogger = new AuditLogger();
  }

  /**
   * Create a new product with validation
   * @param productData Product input data
   * @param userId User ID creating the product
   * @param companyId Company ID
   * @returns Created product
   */
  public async createProduct(
    productData: ProductInput,
    userId: string,
    companyId: string
  ): Promise<any> {
    try {
      // Validate HSN code format
      if (productData.hsnCode && !this.isValidHSNCode(productData.hsnCode)) {
        throw new Error('Invalid HSN code format. Must be 2, 4, 6, or 8 digits');
      }

      // Validate GST rate
      if (!this.isValidGSTRate(productData.gstRate)) {
        throw new Error('Invalid GST rate. Must be one of: 0, 5, 12, 18, 28');
      }

      // Check for duplicate SKU
      const existingSku = await this.prisma.product.findFirst({
        where: {
          sku: productData.sku,
          companyId: companyId
        }
      });

      if (existingSku) {
        throw new Error(`Product with SKU '${productData.sku}' already exists`);
      }

      // Check for duplicate barcode if provided
      if (productData.barcode) {
        const existingBarcode = await this.prisma.product.findFirst({
          where: {
            barcode: productData.barcode,
            companyId: companyId
          }
        });

        if (existingBarcode) {
          throw new Error(`Product with barcode '${productData.barcode}' already exists`);
        }
      }

      // Validate category exists
      if (productData.categoryId) {
        const category = await this.prisma.category.findFirst({
          where: {
            id: productData.categoryId,
            companyId: companyId
          }
        });

        if (!category) {
          throw new Error('Category not found');
        }
      }

      // Validate brand exists
      if (productData.brandId) {
        const brand = await this.prisma.brand.findFirst({
          where: {
            id: productData.brandId,
            companyId: companyId
          }
        });

        if (!brand) {
          throw new Error('Brand not found');
        }
      }

      // Validate pricing logic
      if (productData.costPrice > productData.sellingPrice) {
        throw new Error('Cost price cannot be greater than selling price');
      }

      if (productData.mrp && productData.mrp < productData.sellingPrice) {
        throw new Error('MRP cannot be less than selling price');
      }

      // Create product
      const product = await this.prisma.product.create({
        data: {
          ...productData,
          companyId: companyId,
          createdBy: userId,
          updatedBy: userId
        },
        include: {
          category: true,
          brand: true
        }
      });

      // Log audit entry
      await this.auditLogger.log(
        'CREATE',
        'INVENTORY',
        'PRODUCT',
        product.id,
        userId,
        companyId,
        undefined,
        product
      );

      return product;
    } catch (error) {
      throw new Error(`Failed to create product: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get product by ID
   * @param productId Product ID
   * @param companyId Company ID
   * @returns Product details
   */
  public async getProductById(productId: string, companyId: string): Promise<any> {
    try {
      const product = await this.prisma.product.findFirst({
        where: {
          id: productId,
          companyId: companyId
        },
        include: {
          category: true,
          brand: true,
          stock: {
            include: {
              location: true
            }
          }
        }
      });

      if (!product) {
        throw new Error('Product not found');
      }

      return product;
    } catch (error) {
      throw new Error(`Failed to get product: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Update product
   * @param productId Product ID
   * @param productData Updated product data
   * @param userId User ID updating the product
   * @param companyId Company ID
   * @returns Updated product
   */
  public async updateProduct(
    productId: string,
    productData: Partial<ProductInput>,
    userId: string,
    companyId: string
  ): Promise<any> {
    try {
      // Check if product exists
      const existingProduct = await this.prisma.product.findFirst({
        where: {
          id: productId,
          companyId: companyId
        }
      });

      if (!existingProduct) {
        throw new Error('Product not found');
      }

      // Validate HSN code if provided
      if (productData.hsnCode && !this.isValidHSNCode(productData.hsnCode)) {
        throw new Error('Invalid HSN code format. Must be 2, 4, 6, or 8 digits');
      }

      // Validate GST rate if provided
      if (productData.gstRate !== undefined && !this.isValidGSTRate(productData.gstRate)) {
        throw new Error('Invalid GST rate. Must be one of: 0, 5, 12, 18, 28');
      }

      // Check for duplicate SKU if changed
      if (productData.sku && productData.sku !== existingProduct.sku) {
        const existingSku = await this.prisma.product.findFirst({
          where: {
            sku: productData.sku,
            companyId: companyId,
            id: { not: productId }
          }
        });

        if (existingSku) {
          throw new Error(`Product with SKU '${productData.sku}' already exists`);
        }
      }

      // Check for duplicate barcode if changed
      if (productData.barcode && productData.barcode !== existingProduct.barcode) {
        const existingBarcode = await this.prisma.product.findFirst({
          where: {
            barcode: productData.barcode,
            companyId: companyId,
            id: { not: productId }
          }
        });

        if (existingBarcode) {
          throw new Error(`Product with barcode '${productData.barcode}' already exists`);
        }
      }

      // Validate pricing logic if changed
      const newCostPrice = productData.costPrice ?? existingProduct.costPrice;
      const newSellingPrice = productData.sellingPrice ?? existingProduct.sellingPrice;
      const newMrp = productData.mrp ?? existingProduct.mrp;

      if (newCostPrice > newSellingPrice) {
        throw new Error('Cost price cannot be greater than selling price');
      }

      if (newMrp && newMrp < newSellingPrice) {
        throw new Error('MRP cannot be less than selling price');
      }

      // Update product
      const oldValues = { ...existingProduct };
      const updatedProduct = await this.prisma.product.update({
        where: { id: productId },
        data: {
          ...productData,
          updatedBy: userId,
          updatedAt: new Date()
        },
        include: {
          category: true,
          brand: true
        }
      });

      // Log audit entry
      await this.auditLogger.log(
        'UPDATE',
        'INVENTORY',
        'PRODUCT',
        productId,
        userId,
        companyId,
        oldValues,
        updatedProduct
      );

      return updatedProduct;
    } catch (error) {
      throw new Error(`Failed to update product: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Soft delete product
   * @param productId Product ID
   * @param userId User ID deleting the product
   * @param companyId Company ID
   */
  public async deleteProduct(productId: string, userId: string, companyId: string): Promise<void> {
    try {
      // Check if product exists
      const existingProduct = await this.prisma.product.findFirst({
        where: {
          id: productId,
          companyId: companyId
        }
      });

      if (!existingProduct) {
        throw new Error('Product not found');
      }

      // Check if product has stock (cannot delete if stock exists)
      const stockCount = await this.prisma.stock.count({
        where: {
          productId: productId,
          quantity: { gt: 0 }
        }
      });

      if (stockCount > 0) {
        throw new Error('Cannot delete product with existing stock. Please transfer or adjust stock to zero first.');
      }

      // Soft delete by setting isActive to false
      const oldValues = { ...existingProduct };
      await this.prisma.product.update({
        where: { id: productId },
        data: {
          isActive: false,
          updatedBy: userId,
          updatedAt: new Date()
        }
      });

      // Log audit entry
      await this.auditLogger.log(
        'DELETE',
        'INVENTORY',
        'PRODUCT',
        productId,
        userId,
        companyId,
        oldValues,
        { isActive: false }
      );
    } catch (error) {
      throw new Error(`Failed to delete product: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Search products with filters
   * @param filters Search filters
   * @param companyId Company ID
   * @returns Products list with pagination
   */
  public async searchProducts(
    filters: ProductSearchFilters,
    companyId: string
  ): Promise<{ products: any[]; total: number; page: number; limit: number }> {
    try {
      const page = filters.page || 1;
      const limit = filters.limit || 20;
      const skip = (page - 1) * limit;

      const whereConditions: any = {
        companyId: companyId
      };

      if (filters.categoryId) {
        whereConditions.categoryId = filters.categoryId;
      }

      if (filters.brandId) {
        whereConditions.brandId = filters.brandId;
      }

      if (filters.isActive !== undefined) {
        whereConditions.isActive = filters.isActive;
      }

      if (filters.hasBatchTracking !== undefined) {
        whereConditions.hasBatchTracking = filters.hasBatchTracking;
      }

      if (filters.hasExpiryTracking !== undefined) {
        whereConditions.hasExpiryTracking = filters.hasExpiryTracking;
      }

      if (filters.search) {
        whereConditions.OR = [
          { name: { contains: filters.search, mode: 'insensitive' } },
          { sku: { contains: filters.search, mode: 'insensitive' } },
          { barcode: { contains: filters.search, mode: 'insensitive' } }
        ];
      }

      const [products, total] = await Promise.all([
        this.prisma.product.findMany({
          where: whereConditions,
          include: {
            category: true,
            brand: true,
            stock: {
              where: {
                quantity: { gt: 0 }
              },
              select: {
                location: { select: { name: true } },
                quantity: true,
                availableQuantity: true
              }
            }
          },
          orderBy: { createdAt: 'desc' },
          skip,
          take: limit
        }),
        this.prisma.product.count({ where: whereConditions })
      ]);

      return {
        products,
        total,
        page,
        limit
      };
    } catch (error) {
      throw new Error(`Failed to search products: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Search product by barcode or SKU
   * @param code Barcode or SKU
   * @param companyId Company ID
   * @returns Product details
   */
  public async searchByCode(code: string, companyId: string): Promise<any> {
    try {
      const product = await this.prisma.product.findFirst({
        where: {
          companyId: companyId,
          isActive: true,
          OR: [
            { sku: code },
            { barcode: code }
          ]
        },
        include: {
          category: true,
          brand: true,
          stock: {
            include: {
              location: true
            }
          }
        }
      });

      if (!product) {
        throw new Error('Product not found');
      }

      return product;
    } catch (error) {
      throw new Error(`Failed to search product by code: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Validate HSN code format
   * @param hsnCode HSN code to validate
   * @returns boolean indicating if valid
   */
  private isValidHSNCode(hsnCode: string): boolean {
    return /^[0-9]{2,8}$/.test(hsnCode);
  }

  /**
   * Validate GST rate
   * @param rate GST rate to validate
   * @returns boolean indicating if valid
   */
  private isValidGSTRate(rate: number): boolean {
    return [0, 5, 12, 18, 28].includes(rate);
  }

  /**
   * Close database connections
   */
  public async disconnect(): Promise<void> {
    await this.prisma.$disconnect();
    await this.gstEngine.disconnect();
    await this.auditLogger.disconnect();
  }
}