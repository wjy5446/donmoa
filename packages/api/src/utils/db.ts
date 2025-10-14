/**
 * Supabase 클라이언트
 */

import { createClient, SupabaseClient } from "@supabase/supabase-js";
import { config } from "../config";

/**
 * Supabase 클라이언트 (서비스 역할)
 * RLS 우회 가능 - 서버 사이드 전용
 */
export const supabaseAdmin: SupabaseClient = createClient(
  config.supabase.url,
  config.supabase.serviceRoleKey,
  {
    auth: {
      autoRefreshToken: false,
      persistSession: false,
    },
  }
);

/**
 * Supabase 클라이언트 (익명 키)
 * RLS 적용됨 - 사용자 토큰 필요
 */
export const supabaseClient: SupabaseClient = createClient(
  config.supabase.url,
  config.supabase.anonKey
);

/**
 * 사용자 인증 토큰으로 Supabase 클라이언트 생성
 */
export function createUserClient(accessToken: string): SupabaseClient {
  return createClient(config.supabase.url, config.supabase.anonKey, {
    global: {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    },
  });
}
