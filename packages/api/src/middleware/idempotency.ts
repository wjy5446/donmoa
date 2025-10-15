/**
 * Idempotency Key 미들웨어
 * 중복 요청 방지
 */

import { Request, Response, NextFunction } from "express";
import { ErrorCode } from "@donmoa/shared";
import { ApiError } from "./error";
import { supabaseAdmin } from "../utils/db";

// 간단한 인메모리 캐시 (프로덕션에서는 Redis 사용 권장)
const idempotencyCache = new Map<
  string,
  { response: unknown; timestamp: number }
>();

// 24시간 후 자동 삭제
const CACHE_TTL = 24 * 60 * 60 * 1000;

/**
 * Idempotency Key 검증 미들웨어
 */
export async function idempotencyMiddleware(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const idempotencyKey = req.headers["idempotency-key"] as string | undefined;

    // POST, PUT, PATCH 요청에만 적용
    if (!["POST", "PUT", "PATCH"].includes(req.method)) {
      next();
      return;
    }

    if (!idempotencyKey) {
      // Idempotency Key가 없어도 진행 (선택 사항)
      next();
      return;
    }

    // 캐시 확인
    const cached = idempotencyCache.get(idempotencyKey);
    if (cached) {
      const age = Date.now() - cached.timestamp;
      if (age < CACHE_TTL) {
        // 캐시된 응답 반환
        res.status(200).json(cached.response);
        return;
      } else {
        // TTL 만료, 삭제
        idempotencyCache.delete(idempotencyKey);
      }
    }

    // 응답 캐싱을 위한 래퍼
    const originalJson = res.json.bind(res);
    res.json = function (body: unknown) {
      // 성공 응답만 캐싱 (2xx)
      if (res.statusCode >= 200 && res.statusCode < 300) {
        idempotencyCache.set(idempotencyKey, {
          response: body,
          timestamp: Date.now(),
        });
      }
      return originalJson(body);
    };

    next();
  } catch (error) {
    next(error);
  }
}

/**
 * 캐시 정리 (주기적 실행 권장)
 */
export function cleanupIdempotencyCache(): void {
  const now = Date.now();
  for (const [key, value] of idempotencyCache.entries()) {
    if (now - value.timestamp > CACHE_TTL) {
      idempotencyCache.delete(key);
    }
  }
}

// 1시간마다 캐시 정리
setInterval(cleanupIdempotencyCache, 60 * 60 * 1000);
