/**
 * User Preferences Domain Types
 * 사용자 설정 (즐겨찾기, 카테고리, 대시보드 설정) 타입 정의
 */

/**
 * 카테고리 종류
 */
export type CategoryKind = "income" | "expense" | "transfer" | "investment" | "other";

/**
 * 카테고리
 */
export interface Category {
  id: number;
  user_id: string;
  name: string;
  parent_id?: number;
  kind: CategoryKind;
  meta?: Record<string, unknown>;
  created_at: string;
  updated_at?: string;
}

/**
 * 즐겨찾기
 */
export interface Favorite {
  user_id: string;
  instrument_id: number;
  instrument?: {
    symbol: string;
    name: string;
    asset_class: string;
  };
  starred_at: string;
  holding?: boolean; // 현재 보유 여부
  perf?: {
    pnl_minor: bigint;
    return_pct: number;
  };
}

/**
 * 대시보드 카드 타입
 */
export type DashboardCard =
  | "summary"
  | "timeseries"
  | "allocations"
  | "cashflow"
  | "dividends"
  | "recent_transactions"
  | "favorites"
  | "performance";

/**
 * 대시보드 레이아웃
 */
export type DashboardLayout = "grid-2" | "grid-3" | "list" | "custom";

/**
 * 대시보드 설정
 */
export interface DashboardPrefs {
  user_id?: string;
  cards: DashboardCard[];
  layout: DashboardLayout;
  custom_layout?: {
    positions: Record<DashboardCard, { x: number; y: number; w: number; h: number }>;
  };
  updated_at?: string;
}
