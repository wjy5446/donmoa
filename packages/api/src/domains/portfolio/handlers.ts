/**
 * Portfolio HTTP Handlers
 */

import { Request, Response, NextFunction } from "express";
import { AuthenticatedRequest } from "../../types/express";
import { PortfolioService } from "./service";
import { createUserClient } from "../../utils/db";
import { ErrorCode } from "@donmoa/shared";
import { ApiError } from "../../middleware/error";

/**
 * GET /v1/accounts
 * 계좌 목록 조회
 */
export async function listAccountsHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authReq = req as AuthenticatedRequest;
    const db = createUserClient(authReq.accessToken);
    const service = new PortfolioService(db);

    const accounts = await service.listAccounts(authReq.user.id);
    res.status(200).json({ items: accounts });
  } catch (error) {
    next(error);
  }
}

/**
 * GET /v1/accounts/:id
 * 계좌 상세 조회
 */
export async function getAccountHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authReq = req as AuthenticatedRequest;
    const accountId = parseInt(req.params.id, 10);

    if (isNaN(accountId)) {
      throw new ApiError(ErrorCode.VALIDATION_ERROR, "Invalid account ID");
    }

    const db = createUserClient(authReq.accessToken);
    const service = new PortfolioService(db);

    const account = await service.getAccountById(accountId, authReq.user.id);

    if (!account) {
      throw new ApiError(ErrorCode.NOT_FOUND, "Account not found");
    }

    res.status(200).json(account);
  } catch (error) {
    next(error);
  }
}

/**
 * PATCH /v1/transactions/:id
 * 거래 라인 수정
 */
export async function patchTransactionHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authReq = req as AuthenticatedRequest;
    const transactionId = parseInt(req.params.id, 10);

    if (isNaN(transactionId)) {
      throw new ApiError(ErrorCode.VALIDATION_ERROR, "Invalid transaction ID");
    }

    const db = createUserClient(authReq.accessToken);
    const service = new PortfolioService(db);

    await service.updateTransaction(transactionId, req.body);
    res.status(200).json({ updated: true });
  } catch (error) {
    next(error);
  }
}

/**
 * PATCH /v1/cash/:id
 * 현금 라인 수정
 */
export async function patchCashHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authReq = req as AuthenticatedRequest;
    const cashId = parseInt(req.params.id, 10);

    if (isNaN(cashId)) {
      throw new ApiError(ErrorCode.VALIDATION_ERROR, "Invalid cash ID");
    }

    const db = createUserClient(authReq.accessToken);
    const service = new PortfolioService(db);

    await service.updateCash(cashId, req.body);
    res.status(200).json({ updated: true });
  } catch (error) {
    next(error);
  }
}

/**
 * PATCH /v1/positions/:id
 * 포지션 라인 수정
 */
export async function patchPositionHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authReq = req as AuthenticatedRequest;
    const positionId = parseInt(req.params.id, 10);

    if (isNaN(positionId)) {
      throw new ApiError(ErrorCode.VALIDATION_ERROR, "Invalid position ID");
    }

    const db = createUserClient(authReq.accessToken);
    const service = new PortfolioService(db);

    await service.updatePosition(positionId, req.body);
    res.status(200).json({ updated: true });
  } catch (error) {
    next(error);
  }
}

/**
 * POST /v1/dividends
 * 배당 입력
 */
export async function createDividendHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authReq = req as AuthenticatedRequest;
    const db = createUserClient(authReq.accessToken);
    const service = new PortfolioService(db);

    const result = await service.createDividend(authReq.user.id, req.body);
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}
