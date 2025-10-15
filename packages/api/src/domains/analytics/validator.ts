/**
 * Analytics Validator
 */

import { z } from "zod";

/**
 * 대시보드 요약 쿼리 스키마
 */
export const dashboardSummaryQuerySchema = z.object({
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
});

/**
 * 시계열 쿼리 스키마
 */
export const timeseriesQuerySchema = z.object({
  metric: z.enum(["total_equity", "return", "dividend", "cashflow"]),
  interval: z.enum(["day", "month"]).optional().default("month"),
  from: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional(),
  to: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional(),
});

/**
 * 비중 쿼리 스키마
 */
export const allocationsQuerySchema = z.object({
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  group: z.enum(["account", "asset_class", "subclass"]),
});

/**
 * 현금흐름 쿼리 스키마
 */
export const cashflowQuerySchema = z.object({
  from: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  to: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
});

export type DashboardSummaryQuery = z.infer<typeof dashboardSummaryQuerySchema>;
export type TimeseriesQuery = z.infer<typeof timeseriesQuerySchema>;
export type AllocationsQuery = z.infer<typeof allocationsQuerySchema>;
export type CashflowQuery = z.infer<typeof cashflowQuerySchema>;
