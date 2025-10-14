/**
 * Analytics Service
 * 비즈니스 로직 레이어
 */

import { SupabaseClient } from "@supabase/supabase-js";
import { AnalyticsRepository } from "./repository";
import {
  DashboardSummaryQuery,
  TimeseriesQuery,
  AllocationsQuery,
  CashflowQuery,
} from "./validator";

export class AnalyticsService {
  private repository: AnalyticsRepository;

  constructor(private db: SupabaseClient) {
    this.repository = new AnalyticsRepository(db);
  }

  /**
   * 대시보드 요약
   */
  async getDashboardSummary(userId: string, query: DashboardSummaryQuery) {
    const snapshotId = await this.repository.getSnapshotIdByDate(userId, query.date);

    if (!snapshotId) {
      return {
        as_of: query.date,
        total_equity: { amount_minor: 0n, currency: "KRW" },
        by_account: [],
        by_asset_class: [],
        notes: ["No snapshot found for this date"],
      };
    }

    const { cash, positions } = await this.repository.getAccountSummary(snapshotId);

    // 계좌별 집계 (간단히 현금만)
    const accountMap = new Map<number, bigint>();
    cash.forEach((item: any) => {
      if (item.currency === "KRW") {
        const current = accountMap.get(item.account_id) || 0n;
        accountMap.set(item.account_id, current + BigInt(item.amount_minor));
      }
    });

    const byAccount = Array.from(accountMap.entries()).map(([accountId, amount]) => ({
      account_id: accountId,
      weight: 0, // TODO: 전체 대비 비중 계산
      equity_minor: amount,
    }));

    // 총액 계산
    const totalEquityMinor = byAccount.reduce((sum, item) => sum + item.equity_minor, 0n);

    // 비중 계산
    byAccount.forEach((item) => {
      item.weight = totalEquityMinor > 0n ? Number(item.equity_minor) / Number(totalEquityMinor) : 0;
    });

    // 자산 클래스별 집계
    const assetClassSummary = await this.repository.getAssetClassSummary(snapshotId);
    const assetClassMap = new Map<string, number>();

    assetClassSummary.forEach((item: any) => {
      const assetClass = item.instruments?.asset_class || "other";
      assetClassMap.set(assetClass, (assetClassMap.get(assetClass) || 0) + 1);
    });

    const byAssetClass = Array.from(assetClassMap.entries()).map(([assetClass, count]) => ({
      asset_class: assetClass,
      weight: count / assetClassSummary.length,
    }));

    return {
      as_of: query.date,
      total_equity: {
        amount_minor: totalEquityMinor.toString(),
        currency: "KRW",
      },
      by_account: byAccount.map((item) => ({
        ...item,
        equity_minor: item.equity_minor.toString(),
      })),
      by_asset_class: byAssetClass,
    };
  }

  /**
   * 시계열 데이터
   */
  async getTimeseries(userId: string, query: TimeseriesQuery) {
    const snapshots = await this.repository.getSnapshotsTimeseries(
      userId,
      query.from,
      query.to
    );

    // 각 스냅샷의 총액 계산 (간단히 구현)
    const series = await Promise.all(
      snapshots.map(async (snapshot: any) => {
        const { cash } = await this.repository.getAccountSummary(snapshot.id);

        const totalKRW = cash
          .filter((item: any) => item.currency === "KRW")
          .reduce((sum: number, item: any) => sum + Number(item.amount_minor), 0);

        return {
          date: snapshot.snapshot_date,
          value: totalKRW / 1, // KRW는 스케일 1
        };
      })
    );

    return {
      metric: query.metric,
      interval: query.interval,
      series,
    };
  }

