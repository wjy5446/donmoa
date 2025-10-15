'use client'

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { formatMoney, formatPercent, formatDate } from '@/lib/utils'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'

export default function DashboardPage() {
  const today = new Date().toISOString().split('T')[0]

  const { data: summary, isLoading } = useQuery({
    queryKey: ['dashboard-summary', today],
    queryFn: () => apiClient.getDashboardSummary(today),
  })

  if (isLoading) {
    return <div>로딩 중...</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">대시보드</h1>
        <p className="text-muted-foreground">
          {formatDate(today)} 기준 자산 현황
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">총 자산</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {summary?.total_equity
                ? formatMoney(summary.total_equity.amount_minor, summary.total_equity.currency)
                : '₩0'}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">월 수익률</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {summary?.monthly_return?.m1
                ? formatPercent(summary.monthly_return.m1)
                : '-'}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">YTD 수익률</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {summary?.monthly_return?.ytd
                ? formatPercent(summary.monthly_return.ytd)
                : '-'}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">계좌 수</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {summary?.by_account?.length || 0}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Allocations */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>계좌별 비중</CardTitle>
          </CardHeader>
          <CardContent>
            {summary?.by_account && summary.by_account.length > 0 ? (
              <div className="space-y-4">
                {summary.by_account.map((item: any) => (
                  <div key={item.account_id} className="flex items-center">
                    <div className="flex-1">
                      <p className="text-sm font-medium">계좌 #{item.account_id}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium">{formatPercent(item.weight)}</p>
                      <p className="text-xs text-muted-foreground">
                        {formatMoney(item.equity_minor, 'KRW')}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">데이터가 없습니다</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>자산 클래스별 비중</CardTitle>
          </CardHeader>
          <CardContent>
            {summary?.by_asset_class && summary.by_asset_class.length > 0 ? (
              <div className="space-y-4">
                {summary.by_asset_class.map((item: any) => (
                  <div key={item.asset_class} className="flex items-center">
                    <div className="flex-1">
                      <p className="text-sm font-medium">{item.asset_class}</p>
                    </div>
                    <div className="text-sm font-medium">{formatPercent(item.weight)}</div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">데이터가 없습니다</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Notes */}
      {summary?.notes && summary.notes.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>알림</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {summary.notes.map((note: string, i: number) => (
                <li key={i} className="text-sm text-muted-foreground">
                  • {note}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

