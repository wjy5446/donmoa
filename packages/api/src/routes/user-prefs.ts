/**
 * User Preferences Routes
 */

import { Router } from "express";
import { authMiddleware } from "../middleware/auth";
import { validateBody, validateQuery } from "../middleware/validation";
import {
  listCategoriesHandler,
  createCategoryHandler,
  updateCategoryHandler,
  deleteCategoryHandler,
  toggleFavoriteHandler,
  listFavoritesHandler,
  getDashboardPrefsHandler,
  saveDashboardPrefsHandler,
} from "../domains/user-prefs/handlers";
import {
  categoryCreateSchema,
  categoryUpdateSchema,
  favoriteToggleSchema,
  favoritesQuerySchema,
  dashboardPrefsSchema,
} from "../domains/user-prefs/validator";

const router = Router();

/**
 * GET /v1/categories
 * 카테고리 목록 조회
 */
router.get("/categories", authMiddleware, listCategoriesHandler);

/**
 * POST /v1/categories
 * 카테고리 생성
 */
router.post(
  "/categories",
  authMiddleware,
  validateBody(categoryCreateSchema),
  createCategoryHandler
);

/**
 * PATCH /v1/categories/:id
 * 카테고리 수정
 */
router.patch(
  "/categories/:id",
  authMiddleware,
  validateBody(categoryUpdateSchema),
  updateCategoryHandler
);

/**
 * DELETE /v1/categories/:id
 * 카테고리 삭제
 */
router.delete("/categories/:id", authMiddleware, deleteCategoryHandler);

/**
 * POST /v1/favorites/toggle
 * 즐겨찾기 토글
 */
router.post(
  "/favorites/toggle",
  authMiddleware,
  validateBody(favoriteToggleSchema),
  toggleFavoriteHandler
);

/**
 * GET /v1/favorites
 * 즐겨찾기 목록 조회
 */
router.get(
  "/favorites",
  authMiddleware,
  validateQuery(favoritesQuerySchema),
  listFavoritesHandler
);

/**
 * GET /v1/dashboard/prefs
 * 대시보드 설정 조회
 */
router.get("/dashboard/prefs", authMiddleware, getDashboardPrefsHandler);

/**
 * PUT /v1/dashboard/prefs
 * 대시보드 설정 저장
 */
router.put(
  "/dashboard/prefs",
  authMiddleware,
  validateBody(dashboardPrefsSchema),
  saveDashboardPrefsHandler
);

export default router;

