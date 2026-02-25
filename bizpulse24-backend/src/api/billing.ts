import { Router, Request, Response } from 'express';
import { BillingService } from '../services/BillingService';
import { authenticate, authorize, AuthRequest } from '../middleware/auth';
import { body, query, param, validationResult } from 'express-validator';
import { UserRole } from '../models/types';

const router = Router();
const billingService = new BillingService();

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

// ==================== SALES INVOICE APIs ====================

/**
 * POST /api/v1/billing/sales-invoices
 * Create sales invoice
 */
router.post(
  '/sales-invoices',
  authenticate,
  authorize(UserRole.OWNER, UserRole.ADMIN),
  [
    body('invoiceDate').isISO8601().withMessage('Invalid invoice date'),
    body('dueDate').optional().isISO8601().withMessage('Invalid due date'),
    body('customerId').isUUID().withMessage('Invalid customer ID'),
    body('placeOfSupply').notEmpty().withMessage('Place of supply is required'),
    body('items').isArray({ min: 1 }).withMessage('At least one item is required'),
    body('items.*.productId').isUUID().withMessage('Invalid product ID in items'),
    body('items.*.quantity').isNumeric().withMessage('Quantity must be a number').isFloat({ gt: 0 }).withMessage('Quantity must be greater than 0'),
    body('items.*.unitPrice').isNumeric().withMessage('Unit price must be a number').isFloat({ gt: 0 }).withMessage('Unit price must be greater than 0'),
    body('items.*.discountPercent').optional().isNumeric().withMessage('Discount percent must be a number').isFloat({ min: 0, max: 100 }).withMessage('Discount percent must be between 0 and 100'),
    body('discountAmount').optional().isNumeric().withMessage('Discount amount must be a number'),
    body('roundOff').optional().isNumeric().withMessage('Round off must be a number')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const invoiceData = req.body;
      const userId = req.user!.id;
      const companyId = req.user!.companyId;

      const invoice = await billingService.createSalesInvoice(invoiceData, userId, companyId);

      res.status(201).json({
        data: invoice,
        message: 'Sales invoice created successfully'
      });
    } catch (error) {
      res.status(400).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to create sales invoice',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * GET /api/v1/billing/sales-invoices
 * List sales invoices
 */
router.get(
  '/sales-invoices',
  authenticate,
  [
    query('page').optional().isInt({ min: 1 }).withMessage('Page must be a positive integer'),
    query('limit').optional().isInt({ min: 1, max: 100 }).withMessage('Limit must be between 1 and 100'),
    query('customerId').optional().isUUID().withMessage('Invalid customer ID'),
    query('invoiceDateFrom').optional().isISO8601().withMessage('Invalid from date'),
    query('invoiceDateTo').optional().isISO8601().withMessage('Invalid to date'),
    query('paymentStatus').optional().isIn(['PENDING', 'PARTIAL', 'PAID', 'OVERDUE']).withMessage('Invalid payment status'),
    query('isCancelled').optional().isBoolean().withMessage('isCancelled must be boolean')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const filters = {
        customerId: req.query.customerId as string,
        invoiceDateFrom: req.query.invoiceDateFrom ? new Date(req.query.invoiceDateFrom as string) : undefined,
        invoiceDateTo: req.query.invoiceDateTo ? new Date(req.query.invoiceDateTo as string) : undefined,
        paymentStatus: req.query.paymentStatus as string,
        isCancelled: req.query.isCancelled === 'true' ? true : req.query.isCancelled === 'false' ? false : undefined,
        page: req.query.page ? parseInt(req.query.page as string) : undefined,
        limit: req.query.limit ? parseInt(req.query.limit as string) : undefined
      };

      const companyId = req.user!.companyId;

      const result = await billingService.listSalesInvoices(filters, companyId);

      res.status(200).json({
        data: result.invoices,
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
          message: error instanceof Error ? error.message : 'Failed to fetch sales invoices',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * GET /api/v1/billing/sales-invoices/:id
 * Get sales invoice details
 */
router.get(
  '/sales-invoices/:id',
  authenticate,
  [
    param('id').isUUID().withMessage('Invalid invoice ID')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const invoiceId = req.params.id;
      const companyId = req.user!.companyId;

      const invoice = await billingService.getSalesInvoiceById(invoiceId, companyId);

      res.status(200).json({
        data: invoice
      });
    } catch (error) {
      if (error instanceof Error && error.message === 'Sales invoice not found') {
        return res.status(404).json({
          error: {
            message: 'Sales invoice not found',
            timestamp: new Date().toISOString()
          }
        });
      }

      res.status(500).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to fetch sales invoice',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * PUT /api/v1/billing/sales-invoices/:id/cancel
 * Cancel sales invoice
 */
router.put(
  '/sales-invoices/:id/cancel',
  authenticate,
  authorize(UserRole.OWNER, UserRole.ADMIN),
  [
    param('id').isUUID().withMessage('Invalid invoice ID'),
    body('reason').notEmpty().withMessage('Cancellation reason is required')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const invoiceId = req.params.id;
      const { reason } = req.body;
      const userId = req.user!.id;
      const companyId = req.user!.companyId;

      await billingService.cancelSalesInvoice(invoiceId, userId, companyId, reason);

      res.status(200).json({
        message: 'Sales invoice cancelled successfully'
      });
    } catch (error) {
      if (error instanceof Error && error.message === 'Sales invoice not found') {
        return res.status(404).json({
          error: {
            message: 'Sales invoice not found',
            timestamp: new Date().toISOString()
          }
        });
      }

      res.status(400).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to cancel sales invoice',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * GET /api/v1/billing/sales-invoices/summary
 * Get sales invoice summary
 */
router.get(
  '/sales-invoices/summary',
  authenticate,
  [
    query('fromDate').optional().isISO8601().withMessage('Invalid from date'),
    query('toDate').optional().isISO8601().withMessage('Invalid to date')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const fromDate = req.query.fromDate ? new Date(req.query.fromDate as string) : undefined;
      const toDate = req.query.toDate ? new Date(req.query.toDate as string) : undefined;
      const companyId = req.user!.companyId;

      const summary = await billingService.getInvoiceSummary(companyId, fromDate, toDate);

      res.status(200).json({
        data: summary
      });
    } catch (error) {
      res.status(500).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to fetch invoice summary',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

// ==================== PURCHASE INVOICE APIs ====================

/**
 * POST /api/v1/billing/purchase-invoices
 * Create purchase invoice
 */
router.post(
  '/purchase-invoices',
  authenticate,
  authorize(UserRole.OWNER, UserRole.ADMIN),
  [
    body('invoiceDate').isISO8601().withMessage('Invalid invoice date'),
    body('dueDate').optional().isISO8601().withMessage('Invalid due date'),
    body('vendorId').isUUID().withMessage('Invalid vendor ID'),
    body('placeOfSupply').notEmpty().withMessage('Place of supply is required'),
    body('items').isArray({ min: 1 }).withMessage('At least one item is required'),
    body('items.*.productId').isUUID().withMessage('Invalid product ID in items'),
    body('items.*.quantity').isNumeric().withMessage('Quantity must be a number').isFloat({ gt: 0 }).withMessage('Quantity must be greater than 0'),
    body('items.*.unitPrice').isNumeric().withMessage('Unit price must be a number').isFloat({ gt: 0 }).withMessage('Unit price must be greater than 0'),
    body('items.*.discountPercent').optional().isNumeric().withMessage('Discount percent must be a number').isFloat({ min: 0, max: 100 }).withMessage('Discount percent must be between 0 and 100'),
    body('discountAmount').optional().isNumeric().withMessage('Discount amount must be a number'),
    body('roundOff').optional().isNumeric().withMessage('Round off must be a number')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const invoiceData = req.body;
      const userId = req.user!.id;
      const companyId = req.user!.companyId;

      const invoice = await billingService.createPurchaseInvoice(invoiceData, userId, companyId);

      res.status(201).json({
        data: invoice,
        message: 'Purchase invoice created successfully'
      });
    } catch (error) {
      res.status(400).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to create purchase invoice',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * GET /api/v1/billing/purchase-invoices
 * List purchase invoices
 */
router.get(
  '/purchase-invoices',
  authenticate,
  [
    query('page').optional().isInt({ min: 1 }).withMessage('Page must be a positive integer'),
    query('limit').optional().isInt({ min: 1, max: 100 }).withMessage('Limit must be between 1 and 100'),
    query('vendorId').optional().isUUID().withMessage('Invalid vendor ID'),
    query('invoiceDateFrom').optional().isISO8601().withMessage('Invalid from date'),
    query('invoiceDateTo').optional().isISO8601().withMessage('Invalid to date'),
    query('paymentStatus').optional().isIn(['PENDING', 'PARTIAL', 'PAID', 'OVERDUE']).withMessage('Invalid payment status'),
    query('isCancelled').optional().isBoolean().withMessage('isCancelled must be boolean')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const filters = {
        vendorId: req.query.vendorId as string,
        invoiceDateFrom: req.query.invoiceDateFrom ? new Date(req.query.invoiceDateFrom as string) : undefined,
        invoiceDateTo: req.query.invoiceDateTo ? new Date(req.query.invoiceDateTo as string) : undefined,
        paymentStatus: req.query.paymentStatus as string,
        isCancelled: req.query.isCancelled === 'true' ? true : req.query.isCancelled === 'false' ? false : undefined,
        page: req.query.page ? parseInt(req.query.page as string) : undefined,
        limit: req.query.limit ? parseInt(req.query.limit as string) : undefined
      };

      const companyId = req.user!.companyId;

      const result = await billingService.listPurchaseInvoices(filters, companyId);

      res.status(200).json({
        data: result.invoices,
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
          message: error instanceof Error ? error.message : 'Failed to fetch purchase invoices',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * GET /api/v1/billing/purchase-invoices/:id
 * Get purchase invoice details
 */
router.get(
  '/purchase-invoices/:id',
  authenticate,
  [
    param('id').isUUID().withMessage('Invalid invoice ID')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const invoiceId = req.params.id;
      const companyId = req.user!.companyId;

      const invoice = await billingService.getPurchaseInvoiceById(invoiceId, companyId);

      res.status(200).json({
        data: invoice
      });
    } catch (error) {
      if (error instanceof Error && error.message === 'Purchase invoice not found') {
        return res.status(404).json({
          error: {
            message: 'Purchase invoice not found',
            timestamp: new Date().toISOString()
          }
        });
      }

      res.status(500).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to fetch purchase invoice',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * PUT /api/v1/billing/purchase-invoices/:id/cancel
 * Cancel purchase invoice
 */
router.put(
  '/purchase-invoices/:id/cancel',
  authenticate,
  authorize(UserRole.OWNER, UserRole.ADMIN),
  [
    param('id').isUUID().withMessage('Invalid invoice ID'),
    body('reason').notEmpty().withMessage('Cancellation reason is required')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const invoiceId = req.params.id;
      const { reason } = req.body;
      const userId = req.user!.id;
      const companyId = req.user!.companyId;

      await billingService.cancelPurchaseInvoice(invoiceId, userId, companyId, reason);

      res.status(200).json({
        message: 'Purchase invoice cancelled successfully'
      });
    } catch (error) {
      if (error instanceof Error && error.message === 'Purchase invoice not found') {
        return res.status(404).json({
          error: {
            message: 'Purchase invoice not found',
            timestamp: new Date().toISOString()
          }
        });
      }

      res.status(400).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to cancel purchase invoice',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * GET /api/v1/billing/purchase-invoices/summary
 * Get purchase invoice summary
 */
router.get(
  '/purchase-invoices/summary',
  authenticate,
  [
    query('fromDate').optional().isISO8601().withMessage('Invalid from date'),
    query('toDate').optional().isISO8601().withMessage('Invalid to date')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const fromDate = req.query.fromDate ? new Date(req.query.fromDate as string) : undefined;
      const toDate = req.query.toDate ? new Date(req.query.toDate as string) : undefined;
      const companyId = req.user!.companyId;

      const summary = await billingService.getPurchaseInvoiceSummary(companyId, fromDate, toDate);

      res.status(200).json({
        data: summary
      });
    } catch (error) {
      res.status(500).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to fetch purchase invoice summary',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * GET /api/v1/billing/gstr1/summary
 * Get GSTR-1 summary
 */
router.get(
  '/gstr1/summary',
  authenticate,
  authorize(UserRole.OWNER, UserRole.ADMIN),
  [
    query('financialYear').notEmpty().withMessage('Financial year is required'),
    query('month').optional().isInt({ min: 1, max: 12 }).withMessage('Month must be between 1 and 12')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const { financialYear, month } = req.query;
      const companyId = req.user!.companyId;

      const whereConditions: any = {
        companyId: companyId,
        financialYear: financialYear
      };

      if (month) {
        whereConditions.monthNumber = parseInt(month as string);
      }

      const gstr1Summary = await prisma.gstr1Summary.findMany({
        where: whereConditions,
        orderBy: { monthNumber: 'asc' }
      });

      res.status(200).json({
        data: gstr1Summary
      });
    } catch (error) {
      res.status(500).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to fetch GSTR-1 summary',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * PUT /api/v1/billing/gstr1/:id/file
 * File GSTR-1 report
 */
router.put(
  '/gstr1/:id/file',
  authenticate,
  authorize(UserRole.OWNER),
  [
    param('id').isUUID().withMessage('Invalid GSTR-1 ID')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const summaryId = req.params.id;
      const userId = req.user!.id;
      const companyId = req.user!.companyId;

      const summary = await prisma.gstr1Summary.findFirst({
        where: {
          id: summaryId,
          companyId: companyId
        }
      });

      if (!summary) {
        return res.status(404).json({
          error: {
            message: 'GSTR-1 summary not found',
            timestamp: new Date().toISOString()
          }
        });
      }

      if (summary.isFiled) {
        return res.status(400).json({
          error: {
            message: 'GSTR-1 report is already filed',
            timestamp: new Date().toISOString()
          }
        });
      }

      await prisma.gstr1Summary.update({
        where: { id: summaryId },
        data: {
          isFiled: true,
          filedAt: new Date(),
          filedBy: userId,
          updatedBy: userId,
          updatedAt: new Date()
        }
      });

      res.status(200).json({
        message: 'GSTR-1 report filed successfully'
      });
    } catch (error) {
      res.status(400).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to file GSTR-1 report',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

export default router;