# @donmoa/api

Donmoa API Server (Node.js + Express)

## 구조

```
src/
├── config/           # 설정
├── domains/          # 도메인별 비즈니스 로직
│   ├── snapshot/     # 스냅샷 도메인
│   │   ├── service.ts      # 비즈니스 로직
│   │   ├── repository.ts   # DB 접근
│   │   ├── validator.ts    # 검증 스키마
│   │   └── handlers.ts     # HTTP 핸들러
│   ├── portfolio/
│   ├── analytics/
│   └── ...
├── middleware/       # 미들웨어
├── routes/           # 라우터
├── utils/            # 유틸리티
├── app.ts            # Express 앱
└── index.ts          # 진입점
```

## 레이어 아키텍처

```
[Presentation Layer]  handlers.ts
  ↓
[Application Layer]   service.ts
  ↓
[Domain Layer]        @donmoa/shared types
  ↓
[Infrastructure]      repository.ts → Supabase
```

## 개발

```bash
# 의존성 설치
pnpm install

# 개발 서버 시작
pnpm dev

# 빌드
pnpm build

# 프로덕션 실행
pnpm start
```

## 환경 변수

`.env` 파일 생성:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
PORT=3001
NODE_ENV=development
CORS_ORIGIN=http://localhost:3000
JWT_SECRET=your-jwt-secret
```

## API 엔드포인트

### 스냅샷
- `POST /v1/snapshots/commit` - 스냅샷 커밋
- `POST /v1/snapshots/upload` - 파일 업로드
- `GET /v1/snapshots` - 스냅샷 목록
- `GET /v1/snapshots/:id` - 스냅샷 상세

### TODO
- Dashboard 엔드포인트
- Rebalance 엔드포인트
- Portfolio 엔드포인트
- Market 엔드포인트
- User Preferences 엔드포인트

## 인증

모든 API 요청은 Bearer 토큰 필요:

```
Authorization: Bearer <supabase-jwt-token>
```

## Idempotency

쓰기 요청에 Idempotency-Key 헤더 사용 가능:

```
Idempotency-Key: <unique-key>
```
