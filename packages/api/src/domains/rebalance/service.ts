/**
 * Rebalance Service
 * 비즈니스 로직 레이어
 */

import { SupabaseClient } from "@supabase/supabase-js";
import { RebalanceRepository } from "./repository";
import {
  SaveRebalanceTargetsInput,
  SaveRebalanceRulesInput,
  RebalanceSuggestInput,
} from "./validator";

export class RebalanceService {
  private repository: RebalanceRepository;

  constructor(private db: SupabaseClient) {
    this.repository = new RebalanceRepository(db);
  }

  /**
   * 타겟 목록 조회
   */
  async getTargets(userId: string) {
    const targets = await this.repository.listTargets(userId);
    return { items: targets };
  }

  /**
   * 타겟 저장
   */
  async saveTargets(userId: string, input: SaveRebalanceTargetsInput) {
    await this.repository.replaceTargets(userId, input.targets);
    return { saved: true };
  }

  /**
   * 룰 목록 조회
   */
  async getRules(userId: string) {
    const rules = await this.repository.listRules(userId);
    return { items: rules };
  }

  /**
   * 룰 저장
   */
  async saveRules(userId: string, input: SaveRebalanceRulesInput) {
    await this.repository.replaceRules(userId, input.rules);
    return { saved: true };
  }

  /**
   * 리밸런싱 제안 생성
   *
   * TODO: 실제 리밸런싱 알고리즘 구현
   * 현재는 간단한 예시만 반환
   */
  async createSuggestion(userId: string, input: RebalanceSuggestInput) {
    // 1. 현재 포트폴리오 조회
    const { data: snapshotData } = await this.db
      .from("snapshots")
      .select("id")
      .eq("user_id", userId)
      .eq("snapshot_date", input.as_of)
      .single();

    if (!snapshotData) {
      throw new Error("No snapshot found for the given date");
    }

    // 2. 포지션 조회
    const { data: positions } = await this.db
      .from("snapshot_positions")
      .select("account_id, instrument_id, qty_nano, instruments(asset_class)")
      .eq("snapshot_id", snapshotData.id);

    // 3. 간단한 제안 생성 (예시)
    const proposals = positions
      ?.reduce((acc: any[], pos: any) => {
        const existing = acc.find((p) => p.account_id === pos.account_id);
        if (existing) {
          existing.trades.push({
            instrument_id: pos.instrument_id,
            action: "hold" as const,
            qty: Number(pos.qty_nano) / 1e9,
            amount_minor: 0n,
            currency: "KRW",
          });
        } else {
          acc.push({
            account_id: pos.account_id,
            trades: [
              {
                instrument_id: pos.instrument_id,
                action: "hold" as const,
                qty: Number(pos.qty_nano) / 1e9,
                amount_minor: 0n,
                currency: "KRW",
              },
            ],
            after_weights: {},
          });
        }
        return acc;
      }, []) || [];

    return {
      as_of: input.as_of,
      proposals: proposals.map((p) => ({
        ...p,
        trades: p.trades.map((t: any) => ({
          ...t,
          amount_minor: t.amount_minor.toString(),
        })),
      })),
      summary: {
        total_trades: proposals.reduce((sum, p) => sum + p.trades.length, 0),
        total_amount_minor: "0",
        expected_deviation: 0.02,
      },
    };
  }
}
