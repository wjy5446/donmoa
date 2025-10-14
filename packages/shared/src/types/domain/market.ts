/**
 * Market Data Domain Types
 * 시장 데이터 (종목, 시세, 환율) 타입 정의
 */

/**
 * 자산 클래스
 */
export type AssetClass =
  | "equity" // 주식
  | "bond" // 채권
  | "fund" // 펀드/ETF
  | "crypto" // 암호화폐
  | "commodity" // 원자재
  | "fx" // 외환
  | "cash" // 현금
  | "other";

/**
 * 종목/자산
 */
export interface Instrument {
  id: number;
  symbol: string;
  isin?: string;
  name: string;
  asset_class: AssetClass;
  subclass?: string; // 세부 분류 (예: "tech", "healthcare")
  currency: string;
  metadata?: Record<string, unknown>;
  valid_from?: string;
  valid_to?: string;
  created_at: string;
  updated_at?: string;
}

/**
 * 일별 가격 (OHLCV)
 */
export interface DailyPrice {
  instrument_id: number;
  price_date: string; // ISO date
  open?: number;
  high?: number;
  low?: number;
  close: number;
  volume?: number;
  dividend?: number; // 배당금
  split?: string; // 액면분할 정보
  source_id: number;
  created_at: string;
}

/**
 * 환율 (일별)
 */
export interface FxRate {
  base_currency: string; // 3자 코드
  quote_currency: string; // 3자 코드
  rate_date: string; // ISO date
  rate: number; // 1 quote = rate base
  source_id: number;
  created_at: string;
}

/**
 * 데이터 소스
 */
export type DataSourceKind = "price" | "fx" | "transaction";

export interface DataSource {
  id: number;
  name: string;
  kind: DataSourceKind;
  meta?: Record<string, unknown>;
  created_at: string;
}

/**
 * 종목 메트릭스 (모멘텀, 변동성 등)
 */
export interface InstrumentMetrics {
  instrument_id: number;
  momentum?: Record<string, number>; // { "1m": 0.05, "3m": 0.12, "12m": 0.25 }
  volatility?: number;
  holding_perf?: {
    avg_cost: number;
    pnl_minor: bigint;
    return_pct: number;
  };
}
