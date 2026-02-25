// Common types and interfaces for BizPulse24 ERP Backend

export interface ApiResponse<T = unknown> {
  data?: T;
  error?: {
    message: string;
    statusCode: number;
    timestamp: string;
    path?: string;
  };
  metadata?: {
    page?: number;
    limit?: number;
    total?: number;
  };
}

export enum UserRole {
  OWNER = 'OWNER',
  ADMIN = 'ADMIN',
  STAFF = 'STAFF',
}

export enum MovementType {
  IN = 'IN',
  OUT = 'OUT',
  TRANSFER = 'TRANSFER',
}

export enum PaymentMode {
  CASH = 'CASH',
  BANK_TRANSFER = 'BANK_TRANSFER',
  CHEQUE = 'CHEQUE',
  UPI = 'UPI',
  CARD = 'CARD',
}

export enum GSTRate {
  ZERO = 0,
  FIVE = 5,
  TWELVE = 12,
  EIGHTEEN = 18,
  TWENTY_EIGHT = 28,
}

export interface PaginationParams {
  page: number;
  limit: number;
}

export interface FilterParams {
  startDate?: Date;
  endDate?: Date;
  search?: string;
}
