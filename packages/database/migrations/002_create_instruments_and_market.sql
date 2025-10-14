-- 002_create_instruments_and_market.sql
-- 종목, 시세, 환율 테이블

-- 데이터 소스
CREATE TABLE IF NOT EXISTS data_sources (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  kind TEXT NOT NULL CHECK (kind IN ('price', 'fx', 'transaction')),
  meta JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_data_sources_kind ON data_sources(kind);

-- 종목/자산 마스터
CREATE TABLE IF NOT EXISTS instruments (
  id BIGSERIAL PRIMARY KEY,
  symbol TEXT NOT NULL,
  isin TEXT,
  name TEXT NOT NULL,
  asset_class TEXT NOT NULL CHECK (asset_class IN ('equity', 'bond', 'fund', 'crypto', 'commodity', 'fx', 'cash', 'other')),
  subclass TEXT,
  currency TEXT NOT NULL DEFAULT 'KRW',
  metadata JSONB DEFAULT '{}'::jsonb,
  valid_from DATE,
  valid_to DATE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ,
  CONSTRAINT valid_instrument_date_range CHECK (valid_to IS NULL OR valid_from <= valid_to)
);

CREATE UNIQUE INDEX idx_instruments_symbol_currency ON instruments(symbol, currency) WHERE valid_to IS NULL;
CREATE INDEX idx_instruments_isin ON instruments(isin) WHERE isin IS NOT NULL;
CREATE INDEX idx_instruments_asset_class ON instruments(asset_class);
CREATE INDEX idx_instruments_name ON instruments(name);

CREATE TRIGGER instruments_updated_at
  BEFORE UPDATE ON instruments
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- 일별 가격 (OHLCV)
CREATE TABLE IF NOT EXISTS prices_daily (
  instrument_id BIGINT NOT NULL REFERENCES instruments(id) ON DELETE CASCADE,
  price_date DATE NOT NULL,
  open NUMERIC(38, 8),
  high NUMERIC(38, 8),
  low NUMERIC(38, 8),
  close NUMERIC(38, 8) NOT NULL,
  volume NUMERIC(38, 8),
  dividend NUMERIC(38, 8), -- 배당금
  split TEXT, -- 액면분할 정보 (예: "2:1")
  source_id BIGINT NOT NULL REFERENCES data_sources(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (instrument_id, price_date)
);

CREATE INDEX idx_prices_daily_date ON prices_daily(price_date);
CREATE INDEX idx_prices_daily_instrument_date ON prices_daily(instrument_id, price_date DESC);

-- 환율 (일별)
CREATE TABLE IF NOT EXISTS fx_rates_daily (
  base_currency TEXT NOT NULL,
  quote_currency TEXT NOT NULL,
  rate_date DATE NOT NULL,
  rate NUMERIC(38, 10) NOT NULL, -- 1 quote = rate base
  source_id BIGINT NOT NULL REFERENCES data_sources(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (base_currency, quote_currency, rate_date),
  CONSTRAINT valid_currencies CHECK (
    base_currency ~ '^[A-Z]{3}$' AND
    quote_currency ~ '^[A-Z]{3}$' AND
    base_currency <> quote_currency
  )
);

CREATE INDEX idx_fx_rates_daily_date ON fx_rates_daily(rate_date);
CREATE INDEX idx_fx_rates_daily_pair_date ON fx_rates_daily(base_currency, quote_currency, rate_date DESC);

-- 종목 외부 심볼 매핑 (여러 소스에서 동일 종목을 다른 심볼로 표기하는 경우)
CREATE TABLE IF NOT EXISTS instrument_external_symbols (
  instrument_id BIGINT NOT NULL REFERENCES instruments(id) ON DELETE CASCADE,
  external_symbol TEXT NOT NULL,
  source TEXT NOT NULL,
  PRIMARY KEY (external_symbol, source)
);

CREATE INDEX idx_instrument_external_symbols_instrument ON instrument_external_symbols(instrument_id);

COMMENT ON TABLE data_sources IS '데이터 소스 (가격, 환율, 거래)';
COMMENT ON TABLE instruments IS '종목/자산 마스터';
COMMENT ON TABLE prices_daily IS '일별 가격 (OHLCV)';
COMMENT ON TABLE fx_rates_daily IS '일별 환율';
COMMENT ON TABLE instrument_external_symbols IS '종목 외부 심볼 매핑';
