/**
 * User Preferences Validator
 */

import { z } from "zod";

/**
 * 카테고리 생성 스키마
 */
export const categoryCreateSchema = z.object({
  name: z.string().min(1),
  parent_id: z.number().optional(),
  kind: z.enum(["income", "expense", "transfer", "investment", "other"]).optional(),
});

/**
 * 카테고리 수정 스키마
 */
export const categoryUpdateSchema = z.object({
  name: z.string().min(1).optional(),
  parent_id: z.number().optional(),
});

/**
 * 즐겨찾기 토글 스키마
 */
export const favoriteToggleSchema = z.object({
  instrument_id: z.number(),
  star: z.boolean(),
});

/**
 * 즐겨찾기 목록 쿼리 스키마
 */
export const favoritesQuerySchema = z.object({
  held: z
    .string()
    .transform((val) => val === "true")
    .optional(),
  asset_class: z.string().optional(),
});

/**
 * 대시보드 설정 저장 스키마
 */
export const dashboardPrefsSchema = z.object({
  cards: z.array(z.string()).optional(),
  layout: z.string().optional(),
  custom_layout: z.record(z.unknown()).optional(),
});

export type CategoryCreateInput = z.infer<typeof categoryCreateSchema>;
export type CategoryUpdateInput = z.infer<typeof categoryUpdateSchema>;
export type FavoriteToggleInput = z.infer<typeof favoriteToggleSchema>;
export type FavoritesQuery = z.infer<typeof favoritesQuerySchema>;
export type DashboardPrefsInput = z.infer<typeof dashboardPrefsSchema>;

