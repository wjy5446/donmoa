/**
 * Snapshot Validator
 * 입력 데이터 검증
 */

import { z } from "zod";

/**
 * 스냅샷 커밋 요청 스키마
 */
export const snapshotCommitSchema = z.object({
  snapshot_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  source: z.enum(["cli", "manual", "banksalad", "domino", "web"]),
  notes: z.string().optional(),
  cash: z.array(
    z.object({
      account_external_id: z.string(),
      currency: z.string().length(3),
      amount: z.number(),
    })
  ),
  positions: z.array(
    z.object({
      account_external_id: z.string(),
      symbol: z.string(),
      currency: z.string().length(3),
      qty: z.number(),
      avg_cost: z.number().optional(),
    })
  ),
  transactions: z.array(
    z.object({
      account_external_id: z.string(),
      type: z.enum([
        "buy",
        "sell",
        "dividend",
        "fee",
        "transfer",
        "deposit",
        "withdraw",
        "interest",
        "other",
      ]),
      symbol: z.string().optional(),
      trade_datetime: z.string().optional(),
      settle_date: z.string().optional(),
      qty: z.number().optional(),
      price: z.number().optional(),
      amount: z.number().optional(),
      currency: z.string().length(3),
      note: z.string().optional(),
    })
  ),
  mapping: z
    .object({
      account_map: z.record(z.string(), z.number()).optional(),
      instrument_map: z.record(z.string(), z.number()).optional(),
    })
    .optional(),
  options: z
    .object({
      replace_same_date: z.boolean().optional(),
      create_missing_accounts: z.boolean().optional(),
      create_missing_instruments: z.boolean().optional(),
    })
    .optional(),
});

export type SnapshotCommitInput = z.infer<typeof snapshotCommitSchema>;

/**
 * 스냅샷 목록 조회 쿼리 스키마
 */
export const snapshotListQuerySchema = z.object({
  from: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional(),
  to: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional(),
  limit: z
    .string()
    .transform((val) => parseInt(val, 10))
    .pipe(z.number().min(1).max(200))
    .optional(),
  cursor: z.string().optional(),
});

export type SnapshotListQuery = z.infer<typeof snapshotListQuerySchema>;
