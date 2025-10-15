/**
 * Market Data Validator
 */

import { z } from "zod";

/**
 * 종목 검색 쿼리 스키마
 */
export const instrumentSearchQuerySchema = z.object({
  query: z.string().optional(),
  asset_class: z.string().optional(),
  limit: z
    .string()
    .transform((val) => parseInt(val, 10))
    .pipe(z.number().min(1).max(100))
    .optional()
    .default("30"),
  cursor: z.string().optional(),
});

/**
 * 일별 가격 조회 쿼리 스키마
 */
export const dailyPricesQuerySchema = z.object({
  instrument_id: z
    .string()
    .transform((val) => parseInt(val, 10))
    .pipe(z.number()),
  from: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional(),
  to: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional(),
});

/**
 * 환율 조회 쿼리 스키마
 */
export const dailyFxQuerySchema = z.object({
  base: z.string().length(3),
  quote: z.string().length(3),
  from: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional(),
  to: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional(),
});

/**
 * 종목 메트릭스 쿼리 스키마
 */
export const instrumentMetricsQuerySchema = z.object({
  instrument_id: z
    .string()
    .transform((val) => parseInt(val, 10))
    .pipe(z.number()),
  window: z.string().optional(), // "1,3,6,12"
});

export type InstrumentSearchQuery = z.infer<typeof instrumentSearchQuerySchema>;
export type DailyPricesQuery = z.infer<typeof dailyPricesQuerySchema>;
export type DailyFxQuery = z.infer<typeof dailyFxQuerySchema>;
export type InstrumentMetricsQuery = z.infer<typeof instrumentMetricsQuerySchema>;

