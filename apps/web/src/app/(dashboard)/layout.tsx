import Link from 'next/link'
import { Button } from '@/components/ui/button'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 items-center">
          <div className="mr-4 flex">
            <Link href="/dashboard" className="mr-6 flex items-center space-x-2">
              <span className="font-bold">Donmoa</span>
            </Link>
            <nav className="flex items-center space-x-6 text-sm font-medium">
              <Link
                href="/dashboard"
                className="transition-colors hover:text-foreground/80"
              >
                대시보드
              </Link>
              <Link
                href="/dashboard/snapshots"
                className="transition-colors hover:text-foreground/80"
              >
                스냅샷
              </Link>
              <Link
                href="/dashboard/portfolio"
                className="transition-colors hover:text-foreground/80"
              >
                포트폴리오
              </Link>
              <Link
                href="/dashboard/rebalance"
                className="transition-colors hover:text-foreground/80"
              >
                리밸런싱
              </Link>
            </nav>
          </div>
          <div className="flex flex-1 items-center justify-end space-x-2">
            <Button variant="ghost" size="sm">
              로그아웃
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        <div className="container py-6">{children}</div>
      </main>
    </div>
  )
}

