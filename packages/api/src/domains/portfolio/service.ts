/**
 * Portfolio Service
 * 비즈니스 로직 레이어
 */

import { SupabaseClient } from "@supabase/supabase-js";
import { toMoneyMinor, toQtyNano, toPriceNano } from "@donmoa/shared";
import { PortfolioRepository } from "./repository";
import {
  EditTransactionInput,
  EditCashInput,
  EditPositionInput,
  CreateDividendInput,
} from "./validator";

export class PortfolioService {
  private repository: PortfolioRepository;

  constructor(private db: SupabaseClient) {
    this.repository = new PortfolioRepository(db);
  }

  /**
   * 계좌 목록 조회
   */
  async listAccounts(userId: string) {
    return await this.repository.listAccounts(userId);
  }

  /**
   * 계좌 상세 조회
   */
  async getAccountById(accountId: number, userId: string) {
    const account = await this.repository.getAccountById(accountId);

    if (!account || account.user_id !== userId) {
      return null;
    }

    return account;
  }

  /**
   * 계좌별 현금 잔액 조회
   */
  async getAccountCashBalances(userId: string, snapshotDate?: string) {
    return await this.repository.getAccountCashBalances(userId, snapshotDate);
  }

  /**
   * 계좌별 포지션 조회
   */
  async getAccountPositions(userId: string, snapshotDate?: string) {
    return await this.repository.getAccountPositions(userId, snapshotDate);
  }

  /**
   * 거래 라인 수정
   */
  async updateTransaction(transactionId: number, input: EditTransactionInput) {
    const updates: Record<string, unknown> = {};

    if (input.trade_datetime) {
      updates.trade_datetime = input.trade_datetime;
    }
    if (input.settle_date) {
      updates.settle_date = input.settle_date;
    }
    if (input.qty !== undefined) {
      updates.qty_nano = toQtyNano(input.qty).toString();
    }
    if (input.price !== undefined) {
      updates.price_nano = toPriceNano(input.price).toString();
    }
    if (input.amount !== undefined && input.currency) {
      updates.amount_minor = toMoneyMinor(input.amount, input.currency).toString();
    }
    if (input.currency) {
      updates.currency = input.currency;
    }
    if (input.note !== undefined) {
      updates.note = input.note;
    }

    await this.repository.updateTransaction(transactionId, updates as any);
  }

  /**
   * 현금 라인 수정
   */
  async updateCash(cashId: number, input: EditCashInput) {
    const updates: Record<string, unknown> = {};

    if (input.amount !== undefined && input.currency) {
      updates.amount_minor = toMoneyMinor(input.amount, input.currency).toString();
    }
    if (input.currency) {
      updates.currency = input.currency;
    }

    await this.repository.updateCash(cashId, updates as any);
  }

  /**
   * 포지션 라인 수정
   */
  async updatePosition(positionId: number, input: EditPositionInput) {
    const updates: Record<string, unknown> = {};

    if (input.qty !== undefined) {
      updates.qty_nano = toQtyNano(input.qty).toString();
    }
    if (input.avg_cost !== undefined) {
      updates.avg_cost = input.avg_cost;
    }
    if (input.currency) {
      updates.currency = input.currency;
    }

    await this.repository.updatePosition(positionId, updates as any);
  }

  /**
   * 배당 입력
   */
  async createDividend(userId: string, input: CreateDividendInput) {
    // 최신 스냅샷 조회
    const { data: latestSnapshot, error } = await this.db
      .from("snapshots")
      .select("id")
      .eq("user_id", userId)
      .order("snapshot_date", { ascending: false })
      .order("created_at", { ascending: false })
      .limit(1)
      .single();

    if (error || !latestSnapshot) {
      throw new Error("No snapshot found for user");
    }

    await this.repository.createDividend({
      snapshot_id: latestSnapshot.id,
      account_id: input.account_id,
      instrument_id: input.instrument_id,
      trade_datetime: `${input.pay_date}T00:00:00Z`,
      amount_minor: toMoneyMinor(input.amount, input.currency).toString(),
      currency: input.currency,
      note: input.note,
    });

    return { created: true };
  }
}
