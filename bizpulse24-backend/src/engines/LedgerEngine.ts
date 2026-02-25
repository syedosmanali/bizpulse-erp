import { PrismaClient } from '@prisma/client';

// Interface for ledger entry
export interface LedgerEntry {
  date: Date;
  accountHead: string;
  debitAmount: number;
  creditAmount: number;
  narration: string;
  referenceType: string;
  referenceId: string;
  companyId: string;
}

// Interface for sales invoice
export interface SalesInvoice {
  id: string;
  invoiceNumber: string;
  customerId: string;
  companyId: string;
  invoiceDate: Date;
  taxableAmount: number;
  totalGst: number;
  totalAmount: number;
  lineItems: any[];
}

// Interface for purchase invoice
export interface PurchaseInvoice {
  id: string;
  grnNumber: string;
  vendorId: string;
  companyId: string;
  grnDate: Date;
  taxableAmount: number;
  totalGst: number;
  totalAmount: number;
  lineItems: any[];
}

// Interface for payment
export interface Payment {
  id: string;
  paymentNumber: string;
  partyId: string;
  companyId: string;
  paymentDate: Date;
  amount: number;
  paymentMode: string;
  referenceNumber?: string;
}

/**
 * Ledger Engine for double-entry bookkeeping
 * Implements proper accounting principles where total debits must equal total credits
 */
export class LedgerEngine {
  private prisma: PrismaClient;

  constructor() {
    this.prisma = new PrismaClient();
  }

  /**
   * Create ledger entries - ensures double-entry bookkeeping
   * @param entries Array of ledger entries
   * @param tx Prisma transaction object
   */
  public async createEntries(entries: LedgerEntry[], tx?: PrismaClient): Promise<void> {
    const client = tx || this.prisma;

    // Validate that total debits equal total credits
    const totalDebits = entries.reduce((sum, entry) => sum + entry.debitAmount, 0);
    const totalCredits = entries.reduce((sum, entry) => sum + entry.creditAmount, 0);

    if (Math.abs(totalDebits - totalCredits) > 0.01) {
      throw new Error(
        `Invalid ledger entry: Total debits (${totalDebits}) must equal total credits (${totalCredits})`
      );
    }

    try {
      // Create all ledger entries
      for (const entry of entries) {
        await client.$executeRaw`
          INSERT INTO ledger_entries (
            id, date, account_head, debit_amount, credit_amount,
            narration, reference_type, reference_id, company_id,
            created_at, updated_at
          ) VALUES (
            gen_random_uuid(), ${entry.date}, ${entry.accountHead},
            ${entry.debitAmount}, ${entry.creditAmount}, ${entry.narration},
            ${entry.referenceType}, ${entry.referenceId}, ${entry.companyId},
            NOW(), NOW()
          )
        `;
      }
    } catch (error) {
      throw new Error(`Failed to create ledger entries: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Create ledger entries for sales invoice
   * @param invoice Sales invoice object
   * @param tx Prisma transaction object
   */
  public async createSalesLedgerEntries(invoice: SalesInvoice, tx?: PrismaClient): Promise<void> {
    const client = tx || this.prisma;
    const entries: LedgerEntry[] = [];

    // Debit: Customer Account (Accounts Receivable)
    entries.push({
      date: invoice.invoiceDate,
      accountHead: `CUSTOMER_${invoice.customerId}`,
      debitAmount: invoice.totalAmount,
      creditAmount: 0,
      narration: `Sales Invoice #${invoice.invoiceNumber}`,
      referenceType: 'SALES_INVOICE',
      referenceId: invoice.id,
      companyId: invoice.companyId
    });

    // Credit: Sales Account
    entries.push({
      date: invoice.invoiceDate,
      accountHead: 'SALES',
      debitAmount: 0,
      creditAmount: invoice.taxableAmount,
      narration: `Sales Invoice #${invoice.invoiceNumber} - Sales Amount`,
      referenceType: 'SALES_INVOICE',
      referenceId: invoice.id,
      companyId: invoice.companyId
    });

    // Credit: GST Accounts (if applicable)
    if (invoice.totalGst > 0) {
      // For intra-state sales - CGST and SGST
      const gstBreakdown = this.calculateGSTBreakdown(invoice.totalGst, invoice.companyId);
      
      if (gstBreakdown.cgst > 0) {
        entries.push({
          date: invoice.invoiceDate,
          accountHead: 'CGST_PAYABLE',
          debitAmount: 0,
          creditAmount: gstBreakdown.cgst,
          narration: `Sales Invoice #${invoice.invoiceNumber} - CGST`,
          referenceType: 'SALES_INVOICE',
          referenceId: invoice.id,
          companyId: invoice.companyId
        });
      }

      if (gstBreakdown.sgst > 0) {
        entries.push({
          date: invoice.invoiceDate,
          accountHead: 'SGST_PAYABLE',
          debitAmount: 0,
          creditAmount: gstBreakdown.sgst,
          narration: `Sales Invoice #${invoice.invoiceNumber} - SGST`,
          referenceType: 'SALES_INVOICE',
          referenceId: invoice.id,
          companyId: invoice.companyId
        });
      }

      if (gstBreakdown.igst > 0) {
        entries.push({
          date: invoice.invoiceDate,
          accountHead: 'IGST_PAYABLE',
          debitAmount: 0,
          creditAmount: gstBreakdown.igst,
          narration: `Sales Invoice #${invoice.invoiceNumber} - IGST`,
          referenceType: 'SALES_INVOICE',
          referenceId: invoice.id,
          companyId: invoice.companyId
        });
      }
    }

    await this.createEntries(entries, client);
  }

