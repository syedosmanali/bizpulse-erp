import { PrismaClient } from '@prisma/client';
import { GSTEngine } from '../engines/GSTEngine';
import { LedgerEngine } from '../engines/LedgerEngine';
import { StockLedger } from '../engines/StockLedger';
import { AuditLogger } from '../engines/AuditLogger';

// Interface for sales invoice creation
export interface SalesInvoiceInput {
  invoiceDate: Date;
  dueDate?: Date;
  customerId: string;
  billingAddress?: string;
  shippingAddress?: string;
  placeOfSupply: string;
  invoiceType?: 'TAX_INVOICE' | 'BILL_OF_SUPPLY' | 'RECEIPT';
  items: SalesInvoiceItemInput[];
  discountAmount?: number;
  roundOff?: number;
  notes?: string;
  termsAndConditions?: string;
}

// Interface for sales invoice items
export interface SalesInvoiceItemInput {
  productId: string;
  quantity: number;
  unitPrice: number;
  discountPercent?: number;
  hsnCode?: string;
  description?: string;
  batchNumber?: string;
  expiryDate?: Date;
}

// Interface for purchase invoice creation
export interface PurchaseInvoiceInput {
  invoiceDate: Date;
  dueDate?: Date;
  vendorId: string;
  billingAddress?: string;
  shippingAddress?: string;
  placeOfSupply: string;
  invoiceType?: 'TAX_INVOICE' | 'BILL_OF_SUPPLY';
  items: PurchaseInvoiceItemInput[];
  discountAmount?: number;
  roundOff?: number;
  notes?: string;
  termsAndConditions?: string;
}

// Interface for purchase invoice items
export interface PurchaseInvoiceItemInput {
  productId: string;
  quantity: number;
  unitPrice: number;
  discountPercent?: number;
  hsnCode?: string;
  description?: string;
  batchNumber?: string;
  expiryDate?: Date;
}

// Interface for invoice filters
export interface InvoiceFilters {
  customerId?: string;
  vendorId?: string;
  invoiceDateFrom?: Date;
  invoiceDateTo?: Date;
  paymentStatus?: string;
  isCancelled?: boolean;
  page?: number;
  limit?: number;
}

/**
 * Billing Service for Sales Invoice Management
 * Handles invoice creation with automatic GST calculation
 */
export class BillingService {
  private prisma: PrismaClient;
  private gstEngine: GSTEngine;
  private ledgerEngine: LedgerEngine;
  private stockLedger: StockLedger;
  private auditLogger: AuditLogger;

  constructor() {
    this.prisma = new PrismaClient();
    this.gstEngine = new GSTEngine();
    this.ledgerEngine = new LedgerEngine();
    this.stockLedger = new StockLedger();
    this.auditLogger = new AuditLogger();
  }

