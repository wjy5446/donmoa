/**
 * Rebalance Routes
 */

import { Router } from "express";
import { authMiddleware } from "../middleware/auth";
import { validateBody } from "../middleware/validation";
import {
  getTargetsHandler,
  saveTargetsHandler,
  getRulesHandler,
  saveRulesHandler,
  createSuggestionHandler,
} from "../domains/rebalance/handlers";
import {
  saveRebalanceTargetsSchema,
  saveRebalanceRulesSchema,
  rebalanceSuggestSchema,
} from "../domains/rebalance/validator";

const router = Router();

/**
 * GET /v1/rebalance/targets
 * 타겟 목록 조회
 */
router.get("/targets", authMiddleware, getTargetsHandler);

/**
 * POST /v1/rebalance/targets
 * 타겟 저장
 */
router.post(
  "/targets",
  authMiddleware,
  validateBody(saveRebalanceTargetsSchema),
  saveTargetsHandler
);

/**
 * GET /v1/rebalance/rules
 * 룰 목록 조회
 */
router.get("/rules", authMiddleware, getRulesHandler);

/**
 * POST /v1/rebalance/rules
 * 룰 저장
 */
router.post(
  "/rules",
  authMiddleware,
  validateBody(saveRebalanceRulesSchema),
  saveRulesHandler
);

/**
 * POST /v1/rebalance/suggest
 * 리밸런싱 제안 생성
 */
router.post(
  "/suggest",
  authMiddleware,
  validateBody(rebalanceSuggestSchema),
  createSuggestionHandler
);

export default router;

