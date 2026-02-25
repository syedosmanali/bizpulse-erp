import express, { Request, Response } from 'express';
import { ChartOfAccountsService, LedgerService, TrialBalanceService, ProfitLossService, BalanceSheetService, CashFlowService } from '../services/FinancialReportsService';
import { authenticate, authorize, AuthRequest } from '../middleware/auth';
import { UserRole } from '../models/types';

const router: express.Router = express.Router();
const chartOfAccountsService = new ChartOfAccountsService();
const ledgerService = new LedgerService();
const trialBalanceService = new TrialBalanceService();
const profitLossService = new ProfitLossService();
const balanceSheetService = new BalanceSheetService();
const cashFlowService = new CashFlowService();

// Extend Request type to include user
interface FinancialRequest extends AuthRequest {
  params: {
    accountId?: string;
    companyId?: string;
    financialYear?: string;
    statementId?: string;
  };
  body: any;
  query: any;
}

/**
 * CHART OF ACCOUNTS ROUTES
 */

// Create chart of account
router.post('/accounts',
  authenticate,
  authorize(UserRole.OWNER, UserRole.ADMIN),
  async (req: FinancialRequest, res: Response) => {
    try {
      const { accountCode, accountName, accountType, parentAccountId, isGroup, openingBalance, openingBalanceType, isActive } = req.body;

      if (!accountCode || !accountName || !accountType) {
        return res.status(400).json({
          success: false,
          message: 'Account code, name, and type are required'
        });
      }

      const accountData = {
        accountCode,
        accountName,
        accountType,
        parentAccountId,
        isGroup,
        openingBalance,
        openingBalanceType,
        isActive
      };

      const account = await chartOfAccountsService.createAccount(
        accountData,
        req.user!.id,
        req.user!.companyId
      );

      res.status(201).json({
        success: true,
        message: 'Account created successfully',
        data: account
      });
    } catch (error) {
      res.status(400).json({
        success: false,
        message: error instanceof Error ? error.message : 'Failed to create account'
      });
    }
  }
);

// Get account by ID
router.get('/accounts/:accountId',
  authenticate,
  async (req: FinancialRequest, res: Response) => {
    try {
      const account = await chartOfAccountsService.getAccountById(
        req.params.accountId!,
        req.user!.companyId
      );

      res.json({
        success: true,
        data: account
      });
    } catch (error) {
      res.status(404).json({
        success: false,
        message: error instanceof Error ? error.message : 'Account not found'
      });
    }
  }
);

// Update account
router.put('/accounts/:accountId',
  authenticate,
  authorize(UserRole.OWNER, UserRole.ADMIN),
  async (req: FinancialRequest, res: Response) => {
    try {
      const account = await chartOfAccountsService.updateAccount(
        req.params.accountId!,
        req.body,
        req.user!.id,
        req.user!.companyId
      );

      res.json({
        success: true,
        message: 'Account updated successfully',
        data: account
      });
    } catch (error) {
      res.status(400).json({
        success: false,
        message: error instanceof Error ? error.message : 'Failed to update account'
      });
    }
  }
);

// Delete account (soft delete)
router.delete('/accounts/:accountId',
  authenticate,
  authorize(UserRole.OWNER),
  async (req: FinancialRequest, res: Response) => {
    try {
      await chartOfAccountsService.deleteAccount(
        req.params.accountId!,
        req.user!.id,
        req.user!.companyId
      );

      res.json({
        success: true,
        message: 'Account deleted successfully'
      });
    } catch (error) {
      res.status(400).json({
        success: false,
        message: error instanceof Error ? error.message : 'Failed to delete account'
      });
    }
  }
);

