'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { formatPercent } from '@/lib/utils'

export default function RebalancePage() {
  const [isEditing, setIsEditing] = useState(false)
  const queryClient = useQueryClient()

  const { data: targets, isLoading } = useQuery({
    queryKey: ['rebalance-targets'],
    queryFn: () => apiClient.getRebalanceTargets(),
  })

  const saveMutation = useMutation({
    mutationFn: (newTargets: any[]) => apiClient.saveRebalanceTargets(newTargets),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rebalance-targets'] })
      setIsEditing(false)
      alert('저장되었습니다')
    },
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">리밸런싱</h1>
          <p className="text-muted-foreground">목표 비중 설정 및 제안</p>
        </div>
        <Button
          onClick={() => setIsEditing(!isEditing)}
          variant={isEditing ? 'outline' : 'default'}
        >
          {isEditing ? '취소' : '편집'}
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>목표 비중</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div>로딩 중...</div>
          ) : targets?.items && targets.items.length > 0 ? (
            <div className="space-y-4">
              {targets.items.map((target: any) => (
                <div key={target.id} className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{target.asset_class}</p>
                    <p className="text-sm text-muted-foreground">
                      범위: {target.scope}
                      {target.account_id && ` | 계좌: #${target.account_id}`}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">{formatPercent(target.target_pct)}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              목표 비중이 설정되지 않았습니다
            </p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>리밸런싱 제안</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            목표 비중을 설정하고 "제안 생성" 버튼을 클릭하세요
          </p>
          <Button className="mt-4" disabled>
            제안 생성 (준비 중)
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}

