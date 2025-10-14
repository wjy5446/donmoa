/**
 * Analytics HTTP Handlers
 */

import { Request, Response, NextFunction } from "express";
import { AuthenticatedRequest } from "../../types/express";
import { AnalyticsService } from "./service";
import { createUserClient } from "../../utils/db";

/**
 * GET /v1/dashboard/summary
 * 대시보드 요약
 */
export async function getDashboardSummaryHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authReq = req as AuthenticatedRequest;
    const query = req.query as any;

    const db = createUserClient(authReq.accessToken);
    const service = new AnalyticsService(db);

    const result = await service.getDashboardSummary(authReq.user.id, query);
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}

/**
 * GET /v1/dashboard/timeseries
 * 시계열 데이터
 */
export async function getTimeseriesHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authReq = req as AuthenticatedRequest;
    const query = req.query as any;

    const db = createUserClient(authReq.accessToken);
    const service = new AnalyticsService(db);

    const result = await service.getTimeseries(authReq.user.id, query);
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}

/**
 * GET /v1/dashboard/allocations
 * 비중 데이터
 */
export async function getAllocationsHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authReq = req as AuthenticatedRequest;
    const query = req.query as any;

    const db = createUserClient(authReq.accessToken);
    const service = new AnalyticsService(db);

    const result = await service.getAllocations(authReq.user.id, query);
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}

/**
 * GET /v1/cashflow/summary
 * 현금흐름 요약
 */
export async function getCashflowSummaryHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authReq = req as AuthenticatedRequest;
    const query = req.query as any;

    const db = createUserClient(authReq.accessToken);
    const service = new AnalyticsService(db);

    const result = await service.getCashflowSummary(authReq.user.id, query);
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}

/**
 * GET /v1/dividends
 * 배당 요약
 */
export async function getDividendsHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authReq = req as AuthenticatedRequest;
    const { from, to } = req.query;

    const db = createUserClient(authReq.accessToken);
    const service = new AnalyticsService(db);

    const result = await service.getDividendsSummary(
      authReq.user.id,
      from as string,
      to as string
    );
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}

