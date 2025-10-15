/**
 * Rebalance Validator
 */

import { z } from "zod";

/**
 * 타겟 저장 스키마
 */
export const saveRebalanceTargetsSchema = z.object({
  targets: z.array(
    z.object({
      scope: z.enum(["account", "global"]),
      account_id: z.number().optional(),
      asset_class: z.string(),
      subclass: z.string().optional(),
      target_pct: z.number().min(0).max(1),
    })
  ),
});

/**
 * 룰 저장 스키마
 */
export const saveRebalanceRulesSchema = z.object({
  rules: z.array(
    z.object({
      name: z.string(),
      type: z.enum(["band", "momentum", "custom"]),
      params: z.record(z.unknown()),
      enabled: z.boolean().optional().default(true),
    })
  ),
});

/**
 * 리밸런싱 제안 스키마
 */
export const rebalanceSuggestSchema = z.object({
  as_of: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  target: z.array(
    z.object({
      scope: z.enum(["account", "global"]),
      account_id: z.number().optional(),
      asset_class: z.string(),
      subclass: z.string().optional(),
      target_pct: z.number().min(0).max(1),
    })
  ),
  rules: z
    .array(
      z.object({
        type: z.enum(["band", "momentum", "custom"]),
        params: z.record(z.unknown()),
      })
    )
    .optional(),
});

export type SaveRebalanceTargetsInput = z.infer<typeof saveRebalanceTargetsSchema>;
export type SaveRebalanceRulesInput = z.infer<typeof saveRebalanceRulesSchema>;
export type RebalanceSuggestInput = z.infer<typeof rebalanceSuggestSchema>;

