'use client'

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'

export default function PortfolioPage() {
  const { data: accounts, isLoading } = useQuery({
    queryKey: ['accounts'],
    queryFn: () => apiClient.getAccounts(),
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">포트폴리오</h1>
        <p className="text-muted-foreground">계좌 및 보유 종목</p>
      </div>

      {isLoading ? (
        <div>로딩 중...</div>
      ) : (
        <div className="space-y-4">
          {accounts?.items && accounts.items.length > 0 ? (
            accounts.items.map((account: any) => (
              <Card key={account.id}>
                <CardHeader>
                  <CardTitle className="text-lg">{account.name}</CardTitle>
                  <p className="text-sm text-muted-foreground">
                    {account.institution?.name} | {account.type} | {account.currency}
                  </p>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    상세 정보는 준비 중입니다
                  </p>
                </CardContent>
              </Card>
            ))
          ) : (
            <Card>
              <CardContent className="p-6 text-center text-muted-foreground">
                계좌가 없습니다
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}

