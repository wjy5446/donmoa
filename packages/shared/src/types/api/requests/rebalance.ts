/**
 * Rebalance API Request Types
 */

import { RebalanceTarget, RebalanceRule } from "../../domain/rebalance";

/**
 * 리밸런싱 타겟 저장 요청
 */
export interface SaveRebalanceTargetsRequest {
  targets: Omit<RebalanceTarget, "id" | "user_id" | "created_at" | "updated_at">[];
}

/**
 * 리밸런싱 룰 저장 요청
 */
export interface SaveRebalanceRulesRequest {
  rules: Omit<RebalanceRule, "id" | "user_id" | "created_at" | "updated_at">[];
}

/**
 * 리밸런싱 제안 생성 요청
 */
export interface RebalanceSuggestRequest {
  as_of: string; // ISO date
  target: Array<{
    scope: "account" | "global";
    account_id?: number;
    asset_class: string;
    subclass?: string;
    target_pct: number;
  }>;
  rules?: Array<{
    type: "band" | "momentum" | "custom";
    params: Record<string, unknown>;
  }>;
}
