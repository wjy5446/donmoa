/**
 * Snapshot Service
 * 비즈니스 로직 레이어
 */

import { SupabaseClient } from "@supabase/supabase-js";
import { toMoneyMinor, toQtyNano, toPriceNano } from "@donmoa/shared";
import { SnapshotRepository } from "./repository";
import { SnapshotCommitInput } from "./validator";
import { logger } from "../../utils/logger";

export class SnapshotService {
  private repository: SnapshotRepository;

  constructor(private db: SupabaseClient) {
    this.repository = new SnapshotRepository(db);
  }

  /**
   * 스냅샷 커밋 (원샷)
   * 1. 계좌/종목 매핑/생성
   * 2. 동일 날짜 스냅샷 존재 시 삭제 (교체)
   * 3. 스냅샷 헤더 생성
   * 4. 라인 아이템 삽입
   */
  async commitSnapshot(userId: string, input: SnapshotCommitInput) {
    const warnings: string[] = [];
    const errors: string[] = [];

    try {
      // 1. 계좌 매핑 처리
      const accountMap = await this.resolveAccounts(
        userId,
        input,
        input.options?.create_missing_accounts ?? true,
        warnings
      );

      // 2. 종목 매핑 처리
      const instrumentMap = await this.resolveInstruments(
        input,
        input.options?.create_missing_instruments ?? true,
        warnings
      );

      // 3. 동일 날짜 스냅샷 확인 및 교체
      const existingSnapshot = await this.repository.findSnapshotByDate(
        userId,
        input.snapshot_date
      );

      if (existingSnapshot) {
        if (input.options?.replace_same_date !== false) {
          logger.info(`Replacing existing snapshot for ${input.snapshot_date}`);
          await this.repository.deleteSnapshot(existingSnapshot.id);
        } else {
          throw new Error(
            `Snapshot for ${input.snapshot_date} already exists. Set replace_same_date: true to overwrite.`
          );
        }
      }

      // 4. 스냅샷 헤더 생성
      const snapshot = await this.repository.createSnapshot({
        user_id: userId,
        snapshot_date: input.snapshot_date,
        source: input.source,
        notes: input.notes,
      });

      // 5. 현금 라인 삽입
      const cashLines = input.cash
        .map((item) => {
          const accountId = accountMap.get(item.account_external_id);
          if (!accountId) {
            warnings.push(`Account not found: ${item.account_external_id}`);
            return null;
          }
          return {
            snapshot_id: snapshot.id,
            account_id: accountId,
            currency: item.currency,
            amount_minor: toMoneyMinor(item.amount, item.currency),
          };
        })
        .filter((line): line is NonNullable<typeof line> => line !== null);

      await this.repository.insertCashLines(cashLines);

      // 6. 포지션 라인 삽입
      const positionLines = input.positions
        .map((item) => {
          const accountId = accountMap.get(item.account_external_id);
          const instrumentId = instrumentMap.get(item.symbol);

          if (!accountId) {
            warnings.push(`Account not found: ${item.account_external_id}`);
            return null;
          }
          if (!instrumentId) {
            warnings.push(`Instrument not found: ${item.symbol}`);
            return null;
          }

          return {
            snapshot_id: snapshot.id,
            account_id: accountId,
            instrument_id: instrumentId,
            qty_nano: toQtyNano(item.qty),
            avg_cost: item.avg_cost,
            currency: item.currency,
          };
        })
        .filter((line): line is NonNullable<typeof line> => line !== null);

      await this.repository.insertPositionLines(positionLines);

      // 7. 거래 라인 삽입
      const transactionLines = input.transactions
        .map((item) => {
          const accountId = accountMap.get(item.account_external_id);
          if (!accountId) {
            warnings.push(`Account not found for transaction: ${item.account_external_id}`);
            return null;
          }

          const instrumentId = item.symbol ? instrumentMap.get(item.symbol) : undefined;

          return {
            snapshot_id: snapshot.id,
            account_id: accountId,
            trade_datetime: item.trade_datetime || new Date().toISOString(),
            settle_date: item.settle_date,
            type: item.type,
            instrument_id: instrumentId,
            qty_nano: item.qty !== undefined ? toQtyNano(item.qty) : undefined,
            price_nano: item.price !== undefined ? toPriceNano(item.price) : undefined,
            amount_minor: item.amount !== undefined ? toMoneyMinor(item.amount, item.currency) : undefined,
            currency: item.currency,
            note: item.note,
          };
        })
        .filter((line): line is NonNullable<typeof line> => line !== null);

      await this.repository.insertTransactionLines(transactionLines);

      // 8. 경고/에러 로그 기록
      if (warnings.length > 0) {
        await this.repository.addIngestLog(
          snapshot.id,
          "warning",
          "Snapshot committed with warnings",
          { warnings }
        );
      }

      return {
        snapshot_id: snapshot.id,
        date: snapshot.snapshot_date,
        lines: {
          cash: cashLines.length,
          positions: positionLines.length,
          transactions: transactionLines.length,
        },
        warnings,
        errors,
      };
    } catch (error) {
      logger.error("Snapshot commit failed", error);
      throw error;
    }
  }

