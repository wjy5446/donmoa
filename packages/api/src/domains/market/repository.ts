/**
 * Market Data Repository
 * DB 접근 레이어
 */

import { SupabaseClient } from "@supabase/supabase-js";

export class MarketRepository {
  constructor(private db: SupabaseClient) {}

  /**
   * 종목 검색
   */
  async searchInstruments(query: string, assetClass?: string, limit = 30) {
    let dbQuery = this.db
      .from("instruments")
      .select("id, symbol, name, asset_class, currency")
      .or(`symbol.ilike.%${query}%,name.ilike.%${query}%`)
      .limit(limit);

    if (assetClass) {
      dbQuery = dbQuery.eq("asset_class", assetClass);
    }

    const { data, error } = await dbQuery;

    if (error) throw error;
    return data || [];
  }

  /**
   * 종목 상세 조회
   */
  async getInstrumentById(instrumentId: number) {
    const { data, error } = await this.db
      .from("instruments")
      .select("*")
      .eq("id", instrumentId)
      .single();

    if (error && error.code !== "PGRST116") throw error;
    return data;
  }

  /**
   * 일별 가격 조회
   */
  async getDailyPrices(instrumentId: number, from?: string, to?: string) {
    let query = this.db
      .from("prices_daily")
      .select("*")
      .eq("instrument_id", instrumentId)
      .order("price_date", { ascending: false });

    if (from) {
      query = query.gte("price_date", from);
    }
    if (to) {
      query = query.lte("price_date", to);
    }

    const { data, error } = await query;

    if (error) throw error;
    return data || [];
  }

  /**
   * 환율 조회
   */
  async getDailyFx(base: string, quote: string, from?: string, to?: string) {
    let query = this.db
      .from("fx_rates_daily")
      .select("*")
      .eq("base_currency", base)
      .eq("quote_currency", quote)
      .order("rate_date", { ascending: false });

    if (from) {
      query = query.gte("rate_date", from);
    }
    if (to) {
      query = query.lte("rate_date", to);
    }

    const { data, error } = await query;

    if (error) throw error;
    return data || [];
  }
}

