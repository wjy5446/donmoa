# Donmoa - 개인 자산 관리 도구

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

Donmoa는 여러 금융 기관의 데이터를 통합하여 개인이 손쉽게 관리할 수 있도록 돕는 개인 자산 관리 도구입니다.

## ✨ 주요 기능

- **통합 데이터 관리**: 뱅크샐러드, 도미노 증권, 수동 입력 등 여러 기관의 데이터를 하나로 통합
- **자동화된 워크플로우**: 파일 업로드부터 CSV 내보내기까지 자동화
- **CLI 인터페이스**: 명령줄에서 간편하게 사용
- **Excel 템플릿 지원**: 수동 데이터 입력을 위한 Excel 템플릿 자동 생성

## 🚀 빠른 시작

### 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/donmoa.git
cd donmoa

# 가상환경 생성 및 활성화
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# 의존성 설치
pip install -r requirements.txt
```

### 기본 사용법

```bash
# 1. 데이터 파일 준비
# data/input/YYYY-MM-DD/ 폴더에 다음 파일들을 넣어주세요:
# - domino.mhtml (도미노 증권 포트폴리오)
# - banksalad.xlsx (뱅크샐러드 계좌 데이터)
# - manual.xlsx (수동 입력 데이터)

# 2. 데이터 수집 및 통합
python -m donmoa collect

# 3. 상태 확인
python -m donmoa status

# 4. 수동 입력 템플릿 생성
python -m donmoa template

# 5. 도움말 보기
python -m donmoa --help
```

## 🏗️ 아키텍처

### 데이터 플로우
```
입력 파일 → Provider 파싱 → 스키마 변환 → 데이터 통합 → CSV 내보내기
```

### 핵심 컴포넌트
- **DominoProvider**: 도미노 증권 MHTML 파일 파싱
- **BanksaladProvider**: 뱅크샐러드 Excel 파일 파싱
- **ManualProvider**: 수동 입력 Excel 파일 파싱
- **DataCollector**: 여러 Provider 데이터 수집 및 통합
- **CSVExporter**: 표준화된 CSV 파일 생성
- **TemplateGenerator**: 수동 입력용 Excel 템플릿 생성
- **통일된 스키마**: CashSchema, PositionSchema, TransactionSchema

## 📁 프로젝트 구조

```
📁 donmoa/                    # 메인 패키지
├── 📁 core/                  # 핵심 로직 (Donmoa, DataCollector, CSVExporter, TemplateGenerator)
├── 📁 providers/             # Provider 구현 (Domino, Banksalad, Manual)
├── 📁 utils/                 # 유틸리티 (Config, Logger, DateUtils)
└── 📁 cli/                   # CLI 인터페이스

📁 config/                    # 설정 파일
├── 📄 config.yaml            # 기본 설정
├── 📄 accounts.yaml          # 계좌 매핑 설정
└── 📄 env.example            # 환경 변수 예시

📁 data/                      # 데이터 디렉토리
├── 📁 input/                 # 입력 파일
│   └── 📁 YYYY-MM-DD/        # 날짜별 폴더 (domino.mhtml, banksalad.xlsx, manual.xlsx)
└── 📁 export/                # 출력 CSV 파일 (cash.csv, positions.csv, transactions.csv)

📁 logs/                      # 로그 파일
📄 requirements.txt            # Python 의존성
```

## 🔧 설정

### 기본 설정
프로젝트는 `config/config.yaml`에서 기본 설정을 관리합니다:

```yaml
# 내보내기 설정
export:
  output_dir: "./data/export"
  encoding: "utf-8"

# 로깅 설정
logging:
  level: "INFO"
  file: "./logs/donmoa.log"
```

### 계좌 매핑 설정

1. **예시 파일 복사**:
   ```bash
   cp config/accounts.yaml.example config/accounts.yaml
   ```

2. **계좌 정보 수정**: `config/accounts.yaml`에서 실제 계좌 정보에 맞게 수정합니다:

```yaml
accounts:
  - name: "월급통장-기업"
    type: "은행"
    mapping_name: ["월급통장-기업", "기업은행 월급통장"]

  - name: "주식계좌-삼성"
    type: "증권"
    mapping_name: ["주식계좌-삼성", "삼성증권 주식계좌"]

  - name: "페이서비스"
    type: "페이"
    mapping_name: ["페이", "카카오페이", "네이버페이", "토스페이"]
