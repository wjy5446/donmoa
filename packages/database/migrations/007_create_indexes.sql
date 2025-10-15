-- 007_create_indexes.sql
-- 추가 인덱스 및 성능 최적화

-- 스냅샷 관련 복합 인덱스
CREATE INDEX IF NOT EXISTS idx_snapshots_user_date_status
  ON snapshots(user_id, snapshot_date DESC, status);

-- 거래 내역 조회 최적화
CREATE INDEX IF NOT EXISTS idx_snapshot_transactions_account_datetime
  ON snapshot_transactions(account_id, trade_datetime DESC);

CREATE INDEX IF NOT EXISTS idx_snapshot_transactions_user_datetime
  ON snapshot_transactions(account_id, trade_datetime DESC)
  INCLUDE (type, amount_minor, currency);

-- 시세 조회 최적화
CREATE INDEX IF NOT EXISTS idx_prices_daily_close
  ON prices_daily(instrument_id, price_date DESC)
  INCLUDE (close);

-- 환율 조회 최적화
CREATE INDEX IF NOT EXISTS idx_fx_rates_daily_rate
  ON fx_rates_daily(base_currency, quote_currency, rate_date DESC)
  INCLUDE (rate);

-- 포지션 집계 최적화
CREATE INDEX IF NOT EXISTS idx_snapshot_positions_user_instrument
  ON snapshot_positions(account_id, instrument_id)
  INCLUDE (qty_nano, currency);

-- Full-text search 인덱스 (종목명 검색)
CREATE INDEX IF NOT EXISTS idx_instruments_name_trgm
  ON instruments USING gin(name gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_instruments_symbol_trgm
  ON instruments USING gin(symbol gin_trgm_ops);

-- pg_trgm 확장 활성화 (trigram 검색용)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

COMMENT ON INDEX idx_snapshots_user_date_status IS '사용자별 최신 스냅샷 조회 최적화';
COMMENT ON INDEX idx_snapshot_transactions_account_datetime IS '계좌별 거래 내역 조회 최적화';
COMMENT ON INDEX idx_instruments_name_trgm IS '종목명 부분 검색 최적화';
