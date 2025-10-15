-- 004_create_portfolio_views.sql
-- 포트폴리오 조회를 위한 뷰 및 헬퍼 함수

-- 최신 스냅샷 조회 뷰
CREATE OR REPLACE VIEW v_latest_snapshots AS
SELECT DISTINCT ON (user_id)
  id,
  user_id,
  snapshot_date,
  source,
  status,
  created_at
FROM snapshots
WHERE status = 'completed'
ORDER BY user_id, snapshot_date DESC, created_at DESC;

-- 계좌별 현금 잔액 뷰 (최신 스냅샷 기준)
CREATE OR REPLACE VIEW v_account_cash_balances AS
SELECT
  a.user_id,
  a.id AS account_id,
  a.name AS account_name,
  sc.currency,
  sc.amount_minor,
  s.snapshot_date
FROM accounts a
JOIN snapshot_cash sc ON a.id = sc.account_id
JOIN snapshots s ON sc.snapshot_id = s.id
JOIN v_latest_snapshots vs ON s.id = vs.id AND a.user_id = vs.user_id;

-- 계좌별 포지션 뷰 (최신 스냅샷 기준)
CREATE OR REPLACE VIEW v_account_positions AS
SELECT
  a.user_id,
  a.id AS account_id,
  a.name AS account_name,
  sp.instrument_id,
  i.symbol,
  i.name AS instrument_name,
  i.asset_class,
  i.subclass,
  sp.qty_nano,
  sp.avg_cost,
  sp.currency,
  s.snapshot_date
FROM accounts a
JOIN snapshot_positions sp ON a.id = sp.account_id
JOIN instruments i ON sp.instrument_id = i.id
JOIN snapshots s ON sp.snapshot_id = s.id
JOIN v_latest_snapshots vs ON s.id = vs.id AND a.user_id = vs.user_id;

-- 사용자별 전체 포트폴리오 요약 함수
CREATE OR REPLACE FUNCTION get_portfolio_summary(p_user_id UUID, p_date DATE DEFAULT NULL)
RETURNS TABLE (
  account_id BIGINT,
  account_name TEXT,
  cash_krw_minor BIGINT,
  equity_value_minor BIGINT,
  total_value_minor BIGINT
) AS $$
BEGIN
  -- p_date가 NULL이면 최신 스냅샷 날짜 사용
  IF p_date IS NULL THEN
    SELECT snapshot_date INTO p_date
    FROM v_latest_snapshots
    WHERE user_id = p_user_id;
  END IF;

  RETURN QUERY
  SELECT
    a.id AS account_id,
    a.name AS account_name,
    COALESCE(SUM(sc.amount_minor) FILTER (WHERE sc.currency = 'KRW'), 0) AS cash_krw_minor,
    0::BIGINT AS equity_value_minor, -- TODO: 포지션 평가액 계산
    COALESCE(SUM(sc.amount_minor) FILTER (WHERE sc.currency = 'KRW'), 0) AS total_value_minor
  FROM accounts a
  LEFT JOIN snapshots s ON s.user_id = a.user_id AND s.snapshot_date = p_date
  LEFT JOIN snapshot_cash sc ON sc.snapshot_id = s.id AND sc.account_id = a.id
  WHERE a.user_id = p_user_id
  GROUP BY a.id, a.name;
END;
$$ LANGUAGE plpgsql;

COMMENT ON VIEW v_latest_snapshots IS '사용자별 최신 완료된 스냅샷';
COMMENT ON VIEW v_account_cash_balances IS '계좌별 현금 잔액 (최신)';
COMMENT ON VIEW v_account_positions IS '계좌별 포지션 (최신)';
COMMENT ON FUNCTION get_portfolio_summary IS '사용자 포트폴리오 요약';
