# Donmoa 아키텍처 문서

## 전체 시스템 아키텍처

### 데이터 플로우

```
[CLI (Python)]
    ↓ CSV 생성
[로컬 파일 시스템]
    ↓ 수동 업로드
[Web Frontend (Next.js)]
    ↓ HTTP/REST
[API Server (Node.js + Express)]
    ↓ SQL
[Database (Supabase Postgres)]
```

### 컴포넌트 다이어그램

```
┌─────────────────┐
│   Web (Next.js) │
│   Mobile (Expo) │
└────────┬────────┘
         │ HTTP
         ↓
┌─────────────────────────────┐
│  API Server (Node.js)       │
│  ┌─────────────────────┐    │
│  │ Presentation Layer  │    │
│  │  (handlers)         │    │
│  └──────────┬──────────┘    │
│             ↓                │
│  ┌─────────────────────┐    │
│  │ Application Layer   │    │
│  │  (services)         │    │
│  └──────────┬──────────┘    │
│             ↓                │
│  ┌─────────────────────┐    │
│  │ Infrastructure      │    │
│  │  (repositories)     │    │
│  └──────────┬──────────┘    │
└─────────────┼───────────────┘
              ↓
┌─────────────────────────────┐
│  Database (Postgres)        │
│  - RLS enabled              │
│  - Migrations managed       │
└─────────────────────────────┘
```

## 도메인 경계 (Bounded Contexts)

### 1. Snapshot Domain
**책임**: 원본 데이터 수집 및 정규화

- 파일 업로드
- 데이터 파싱
- 계좌/종목 매핑
- 스냅샷 커밋 (원샷)
- 정수화 (Money, Quantity, Price)

**경계**:
- 입력: 원본 파일 (CSV, Excel, MHTML)
- 출력: 정규화된 스냅샷 데이터 (snapshots, snapshot_*)

### 2. Portfolio Domain
**책임**: 포트폴리오 조회 및 관리

- 계좌 조회
- 포지션 조회
- 현금 잔액 조회
- 라인 아이템 수정

**경계**:
- 입력: 스냅샷 데이터
- 출력: 포트폴리오 뷰

### 3. Analytics Domain
**책임**: 데이터 분석 및 시각화

- 대시보드 요약
- 시계열 차트
- 비중 계산
- 현금흐름 분석
- 배당 집계

**경계**:
- 입력: 포트폴리오 데이터, 시세 데이터
- 출력: 분석 결과

### 4. Rebalancing Domain
**책임**: 포트폴리오 리밸런싱

- 타겟 비중 관리
- 동적 룰 관리
- 리밸런싱 제안 생성

**경계**:
- 입력: 현재 포트폴리오, 타겟 비중
- 출력: 매수/매도 제안

### 5. Market Data Domain
**책임**: 시장 데이터 관리

- 종목 검색
- 시세 조회
- 환율 조회
- 메트릭스 계산

**경계**:
- 입력: 외부 데이터 소스
- 출력: 정규화된 시세/환율

### 6. User Preferences Domain
**책임**: 사용자 커스터마이징

- 즐겨찾기 관리
- 카테고리 관리
- 대시보드 레이아웃 설정

**경계**:
- 입력: 사용자 입력
- 출력: 설정 데이터

## 레이어 아키텍처

### Presentation Layer (handlers)
- HTTP 요청 수신
- 인증 검증
- 입력 검증
- 응답 포맷팅

### Application Layer (services)
- 비즈니스 로직
- 트랜잭션 관리
- 도메인 오케스트레이션
- 검증 규칙

### Domain Layer (types)
- 도메인 엔티티
- 값 객체
- 도메인 이벤트
- 비즈니스 규칙

### Infrastructure Layer (repositories)
- DB 접근
- 외부 API 호출
- 파일 시스템 접근
- 캐싱

## 타입 일관성

