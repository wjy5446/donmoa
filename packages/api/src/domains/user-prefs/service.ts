/**
 * User Preferences Service
 * 비즈니스 로직 레이어
 */

import { SupabaseClient } from "@supabase/supabase-js";
import { UserPrefsRepository } from "./repository";
import {
  CategoryCreateInput,
  CategoryUpdateInput,
  FavoriteToggleInput,
  FavoritesQuery,
  DashboardPrefsInput,
} from "./validator";

export class UserPrefsService {
  private repository: UserPrefsRepository;

  constructor(private db: SupabaseClient) {
    this.repository = new UserPrefsRepository(db);
  }

  /**
   * 카테고리 목록 조회
   */
  async listCategories(userId: string) {
    const categories = await this.repository.listCategories(userId);
    return { items: categories };
  }

  /**
   * 카테고리 생성
   */
  async createCategory(userId: string, input: CategoryCreateInput) {
    const category = await this.repository.createCategory({
      user_id: userId,
      ...input,
    });

    return { id: category.id, created: true };
  }

  /**
   * 카테고리 수정
   */
  async updateCategory(categoryId: number, input: CategoryUpdateInput) {
    await this.repository.updateCategory(categoryId, input);
    return { updated: true };
  }

  /**
   * 카테고리 삭제
   */
  async deleteCategory(categoryId: number) {
    await this.repository.deleteCategory(categoryId);
    return { deleted: true };
  }

  /**
   * 즐겨찾기 토글
   */
  async toggleFavorite(userId: string, input: FavoriteToggleInput) {
    await this.repository.toggleFavorite(userId, input.instrument_id, input.star);
    return { starred: input.star };
  }

  /**
   * 즐겨찾기 목록 조회
   */
  async listFavorites(userId: string, query: FavoritesQuery) {
    const favorites = await this.repository.listFavorites(
      userId,
      query.held,
      query.asset_class
    );

    return {
      items: favorites.map((fav: any) => ({
        instrument: fav.instruments,
        starred_at: fav.starred_at,
        holding: false, // TODO: 실제 보유 여부 확인
        perf: {
          pnl_minor: "0",
          return_pct: 0,
        },
      })),
    };
  }

  /**
   * 대시보드 설정 조회
   */
  async getDashboardPrefs(userId: string) {
    const prefs = await this.repository.getDashboardPrefs(userId);

    if (!prefs) {
      // 기본값 반환
      return {
        cards: ["summary", "timeseries", "allocations"],
        layout: "grid-2",
      };
    }

    return prefs.layout;
  }

  /**
   * 대시보드 설정 저장
   */
  async saveDashboardPrefs(userId: string, input: DashboardPrefsInput) {
    await this.repository.saveDashboardPrefs(userId, input as any);
    return { saved: true };
  }
}

