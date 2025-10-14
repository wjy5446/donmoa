import Link from 'next/link'
import { Button } from '@/components/ui/button'

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      {/* Hero Section */}
      <main className="flex-1">
        <section className="container flex flex-col items-center gap-6 pb-8 pt-6 md:py-10">
          <div className="flex max-w-[980px] flex-col items-center gap-2 text-center">
            <h1 className="text-3xl font-extrabold leading-tight tracking-tighter md:text-5xl lg:text-6xl lg:leading-[1.1]">
              개인 자산을 한 곳에서
              <br className="hidden sm:inline" />
              <span className="text-primary"> 통합 관리</span>
            </h1>
            <p className="max-w-[750px] text-lg text-muted-foreground sm:text-xl">
              여러 금융기관의 자산 데이터를 스냅샷 단위로 업로드하여
              <br className="hidden sm:inline" />
              통합 관리·분석·시각화하는 개인 자산 관리 플랫폼
            </p>
          </div>
          <div className="flex gap-4">
            <Link href="/auth/login">
              <Button size="lg">시작하기</Button>
            </Link>
            <Link href="/dashboard">
              <Button variant="outline" size="lg">
                대시보드 보기
              </Button>
            </Link>
          </div>
        </section>

        {/* Features Section */}
        <section className="container pb-8 pt-6 md:py-10">
          <div className="grid gap-6 md:grid-cols-3">
            <FeatureCard
              title="데이터 통합"
              description="여러 금융기관의 자산 데이터를 표준화하여 한 곳에서 관리"
            />
            <FeatureCard
              title="대시보드 분석"
              description="총액, 비중, 수익률 등 핵심 지표를 한눈에 확인"
            />
            <FeatureCard
              title="리밸런싱"
              description="목표 비중 설정 및 리밸런싱 제안 자동 생성"
            />
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t py-6 md:py-0">
        <div className="container flex flex-col items-center justify-between gap-4 md:h-24 md:flex-row">
          <p className="text-center text-sm leading-loose text-muted-foreground md:text-left">
            Built with Next.js, TypeScript, and Supabase
          </p>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({ title, description }: { title: string; description: string }) {
  return (
    <div className="rounded-lg border bg-card p-6 shadow-sm">
      <h3 className="mb-2 text-lg font-semibold">{title}</h3>
      <p className="text-sm text-muted-foreground">{description}</p>
    </div>
  )
}