// List accounts
router.get('/accounts',
  authenticate,
  async (req: FinancialRequest, res: Response) => {
    try {
      const filters = {
        accountType: req.query.accountType as string,
        isActive: req.query.isActive !== undefined ? req.query.isActive === 'true' : undefined,
        isGroup: req.query.isGroup !== undefined ? req.query.isGroup === 'true' : undefined,
        search: req.query.search as string
      };

      const page = parseInt(req.query.page as string) || 1;
      const limit = parseInt(req.query.limit as string) || 20;

      const result = await chartOfAccountsService.listAccounts(
        req.user!.companyId,
        filters,
        page,
        limit
      );

      res.json({
        success: true,
        data: result.accounts,
        pagination: {
          total: result.total,
          page: result.page,
          limit: result.limit,
          totalPages: Math.ceil(result.total / result.limit)
        }
      });
    } catch (error) {
      res.status(400).json({
        success: false,
        message: error instanceof Error ? error.message : 'Failed to list accounts'
      });
    }
  }
);

// Get account hierarchy
router.get('/accounts/hierarchy/tree',
  authenticate,
  async (req: FinancialRequest, res: Response) => {
    try {
      const includeInactive = req.query.includeInactive === 'true';
      
      const hierarchy = await chartOfAccountsService.getAccountHierarchy(
        req.user!.companyId,
        includeInactive
      );

      res.json({
        success: true,
        data: hierarchy
      });
    } catch (error) {
      res.status(400).json({
        success: false,
        message: error instanceof Error ? error.message : 'Failed to get account hierarchy'
      });
    }
  }
);

// Get account balance
router.get('/accounts/:accountId/balance',
  authenticate,
  async (req: FinancialRequest, res: Response) => {
    try {
      const asOfDate = req.query.asOfDate ? new Date(req.query.asOfDate as string) : undefined;
      
      const balance = await chartOfAccountsService.getAccountBalance(
        req.params.accountId!,
        req.user!.companyId,
        asOfDate
      );

      res.json({
        success: true,
        data: {
          accountId: req.params.accountId,
          balance: balance,
          asOfDate: asOfDate || new Date()
        }
      });
    } catch (error) {
      res.status(400).json({
        success: false,
        message: error instanceof Error ? error.message : 'Failed to get account balance'
      });
    }
  }
);

/**
 * LEDGER ROUTES
 */

// Create ledger entry
router.post('/ledger',
  authenticate,
  authorize(UserRole.OWNER, UserRole.ADMIN),
  async (req: FinancialRequest, res: Response) => {
    try {
      const { accountId, transactionDate, referenceType, referenceId, description, debitAmount, creditAmount } = req.body;

      // Validate that exactly one of debitAmount or creditAmount is provided
      const hasDebit = debitAmount !== undefined;
      const hasCredit = creditAmount !== undefined;
      
      if ((hasDebit && hasCredit) || (!hasDebit && !hasCredit)) {
        return res.status(400).json({
          success: false,
          message: 'Exactly one of debitAmount or creditAmount must be provided'
        });
      }

      const entryData = {
        accountId,
        transactionDate: new Date(transactionDate),
        referenceType,
        referenceId,
        description,
        debitAmount,
        creditAmount
      };

      const ledgerEntry = await ledgerService.createLedgerEntry(
        entryData,
        req.user!.id,
        req.user!.companyId
      );

      res.status(201).json({
        success: true,
        message: 'Ledger entry created successfully',
        data: ledgerEntry
      });
    } catch (error) {
      res.status(400).json({
        success: false,
        message: error instanceof Error ? error.message : 'Failed to create ledger entry'
      });
    }
  }
);

// Get account ledger
router.get('/ledger/accounts/:accountId',
  authenticate,
  async (req: FinancialRequest, res: Response) => {
    try {
      const fromDate = req.query.fromDate ? new Date(req.query.fromDate as string) : undefined;
      const toDate = req.query.toDate ? new Date(req.query.toDate as string) : undefined;
      const page = parseInt(req.query.page as string) || 1;
      const limit = parseInt(req.query.limit as string) || 50;

      const result = await ledgerService.getAccountLedger(
        req.params.accountId!,
        req.user!.companyId,
        fromDate,
        toDate,
        page,
        limit
      );

      res.json({
        success: true,
        data: {
          entries: result.entries,
          runningBalance: result.runningBalance
        },
        pagination: {
          total: result.total,
          page: result.page,
          limit: result.limit,
          totalPages: Math.ceil(result.total / result.limit)
        }
      });
    } catch (error) {
      res.status(400).json({
        success: false,
        message: error instanceof Error ? error.message : 'Failed to get account ledger'
      });
    }
  }
);

