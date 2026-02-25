import { PrismaClient } from '@prisma/client';
import { AuditLogger } from '../engines/AuditLogger';

// Interface for customer creation/update
export interface CustomerInput {
  customerCode: string;
  companyName: string;
  contactPerson?: string;
  gstin?: string;
  pan?: string;
  email?: string;
  phone?: string;
  mobile?: string;
  address?: string;
  city?: string;
  state?: string;
  pincode?: string;
  country?: string;
  creditLimit?: number;
  creditDays?: number;
  openingBalance?: number;
  openingBalanceType?: 'DEBIT' | 'CREDIT';
  isActive?: boolean;
}

// Interface for vendor creation/update
export interface VendorInput {
  vendorCode: string;
  companyName: string;
  contactPerson?: string;
  gstin?: string;
  pan?: string;
  email?: string;
  phone?: string;
  mobile?: string;
  address?: string;
  city?: string;
  state?: string;
  pincode?: string;
  country?: string;
  paymentTerms?: number;
  openingBalance?: number;
  openingBalanceType?: 'DEBIT' | 'CREDIT';
  isActive?: boolean;
}

/**
 * Customer Service for Customer Management
 * Handles CRUD operations for customers with GSTIN validation
 */
export class CustomerService {
  private prisma: PrismaClient;
  private auditLogger: AuditLogger;

  constructor() {
    this.prisma = new PrismaClient();
    this.auditLogger = new AuditLogger();
  }

  /**
   * Validate GSTIN format
   * @param gstin GSTIN number to validate
   * @returns boolean indicating if GSTIN is valid
   */
  public static validateGSTIN(gstin: string): boolean {
    if (!gstin) return true; // GSTIN is optional
    
    // GSTIN format: 2 digits (state code) + 5 chars (PAN) + 4 digits + 1 char + 1 digit + 1 char (checksum)
    const gstinRegex = /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[0-9A-Z]{3}$/;
    return gstinRegex.test(gstin.toUpperCase());
  }

  /**
   * Validate PAN format
   * @param pan PAN number to validate
   * @returns boolean indicating if PAN is valid
   */
  public static validatePAN(pan: string): boolean {
    if (!pan) return true; // PAN is optional
    
    // PAN format: 5 uppercase letters + 4 digits + 1 uppercase letter
    const panRegex = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;
    return panRegex.test(pan.toUpperCase());
  }

