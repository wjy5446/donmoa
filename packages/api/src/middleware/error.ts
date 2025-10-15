/**
 * 에러 핸들링 미들웨어
 */

import { Request, Response, NextFunction } from "express";
import { ErrorCode, ERROR_STATUS_MAP, ApiError as SharedApiError } from "@donmoa/shared";
import { logger } from "../utils/logger";

/**
 * 커스텀 API 에러 클래스
 */
export class ApiError extends Error {
  constructor(
    public code: ErrorCode,
    message: string,
    public details?: Record<string, unknown>
  ) {
    super(message);
    this.name = "ApiError";
  }

  toJSON(): SharedApiError {
    return {
      error: {
        code: this.code,
        message: this.message,
        details: this.details,
      },
    };
  }

  get statusCode(): number {
    return ERROR_STATUS_MAP[this.code] || 500;
  }
}

/**
 * 에러 핸들러 미들웨어
 */
export function errorHandler(
  err: Error | ApiError,
  req: Request,
  res: Response,
  _next: NextFunction
): void {
  // ApiError인 경우
  if (err instanceof ApiError) {
    logger.warn("API Error", {
      code: err.code,
      message: err.message,
      path: req.path,
      method: req.method,
      details: err.details,
    });

    res.status(err.statusCode).json(err.toJSON());
    return;
  }

  // 일반 에러인 경우
  logger.error("Unhandled Error", err, {
    path: req.path,
    method: req.method,
  });

  res.status(500).json({
    error: {
      code: ErrorCode.INTERNAL_ERROR,
      message: "An unexpected error occurred",
      details: process.env.NODE_ENV === "development" ? { message: err.message } : undefined,
    },
  });
}

/**
 * 404 핸들러
 */
export function notFoundHandler(req: Request, res: Response): void {
  res.status(404).json({
    error: {
      code: ErrorCode.NOT_FOUND,
      message: `Route ${req.method} ${req.path} not found`,
    },
  });
}
