/**
 * Portfolio Validator
 */

import { z } from "zod";

/**
 * 거래 라인 수정 스키마
 */
export const editTransactionSchema = z.object({
  trade_datetime: z.string().optional(),
  settle_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional(),
  qty: z.number().optional(),
  price: z.number().optional(),
  amount: z.number().optional(),
  currency: z.string().length(3).optional(),
  note: z.string().optional(),
});

/**
 * 현금 라인 수정 스키마
 */
export const editCashSchema = z.object({
  amount: z.number().optional(),
  currency: z.string().length(3).optional(),
});

/**
 * 포지션 라인 수정 스키마
 */
export const editPositionSchema = z.object({
  qty: z.number().optional(),
  avg_cost: z.number().optional(),
  currency: z.string().length(3).optional(),
});

/**
 * 배당 입력 스키마
 */
export const createDividendSchema = z.object({
  account_id: z.number(),
  instrument_id: z.number(),
  pay_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  amount: z.number(),
  currency: z.string().length(3),
  note: z.string().optional(),
});

export type EditTransactionInput = z.infer<typeof editTransactionSchema>;
export type EditCashInput = z.infer<typeof editCashSchema>;
export type EditPositionInput = z.infer<typeof editPositionSchema>;
export type CreateDividendInput = z.infer<typeof createDividendSchema>;