  /**
   * Create a new customer
   * @param customerData Customer input data
   * @param userId User ID creating the customer
   * @param companyId Company ID
   * @returns Created customer
   */
  public async createCustomer(
    customerData: CustomerInput,
    userId: string,
    companyId: string
  ): Promise<any> {
    try {
      // Validate GSTIN if provided
      if (customerData.gstin && !CustomerService.validateGSTIN(customerData.gstin)) {
        throw new Error('Invalid GSTIN format. Expected format: 22AAAAA0000A1Z5');
      }

      // Validate PAN if provided
      if (customerData.pan && !CustomerService.validatePAN(customerData.pan)) {
        throw new Error('Invalid PAN format. Expected format: AAAAA0000A');
      }

      // Check for duplicate customer code
      const existingCode = await this.prisma.customer.findFirst({
        where: {
          customerCode: customerData.customerCode,
          companyId: companyId
        }
      });

      if (existingCode) {
        throw new Error(`Customer code '${customerData.customerCode}' already exists`);
      }

      // Check for duplicate GSTIN if provided
      if (customerData.gstin) {
        const existingGSTIN = await this.prisma.customer.findFirst({
          where: {
            gstin: customerData.gstin,
            companyId: companyId
          }
        });

        if (existingGSTIN) {
          throw new Error(`Customer with GSTIN '${customerData.gstin}' already exists`);
        }
      }

      // Check for duplicate PAN if provided
      if (customerData.pan) {
        const existingPAN = await this.prisma.customer.findFirst({
          where: {
            pan: customerData.pan,
            companyId: companyId
          }
        });

        if (existingPAN) {
          throw new Error(`Customer with PAN '${customerData.pan}' already exists`);
        }
      }

      // Create customer
      const customer = await this.prisma.customer.create({
        data: {
          ...customerData,
          companyId: companyId,
          createdBy: userId,
          updatedBy: userId
        },
        include: {
          customerDues: true
        }
      });

      // Log audit entry
      await this.auditLogger.log(
        'CREATE',
        'PARTY',
        'CUSTOMER',
        customer.id,
        userId,
        companyId,
        undefined,
        customer
      );

      return customer;
    } catch (error) {
      throw new Error(`Failed to create customer: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get customer by ID
   * @param customerId Customer ID
   * @param companyId Company ID
   * @returns Customer details
   */
  public async getCustomerById(customerId: string, companyId: string): Promise<any> {
    try {
      const customer = await this.prisma.customer.findFirst({
        where: {
          id: customerId,
          companyId: companyId
        },
        include: {
          customerDues: true
        }
      });

      if (!customer) {
        throw new Error('Customer not found');
      }

      return customer;
    } catch (error) {
      throw new Error(`Failed to get customer: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Update customer
   * @param customerId Customer ID
   * @param customerData Updated customer data
   * @param userId User ID updating the customer
   * @param companyId Company ID
   * @returns Updated customer
   */
  public async updateCustomer(
    customerId: string,
    customerData: Partial<CustomerInput>,
    userId: string,
    companyId: string
  ): Promise<any> {
    try {
      // Check if customer exists
      const existingCustomer = await this.prisma.customer.findFirst({
        where: {
          id: customerId,
          companyId: companyId
        }
      });

      if (!existingCustomer) {
        throw new Error('Customer not found');
      }

      // Validate GSTIN if provided and changed
      if (customerData.gstin && customerData.gstin !== existingCustomer.gstin) {
        if (!CustomerService.validateGSTIN(customerData.gstin)) {
          throw new Error('Invalid GSTIN format. Expected format: 22AAAAA0000A1Z5');
        }

        // Check for duplicate GSTIN
        const existingGSTIN = await this.prisma.customer.findFirst({
          where: {
            gstin: customerData.gstin,
            companyId: companyId,
            id: { not: customerId }
          }
        });

        if (existingGSTIN) {
          throw new Error(`Customer with GSTIN '${customerData.gstin}' already exists`);
        }
      }

      // Validate PAN if provided and changed
      if (customerData.pan && customerData.pan !== existingCustomer.pan) {
        if (!CustomerService.validatePAN(customerData.pan)) {
          throw new Error('Invalid PAN format. Expected format: AAAAA0000A');
        }

        // Check for duplicate PAN
        const existingPAN = await this.prisma.customer.findFirst({
          where: {
            pan: customerData.pan,
            companyId: companyId,
            id: { not: customerId }
          }
        });

        if (existingPAN) {
          throw new Error(`Customer with PAN '${customerData.pan}' already exists`);
        }
      }

      // Check for duplicate customer code if changed
      if (customerData.customerCode && customerData.customerCode !== existingCustomer.customerCode) {
        const existingCode = await this.prisma.customer.findFirst({
          where: {
            customerCode: customerData.customerCode,
            companyId: companyId,
            id: { not: customerId }
          }
        });

        if (existingCode) {
          throw new Error(`Customer code '${customerData.customerCode}' already exists`);
        }
      }

      // Update customer
      const oldValues = { ...existingCustomer };
      const updatedCustomer = await this.prisma.customer.update({
        where: { id: customerId },
        data: {
          ...customerData,
          updatedBy: userId,
          updatedAt: new Date()
        },
        include: {
          customerDues: true
        }
      });

      // Log audit entry
      await this.auditLogger.log(
        'UPDATE',
        'PARTY',
        'CUSTOMER',
        customerId,
        userId,
        companyId,
        oldValues,
        updatedCustomer
      );

      return updatedCustomer;
    } catch (error) {
      throw new Error(`Failed to update customer: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Delete customer (soft delete)
   * @param customerId Customer ID
   * @param userId User ID deleting the customer
   * @param companyId Company ID
   */
  public async deleteCustomer(customerId: string, userId: string, companyId: string): Promise<void> {
    try {
      // Check if customer exists
      const existingCustomer = await this.prisma.customer.findFirst({
        where: {
          id: customerId,
          companyId: companyId
        }
      });

      if (!existingCustomer) {
        throw new Error('Customer not found');
      }

      // Check if customer has any transactions (dues > 0)
      const customerDues = await this.prisma.customerDue.findFirst({
        where: {
          customerId: customerId,
          companyId: companyId
        }
      });

      if (customerDues && (customerDues.totalSales > 0 || customerDues.totalPayments > 0)) {
        throw new Error('Cannot delete customer with existing transactions. Mark as inactive instead.');
      }

      // Soft delete by setting isActive to false
      const oldValues = { ...existingCustomer };
      await this.prisma.customer.update({
        where: { id: customerId },
        data: {
          isActive: false,
          updatedBy: userId,
          updatedAt: new Date()
        }
      });

      // Log audit entry
      await this.auditLogger.log(
        'DELETE',
        'PARTY',
        'CUSTOMER',
        customerId,
        userId,
        companyId,
        oldValues,
        { isActive: false }
      );
    } catch (error) {
      throw new Error(`Failed to delete customer: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * List customers with pagination
   * @param companyId Company ID
   * @param filters Filter criteria
   * @param page Page number
   * @param limit Results per page
   * @returns List of customers with pagination
   */
  public async listCustomers(
    companyId: string,
    filters: {
      isActive?: boolean;
      gstin?: string;
      search?: string;
    },
    page: number = 1,
    limit: number = 20
  ): Promise<{ customers: any[]; total: number; page: number; limit: number }> {
    try {
      const skip = (page - 1) * limit;

      const whereConditions: any = {
        companyId: companyId
      };

      if (filters.isActive !== undefined) {
        whereConditions.isActive = filters.isActive;
      }

      if (filters.gstin) {
        whereConditions.gstin = filters.gstin;
      }

      if (filters.search) {
        whereConditions.OR = [
          { companyName: { contains: filters.search, mode: 'insensitive' } },
          { customerCode: { contains: filters.search, mode: 'insensitive' } },
          { gstin: { contains: filters.search, mode: 'insensitive' } },
          { phone: { contains: filters.search, mode: 'insensitive' } },
          { mobile: { contains: filters.search, mode: 'insensitive' } },
          { email: { contains: filters.search, mode: 'insensitive' } }
        ];
      }

      const [customers, total] = await Promise.all([
        this.prisma.customer.findMany({
          where: whereConditions,
          include: {
            customerDues: true
          },
          orderBy: { createdAt: 'desc' },
          skip,
          take: limit
        }),
        this.prisma.customer.count({ where: whereConditions })
      ]);

      return {
        customers,
        total,
        page,
        limit
      };
    } catch (error) {
      throw new Error(`Failed to list customers: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Search customers by GSTIN
   * @param gstin GSTIN to search
   * @param companyId Company ID
   * @returns Matching customer
   */
  public async searchCustomerByGSTIN(gstin: string, companyId: string): Promise<any> {
    try {
      if (!CustomerService.validateGSTIN(gstin)) {
        throw new Error('Invalid GSTIN format');
      }

      const customer = await this.prisma.customer.findFirst({
        where: {
          gstin: gstin.toUpperCase(),
          companyId: companyId,
          isActive: true
        },
        include: {
          customerDues: true
        }
      });

      return customer;
    } catch (error) {
      throw new Error(`Failed to search customer by GSTIN: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Update customer due information
   * @param customerId Customer ID
   * @param updates Due amount updates
   * @param companyId Company ID
   * @param transaction Prisma transaction
   */
  public async updateCustomerDue(
    customerId: string,
    updates: {
      salesAmount?: number;
      paymentAmount?: number;
    },
    companyId: string,
    transaction?: any
  ): Promise<void> {
    try {
      const customerDue = await this.prisma.customerDue.findFirst({
        where: {
          customerId: customerId,
          companyId: companyId
        }
      });

      if (!customerDue) {
        throw new Error('Customer due record not found');
      }

      const updateData: any = {
        lastUpdated: new Date()
      };

      if (updates.salesAmount !== undefined) {
        updateData.totalSales = customerDue.totalSales + updates.salesAmount;
      }

      if (updates.paymentAmount !== undefined) {
        updateData.totalPayments = customerDue.totalPayments + updates.paymentAmount;
      }

      if (transaction) {
        await transaction.customerDue.update({
          where: { id: customerDue.id },
          data: updateData
        });
      } else {
        await this.prisma.customerDue.update({
          where: { id: customerDue.id },
          data: updateData
        });
      }
    } catch (error) {
      throw new Error(`Failed to update customer due: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }
}

/**
 * Vendor Service for Vendor Management
 * Handles CRUD operations for vendors with GSTIN validation
 */
export class VendorService {
  private prisma: PrismaClient;
  private auditLogger: AuditLogger;

  constructor() {
    this.prisma = new PrismaClient();
    this.auditLogger = new AuditLogger();
  }

  /**
   * Validate GSTIN format
   * @param gstin GSTIN number to validate
   * @returns boolean indicating if GSTIN is valid
   */
  public static validateGSTIN(gstin: string): boolean {
    if (!gstin) return true; // GSTIN is optional
    
    // GSTIN format: 2 digits (state code) + 5 chars (PAN) + 4 digits + 1 char + 1 digit + 1 char (checksum)
    const gstinRegex = /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[0-9A-Z]{3}$/;
    return gstinRegex.test(gstin.toUpperCase());
  }

  /**
   * Validate PAN format
   * @param pan PAN number to validate
   * @returns boolean indicating if PAN is valid
   */
  public static validatePAN(pan: string): boolean {
    if (!pan) return true; // PAN is optional
    
    // PAN format: 5 uppercase letters + 4 digits + 1 uppercase letter
    const panRegex = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;
    return panRegex.test(pan.toUpperCase());
  }

  /**
   * Create a new vendor
   * @param vendorData Vendor input data
   * @param userId User ID creating the vendor
   * @param companyId Company ID
   * @returns Created vendor
   */
  public async createVendor(
    vendorData: VendorInput,
    userId: string,
    companyId: string
  ): Promise<any> {
    try {
      // Validate GSTIN if provided
      if (vendorData.gstin && !VendorService.validateGSTIN(vendorData.gstin)) {
        throw new Error('Invalid GSTIN format. Expected format: 22AAAAA0000A1Z5');
      }

      // Validate PAN if provided
      if (vendorData.pan && !VendorService.validatePAN(vendorData.pan)) {
        throw new Error('Invalid PAN format. Expected format: AAAAA0000A');
      }

      // Check for duplicate vendor code
      const existingCode = await this.prisma.vendor.findFirst({
        where: {
          vendorCode: vendorData.vendorCode,
          companyId: companyId
        }
      });

      if (existingCode) {
        throw new Error(`Vendor code '${vendorData.vendorCode}' already exists`);
      }

      // Check for duplicate GSTIN if provided
      if (vendorData.gstin) {
        const existingGSTIN = await this.prisma.vendor.findFirst({
          where: {
            gstin: vendorData.gstin,
            companyId: companyId
          }
        });

        if (existingGSTIN) {
          throw new Error(`Vendor with GSTIN '${vendorData.gstin}' already exists`);
        }
      }

      // Check for duplicate PAN if provided
      if (vendorData.pan) {
        const existingPAN = await this.prisma.vendor.findFirst({
          where: {
            pan: vendorData.pan,
            companyId: companyId
          }
        });

        if (existingPAN) {
          throw new Error(`Vendor with PAN '${vendorData.pan}' already exists`);
        }
      }

      // Create vendor
      const vendor = await this.prisma.vendor.create({
        data: {
          ...vendorData,
          companyId: companyId,
          createdBy: userId,
          updatedBy: userId
        },
        include: {
          vendorPayables: true
        }
      });

      // Log audit entry
      await this.auditLogger.log(
        'CREATE',
        'PARTY',
        'VENDOR',
        vendor.id,
        userId,
        companyId,
        undefined,
        vendor
      );

      return vendor;
    } catch (error) {
      throw new Error(`Failed to create vendor: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get vendor by ID
   * @param vendorId Vendor ID
   * @param companyId Company ID
   * @returns Vendor details
   */
  public async getVendorById(vendorId: string, companyId: string): Promise<any> {
    try {
      const vendor = await this.prisma.vendor.findFirst({
        where: {
          id: vendorId,
          companyId: companyId
        },
        include: {
          vendorPayables: true
        }
      });

      if (!vendor) {
        throw new Error('Vendor not found');
      }

      return vendor;
    } catch (error) {
      throw new Error(`Failed to get vendor: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Update vendor
   * @param vendorId Vendor ID
   * @param vendorData Updated vendor data
   * @param userId User ID updating the vendor
   * @param companyId Company ID
   * @returns Updated vendor
   */
  public async updateVendor(
    vendorId: string,
    vendorData: Partial<VendorInput>,
    userId: string,
    companyId: string
  ): Promise<any> {
    try {
      // Check if vendor exists
      const existingVendor = await this.prisma.vendor.findFirst({
        where: {
          id: vendorId,
          companyId: companyId
        }
      });

      if (!existingVendor) {
        throw new Error('Vendor not found');
      }

      // Validate GSTIN if provided and changed
      if (vendorData.gstin && vendorData.gstin !== existingVendor.gstin) {
        if (!VendorService.validateGSTIN(vendorData.gstin)) {
          throw new Error('Invalid GSTIN format. Expected format: 22AAAAA0000A1Z5');
        }

        // Check for duplicate GSTIN
        const existingGSTIN = await this.prisma.vendor.findFirst({
          where: {
            gstin: vendorData.gstin,
            companyId: companyId,
            id: { not: vendorId }
          }
        });

        if (existingGSTIN) {
          throw new Error(`Vendor with GSTIN '${vendorData.gstin}' already exists`);
        }
      }

      // Validate PAN if provided and changed
      if (vendorData.pan && vendorData.pan !== existingVendor.pan) {
        if (!VendorService.validatePAN(vendorData.pan)) {
          throw new Error('Invalid PAN format. Expected format: AAAAA0000A');
        }

        // Check for duplicate PAN
        const existingPAN = await this.prisma.vendor.findFirst({
          where: {
            pan: vendorData.pan,
            companyId: companyId,
            id: { not: vendorId }
          }
        });

        if (existingPAN) {
          throw new Error(`Vendor with PAN '${vendorData.pan}' already exists`);
        }
      }

      // Check for duplicate vendor code if changed
      if (vendorData.vendorCode && vendorData.vendorCode !== existingVendor.vendorCode) {
        const existingCode = await this.prisma.vendor.findFirst({
          where: {
            vendorCode: vendorData.vendorCode,
            companyId: companyId,
            id: { not: vendorId }
          }
        });

        if (existingCode) {
          throw new Error(`Vendor code '${vendorData.vendorCode}' already exists`);
        }
      }

      // Update vendor
      const oldValues = { ...existingVendor };
      const updatedVendor = await this.prisma.vendor.update({
        where: { id: vendorId },
        data: {
          ...vendorData,
          updatedBy: userId,
          updatedAt: new Date()
        },
        include: {
          vendorPayables: true
        }
      });

      // Log audit entry
      await this.auditLogger.log(
        'UPDATE',
        'PARTY',
        'VENDOR',
        vendorId,
        userId,
        companyId,
        oldValues,
        updatedVendor
      );

      return updatedVendor;
    } catch (error) {
      throw new Error(`Failed to update vendor: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Delete vendor (soft delete)
   * @param vendorId Vendor ID
   * @param userId User ID deleting the vendor
   * @param companyId Company ID
   */
  public async deleteVendor(vendorId: string, userId: string, companyId: string): Promise<void> {
    try {
      // Check if vendor exists
      const existingVendor = await this.prisma.vendor.findFirst({
        where: {
          id: vendorId,
          companyId: companyId
        }
      });

      if (!existingVendor) {
        throw new Error('Vendor not found');
      }

      // Check if vendor has any transactions (payables > 0)
      const vendorPayables = await this.prisma.vendorPayable.findFirst({
        where: {
          vendorId: vendorId,
          companyId: companyId
        }
      });

      if (vendorPayables && (vendorPayables.totalPurchases > 0 || vendorPayables.totalPayments > 0)) {
        throw new Error('Cannot delete vendor with existing transactions. Mark as inactive instead.');
      }

      // Soft delete by setting isActive to false
      const oldValues = { ...existingVendor };
      await this.prisma.vendor.update({
        where: { id: vendorId },
        data: {
          isActive: false,
          updatedBy: userId,
          updatedAt: new Date()
        }
      });

      // Log audit entry
      await this.auditLogger.log(
        'DELETE',
        'PARTY',
        'VENDOR',
        vendorId,
        userId,
        companyId,
        oldValues,
        { isActive: false }
      );
    } catch (error) {
      throw new Error(`Failed to delete vendor: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * List vendors with pagination
   * @param companyId Company ID
   * @param filters Filter criteria
   * @param page Page number
   * @param limit Results per page
   * @returns List of vendors with pagination
   */
  public async listVendors(
    companyId: string,
    filters: {
      isActive?: boolean;
      gstin?: string;
      search?: string;
    },
    page: number = 1,
    limit: number = 20
  ): Promise<{ vendors: any[]; total: number; page: number; limit: number }> {
    try {
      const skip = (page - 1) * limit;

      const whereConditions: any = {
        companyId: companyId
      };

      if (filters.isActive !== undefined) {
        whereConditions.isActive = filters.isActive;
      }

      if (filters.gstin) {
        whereConditions.gstin = filters.gstin;
      }

      if (filters.search) {
        whereConditions.OR = [
          { companyName: { contains: filters.search, mode: 'insensitive' } },
          { vendorCode: { contains: filters.search, mode: 'insensitive' } },
          { gstin: { contains: filters.search, mode: 'insensitive' } },
          { phone: { contains: filters.search, mode: 'insensitive' } },
          { mobile: { contains: filters.search, mode: 'insensitive' } },
          { email: { contains: filters.search, mode: 'insensitive' } }
        ];
      }

      const [vendors, total] = await Promise.all([
        this.prisma.vendor.findMany({
          where: whereConditions,
          include: {
            vendorPayables: true
          },
          orderBy: { createdAt: 'desc' },
          skip,
          take: limit
        }),
        this.prisma.vendor.count({ where: whereConditions })
      ]);

      return {
        vendors,
        total,
        page,
        limit
      };
    } catch (error) {
      throw new Error(`Failed to list vendors: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Search vendors by GSTIN
   * @param gstin GSTIN to search
   * @param companyId Company ID
   * @returns Matching vendor
   */
  public async searchVendorByGSTIN(gstin: string, companyId: string): Promise<any> {
    try {
      if (!VendorService.validateGSTIN(gstin)) {
        throw new Error('Invalid GSTIN format');
      }

      const vendor = await this.prisma.vendor.findFirst({
        where: {
          gstin: gstin.toUpperCase(),
          companyId: companyId,
          isActive: true
        },
        include: {
          vendorPayables: true
        }
      });

      return vendor;
    } catch (error) {
      throw new Error(`Failed to search vendor by GSTIN: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Update vendor payable information
   * @param vendorId Vendor ID
   * @param updates Payable amount updates
   * @param companyId Company ID
   * @param transaction Prisma transaction
   */
  public async updateVendorPayable(
    vendorId: string,
    updates: {
      purchaseAmount?: number;
      paymentAmount?: number;
    },
    companyId: string,
    transaction?: any
  ): Promise<void> {
    try {
      const vendorPayable = await this.prisma.vendorPayable.findFirst({
        where: {
          vendorId: vendorId,
          companyId: companyId
        }
      });

      if (!vendorPayable) {
        throw new Error('Vendor payable record not found');
      }

      const updateData: any = {
        lastUpdated: new Date()
      };

      if (updates.purchaseAmount !== undefined) {
        updateData.totalPurchases = vendorPayable.totalPurchases + updates.purchaseAmount;
      }

      if (updates.paymentAmount !== undefined) {
        updateData.totalPayments = vendorPayable.totalPayments + updates.paymentAmount;
      }

      if (transaction) {
        await transaction.vendorPayable.update({
          where: { id: vendorPayable.id },
          data: updateData
        });
      } else {
        await this.prisma.vendorPayable.update({
          where: { id: vendorPayable.id },
          data: updateData
        });
      }
    } catch (error) {
      throw new Error(`Failed to update vendor payable: ${error instanceof Error ? error.message : 'Unknown error'}`);
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