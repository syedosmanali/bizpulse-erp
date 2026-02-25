import { Router, Request, Response } from 'express';
import { StockService } from '../services/StockService';
import { CategoryService, BrandService } from '../services/CategoryBrandService';
import { authenticate, authorize, AuthRequest } from '../middleware/auth';
import { body, query, param, validationResult } from 'express-validator';
import { UserRole } from '../models/types';

const router = Router();
const stockService = new StockService();
const categoryService = new CategoryService();
const brandService = new BrandService();

// Validation middleware
const handleValidation = (req: Request, res: Response, next: any) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      error: {
        message: 'Validation failed',
        details: errors.array()
      }
    });
  }
  next();
};

// ==================== STOCK MANAGEMENT APIs ====================

/**
 * GET /api/v1/inventory/stock/current
 * Get current stock levels
 */
router.get(
  '/stock/current',
  authenticate,
  [
    query('page').optional().isInt({ min: 1 }).withMessage('Page must be a positive integer'),
    query('limit').optional().isInt({ min: 1, max: 100 }).withMessage('Limit must be between 1 and 100'),
    query('productId').optional().isUUID().withMessage('Invalid product ID'),
    query('locationId').optional().isUUID().withMessage('Invalid location ID'),
    query('hasStock').optional().isBoolean().withMessage('hasStock must be boolean')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const filters = {
        productId: req.query.productId as string,
        locationId: req.query.locationId as string,
        hasStock: req.query.hasStock === 'true' ? true : req.query.hasStock === 'false' ? false : undefined,
        page: req.query.page ? parseInt(req.query.page as string) : undefined,
        limit: req.query.limit ? parseInt(req.query.limit as string) : undefined
      };

      const companyId = req.user!.companyId;

      const result = await stockService.getCurrentStock(filters, companyId);

      res.status(200).json({
        data: result.stock,
        metadata: {
          total: result.total,
          page: result.page,
          limit: result.limit,
          totalPages: Math.ceil(result.total / result.limit)
        }
      });
    } catch (error) {
      res.status(500).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to fetch stock',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * POST /api/v1/inventory/stock/transfer
 * Transfer stock between locations
 */
router.post(
  '/stock/transfer',
  authenticate,
  authorize(UserRole.OWNER, UserRole.ADMIN),
  [
    body('productId').isUUID().withMessage('Invalid product ID'),
    body('fromLocationId').isUUID().withMessage('Invalid source location ID'),
    body('toLocationId').isUUID().withMessage('Invalid destination location ID'),
    body('quantity').isNumeric().withMessage('Quantity must be a number').isFloat({ gt: 0 }).withMessage('Quantity must be greater than 0')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const transferData = req.body;
      const userId = req.user!.id;
      const companyId = req.user!.companyId;

      await stockService.transferStock(transferData, userId, companyId);

      res.status(200).json({
        message: 'Stock transferred successfully'
      });
    } catch (error) {
      res.status(400).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to transfer stock',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * POST /api/v1/inventory/stock/adjust
 * Manual stock adjustment
 */
router.post(
  '/stock/adjust',
  authenticate,
  authorize(UserRole.OWNER, UserRole.ADMIN),
  [
    body('productId').isUUID().withMessage('Invalid product ID'),
    body('locationId').isUUID().withMessage('Invalid location ID'),
    body('quantity').isNumeric().withMessage('Quantity must be a number'),
    body('referenceType').notEmpty().withMessage('Reference type is required'),
    body('referenceId').notEmpty().withMessage('Reference ID is required')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const adjustmentData = req.body;
      const userId = req.user!.id;
      const companyId = req.user!.companyId;

      await stockService.adjustStock(adjustmentData, userId, companyId);

      res.status(200).json({
        message: 'Stock adjusted successfully'
      });
    } catch (error) {
      res.status(400).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to adjust stock',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * GET /api/v1/inventory/stock/movements
 * Get stock movement history
 */
router.get(
  '/stock/movements',
  authenticate,
  [
    query('productId').isUUID().withMessage('Invalid product ID'),
    query('locationId').isUUID().withMessage('Invalid location ID'),
    query('startDate').optional().isISO8601().withMessage('Invalid start date'),
    query('endDate').optional().isISO8601().withMessage('Invalid end date')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const { productId, locationId, startDate, endDate } = req.query;
      const companyId = req.user!.companyId;

      const movements = await stockService.getStockMovements(
        productId as string,
        locationId as string,
        startDate ? new Date(startDate as string) : undefined,
        endDate ? new Date(endDate as string) : undefined,
        companyId
      );

      res.status(200).json({
        data: movements
      });
    } catch (error) {
      res.status(500).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to fetch stock movements',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * GET /api/v1/inventory/stock/alerts
 * Get low stock alerts
 */
router.get(
  '/stock/alerts',
  authenticate,
  [
    query('threshold').optional().isInt({ min: 0 }).withMessage('Threshold must be a non-negative integer')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const threshold = req.query.threshold ? parseInt(req.query.threshold as string) : 10;
      const companyId = req.user!.companyId;

      const alerts = await stockService.getLowStockAlerts(companyId, threshold);

      res.status(200).json({
        data: alerts
      });
    } catch (error) {
      res.status(500).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to fetch stock alerts',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * PUT /api/v1/inventory/stock/alerts/:id/acknowledge
 * Acknowledge stock alert
 */
router.put(
  '/stock/alerts/:id/acknowledge',
  authenticate,
  authorize(UserRole.OWNER, UserRole.ADMIN),
  [
    param('id').isUUID().withMessage('Invalid alert ID')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const alertId = req.params.id;
      const userId = req.user!.id;
      const companyId = req.user!.companyId;

      await stockService.acknowledgeAlert(alertId, userId, companyId);

      res.status(200).json({
        message: 'Alert acknowledged successfully'
      });
    } catch (error) {
      if (error instanceof Error && error.message === 'Alert not found') {
        return res.status(404).json({
          error: {
            message: 'Alert not found',
            timestamp: new Date().toISOString()
          }
        });
      }

      res.status(400).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to acknowledge alert',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

// ==================== CATEGORY MANAGEMENT APIs ====================

/**
 * POST /api/v1/inventory/categories
 * Create category
 */
router.post(
  '/categories',
  authenticate,
  authorize(UserRole.OWNER, UserRole.ADMIN),
  [
    body('name').notEmpty().withMessage('Category name is required'),
    body('parentId').optional().isUUID().withMessage('Invalid parent category ID')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const categoryData = req.body;
      const userId = req.user!.id;
      const companyId = req.user!.companyId;

      const category = await categoryService.createCategory(categoryData, userId, companyId);

      res.status(201).json({
        data: category,
        message: 'Category created successfully'
      });
    } catch (error) {
      res.status(400).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to create category',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * GET /api/v1/inventory/categories
 * List categories
 */
router.get(
  '/categories',
  authenticate,
  [
    query('includeInactive').optional().isBoolean().withMessage('includeInactive must be boolean')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const includeInactive = req.query.includeInactive === 'true';
      const companyId = req.user!.companyId;

      const categories = await categoryService.listCategories(companyId, includeInactive);

      res.status(200).json({
        data: categories
      });
    } catch (error) {
      res.status(500).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to fetch categories',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * GET /api/v1/inventory/categories/:id
 * Get category details
 */
router.get(
  '/categories/:id',
  authenticate,
  [
    param('id').isUUID().withMessage('Invalid category ID')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const categoryId = req.params.id;
      const companyId = req.user!.companyId;

      const category = await categoryService.getCategoryById(categoryId, companyId);

      res.status(200).json({
        data: category
      });
    } catch (error) {
      if (error instanceof Error && error.message === 'Category not found') {
        return res.status(404).json({
          error: {
            message: 'Category not found',
            timestamp: new Date().toISOString()
          }
        });
      }

      res.status(500).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to fetch category',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * PUT /api/v1/inventory/categories/:id
 * Update category
 */
router.put(
  '/categories/:id',
  authenticate,
  authorize(UserRole.OWNER, UserRole.ADMIN),
  [
    param('id').isUUID().withMessage('Invalid category ID'),
    body('parentId').optional().isUUID().withMessage('Invalid parent category ID')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const categoryId = req.params.id;
      const categoryData = req.body;
      const userId = req.user!.id;
      const companyId = req.user!.companyId;

      const updatedCategory = await categoryService.updateCategory(categoryId, categoryData, userId, companyId);

      res.status(200).json({
        data: updatedCategory,
        message: 'Category updated successfully'
      });
    } catch (error) {
      if (error instanceof Error && error.message === 'Category not found') {
        return res.status(404).json({
          error: {
            message: 'Category not found',
            timestamp: new Date().toISOString()
          }
        });
      }

      res.status(400).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to update category',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * DELETE /api/v1/inventory/categories/:id
 * Delete category (soft delete)
 */
router.delete(
  '/categories/:id',
  authenticate,
  authorize(UserRole.OWNER),
  [
    param('id').isUUID().withMessage('Invalid category ID')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const categoryId = req.params.id;
      const userId = req.user!.id;
      const companyId = req.user!.companyId;

      await categoryService.deleteCategory(categoryId, userId, companyId);

      res.status(200).json({
        message: 'Category deleted successfully'
      });
    } catch (error) {
      if (error instanceof Error && error.message === 'Category not found') {
        return res.status(404).json({
          error: {
            message: 'Category not found',
            timestamp: new Date().toISOString()
          }
        });
      }

      res.status(400).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to delete category',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

// ==================== BRAND MANAGEMENT APIs ====================

/**
 * POST /api/v1/inventory/brands
 * Create brand
 */
router.post(
  '/brands',
  authenticate,
  authorize(UserRole.OWNER, UserRole.ADMIN),
  [
    body('name').notEmpty().withMessage('Brand name is required')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const brandData = req.body;
      const userId = req.user!.id;
      const companyId = req.user!.companyId;

      const brand = await brandService.createBrand(brandData, userId, companyId);

      res.status(201).json({
        data: brand,
        message: 'Brand created successfully'
      });
    } catch (error) {
      res.status(400).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to create brand',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * GET /api/v1/inventory/brands
 * List brands
 */
router.get(
  '/brands',
  authenticate,
  [
    query('includeInactive').optional().isBoolean().withMessage('includeInactive must be boolean')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const includeInactive = req.query.includeInactive === 'true';
      const companyId = req.user!.companyId;

      const brands = await brandService.listBrands(companyId, includeInactive);

      res.status(200).json({
        data: brands
      });
    } catch (error) {
      res.status(500).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to fetch brands',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * GET /api/v1/inventory/brands/:id
 * Get brand details
 */
router.get(
  '/brands/:id',
  authenticate,
  [
    param('id').isUUID().withMessage('Invalid brand ID')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const brandId = req.params.id;
      const companyId = req.user!.companyId;

      const brand = await brandService.getBrandById(brandId, companyId);

      res.status(200).json({
        data: brand
      });
    } catch (error) {
      if (error instanceof Error && error.message === 'Brand not found') {
        return res.status(404).json({
          error: {
            message: 'Brand not found',
            timestamp: new Date().toISOString()
          }
        });
      }

      res.status(500).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to fetch brand',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * PUT /api/v1/inventory/brands/:id
 * Update brand
 */
router.put(
  '/brands/:id',
  authenticate,
  authorize(UserRole.OWNER, UserRole.ADMIN),
  [
    param('id').isUUID().withMessage('Invalid brand ID')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const brandId = req.params.id;
      const brandData = req.body;
      const userId = req.user!.id;
      const companyId = req.user!.companyId;

      const updatedBrand = await brandService.updateBrand(brandId, brandData, userId, companyId);

      res.status(200).json({
        data: updatedBrand,
        message: 'Brand updated successfully'
      });
    } catch (error) {
      if (error instanceof Error && error.message === 'Brand not found') {
        return res.status(404).json({
          error: {
            message: 'Brand not found',
            timestamp: new Date().toISOString()
          }
        });
      }

      res.status(400).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to update brand',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * DELETE /api/v1/inventory/brands/:id
 * Delete brand (soft delete)
 */
router.delete(
  '/brands/:id',
  authenticate,
  authorize(UserRole.OWNER),
  [
    param('id').isUUID().withMessage('Invalid brand ID')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const brandId = req.params.id;
      const userId = req.user!.id;
      const companyId = req.user!.companyId;

      await brandService.deleteBrand(brandId, userId, companyId);

      res.status(200).json({
        message: 'Brand deleted successfully'
      });
    } catch (error) {
      if (error instanceof Error && error.message === 'Brand not found') {
        return res.status(404).json({
          error: {
            message: 'Brand not found',
            timestamp: new Date().toISOString()
          }
        });
      }

      res.status(400).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to delete brand',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

export default router;