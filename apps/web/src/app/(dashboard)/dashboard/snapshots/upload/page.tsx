'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { createClient } from '@/lib/supabase'

export default function SnapshotUploadPage() {
  const [file, setFile] = useState<File | null>(null)
  const [snapshotDate, setSnapshotDate] = useState(
    new Date().toISOString().split('T')[0]
  )
  const [notes, setNotes] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [accessToken, setAccessToken] = useState<string | null>(null)
  const router = useRouter()

  // Supabase에서 액세스 토큰 가져오기
  useEffect(() => {
    const getAccessToken = async () => {
      const supabase = createClient()
      const { data: { session } } = await supabase.auth.getSession()

      if (session?.access_token) {
        setAccessToken(session.access_token)
      }
    }

    getAccessToken()
  }, [])

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!file) {
      setError('파일을 선택해주세요')
      return
    }

    if (!accessToken) {
      setError('로그인이 필요합니다')
      return
    }

    setLoading(true)
    setError('')

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('snapshot_date', snapshotDate)
      if (notes) formData.append('notes', notes)

      const response = await fetch('http://localhost:3001/v1/snapshots/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`, // ✅ 인증 토큰 추가
        },
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.error?.message || `업로드 실패 (${response.status})`)
      }

      alert('스냅샷이 업로드되었습니다')
      router.push('/dashboard/snapshots')
    } catch (err: any) {
      setError(err.message || '업로드에 실패했습니다')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">스냅샷 업로드</h1>
        <p className="text-muted-foreground">
          CSV, Excel, MHTML 파일을 업로드하세요
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>파일 선택</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleUpload} className="space-y-4">
            <div>
              <label htmlFor="file" className="block text-sm font-medium mb-2">
                파일
              </label>
              <input
                id="file"
                type="file"
                accept=".csv,.xlsx,.mhtml"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="w-full"
                required
              />
            </div>

            <div>
              <label htmlFor="date" className="block text-sm font-medium mb-2">
                스냅샷 날짜
              </label>
              <input
                id="date"
                type="date"
                value={snapshotDate}
                onChange={(e) => setSnapshotDate(e.target.value)}
                className="w-full rounded-md border border-input bg-background px-3 py-2"
                required
              />
            </div>

            <div>
              <label htmlFor="notes" className="block text-sm font-medium mb-2">
                메모 (선택)
              </label>
              <textarea
                id="notes"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="w-full rounded-md border border-input bg-background px-3 py-2"
                rows={3}
                placeholder="메모를 입력하세요"
              />
            </div>

            {error && (
              <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
                {error}
              </div>
            )}

            <div className="flex gap-2">
              <Button type="submit" disabled={loading || !accessToken}>
                {loading ? '업로드 중...' : '업로드'}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => router.back()}
              >
                취소
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>지원 파일 형식</CardTitle>
        </CardHeader>
        <CardContent className="text-sm space-y-2">
          <p>• <strong>CSV</strong>: 표준 CSV 형식</p>
          <p>• <strong>Excel</strong>: .xlsx 형식 (뱅크샐러드, 수동 입력)</p>
          <p>• <strong>MHTML</strong>: 도미노 증권 파일</p>
        </CardContent>
      </Card>
    </div>
  )
}
