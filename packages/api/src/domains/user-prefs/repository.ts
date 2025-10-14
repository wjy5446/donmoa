/**
 * User Preferences Repository
 * DB 접근 레이어
 */

import { SupabaseClient } from "@supabase/supabase-js";

export class UserPrefsRepository {
  constructor(private db: SupabaseClient) {}

  /**
   * 카테고리 목록 조회
   */
  async listCategories(userId: string) {
    const { data, error } = await this.db
      .from("categories")
      .select("*")
      .eq("user_id", userId)
      .order("created_at", { ascending: false });

    if (error) throw error;
    return data || [];
  }

  /**
   * 카테고리 생성
   */
  async createCategory(data: {
    user_id: string;
    name: string;
    parent_id?: number;
    kind?: string;
  }) {
    const { data: category, error } = await this.db
      .from("categories")
      .insert(data)
      .select()
      .single();

    if (error) throw error;
    return category;
  }

  /**
   * 카테고리 수정
   */
  async updateCategory(
    categoryId: number,
    updates: {
      name?: string;
      parent_id?: number;
    }
  ) {
    const { error } = await this.db
      .from("categories")
      .update(updates)
      .eq("id", categoryId);

    if (error) throw error;
  }

  /**
   * 카테고리 삭제
   */
  async deleteCategory(categoryId: number) {
    const { error } = await this.db
      .from("categories")
      .delete()
      .eq("id", categoryId);

    if (error) throw error;
  }

  /**
   * 즐겨찾기 토글
   */
  async toggleFavorite(userId: string, instrumentId: number, star: boolean) {
    if (star) {
      // 추가
      const { error } = await this.db.from("favorites").insert({
        user_id: userId,
        instrument_id: instrumentId,
      });

      if (error && error.code !== "23505") throw error; // 중복 무시
    } else {
      // 제거
      const { error } = await this.db
        .from("favorites")
        .delete()
        .eq("user_id", userId)
        .eq("instrument_id", instrumentId);

      if (error) throw error;
    }
  }

  /**
   * 즐겨찾기 목록 조회
   */
  async listFavorites(userId: string, held?: boolean, assetClass?: string) {
    let query = this.db
      .from("favorites")
      .select("*, instruments(*)")
      .eq("user_id", userId)
      .order("starred_at", { ascending: false });

    // TODO: held 필터 (보유 여부)
    // TODO: assetClass 필터

    const { data, error } = await query;

    if (error) throw error;
    return data || [];
  }

  /**
   * 대시보드 설정 조회
   */
  async getDashboardPrefs(userId: string) {
    const { data, error } = await this.db
      .from("dashboard_prefs")
      .select("*")
      .eq("user_id", userId)
      .single();

    if (error && error.code !== "PGRST116") throw error;
    return data;
  }

  /**
   * 대시보드 설정 저장
   */
  async saveDashboardPrefs(userId: string, layout: Record<string, unknown>) {
    const { error } = await this.db
      .from("dashboard_prefs")
      .upsert({
        user_id: userId,
        layout,
      });

    if (error) throw error;
  }
}

