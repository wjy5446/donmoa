/**
 * Market Data Service
 * 비즈니스 로직 레이어
 */

import { SupabaseClient } from "@supabase/supabase-js";
import { MarketRepository } from "./repository";
import {
  InstrumentSearchQuery,
  DailyPricesQuery,
  DailyFxQuery,
  InstrumentMetricsQuery,
} from "./validator";

export class MarketService {
  private repository: MarketRepository;

  constructor(private db: SupabaseClient) {
    this.repository = new MarketRepository(db);
  }

  /**
   * 종목 검색
   */
  async searchInstruments(query: InstrumentSearchQuery) {
    const instruments = await this.repository.searchInstruments(
      query.query || "",
      query.asset_class,
      query.limit
    );

    return {
      items: instruments,
      next_cursor: null, // TODO: 페이지네이션
    };
  }

  /**
   * 종목 상세 조회
   */
  async getInstrumentById(instrumentId: number) {
    return await this.repository.getInstrumentById(instrumentId);
  }

  /**
   * 일별 가격 조회
   */
  async getDailyPrices(query: DailyPricesQuery) {
    const prices = await this.repository.getDailyPrices(
      query.instrument_id,
      query.from,
      query.to
    );

    return {
      instrument_id: query.instrument_id,
      items: prices.map((p: any) => ({
        date: p.price_date,
        open: p.open ? Number(p.open) : undefined,
        high: p.high ? Number(p.high) : undefined,
        low: p.low ? Number(p.low) : undefined,
        close: Number(p.close),
        volume: p.volume ? Number(p.volume) : undefined,
      })),
    };
  }

  /**
   * 환율 조회
   */
  async getDailyFx(query: DailyFxQuery) {
    const rates = await this.repository.getDailyFx(
      query.base,
      query.quote,
      query.from,
      query.to
    );

    return {
      base: query.base,
      quote: query.quote,
      items: rates.map((r: any) => ({
        date: r.rate_date,
        rate: Number(r.rate),
      })),
    };
  }

  /**
   * 종목 메트릭스 조회
   *
   * TODO: 실제 모멘텀/변동성 계산
   */
  async getInstrumentMetrics(query: InstrumentMetricsQuery) {
    const instrument = await this.repository.getInstrumentById(query.instrument_id);

    if (!instrument) {
      return null;
    }

    // 간단한 예시 데이터
    return {
      instrument_id: query.instrument_id,
      momentum: {
        "1m": 0.05,
        "3m": 0.12,
        "6m": 0.18,
        "12m": 0.25,
      },
      volatility: 0.15,
      holding_perf: {
        avg_cost: 0,
        pnl_minor: 0n,
        return_pct: 0,
      },
    };
  }
}
