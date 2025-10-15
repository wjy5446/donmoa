-- 006_create_user_prefs.sql
-- 사용자 설정 (카테고리, 즐겨찾기, 대시보드 설정)

-- 카테고리 (거래 분류)
CREATE TABLE IF NOT EXISTS categories (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  parent_id BIGINT REFERENCES categories(id) ON DELETE SET NULL,
  kind TEXT CHECK (kind IN ('income', 'expense', 'transfer', 'investment', 'other')),
  meta JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ
);

CREATE INDEX idx_categories_user ON categories(user_id);
CREATE INDEX idx_categories_parent ON categories(parent_id);
CREATE INDEX idx_categories_kind ON categories(kind);

CREATE TRIGGER categories_updated_at
  BEFORE UPDATE ON categories
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- 이제 snapshot_transactions의 category_id에 FK 추가
ALTER TABLE snapshot_transactions
  ADD CONSTRAINT fk_snapshot_transactions_category
  FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL;

-- 즐겨찾기
CREATE TABLE IF NOT EXISTS favorites (
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  instrument_id BIGINT NOT NULL REFERENCES instruments(id) ON DELETE CASCADE,
  starred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (user_id, instrument_id)
);

CREATE INDEX idx_favorites_user ON favorites(user_id);
CREATE INDEX idx_favorites_instrument ON favorites(instrument_id);

-- 대시보드 설정
CREATE TABLE IF NOT EXISTS dashboard_prefs (
  user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  layout JSONB NOT NULL DEFAULT '{"cards": [], "layout": "grid-2"}'::jsonb,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER dashboard_prefs_updated_at
  BEFORE UPDATE ON dashboard_prefs
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE categories IS '거래 카테고리 (사용자 정의)';
COMMENT ON TABLE favorites IS '즐겨찾기 종목';
COMMENT ON TABLE dashboard_prefs IS '대시보드 설정 (카드 배치, 레이아웃)';
