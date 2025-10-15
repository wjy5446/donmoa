'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { useSearchParams } from 'next/navigation'

export default function AuthCodeError() {
  const searchParams = useSearchParams()
  const error = searchParams.get('error')
  const errorCode = searchParams.get('error_code')
  const errorDescription = searchParams.get('error_description')

  const getErrorMessage = () => {
    if (errorCode === 'otp_expired') {
      return {
        title: '인증 링크 만료',
        message: '이메일 인증 링크가 만료되었습니다. 새로운 링크를 요청해주세요.',
        action: '새로운 인증 링크 요청'
      }
    }

    if (error === 'access_denied') {
      return {
        title: '인증 거부',
        message: '이메일 인증이 거부되었습니다. 다시 시도해주세요.',
        action: '다시 시도'
      }
    }

    return {
      title: '인증 오류',
      message: '이메일 인증 중 오류가 발생했습니다.',
      action: '로그인 페이지로 돌아가기'
    }
  }

  const errorInfo = getErrorMessage()

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/50">
      <div className="w-full max-w-md rounded-lg border bg-card p-8 shadow-sm">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">{errorInfo.title}</h1>
          <p className="text-muted-foreground mb-6">
            {errorInfo.message}
          </p>

          {/* 디버그 정보 (개발 환경에서만) */}
          {process.env.NODE_ENV === 'development' && (
            <div className="mb-6 rounded-md bg-muted p-3 text-left text-sm">
              <p><strong>Error:</strong> {error}</p>
              <p><strong>Code:</strong> {errorCode}</p>
              <p><strong>Description:</strong> {errorDescription}</p>
            </div>
          )}

          <div className="space-y-3">
            {errorCode === 'otp_expired' ? (
              <Link href="/auth/signup">
                <Button className="w-full">
                  새로운 인증 링크 요청
                </Button>
              </Link>
            ) : (
              <Link href="/auth/login">
                <Button className="w-full">
                  로그인 페이지로 돌아가기
                </Button>
              </Link>
            )}

            <Link href="/auth/signup">
              <Button variant="outline" className="w-full">
                회원가입 다시 시도
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
