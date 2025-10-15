# Donmoa

개인 자산 관리 플랫폼

## 프로젝트 구조

```
donmoa/
├── cli/                    # Python CLI (데이터 수집)
│   └── donmoa/
├── packages/
│   ├── shared/            # 공통 타입 (TypeScript)
│   ├── database/          # DB 마이그레이션
│   ├── api/               # API 서버 (Node.js + Express)
│   └── ui/                # 공통 UI 컴포넌트 (TODO)
├── apps/
│   ├── web/              # Next.js 웹 앱 ✅
│   └── mobile/           # React Native/Expo 앱 (TODO)
└── docs/                 # 문서 (PRD, API, DB)
```

## 기술 스택

- **CLI**: Python 3.x
- **Backend**: Node.js + Express + Supabase (Postgres)
- **Frontend**: Next.js (Web), React Native/Expo (Mobile)
- **공통**: TypeScript, Turborepo, pnpm

## 빠른 시작

### 1. 의존성 설치

```bash
# pnpm 설치 (없는 경우)
npm install -g pnpm

# 프로젝트 의존성 설치
pnpm install
```

### 2. 환경 변수 설정

```bash
# API 환경 변수
cp packages/api/.env.example packages/api/.env
# .env 파일 편집하여 Supabase 정보 입력
```

### 3. 데이터베이스 마이그레이션

```bash
# Supabase CLI로 마이그레이션 실행
# (또는 Supabase 콘솔에서 SQL 직접 실행)
cd packages/database
# migrations/*.sql 파일 순서대로 실행
```

### 4. 개발 서버 실행

```bash
# API 서버 시작
cd packages/api && pnpm dev
# → http://localhost:3001

# 웹 앱 시작 (별도 터미널)
cd apps/web
cp .env.local.example .env.local
# .env.local 파일 편집 (Supabase URL, API URL 입력)
pnpm dev
# → http://localhost:3000

# 또는 전체 개발 서버 시작 (Turborepo)
pnpm dev
```

## 패키지 설명

### @donmoa/shared

공통 타입 및 유틸리티 패키지

- 도메인 타입 (Snapshot, Portfolio, Analytics, Rebalance, Market, User)
- API 요청/응답 스키마
- 공통 유틸 (Money, Quantity, Pagination, Errors)

### @donmoa/database

데이터베이스 마이그레이션 스크립트

- 8개 마이그레이션 파일
- 정수화 규칙 (amount_minor, qty_nano, price_nano)
- Row Level Security (RLS) 정책

### @donmoa/api

Node.js API 서버

- 도메인 주도 설계 (DDD)
- 레이어 아키텍처 (Presentation → Application → Domain → Infrastructure)
- 미들웨어 (인증, 에러 핸들링, 검증, Idempotency)
- **6개 도메인 완전 구현** (33개 API 엔드포인트)

### @donmoa/web ✅

Next.js 14 웹 애플리케이션

- App Router, TypeScript
- Tailwind CSS 디자인 시스템
- TanStack Query (React Query)
- Supabase Auth
- **주요 페이지 구현 완료** (인증, 대시보드, 스냅샷, 포트폴리오, 리밸런싱)

## 도메인 모델

### 1. Snapshot Domain ✅
- 파일 업로드, 파싱, 커밋
- 스냅샷 조회
- 4개 엔드포인트

### 2. Portfolio Domain ✅
- 계좌, 포지션, 현금 조회/수정
- 배당 입력
- 6개 엔드포인트

### 3. Analytics Domain ✅
- 대시보드 요약, 시계열, 비중
- 현금흐름, 배당 집계
- 5개 엔드포인트

### 4. Rebalancing Domain ✅
- 타겟/룰 관리
- 리밸런싱 제안 생성
- 5개 엔드포인트

### 5. Market Data Domain ✅
- 종목 검색, 시세, 환율 조회
- 종목 메트릭스
- 5개 엔드포인트

### 6. User Preferences Domain ✅
- 즐겨찾기, 카테고리, 대시보드 설정
- 8개 엔드포인트

## 개발 가이드

### 레이어 아키텍처

```
[Presentation Layer]  handlers.ts     # HTTP 요청/응답
  ↓
[Application Layer]   service.ts      # 비즈니스 로직
  ↓
[Domain Layer]        @donmoa/shared  # 타입 정의
  ↓
[Infrastructure]      repository.ts   # DB 접근
```

### 새 도메인 추가 방법

1. `packages/shared/src/types/domain/` - 도메인 타입 정의
2. `packages/shared/src/types/api/` - API 스키마 정의
3. `packages/api/src/domains/[domain]/` - 도메인 로직 구현
   - `repository.ts` - DB 접근
   - `validator.ts` - 검증 스키마
   - `service.ts` - 비즈니스 로직
   - `handlers.ts` - HTTP 핸들러
4. `packages/api/src/routes/` - 라우터 추가

### 정수화 규칙

- **금액**: `amount_minor = amount * 통화스케일` (KRW: 1, USD: 100)
- **수량**: `qty_nano = quantity * 1e9`
- **단가**: `price_nano = price * 1e9`

## 스크립트

```bash
# 개발
pnpm dev          # 전체 개발 서버
pnpm build        # 전체 빌드
pnpm type-check   # 타입 체크
pnpm lint         # 린트
pnpm test         # 테스트 (TODO)

# 정리
pnpm clean        # 빌드 아티팩트 삭제
```

## 문서

- [PRD](docs/prd.txt) - 제품 요구사항 문서
- [DB 스키마](docs/db.txt) - 데이터베이스 설계
- [API 명세](docs/api.txt) - OpenAPI 3.1 스펙
- [CLI 데이터 스키마](docs/db_cli.txt) - CLI 출력 형식
- [Architecture](ARCHITECTURE.md) - 아키텍처 상세 설명
- [Progress](PROGRESS.md) - 진행 상황 (전체 65% 완료)
- [Phase 3 Complete](PHASE3_COMPLETE.md) - Web Frontend 완료 보고서

## 라이선스

Private

## 기여

현재 개인 프로젝트
