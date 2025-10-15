-- 001_create_users_and_auth.sql
-- 사용자 및 인증 관련 테이블

-- users 테이블 (Supabase Auth와 연동)
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  display_name TEXT,
  settings JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ
);

-- users 인덱스
CREATE INDEX idx_users_email ON users(email);

-- users 트리거 (updated_at 자동 갱신)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_updated_at
  BEFORE UPDATE ON users
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- 기관 (증권사, 은행 등)
CREATE TABLE IF NOT EXISTS institutions (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  kind TEXT NOT NULL CHECK (kind IN ('securities', 'bank', 'crypto', 'pension', 'other')),
  meta JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ
);

CREATE INDEX idx_institutions_user_id ON institutions(user_id);
CREATE INDEX idx_institutions_kind ON institutions(kind);

CREATE TRIGGER institutions_updated_at
  BEFORE UPDATE ON institutions
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- 계좌
CREATE TABLE IF NOT EXISTS accounts (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  institution_id BIGINT REFERENCES institutions(id) ON DELETE SET NULL,
  name TEXT NOT NULL,
  type TEXT NOT NULL CHECK (type IN ('investment', 'savings', 'checking', 'pension', 'crypto', 'other')),
  currency TEXT NOT NULL DEFAULT 'KRW',
  meta JSONB DEFAULT '{}'::jsonb,
  valid_from DATE,
  valid_to DATE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ,
  CONSTRAINT valid_date_range CHECK (valid_to IS NULL OR valid_from <= valid_to)
);

CREATE INDEX idx_accounts_user_id ON accounts(user_id);
CREATE INDEX idx_accounts_institution_id ON accounts(institution_id);
CREATE INDEX idx_accounts_name ON accounts(name);

CREATE TRIGGER accounts_updated_at
  BEFORE UPDATE ON accounts
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- 계정 외부 ID 매핑 테이블 (CLI에서 사용하는 계좌명 -> DB ID 매핑)
CREATE TABLE IF NOT EXISTS account_external_ids (
  account_id BIGINT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
  external_id TEXT NOT NULL,
  source TEXT NOT NULL, -- 'cli', 'banksalad', 'domino', etc.
  PRIMARY KEY (external_id, source)
);

CREATE INDEX idx_account_external_ids_account ON account_external_ids(account_id);

COMMENT ON TABLE users IS '사용자 기본 정보';
COMMENT ON TABLE institutions IS '금융 기관 (증권사, 은행 등)';
COMMENT ON TABLE accounts IS '계좌 정보';
COMMENT ON TABLE account_external_ids IS '계좌 외부 ID 매핑 (CLI 등에서 사용)';
