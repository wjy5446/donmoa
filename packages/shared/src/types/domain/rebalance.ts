/**
 * Rebalancing Domain Types
 * 리밸런싱 관련 타입 정의
 */

/**
 * 타겟 스코프
 */
export type TargetScope = "account" | "global";

/**
 * 리밸런싱 타겟 (정적 비중)
 */
export interface RebalanceTarget {
  id?: number;
  user_id?: string;
  scope: TargetScope;
  account_id?: number; // scope === 'account'일 때
  asset_class: string;
  subclass?: string;
  target_pct: number; // 0~1
  created_at?: string;
  updated_at?: string;
}

/**
 * 리밸런싱 룰 타입
 */
export type RebalanceRuleType = "band" | "momentum" | "custom";

/**
 * 리밸런싱 룰 (동적 규칙)
 */
export interface RebalanceRule {
  id?: number;
  user_id?: string;
  name: string;
  type: RebalanceRuleType;
  params: Record<string, unknown>; // band: { threshold: 0.05 }, momentum: { window: 90 }
  enabled: boolean;
  created_at?: string;
  updated_at?: string;
}

/**
 * 리밸런싱 거래 제안
 */
export interface RebalanceTrade {
  instrument_id: number;
  instrument_name?: string;
  action: "buy" | "sell";
  qty: number; // 수량 (실수)
  amount_minor: bigint; // 예상 금액
  currency: string;
}

/**
 * 리밸런싱 제안 (계좌별)
 */
export interface RebalanceProposal {
  account_id: number;
  account_name?: string;
  trades: RebalanceTrade[];
  after_weights: Record<string, number>; // asset_class -> weight
  estimated_cost_minor?: bigint; // 예상 수수료
}

/**
 * 리밸런싱 제안 응답
 */
export interface RebalanceSuggestion {
  as_of: string; // ISO date
  proposals: RebalanceProposal[];
  summary?: {
    total_trades: number;
    total_amount_minor: bigint;
    expected_deviation: number; // 목표 대비 예상 오차 (평균)
  };
}
