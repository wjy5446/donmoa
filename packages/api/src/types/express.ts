/**
 * Express 타입 확장
 */

import { Request, Response } from "express";

/**
 * 인증된 요청 타입
 */
export interface AuthenticatedRequest extends Request {
  user: {
    id: string;
    email?: string;
  };
  accessToken: string;
}

/**
 * 타입 안전 응답 헬퍼
 */
export function sendSuccess<T>(res: Response, data: T, statusCode = 200): void {
  res.status(statusCode).json(data);
}

export function sendError(
  res: Response,
  code: string,
  message: string,
  statusCode = 400
): void {
  res.status(statusCode).json({
    error: {
      code,
      message,
    },
  });
}
