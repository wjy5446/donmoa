/**
 * Snapshot API Response Types
 */

import { SnapshotSummary } from "../../domain/snapshot";
import { PaginatedResponse } from "../../common/pagination";

/**
 * 스냅샷 커밋 응답
 */
export interface SnapshotCommitResponse {
  snapshot_id: number;
  date: string; // ISO date
  lines: {
    cash: number;
    positions: number;
    transactions: number;
  };
  warnings?: string[];
  errors?: string[];
}

/**
 * 스냅샷 업로드 응답
 */
export interface SnapshotUploadResponse {
  snapshot_id: number;
  parsed_rows: {
    cash: number;
    positions: number;
    transactions: number;
  };
  warnings?: string[];
}

/**
 * 스냅샷 목록 응답
 */
export type SnapshotListResponse = PaginatedResponse<SnapshotSummary>;

/**
 * 스냅샷 상세 응답
 */
export interface SnapshotDetailResponse extends SnapshotSummary {
  // 추가 상세 정보 (필요 시)
}
