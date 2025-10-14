import { createServerClient } from '@supabase/ssr'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function GET(request: NextRequest) {
  const { searchParams, origin } = new URL(request.url)
  const code = searchParams.get('code')
  const error = searchParams.get('error')
  const errorCode = searchParams.get('error_code')
  const errorDescription = searchParams.get('error_description')

  // 에러가 있는 경우 에러 페이지로 리다이렉트
  if (error) {
    const errorUrl = new URL('/auth/auth-code-error', origin)
    errorUrl.searchParams.set('error', error)
    if (errorCode) errorUrl.searchParams.set('error_code', errorCode)
    if (errorDescription) errorUrl.searchParams.set('error_description', errorDescription)

    return NextResponse.redirect(errorUrl)
  }

  const next = searchParams.get('next') ?? '/dashboard'

  if (code) {
    const supabase = createServerClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        {
          auth: {
            flowType: 'pkce' // PKCE 플로우 활성화
          },
          cookies: {
            getAll() {
              return request.cookies.getAll()
            },
            setAll(cookiesToSet) {
              cookiesToSet.forEach(({ name, value, options }) => {
                request.cookies.set(name, value)
              })
            },
          },
    }
    )

    const { error } = await supabase.auth.exchangeCodeForSession(code)
    if (!error) {
      const forwardedHost = request.headers.get('x-forwarded-host')
      const isLocalEnv = process.env.NODE_ENV === 'development'

      if (isLocalEnv) {
        return NextResponse.redirect(`${origin}${next}`)
      } else if (forwardedHost) {
        return NextResponse.redirect(`https://${forwardedHost}${next}`)
      } else {
        return NextResponse.redirect(`${origin}${next}`)
      }
    } else {
      // 코드 교환 실패 시 에러 페이지로 리다이렉트
      const errorUrl = new URL('/auth/auth-code-error', origin)
      errorUrl.searchParams.set('error', 'code_exchange_failed')
      errorUrl.searchParams.set('error_description', error.message)

      return NextResponse.redirect(errorUrl)
    }
  }

  // 코드가 없는 경우 에러 페이지로 리다이렉트
  const errorUrl = new URL('/auth/auth-code-error', origin)
  errorUrl.searchParams.set('error', 'no_code')
  errorUrl.searchParams.set('error_description', 'No authentication code provided')

  return NextResponse.redirect(errorUrl)
}
