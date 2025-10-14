# Database Migrations

Donmoa 데이터베이스 마이그레이션 스크립트입니다.

## 마이그레이션 목록

1. `001_create_users_and_auth.sql` - 사용자, 기관, 계좌 테이블
2. `002_create_instruments_and_market.sql` - 종목, 시세, 환율 테이블
3. `003_create_snapshots.sql` - 스냅샷 및 라인 아이템 테이블
4. `004_create_portfolio_views.sql` - 포트폴리오 조회 뷰 및 함수
5. `005_create_rebalance_tables.sql` - 리밸런싱 테이블
6. `006_create_user_prefs.sql` - 사용자 설정 테이블
7. `007_create_indexes.sql` - 성능 최적화 인덱스
8. `008_create_rls_policies.sql` - Row Level Security 정책

## 실행 방법

### Supabase CLI 사용

```bash
# 로컬 Supabase 시작
supabase start

# 마이그레이션 실행
supabase db push

# 또는 개별 마이그레이션 실행
psql -h localhost -p 54322 -U postgres -d postgres -f migrations/001_create_users_and_auth.sql
```

### 직접 psql 사용

```bash
for file in migrations/*.sql; do
  psql -h your-db-host -U your-user -d your-db -f "$file"
done
```

## 주요 테이블

### 핵심 엔티티
- `users` - 사용자
- `institutions` - 기관
- `accounts` - 계좌
- `instruments` - 종목

### 스냅샷
- `snapshots` - 스냅샷 헤더
- `snapshot_cash` - 현금 잔액
- `snapshot_positions` - 포지션
- `snapshot_transactions` - 거래 내역

### 시장 데이터
- `prices_daily` - 일별 가격
- `fx_rates_daily` - 일별 환율

### 설정
- `categories` - 카테고리
- `favorites` - 즐겨찾기
- `dashboard_prefs` - 대시보드 설정
- `rebalance_targets` - 리밸런싱 타겟
- `rebalance_rules` - 리밸런싱 룰

## 정수화 규칙

- **금액 (`amount_minor`)**: `BIGINT`, 통화별 스케일 적용
  - KRW: ₩1,000 = 1000
  - USD: $10.50 = 1050 (센트)
- **수량 (`qty_nano`)**: `BIGINT`, 수량 × 1,000,000,000
- **단가 (`price_nano`)**: `BIGINT`, 단가 × 1,000,000,000

## RLS (Row Level Security)

모든 사용자 데이터는 RLS로 보호됩니다:
- 사용자는 본인의 데이터만 접근 가능
- 시장 데이터(종목, 시세, 환율)는 모든 인증된 사용자가 읽기 가능
