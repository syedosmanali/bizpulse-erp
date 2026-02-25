import { Router, Request, Response } from 'express';
import { ProductService } from '../services/ProductService';
import { authenticate, authorize, AuthRequest } from '../middleware/auth';
import { body, query, param, validationResult } from 'express-validator';
import { UserRole } from '../models/types';

const router = Router();
const productService = new ProductService();

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

/**
 * POST /api/v1/inventory/products
 * Create a new product
 */
router.post(
  '/products',
  authenticate,
  authorize(UserRole.OWNER, UserRole.ADMIN),
  [
    body('sku').notEmpty().withMessage('SKU is required'),
    body('name').notEmpty().withMessage('Product name is required'),
    body('sellingPrice').isNumeric().withMessage('Selling price must be a number'),
    body('gstRate').isNumeric().withMessage('GST rate must be a number'),
    body('hsnCode').optional().isLength({ min: 2, max: 8 }).withMessage('HSN code must be 2-8 digits')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const productData = req.body;
      const userId = req.user!.id;
      const companyId = req.user!.companyId;

      const product = await productService.createProduct(productData, userId, companyId);

      res.status(201).json({
        data: product,
        message: 'Product created successfully'
      });
    } catch (error) {
      res.status(400).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to create product',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * GET /api/v1/inventory/products
 * List products with pagination and filtering
 */
router.get(
  '/products',
  authenticate,
  [
    query('page').optional().isInt({ min: 1 }).withMessage('Page must be a positive integer'),
    query('limit').optional().isInt({ min: 1, max: 100 }).withMessage('Limit must be between 1 and 100'),
    query('categoryId').optional().isUUID().withMessage('Invalid category ID'),
    query('brandId').optional().isUUID().withMessage('Invalid brand ID'),
    query('search').optional().isString().withMessage('Search must be a string'),
    query('isActive').optional().isBoolean().withMessage('isActive must be boolean')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const filters = {
        categoryId: req.query.categoryId as string,
        brandId: req.query.brandId as string,
        search: req.query.search as string,
        isActive: req.query.isActive === 'true' ? true : req.query.isActive === 'false' ? false : undefined,
        page: req.query.page ? parseInt(req.query.page as string) : undefined,
        limit: req.query.limit ? parseInt(req.query.limit as string) : undefined
      };

      const companyId = req.user!.companyId;

      const result = await productService.searchProducts(filters, companyId);

      res.status(200).json({
        data: result.products,
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
          message: error instanceof Error ? error.message : 'Failed to fetch products',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * GET /api/v1/inventory/products/:id
 * Get product details by ID
 */
router.get(
  '/products/:id',
  authenticate,
  [
    param('id').isUUID().withMessage('Invalid product ID')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const productId = req.params.id;
      const companyId = req.user!.companyId;

      const product = await productService.getProductById(productId, companyId);

      res.status(200).json({
        data: product
      });
    } catch (error) {
      if (error instanceof Error && error.message === 'Product not found') {
        return res.status(404).json({
          error: {
            message: 'Product not found',
            timestamp: new Date().toISOString()
          }
        });
      }

      res.status(500).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to fetch product',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * PUT /api/v1/inventory/products/:id
 * Update product
 */
router.put(
  '/products/:id',
  authenticate,
  authorize(UserRole.OWNER, UserRole.ADMIN),
  [
    param('id').isUUID().withMessage('Invalid product ID'),
    body('sellingPrice').optional().isNumeric().withMessage('Selling price must be a number'),
    body('gstRate').optional().isNumeric().withMessage('GST rate must be a number'),
    body('hsnCode').optional().isLength({ min: 2, max: 8 }).withMessage('HSN code must be 2-8 digits')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const productId = req.params.id;
      const productData = req.body;
      const userId = req.user!.id;
      const companyId = req.user!.companyId;

      const updatedProduct = await productService.updateProduct(productId, productData, userId, companyId);

      res.status(200).json({
        data: updatedProduct,
        message: 'Product updated successfully'
      });
    } catch (error) {
      if (error instanceof Error && error.message === 'Product not found') {
        return res.status(404).json({
          error: {
            message: 'Product not found',
            timestamp: new Date().toISOString()
          }
        });
      }

      res.status(400).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to update product',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * DELETE /api/v1/inventory/products/:id
 * Soft delete product
 */
router.delete(
  '/products/:id',
  authenticate,
  authorize(UserRole.OWNER),
  [
    param('id').isUUID().withMessage('Invalid product ID')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const productId = req.params.id;
      const userId = req.user!.id;
      const companyId = req.user!.companyId;

      await productService.deleteProduct(productId, userId, companyId);

      res.status(200).json({
        message: 'Product deleted successfully'
      });
    } catch (error) {
      if (error instanceof Error && error.message === 'Product not found') {
        return res.status(404).json({
          error: {
            message: 'Product not found',
            timestamp: new Date().toISOString()
          }
        });
      }

      res.status(400).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to delete product',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * GET /api/v1/inventory/products/search/:code
 * Search product by barcode or SKU
 */
router.get(
  '/products/search/:code',
  authenticate,
  [
    param('code').notEmpty().withMessage('Search code is required')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const code = req.params.code;
      const companyId = req.user!.companyId;

      const product = await productService.searchByCode(code, companyId);

      res.status(200).json({
        data: product
      });
    } catch (error) {
      if (error instanceof Error && error.message === 'Product not found') {
        return res.status(404).json({
          error: {
            message: 'Product not found',
            timestamp: new Date().toISOString()
          }
        });
      }

      res.status(500).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to search product',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

export default router;