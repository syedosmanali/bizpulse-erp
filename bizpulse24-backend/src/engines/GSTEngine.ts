import { PrismaClient } from '@prisma/client';
import { GSTRate } from '../models/types';

// Interface for GST calculation result
export interface GSTCalculation {
  taxableAmount: number;
  gstRate: number;
  cgst: number;
  sgst: number;
  igst: number;
  totalGst: number;
  totalAmount: number;
}

// Interface for line item with GST details
export interface LineItem {
  id: string;
  productId: string;
  quantity: number;
  rate: number;
  discount?: number;
  taxableAmount: number;
  gstRate: number;
  cgst: number;
  sgst: number;
  igst: number;
  totalGst: number;
  totalAmount: number;
}

/**
 * GST Engine for Indian GST calculations
 * Handles CGST/SGST for intra-state transactions and IGST for inter-state transactions
 */
export class GSTEngine {
  private prisma: PrismaClient;

  constructor() {
    this.prisma = new PrismaClient();
  }

  /**
   * Calculate GST for a given taxable amount and GST rate
   * @param taxableAmount The taxable amount
   * @param gstRate The GST rate (0, 5, 12, 18, 28)
   * @param customerState The customer's state
   * @param companyState The company's state
   * @returns GSTCalculation object with detailed breakdown
   */
  public calculateGST(
    taxableAmount: number,
    gstRate: number,
    customerState: string,
    companyState: string
  ): GSTCalculation {
    // Validate GST rate
    if (!this.isValidGSTRate(gstRate)) {
      throw new Error(`Invalid GST rate: ${gstRate}. Valid rates are: 0, 5, 12, 18, 28`);
    }

    // Validate inputs
    if (taxableAmount < 0) {
      throw new Error('Taxable amount cannot be negative');
    }

    if (!customerState || !companyState) {
      throw new Error('Customer state and company state are required');
    }

    const totalGst = (taxableAmount * gstRate) / 100;
    let cgst = 0;
    let sgst = 0;
    let igst = 0;

    // Determine GST type based on state comparison
    if (customerState.toLowerCase() === companyState.toLowerCase()) {
      // Intra-state: CGST + SGST
      cgst = totalGst / 2;
      sgst = totalGst / 2;
      igst = 0;
    } else {
      // Inter-state: IGST
      cgst = 0;
      sgst = 0;
      igst = totalGst;
    }

    return {
      taxableAmount,
      gstRate,
      cgst: Number(cgst.toFixed(2)),
      sgst: Number(sgst.toFixed(2)),
      igst: Number(igst.toFixed(2)),
      totalGst: Number(totalGst.toFixed(2)),
      totalAmount: Number((taxableAmount + totalGst).toFixed(2))
    };
  }

  /**
   * Create GST entries for an invoice
   * @param invoiceId The invoice ID
   * @param lineItems Array of line items with GST calculations
   * @param customerState The customer's state
   * @param tx Prisma transaction object
   */
  public async createGSTEntries(
    invoiceId: string,
    lineItems: LineItem[],
    customerState: string,
    tx?: PrismaClient
  ): Promise<void> {
    const client = tx || this.prisma;

    try {
      // Create GST entries for each line item
      for (const item of lineItems) {
        await client.$executeRaw`
          INSERT INTO gst_entries (
            id, invoice_id, product_id, quantity, rate, taxable_amount,
            gst_rate, cgst_amount, sgst_amount, igst_amount, total_gst,
            total_amount, created_at, updated_at
          ) VALUES (
            gen_random_uuid(), ${invoiceId}, ${item.productId}, ${item.quantity},
            ${item.rate}, ${item.taxableAmount}, ${item.gstRate}, ${item.cgst},
            ${item.sgst}, ${item.igst}, ${item.totalGst}, ${item.totalAmount},
            NOW(), NOW()
          )
        `;
      }
    } catch (error) {
      throw new Error(`Failed to create GST entries: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Reverse GST entries for a return/credit note
   * @param originalInvoiceId The original invoice ID
   * @param returnLineItems Array of return line items
   * @param tx Prisma transaction object
   */
  public async reverseGSTEntries(
    originalInvoiceId: string,
    returnLineItems: LineItem[],
    tx?: PrismaClient
  ): Promise<void> {
    const client = tx || this.prisma;

    try {
      // Create reverse GST entries (negative amounts)
      for (const item of returnLineItems) {
        await client.$executeRaw`
          INSERT INTO gst_entries (
            id, invoice_id, product_id, quantity, rate, taxable_amount,
            gst_rate, cgst_amount, sgst_amount, igst_amount, total_gst,
            total_amount, is_reversed, original_invoice_id, created_at, updated_at
          ) VALUES (
            gen_random_uuid(), ${originalInvoiceId}, ${item.productId}, ${-item.quantity},
            ${item.rate}, ${-item.taxableAmount}, ${item.gstRate}, ${-item.cgst},
            ${-item.sgst}, ${-item.igst}, ${-item.totalGst}, ${-item.totalAmount},
            true, ${originalInvoiceId}, NOW(), NOW()
          )
        `;
      }
    } catch (error) {
      throw new Error(`Failed to reverse GST entries: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Calculate total GST summary for an invoice
   * @param lineItems Array of line items
   * @returns Summary object with total amounts
   */
  public calculateGSTSummary(lineItems: LineItem[]): {
    totalTaxableAmount: number;
    totalCGST: number;
    totalSGST: number;
    totalIGST: number;
    totalGST: number;
    totalAmount: number;
  } {
    return lineItems.reduce(
      (summary, item) => ({
        totalTaxableAmount: Number((summary.totalTaxableAmount + item.taxableAmount).toFixed(2)),
        totalCGST: Number((summary.totalCGST + item.cgst).toFixed(2)),
        totalSGST: Number((summary.totalSGST + item.sgst).toFixed(2)),
        totalIGST: Number((summary.totalIGST + item.igst).toFixed(2)),
        totalGST: Number((summary.totalGST + item.totalGst).toFixed(2)),
        totalAmount: Number((summary.totalAmount + item.totalAmount).toFixed(2))
      }),
      {
        totalTaxableAmount: 0,
        totalCGST: 0,
        totalSGST: 0,
        totalIGST: 0,
        totalGST: 0,
        totalAmount: 0
      }
    );
  }

  /**
   * Validate if GST rate is valid
   * @param rate GST rate to validate
   * @returns boolean indicating if rate is valid
   */
  private isValidGSTRate(rate: number): boolean {
    return Object.values(GSTRate).includes(rate as GSTRate);
  }

  /**
   * Get GST rates for a product category
   * @param productCategory Product category
   * @returns Applicable GST rate
   */
  public getGSTRateForCategory(productCategory: string): number {
    // This would typically come from a database lookup
    // For now, returning common rates based on category
    const categoryRates: Record<string, number> = {
      'goods': 18,
      'services': 18,
      'food': 5,
      'medicines': 0,
      'books': 0,
      'electronics': 18,
      'clothing': 12,
      'jewelry': 3
    };

    return categoryRates[productCategory.toLowerCase()] || 18;
  }

  /**
   * Close the database connection
   */
  public async disconnect(): Promise<void> {
    await this.prisma.$disconnect();
  }
}