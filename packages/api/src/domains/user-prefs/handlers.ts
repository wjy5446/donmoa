/**
 * User Preferences HTTP Handlers
 */

import { Request, Response, NextFunction } from "express";
import { AuthenticatedRequest } from "../../types/express";
import { UserPrefsService } from "./service";
import { createUserClient } from "../../utils/db";
import { ErrorCode } from "@donmoa/shared";
import { ApiError } from "../../middleware/error";

/**
 * GET /v1/categories
 * 카테고리 목록 조회
 */
export async function listCategoriesHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authReq = req as AuthenticatedRequest;
    const db = createUserClient(authReq.accessToken);
    const service = new UserPrefsService(db);

    const result = await service.listCategories(authReq.user.id);
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}

/**
 * POST /v1/categories
 * 카테고리 생성
 */
export async function createCategoryHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authReq = req as AuthenticatedRequest;
    const db = createUserClient(authReq.accessToken);
    const service = new UserPrefsService(db);

    const result = await service.createCategory(authReq.user.id, req.body);
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}

/**
 * PATCH /v1/categories/:id
 * 카테고리 수정
 */
export async function updateCategoryHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const categoryId = parseInt(req.params.id, 10);

    if (isNaN(categoryId)) {
      throw new ApiError(ErrorCode.VALIDATION_ERROR, "Invalid category ID");
    }

    const authReq = req as AuthenticatedRequest;
    const db = createUserClient(authReq.accessToken);
    const service = new UserPrefsService(db);

    const result = await service.updateCategory(categoryId, req.body);
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}

/**
 * DELETE /v1/categories/:id
 * 카테고리 삭제
 */
export async function deleteCategoryHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const categoryId = parseInt(req.params.id, 10);

    if (isNaN(categoryId)) {
      throw new ApiError(ErrorCode.VALIDATION_ERROR, "Invalid category ID");
    }

    const authReq = req as AuthenticatedRequest;
    const db = createUserClient(authReq.accessToken);
    const service = new UserPrefsService(db);

    const result = await service.deleteCategory(categoryId);
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}

/**
 * POST /v1/favorites/toggle
 * 즐겨찾기 토글
 */
export async function toggleFavoriteHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authReq = req as AuthenticatedRequest;
    const db = createUserClient(authReq.accessToken);
    const service = new UserPrefsService(db);

    const result = await service.toggleFavorite(authReq.user.id, req.body);
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}

/**
 * GET /v1/favorites
 * 즐겨찾기 목록 조회
 */
export async function listFavoritesHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authReq = req as AuthenticatedRequest;
    const query = req.query as any;

    const db = createUserClient(authReq.accessToken);
    const service = new UserPrefsService(db);

    const result = await service.listFavorites(authReq.user.id, query);
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}

/**
 * GET /v1/dashboard/prefs
 * 대시보드 설정 조회
 */
export async function getDashboardPrefsHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authReq = req as AuthenticatedRequest;
    const db = createUserClient(authReq.accessToken);
    const service = new UserPrefsService(db);

    const result = await service.getDashboardPrefs(authReq.user.id);
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}

/**
 * PUT /v1/dashboard/prefs
 * 대시보드 설정 저장
 */
export async function saveDashboardPrefsHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authReq = req as AuthenticatedRequest;
    const db = createUserClient(authReq.accessToken);
    const service = new UserPrefsService(db);

    const result = await service.saveDashboardPrefs(authReq.user.id, req.body);
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}

