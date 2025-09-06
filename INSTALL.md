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

### 4. 디렉토리 구조 확인

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
│   ├── config.yaml            # 메인 설정 파일
│   ├── accounts.yaml          # 계좌 설정 파일
│   └── providers/             # Provider별 설정
│       ├── banksalad.yaml     # 뱅크샐러드 설정
│       ├── domino.yaml        # 도미노 설정
│       └── securities.yaml    # 증권사 설정
├── logs/                       # 로그 파일
├── requirements.txt            # Python 의존성
└── README.md                   # 프로젝트 설명
```

## ⚙️ 설정

### 1. 계좌 설정

`config/accounts.yaml` 파일에서 계좌 정보를 설정합니다:

```yaml
accounts:
  - name: "통합계좌1"
    type: "증권"
    mapping_name: ["증권계좌1", "증권계좌2"]
  - name: "통합계좌2"
    type: "은행"
    mapping_name: ["은행계좌1"]
```

### 2. Provider 설정

각 Provider의 설정 파일을 수정합니다:

- `config/providers/banksalad.yaml`: 뱅크샐러드 설정
- `config/providers/domino.yaml`: 도미노 설정
- `config/providers/securities.yaml`: 증권사 설정

### 3. 메인 설정

`config/config.yaml`에서 전역 설정을 관리합니다:

```yaml
schedule:
  enabled: true
  interval_hours: 24
  start_time: "09:00"

export:
  output_dir: "./export"
  file_format: "csv"
  encoding: "utf-8"

providers:
  banksalad: "config/providers/banksalad.yaml"
  domino: "config/providers/domino.yaml"
  securities: "config/providers/securities.yaml"

accounts: "config/accounts.yaml"

logging:
  level: "INFO"
  file: "./logs/donmoa.log"
  console: true
```

## 🚀 사용법

### CLI 사용

```bash
# 도움말 보기
python -m donmoa --help

# 데이터 수집 및 내보내기
python -m donmoa collect

# 특정 Provider만 실행
python -m donmoa collect --provider banksalad

# 설정 확인
python -m donmoa config show
```

### Python 모듈로 사용

```python
from donmoa.core.donmoa import Donmoa

# Donmoa 인스턴스 생성
donmoa = Donmoa()

# 데이터 수집
donmoa.collect_data()

# 데이터 내보내기
donmoa.export_data()
```

## 📝 데이터 구조

### 입력 데이터

- **Excel 파일**: `data/input/` 디렉토리에 `.xlsx` 파일
- **MHTML 파일**: `data/input/` 디렉토리에 `.mhtml` 파일

### 출력 데이터

- **CSV 파일**: `data/export/` 디렉토리에 생성
- **파일명 형식**: `{provider}_{account}_{timestamp}.csv`

## 🚨 문제 해결

### 일반적인 문제

1. **설정 파일 오류**
   - YAML 문법 확인
   - 파일 경로 확인

2. **의존성 문제**
   - 가상환경 활성화 확인
   - `pip install -r requirements.txt` 재실행

3. **권한 문제**
   - 로그 디렉토리 쓰기 권한 확인
   - 출력 디렉토리 쓰기 권한 확인

### 로그 확인

```bash
# 로그 파일 위치
tail -f logs/donmoa.log

# 디버그 모드로 실행
python -m donmoa collect --debug
```

## 📝 개발자 가이드

### 프로젝트 구조

- `donmoa/core/`: 핵심 비즈니스 로직
- `donmoa/providers/`: 기관별 데이터 수집 로직
- `donmoa/utils/`: 공통 유틸리티
- `donmoa/cli/`: 명령줄 인터페이스

### 새로운 Provider 추가

1. `donmoa/providers/` 디렉토리에 새 파일 생성
2. `BaseProvider` 클래스 상속
3. `config/providers/` 디렉토리에 설정 파일 추가
4. `config/config.yaml`에 Provider 등록

### 테스트

```bash
# 단위 테스트 실행
python -m pytest tests/

# 특정 테스트 실행
python -m pytest tests/test_providers.py
```

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 지원

문제가 발생하거나 질문이 있으시면 이슈를 생성해 주세요.

---

**참고**: 이 가이드는 프로젝트의 기본적인 설치 및 사용법을 다룹니다. 더 자세한 내용은 `README.md`와 `FOR_DEV.md`를 참조하세요.
