import { Router, Request, Response } from 'express';
import { PrismaClient } from '@prisma/client';
import { CustomerService, VendorService } from '../services/PartyService';
import { authenticate, authorize, AuthRequest } from '../middleware/auth';
import { query, param, body, validationResult } from 'express-validator';
import { UserRole } from '../models/types';

const router = Router();
const prisma = new PrismaClient();
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

// ==================== CUSTOMER DUES MANAGEMENT APIs ====================

/**
 * GET /api/v1/party/customer-dues
 * Get all customer dues with filtering
 */
router.get(
  '/customer-dues',
  authenticate,
  [
    query('page').optional().isInt({ min: 1 }).withMessage('Page must be a positive integer'),
    query('limit').optional().isInt({ min: 1, max: 100 }).withMessage('Limit must be between 1 and 100'),
    query('hasOutstanding').optional().isBoolean().withMessage('hasOutstanding must be boolean'),
    query('minAmount').optional().isNumeric().withMessage('minAmount must be a number'),
    query('customerId').optional().isUUID().withMessage('Invalid customer ID')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const page = req.query.page ? parseInt(req.query.page as string) : 1;
      const limit = req.query.limit ? parseInt(req.query.limit as string) : 20;
      const skip = (page - 1) * limit;
      const companyId = req.user!.companyId;

      const whereConditions: any = {
        companyId: companyId
      };

      // Filter by customer ID if provided
      if (req.query.customerId) {
        whereConditions.customerId = req.query.customerId;
      }

      // Filter by outstanding amount
      if (req.query.hasOutstanding === 'true') {
        whereConditions.outstandingAmount = { gt: 0 };
      } else if (req.query.hasOutstanding === 'false') {
        whereConditions.outstandingAmount = { equals: 0 };
      }

      // Filter by minimum amount
      if (req.query.minAmount) {
        const minAmount = parseFloat(req.query.minAmount as string);
        whereConditions.outstandingAmount = {
          ...whereConditions.outstandingAmount,
          gte: minAmount
        };
      }

      const [customerDues, total] = await Promise.all([
        prisma.customerDue.findMany({
          where: whereConditions,
          include: {
            customer: {
              select: {
                customerCode: true,
                companyName: true,
                gstin: true,
                contactPerson: true,
                phone: true,
                email: true
              }
            }
          },
          orderBy: { outstandingAmount: 'desc' },
          skip,
          take: limit
        }),
        prisma.customerDue.count({ where: whereConditions })
      ]);

      res.status(200).json({
        data: customerDues,
        metadata: {
          total,
          page,
          limit,
          totalPages: Math.ceil(total / limit)
        }
      });
    } catch (error) {
      res.status(500).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to fetch customer dues',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * GET /api/v1/party/customer-dues/:id
 * Get specific customer due details
 */
router.get(
  '/customer-dues/:id',
  authenticate,
  [
    param('id').isUUID().withMessage('Invalid customer due ID')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const dueId = req.params.id;
      const companyId = req.user!.companyId;

      const customerDue = await prisma.customerDue.findFirst({
        where: {
          id: dueId,
          companyId: companyId
        },
        include: {
          customer: {
            include: {
              customerDues: true
            }
          }
        }
      });

      if (!customerDue) {
        return res.status(404).json({
          error: {
            message: 'Customer due record not found',
            timestamp: new Date().toISOString()
          }
        });
      }

      res.status(200).json({
        data: customerDue
      });
    } catch (error) {
      res.status(500).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to fetch customer due details',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * GET /api/v1/party/customer-dues/customer/:customerId
 * Get dues for specific customer
 */
router.get(
  '/customer-dues/customer/:customerId',
  authenticate,
  [
    param('customerId').isUUID().withMessage('Invalid customer ID')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const customerId = req.params.customerId;
      const companyId = req.user!.companyId;

      const customerDue = await prisma.customerDue.findFirst({
        where: {
          customerId: customerId,
          companyId: companyId
        },
        include: {
          customer: {
            select: {
              customerCode: true,
              companyName: true,
              gstin: true,
              contactPerson: true,
              phone: true,
              email: true
            }
          }
        }
      });

      if (!customerDue) {
        return res.status(404).json({
          error: {
            message: 'Customer due record not found',
            timestamp: new Date().toISOString()
          }
        });
      }

      res.status(200).json({
        data: customerDue
      });
    } catch (error) {
      res.status(500).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to fetch customer dues',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * PUT /api/v1/party/customer-dues/:id/update
 * Update customer due amounts (ADMIN/OWNER only)
 */
router.put(
  '/customer-dues/:id/update',
  authenticate,
  authorize(UserRole.OWNER, UserRole.ADMIN),
  [
    param('id').isUUID().withMessage('Invalid customer due ID'),
    body('totalSales').optional().isNumeric().withMessage('Total sales must be a number'),
    body('totalPayments').optional().isNumeric().withMessage('Total payments must be a number')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const dueId = req.params.id;
      const { totalSales, totalPayments } = req.body;
      const userId = req.user!.id;
      const companyId = req.user!.companyId;

      const existingDue = await prisma.customerDue.findFirst({
        where: {
          id: dueId,
          companyId: companyId
        }
      });

      if (!existingDue) {
        return res.status(404).json({
          error: {
            message: 'Customer due record not found',
            timestamp: new Date().toISOString()
          }
        });
      }

      // Update due amounts
      const updateData: any = {
        lastUpdated: new Date(),
        updatedBy: userId
      };

      if (totalSales !== undefined) {
        updateData.totalSales = totalSales;
      }

      if (totalPayments !== undefined) {
        updateData.totalPayments = totalPayments;
      }

      const updatedDue = await prisma.customerDue.update({
        where: { id: dueId },
        data: updateData,
        include: {
          customer: {
            select: {
              customerCode: true,
              companyName: true
            }
          }
        }
      });

      res.status(200).json({
        data: updatedDue,
        message: 'Customer due updated successfully'
      });
    } catch (error) {
      res.status(400).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to update customer due',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

// ==================== VENDOR PAYABLES MANAGEMENT APIs ====================

/**
 * GET /api/v1/party/vendor-payables
 * Get all vendor payables with filtering
 */
router.get(
  '/vendor-payables',
  authenticate,
  [
    query('page').optional().isInt({ min: 1 }).withMessage('Page must be a positive integer'),
    query('limit').optional().isInt({ min: 1, max: 100 }).withMessage('Limit must be between 1 and 100'),
    query('hasPayable').optional().isBoolean().withMessage('hasPayable must be boolean'),
    query('minAmount').optional().isNumeric().withMessage('minAmount must be a number'),
    query('vendorId').optional().isUUID().withMessage('Invalid vendor ID')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const page = req.query.page ? parseInt(req.query.page as string) : 1;
      const limit = req.query.limit ? parseInt(req.query.limit as string) : 20;
      const skip = (page - 1) * limit;
      const companyId = req.user!.companyId;

      const whereConditions: any = {
        companyId: companyId
      };

      // Filter by vendor ID if provided
      if (req.query.vendorId) {
        whereConditions.vendorId = req.query.vendorId;
      }

      // Filter by payable amount
      if (req.query.hasPayable === 'true') {
        whereConditions.payableAmount = { gt: 0 };
      } else if (req.query.hasPayable === 'false') {
        whereConditions.payableAmount = { equals: 0 };
      }

      // Filter by minimum amount
      if (req.query.minAmount) {
        const minAmount = parseFloat(req.query.minAmount as string);
        whereConditions.payableAmount = {
          ...whereConditions.payableAmount,
          gte: minAmount
        };
      }

      const [vendorPayables, total] = await Promise.all([
        prisma.vendorPayable.findMany({
          where: whereConditions,
          include: {
            vendor: {
              select: {
                vendorCode: true,
                companyName: true,
                gstin: true,
                contactPerson: true,
                phone: true,
                email: true
              }
            }
          },
          orderBy: { payableAmount: 'desc' },
          skip,
          take: limit
        }),
        prisma.vendorPayable.count({ where: whereConditions })
      ]);

      res.status(200).json({
        data: vendorPayables,
        metadata: {
          total,
          page,
          limit,
          totalPages: Math.ceil(total / limit)
        }
      });
    } catch (error) {
      res.status(500).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to fetch vendor payables',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * GET /api/v1/party/vendor-payables/:id
 * Get specific vendor payable details
 */
router.get(
  '/vendor-payables/:id',
  authenticate,
  [
    param('id').isUUID().withMessage('Invalid vendor payable ID')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const payableId = req.params.id;
      const companyId = req.user!.companyId;

      const vendorPayable = await prisma.vendorPayable.findFirst({
        where: {
          id: payableId,
          companyId: companyId
        },
        include: {
          vendor: {
            include: {
              vendorPayables: true
            }
          }
        }
      });

      if (!vendorPayable) {
        return res.status(404).json({
          error: {
            message: 'Vendor payable record not found',
            timestamp: new Date().toISOString()
          }
        });
      }

      res.status(200).json({
        data: vendorPayable
      });
    } catch (error) {
      res.status(500).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to fetch vendor payable details',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * GET /api/v1/party/vendor-payables/vendor/:vendorId
 * Get payables for specific vendor
 */
router.get(
  '/vendor-payables/vendor/:vendorId',
  authenticate,
  [
    param('vendorId').isUUID().withMessage('Invalid vendor ID')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const vendorId = req.params.vendorId;
      const companyId = req.user!.companyId;

      const vendorPayable = await prisma.vendorPayable.findFirst({
        where: {
          vendorId: vendorId,
          companyId: companyId
        },
        include: {
          vendor: {
            select: {
              vendorCode: true,
              companyName: true,
              gstin: true,
              contactPerson: true,
              phone: true,
              email: true
            }
          }
        }
      });

      if (!vendorPayable) {
        return res.status(404).json({
          error: {
            message: 'Vendor payable record not found',
            timestamp: new Date().toISOString()
          }
        });
      }

      res.status(200).json({
        data: vendorPayable
      });
    } catch (error) {
      res.status(500).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to fetch vendor payables',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

/**
 * PUT /api/v1/party/vendor-payables/:id/update
 * Update vendor payable amounts (ADMIN/OWNER only)
 */
router.put(
  '/vendor-payables/:id/update',
  authenticate,
  authorize(UserRole.OWNER, UserRole.ADMIN),
  [
    param('id').isUUID().withMessage('Invalid vendor payable ID'),
    body('totalPurchases').optional().isNumeric().withMessage('Total purchases must be a number'),
    body('totalPayments').optional().isNumeric().withMessage('Total payments must be a number')
  ],
  handleValidation,
  async (req: AuthRequest, res: Response) => {
    try {
      const payableId = req.params.id;
      const { totalPurchases, totalPayments } = req.body;
      const userId = req.user!.id;
      const companyId = req.user!.companyId;

      const existingPayable = await prisma.vendorPayable.findFirst({
        where: {
          id: payableId,
          companyId: companyId
        }
      });

      if (!existingPayable) {
        return res.status(404).json({
          error: {
            message: 'Vendor payable record not found',
            timestamp: new Date().toISOString()
          }
        });
      }

      // Update payable amounts
      const updateData: any = {
        lastUpdated: new Date(),
        updatedBy: userId
      };

      if (totalPurchases !== undefined) {
        updateData.totalPurchases = totalPurchases;
      }

      if (totalPayments !== undefined) {
        updateData.totalPayments = totalPayments;
      }

      const updatedPayable = await prisma.vendorPayable.update({
        where: { id: payableId },
        data: updateData,
        include: {
          vendor: {
            select: {
              vendorCode: true,
              companyName: true
            }
          }
        }
      });

      res.status(200).json({
        data: updatedPayable,
        message: 'Vendor payable updated successfully'
      });
    } catch (error) {
      res.status(400).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to update vendor payable',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

// ==================== SUMMARY REPORTS ====================

/**
 * GET /api/v1/party/dues-summary
 * Get summary of all dues and payables
 */
router.get(
  '/dues-summary',
  authenticate,
  async (req: AuthRequest, res: Response) => {
    try {
      const companyId = req.user!.companyId;

      // Get customer dues summary
      const customerDuesSummary = await prisma.customerDue.aggregate({
        where: { companyId: companyId },
        _sum: {
          totalSales: true,
          totalPayments: true,
          outstandingAmount: true
        },
        _count: {
          id: true
        }
      });

      // Get vendor payables summary
      const vendorPayablesSummary = await prisma.vendorPayable.aggregate({
        where: { companyId: companyId },
        _sum: {
          totalPurchases: true,
          totalPayments: true,
          payableAmount: true
        },
        _count: {
          id: true
        }
      });

      // Get counts of parties with outstanding amounts
      const customersWithDues = await prisma.customerDue.count({
        where: {
          companyId: companyId,
          outstandingAmount: { gt: 0 }
        }
      });

      const vendorsWithPayables = await prisma.vendorPayable.count({
        where: {
          companyId: companyId,
          payableAmount: { gt: 0 }
        }
      });

      const summary = {
        customerDues: {
          totalRecords: customerDuesSummary._count.id,
          totalSales: customerDuesSummary._sum.totalSales || 0,
          totalPayments: customerDuesSummary._sum.totalPayments || 0,
          totalOutstanding: customerDuesSummary._sum.outstandingAmount || 0,
          customersWithDues: customersWithDues
        },
        vendorPayables: {
          totalRecords: vendorPayablesSummary._count.id,
          totalPurchases: vendorPayablesSummary._sum.totalPurchases || 0,
          totalPayments: vendorPayablesSummary._sum.totalPayments || 0,
          totalPayable: vendorPayablesSummary._sum.payableAmount || 0,
          vendorsWithPayables: vendorsWithPayables
        },
        netPosition: (customerDuesSummary._sum.outstandingAmount || 0) - (vendorPayablesSummary._sum.payableAmount || 0)
      };

      res.status(200).json({
        data: summary
      });
    } catch (error) {
      res.status(500).json({
        error: {
          message: error instanceof Error ? error.message : 'Failed to fetch dues summary',
          timestamp: new Date().toISOString()
        }
      });
    }
  }
);

export default router;