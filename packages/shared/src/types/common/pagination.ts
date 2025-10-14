/**
 * 페이지네이션 요청 파라미터
 */
export interface PaginationParams {
  limit?: number;
  cursor?: string;
}

/**
 * 페이지네이션 응답 메타데이터
 */
export interface PaginationMeta {
  next_cursor: string | null;
  has_more: boolean;
}

/**
 * 페이지네이션 응답 타입
 */
export interface PaginatedResponse<T> {
  items: T[];
  next_cursor: string | null;
}
