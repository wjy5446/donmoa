/**
 * Market Data HTTP Handlers
 */

import { Request, Response, NextFunction } from "express";
import { AuthenticatedRequest } from "../../types/express";
import { MarketService } from "./service";
import { createUserClient, supabaseClient } from "../../utils/db";
import { ErrorCode } from "@donmoa/shared";
import { ApiError } from "../../middleware/error";

/**
 * GET /v1/instruments
 * 종목 검색
 */
export async function searchInstrumentsHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authReq = req as AuthenticatedRequest;
    const query = req.query as any;

    // 공개 데이터이므로 익명 클라이언트 사용 가능
    const db = supabaseClient;
    const service = new MarketService(db);

    const result = await service.searchInstruments(query);
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}

/**
 * GET /v1/instruments/:id
 * 종목 상세 조회
 */
export async function getInstrumentHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const instrumentId = parseInt(req.params.id, 10);

    if (isNaN(instrumentId)) {
      throw new ApiError(ErrorCode.VALIDATION_ERROR, "Invalid instrument ID");
    }

    const db = supabaseClient;
    const service = new MarketService(db);

    const result = await service.getInstrumentById(instrumentId);

    if (!result) {
      throw new ApiError(ErrorCode.NOT_FOUND, "Instrument not found");
    }

    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}

/**
 * GET /v1/instruments/:id/metrics
 * 종목 메트릭스 조회
 */
export async function getInstrumentMetricsHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const instrumentId = parseInt(req.params.id, 10);

    if (isNaN(instrumentId)) {
      throw new ApiError(ErrorCode.VALIDATION_ERROR, "Invalid instrument ID");
    }

    const db = supabaseClient;
    const service = new MarketService(db);

    const result = await service.getInstrumentMetrics({
      instrument_id: instrumentId,
      window: req.query.window as string,
    });

    if (!result) {
      throw new ApiError(ErrorCode.NOT_FOUND, "Instrument not found");
    }

    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}

/**
 * GET /v1/prices/daily
 * 일별 가격 조회
 */
export async function getDailyPricesHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const query = req.query as any;

    const db = supabaseClient;
    const service = new MarketService(db);

    const result = await service.getDailyPrices(query);
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}

/**
 * GET /v1/fx/daily
 * 환율 조회
 */
export async function getDailyFxHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const query = req.query as any;

    const db = supabaseClient;
    const service = new MarketService(db);

    const result = await service.getDailyFx(query);
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}