  /**
   * 비중 데이터
   */
  async getAllocations(userId: string, query: AllocationsQuery) {
    const snapshotId = await this.repository.getSnapshotIdByDate(userId, query.date);

    if (!snapshotId) {
      return {
        date: query.date,
        group: query.group,
        items: [],
      };
    }

    if (query.group === "account") {
      const { cash } = await this.repository.getAccountSummary(snapshotId);

      const accountMap = new Map<number, bigint>();
      cash.forEach((item: any) => {
        if (item.currency === "KRW") {
          const current = accountMap.get(item.account_id) || 0n;
          accountMap.set(item.account_id, current + BigInt(item.amount_minor));
        }
      });

      const total = Array.from(accountMap.values()).reduce((sum, val) => sum + val, 0n);

      const items = Array.from(accountMap.entries()).map(([accountId, amount]) => ({
        key: accountId.toString(),
        weight: total > 0n ? Number(amount) / Number(total) : 0,
        equity_minor: amount.toString(),
      }));

      return {
        date: query.date,
        group: query.group,
        items,
      };
    } else if (query.group === "asset_class") {
      const assetClassSummary = await this.repository.getAssetClassSummary(snapshotId);

      const assetClassMap = new Map<string, number>();
      assetClassSummary.forEach((item: any) => {
        const assetClass = item.instruments?.asset_class || "other";
        assetClassMap.set(assetClass, (assetClassMap.get(assetClass) || 0) + 1);
      });

      const total = assetClassSummary.length;

      const items = Array.from(assetClassMap.entries()).map(([assetClass, count]) => ({
        key: assetClass,
        weight: count / total,
        equity_minor: "0", // TODO: 실제 평가액 계산
      }));

      return {
        date: query.date,
        group: query.group,
        items,
      };
    }

    return {
      date: query.date,
      group: query.group,
      items: [],
    };
  }

  /**
   * 현금흐름 요약
   */
  async getCashflowSummary(userId: string, query: CashflowQuery) {
    const transactions = await this.repository.getCashflowTransactions(
      userId,
      query.from,
      query.to
    );

    // 월별 집계
    const monthlyMap = new Map<
      string,
      { income: bigint; expense: bigint; transfer: bigint }
    >();

    transactions.forEach((txn: any) => {
      const month = txn.trade_datetime.substring(0, 7); // YYYY-MM
      const amount = BigInt(txn.amount_minor || 0);

      if (!monthlyMap.has(month)) {
        monthlyMap.set(month, { income: 0n, expense: 0n, transfer: 0n });
      }

      const monthData = monthlyMap.get(month)!;

      if (["deposit", "dividend", "interest"].includes(txn.type)) {
        monthData.income += amount;
      } else if (txn.type === "withdraw") {
        monthData.expense += amount < 0n ? -amount : amount;
      } else if (txn.type === "transfer") {
        monthData.transfer += amount;
      }
    });

    const monthly = Array.from(monthlyMap.entries()).map(([month, data]) => ({
      month,
      income_minor: data.income.toString(),
      expense_minor: data.expense.toString(),
      transfer_minor: data.transfer.toString(),
      net_minor: (data.income - data.expense).toString(),
    }));

    return {
      period: { from: query.from, to: query.to },
      monthly: monthly.sort((a, b) => a.month.localeCompare(b.month)),
    };
  }

  /**
   * 배당 요약
   */
  async getDividendsSummary(userId: string, from: string, to: string) {
    const dividends = await this.repository.getDividends(userId, from, to);

    const instrumentMap = new Map<
      number,
      { name: string; total: bigint; count: number }
    >();

    let totalMinor = 0n;

    dividends.forEach((div: any) => {
      const amount = BigInt(div.amount_minor || 0);
      totalMinor += amount;

      if (!instrumentMap.has(div.instrument_id)) {
        instrumentMap.set(div.instrument_id, {
          name: div.instruments?.name || div.instruments?.symbol || "Unknown",
          total: 0n,
          count: 0,
        });
      }

      const data = instrumentMap.get(div.instrument_id)!;
      data.total += amount;
      data.count += 1;
    });

    const byInstrument = Array.from(instrumentMap.entries()).map(([instrumentId, data]) => ({
      instrument_id: instrumentId,
      instrument_name: data.name,
      amount_minor: data.total.toString(),
      count: data.count,
    }));

    return {
      period: { from, to },
      total_minor: totalMinor.toString(),
      currency: "KRW", // TODO: 다중 통화 지원
      by_instrument: byInstrument.sort((a, b) => b.count - a.count),
    };
  }
}