  /**
   * 계좌 매핑 처리
   */
  private async resolveAccounts(
    userId: string,
    input: SnapshotCommitInput,
    createMissing: boolean,
    warnings: string[]
  ): Promise<Map<string, number>> {
    const accountMap = new Map<string, number>();

    // 사용자 정의 매핑 우선 적용
    if (input.mapping?.account_map) {
      for (const [externalId, accountId] of Object.entries(input.mapping.account_map)) {
        accountMap.set(externalId, accountId);
      }
    }

    // 매핑되지 않은 계좌 처리
    const unmappedAccounts = new Set<string>();
    [...input.cash, ...input.positions, ...input.transactions].forEach((item) => {
      const externalId = item.account_external_id;
      if (!accountMap.has(externalId)) {
        unmappedAccounts.add(externalId);
      }
    });

    // DB에서 외부 ID 매핑 조회
    if (unmappedAccounts.size > 0) {
      const { data, error } = await this.db
        .from("account_external_ids")
        .select("external_id, account_id, accounts!inner(user_id)")
        .in("external_id", Array.from(unmappedAccounts))
        .eq("accounts.user_id", userId);

      if (!error && data) {
        data.forEach((row: { external_id: string; account_id: number }) => {
          accountMap.set(row.external_id, row.account_id);
          unmappedAccounts.delete(row.external_id);
        });
      }
    }

    // 여전히 매핑되지 않은 계좌 처리
    if (unmappedAccounts.size > 0 && createMissing) {
      for (const externalId of unmappedAccounts) {
        // 새 계좌 생성 (간단히 처리)
        const { data, error } = await this.db
          .from("accounts")
          .insert({
            user_id: userId,
            name: externalId,
            type: "other",
            currency: "KRW",
          })
          .select()
          .single();

        if (!error && data) {
          accountMap.set(externalId, data.id);
          // 외부 ID 매핑 추가
          await this.db.from("account_external_ids").insert({
            account_id: data.id,
            external_id: externalId,
            source: input.source,
          });
          warnings.push(`Created new account: ${externalId}`);
        }
      }
    }

    return accountMap;
  }

  /**
   * 종목 매핑 처리
   */
  private async resolveInstruments(
    input: SnapshotCommitInput,
    createMissing: boolean,
    warnings: string[]
  ): Promise<Map<string, number>> {
    const instrumentMap = new Map<string, number>();

    // 사용자 정의 매핑 우선 적용
    if (input.mapping?.instrument_map) {
      for (const [symbol, instrumentId] of Object.entries(input.mapping.instrument_map)) {
        instrumentMap.set(symbol, instrumentId);
      }
    }

    // 매핑되지 않은 종목 수집
    const unmappedSymbols = new Set<string>();
    [...input.positions, ...input.transactions].forEach((item) => {
      const symbol = "symbol" in item ? item.symbol : undefined;
      if (symbol && !instrumentMap.has(symbol)) {
        unmappedSymbols.add(symbol);
      }
    });

    // DB에서 종목 조회
    if (unmappedSymbols.size > 0) {
      const { data, error } = await this.db
        .from("instruments")
        .select("id, symbol")
        .in("symbol", Array.from(unmappedSymbols));

      if (!error && data) {
        data.forEach((row: { id: number; symbol: string }) => {
          instrumentMap.set(row.symbol, row.id);
          unmappedSymbols.delete(row.symbol);
        });
      }
    }

    // 여전히 매핑되지 않은 종목 처리
    if (unmappedSymbols.size > 0 && createMissing) {
      for (const symbol of unmappedSymbols) {
        const { data, error } = await this.db
          .from("instruments")
          .insert({
            symbol,
            name: symbol,
            asset_class: "other",
            currency: "KRW",
          })
          .select()
          .single();

        if (!error && data) {
          instrumentMap.set(symbol, data.id);
          warnings.push(`Created new instrument: ${symbol}`);
        }
      }
    }

    return instrumentMap;
  }

  /**
   * 스냅샷 목록 조회
   */
  async listSnapshots(
    userId: string,
    options: {
      from?: string;
      to?: string;
      limit?: number;
      cursor?: string;
    }
  ) {
    return await this.repository.listSnapshots(userId, options);
  }

  /**
   * 스냅샷 상세 조회
   */
  async getSnapshotById(snapshotId: number, userId: string) {
    const snapshot = await this.repository.findSnapshotById(snapshotId);

    if (!snapshot || snapshot.user_id !== userId) {
      return null;
    }

    const [cashCount, positionsCount, transactionsCount] = await Promise.all([
      this.repository["countCashLines"](snapshotId),
      this.repository["countPositionLines"](snapshotId),
      this.repository["countTransactionLines"](snapshotId),
    ]);

    return {
      id: snapshot.id,
      date: snapshot.snapshot_date,
      source: snapshot.source,
      notes: snapshot.notes,
      counts: {
        cash: cashCount,
        positions: positionsCount,
        transactions: transactionsCount,
      },
    };
  }
}
