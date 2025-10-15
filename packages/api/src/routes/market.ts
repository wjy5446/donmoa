/**
 * Market Data Routes
 */

import { Router } from "express";
import { optionalAuthMiddleware } from "../middleware/auth";
import { validateQuery } from "../middleware/validation";
import {
  searchInstrumentsHandler,
  getInstrumentHandler,
  getInstrumentMetricsHandler,
  getDailyPricesHandler,
  getDailyFxHandler,
} from "../domains/market/handlers";
import {
  instrumentSearchQuerySchema,
  dailyPricesQuerySchema,
  dailyFxQuerySchema,
} from "../domains/market/validator";

const router = Router();

/**
 * GET /v1/instruments
 * 종목 검색
 */
router.get(
  "/instruments",
  optionalAuthMiddleware,
  validateQuery(instrumentSearchQuerySchema),
  searchInstrumentsHandler
);

/**
 * GET /v1/instruments/:id
 * 종목 상세 조회
 */
router.get(
  "/instruments/:id",
  optionalAuthMiddleware,
  getInstrumentHandler
);

/**
 * GET /v1/instruments/:id/metrics
 * 종목 메트릭스 조회
 */
router.get(
  "/instruments/:id/metrics",
  optionalAuthMiddleware,
  getInstrumentMetricsHandler
);

/**
 * GET /v1/prices/daily
 * 일별 가격 조회
 */
router.get(
  "/prices/daily",
  optionalAuthMiddleware,
  validateQuery(dailyPricesQuerySchema),
  getDailyPricesHandler
);

/**
 * GET /v1/fx/daily
 * 환율 조회
 */
router.get(
  "/fx/daily",
  optionalAuthMiddleware,
  validateQuery(dailyFxQuerySchema),
  getDailyFxHandler
);

export default router;