  /**
   * Create sales invoice with automatic GST calculation
   * @param invoiceData Invoice input data
   * @param userId User creating the invoice
   * @param companyId Company ID
   * @returns Created invoice with items
   */
  public async createSalesInvoice(
    invoiceData: SalesInvoiceInput,
    userId: string,
    companyId: string
  ): Promise<any> {
    try {
      // Validate customer exists
      const customer = await this.prisma.customer.findFirst({
        where: {
          id: invoiceData.customerId,
          companyId: companyId,
          isActive: true
        }
      });

      if (!customer) {
        throw new Error('Customer not found or inactive');
      }

      // Validate products and calculate totals
      let subtotal = 0;
      let totalTaxableAmount = 0;
      let totalGSTAmount = 0;
      let totalCGST = 0;
      let totalSGST = 0;
      let totalIGST = 0;
      let totalCESS = 0;

      // Validate items and calculate amounts
      const validatedItems = await Promise.all(
        invoiceData.items.map(async (item) => {
          // Validate product exists
          const product = await this.prisma.product.findFirst({
            where: {
              id: item.productId,
              companyId: companyId,
              isActive: true
            }
          });

          if (!product) {
            throw new Error(`Product not found: ${item.productId}`);
          }

          // Check stock availability
          const availableStock = await this.stockLedger.getCurrentStock(
            item.productId,
            undefined, // Default location
            item.batchNumber
          );

          if (availableStock < item.quantity) {
            throw new Error(`Insufficient stock for product ${product.name}. Available: ${availableStock}, Required: ${item.quantity}`);
          }

          // Calculate item amounts
          const discountAmount = item.discountPercent ? 
            (item.unitPrice * item.quantity * item.discountPercent / 100) : 0;
          const taxableAmount = (item.unitPrice * item.quantity) - discountAmount;
          const hsnCode = item.hsnCode || product.hsnCode || '0000';
          
          // Calculate GST using GST Engine
          const gstCalculation = this.gstEngine.calculateGST(
            taxableAmount,
            product.gstRate,
            customer.state === 'YOUR_STATE' ? 'INTRA_STATE' : 'INTER_STATE', // TODO: Get company state
            0 // CESS rate
          );

          subtotal += item.unitPrice * item.quantity;
          totalTaxableAmount += taxableAmount;
          totalGSTAmount += gstCalculation.totalGST;
          totalCGST += gstCalculation.cgstAmount;
          totalSGST += gstCalculation.sgstAmount;
          totalIGST += gstCalculation.igstAmount;
          totalCESS += gstCalculation.cessAmount;

          return {
            productId: item.productId,
            hsnCode: hsnCode,
            description: item.description || product.name,
            quantity: item.quantity,
            unit: product.unit,
            unitPrice: item.unitPrice,
            discountPercent: item.discountPercent || 0,
            discountAmount: discountAmount,
            taxableAmount: taxableAmount,
            gstRate: product.gstRate,
            gstAmount: gstCalculation.totalGST,
            cgstAmount: gstCalculation.cgstAmount,
            sgstAmount: gstCalculation.sgstAmount,
            igstAmount: gstCalculation.igstAmount,
            cessRate: 0,
            cessAmount: gstCalculation.cessAmount,
            totalAmount: taxableAmount + gstCalculation.totalGST,
            batchNumber: item.batchNumber,
            expiryDate: item.expiryDate
          };
        })
      );

      // Calculate invoice totals
      const discountAmount = invoiceData.discountAmount || 0;
      const taxableAmount = totalTaxableAmount - discountAmount;
      const taxAmount = totalGSTAmount;
      const totalAmount = taxableAmount + taxAmount;
      const roundOff = invoiceData.roundOff || 0;
      const grandTotal = Math.round(totalAmount + roundOff);

      // Generate invoice number
      const invoiceNumber = await this.generateInvoiceNumber('SI', companyId);

      // Start transaction
      const result = await this.prisma.$transaction(async (tx) => {
        // Create sales invoice
        const invoice = await tx.salesInvoice.create({
          data: {
            companyId: companyId,
            invoiceNumber: invoiceNumber,
            invoiceDate: invoiceData.invoiceDate,
            dueDate: invoiceData.dueDate,
            customerId: invoiceData.customerId,
            customerGstin: customer.gstin,
            billingAddress: invoiceData.billingAddress || customer.address,
            shippingAddress: invoiceData.shippingAddress,
            placeOfSupply: invoiceData.placeOfSupply,
            invoiceType: invoiceData.invoiceType || 'TAX_INVOICE',
            subtotal: subtotal,
            discountAmount: discountAmount,
            taxAmount: taxAmount,
            totalAmount: totalAmount,
            roundOff: roundOff,
            grandTotal: grandTotal,
            cgstAmount: totalCGST,
            sgstAmount: totalSGST,
            igstAmount: totalIGST,
            cessAmount: totalCESS,
            notes: invoiceData.notes,
            termsAndConditions: invoiceData.termsAndConditions,
            createdBy: userId,
            updatedBy: userId
          }
        });

        // Create invoice items
        const invoiceItems = await Promise.all(
          validatedItems.map(async (item) => {
            return await tx.salesInvoiceItem.create({
              data: {
                invoiceId: invoice.id,
                productId: item.productId,
                hsnCode: item.hsnCode,
                description: item.description,
                quantity: item.quantity,
                unit: item.unit,
                unitPrice: item.unitPrice,
                discountPercent: item.discountPercent,
                discountAmount: item.discountAmount,
                taxableAmount: item.taxableAmount,
                gstRate: item.gstRate,
                gstAmount: item.gstAmount,
                cgstAmount: item.cgstAmount,
                sgstAmount: item.sgstAmount,
                igstAmount: item.igstAmount,
                cessRate: item.cessRate,
                cessAmount: item.cessAmount,
                totalAmount: item.totalAmount,
                batchNumber: item.batchNumber,
                expiryDate: item.expiryDate
              }
            });
          })
        );

        // Update stock (record OUT movements)
        for (const item of validatedItems) {
          const stockMovement = {
            productId: item.productId,
            locationId: '', // TODO: Get default location
            movementType: 'OUT' as const,
            quantity: item.quantity,
            batchNumber: item.batchNumber,
            referenceType: 'SALES_INVOICE',
            referenceId: invoice.id,
            userId: userId,
            companyId: companyId,
            remarks: `Sale: Invoice ${invoiceNumber}`
          };

          await this.stockLedger.recordMovement(stockMovement, tx);
        }

        // Create ledger entries
        await this.ledgerEngine.createSalesEntry(
          invoice.id,
          customerId,
          grandTotal,
          totalCGST,
          totalSGST,
          totalIGST,
          totalCESS,
          userId,
          companyId,
          tx
        );

        // Log audit entry
        await this.auditLogger.log(
          'CREATE',
          'BILLING',
          'SALES_INVOICE',
          invoice.id,
          userId,
          companyId,
          undefined,
          {
            invoiceNumber,
            customerId: invoiceData.customerId,
            grandTotal,
            items: validatedItems.length
          },
          tx
        );

        return {
          invoice: {
            ...invoice,
            salesInvoiceItems: invoiceItems
          }
        };
      });

      return result.invoice;
    } catch (error) {
      throw new Error(`Failed to create sales invoice: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get sales invoice by ID
   * @param invoiceId Invoice ID
   * @param companyId Company ID
   * @returns Invoice details with items
   */
  public async getSalesInvoiceById(invoiceId: string, companyId: string): Promise<any> {
    try {
      const invoice = await this.prisma.salesInvoice.findFirst({
        where: {
          id: invoiceId,
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
          },
          salesInvoiceItems: {
            include: {
              product: {
                select: {
                  name: true,
                  sku: true,
                  unit: true
                }
              }
            }
          }
        }
      });

      if (!invoice) {
        throw new Error('Sales invoice not found');
      }

      return invoice;
    } catch (error) {
      throw new Error(`Failed to get sales invoice: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * List sales invoices with filtering
   * @param filters Invoice filters
   * @param companyId Company ID
   * @returns List of invoices with pagination
   */
  public async listSalesInvoices(
    filters: InvoiceFilters,
    companyId: string
  ): Promise<{ invoices: any[]; total: number; page: number; limit: number }> {
    try {
      const page = filters.page || 1;
      const limit = filters.limit || 20;
      const skip = (page - 1) * limit;

      const whereConditions: any = {
        companyId: companyId
      };

      if (filters.customerId) {
        whereConditions.customerId = filters.customerId;
      }

      if (filters.invoiceDateFrom) {
        whereConditions.invoiceDate = { ...whereConditions.invoiceDate, gte: filters.invoiceDateFrom };
      }

      if (filters.invoiceDateTo) {
        whereConditions.invoiceDate = { ...whereConditions.invoiceDate, lte: filters.invoiceDateTo };
      }

      if (filters.paymentStatus) {
        whereConditions.paymentStatus = filters.paymentStatus;
      }

      if (filters.isCancelled !== undefined) {
        whereConditions.isCancelled = filters.isCancelled;
      }

      const [invoices, total] = await Promise.all([
        this.prisma.salesInvoice.findMany({
          where: whereConditions,
          include: {
            customer: {
              select: {
                customerCode: true,
                companyName: true,
                gstin: true
              }
            }
          },
          orderBy: { invoiceDate: 'desc' },
          skip,
          take: limit
        }),
        this.prisma.salesInvoice.count({ where: whereConditions })
      ]);

      return {
        invoices,
        total,
        page,
        limit
      };
    } catch (error) {
      throw new Error(`Failed to list sales invoices: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Cancel sales invoice
   * @param invoiceId Invoice ID
   * @param userId User cancelling the invoice
   * @param companyId Company ID
   * @param reason Cancellation reason
   */
  public async cancelSalesInvoice(
    invoiceId: string,
    userId: string,
    companyId: string,
    reason: string
  ): Promise<void> {
    try {
      const invoice = await this.prisma.salesInvoice.findFirst({
        where: {
          id: invoiceId,
          companyId: companyId
        }
      });

      if (!invoice) {
        throw new Error('Sales invoice not found');
      }

      if (invoice.isCancelled) {
        throw new Error('Invoice is already cancelled');
      }

      // Check if invoice has payments
      const paymentCount = await this.prisma.invoicePayment.count({
        where: {
          invoiceId: invoiceId,
          invoiceType: 'SALES'
        }
      });

      if (paymentCount > 0) {
        throw new Error('Cannot cancel invoice with payments. Create a credit note instead.');
      }

      // Start transaction
      await this.prisma.$transaction(async (tx) => {
        // Update invoice status
        await tx.salesInvoice.update({
          where: { id: invoiceId },
          data: {
            isCancelled: true,
            cancelledAt: new Date(),
            cancelledBy: userId,
            cancellationReason: reason,
            updatedBy: userId
          }
        });

        // Reverse stock movements
        const invoiceItems = await tx.salesInvoiceItem.findMany({
          where: { invoiceId: invoiceId }
        });

        for (const item of invoiceItems) {
          const stockMovement = {
            productId: item.productId,
            locationId: '', // TODO: Get default location
            movementType: 'IN' as const,
            quantity: item.quantity,
            batchNumber: item.batchNumber,
            referenceType: 'SALES_INVOICE_CANCEL',
            referenceId: invoiceId,
            userId: userId,
            companyId: companyId,
            remarks: `Cancellation: Invoice ${invoice.invoiceNumber}`
          };

          await this.stockLedger.recordMovement(stockMovement, tx);
        }

        // Reverse ledger entries
        await this.ledgerEngine.reverseEntry(
          invoiceId,
          'SALES_INVOICE',
          userId,
          companyId,
          tx
        );

        // Log audit entry
        await this.auditLogger.log(
          'CANCEL',
          'BILLING',
          'SALES_INVOICE',
          invoiceId,
          userId,
          companyId,
          undefined,
          { reason },
          tx
        );
      });
    } catch (error) {
      throw new Error(`Failed to cancel sales invoice: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Generate invoice number
   * @param prefix Invoice prefix (SI for Sales Invoice)
   * @param companyId Company ID
   * @returns Generated invoice number
   */
  private async generateInvoiceNumber(prefix: string, companyId: string): Promise<string> {
    try {
      // Get the next sequence number for this company and prefix
      const result = await this.prisma.$queryRaw`
        SELECT COALESCE(MAX(CAST(SUBSTRING(invoice_number FROM LENGTH(${prefix}) + 2) AS INTEGER)), 0) + 1 as next_number
        FROM sales_invoices
        WHERE company_id = ${companyId}
        AND invoice_number LIKE ${prefix + '/%'}
      ` as any[];

      const nextNumber = result[0].next_number;
      const year = new Date().getFullYear();
      
      // Generate invoice number (e.g., SI/2024/0001)
      return `${prefix}/${year}/${nextNumber.toString().padStart(4, '0')}`;
    } catch (error) {
      throw new Error(`Failed to generate invoice number: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get invoice summary statistics
   * @param companyId Company ID
   * @param fromDate Start date
   * @param toDate End date
   * @returns Invoice summary
   */
  public async getInvoiceSummary(
    companyId: string,
    fromDate?: Date,
    toDate?: Date
  ): Promise<any> {
    try {
      const whereConditions: any = {
        companyId: companyId,
        isCancelled: false
      };

      if (fromDate) {
        whereConditions.invoiceDate = { ...whereConditions.invoiceDate, gte: fromDate };
      }

      if (toDate) {
        whereConditions.invoiceDate = { ...whereConditions.invoiceDate, lte: toDate };
      }

      const summary = await this.prisma.salesInvoice.aggregate({
        where: whereConditions,
        _count: {
          id: true
        },
        _sum: {
          grandTotal: true,
          cgstAmount: true,
          sgstAmount: true,
          igstAmount: true,
          cessAmount: true
        }
      });

      // Get payment status breakdown
      const statusBreakdown = await this.prisma.salesInvoice.groupBy({
        by: ['paymentStatus'],
        where: whereConditions,
        _count: {
          id: true
        }
      });

      return {
        totalInvoices: summary._count.id,
        totalAmount: summary._sum.grandTotal || 0,
        totalCGST: summary._sum.cgstAmount || 0,
        totalSGST: summary._sum.sgstAmount || 0,
        totalIGST: summary._sum.igstAmount || 0,
        totalCESS: summary._sum.cessAmount || 0,
        statusBreakdown: statusBreakdown
      };
    } catch (error) {
      throw new Error(`Failed to get invoice summary: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Create purchase invoice with automatic GST calculation
   * @param invoiceData Invoice input data
   * @param userId User creating the invoice
   * @param companyId Company ID
   * @returns Created invoice with items
   */
  public async createPurchaseInvoice(
    invoiceData: PurchaseInvoiceInput,
    userId: string,
    companyId: string
  ): Promise<any> {
    try {
      // Validate vendor exists
      const vendor = await this.prisma.vendor.findFirst({
        where: {
          id: invoiceData.vendorId,
          companyId: companyId,
          isActive: true
        }
      });

      if (!vendor) {
        throw new Error('Vendor not found or inactive');
      }

      // Validate products and calculate totals
      let subtotal = 0;
      let totalTaxableAmount = 0;
      let totalGSTAmount = 0;
      let totalCGST = 0;
      let totalSGST = 0;
      let totalIGST = 0;
      let totalCESS = 0;

      // Validate items and calculate amounts
      const validatedItems = await Promise.all(
        invoiceData.items.map(async (item) => {
          // Validate product exists
          const product = await this.prisma.product.findFirst({
            where: {
              id: item.productId,
              companyId: companyId,
              isActive: true
            }
          });

          if (!product) {
            throw new Error(`Product not found: ${item.productId}`);
          }

          // Calculate item amounts
          const discountAmount = item.discountPercent ? 
            (item.unitPrice * item.quantity * item.discountPercent / 100) : 0;
          const taxableAmount = (item.unitPrice * item.quantity) - discountAmount;
          const hsnCode = item.hsnCode || product.hsnCode || '0000';
          
          // Calculate GST using GST Engine
          const gstCalculation = this.gstEngine.calculateGST(
            taxableAmount,
            product.gstRate,
            vendor.state === 'YOUR_STATE' ? 'INTRA_STATE' : 'INTER_STATE', // TODO: Get company state
            0 // CESS rate
          );

          subtotal += item.unitPrice * item.quantity;
          totalTaxableAmount += taxableAmount;
          totalGSTAmount += gstCalculation.totalGst;
          totalCGST += gstCalculation.cgstAmount;
          totalSGST += gstCalculation.sgstAmount;
          totalIGST += gstCalculation.igstAmount;
          totalCESS += gstCalculation.cessAmount;

          return {
            productId: item.productId,
            hsnCode: hsnCode,
            description: item.description || product.name,
            quantity: item.quantity,
            unit: product.unit,
            unitPrice: item.unitPrice,
            discountPercent: item.discountPercent || 0,
            discountAmount: discountAmount,
            taxableAmount: taxableAmount,
            gstRate: product.gstRate,
            gstAmount: gstCalculation.totalGst,
            cgstAmount: gstCalculation.cgstAmount,
            sgstAmount: gstCalculation.sgstAmount,
            igstAmount: gstCalculation.igstAmount,
            cessRate: 0,
            cessAmount: gstCalculation.cessAmount,
            totalAmount: taxableAmount + gstCalculation.totalGst,
            batchNumber: item.batchNumber,
            expiryDate: item.expiryDate
          };
        })
      );

      // Calculate invoice totals
      const discountAmount = invoiceData.discountAmount || 0;
      const taxableAmount = totalTaxableAmount - discountAmount;
      const taxAmount = totalGSTAmount;
      const totalAmount = taxableAmount + taxAmount;
      const roundOff = invoiceData.roundOff || 0;
      const grandTotal = Math.round(totalAmount + roundOff);

      // Generate invoice number
      const invoiceNumber = await this.generateInvoiceNumber('PI', companyId);

      // Start transaction
      const result = await this.prisma.$transaction(async (tx) => {
        // Create purchase invoice
        const invoice = await tx.purchaseInvoice.create({
          data: {
            companyId: companyId,
            invoiceNumber: invoiceNumber,
            invoiceDate: invoiceData.invoiceDate,
            dueDate: invoiceData.dueDate,
            vendorId: invoiceData.vendorId,
            vendorGstin: vendor.gstin,
            billingAddress: invoiceData.billingAddress || vendor.address,
            shippingAddress: invoiceData.shippingAddress,
            placeOfSupply: invoiceData.placeOfSupply,
            invoiceType: invoiceData.invoiceType || 'TAX_INVOICE',
            subtotal: subtotal,
            discountAmount: discountAmount,
            taxAmount: taxAmount,
            totalAmount: totalAmount,
            roundOff: roundOff,
            grandTotal: grandTotal,
            cgstAmount: totalCGST,
            sgstAmount: totalSGST,
            igstAmount: totalIGST,
            cessAmount: totalCESS,
            notes: invoiceData.notes,
            termsAndConditions: invoiceData.termsAndConditions,
            createdBy: userId,
            updatedBy: userId
          }
        });

        // Create invoice items
        const invoiceItems = await Promise.all(
          validatedItems.map(async (item) => {
            return await tx.purchaseInvoiceItem.create({
              data: {
                invoiceId: invoice.id,
                productId: item.productId,
                hsnCode: item.hsnCode,
                description: item.description,
                quantity: item.quantity,
                unit: item.unit,
                unitPrice: item.unitPrice,
                discountPercent: item.discountPercent,
                discountAmount: item.discountAmount,
                taxableAmount: item.taxableAmount,
                gstRate: item.gstRate,
                gstAmount: item.gstAmount,
                cgstAmount: item.cgstAmount,
                sgstAmount: item.sgstAmount,
                igstAmount: item.igstAmount,
                cessRate: item.cessRate,
                cessAmount: item.cessAmount,
                totalAmount: item.totalAmount,
                batchNumber: item.batchNumber,
                expiryDate: item.expiryDate
              }
            });
          })
        );

        // Update stock (record IN movements)
        for (const item of validatedItems) {
          const stockMovement = {
            productId: item.productId,
            locationId: '', // TODO: Get default location
            movementType: 'IN' as const,
            quantity: item.quantity,
            batchNumber: item.batchNumber,
            expiryDate: item.expiryDate,
            referenceType: 'PURCHASE_INVOICE',
            referenceId: invoice.id,
            userId: userId,
            companyId: companyId,
            remarks: `Purchase: Invoice ${invoiceNumber}`
          };

          await this.stockLedger.recordMovement(stockMovement, tx);
        }

        // Create ledger entries
        await this.ledgerEngine.createPurchaseEntry(
          invoice.id,
          invoiceData.vendorId,
          grandTotal,
          totalCGST,
          totalSGST,
          totalIGST,
          totalCESS,
          userId,
          companyId,
          tx
        );

        // Log audit entry
        await this.auditLogger.log(
          'CREATE',
          'BILLING',
          'PURCHASE_INVOICE',
          invoice.id,
          userId,
          companyId,
          undefined,
          {
            invoiceNumber,
            vendorId: invoiceData.vendorId,
            grandTotal,
            items: validatedItems.length
          },
          tx
        );

        return {
          invoice: {
            ...invoice,
            purchaseInvoiceItems: invoiceItems
          }
        };
      });

      return result.invoice;
    } catch (error) {
      throw new Error(`Failed to create purchase invoice: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get purchase invoice by ID
   * @param invoiceId Invoice ID
   * @param companyId Company ID
   * @returns Invoice details with items
   */
  public async getPurchaseInvoiceById(invoiceId: string, companyId: string): Promise<any> {
    try {
      const invoice = await this.prisma.purchaseInvoice.findFirst({
        where: {
          id: invoiceId,
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
          },
          purchaseInvoiceItems: {
            include: {
              product: {
                select: {
                  name: true,
                  sku: true,
                  unit: true
                }
              }
            }
          }
        }
      });

      if (!invoice) {
        throw new Error('Purchase invoice not found');
      }

      return invoice;
    } catch (error) {
      throw new Error(`Failed to get purchase invoice: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * List purchase invoices with filtering
   * @param filters Invoice filters
   * @param companyId Company ID
   * @returns List of invoices with pagination
   */
  public async listPurchaseInvoices(
    filters: InvoiceFilters,
    companyId: string
  ): Promise<{ invoices: any[]; total: number; page: number; limit: number }> {
    try {
      const page = filters.page || 1;
      const limit = filters.limit || 20;
      const skip = (page - 1) * limit;

      const whereConditions: any = {
        companyId: companyId
      };

      if (filters.vendorId) {
        whereConditions.vendorId = filters.vendorId;
      }

      if (filters.invoiceDateFrom) {
        whereConditions.invoiceDate = { ...whereConditions.invoiceDate, gte: filters.invoiceDateFrom };
      }

      if (filters.invoiceDateTo) {
        whereConditions.invoiceDate = { ...whereConditions.invoiceDate, lte: filters.invoiceDateTo };
      }

      if (filters.paymentStatus) {
        whereConditions.paymentStatus = filters.paymentStatus;
      }

      if (filters.isCancelled !== undefined) {
        whereConditions.isCancelled = filters.isCancelled;
      }

      const [invoices, total] = await Promise.all([
        this.prisma.purchaseInvoice.findMany({
          where: whereConditions,
          include: {
            vendor: {
              select: {
                vendorCode: true,
                companyName: true,
                gstin: true
              }
            }
          },
          orderBy: { invoiceDate: 'desc' },
          skip,
          take: limit
        }),
        this.prisma.purchaseInvoice.count({ where: whereConditions })
      ]);

      return {
        invoices,
        total,
        page,
        limit
      };
    } catch (error) {
      throw new Error(`Failed to list purchase invoices: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Cancel purchase invoice
   * @param invoiceId Invoice ID
   * @param userId User cancelling the invoice
   * @param companyId Company ID
   * @param reason Cancellation reason
   */
  public async cancelPurchaseInvoice(
    invoiceId: string,
    userId: string,
    companyId: string,
    reason: string
  ): Promise<void> {
    try {
      const invoice = await this.prisma.purchaseInvoice.findFirst({
        where: {
          id: invoiceId,
          companyId: companyId
        }
      });

      if (!invoice) {
        throw new Error('Purchase invoice not found');
      }

      if (invoice.isCancelled) {
        throw new Error('Invoice is already cancelled');
      }

      // Check if invoice has payments
      const paymentCount = await this.prisma.invoicePayment.count({
        where: {
          invoiceId: invoiceId,
          invoiceType: 'PURCHASE'
        }
      });

      if (paymentCount > 0) {
        throw new Error('Cannot cancel invoice with payments. Create a debit note instead.');
      }

      // Start transaction
      await this.prisma.$transaction(async (tx) => {
        // Update invoice status
        await tx.purchaseInvoice.update({
          where: { id: invoiceId },
          data: {
            isCancelled: true,
            cancelledAt: new Date(),
            cancelledBy: userId,
            cancellationReason: reason,
            updatedBy: userId
          }
        });

        // Reverse stock movements
        const invoiceItems = await tx.purchaseInvoiceItem.findMany({
          where: { invoiceId: invoiceId }
        });

        for (const item of invoiceItems) {
          const stockMovement = {
            productId: item.productId,
            locationId: '', // TODO: Get default location
            movementType: 'OUT' as const,
            quantity: item.quantity,
            batchNumber: item.batchNumber,
            referenceType: 'PURCHASE_INVOICE_CANCEL',
            referenceId: invoiceId,
            userId: userId,
            companyId: companyId,
            remarks: `Cancellation: Invoice ${invoice.invoiceNumber}`
          };

          await this.stockLedger.recordMovement(stockMovement, tx);
        }

        // Reverse ledger entries
        await this.ledgerEngine.reverseEntry(
          invoiceId,
          'PURCHASE_INVOICE',
          userId,
          companyId,
          tx
        );

        // Log audit entry
        await this.auditLogger.log(
          'CANCEL',
          'BILLING',
          'PURCHASE_INVOICE',
          invoiceId,
          userId,
          companyId,
          undefined,
          { reason },
          tx
        );
      });
    } catch (error) {
      throw new Error(`Failed to cancel purchase invoice: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get purchase invoice summary statistics
   * @param companyId Company ID
   * @param fromDate Start date
   * @param toDate End date
   * @returns Invoice summary
   */
  public async getPurchaseInvoiceSummary(
    companyId: string,
    fromDate?: Date,
    toDate?: Date
  ): Promise<any> {
    try {
      const whereConditions: any = {
        companyId: companyId,
        isCancelled: false
      };

      if (fromDate) {
        whereConditions.invoiceDate = { ...whereConditions.invoiceDate, gte: fromDate };
      }

      if (toDate) {
        whereConditions.invoiceDate = { ...whereConditions.invoiceDate, lte: toDate };
      }

      const summary = await this.prisma.purchaseInvoice.aggregate({
        where: whereConditions,
        _count: {
          id: true
        },
        _sum: {
          grandTotal: true,
          cgstAmount: true,
          sgstAmount: true,
          igstAmount: true,
          cessAmount: true
        }
      });

      // Get payment status breakdown
      const statusBreakdown = await this.prisma.purchaseInvoice.groupBy({
        by: ['paymentStatus'],
        where: whereConditions,
        _count: {
          id: true
        }
      });

      return {
        totalInvoices: summary._count.id,
        totalAmount: summary._sum.grandTotal || 0,
        totalCGST: summary._sum.cgstAmount || 0,
        totalSGST: summary._sum.sgstAmount || 0,
        totalIGST: summary._sum.igstAmount || 0,
        totalCESS: summary._sum.cessAmount || 0,
        statusBreakdown: statusBreakdown
      };
    } catch (error) {
      throw new Error(`Failed to get purchase invoice summary: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Close database connections
   */
  public async disconnect(): Promise<void> {
    await this.prisma.$disconnect();
    await this.gstEngine.disconnect();
    await this.ledgerEngine.disconnect();
    await this.stockLedger.disconnect();
    await this.auditLogger.disconnect();
  }
}