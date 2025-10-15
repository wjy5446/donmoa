-- 003_create_snapshots.sql
-- 스냅샷 및 스냅샷 라인 테이블

-- 스냅샷 헤더
CREATE TABLE IF NOT EXISTS snapshots (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  snapshot_date DATE NOT NULL,
  source TEXT NOT NULL CHECK (source IN ('cli', 'manual', 'banksalad', 'domino', 'web')),
  status TEXT NOT NULL DEFAULT 'completed' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ
);

CREATE UNIQUE INDEX idx_snapshots_user_date ON snapshots(user_id, snapshot_date);
CREATE INDEX idx_snapshots_date ON snapshots(snapshot_date);
CREATE INDEX idx_snapshots_source ON snapshots(source);

CREATE TRIGGER snapshots_updated_at
  BEFORE UPDATE ON snapshots
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- 스냅샷 현금 라인
CREATE TABLE IF NOT EXISTS snapshot_cash (
  id BIGSERIAL PRIMARY KEY,
  snapshot_id BIGINT NOT NULL REFERENCES snapshots(id) ON DELETE CASCADE,
  account_id BIGINT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
  currency TEXT NOT NULL,
  amount_minor BIGINT NOT NULL, -- 정수화된 금액
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT unique_snapshot_cash UNIQUE (snapshot_id, account_id, currency)
);

CREATE INDEX idx_snapshot_cash_snapshot ON snapshot_cash(snapshot_id);
CREATE INDEX idx_snapshot_cash_account ON snapshot_cash(account_id);

-- 스냅샷 포지션 라인
CREATE TABLE IF NOT EXISTS snapshot_positions (
  id BIGSERIAL PRIMARY KEY,
  snapshot_id BIGINT NOT NULL REFERENCES snapshots(id) ON DELETE CASCADE,
  account_id BIGINT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
  instrument_id BIGINT NOT NULL REFERENCES instruments(id) ON DELETE CASCADE,
  qty_nano BIGINT NOT NULL, -- 정수화된 수량
  avg_cost NUMERIC(38, 8), -- 평균 단가 (옵션)
  currency TEXT NOT NULL,
  tags JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT unique_snapshot_position UNIQUE (snapshot_id, account_id, instrument_id)
);

CREATE INDEX idx_snapshot_positions_snapshot ON snapshot_positions(snapshot_id);
CREATE INDEX idx_snapshot_positions_account ON snapshot_positions(account_id);
CREATE INDEX idx_snapshot_positions_instrument ON snapshot_positions(instrument_id);

-- 스냅샷 거래 라인
CREATE TABLE IF NOT EXISTS snapshot_transactions (
  id BIGSERIAL PRIMARY KEY,
  snapshot_id BIGINT NOT NULL REFERENCES snapshots(id) ON DELETE CASCADE,
  account_id BIGINT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
  txn_id TEXT, -- 외부 거래 ID
  trade_datetime TIMESTAMPTZ NOT NULL,
  settle_date DATE,
  type TEXT NOT NULL CHECK (type IN ('buy', 'sell', 'dividend', 'fee', 'transfer', 'deposit', 'withdraw', 'interest', 'other')),
  instrument_id BIGINT REFERENCES instruments(id) ON DELETE SET NULL,
  qty_nano BIGINT, -- 정수화된 수량
  price_nano BIGINT, -- 정수화된 단가
  amount_minor BIGINT, -- 정수화된 금액
  currency TEXT NOT NULL,
  category_id BIGINT, -- categories 테이블 참조 (나중에 FK 추가)
  note TEXT,
  raw JSONB, -- 원본 데이터 보존
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_snapshot_transactions_snapshot ON snapshot_transactions(snapshot_id);
CREATE INDEX idx_snapshot_transactions_account ON snapshot_transactions(account_id);
CREATE INDEX idx_snapshot_transactions_instrument ON snapshot_transactions(instrument_id);
CREATE INDEX idx_snapshot_transactions_trade_datetime ON snapshot_transactions(trade_datetime);
CREATE INDEX idx_snapshot_transactions_type ON snapshot_transactions(type);

-- 인제스트 로그
CREATE TABLE IF NOT EXISTS ingest_logs (
  id BIGSERIAL PRIMARY KEY,
  snapshot_id BIGINT NOT NULL REFERENCES snapshots(id) ON DELETE CASCADE,
  level TEXT NOT NULL CHECK (level IN ('info', 'warning', 'error')),
  message TEXT NOT NULL,
  context JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ingest_logs_snapshot ON ingest_logs(snapshot_id);
CREATE INDEX idx_ingest_logs_level ON ingest_logs(level);
CREATE INDEX idx_ingest_logs_created ON ingest_logs(created_at DESC);

COMMENT ON TABLE snapshots IS '스냅샷 헤더 (불변)';
COMMENT ON TABLE snapshot_cash IS '스냅샷 현금 잔액 (계좌×통화)';
COMMENT ON TABLE snapshot_positions IS '스냅샷 포지션 (계좌×종목)';
COMMENT ON TABLE snapshot_transactions IS '스냅샷 거래 내역';
COMMENT ON TABLE ingest_logs IS '업로드/커밋 검증 로그';
