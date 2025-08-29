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
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 환경 설정

```bash
# 환경 변수 파일 복사
cp env.example .env

# 설정 파일 확인 (이미 config.yaml로 생성됨)
# 필요시 config.yaml 수정
```

### 5. .env 파일 설정

`.env` 파일을 열고 실제 API 키와 인증 정보를 입력하세요:

```env
# 증권사 API 설정
SECURITIES_API_KEY=your_actual_api_key
SECURITIES_SECRET=your_actual_secret
SECURITIES_ACCOUNT_NO=your_account_number

# 은행 API 설정
BANK_API_KEY=your_actual_api_key
BANK_SECRET=your_actual_secret
BANK_ACCOUNT_NO=your_account_number

# 거래소 API 설정
EXCHANGE_API_KEY=your_actual_api_key
EXCHANGE_SECRET=your_actual_secret
EXCHANGE_PASSPHRASE=your_passphrase
```

## 🧪 테스트 실행

### 기본 테스트

```bash
python test_donmoa.py
```

### 사용 예시 실행

```bash
python example_usage.py
```

## 📖 사용 방법

### CLI 사용

```bash
# 데이터 수집 및 CSV 내보내기
python -m donmoa collect

# 특정 Provider만 수집
python -m donmoa collect --provider MockSecurities

# 상태 확인
python -m donmoa status

# Provider 연결 테스트
python -m donmoa test --provider MockSecurities

# 설정 확인
python -m donmoa config

# 스케줄러 시작
python -m donmoa scheduler start

# 스케줄러 상태 확인
python -m donmoa scheduler status

# 스케줄러 중지
python -m donmoa scheduler stop
```

### Python API 사용

```python
from donmoa.core import Donmoa
from donmoa.providers.securities import MockSecuritiesProvider

# Donmoa 인스턴스 생성
donmoa = Donmoa()

# Provider 추가
provider = MockSecuritiesProvider("MySecurities")
donmoa.add_provider(provider)

# 전체 워크플로우 실행
result = donmoa.run_full_workflow()

# 결과 확인
if result['status'] == 'success':
    print(f"성공! {result['total_data_records']}건 데이터 수집")
```

## 🔧 설정 파일

### config.yaml

주요 설정 항목:

```yaml
# 스케줄 설정
schedule:
  enabled: true
  interval_hours: 24
  start_time: "09:00"

# 내보내기 설정
export:
  output_dir: "./export"
  file_format: "csv"
  encoding: "utf-8"

# Provider 설정
providers:
  securities:
    enabled: true
    retry_count: 3
    timeout: 30

# 로깅 설정
logging:
  level: "INFO"
  file: "./logs/donmoa.log"
  console: true
```

## 📁 프로젝트 구조

```
donmoa/
├── donmoa/                    # 메인 패키지
│   ├── __init__.py
│   ├── __main__.py           # CLI 진입점
│   ├── cli/                  # CLI 인터페이스
│   │   ├── __init__.py
│   │   └── main.py
│   ├── core/                 # 핵심 기능
│   │   ├── __init__.py
│   │   ├── donmoa.py         # 메인 클래스
│   │   ├── data_collector.py # 데이터 수집
│   │   ├── csv_exporter.py   # CSV 내보내기
│   │   └── scheduler.py      # 스케줄러
│   ├── providers/            # 기관별 Provider
│   │   ├── __init__.py
│   │   ├── base.py           # 기본 Provider 클래스
│   │   └── securities.py     # 증권사 Provider 예시
│   └── utils/                # 유틸리티
│       ├── __init__.py
│       ├── logger.py         # 로깅
│       ├── config.py         # 설정 관리
│       └── encryption.py     # 암호화
├── requirements.txt           # 의존성
├── config.yaml               # 설정 파일
├── env.example               # 환경 변수 예시
├── example_usage.py          # 사용 예시
├── test_donmoa.py            # 테스트 스크립트
├── README.md                 # 프로젝트 설명
└── INSTALL.md                # 이 파일
```

## 🚨 문제 해결

### 일반적인 오류

1. **ImportError: No module named 'donmoa'**
   - 프로젝트 루트 디렉토리에서 실행하고 있는지 확인
   - 가상환경이 활성화되어 있는지 확인

2. **ModuleNotFoundError: No module named 'requests'**
   - `pip install -r requirements.txt` 실행

3. **FileNotFoundError: config.yaml**
   - `config.yaml` 파일이 프로젝트 루트에 있는지 확인

4. **PermissionError: [Errno 13] Permission denied**
   - 출력 디렉토리에 쓰기 권한이 있는지 확인
   - 관리자 권한으로 실행 시도

### 로그 확인

```bash
# 로그 파일 위치
./logs/donmoa.log

# 로그 레벨 변경 (config.yaml)
logging:
  level: "DEBUG"  # 더 상세한 로그
```

## 🔒 보안 고려사항

1. **API 키 보안**
   - `.env` 파일을 `.gitignore`에 추가
   - API 키를 소스 코드에 하드코딩하지 않음
   - 암호화된 저장소 사용 고려

2. **파일 권한**
   - 암호화 키 파일은 적절한 권한 설정
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
