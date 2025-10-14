-- 008_create_rls_policies.sql
-- Row Level Security (RLS) 정책

-- RLS 활성화
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE institutions ENABLE ROW LEVEL SECURITY;
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE snapshot_cash ENABLE ROW LEVEL SECURITY;
ALTER TABLE snapshot_positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE snapshot_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE favorites ENABLE ROW LEVEL SECURITY;
ALTER TABLE dashboard_prefs ENABLE ROW LEVEL SECURITY;
ALTER TABLE rebalance_targets ENABLE ROW LEVEL SECURITY;
ALTER TABLE rebalance_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;

-- users 정책
CREATE POLICY users_select_own ON users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY users_update_own ON users
  FOR UPDATE USING (auth.uid() = id);

-- institutions 정책
CREATE POLICY institutions_all_own ON institutions
  FOR ALL USING (auth.uid() = user_id);

-- accounts 정책
CREATE POLICY accounts_all_own ON accounts
  FOR ALL USING (auth.uid() = user_id);

-- snapshots 정책
CREATE POLICY snapshots_all_own ON snapshots
  FOR ALL USING (auth.uid() = user_id);

-- snapshot_cash 정책
CREATE POLICY snapshot_cash_select_own ON snapshot_cash
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM snapshots s
      WHERE s.id = snapshot_cash.snapshot_id
      AND s.user_id = auth.uid()
    )
  );

CREATE POLICY snapshot_cash_insert_own ON snapshot_cash
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM snapshots s
      WHERE s.id = snapshot_cash.snapshot_id
      AND s.user_id = auth.uid()
    )
  );

CREATE POLICY snapshot_cash_update_own ON snapshot_cash
  FOR UPDATE USING (
    EXISTS (
      SELECT 1 FROM snapshots s
      WHERE s.id = snapshot_cash.snapshot_id
      AND s.user_id = auth.uid()
    )
  );

CREATE POLICY snapshot_cash_delete_own ON snapshot_cash
  FOR DELETE USING (
    EXISTS (
      SELECT 1 FROM snapshots s
      WHERE s.id = snapshot_cash.snapshot_id
      AND s.user_id = auth.uid()
    )
  );

-- snapshot_positions 정책 (snapshot_cash와 동일 패턴)
CREATE POLICY snapshot_positions_select_own ON snapshot_positions
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM snapshots s WHERE s.id = snapshot_positions.snapshot_id AND s.user_id = auth.uid())
  );

CREATE POLICY snapshot_positions_insert_own ON snapshot_positions
  FOR INSERT WITH CHECK (
    EXISTS (SELECT 1 FROM snapshots s WHERE s.id = snapshot_positions.snapshot_id AND s.user_id = auth.uid())
  );

CREATE POLICY snapshot_positions_update_own ON snapshot_positions
  FOR UPDATE USING (
    EXISTS (SELECT 1 FROM snapshots s WHERE s.id = snapshot_positions.snapshot_id AND s.user_id = auth.uid())
  );

CREATE POLICY snapshot_positions_delete_own ON snapshot_positions
  FOR DELETE USING (
    EXISTS (SELECT 1 FROM snapshots s WHERE s.id = snapshot_positions.snapshot_id AND s.user_id = auth.uid())
  );

-- snapshot_transactions 정책 (snapshot_cash와 동일 패턴)
CREATE POLICY snapshot_transactions_select_own ON snapshot_transactions
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM snapshots s WHERE s.id = snapshot_transactions.snapshot_id AND s.user_id = auth.uid())
  );

CREATE POLICY snapshot_transactions_insert_own ON snapshot_transactions
  FOR INSERT WITH CHECK (
    EXISTS (SELECT 1 FROM snapshots s WHERE s.id = snapshot_transactions.snapshot_id AND s.user_id = auth.uid())
  );

CREATE POLICY snapshot_transactions_update_own ON snapshot_transactions
  FOR UPDATE USING (
    EXISTS (SELECT 1 FROM snapshots s WHERE s.id = snapshot_transactions.snapshot_id AND s.user_id = auth.uid())
  );

CREATE POLICY snapshot_transactions_delete_own ON snapshot_transactions
  FOR DELETE USING (
    EXISTS (SELECT 1 FROM snapshots s WHERE s.id = snapshot_transactions.snapshot_id AND s.user_id = auth.uid())
  );

-- categories 정책
CREATE POLICY categories_all_own ON categories
  FOR ALL USING (auth.uid() = user_id);

-- favorites 정책
CREATE POLICY favorites_all_own ON favorites
  FOR ALL USING (auth.uid() = user_id);

-- dashboard_prefs 정책
CREATE POLICY dashboard_prefs_all_own ON dashboard_prefs
  FOR ALL USING (auth.uid() = user_id);

-- rebalance_targets 정책
CREATE POLICY rebalance_targets_all_own ON rebalance_targets
  FOR ALL USING (auth.uid() = user_id);

-- rebalance_rules 정책
CREATE POLICY rebalance_rules_all_own ON rebalance_rules
  FOR ALL USING (auth.uid() = user_id);

-- portfolios 정책
CREATE POLICY portfolios_all_own ON portfolios
  FOR ALL USING (auth.uid() = user_id);

-- 공개 읽기 테이블 (instruments, prices_daily, fx_rates_daily, data_sources)
-- 모든 인증된 사용자가 읽을 수 있음
CREATE POLICY instruments_select_all ON instruments
  FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY prices_daily_select_all ON prices_daily
  FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY fx_rates_daily_select_all ON fx_rates_daily
  FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY data_sources_select_all ON data_sources
  FOR SELECT USING (auth.role() = 'authenticated');

ALTER TABLE instruments ENABLE ROW LEVEL SECURITY;
ALTER TABLE prices_daily ENABLE ROW LEVEL SECURITY;
ALTER TABLE fx_rates_daily ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_sources ENABLE ROW LEVEL SECURITY;

COMMENT ON POLICY users_select_own ON users IS '사용자 본인 정보만 조회';
COMMENT ON POLICY snapshots_all_own ON snapshots IS '사용자 본인 스냅샷만 접근';
