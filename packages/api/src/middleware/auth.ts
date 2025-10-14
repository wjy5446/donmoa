/**
 * 인증 미들웨어
 */

import { Request, Response, NextFunction } from "express";
import { supabaseClient } from "../utils/db";
import { ErrorCode } from "@donmoa/shared";
import { ApiError } from "../types/error";

// Express Request에 사용자 정보 추가
declare global {
  namespace Express {
    interface Request {
      user?: {
        id: string;
        email?: string;
      };
      accessToken?: string;
    }
  }
}

/**
 * JWT 토큰 검증 및 사용자 정보 추출
 */
export async function authMiddleware(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authHeader = req.headers.authorization;

    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      throw new ApiError(
        ErrorCode.UNAUTHORIZED,
        "Missing or invalid authorization header"
      );
    }

    const token = authHeader.substring(7); // "Bearer " 제거

    // Supabase JWT 검증
    const {
      data: { user },
      error,
    } = await supabaseClient.auth.getUser(token);

    if (error || !user) {
      throw new ApiError(ErrorCode.UNAUTHORIZED, "Invalid or expired token");
    }

    // Request 객체에 사용자 정보 추가
    req.user = {
      id: user.id,
      email: user.email,
    };
    req.accessToken = token;

    next();
  } catch (error) {
    next(error);
  }
}

/**
 * 선택적 인증 미들웨어 (토큰이 있으면 검증, 없어도 통과)
 */
export async function optionalAuthMiddleware(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authHeader = req.headers.authorization;

    if (authHeader && authHeader.startsWith("Bearer ")) {
      const token = authHeader.substring(7);
      const {
        data: { user },
      } = await supabaseClient.auth.getUser(token);

      if (user) {
        req.user = {
          id: user.id,
          email: user.email,
        };
        req.accessToken = token;
      }
    }

    next();
  } catch (error) {
    // 인증 실패해도 계속 진행
    next();
  }
}
