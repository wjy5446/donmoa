# @donmoa/web

Donmoa Web Application (Next.js 14)

## 기술 스택

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: TanStack Query (React Query)
- **Authentication**: Supabase Auth
- **Forms**: React Hook Form + Zod
- **Charts**: Recharts

## 시작하기

### 1. 환경 변수 설정

`.env.local` 파일 생성:

```bash
cp .env.local.example .env.local
```

환경 변수 입력:
```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=http://localhost:3001
```

### 2. 의존성 설치

```bash
pnpm install
```

### 3. 개발 서버 실행

```bash
pnpm dev
```

http://localhost:3000에서 확인

## 프로젝트 구조

```
src/
├── app/
│   ├── (auth)/          # 인증 페이지 (로그인, 회원가입)
│   ├── (dashboard)/     # 대시보드 페이지들
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx         # 홈 페이지
├── components/
│   ├── ui/              # 재사용 가능한 UI 컴포넌트
│   └── providers.tsx    # React Query Provider
└── lib/
    ├── api-client.ts    # API 클라이언트
    ├── supabase.ts      # Supabase 클라이언트
    └── utils.ts         # 유틸리티 함수
```

## 주요 페이지

### 인증
- `/auth/login` - 로그인
- `/auth/signup` - 회원가입

### 대시보드
- `/dashboard` - 대시보드 홈 (요약)
- `/dashboard/snapshots` - 스냅샷 목록
- `/dashboard/snapshots/upload` - 스냅샷 업로드
- `/dashboard/portfolio` - 포트폴리오
- `/dashboard/rebalance` - 리밸런싱

## API 연동

API 클라이언트는 `src/lib/api-client.ts`에 정의되어 있습니다.

```typescript
import { apiClient } from '@/lib/api-client'

// 사용 예시
const data = await apiClient.getDashboardSummary('2025-01-10')
```

## 스타일링

Tailwind CSS + shadcn/ui 디자인 시스템 사용

색상 테마는 `src/app/globals.css`에서 설정

## 빌드

```bash
pnpm build
```

## 프로덕션 실행

```bash
pnpm start
```

