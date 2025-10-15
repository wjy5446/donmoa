/**
 * Portfolio Repository
 * DB 접근 레이어
 */

import { SupabaseClient } from "@supabase/supabase-js";

export class PortfolioRepository {
  constructor(private db: SupabaseClient) {}

  /**
   * 계좌 목록 조회
   */
  async listAccounts(userId: string) {
    const { data, error } = await this.db
      .from("accounts")
      .select("*, institution:institutions(name, kind)")
      .eq("user_id", userId)
      .order("created_at", { ascending: false });

    if (error) throw error;
    return data || [];
  }

  /**
   * 계좌 상세 조회
   */
  async getAccountById(accountId: number) {
    const { data, error } = await this.db
      .from("accounts")
      .select("*, institution:institutions(name, kind)")
      .eq("id", accountId)
      .single();

    if (error && error.code !== "PGRST116") throw error;
    return data;
  }

  /**
   * 최신 스냅샷의 계좌별 현금 잔액 조회
   */
  async getAccountCashBalances(userId: string, snapshotDate?: string) {
    let query = this.db
      .from("v_account_cash_balances")
      .select("*")
      .eq("user_id", userId);

    if (snapshotDate) {
      query = query.eq("snapshot_date", snapshotDate);
    }

    const { data, error } = await query;

    if (error) throw error;
    return data || [];
  }

  /**
   * 최신 스냅샷의 계좌별 포지션 조회
   */
  async getAccountPositions(userId: string, snapshotDate?: string) {
    let query = this.db
      .from("v_account_positions")
      .select("*")
      .eq("user_id", userId);

    if (snapshotDate) {
      query = query.eq("snapshot_date", snapshotDate);
    }

    const { data, error } = await query;

    if (error) throw error;
    return data || [];
  }

  /**
   * 거래 라인 수정
   */
  async updateTransaction(
    transactionId: number,
    updates: {
      trade_datetime?: string;
      settle_date?: string;
      qty_nano?: string;
      price_nano?: string;
      amount_minor?: string;
      currency?: string;
      note?: string;
    }
  ) {
    const { error } = await this.db
      .from("snapshot_transactions")
      .update(updates)
      .eq("id", transactionId);

    if (error) throw error;
  }

  /**
   * 현금 라인 수정
   */
  async updateCash(
    cashId: number,
    updates: {
      amount_minor?: string;
      currency?: string;
    }
  ) {
    const { error } = await this.db
      .from("snapshot_cash")
      .update(updates)
      .eq("id", cashId);

    if (error) throw error;
  }

  /**
   * 포지션 라인 수정
   */
  async updatePosition(
    positionId: number,
    updates: {
      qty_nano?: string;
      avg_cost?: number;
      currency?: string;
    }
  ) {
    const { error } = await this.db
      .from("snapshot_positions")
      .update(updates)
      .eq("id", positionId);

    if (error) throw error;
  }

  /**
   * 배당 입력
   */
  async createDividend(data: {
    snapshot_id: number;
    account_id: number;
    instrument_id: number;
    trade_datetime: string;
    amount_minor: string;
    currency: string;
    note?: string;
  }) {
    const { error } = await this.db.from("snapshot_transactions").insert({
      ...data,
      type: "dividend",
      settle_date: data.trade_datetime.split("T")[0],
    });

    if (error) throw error;
  }
}
