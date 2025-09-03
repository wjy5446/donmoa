# Changelog

모든 주요 변경사항은 이 파일에 기록됩니다.

형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.0.0/)를 따르며,
이 프로젝트는 [Semantic Versioning](https://semver.org/lang/ko/)을 준수합니다.

## [Unreleased]

### Added
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

## [0.1.0] - 2024-01-XX

### Added
- 🚀 **초기 프로젝트 구조 설정**
  - Python 패키지 구조 (`donmoa/` 폴더)
  - 핵심 모듈: `core/`, `providers/`, `utils/`, `cli/`
  - CLI 인터페이스 (`click` 기반)
  - 설정 관리 시스템 (`config/` 폴더 통합)

- 🔧 **Provider 시스템 구현**
  - `BaseProvider` 추상 클래스
  - `BanksaladProvider`: Excel 파일 파싱 지원
  - `DominoProvider`: MHTML 파일 파싱 지원
  - `SecuritiesProvider`: 증권사 데이터 처리

- 📊 **데이터 처리 기능**
  - Excel (.xlsx, .xls) 파일 파싱
  - MHTML (.mhtml, .html, .htm) 파일 파싱
  - CSV (.csv) 파일 파싱
  - 데이터 정제 및 통합
  - CSV 내보내기 기능

- 🐳 **배포 환경 지원**
  - Docker 이미지 정의 (`Dockerfile`)
  - Docker Compose 설정 (`docker-compose.yml`)
  - 배포 스크립트 (`deploy.sh`)
  - 배포 환경 설정 (`config/deployment.yaml`)

- 🧪 **테스트 시스템**
  - 파일 파싱 테스트 (`tests/test_file_parsing.py`)
  - 배포 기능 테스트 (`tests/test_deployment.py`)
  - pytest 기반 테스트 프레임워크

- 📝 **문서화**
  - `README.md`: 프로젝트 개요 및 사용법
  - `INSTALL.md`: 설치 및 설정 가이드
  - `FOR_DEV.md`: 개발자 가이드
  - `CHANGELOG.md`: 변경사항 기록

### Changed
- 🔄 **설정 파일 구조 개선**
  - 모든 설정 파일을 `config/` 폴더로 통합
  - Provider별 설정을 `config/providers/` 하위로 정리
  - 설정 파일 경로 참조 방식 개선

- 🏗️ **프로젝트 구조 정리**
  - 불필요한 폴더 및 파일 제거
  - 데이터 디렉토리 구조 최적화 (`data/input/`, `data/export/`)
  - 로그 및 백업 디렉토리 정리

### Fixed
- 🐛 **CLI 인터페이스 개선**
  - `async` 키워드 충돌 해결 (`async_mode`로 변경)
  - 배포 환경 설정 파일 경로 수정
  - 상태 확인 함수의 Provider 구조 처리 개선

- 🔧 **설정 관리 시스템 수정**
  - 설정 파일 경로 참조 오류 수정
  - 환경 변수 파일 경로 업데이트
  - Provider 설정 로딩 로직 개선

### Security
- 🔒 **보안 강화**
  - 환경 변수 파일 분리 (`.env.example`)
  - API 키 및 민감 정보 보안 처리
  - 파일 권한 관리 개선

## [0.0.1] - 2024-01-XX

### Added
- 🎯 **프로젝트 초기 설정**
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