### Money 타입
```typescript
interface Money {
  amount_minor: bigint;  // 정수화된 금액
  currency: string;       // 3자 통화 코드
}

// 변환
amount_minor = amount * CURRENCY_SCALE[currency]
// KRW: ₩1,000 → 1000
// USD: $10.50 → 1050
```

### Quantity 타입
```typescript
qty_nano: bigint = quantity * 1e9

// 예시
// 1.5 주 → 1_500_000_000n
// 0.00000123 BTC → 1_230n
```

### Price 타입
```typescript
price_nano: bigint = price * 1e9

// 예시
// ₩50,000 → 50_000_000_000_000n
```

## 데이터베이스 설계

### 핵심 엔티티
```
users (UUID)
  ├─ institutions (bigserial)
  │    └─ accounts (bigserial)
  │         ├─ snapshot_cash
  │         ├─ snapshot_positions
  │         └─ snapshot_transactions
  └─ snapshots (bigserial)
       └─ ingest_logs
```

### 시장 데이터
```
data_sources (bigserial)
  ├─ instruments (bigserial)
  │    └─ prices_daily
  └─ fx_rates_daily
```

### 사용자 설정
```
users
  ├─ categories (bigserial)
  ├─ favorites
  ├─ dashboard_prefs
  ├─ rebalance_targets
  ├─ rebalance_rules
  └─ portfolios
```

### RLS (Row Level Security)
- 모든 사용자 데이터는 `user_id`로 격리
- 시장 데이터는 모든 인증 사용자가 읽기 가능
- 정책: `auth.uid() = user_id`

## 보안

### 인증
- Supabase Auth (JWT)
- Bearer Token 인증
- 토큰 검증 미들웨어

### 인가
- Row Level Security (RLS)
- 사용자별 데이터 격리
- API 레벨 권한 체크

### 데이터 보호
- 정수화로 정밀도 유지
- 트랜잭션 보장
- Idempotency Key 지원

## 확장성

### 수평 확장
- API 서버 스테이트리스
- 데이터베이스 연결 풀링
- 캐싱 레이어 (Redis - TODO)

### 성능 최적화
- 인덱스 최적화
- 뷰 및 함수 활용
- 페이지네이션
- 데이터 정규화

### 모니터링
- 구조화된 로깅
- 에러 추적
- 성능 메트릭스 (TODO)

## 개발 원칙

### 1. 도메인 주도 설계 (DDD)
- 명확한 도메인 경계
- 유비쿼터스 언어
- 집계 루트

### 2. 관심사 분리
- 레이어별 책임 분리
- 인터페이스 기반 설계
- 의존성 주입

### 3. 타입 안정성
- TypeScript strict 모드
- Zod 스키마 검증
- 컴파일 타임 안정성

### 4. 테스트 가능성
- 순수 함수 선호
- 목 객체 사용 가능
- 단위 테스트 우선 (TODO)

## 배포 전략

### 개발 환경
- 로컬 Supabase
- Hot reload (tsx watch)
- 개발 DB

### 스테이징
- Supabase Staging
- 별도 환경 변수
- 테스트 데이터

### 프로덕션
- Supabase Production
- 환경 변수 분리
- 백업 및 롤백 계획

## 향후 계획

### Phase 1 ✅ (완료)
- [x] 모노레포 구조
- [x] 공통 타입
- [x] DB 마이그레이션
- [x] API 기본 구조
- [x] Snapshot 도메인

### Phase 2 (진행 중)
- [ ] Portfolio 도메인
- [ ] Analytics 도메인
- [ ] Rebalancing 도메인
- [ ] Market Data 도메인
- [ ] User Preferences 도메인

### Phase 3 (예정)
- [ ] Web Frontend (Next.js)
- [ ] Mobile App (Expo)
- [ ] UI 컴포넌트 라이브러리

### Phase 4 (예정)
- [ ] 테스트 작성
- [ ] CI/CD 파이프라인
- [ ] 모니터링 및 로깅
- [ ] 성능 최적화
