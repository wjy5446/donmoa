/**
 * Analytics Domain Types
 * 대시보드 및 분석 관련 타입 정의
 */

import { Money } from "../common/money";

/**
 * 대시보드 요약
 */
export interface DashboardSummary {
  as_of: string; // ISO date
  total_equity: Money;
  by_account: Array<{
    account_id: number;
    account_name?: string;
    weight: number; // 비중 (0~1)
    equity_minor: bigint;
  }>;
  by_asset_class: Array<{
    asset_class: string;
    weight: number;
    equity_minor: bigint;
  }>;
  monthly_return?: {
    m1?: number; // 1개월 수익률
    ytd?: number; // 연초 대비 수익률
  };
  notes?: string[];
}

/**
 * 시계열 메트릭 타입
 */
export type TimeseriesMetric = "total_equity" | "return" | "dividend" | "cashflow";

/**
 * 시계열 간격
 */
export type TimeseriesInterval = "day" | "week" | "month";

/**
 * 시계열 데이터 포인트
 */
export interface TimeseriesPoint {
  date: string; // ISO date
  value: number;
}

/**
 * 시계열 응답
 */
export interface TimeseriesResponse {
  metric: TimeseriesMetric;
  interval: TimeseriesInterval;
  series: TimeseriesPoint[];
}

/**
 * 비중 그룹 타입
 */
export type AllocationGroup = "account" | "asset_class" | "subclass";

/**
 * 비중 아이템
 */
export interface AllocationItem {
  key: string; // account_id, asset_class, subclass 등
  label?: string; // 표시명
  weight: number; // 비중 (0~1)
  equity_minor: bigint;
}

/**
 * 비중 응답
 */
export interface AllocationsResponse {
  date: string; // ISO date
  group: AllocationGroup;
  items: AllocationItem[];
}

/**
 * 현금흐름 요약 (월별)
 */
export interface CashflowSummary {
  period: {
    from: string; // ISO date
    to: string; // ISO date
  };
  monthly: Array<{
    month: string; // "2025-09"
    income_minor: bigint;
    expense_minor: bigint;
    transfer_minor: bigint;
    net_minor: bigint;
  }>;
}

/**
 * 배당 요약
 */
export interface DividendSummary {
  period: {
    from: string;
    to: string;
  };
  total_minor: bigint;
  currency: string;
  by_instrument: Array<{
    instrument_id: number;
    instrument_name?: string;
    amount_minor: bigint;
    count: number; // 배당 횟수
  }>;
}
