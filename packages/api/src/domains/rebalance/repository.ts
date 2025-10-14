/**
 * Rebalance Repository
 * DB 접근 레이어
 */

import { SupabaseClient } from "@supabase/supabase-js";

export class RebalanceRepository {
  constructor(private db: SupabaseClient) {}

  /**
   * 타겟 목록 조회
   */
  async listTargets(userId: string) {
    const { data, error } = await this.db
      .from("rebalance_targets")
      .select("*")
      .eq("user_id", userId)
      .order("created_at", { ascending: false });

    if (error) throw error;
    return data || [];
  }

  /**
   * 타겟 저장 (교체)
   */
  async replaceTargets(
    userId: string,
    targets: Array<{
      scope: string;
      account_id?: number;
      asset_class: string;
      subclass?: string;
      target_pct: number;
    }>
  ) {
    // 기존 타겟 삭제
    await this.db.from("rebalance_targets").delete().eq("user_id", userId);

    // 새 타겟 삽입
    if (targets.length > 0) {
      const { error } = await this.db
        .from("rebalance_targets")
        .insert(targets.map((t) => ({ ...t, user_id: userId })));

      if (error) throw error;
    }
  }

  /**
   * 룰 목록 조회
   */
  async listRules(userId: string) {
    const { data, error } = await this.db
      .from("rebalance_rules")
      .select("*")
      .eq("user_id", userId)
      .order("created_at", { ascending: false });

    if (error) throw error;
    return data || [];
  }

  /**
   * 룰 저장 (교체)
   */
  async replaceRules(
    userId: string,
    rules: Array<{
      name: string;
      type: string;
      params: Record<string, unknown>;
      enabled: boolean;
    }>
  ) {
    // 기존 룰 삭제
    await this.db.from("rebalance_rules").delete().eq("user_id", userId);

    // 새 룰 삽입
    if (rules.length > 0) {
      const { error } = await this.db
        .from("rebalance_rules")
        .insert(rules.map((r) => ({ ...r, user_id: userId })));

      if (error) throw error;
    }
  }
}

