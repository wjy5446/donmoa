'use client'

import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { apiClient } from '@/lib/api-client'
import { formatDate } from '@/lib/utils'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

export default function SnapshotsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['snapshots'],
    queryFn: () => apiClient.getSnapshots(),
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">스냅샷</h1>
          <p className="text-muted-foreground">업로드된 스냅샷 목록</p>
        </div>
        <Link href="/dashboard/snapshots/upload">
          <Button>스냅샷 업로드</Button>
        </Link>
      </div>

      {isLoading ? (
        <div>로딩 중...</div>
      ) : (
        <div className="space-y-4">
          {data?.items && data.items.length > 0 ? (
            data.items.map((snapshot: any) => (
              <Card key={snapshot.id}>
                <CardContent className="flex items-center justify-between p-6">
                  <div>
                    <p className="font-medium">{formatDate(snapshot.date)}</p>
                    <p className="text-sm text-muted-foreground">
                      출처: {snapshot.source} | 현금: {snapshot.line_counts?.cash || 0}건,
                      포지션: {snapshot.line_counts?.positions || 0}건, 거래:{' '}
                      {snapshot.line_counts?.transactions || 0}건
                    </p>
                    {snapshot.notes && (
                      <p className="text-sm text-muted-foreground mt-1">{snapshot.notes}</p>
                    )}
                  </div>
                  <Link href={`/dashboard/snapshots/${snapshot.id}`}>
                    <Button variant="outline" size="sm">
                      상세보기
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            ))
          ) : (
            <Card>
              <CardContent className="p-6 text-center text-muted-foreground">
                스냅샷이 없습니다. 먼저 데이터를 업로드하세요.
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}

