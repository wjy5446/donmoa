/**
 * Analytics Repository
 * DB 접근 레이어
 */

import { SupabaseClient } from "@supabase/supabase-js";

export class AnalyticsRepository {
  constructor(private db: SupabaseClient) {}

  /**
   * 특정 날짜의 스냅샷 ID 조회
   */
  async getSnapshotIdByDate(userId: string, date: string): Promise<number | null> {
    const { data, error } = await this.db
      .from("snapshots")
      .select("id")
      .eq("user_id", userId)
      .eq("snapshot_date", date)
      .eq("status", "completed")
      .single();

    if (error && error.code !== "PGRST116") throw error;
    return data?.id || null;
  }

  /**
   * 최신 스냅샷 ID 조회
   */
  async getLatestSnapshotId(userId: string): Promise<number | null> {
    const { data, error } = await this.db
      .from("snapshots")
      .select("id, snapshot_date")
      .eq("user_id", userId)
      .eq("status", "completed")
      .order("snapshot_date", { ascending: false })
      .order("created_at", { ascending: false })
      .limit(1)
      .single();

    if (error && error.code !== "PGRST116") throw error;
    return data?.id || null;
  }

  /**
   * 계좌별 현금+포지션 집계
   */
  async getAccountSummary(snapshotId: number) {
    // 현금 집계
    const { data: cashData, error: cashError } = await this.db
      .from("snapshot_cash")
      .select("account_id, amount_minor, currency")
      .eq("snapshot_id", snapshotId);

    if (cashError) throw cashError;

    // 포지션 집계 (평가액은 시세 데이터 필요, 현재는 수량만)
    const { data: positionsData, error: positionsError } = await this.db
      .from("snapshot_positions")
      .select("account_id, qty_nano, instrument_id, instruments(symbol, currency)")
      .eq("snapshot_id", snapshotId);

    if (positionsError) throw positionsError;

    return { cash: cashData || [], positions: positionsData || [] };
  }

  /**
   * 자산 클래스별 포지션 집계
   */
  async getAssetClassSummary(snapshotId: number) {
    const { data, error } = await this.db
      .from("snapshot_positions")
      .select("qty_nano, instruments(asset_class, subclass, currency)")
      .eq("snapshot_id", snapshotId);

    if (error) throw error;
    return data || [];
  }

  /**
   * 시계열 데이터 (스냅샷 목록)
   */
  async getSnapshotsTimeseries(
    userId: string,
    from?: string,
    to?: string
  ) {
    let query = this.db
      .from("snapshots")
      .select("id, snapshot_date")
      .eq("user_id", userId)
      .eq("status", "completed")
      .order("snapshot_date", { ascending: true });

    if (from) {
      query = query.gte("snapshot_date", from);
    }
    if (to) {
      query = query.lte("snapshot_date", to);
    }

    const { data, error } = await query;

    if (error) throw error;
    return data || [];
  }

  /**
   * 현금흐름 거래 조회
   */
  async getCashflowTransactions(
    userId: string,
    from: string,
    to: string
  ) {
    const { data, error } = await this.db
      .from("snapshot_transactions")
      .select("type, amount_minor, currency, trade_datetime, snapshots!inner(user_id)")
      .eq("snapshots.user_id", userId)
      .gte("trade_datetime", from)
      .lte("trade_datetime", to)
      .in("type", ["deposit", "withdraw", "transfer", "dividend", "interest"]);

    if (error) throw error;
    return data || [];
  }

  /**
   * 배당 내역 조회
   */
  async getDividends(
    userId: string,
    from: string,
    to: string
  ) {
    const { data, error } = await this.db
      .from("snapshot_transactions")
      .select(`
        instrument_id,
        amount_minor,
        currency,
        trade_datetime,
        instruments(symbol, name),
        snapshots!inner(user_id)
      `)
      .eq("snapshots.user_id", userId)
      .eq("type", "dividend")
      .gte("trade_datetime", from)
      .lte("trade_datetime", to)
      .order("trade_datetime", { ascending: false });

    if (error) throw error;
    return data || [];
  }
}
