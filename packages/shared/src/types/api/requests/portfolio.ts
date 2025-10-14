/**
 * Portfolio API Request Types
 */

/**
 * 거래 라인 수정 요청
 */
export interface EditTransactionRequest {
  trade_datetime?: string; // ISO datetime
  settle_date?: string; // ISO date
  qty?: number;
  price?: number;
  amount?: number;
  currency?: string;
  note?: string;
}

/**
 * 현금 라인 수정 요청
 */
export interface EditCashRequest {
  amount?: number;
  currency?: string;
}

/**
 * 포지션 라인 수정 요청
 */
export interface EditPositionRequest {
  qty?: number;
  avg_cost?: number;
  currency?: string;
}

/**
 * 배당 입력 요청
 */
export interface CreateDividendRequest {
  account_id: number;
  instrument_id: number;
  pay_date: string; // ISO date
  amount: number;
  currency: string;
  note?: string;
}
