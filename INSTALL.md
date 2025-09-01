# Donmoa 설치 및 사용 가이드

## 📋 요구사항

- Python 3.8 이상
- pip (Python 패키지 관리자)

## 🚀 설치 방법

### 1. 저장소 클론

```bash
git clone https://github.com/yourusername/donmoa.git
cd donmoa
```

### 2. 가상환경 생성 (권장)

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 환경 설정

```bash
# 환경 변수 설정 (선택사항)
cp config/env.example config/.env
# .env 파일에 필요한 설정 입력
```

### 5. 디렉토리 구조 확인

프로젝트가 올바르게 설치되었는지 확인:

```
donmoa/
├── donmoa/                     # 메인 패키지
│   ├── core/                   # 핵심 로직
│   │   ├── donmoa.py          # 메인 클래스
│   │   ├── data_collector.py  # 데이터 수집
│   │   └── csv_exporter.py    # CSV 내보내기
│   ├── providers/              # 기관별 Provider
│   │   ├── __init__.py
│   │   ├── base.py            # 기본 Provider
│   │   ├── banksalad.py       # 뱅크샐러드 Provider
│   │   ├── domino.py          # 도미노 Provider
│   │   └── securities.py      # 증권사 Provider
│   ├── utils/                  # 유틸리티
│   │   ├── config.py          # 설정 관리
│   │   └── logger.py          # 로깅
│   ├── cli/                    # CLI 인터페이스
│   │   └── main.py            # CLI 메인
│   └── __main__.py            # CLI 진입점
├── data/                       # 데이터 디렉토리
│   ├── input/                  # 입력 파일 (Excel, MHTML 등)
│   └── export/                 # 출력 파일
├── config/                     # 통합 설정 디렉토리
│   ├── config.yaml             # 기본 설정
│   ├── deployment.yaml         # 배포 환경 설정
│   ├── env.example             # 환경 변수 예제
│   └── providers/              # Provider별 설정
│       ├── banksalad.yaml      # 뱅크샐러드 Provider 설정
│       └── domino.yaml         # 도미노 Provider 설정
├── tests/                      # 테스트 코드
├── logs/                       # 로그 파일
├── backups/                    # 백업 파일
├── requirements.txt            # Python 의존성
├── Dockerfile                  # Docker 이미지 정의
├── docker-compose.yml          # Docker Compose 설정
├── deploy.sh                   # 배포 스크립트
├── README.md                   # 프로젝트 설명
├── INSTALL.md                  # 이 파일
└── FOR_DEV.md                  # 개발자 가이드
```

## 🧪 테스트 실행

### 파일 파싱 테스트

```bash
python tests/test_file_parsing.py
```

### 배포 환경 기능 테스트

```bash
python tests/test_deployment.py
```

## 📖 사용 방법

### CLI 사용

```bash
# 데이터 수집 및 CSV 내보내기
python -m donmoa collect

# 특정 Provider만 수집
python -m donmoa collect --provider banksalad

# 상태 확인
python -m donmoa status

# Provider 연결 테스트
python -m donmoa test --provider banksalad

# 설정 확인
python -m donmoa config

# 배포 환경 모드
python -m donmoa --deployment health

# 도움말 보기
python -m donmoa --help
python -m donmoa collect --help
```

### Python API 사용

```python
from donmoa.core import Donmoa
from donmoa.providers.domino import DominoProvider
from donmoa.providers.banksalad import BanksaladProvider

# Donmoa 인스턴스 생성
donmoa = Donmoa()

# Provider 추가
domino_provider = DominoProvider("MySecurities")
banksalad_provider = BanksaladProvider("MyBank")
donmoa.add_provider(domino_provider)
donmoa.add_provider(banksalad_provider)

# 전체 워크플로우 실행
result = donmoa.run_full_workflow(
    temp_dir="./temp_data",
    output_dir="./export"
)

# 결과 확인
if result['status'] == 'success':
    print(f"성공! {result['total_data_records']}건 데이터 수집")
```

## 🔧 설정 파일

### config.yaml

주요 설정 항목:

```yaml
# 통합 계좌 리스트 설정
unified_accounts:
  - "주거래계좌"
  - "주식투자계좌"
  - "펀드투자계좌"
  - "급여계좌"
  - "사업자계좌"
  - "해외투자계좌"

# Provider 설정 파일 경로
providers:
  domino: "providers/domino.yaml"
  banksalad: "providers/banksalad.yaml"

# 내보내기 설정
export:
  output_dir: "./data/export"
  file_format: "csv"
  encoding: "utf-8"

# 로깅 설정
logging:
  level: "INFO"
  file: "./data/logs/donmoa.log"
  console: true

# 전역 성능 설정
performance:
  default_retry_count: 3
  default_timeout: 30
  max_concurrent_providers: 5
```

## 🚨 문제 해결

### 일반적인 오류

1. **ImportError: No module named 'donmoa'**
   - 프로젝트 루트 디렉토리에서 실행하고 있는지 확인
   - 가상환경이 활성화되어 있는지 확인

2. **ModuleNotFoundError: No module named 'requests'**
   - `pip install -r requirements.txt` 실행

3. **FileNotFoundError: config.yaml**
   - `config/config.yaml` 파일이 존재하는지 확인

4. **PermissionError: [Errno 13] Permission denied**
   - 출력 디렉토리에 쓰기 권한이 있는지 확인
   - 관리자 권한으로 실행 시도

### 설정 파일 관련

1. **설정 파일을 찾을 수 없음**
   - `config/` 폴더 내 설정 파일 존재 확인
   - `config/providers/` 폴더 내 Provider 설정 파일 확인

2. **Provider 설정 오류**
   - `config/providers/` 폴더 내 YAML 파일 확인
   - 파일 형식 및 문법 오류 확인

### 로그 확인

```bash
# 로그 파일 위치
./logs/donmoa.log

# 로그 레벨 변경 (config/config.yaml)
logging:
  level: "DEBUG"  # 더 상세한 로그
```

## 🔒 보안 고려사항

1. **API 키 보안**
   - `config/.env` 파일을 `.gitignore`에 추가
   - API 키를 소스 코드에 하드코딩하지 않음

2. **파일 권한**
   - 출력 디렉토리 접근 제한

3. **네트워크 보안**
   - HTTPS API 엔드포인트 사용
   - 방화벽 설정 확인

## 📞 지원

문제가 발생하거나 질문이 있으시면:

1. [Issues](https://github.com/yourusername/donmoa/issues) 페이지 확인
2. 새로운 이슈 생성
3. 프로젝트 문서 참조

## 🔄 업데이트

```bash
# 최신 코드 가져오기
git pull origin main

# 의존성 업데이트
pip install -r requirements.txt --upgrade

# 설정 파일 확인 (새로운 설정 항목 추가 여부)
```

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.