// Create double-entry transaction
router.post('/ledger/double-entry',
  authenticate,
  authorize(UserRole.OWNER, UserRole.ADMIN),
  async (req: FinancialRequest, res: Response) => {
    try {
      const { debitEntries, creditEntries, referenceType, referenceId, description, transactionDate } = req.body;

      if (!debitEntries || !creditEntries || !Array.isArray(debitEntries) || !Array.isArray(creditEntries)) {
        return res.status(400).json({
          success: false,
          message: 'debitEntries and creditEntries must be arrays'
        });
      }

      await ledgerService.createDoubleEntryTransaction(
        debitEntries,
        creditEntries,
        referenceType,
        referenceId,
        description,
        new Date(transactionDate),
        req.user!.id,
        req.user!.companyId
      );

      res.status(201).json({
        success: true,
        message: 'Double-entry transaction created successfully'
      });
    } catch (error) {
      res.status(400).json({
        success: false,
        message: error instanceof Error ? error.message : 'Failed to create double-entry transaction'
      });
    }
  }
);

/**
 * TRIAL BALANCE ROUTES
 */

// Generate trial balance
router.post('/trial-balance/generate',
  authenticate,
  authorize(UserRole.OWNER, UserRole.ADMIN),
  async (req: FinancialRequest, res: Response) => {
    try {
      const { financialYear, periodFrom, periodTo } = req.body;

      if (!financialYear) {
        return res.status(400).json({
          success: false,
          message: 'Financial year is required'
        });
      }

      const trialBalance = await trialBalanceService.generateTrialBalance(
        financialYear,
        req.user!.companyId,
        req.user!.id
      );

      res.status(201).json({
        success: true,
        message: 'Trial balance generated successfully',
        data: trialBalance
      });
    } catch (error) {
      res.status(400).json({
        success: false,
        message: error instanceof Error ? error.message : 'Failed to generate trial balance'
      });
    }
  }
);

// Get trial balance
router.get('/trial-balance/:financialYear',
  authenticate,
  async (req: FinancialRequest, res: Response) => {
    try {
      const accountType = req.query.accountType as string;
      
      const trialBalance = await trialBalanceService.getTrialBalance(
        req.params.financialYear!,
        req.user!.companyId,
        accountType
      );

      res.json({
        success: true,
        data: trialBalance
      });
    } catch (error) {
      res.status(400).json({
        success: false,
        message: error instanceof Error ? error.message : 'Failed to get trial balance'
      });
    }
  }
);

// Validate trial balance
router.get('/trial-balance/:financialYear/validate',
  authenticate,
  authorize(UserRole.OWNER, UserRole.ADMIN),
  async (req: FinancialRequest, res: Response) => {
    try {
      const validation = await trialBalanceService.validateTrialBalance(
        req.params.financialYear!,
        req.user!.companyId
      );

      res.json({
        success: true,
        data: validation
      });
    } catch (error) {
      res.status(400).json({
        success: false,
        message: error instanceof Error ? error.message : 'Failed to validate trial balance'
      });
    }
  }
);

/**
 * PROFIT AND LOSS ROUTES
 */

