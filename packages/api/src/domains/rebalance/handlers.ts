/**
 * Rebalance HTTP Handlers
 */

import { Request, Response, NextFunction } from "express";
import { AuthenticatedRequest } from "../../types/express";
import { RebalanceService } from "./service";
import { createUserClient } from "../../utils/db";

/**
 * GET /v1/rebalance/targets
 * 타겟 목록 조회
 */
export async function getTargetsHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authReq = req as AuthenticatedRequest;
    const db = createUserClient(authReq.accessToken);
    const service = new RebalanceService(db);

    const result = await service.getTargets(authReq.user.id);
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}

/**
 * POST /v1/rebalance/targets
 * 타겟 저장
 */
export async function saveTargetsHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authReq = req as AuthenticatedRequest;
    const db = createUserClient(authReq.accessToken);
    const service = new RebalanceService(db);

    const result = await service.saveTargets(authReq.user.id, req.body);
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}

/**
 * GET /v1/rebalance/rules
 * 룰 목록 조회
 */
export async function getRulesHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authReq = req as AuthenticatedRequest;
    const db = createUserClient(authReq.accessToken);
    const service = new RebalanceService(db);

    const result = await service.getRules(authReq.user.id);
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}

/**
 * POST /v1/rebalance/rules
 * 룰 저장
 */
export async function saveRulesHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authReq = req as AuthenticatedRequest;
    const db = createUserClient(authReq.accessToken);
    const service = new RebalanceService(db);

    const result = await service.saveRules(authReq.user.id, req.body);
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}

/**
 * POST /v1/rebalance/suggest
 * 리밸런싱 제안 생성
 */
export async function createSuggestionHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authReq = req as AuthenticatedRequest;
    const db = createUserClient(authReq.accessToken);
    const service = new RebalanceService(db);

    const result = await service.createSuggestion(authReq.user.id, req.body);
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}

