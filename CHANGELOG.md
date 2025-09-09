# Changelog

모든 주요 변경사항은 이 파일에 기록됩니다.

형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.0.0/)를 따르며,
이 프로젝트는 [Semantic Versioning](https://semver.org/lang/ko/)을 준수합니다.

## [Unreleased]

## [0.3.0] - 2025-01-15

### Added
- **ManualProvider 추가**: 수동 입력을 위한 Excel 파일 파싱 지원
  - Excel 템플릿 자동 생성 기능 (`template` 명령어)
  - 수동 입력 데이터를 표준 스키마로 변환
  - `data/input/YYYY-MM-DD/manual.xlsx` 파일 지원
- **통일된 데이터 스키마**: 모든 Provider에서 동일한 스키마 사용
  - `CashSchema`: 현금 데이터 (날짜, 카테고리, 계좌, 잔액, 통화)
  - `PositionSchema`: 포지션 데이터 (날짜, 계좌, 자산명, 티커, 수량, 평단가)
  - `TransactionSchema`: 거래 데이터 (날짜, 계좌, 거래유형, 금액, 카테고리)
- **Excel 템플릿 생성기**: `TemplateGenerator` 클래스 추가
  - 사용자 친화적인 Excel 템플릿 자동 생성
  - 필수/선택 필드 구분 및 가이드 제공
- **날짜별 폴더 구조**: `data/input/YYYY-MM-DD/` 형태의 입력 폴더 구조
- **계좌 매핑 시스템**: `config/accounts.yaml`을 통한 계좌 통합 관리

### Changed
- **Provider 구조 개선**: BaseProvider 추상 클래스 개선
  - 필수 메서드 명확화 (`get_supported_extensions`, `parse_raw`, `parse_cash`, `parse_positions`, `parse_transactions`)
  - 공통 유틸리티 메서드 통합
  - 일관된 에러 처리 및 로깅
- **데이터 수집 최적화**: DataCollector 개선
  - 날짜별 폴더 자동 감지
  - Provider별 데이터 통합 로직 개선
  - 빈 데이터 처리 개선
- **CSV 내보내기 개선**: CSVExporter 정리
  - 사용하지 않는 메서드 제거 (`export_provider_data_to_csv`)
  - 통합된 데이터만 내보내기로 단순화
- **CLI 명령어 추가**: `template` 명령어로 Excel 템플릿 생성
- **문서 업데이트**: README.md, INSTALL.md에 ManualProvider 및 템플릿 기능 반영

### Fixed
- **코드 중복 제거**: BaseProvider와 ManualProvider 간 중복 메서드 제거
- **메모리 사용량 최적화**: 빈 DataFrame으로 초기화하여 일관성 개선
- **날짜 형식 통일**: 모든 Provider에서 `strftime` 사용으로 통일
- **에러 처리 개선**: Provider별 예외 처리 강화

### Removed
- **사용하지 않는 메서드**: CSVExporter의 `export_provider_data_to_csv` 메서드 제거
- **중복 코드**: ManualProvider의 `_find_input_file` 메서드 제거 (BaseProvider에서 상속)
- **불필요한 의존성**: requirements.txt에서 사용하지 않는 라이브러리 제거

### Security
- **설정 파일 보안**: 민감한 정보 분리 및 환경 변수 지원
- **입력 데이터 검증**: 수동 입력 데이터의 유효성 검증 강화

## [0.2.0] - 2025-09-06

### Added
- **완전한 CLI 인터페이스**: `collect`, `status`, `test`, `config`, `health`, `backup`, `maintenance` 명령어 지원
- **Rich UI 지원**: 진행률 표시, 테이블 출력, 색상 구분을 통한 사용자 친화적 인터페이스
- **고급 데이터 검증**: Provider별 데이터 유효성 검증 및 교차 검증 기능
- **백업 및 복원 시스템**: 자동 백업 생성, 복원, 백업 목록 관리 기능
- **시스템 유지보수 도구**: 데이터 정리, 저장소 최적화, 공간 정리 기능
- **상태 모니터링**: 실시간 시스템 상태 확인 및 메트릭 수집
- **Provider 연결 테스트**: 개별 Provider 연결 상태 및 데이터 수집 테스트
- **설정 관리**: 통합 설정 파일 관리 및 환경별 설정 지원
- **워크플로우 결과 저장**: 실행 결과를 JSON 파일로 저장하여 추적 가능
- **다중 폴더 구조**: `all`, `domino` 등 Provider별 하위 폴더 지원

### Changed
- **CLI 구조 개선**: Click 기반 계층적 명령어 구조로 재구성
- **에러 처리 강화**: 상세한 에러 메시지 및 복구 가이드 제공
- **로그 시스템 개선**: 구조화된 로깅 및 디버그 모드 지원
- **데이터 수집 최적화**: 비동기 처리 및 성능 개선
- **CSV 내보내기 개선**: donmoa 표준 형식(position.csv, cash.csv) 지원
- **문서 간소화**: README.md에서 고급 기능 설명 제거, 핵심 기능에 집중
- **출력 데이터 형식**: 2025년 9월 6일 기준 최신 데이터 형식 적용

### Fixed
- **Provider 등록 로직**: 자동 Provider 등록 및 설정 적용 개선
- **데이터 파싱 안정성**: MHTML 파일 파싱 오류 처리 강화
- **메모리 관리**: 대용량 데이터 처리 시 메모리 사용량 최적화
- **파일 경로 처리**: 크로스 플랫폼 파일 경로 처리 개선

### Security
- **설정 파일 보안**: 민감한 정보 분리 및 환경 변수 지원
- **백업 암호화**: 백업 파일 보안 강화 (향후 구현 예정)

## [0.1.0] - 2025-09-01

### Added
- **pandas DataFrame 기반 아키텍처**: 효율적인 데이터 처리 및 분석
- **새로운 Provider 인터페이스**: raw data → DataFrame 변환에 특화
- **DataCollector 통합 기능**: 여러 provider DataFrame을 통합하여 최종 데이터 생성
- **Domino Provider**: 도미노 증권 MHTML 파일 파싱 지원
  - 포지션 데이터 추출 (계좌별 자산 보유량)
  - 현금 데이터 추출 (원화, 달러, 엔화)
  - MHTML 파일에서 HTML 파싱 및 데이터 추출
- **donmoa 형태 CSV 내보내기**: `export` 명령 추가
  - `position.csv`: 계좌명, 자산명, 티커, 보유량, 평단가, 수행일시
  - `cash.csv`: 자산명, 보유량, 수행일시
- **날짜별 폴더 구조**: `data/export/{YYYYMMDD}/` 폴더에 CSV 파일 저장
- **자동 Provider 등록**: 기본 Provider 자동 등록 기능

### Changed
- **Provider 구조 개선**: raw data 파싱과 CSV export 역할 분리
- **DataCollector 역할 확장**: DataFrame 통합 및 최종 CSV export 담당
- **Provider 이름**: `domino_securities` → `domino`로 단순화
- **파일명 구조**: 타임스탬프 포함 파일명 → 날짜별 폴더 + 단순 파일명
- **설정 파일**: `config/config.yaml`에서 Provider 이름 통일

### Removed
- **scripts/analyze_domino_mhtml.py**: 독립 스크립트 → donmoa Provider로 통합
- **domino_positions.csv**: 불필요한 중간 파일 제거

### Fixed
- **설정 파일 로드**: Provider 설정 파일 경로 문제 해결
- **데이터 파싱**: MHTML 파일에서 정확한 데이터 추출
- **코드 정리**: 린터 오류 수정 및 코드 스타일 개선

## [0.0.1] - 2025-08-XX

### Added
-  **프로젝트 초기 설정**
  - 기본 Python 패키지 구조
  - 의존성 관리 (`requirements.txt`)
  - 가상환경 설정 (`.venv/`)

---

## 버전 관리 규칙

### Semantic Versioning (MAJOR.MINOR.PATCH)

- **MAJOR**: 호환되지 않는 API 변경
- **MINOR**: 이전 버전과 호환되는 새로운 기능 추가
- **PATCH**: 이전 버전과 호환되는 버그 수정

### 변경사항 분류

- **Added**: 새로운 기능
- **Changed**: 기존 기능의 변경
- **Deprecated**: 곧 제거될 기능
- **Removed**: 제거된 기능
- **Fixed**: 버그 수정
- **Security**: 보안 관련 수정

## 기여자

이 프로젝트에 기여해주신 모든 분들께 감사드립니다.

---

**참고**: 이 파일은 [Keep a Changelog](https://keepachangelog.com/) 형식을 따릅니다.