// Generate profit and loss statement
router.post('/profit-loss/generate',
  authenticate,
  authorize(UserRole.OWNER, UserRole.ADMIN),
  async (req: FinancialRequest, res: Response) => {
    try {
      const { financialYear, periodFrom, periodTo } = req.body;

      if (!financialYear || !periodFrom || !periodTo) {
        return res.status(400).json({
          success: false,
          message: 'Financial year, periodFrom, and periodTo are required'
        });
      }

      const profitLoss = await profitLossService.generateProfitLoss(
        financialYear,
        new Date(periodFrom),
        new Date(periodTo),
        req.user!.companyId,
        req.user!.id
      );

      res.status(201).json({
        success: true,
        message: 'Profit and loss statement generated successfully',
        data: profitLoss
      });
    } catch (error) {
      res.status(400).json({
        success: false,
        message: error instanceof Error ? error.message : 'Failed to generate profit and loss statement'
      });
    }
  }
);

// Get profit and loss statement
router.get('/profit-loss/:financialYear',
  authenticate,
  async (req: FinancialRequest, res: Response) => {
    try {
      const profitLoss = await profitLossService.getProfitLoss(
        req.params.financialYear!,
        req.user!.companyId
      );

      res.json({
        success: true,
        data: profitLoss
      });
    } catch (error) {
      res.status(400).json({
        success: false,
        message: error instanceof Error ? error.message : 'Failed to get profit and loss statement'
      });
    }
  }
);

/**
 * BALANCE SHEET ROUTES
 */

// Generate balance sheet
router.post('/balance-sheet/generate',
  authenticate,
  authorize(UserRole.OWNER, UserRole.ADMIN),
  async (req: FinancialRequest, res: Response) => {
    try {
      const { financialYear, statementDate } = req.body;

      if (!financialYear || !statementDate) {
        return res.status(400).json({
          success: false,
          message: 'Financial year and statement date are required'
        });
      }

      const balanceSheet = await balanceSheetService.generateBalanceSheet(
        financialYear,
        new Date(statementDate),
        req.user!.companyId,
        req.user!.id
      );

      res.status(201).json({
        success: true,
        message: 'Balance sheet generated successfully',
        data: balanceSheet
      });
    } catch (error) {
      res.status(400).json({
        success: false,
        message: error instanceof Error ? error.message : 'Failed to generate balance sheet'
      });
    }
  }
);

// Get balance sheet
router.get('/balance-sheet/:financialYear',
  authenticate,
  async (req: FinancialRequest, res: Response) => {
    try {
      const balanceSheet = await balanceSheetService.getBalanceSheet(
        req.params.financialYear!,
        req.user!.companyId
      );

      res.json({
        success: true,
        data: balanceSheet
      });
    } catch (error) {
      res.status(400).json({
        success: false,
        message: error instanceof Error ? error.message : 'Failed to get balance sheet'
      });
    }
  }
);

/**
 * CASH FLOW ROUTES
 */

// Generate cash flow statement
router.post('/cash-flow/generate',
  authenticate,
  authorize(UserRole.OWNER, UserRole.ADMIN),
  async (req: FinancialRequest, res: Response) => {
    try {
      const { financialYear, periodFrom, periodTo } = req.body;

      if (!financialYear || !periodFrom || !periodTo) {
        return res.status(400).json({
          success: false,
          message: 'Financial year, periodFrom, and periodTo are required'
        });
      }

      const cashFlow = await cashFlowService.generateCashFlow(
        financialYear,
        new Date(periodFrom),
        new Date(periodTo),
        req.user!.companyId,
        req.user!.id
      );

      res.status(201).json({
        success: true,
        message: 'Cash flow statement generated successfully',
        data: cashFlow
      });
    } catch (error) {
      res.status(400).json({
        success: false,
        message: error instanceof Error ? error.message : 'Failed to generate cash flow statement'
      });
    }
  }
);

// Get cash flow statement
router.get('/cash-flow/:financialYear',
  authenticate,
  async (req: FinancialRequest, res: Response) => {
    try {
      const cashFlow = await cashFlowService.getCashFlow(
        req.params.financialYear!,
        req.user!.companyId
      );

      res.json({
        success: true,
        data: cashFlow
      });
    } catch (error) {
      res.status(400).json({
        success: false,
        message: error instanceof Error ? error.message : 'Failed to get cash flow statement'
      });
    }
  }
);

export default router;