```

> **중요**: `accounts.yaml`은 개인 정보이므로 `.gitignore`에 추가되어 버전 관리에서 제외됩니다.
> 실제 계좌 정보는 `accounts.yaml`에, 예시는 `accounts.yaml.example`에 저장됩니다.

## 🔌 지원 Provider

### Domino Provider (도미노 증권)
- **입력**: `data/input/YYYY-MM-DD/domino.mhtml` (도미노 증권 포트폴리오 페이지)
- **출력**: `positions.csv`, `cash.csv`
- **데이터**: 계좌별 자산 보유량, 현금 보유량

### Banksalad Provider (뱅크샐러드)
- **입력**: `data/input/YYYY-MM-DD/banksalad.xlsx` (뱅크샐러드 계좌 데이터)
- **출력**: `cash.csv`, `transactions.csv`
- **데이터**: 은행/증권사 계좌별 잔고 정보, 거래 내역

### Manual Provider (수동 입력)
- **입력**: `data/input/YYYY-MM-DD/manual.xlsx` (수동 입력 데이터)
- **출력**: `cash.csv`, `positions.csv`, `transactions.csv`
- **데이터**: 사용자가 직접 입력한 자산 데이터

## 📊 출력 파일

### cash.csv (현금 데이터)
```csv
date,category,account,balance,currency,provider,collected_at
2025-01-15,증권,증권,2467838.0,KRW,domino,2025-01-15T10:30:00
2025-01-15,은행,주거래계좌,5000000.0,KRW,banksalad,2025-01-15T10:30:00
```

### positions.csv (포지션 데이터)
```csv
date,account,name,ticker,quantity,average_price,currency,provider,collected_at
2025-01-15,위탁종합,팔란티어,PLTR,8.0,225902.0,KRW,domino,2025-01-15T10:30:00
2025-01-15,투자계좌,삼성전자,005930,100.0,70000.0,KRW,manual,2025-01-15T10:30:00
```

### transactions.csv (거래 데이터)
```csv
date,account,transaction_type,amount,category,category_detail,currency,note,provider,collected_at
2025-01-15,주거래계좌,입금,1000000.0,급여,월급,KRW,1월 급여,banksalad,2025-01-15T10:30:00
```

## 📖 사용 방법

### 기본 워크플로우

```bash
# 1. 데이터 파일 준비
# data/input/YYYY-MM-DD/ 폴더에 파일들을 넣어주세요

# 2. 데이터 수집 및 통합
python -m donmoa collect

# 3. 상태 확인
python -m donmoa status

# 4. 수동 입력 템플릿 생성
python -m donmoa template

# 5. 도움말 보기
python -m donmoa --help
```

### 고급 사용법

```bash
# 특정 입력 디렉토리 지정
python -m donmoa collect --input-dir data/input/2025-01-15

# 출력 디렉토리 지정
python -m donmoa collect --output-dir data/export/custom

# 설정 파일 지정
python -m donmoa collect --config custom_config.yaml
```

### Python API 사용

```python
from donmoa.core.donmoa import Donmoa

# Donmoa 인스턴스 생성
donmoa = Donmoa()

# 전체 워크플로우 실행
result = donmoa.run_full_workflow()

# 결과 확인
if result['status'] == 'success':
    print(f"성공! {result['total_records']}개 레코드 처리")
    for file_type, file_path in result['exported_files'].items():
        print(f"{file_type}: {file_path}")
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

### 로그 확인

```bash
# 로그 파일 위치
./logs/donmoa.log

# 로그 레벨 변경 (config/config.yaml)
logging:
  level: "DEBUG"  # 더 상세한 로그
```

## 📞 지원

문제가 발생하거나 질문이 있으시면:

1. [Issues](https://github.com/yourusername/donmoa/issues) 페이지 확인
2. 새로운 이슈 생성
3. 프로젝트 문서 참조

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

**Donmoa** - 개인 자산 관리의 새로운 시작 🚀
