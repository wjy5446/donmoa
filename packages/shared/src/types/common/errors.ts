/**
 * API 에러 응답 구조
 */
export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

/**
 * 에러 코드 정의
 */
export enum ErrorCode {
  // 인증/인가
  UNAUTHORIZED = "UNAUTHORIZED",
  FORBIDDEN = "FORBIDDEN",

  // 리소스
  NOT_FOUND = "NOT_FOUND",
  CONFLICT = "CONFLICT",

  // 검증
  VALIDATION_ERROR = "VALIDATION_ERROR",
  UNPROCESSABLE = "UNPROCESSABLE",

  // 의존성
  FAILED_DEPENDENCY = "FAILED_DEPENDENCY",

  // 서버
  INTERNAL_ERROR = "INTERNAL_ERROR",
  SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE",
}

/**
 * HTTP 상태 코드 매핑
 */
export const ERROR_STATUS_MAP: Record<ErrorCode, number> = {
  [ErrorCode.UNAUTHORIZED]: 401,
  [ErrorCode.FORBIDDEN]: 403,
  [ErrorCode.NOT_FOUND]: 404,
  [ErrorCode.CONFLICT]: 409,
  [ErrorCode.VALIDATION_ERROR]: 422,
  [ErrorCode.UNPROCESSABLE]: 422,
  [ErrorCode.FAILED_DEPENDENCY]: 424,
  [ErrorCode.INTERNAL_ERROR]: 500,
  [ErrorCode.SERVICE_UNAVAILABLE]: 503,
};
