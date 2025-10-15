/**
 * Snapshot API Request Types
 */

import { SnapshotSource } from "../../domain/snapshot";

/**
 * 스냅샷 커밋 요청
 */
export interface SnapshotCommitRequest {
  snapshot_date: string; // ISO date
  source: SnapshotSource;
  notes?: string;
  cash: Array<{
    account_external_id: string;
    currency: string;
    amount: number; // 실수 금액 (서버에서 정수화)
  }>;
  positions: Array<{
    account_external_id: string;
    symbol: string;
    currency: string;
    qty: number; // 실수 수량
    avg_cost?: number;
  }>;
  transactions: Array<{
    account_external_id: string;
    type: string;
    symbol?: string;
    trade_datetime?: string; // ISO datetime
    settle_date?: string; // ISO date
    qty?: number;
    price?: number;
    amount?: number;
    currency: string;
    note?: string;
  }>;
  mapping?: {
    account_map?: Record<string, number>; // external_id -> accounts.id
    instrument_map?: Record<string, number>; // symbol -> instruments.id
  };
  options?: {
    replace_same_date?: boolean; // 기본값: true
    create_missing_accounts?: boolean; // 기본값: true
    create_missing_instruments?: boolean; // 기본값: true
  };
}

/**
 * 스냅샷 업로드 요청 (multipart/form-data)
 */
export interface SnapshotUploadRequest {
  file: File | Blob;
  snapshot_date: string; // ISO date
  notes?: string;
}

/**
 * 스냅샷 목록 조회 쿼리
 */
export interface SnapshotListQuery {
  from?: string; // ISO date
  to?: string; // ISO date
  limit?: number;
  cursor?: string;
}
