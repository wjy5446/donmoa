/**
 * Snapshot Repository
 * DB 접근 레이어
 */

import { SupabaseClient } from "@supabase/supabase-js";
import {
  Snapshot,
  SnapshotCash,
  SnapshotPosition,
  SnapshotTransaction,
  IngestLog,
  SnapshotSummary,
} from "@donmoa/shared";

export class SnapshotRepository {
  constructor(private db: SupabaseClient) {}

  /**
   * 스냅샷 생성
   */
  async createSnapshot(data: {
    user_id: string;
    snapshot_date: string;
    source: string;
    notes?: string;
  }): Promise<Snapshot> {
    const { data: snapshot, error } = await this.db
      .from("snapshots")
      .insert(data)
      .select()
      .single();

    if (error) throw error;
    return snapshot;
  }

  /**
   * 동일 날짜 스냅샷 조회
   */
  async findSnapshotByDate(
    userId: string,
    snapshotDate: string
  ): Promise<Snapshot | null> {
    const { data, error } = await this.db
      .from("snapshots")
      .select()
      .eq("user_id", userId)
      .eq("snapshot_date", snapshotDate)
      .single();

    if (error && error.code !== "PGRST116") throw error;
    return data;
  }

  /**
   * 스냅샷 ID로 조회
   */
  async findSnapshotById(snapshotId: number): Promise<Snapshot | null> {
    const { data, error } = await this.db
      .from("snapshots")
      .select()
      .eq("id", snapshotId)
      .single();

    if (error && error.code !== "PGRST116") throw error;
    return data;
  }

  /**
   * 스냅샷 삭제
   */
  async deleteSnapshot(snapshotId: number): Promise<void> {
    const { error } = await this.db
      .from("snapshots")
      .delete()
      .eq("id", snapshotId);

    if (error) throw error;
  }

  /**
   * 현금 라인 벌크 삽입
   */
  async insertCashLines(lines: Omit<SnapshotCash, "id" | "created_at">[]): Promise<void> {
    if (lines.length === 0) return;

    // BigInt를 문자열로 변환
    const serializedLines = lines.map((line) => ({
      ...line,
      amount_minor: line.amount_minor.toString(),
    }));

    const { error } = await this.db.from("snapshot_cash").insert(serializedLines);

    if (error) throw error;
  }

  /**
   * 포지션 라인 벌크 삽입
   */
  async insertPositionLines(
    lines: Omit<SnapshotPosition, "id" | "created_at">[]
  ): Promise<void> {
    if (lines.length === 0) return;

    const serializedLines = lines.map((line) => ({
      ...line,
      qty_nano: line.qty_nano.toString(),
    }));

    const { error } = await this.db.from("snapshot_positions").insert(serializedLines);

    if (error) throw error;
  }

  /**
   * 거래 라인 벌크 삽입
   */
  async insertTransactionLines(
    lines: Omit<SnapshotTransaction, "id" | "created_at">[]
  ): Promise<void> {
    if (lines.length === 0) return;

    const serializedLines = lines.map((line) => ({
      ...line,
      qty_nano: line.qty_nano?.toString(),
      price_nano: line.price_nano?.toString(),
      amount_minor: line.amount_minor?.toString(),
    }));

    const { error } = await this.db.from("snapshot_transactions").insert(serializedLines);

    if (error) throw error;
  }

  /**
   * 인제스트 로그 추가
   */
  async addIngestLog(
    snapshotId: number,
    level: "info" | "warning" | "error",
    message: string,
    context?: Record<string, unknown>
  ): Promise<void> {
    const { error } = await this.db.from("ingest_logs").insert({
      snapshot_id: snapshotId,
      level,
      message,
      context,
    });

    if (error) throw error;
  }

  /**
   * 스냅샷 목록 조회 (페이지네이션)
   */
  async listSnapshots(
    userId: string,
    options: {
      from?: string;
      to?: string;
      limit?: number;
      cursor?: string;
    }
  ): Promise<{ items: SnapshotSummary[]; next_cursor: string | null }> {
    let query = this.db
      .from("snapshots")
      .select("*")
      .eq("user_id", userId)
      .order("snapshot_date", { ascending: false })
      .order("created_at", { ascending: false });

    if (options.from) {
      query = query.gte("snapshot_date", options.from);
    }
    if (options.to) {
      query = query.lte("snapshot_date", options.to);
    }
    if (options.cursor) {
      query = query.lt("id", parseInt(options.cursor, 10));
    }

    const limit = Math.min(options.limit || 50, 200);
    query = query.limit(limit + 1);

    const { data, error } = await query;

    if (error) throw error;

    const hasMore = data.length > limit;
    const items = hasMore ? data.slice(0, limit) : data;
    const nextCursor = hasMore ? items[items.length - 1].id.toString() : null;

    // 라인 수 집계 (간단히 별도 쿼리)
    const summaries: SnapshotSummary[] = await Promise.all(
      items.map(async (snapshot) => {
        const [cashCount, positionsCount, transactionsCount] = await Promise.all([
          this.countCashLines(snapshot.id),
          this.countPositionLines(snapshot.id),
          this.countTransactionLines(snapshot.id),
        ]);

        return {
          id: snapshot.id,
          date: snapshot.snapshot_date,
          source: snapshot.source,
          notes: snapshot.notes,
          line_counts: {
            cash: cashCount,
            positions: positionsCount,
            transactions: transactionsCount,
          },
        };
      })
    );

    return { items: summaries, next_cursor: nextCursor };
  }

  /**
   * 현금 라인 수 집계
   */
  private async countCashLines(snapshotId: number): Promise<number> {
    const { count, error } = await this.db
      .from("snapshot_cash")
      .select("*", { count: "exact", head: true })
      .eq("snapshot_id", snapshotId);

    if (error) throw error;
    return count || 0;
  }

  /**
   * 포지션 라인 수 집계
   */
  private async countPositionLines(snapshotId: number): Promise<number> {
    const { count, error } = await this.db
      .from("snapshot_positions")
      .select("*", { count: "exact", head: true })
      .eq("snapshot_id", snapshotId);

    if (error) throw error;
    return count || 0;
  }

  /**
   * 거래 라인 수 집계
   */
  private async countTransactionLines(snapshotId: number): Promise<number> {
    const { count, error } = await this.db
      .from("snapshot_transactions")
      .select("*", { count: "exact", head: true })
      .eq("snapshot_id", snapshotId);

    if (error) throw error;
    return count || 0;
  }
}
