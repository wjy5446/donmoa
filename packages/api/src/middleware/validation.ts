/**
 * 요청 검증 미들웨어 (Zod 기반)
 */

import { Request, Response, NextFunction } from "express";
import { ZodSchema, ZodError } from "zod";
import { ErrorCode } from "@donmoa/shared";
import { ApiError } from "./error";

/**
 * 요청 바디 검증
 */
export function validateBody<T>(schema: ZodSchema<T>) {
  return async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      req.body = await schema.parseAsync(req.body);
      next();
    } catch (error) {
      if (error instanceof ZodError) {
        next(
          new ApiError(ErrorCode.VALIDATION_ERROR, "Validation failed", {
            issues: error.issues,
          })
        );
      } else {
        next(error);
      }
    }
  };
}

/**
 * 쿼리 파라미터 검증
 */
export function validateQuery<T>(schema: ZodSchema<T>) {
  return async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      req.query = await schema.parseAsync(req.query);
      next();
    } catch (error) {
      if (error instanceof ZodError) {
        next(
          new ApiError(ErrorCode.VALIDATION_ERROR, "Query validation failed", {
            issues: error.issues,
          })
        );
      } else {
        next(error);
      }
    }
  };
}

/**
 * URL 파라미터 검증
 */
export function validateParams<T>(schema: ZodSchema<T>) {
  return async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      req.params = await schema.parseAsync(req.params);
      next();
    } catch (error) {
      if (error instanceof ZodError) {
        next(
          new ApiError(ErrorCode.VALIDATION_ERROR, "Params validation failed", {
            issues: error.issues,
          })
        );
      } else {
        next(error);
      }
    }
  };
}
