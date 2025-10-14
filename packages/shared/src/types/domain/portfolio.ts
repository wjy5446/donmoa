/**
 * Portfolio Domain Types
 * 포트폴리오 (계좌, 기관, 포지션) 타입 정의
 */

/**
 * 사용자
 */
export interface User {
  id: string; // UUID
  email: string;
  display_name?: string;
  settings?: {
    base_currency?: string;
    timezone?: string;
    locale?: string;
  };
  created_at: string;
  updated_at?: string;
}

/**
 * 기관 타입
 */
export type InstitutionKind = "securities" | "bank" | "crypto" | "pension" | "other";

/**
 * 기관 (증권사, 은행 등)
 */
export interface Institution {
  id: number;
  user_id: string;
  name: string;
  kind: InstitutionKind;
  meta?: Record<string, unknown>;
  created_at: string;
  updated_at?: string;
}

/**
 * 계좌 타입
 */
export type AccountType = "investment" | "savings" | "checking" | "pension" | "crypto" | "other";

/**
 * 계좌
 */
export interface Account {
  id: number;
  user_id: string;
  institution_id: number;
  name: string;
  type: AccountType;
  currency: string; // 기본 통화
  meta?: Record<string, unknown>;
  valid_from?: string; // ISO date
  valid_to?: string; // ISO date
  created_at: string;
  updated_at?: string;
}

/**
 * 계좌 잔액 (특정 시점)
 */
export interface AccountBalance {
  account_id: number;
  snapshot_date: string;
  cash: Array<{
    currency: string;
    amount_minor: bigint;
  }>;
  equity_value?: bigint; // 평가 금액
  total_value?: bigint;
}

/**
 * 포지션 (보유 종목)
 */
export interface Position {
  account_id: number;
  instrument_id: number;
  snapshot_date: string;
  qty_nano: bigint;
  avg_cost?: number;
  current_price?: number;
  market_value_minor?: bigint;
  unrealized_pnl_minor?: bigint;
  currency: string;
}
