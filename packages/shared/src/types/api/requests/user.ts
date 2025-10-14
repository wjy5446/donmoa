/**
 * User Preferences API Request Types
 */

import { CategoryKind, DashboardCard, DashboardLayout } from "../../domain/user";

/**
 * 카테고리 생성 요청
 */
export interface CategoryCreateRequest {
  name: string;
  parent_id?: number;
  kind?: CategoryKind;
}

/**
 * 카테고리 수정 요청
 */
export interface CategoryUpdateRequest {
  name?: string;
  parent_id?: number;
}

/**
 * 즐겨찾기 토글 요청
 */
export interface FavoriteToggleRequest {
  instrument_id: number;
  star: boolean; // true: 등록, false: 해제
}

/**
 * 즐겨찾기 목록 조회 쿼리
 */
export interface FavoritesQuery {
  held?: boolean; // 현재 보유 종목만
  asset_class?: string;
}

/**
 * 대시보드 설정 저장 요청
 */
export interface DashboardPrefsUpdateRequest {
  cards?: DashboardCard[];
  layout?: DashboardLayout;
  custom_layout?: {
    positions: Record<DashboardCard, { x: number; y: number; w: number; h: number }>;
  };
}
