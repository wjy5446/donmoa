/**
 * Dashboard API Request Types
 */

import { TimeseriesMetric, TimeseriesInterval, AllocationGroup } from "../../domain/analytics";

/**
 * 대시보드 요약 조회 쿼리
 */
export interface DashboardSummaryQuery {
  date: string; // ISO date (필수)
}

/**
 * 시계열 데이터 조회 쿼리
 */
export interface TimeseriesQuery {
  metric: TimeseriesMetric;
  interval?: TimeseriesInterval; // 기본값: month
  from?: string; // ISO date
  to?: string; // ISO date
}

/**
 * 비중 데이터 조회 쿼리
 */
export interface AllocationsQuery {
  date: string; // ISO date (필수)
  group: AllocationGroup;
}

/**
 * 현금흐름 조회 쿼리
 */
export interface CashflowQuery {
  from: string; // ISO date (필수)
  to: string; // ISO date (필수)
}
