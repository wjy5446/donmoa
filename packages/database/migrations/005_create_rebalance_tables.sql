-- 005_create_rebalance_tables.sql
-- 리밸런싱 관련 테이블

-- 리밸런싱 타겟 (정적 비중)
CREATE TABLE IF NOT EXISTS rebalance_targets (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  scope TEXT NOT NULL CHECK (scope IN ('account', 'global')),
  account_id BIGINT REFERENCES accounts(id) ON DELETE CASCADE,
  asset_class TEXT NOT NULL,
  subclass TEXT,
  target_pct NUMERIC(5, 4) NOT NULL CHECK (target_pct >= 0 AND target_pct <= 1),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ,
  CONSTRAINT check_account_scope CHECK (
    (scope = 'account' AND account_id IS NOT NULL) OR
    (scope = 'global' AND account_id IS NULL)
  )
);

CREATE INDEX idx_rebalance_targets_user ON rebalance_targets(user_id);
CREATE INDEX idx_rebalance_targets_account ON rebalance_targets(account_id);

CREATE TRIGGER rebalance_targets_updated_at
  BEFORE UPDATE ON rebalance_targets
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- 리밸런싱 룰 (동적 규칙)
CREATE TABLE IF NOT EXISTS rebalance_rules (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  type TEXT NOT NULL CHECK (type IN ('band', 'momentum', 'custom')),
  params JSONB NOT NULL DEFAULT '{}'::jsonb,
  enabled BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ
);

CREATE INDEX idx_rebalance_rules_user ON rebalance_rules(user_id);
CREATE INDEX idx_rebalance_rules_enabled ON rebalance_rules(enabled);

CREATE TRIGGER rebalance_rules_updated_at
  BEFORE UPDATE ON rebalance_rules
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- 포트폴리오 정의 (계좌 그룹)
CREATE TABLE IF NOT EXISTS portfolios (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  base_currency TEXT NOT NULL DEFAULT 'KRW',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ
);

CREATE INDEX idx_portfolios_user ON portfolios(user_id);

CREATE TRIGGER portfolios_updated_at
  BEFORE UPDATE ON portfolios
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- 포트폴리오-계좌 매핑
CREATE TABLE IF NOT EXISTS portfolio_accounts (
  portfolio_id BIGINT NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
  account_id BIGINT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
  weight NUMERIC(5, 4), -- 포트폴리오 내 비중 (선택)
  PRIMARY KEY (portfolio_id, account_id)
);

CREATE INDEX idx_portfolio_accounts_portfolio ON portfolio_accounts(portfolio_id);
CREATE INDEX idx_portfolio_accounts_account ON portfolio_accounts(account_id);

COMMENT ON TABLE rebalance_targets IS '리밸런싱 타겟 (정적 비중)';
COMMENT ON TABLE rebalance_rules IS '리밸런싱 룰 (동적 규칙)';
COMMENT ON TABLE portfolios IS '포트폴리오 정의';
COMMENT ON TABLE portfolio_accounts IS '포트폴리오-계좌 매핑';
