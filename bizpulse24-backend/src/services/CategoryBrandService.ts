import { PrismaClient } from '@prisma/client';
import { AuditLogger } from '../engines/AuditLogger';

// Interface for category creation/update
export interface CategoryInput {
  name: string;
  description?: string;
  parentId?: string;
  isActive?: boolean;
}

// Interface for brand creation/update
export interface BrandInput {
  name: string;
  description?: string;
  isActive?: boolean;
}

/**
 * Category Service for Category Management
 * Handles CRUD operations for product categories
 */
export class CategoryService {
  private prisma: PrismaClient;
  private auditLogger: AuditLogger;

  constructor() {
    this.prisma = new PrismaClient();
    this.auditLogger = new AuditLogger();
  }

  /**
   * Create a new category
   * @param categoryData Category input data
   * @param userId User ID creating the category
   * @param companyId Company ID
   * @returns Created category
   */
  public async createCategory(
    categoryData: CategoryInput,
    userId: string,
    companyId: string
  ): Promise<any> {
    try {
      // Check for duplicate category name
      const existingCategory = await this.prisma.category.findFirst({
        where: {
          name: categoryData.name,
          companyId: companyId
        }
      });

      if (existingCategory) {
        throw new Error(`Category '${categoryData.name}' already exists`);
      }

      // Validate parent category if provided
      if (categoryData.parentId) {
        const parentCategory = await this.prisma.category.findFirst({
          where: {
            id: categoryData.parentId,
            companyId: companyId
          }
        });

        if (!parentCategory) {
          throw new Error('Parent category not found');
        }

        // Prevent circular references
        if (categoryData.parentId === existingCategory?.id) {
          throw new Error('Cannot set category as its own parent');
        }
      }

      // Create category
      const category = await this.prisma.category.create({
        data: {
          ...categoryData,
          companyId: companyId,
          createdBy: userId,
          updatedBy: userId
        },
        include: {
          parent: {
            select: {
              name: true
            }
          },
          children: {
            select: {
              name: true
            }
          }
        }
      });

      // Log audit entry
      await this.auditLogger.log(
        'CREATE',
        'INVENTORY',
        'CATEGORY',
        category.id,
        userId,
        companyId,
        undefined,
        category
      );

      return category;
    } catch (error) {
      throw new Error(`Failed to create category: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get category by ID
   * @param categoryId Category ID
   * @param companyId Company ID
   * @returns Category details
   */
  public async getCategoryById(categoryId: string, companyId: string): Promise<any> {
    try {
      const category = await this.prisma.category.findFirst({
        where: {
          id: categoryId,
          companyId: companyId
        },
        include: {
          parent: {
            select: {
              name: true
            }
          },
          children: {
            select: {
              name: true
            }
          },
          products: {
            select: {
              name: true,
              sku: true
            }
          }
        }
      });

      if (!category) {
        throw new Error('Category not found');
      }

      return category;
    } catch (error) {
      throw new Error(`Failed to get category: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Update category
   * @param categoryId Category ID
   * @param categoryData Updated category data
   * @param userId User ID updating the category
   * @param companyId Company ID
   * @returns Updated category
   */
  public async updateCategory(
    categoryId: string,
    categoryData: Partial<CategoryInput>,
    userId: string,
    companyId: string
  ): Promise<any> {
    try {
      // Check if category exists
      const existingCategory = await this.prisma.category.findFirst({
        where: {
          id: categoryId,
          companyId: companyId
        }
      });

      if (!existingCategory) {
        throw new Error('Category not found');
      }

      // Check for duplicate category name if changed
      if (categoryData.name && categoryData.name !== existingCategory.name) {
        const existingName = await this.prisma.category.findFirst({
          where: {
            name: categoryData.name,
            companyId: companyId,
            id: { not: categoryId }
          }
        });

        if (existingName) {
          throw new Error(`Category '${categoryData.name}' already exists`);
        }
      }

      // Validate parent category if changed
      if (categoryData.parentId && categoryData.parentId !== existingCategory.parentId) {
        const parentCategory = await this.prisma.category.findFirst({
          where: {
            id: categoryData.parentId,
            companyId: companyId
          }
        });

        if (!parentCategory) {
          throw new Error('Parent category not found');
        }

        // Prevent circular references
        if (categoryData.parentId === categoryId) {
          throw new Error('Cannot set category as its own parent');
        }
      }

      // Update category
      const oldValues = { ...existingCategory };
      const updatedCategory = await this.prisma.category.update({
        where: { id: categoryId },
        data: {
          ...categoryData,
          updatedBy: userId,
          updatedAt: new Date()
        },
        include: {
          parent: {
            select: {
              name: true
            }
          },
          children: {
            select: {
              name: true
            }
          }
        }
      });

      // Log audit entry
      await this.auditLogger.log(
        'UPDATE',
        'INVENTORY',
        'CATEGORY',
        categoryId,
        userId,
        companyId,
        oldValues,
        updatedCategory
      );

      return updatedCategory;
    } catch (error) {
      throw new Error(`Failed to update category: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Delete category (soft delete)
   * @param categoryId Category ID
   * @param userId User ID deleting the category
   * @param companyId Company ID
   */
  public async deleteCategory(categoryId: string, userId: string, companyId: string): Promise<void> {
    try {
      // Check if category exists
      const existingCategory = await this.prisma.category.findFirst({
        where: {
          id: categoryId,
          companyId: companyId
        }
      });

      if (!existingCategory) {
        throw new Error('Category not found');
      }

      // Check if category has children
      const childCount = await this.prisma.category.count({
        where: {
          parentId: categoryId
        }
      });

      if (childCount > 0) {
        throw new Error('Cannot delete category with child categories. Delete child categories first.');
      }

      // Check if category has products
      const productCount = await this.prisma.product.count({
        where: {
          categoryId: categoryId
        }
      });

      if (productCount > 0) {
        throw new Error('Cannot delete category with associated products. Reassign products first.');
      }

      // Soft delete by setting isActive to false
      const oldValues = { ...existingCategory };
      await this.prisma.category.update({
        where: { id: categoryId },
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
        'CATEGORY',
        categoryId,
        userId,
        companyId,
        oldValues,
        { isActive: false }
      );
    } catch (error) {
      throw new Error(`Failed to delete category: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * List categories with hierarchical structure
   * @param companyId Company ID
   * @param includeInactive Include inactive categories
   * @returns Category hierarchy
   */
  public async listCategories(companyId: string, includeInactive: boolean = false): Promise<any[]> {
    try {
      const whereConditions: any = {
        companyId: companyId
      };

      if (!includeInactive) {
        whereConditions.isActive = true;
      }

      const categories = await this.prisma.category.findMany({
        where: whereConditions,
        include: {
          parent: {
            select: {
              name: true
            }
          },
          children: {
            where: includeInactive ? {} : { isActive: true },
            select: {
              name: true
            }
          }
        },
        orderBy: { name: 'asc' }
      });

      return categories;
    } catch (error) {
      throw new Error(`Failed to list categories: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }
}

/**
 * Brand Service for Brand Management
 * Handles CRUD operations for product brands
 */
export class BrandService {
  private prisma: PrismaClient;
  private auditLogger: AuditLogger;

  constructor() {
    this.prisma = new PrismaClient();
    this.auditLogger = new AuditLogger();
  }

  /**
   * Create a new brand
   * @param brandData Brand input data
   * @param userId User ID creating the brand
   * @param companyId Company ID
   * @returns Created brand
   */
  public async createBrand(
    brandData: BrandInput,
    userId: string,
    companyId: string
  ): Promise<any> {
    try {
      // Check for duplicate brand name
      const existingBrand = await this.prisma.brand.findFirst({
        where: {
          name: brandData.name,
          companyId: companyId
        }
      });

      if (existingBrand) {
        throw new Error(`Brand '${brandData.name}' already exists`);
      }

      // Create brand
      const brand = await this.prisma.brand.create({
        data: {
          ...brandData,
          companyId: companyId,
          createdBy: userId,
          updatedBy: userId
        }
      });

      // Log audit entry
      await this.auditLogger.log(
        'CREATE',
        'INVENTORY',
        'BRAND',
        brand.id,
        userId,
        companyId,
        undefined,
        brand
      );

      return brand;
    } catch (error) {
      throw new Error(`Failed to create brand: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get brand by ID
   * @param brandId Brand ID
   * @param companyId Company ID
   * @returns Brand details
   */
  public async getBrandById(brandId: string, companyId: string): Promise<any> {
    try {
      const brand = await this.prisma.brand.findFirst({
        where: {
          id: brandId,
          companyId: companyId
        },
        include: {
          products: {
            select: {
              name: true,
              sku: true
            }
          }
        }
      });

      if (!brand) {
        throw new Error('Brand not found');
      }

      return brand;
    } catch (error) {
      throw new Error(`Failed to get brand: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Update brand
   * @param brandId Brand ID
   * @param brandData Updated brand data
   * @param userId User ID updating the brand
   * @param companyId Company ID
   * @returns Updated brand
   */
  public async updateBrand(
    brandId: string,
    brandData: Partial<BrandInput>,
    userId: string,
    companyId: string
  ): Promise<any> {
    try {
      // Check if brand exists
      const existingBrand = await this.prisma.brand.findFirst({
        where: {
          id: brandId,
          companyId: companyId
        }
      });

      if (!existingBrand) {
        throw new Error('Brand not found');
      }

      // Check for duplicate brand name if changed
      if (brandData.name && brandData.name !== existingBrand.name) {
        const existingName = await this.prisma.brand.findFirst({
          where: {
            name: brandData.name,
            companyId: companyId,
            id: { not: brandId }
          }
        });

        if (existingName) {
          throw new Error(`Brand '${brandData.name}' already exists`);
        }
      }

      // Update brand
      const oldValues = { ...existingBrand };
      const updatedBrand = await this.prisma.brand.update({
        where: { id: brandId },
        data: {
          ...brandData,
          updatedBy: userId,
          updatedAt: new Date()
        }
      });

      // Log audit entry
      await this.auditLogger.log(
        'UPDATE',
        'INVENTORY',
        'BRAND',
        brandId,
        userId,
        companyId,
        oldValues,
        updatedBrand
      );

      return updatedBrand;
    } catch (error) {
      throw new Error(`Failed to update brand: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Delete brand (soft delete)
   * @param brandId Brand ID
   * @param userId User ID deleting the brand
   * @param companyId Company ID
   */
  public async deleteBrand(brandId: string, userId: string, companyId: string): Promise<void> {
    try {
      // Check if brand exists
      const existingBrand = await this.prisma.brand.findFirst({
        where: {
          id: brandId,
          companyId: companyId
        }
      });

      if (!existingBrand) {
        throw new Error('Brand not found');
      }

      // Check if brand has products
      const productCount = await this.prisma.product.count({
        where: {
          brandId: brandId
        }
      });

      if (productCount > 0) {
        throw new Error('Cannot delete brand with associated products. Reassign products first.');
      }

      // Soft delete by setting isActive to false
      const oldValues = { ...existingBrand };
      await this.prisma.brand.update({
        where: { id: brandId },
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
        'BRAND',
        brandId,
        userId,
        companyId,
        oldValues,
        { isActive: false }
      );
    } catch (error) {
      throw new Error(`Failed to delete brand: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * List brands
   * @param companyId Company ID
   * @param includeInactive Include inactive brands
   * @returns List of brands
   */
  public async listBrands(companyId: string, includeInactive: boolean = false): Promise<any[]> {
    try {
      const whereConditions: any = {
        companyId: companyId
      };

      if (!includeInactive) {
        whereConditions.isActive = true;
      }

      const brands = await this.prisma.brand.findMany({
        where: whereConditions,
        include: {
          products: {
            select: {
              name: true,
              sku: true
            }
          }
        },
        orderBy: { name: 'asc' }
      });

      return brands;
    } catch (error) {
      throw new Error(`Failed to list brands: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Close database connections
   */
  public async disconnect(): Promise<void> {
    await this.prisma.$disconnect();
    await this.auditLogger.disconnect();
  }
}