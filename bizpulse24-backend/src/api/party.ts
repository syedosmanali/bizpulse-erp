import { Router, Request, Response } from 'express';
import { CustomerService, VendorService } from '../services/PartyService';
import { authenticate, authorize, AuthRequest } from '../middleware/auth';
import { body, query, param, validationResult } from 'express-validator';
import { UserRole } from '../models/types';

const router = Router();
const customerService = new CustomerService();
const vendorService = new VendorService();

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

// ==================== CUSTOMER MANAGEMENT APIs ====================

/**
 * POST /api/v1/party/customers
 * Create customer
 */
router.post(
  '/customers',
  authenticate,
  authorize(UserRole.OWNER, UserRole.ADMIN),
  [
    body('customerCode').notEmpty().withMessage('Customer code is required'),
    body('companyName').notEmpty().withMessage('Company name is required'),
    body('gstin').optional().isLength({ min: 15, max: 15 }).withMessage('GSTIN must be 15 characters'),
    body('pan').optional().isLength({ min: 10, max: 10 }).withMessage('PAN must be 10 characters'),
    body('email').optional().isEmail().withMessage('Invalid email format'),
    body('creditLimit').optional().isNumeric().withMessage('Credit limit must be a number'),
    body('creditDays').optional().isInt({ min: 0 }).withMessage('Credit days must be non-negative')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const customerData = req.body;
      const userId = req.user!.id;
      const companyId = req.user!.companyId;

      // Validate GSTIN format if provided
      if (customerData.gstin && !CustomerService.validateGSTIN(customerData.gstin)) {
        return res.status(400).json({
          error: {
            message: 'Invalid GSTIN format. Expected format: 22AAAAA0000A1Z5',
            timestamp: new Date().toISOString()
          }
        });
      }

      // Validate PAN format if provided
      if (customerData.pan && !CustomerService.validatePAN(customerData.pan)) {
        return res.status(400).json({
          error: {
            message: 'Invalid PAN format. Expected format: AAAAA0000A',
            timestamp: new Date().toISOString()
          }
        });
      }

      const customer = await customerService.createCustomer(customerData, userId, companyId);

      res.status(201).json({
        data: customer,
        message: 'Customer created successfully'
      });
    } catch (error) {
      res.status(400).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to create customer',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * GET /api/v1/party/customers
 * List customers
 */
router.get(
  '/customers',
  authenticate,
  [
    query('page').optional().isInt({ min: 1 }).withMessage('Page must be a positive integer'),
    query('limit').optional().isInt({ min: 1, max: 100 }).withMessage('Limit must be between 1 and 100'),
    query('isActive').optional().isBoolean().withMessage('isActive must be boolean'),
    query('gstin').optional().isLength({ min: 15, max: 15 }).withMessage('GSTIN must be 15 characters'),
    query('search').optional().isString().withMessage('Search must be a string')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const filters = {
        isActive: req.query.isActive === 'true' ? true : req.query.isActive === 'false' ? false : undefined,
        gstin: req.query.gstin as string,
        search: req.query.search as string
      };

      const page = req.query.page ? parseInt(req.query.page as string) : 1;
      const limit = req.query.limit ? parseInt(req.query.limit as string) : 20;
      const companyId = req.user!.companyId;

      const result = await customerService.listCustomers(companyId, filters, page, limit);

      res.status(200).json({
        data: result.customers,
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
          message: error instanceof Error ? error.message : 'Failed to fetch customers',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * GET /api/v1/party/customers/:id
 * Get customer details
 */
router.get(
  '/customers/:id',
  authenticate,
  [
    param('id').isUUID().withMessage('Invalid customer ID')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const customerId = req.params.id;
      const companyId = req.user!.companyId;

      const customer = await customerService.getCustomerById(customerId, companyId);

      res.status(200).json({
        data: customer
      });
    } catch (error) {
      if (error instanceof Error && error.message === 'Customer not found') {
        return res.status(404).json({
          error: {
            message: 'Customer not found',
            timestamp: new Date().toISOString()
          }
        });
      }

      res.status(500).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to fetch customer',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * PUT /api/v1/party/customers/:id
 * Update customer
 */
router.put(
  '/customers/:id',
  authenticate,
  authorize(UserRole.OWNER, UserRole.ADMIN),
  [
    param('id').isUUID().withMessage('Invalid customer ID'),
    body('gstin').optional().isLength({ min: 15, max: 15 }).withMessage('GSTIN must be 15 characters'),
    body('pan').optional().isLength({ min: 10, max: 10 }).withMessage('PAN must be 10 characters'),
    body('email').optional().isEmail().withMessage('Invalid email format'),
    body('creditLimit').optional().isNumeric().withMessage('Credit limit must be a number'),
    body('creditDays').optional().isInt({ min: 0 }).withMessage('Credit days must be non-negative')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const customerId = req.params.id;
      const customerData = req.body;
      const userId = req.user!.id;
      const companyId = req.user!.companyId;

      // Validate GSTIN format if provided
      if (customerData.gstin && !CustomerService.validateGSTIN(customerData.gstin)) {
        return res.status(400).json({
          error: {
            message: 'Invalid GSTIN format. Expected format: 22AAAAA0000A1Z5',
            timestamp: new Date().toISOString()
          }
        });
      }

      // Validate PAN format if provided
      if (customerData.pan && !CustomerService.validatePAN(customerData.pan)) {
        return res.status(400).json({
          error: {
            message: 'Invalid PAN format. Expected format: AAAAA0000A',
            timestamp: new Date().toISOString()
          }
        });
      }

      const updatedCustomer = await customerService.updateCustomer(customerId, customerData, userId, companyId);

      res.status(200).json({
        data: updatedCustomer,
        message: 'Customer updated successfully'
      });
    } catch (error) {
      if (error instanceof Error && error.message === 'Customer not found') {
        return res.status(404).json({
          error: {
            message: 'Customer not found',
            timestamp: new Date().toISOString()
          }
        });
      }

      res.status(400).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to update customer',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * DELETE /api/v1/party/customers/:id
 * Delete customer (soft delete)
 */
router.delete(
  '/customers/:id',
  authenticate,
  authorize(UserRole.OWNER),
  [
    param('id').isUUID().withMessage('Invalid customer ID')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const customerId = req.params.id;
      const userId = req.user!.id;
      const companyId = req.user!.companyId;

      await customerService.deleteCustomer(customerId, userId, companyId);

      res.status(200).json({
        message: 'Customer deleted successfully'
      });
    } catch (error) {
      if (error instanceof Error && error.message === 'Customer not found') {
        return res.status(404).json({
          error: {
            message: 'Customer not found',
            timestamp: new Date().toISOString()
          }
        });
      }

      res.status(400).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to delete customer',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * GET /api/v1/party/customers/search/gstin/:gstin
 * Search customer by GSTIN
 */
router.get(
  '/customers/search/gstin/:gstin',
  authenticate,
  [
    param('gstin').isLength({ min: 15, max: 15 }).withMessage('GSTIN must be 15 characters')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const gstin = req.params.gstin;
      const companyId = req.user!.companyId;

      const customer = await customerService.searchCustomerByGSTIN(gstin, companyId);

      if (!customer) {
        return res.status(404).json({
          error: {
            message: 'Customer not found with provided GSTIN',
            timestamp: new Date().toISOString()
          }
        });
      }

      res.status(200).json({
        data: customer
      });
    } catch (error) {
      res.status(400).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to search customer by GSTIN',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

// ==================== VENDOR MANAGEMENT APIs ====================

/**
 * POST /api/v1/party/vendors
 * Create vendor
 */
router.post(
  '/vendors',
  authenticate,
  authorize(UserRole.OWNER, UserRole.ADMIN),
  [
    body('vendorCode').notEmpty().withMessage('Vendor code is required'),
    body('companyName').notEmpty().withMessage('Company name is required'),
    body('gstin').optional().isLength({ min: 15, max: 15 }).withMessage('GSTIN must be 15 characters'),
    body('pan').optional().isLength({ min: 10, max: 10 }).withMessage('PAN must be 10 characters'),
    body('email').optional().isEmail().withMessage('Invalid email format'),
    body('paymentTerms').optional().isInt({ min: 0 }).withMessage('Payment terms must be non-negative')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const vendorData = req.body;
      const userId = req.user!.id;
      const companyId = req.user!.companyId;

      // Validate GSTIN format if provided
      if (vendorData.gstin && !VendorService.validateGSTIN(vendorData.gstin)) {
        return res.status(400).json({
          error: {
            message: 'Invalid GSTIN format. Expected format: 22AAAAA0000A1Z5',
            timestamp: new Date().toISOString()
          }
        });
      }

      // Validate PAN format if provided
      if (vendorData.pan && !VendorService.validatePAN(vendorData.pan)) {
        return res.status(400).json({
          error: {
            message: 'Invalid PAN format. Expected format: AAAAA0000A',
            timestamp: new Date().toISOString()
          }
        });
      }

      const vendor = await vendorService.createVendor(vendorData, userId, companyId);

      res.status(201).json({
        data: vendor,
        message: 'Vendor created successfully'
      });
    } catch (error) {
      res.status(400).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to create vendor',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * GET /api/v1/party/vendors
 * List vendors
 */
router.get(
  '/vendors',
  authenticate,
  [
    query('page').optional().isInt({ min: 1 }).withMessage('Page must be a positive integer'),
    query('limit').optional().isInt({ min: 1, max: 100 }).withMessage('Limit must be between 1 and 100'),
    query('isActive').optional().isBoolean().withMessage('isActive must be boolean'),
    query('gstin').optional().isLength({ min: 15, max: 15 }).withMessage('GSTIN must be 15 characters'),
    query('search').optional().isString().withMessage('Search must be a string')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const filters = {
        isActive: req.query.isActive === 'true' ? true : req.query.isActive === 'false' ? false : undefined,
        gstin: req.query.gstin as string,
        search: req.query.search as string
      };

      const page = req.query.page ? parseInt(req.query.page as string) : 1;
      const limit = req.query.limit ? parseInt(req.query.limit as string) : 20;
      const companyId = req.user!.companyId;

      const result = await vendorService.listVendors(companyId, filters, page, limit);

      res.status(200).json({
        data: result.vendors,
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
          message: error instanceof Error ? error.message : 'Failed to fetch vendors',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * GET /api/v1/party/vendors/:id
 * Get vendor details
 */
router.get(
  '/vendors/:id',
  authenticate,
  [
    param('id').isUUID().withMessage('Invalid vendor ID')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const vendorId = req.params.id;
      const companyId = req.user!.companyId;

      const vendor = await vendorService.getVendorById(vendorId, companyId);

      res.status(200).json({
        data: vendor
      });
    } catch (error) {
      if (error instanceof Error && error.message === 'Vendor not found') {
        return res.status(404).json({
          error: {
            message: 'Vendor not found',
            timestamp: new Date().toISOString()
          }
        });
      }

      res.status(500).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to fetch vendor',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * PUT /api/v1/party/vendors/:id
 * Update vendor
 */
router.put(
  '/vendors/:id',
  authenticate,
  authorize(UserRole.OWNER, UserRole.ADMIN),
  [
    param('id').isUUID().withMessage('Invalid vendor ID'),
    body('gstin').optional().isLength({ min: 15, max: 15 }).withMessage('GSTIN must be 15 characters'),
    body('pan').optional().isLength({ min: 10, max: 10 }).withMessage('PAN must be 10 characters'),
    body('email').optional().isEmail().withMessage('Invalid email format'),
    body('paymentTerms').optional().isInt({ min: 0 }).withMessage('Payment terms must be non-negative')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const vendorId = req.params.id;
      const vendorData = req.body;
      const userId = req.user!.id;
      const companyId = req.user!.companyId;

      // Validate GSTIN format if provided
      if (vendorData.gstin && !VendorService.validateGSTIN(vendorData.gstin)) {
        return res.status(400).json({
          error: {
            message: 'Invalid GSTIN format. Expected format: 22AAAAA0000A1Z5',
            timestamp: new Date().toISOString()
          }
        });
      }

      // Validate PAN format if provided
      if (vendorData.pan && !VendorService.validatePAN(vendorData.pan)) {
        return res.status(400).json({
          error: {
            message: 'Invalid PAN format. Expected format: AAAAA0000A',
            timestamp: new Date().toISOString()
          }
        });
      }

      const updatedVendor = await vendorService.updateVendor(vendorId, vendorData, userId, companyId);

      res.status(200).json({
        data: updatedVendor,
        message: 'Vendor updated successfully'
      });
    } catch (error) {
      if (error instanceof Error && error.message === 'Vendor not found') {
        return res.status(404).json({
          error: {
            message: 'Vendor not found',
            timestamp: new Date().toISOString()
          }
        });
      }

      res.status(400).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to update vendor',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * DELETE /api/v1/party/vendors/:id
 * Delete vendor (soft delete)
 */
router.delete(
  '/vendors/:id',
  authenticate,
  authorize(UserRole.OWNER),
  [
    param('id').isUUID().withMessage('Invalid vendor ID')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const vendorId = req.params.id;
      const userId = req.user!.id;
      const companyId = req.user!.companyId;

      await vendorService.deleteVendor(vendorId, userId, companyId);

      res.status(200).json({
        message: 'Vendor deleted successfully'
      });
    } catch (error) {
      if (error instanceof Error && error.message === 'Vendor not found') {
        return res.status(404).json({
          error: {
            message: 'Vendor not found',
            timestamp: new Date().toISOString()
          }
        });
      }

      res.status(400).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to delete vendor',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * GET /api/v1/party/vendors/search/gstin/:gstin
 * Search vendor by GSTIN
 */
router.get(
  '/vendors/search/gstin/:gstin',
  authenticate,
  [
    param('gstin').isLength({ min: 15, max: 15 }).withMessage('GSTIN must be 15 characters')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const gstin = req.params.gstin;
      const companyId = req.user!.companyId;

      const vendor = await vendorService.searchVendorByGSTIN(gstin, companyId);

      if (!vendor) {
        return res.status(404).json({
          error: {
            message: 'Vendor not found with provided GSTIN',
            timestamp: new Date().toISOString()
          }
        });
      }

      res.status(200).json({
        data: vendor
      });
    } catch (error) {
      res.status(400).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to search vendor by GSTIN',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

export default router;