  /**
   * Create ledger entries for purchase invoice (GRN)
   * @param grn Purchase invoice/GRN object
   * @param tx Prisma transaction object
   */
  public async createPurchaseLedgerEntries(grn: PurchaseInvoice, tx?: PrismaClient): Promise<void> {
    const client = tx || this.prisma;
    const entries: LedgerEntry[] = [];

    // Credit: Vendor Account (Accounts Payable)
    entries.push({
      date: grn.grnDate,
      accountHead: `VENDOR_${grn.vendorId}`,
      debitAmount: 0,
      creditAmount: grn.totalAmount,
      narration: `Purchase Invoice #${grn.grnNumber}`,
      referenceType: 'PURCHASE_INVOICE',
      referenceId: grn.id,
      companyId: grn.companyId
    });

    // Debit: Purchase Account
    entries.push({
      date: grn.grnDate,
      accountHead: 'PURCHASE',
      debitAmount: grn.taxableAmount,
      creditAmount: 0,
      narration: `Purchase Invoice #${grn.grnNumber} - Purchase Amount`,
      referenceType: 'PURCHASE_INVOICE',
      referenceId: grn.id,
      companyId: grn.companyId
    });

    // Debit: GST Input Credit Accounts (if applicable)
    if (grn.totalGst > 0) {
      const gstBreakdown = this.calculateGSTBreakdown(grn.totalGst, grn.companyId);
      
      if (gstBreakdown.cgst > 0) {
        entries.push({
          date: grn.grnDate,
          accountHead: 'CGST_INPUT_CREDIT',
          debitAmount: gstBreakdown.cgst,
          creditAmount: 0,
          narration: `Purchase Invoice #${grn.grnNumber} - CGST Input Credit`,
          referenceType: 'PURCHASE_INVOICE',
          referenceId: grn.id,
          companyId: grn.companyId
        });
      }

      if (gstBreakdown.sgst > 0) {
        entries.push({
          date: grn.grnDate,
          accountHead: 'SGST_INPUT_CREDIT',
          debitAmount: gstBreakdown.sgst,
          creditAmount: 0,
          narration: `Purchase Invoice #${grn.grnNumber} - SGST Input Credit`,
          referenceType: 'PURCHASE_INVOICE',
          referenceId: grn.id,
          companyId: grn.companyId
        });
      }

      if (gstBreakdown.igst > 0) {
        entries.push({
          date: grn.grnDate,
          accountHead: 'IGST_INPUT_CREDIT',
          debitAmount: gstBreakdown.igst,
          creditAmount: 0,
          narration: `Purchase Invoice #${grn.grnNumber} - IGST Input Credit`,
          referenceType: 'PURCHASE_INVOICE',
          referenceId: grn.id,
          companyId: grn.companyId
        });
      }
    }

    await this.createEntries(entries, client);
  }

