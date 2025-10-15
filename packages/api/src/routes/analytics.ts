/**
 * Analytics Routes
 */

import { Router } from "express";
import { authMiddleware } from "../middleware/auth";
import { validateQuery } from "../middleware/validation";
import {
  getDashboardSummaryHandler,
  getTimeseriesHandler,
  getAllocationsHandler,
  getCashflowSummaryHandler,
  getDividendsHandler,
} from "../domains/analytics/handlers";
import {
  dashboardSummaryQuerySchema,
  timeseriesQuerySchema,
  allocationsQuerySchema,
  cashflowQuerySchema,
} from "../domains/analytics/validator";

const router = Router();

/**
 * GET /v1/dashboard/summary
 * 대시보드 요약
 */
router.get(
  "/dashboard/summary",
  authMiddleware,
  validateQuery(dashboardSummaryQuerySchema),
  getDashboardSummaryHandler
);

/**
 * GET /v1/dashboard/timeseries
 * 시계열 데이터
 */
router.get(
  "/dashboard/timeseries",
  authMiddleware,
  validateQuery(timeseriesQuerySchema),
  getTimeseriesHandler
);

/**
 * GET /v1/dashboard/allocations
 * 비중 데이터
 */
router.get(
  "/dashboard/allocations",
  authMiddleware,
  validateQuery(allocationsQuerySchema),
  getAllocationsHandler
);

/**
 * GET /v1/cashflow/summary
 * 현금흐름 요약
 */
router.get(
  "/cashflow/summary",
  authMiddleware,
  validateQuery(cashflowQuerySchema),
  getCashflowSummaryHandler
);

/**
 * GET /v1/dividends
 * 배당 요약
 */
router.get(
  "/dividends",
  authMiddleware,
  getDividendsHandler
);

export default router;

