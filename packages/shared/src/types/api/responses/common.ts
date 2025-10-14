/**
 * Common API Response Types
 */

/**
 * 생성 응답
 */
export interface CreatedResponse {
  id: number | string;
  created: boolean;
}

/**
 * 수정 응답
 */
export interface UpdatedResponse {
  updated: boolean;
}

/**
 * 삭제 응답
 */
export interface DeletedResponse {
  deleted: boolean;
}

/**
 * 저장 응답
 */
export interface SavedResponse {
  saved: boolean;
}