  /**
   * Create ledger entries for customer payment/receipt
   * @param payment Payment object
   * @param tx Prisma transaction object
   */
  public async createPaymentReceiptEntries(payment: Payment, tx?: PrismaClient): Promise<void> {
    const client = tx || this.prisma;
    const entries: LedgerEntry[] = [];

    // Debit: Cash/Bank Account
    const accountHead = payment.paymentMode === 'CASH' ? 'CASH' : 'BANK';
    entries.push({
      date: payment.paymentDate,
      accountHead: accountHead,
      debitAmount: payment.amount,
      creditAmount: 0,
      narration: `Payment Receipt #${payment.paymentNumber} from Customer`,
      referenceType: 'PAYMENT_RECEIPT',
      referenceId: payment.id,
      companyId: payment.companyId
    });

    // Credit: Customer Account
    entries.push({
      date: payment.paymentDate,
      accountHead: `CUSTOMER_${payment.partyId}`,
      debitAmount: 0,
      creditAmount: payment.amount,
      narration: `Payment Receipt #${payment.paymentNumber}`,
      referenceType: 'PAYMENT_RECEIPT',
      referenceId: payment.id,
      companyId: payment.companyId
    });

    await this.createEntries(entries, client);
  }

  /**
   * Create ledger entries for vendor payment
   * @param payment Payment object
   * @param tx Prisma transaction object
   */
  public async createVendorPaymentEntries(payment: Payment, tx?: PrismaClient): Promise<void> {
    const client = tx || this.prisma;
    const entries: LedgerEntry[] = [];

    // Debit: Vendor Account
    entries.push({
      date: payment.paymentDate,
      accountHead: `VENDOR_${payment.partyId}`,
      debitAmount: payment.amount,
      creditAmount: 0,
      narration: `Vendor Payment #${payment.paymentNumber}`,
      referenceType: 'VENDOR_PAYMENT',
      referenceId: payment.id,
      companyId: payment.companyId
    });

    // Credit: Cash/Bank Account
    const accountHead = payment.paymentMode === 'CASH' ? 'CASH' : 'BANK';
    entries.push({
      date: payment.paymentDate,
      accountHead: accountHead,
      debitAmount: 0,
      creditAmount: payment.amount,
      narration: `Vendor Payment #${payment.paymentNumber} to Vendor`,
      referenceType: 'VENDOR_PAYMENT',
      referenceId: payment.id,
      companyId: payment.companyId
    });

    await this.createEntries(entries, client);
  }

  /**
   * Get account balance as of a specific date
   * @param accountHead Account head name
   * @param asOfDate Date to calculate balance as of
   * @param companyId Company ID
   * @param tx Prisma transaction object
   * @returns Account balance
   */
  public async getAccountBalance(
    accountHead: string,
    asOfDate: Date,
    companyId: string,
    tx?: PrismaClient
  ): Promise<number> {
    const client = tx || this.prisma;

    try {
      const result = await client.$queryRaw<any[]>`
        SELECT 
          COALESCE(SUM(debit_amount), 0) - COALESCE(SUM(credit_amount), 0) as balance
        FROM ledger_entries
        WHERE account_head = ${accountHead}
          AND company_id = ${companyId}
          AND date <= ${asOfDate}
      `;

      return result[0]?.balance || 0;
    } catch (error) {
      throw new Error(`Failed to get account balance: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get trial balance for a company
   * @param companyId Company ID
   * @param startDate Start date
   * @param endDate End date
   * @param tx Prisma transaction object
   * @returns Trial balance data
   */
  public async getTrialBalance(
    companyId: string,
    startDate: Date,
    endDate: Date,
    tx?: PrismaClient
  ): Promise<any[]> {
    const client = tx || this.prisma;

    try {
      const result = await client.$queryRaw<any[]>`
        SELECT 
          account_head,
          COALESCE(SUM(debit_amount), 0) as total_debit,
          COALESCE(SUM(credit_amount), 0) as total_credit,
          (COALESCE(SUM(debit_amount), 0) - COALESCE(SUM(credit_amount), 0)) as balance
        FROM ledger_entries
        WHERE company_id = ${companyId}
          AND date >= ${startDate}
          AND date <= ${endDate}
        GROUP BY account_head
        ORDER BY account_head
      `;

      return result;
    } catch (error) {
      throw new Error(`Failed to get trial balance: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Calculate GST breakdown for ledger entries
   * @param totalGst Total GST amount
   * @param companyId Company ID (to determine state)
   * @returns GST breakdown object
   */
  private calculateGSTBreakdown(totalGst: number, companyId: string): { cgst: number; sgst: number; igst: number } {
    // This would typically fetch company state from database
    // For now, assuming intra-state (CGST + SGST)
    return {
      cgst: totalGst / 2,
      sgst: totalGst / 2,
      igst: 0
    };
  }

  /**
   * Close the database connection
   */
  public async disconnect(): Promise<void> {
    await this.prisma.$disconnect();
  }
}