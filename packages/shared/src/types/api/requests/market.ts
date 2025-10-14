/**
 * Market Data API Request Types
 */

/**
 * 종목 검색 쿼리
 */
export interface InstrumentSearchQuery {
  query?: string; // 검색어 (symbol, name)
  asset_class?: string;
  limit?: number;
  cursor?: string;
}

/**
 * 일별 가격 조회 쿼리
 */
export interface DailyPricesQuery {
  instrument_id: number;
  from?: string; // ISO date
  to?: string; // ISO date
}

/**
 * 환율 조회 쿼리
 */
export interface DailyFxQuery {
  base: string; // 3자 통화 코드
  quote: string; // 3자 통화 코드
  from?: string; // ISO date
  to?: string; // ISO date
}

/**
 * 종목 메트릭스 조회 쿼리
 */
export interface InstrumentMetricsQuery {
  instrument_id: number;
  window?: string; // "1,3,6,12" (모멘텀 윈도우, 월 단위)
}
