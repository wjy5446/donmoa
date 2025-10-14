/**
 * Snapshot Domain Types
 * 스냅샷 및 스냅샷 라인 아이템 타입 정의
 */

import { Money } from "../common/money";

/**
 * 스냅샷 상태
 */
export type SnapshotStatus = "pending" | "processing" | "completed" | "failed";

/**
 * 스냅샷 소스
 */
export type SnapshotSource = "cli" | "manual" | "banksalad" | "domino" | "web";

/**
 * 스냅샷 헤더
 */
export interface Snapshot {
  id: number;
  user_id: string;
  snapshot_date: string; // ISO date (YYYY-MM-DD)
  source: SnapshotSource;
  status: SnapshotStatus;
  notes?: string;
  created_at: string; // ISO datetime
  updated_at?: string;
}

/**
 * 스냅샷 현금 라인
 */
export interface SnapshotCash {
  id?: number;
  snapshot_id: number;
  account_id: number;
  currency: string;
  amount_minor: bigint;
  created_at?: string;
}

/**
 * 스냅샷 포지션 라인
 */
export interface SnapshotPosition {
  id?: number;
  snapshot_id: number;
  account_id: number;
  instrument_id: number;
  qty_nano: bigint;
  avg_cost?: number; // 또는 avg_cost_minor: bigint
  currency: string;
  tags?: Record<string, unknown>;
  created_at?: string;
}

/**
 * 거래 타입
 */
export type TransactionType =
  | "buy"
  | "sell"
  | "dividend"
  | "fee"
  | "transfer"
  | "deposit"
  | "withdraw"
  | "interest"
  | "other";

/**
 * 스냅샷 거래 라인
 */
export interface SnapshotTransaction {
  id?: number;
  snapshot_id: number;
  account_id: number;
  txn_id?: string; // 외부 거래 ID
  trade_datetime: string; // ISO datetime
  settle_date?: string; // ISO date
  type: TransactionType;
  instrument_id?: number;
  qty_nano?: bigint;
  price_nano?: bigint;
  amount_minor?: bigint;
  currency: string;
  category_id?: number;
  note?: string;
  raw?: Record<string, unknown>;
  created_at?: string;
}

/**
 * 인제스트 로그
 */
export type IngestLogLevel = "info" | "warning" | "error";

export interface IngestLog {
  id: number;
  snapshot_id: number;
  level: IngestLogLevel;
  message: string;
  context?: Record<string, unknown>;
  created_at: string;
}

/**
 * 스냅샷 요약
 */
export interface SnapshotSummary {
  id: number;
  date: string;
  source: SnapshotSource;
  notes?: string;
  line_counts: {
    cash: number;
    positions: number;
    transactions: number;
  };
  totals_by_currency?: Array<Money & { role: "cash" | "equity_value" }>;
}
