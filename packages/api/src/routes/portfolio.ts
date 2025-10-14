/**
 * Portfolio Routes
 */

import { Router } from "express";
import { authMiddleware } from "../middleware/auth";
import { validateBody } from "../middleware/validation";
import {
  listAccountsHandler,
  getAccountHandler,
  patchTransactionHandler,
  patchCashHandler,
  patchPositionHandler,
  createDividendHandler,
} from "../domains/portfolio/handlers";
import {
  editTransactionSchema,
  editCashSchema,
  editPositionSchema,
  createDividendSchema,
} from "../domains/portfolio/validator";

const router = Router();

/**
 * GET /v1/accounts
 * 계좌 목록
 */
router.get("/accounts", authMiddleware, listAccountsHandler);

/**
 * GET /v1/accounts/:id
 * 계좌 상세
 */
router.get("/accounts/:id", authMiddleware, getAccountHandler);

/**
 * PATCH /v1/transactions/:id
 * 거래 라인 수정
 */
router.patch(
  "/transactions/:id",
  authMiddleware,
  validateBody(editTransactionSchema),
  patchTransactionHandler
);

/**
 * PATCH /v1/cash/:id
 * 현금 라인 수정
 */
router.patch(
  "/cash/:id",
  authMiddleware,
  validateBody(editCashSchema),
  patchCashHandler
);

/**
 * PATCH /v1/positions/:id
 * 포지션 라인 수정
 */
router.patch(
  "/positions/:id",
  authMiddleware,
  validateBody(editPositionSchema),
  patchPositionHandler
);

/**
 * POST /v1/dividends
 * 배당 입력
 */
router.post(
  "/dividends",
  authMiddleware,
  validateBody(createDividendSchema),
  createDividendHandler
);

export default router;
