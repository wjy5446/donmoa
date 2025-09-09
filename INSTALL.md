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
- **Docker 지원**: 컨테이너화된 배포 환경
- **pandas DataFrame 기반**: 효율적인 데이터 처리 및 분석

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
# data/input/ 폴더에 다음 파일들을 넣어주세요:
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

## 📋 아키텍처

### 데이터 플로우
```
입력 파일 → Provider 파싱 → DataFrame 변환 → 데이터 통합 → CSV 내보내기
```

### 핵심 컴포넌트
- **DominoProvider**: 도미노 증권 MHTML 파일 파싱
- **BanksaladProvider**: 뱅크샐러드 Excel 파일 파싱
- **ManualProvider**: 수동 입력 Excel 파일 파싱
- **DataCollector**: 여러 Provider 데이터 수집 및 통합
- **CSVExporter**: 표준화된 CSV 파일 생성
- **TemplateGenerator**: 수동 입력용 Excel 템플릿 생성

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
├── 📁 input/                 # 입력 파일 (domino.mhtml, banksalad.xlsx, manual.xlsx)
└── 📁 export/                # 출력 CSV 파일 (cash.csv, positions.csv, transactions.csv)

📄 requirements.txt            # Python 의존성
📄 docker-compose.yml         # Docker 설정
```

## 📝 설정

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
`config/accounts.yaml`에서 계좌 매핑을 설정합니다:

```yaml
accounts:
  - name: "통합계좌1"
    mapping_name: ["증권계좌1", "증권계좌2"]
  - name: "통합계좌2"
    mapping_name: ["은행계좌1"]
```

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

## 🚀 사용 방법

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
# 특정 Provider만 수집
python -m donmoa collect --provider manual

# 특정 날짜 폴더 지정
python -m donmoa collect --input-dir data/input/2025-01-15

# 출력 디렉토리 지정
python -m donmoa collect --output-dir data/export/custom
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

## 🧪 테스트

```bash
# 파일 파싱 테스트
python tests/test_file_parsing.py

# 배포 환경 기능 테스트
python tests/test_deployment.py
```

## 🔄 Docker 배포

```bash
# Docker Compose로 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

## 📝 문제 해결

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

```

```markdown:FOR_DEV.md
# Donmoa 개발자 가이드

## 📦 개발 환경 설정

### 필수 요구사항

- Python 3.8 이상
- pip (Python 패키지 관리자)
- Git
- 가상환경 도구 (venv, conda 등)

### 개발 환경 구축

```bash
# 저장소 클론
git clone https://github.com/yourusername/donmoa.git
cd donmoa

# 가상환경 생성 및 활성화
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# 개발 의존성 설치
pip install -r requirements.txt

# 개발 도구 설치 (선택사항)
pip install black flake8 mypy pytest-cov
```

## 📁 프로젝트 아키텍처

### 핵심 구조

```
donmoa/
├── core/                    # 핵심 비즈니스 로직
│   ├── donmoa.py          # 메인 Donmoa 클래스
│   ├── data_collector.py  # 데이터 수집 관리
│   ├── csv_exporter.py    # CSV 내보내기
│   ├── template_generator.py  # Excel 템플릿 생성
│   └── schemas.py         # 데이터 스키마 정의
├── providers/              # Provider 구현
│   ├── base.py            # 기본 Provider 클래스
│   ├── banksalad.py       # 뱅크샐러드 Provider
│   ├── domino.py          # 도미노 Provider
│   └── manual.py          # 수동 입력 Provider
├── utils/                  # 유틸리티
│   ├── config.py          # 설정 관리
│   ├── logger.py          # 로깅
│   └── date_utils.py      # 날짜 유틸리티
└── cli/                    # CLI 인터페이스
    └── main.py            # CLI 메인
```

### 아키텍처 패턴

1. **Provider 패턴**: 각 금융 기관별로 독립적인 Provider 구현
2. **Strategy 패턴**: 데이터 파싱 전략을 Provider별로 구현
3. **Factory 패턴**: Provider 인스턴스 생성 관리
4. **Observer 패턴**: 데이터 수집 진행 상황 모니터링

## 📝 개발 가이드라인

### 코드 스타일

- **Python PEP 8** 준수
- **Type Hints** 사용 (Python 3.8+)
- **Docstring** 작성 (Google 스타일)
- **한글 주석** 사용 (비즈니스 로직 설명)

### 예시 코드

```python
from typing import Dict, List, Optional, Any
from pathlib import Path
import pandas as pd
from .base import BaseProvider
from ..core.schemas import CashSchema, PositionSchema, TransactionSchema

class ExampleProvider(BaseProvider):
    """예시 Provider 클래스

    이 클래스는 Provider 구현의 예시를 보여줍니다.
    """

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """Provider 초기화

        Args:
            name: Provider 이름
            config: Provider 설정 (선택사항)
        """
        super().__init__(name, config)

    def get_supported_extensions(self) -> List[str]:
        """지원하는 파일 확장자 목록을 반환합니다."""
        return [".xlsx", ".csv"]

    def parse_raw(self, file_path: Path) -> Dict[str, pd.DataFrame]:
        """원본 데이터를 파싱합니다."""
        # 실제 파싱 로직 구현
        pass

    def parse_cash(self, data: Dict[str, pd.DataFrame]) -> List[CashSchema]:
        """현금 데이터를 파싱합니다."""
        # 실제 파싱 로직 구현
        pass

    def parse_positions(self, data: Dict[str, pd.DataFrame]) -> List[PositionSchema]:
        """포지션 데이터를 파싱합니다."""
        # 실제 파싱 로직 구현
        pass

    def parse_transactions(self, data: Dict[str, pd.DataFrame]) -> List[TransactionSchema]:
        """거래 데이터를 파싱합니다."""
        # 실제 파싱 로직 구현
        pass
```

## 📝 테스트 작성

### 테스트 구조

```
tests/
├── test_file_parsing.py    # 파일 파싱 테스트
├── test_deployment.py      # 배포 기능 테스트
├── conftest.py             # pytest 설정
└── fixtures/               # 테스트 데이터
    ├── sample_banksalad.xlsx
    ├── sample_domino.mhtml
    └── sample_manual.xlsx
```

### 테스트 작성 예시

```python
import pytest
from pathlib import Path
from donmoa.providers.banksalad import BanksaladProvider

class TestBanksaladProvider:
    """뱅크샐러드 Provider 테스트 클래스"""

    @pytest.fixture
    def provider(self):
        """테스트용 Provider 인스턴스"""
        return BanksaladProvider("TestBank")

    @pytest.fixture
    def sample_file(self, tmp_path):
        """테스트용 샘플 파일"""
        file_path = tmp_path / "test_banksalad.xlsx"
        # 샘플 파일 생성 로직
        return file_path

    def test_collect_all_success(self, provider, sample_file):
        """데이터 수집 성공 테스트"""
        result = provider.collect_all(sample_file)

        assert 'cash' in result
        assert 'positions' in result
        assert 'transactions' in result
        assert len(result['cash']) > 0

    def test_parse_raw_invalid_format(self, provider, tmp_path):
        """잘못된 파일 형식 테스트"""
        invalid_file = tmp_path / "test.txt"
        invalid_file.write_text("invalid content")

        with pytest.raises(Exception):
            provider.parse_raw(invalid_file)
```

### 테스트 실행

```bash
# 전체 테스트 실행
pytest

# 특정 테스트 파일 실행
pytest tests/test_file_parsing.py

# 커버리지 포함 테스트
pytest --cov=donmoa

# 상세 출력
pytest -v

# 실패한 테스트만 재실행
pytest --lf
```

## 🔄 Provider 추가 방법

### 1. 새로운 Provider 클래스 생성

```python
# donmoa/providers/new_provider.py
from typing import Dict, Any, List
from pathlib import Path
import pandas as pd
from .base import BaseProvider
from ..core.schemas import CashSchema, PositionSchema, TransactionSchema

class NewProvider(BaseProvider):
    """새로운 금융 기관 Provider"""

    def __init__(self, name: str = "new_provider", config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)

    def get_supported_extensions(self) -> List[str]:
        """지원하는 파일 확장자 목록을 반환합니다."""
        return [".xlsx", ".csv"]

    def parse_raw(self, file_path: Path) -> Dict[str, pd.DataFrame]:
        """원본 데이터를 파싱합니다."""
        # 실제 파싱 로직 구현
        return {
            "cash": pd.DataFrame(),
            "positions": pd.DataFrame(),
            "transactions": pd.DataFrame()
        }

    def parse_cash(self, data: Dict[str, pd.DataFrame]) -> List[CashSchema]:
        """현금 데이터를 파싱합니다."""
        # 실제 파싱 로직 구현
        return []

    def parse_positions(self, data: Dict[str, pd.DataFrame]) -> List[PositionSchema]:
        """포지션 데이터를 파싱합니다."""
        # 실제 파싱 로직 구현
        return []

    def parse_transactions(self, data: Dict[str, pd.DataFrame]) -> List[TransactionSchema]:
        """거래 데이터를 파싱합니다."""
        # 실제 파싱 로직 구현
        return []
```

### 2. Provider 등록

```python
# donmoa/core/donmoa.py에 추가
from ..providers.new_provider import NewProvider

def _register_default_providers(self) -> None:
    """설정에서 기본 Provider들을 등록합니다."""
    try:
        # 전체 설정을 Provider들에게 전달
        full_config = config_manager.config

        # 기존 Provider들...

        # 새로운 Provider 추가
        new_provider = NewProvider("new_provider", full_config)
        self.add_provider(new_provider)

    except Exception as e:
        logger.warning(f"기본 Provider 등록 실패: {e}")
```

## 📝 디버깅 가이드

### 로깅 활용

```python
import logging
from donmoa.utils.logger import logger

def debug_method(self, data):
    """디버깅을 위한 로깅 예시"""
    logger.debug(f"입력 데이터: {data}")

    try:
        result = self._process_data(data)
        logger.info(f"처리 완료: {result}")
        return result
    except Exception as e:
        logger.error(f"처리 실패: {e}", exc_info=True)
        raise
```

### 디버깅 모드 활성화

```bash
# 환경 변수로 디버깅 모드 활성화
export DONMOA_DEBUG=1

# Python에서 직접 설정
import logging
logging.getLogger('donmoa').setLevel(logging.DEBUG)
```

### 일반적인 디버깅 시나리오

1. **데이터 파싱 오류**
   - 입력 파일 형식 확인
   - 파싱 규칙 검증
   - 예외 처리 로직 점검

2. **Provider 연결 실패**
   - 설정 파일 경로 확인
   - 인증 정보 검증
   - 네트워크 연결 상태 확인

3. **CSV 내보내기 오류**
   - 출력 디렉토리 권한 확인
   - 데이터 형식 검증
   - 인코딩 설정 확인

## 📝 성능 최적화

### 데이터 처리 최적화

```python
# 대용량 파일 처리 시 청크 단위로 읽기
def process_large_file(self, file_path: Path):
    """대용량 파일 처리"""
    chunk_size = 10000

    for chunk in pd.read_excel(file_path, chunksize=chunk_size):
        processed_chunk = self._process_chunk(chunk)
        yield processed_chunk

# 비동기 처리 활용
import asyncio

async def collect_data_async(self, providers: List[str]):
    """비동기 데이터 수집"""
    tasks = []
    for provider_name in providers:
        task = asyncio.create_task(
            self._collect_from_provider(provider_name)
        )
        tasks.append(task)

    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

### 메모리 사용량 최적화

```python
# 불필요한 데이터 즉시 제거
def optimize_memory(self, data: pd.DataFrame):
    """메모리 사용량 최적화"""
    # 데이터 타입 최적화
    for col in data.select_dtypes(include=['object']):
        data[col] = data[col].astype('category')

    # 불필요한 컬럼 제거
    data = data.dropna(how='all')

    return data
```

## 🚀 배포 및 CI/CD

### Docker 빌드

```bash
# 개발용 이미지 빌드
docker build -t donmoa:dev .

# 프로덕션용 이미지 빌드
docker build -t donmoa:prod --target production .
```

### GitHub Actions 예시

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run tests
      run: |
        pytest --cov=donmoa --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## 📝 문서화

### 코드 문서화

- **모든 클래스와 메서드**에 docstring 작성
- **비즈니스 로직**에 한글 주석 추가
- **API 변경사항**을 CHANGELOG.md에 기록

### 문서 업데이트

새로운 기능 추가 시 다음 문서들을 업데이트:

1. **README.md**: 주요 기능 및 사용법
2. **INSTALL.md**: 설치 및 설정 방법
3. **FOR_DEV.md**: 개발 가이드 (이 파일)
4. **CHANGELOG.md**: 버전별 변경사항

## 🤝 기여 가이드라인

### Pull Request 프로세스

1. **Feature Branch 생성**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **코드 작성 및 테스트**
   ```bash
   # 코드 작성
   # 테스트 실행
   pytest

   # 코드 스타일 검사
   black donmoa/
   flake8 donmoa/
   ```

3. **커밋 및 푸시**
   ```bash
   git add .
   git commit -m "feat: 새로운 기능 추가"
   git push origin feature/new-feature
   ```

4. **Pull Request 생성**
   - 명확한 제목과 설명
   - 관련 이슈 링크
   - 테스트 결과 포함

### 커밋 메시지 규칙

- **feat**: 새로운 기능
- **fix**: 버그 수정
- **docs**: 문서 수정
- **style**: 코드 스타일 변경
- **refactor**: 코드 리팩토링
- **test**: 테스트 추가/수정
- **chore**: 빌드 프로세스 또는 보조 도구 변경

## 📝 개발 지원

### 문제 해결

1. **GitHub Issues** 확인
2. **프로젝트 문서** 참조
3. **코드 리뷰** 요청
4. **개발자 커뮤니티** 활용

### 개발 도구

- **IDE**: VS Code, PyCharm (Python 개발 최적화)
- **디버거**: pdb, ipdb
- **프로파일링**: cProfile, memory_profiler
- **코드 품질**: black, flake8, mypy

---

**Happy Coding! 🚀**

Donmoa 프로젝트에 기여해주셔서 감사합니다.
```

```markdown:INSTALL.md
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
│   │   ├── csv_exporter.py    # CSV 내보내기
│   │   ├── template_generator.py  # Excel 템플릿 생성
│   │   └── schemas.py         # 데이터 스키마
│   ├── providers/              # 기관별 Provider
│   │   ├── __init__.py
│   │   ├── base.py            # 기본 Provider
│   │   ├── banksalad.py       # 뱅크샐러드 Provider
│   │   ├── domino.py          # 도미노 Provider
│   │   └── manual.py          # 수동 입력 Provider
│   ├── utils/                  # 유틸리티
│   │   ├── config.py          # 설정 관리
│   │   ├── logger.py          # 로깅
│   │   └── date_utils.py      # 날짜 유틸리티
│   ├── cli/                    # CLI 인터페이스
│   │   └── main.py            # CLI 메인
│   └── __main__.py            # CLI 진입점
├── data/                       # 데이터 디렉토리
│   ├── input/                  # 입력 파일 (Excel, MHTML 등)
│   │   └── YYYY-MM-DD/         # 날짜별 폴더
│   └── export/                 # 출력 파일
│       └── YYYYMMDD_HHMMSS/    # 타임스탬프별 폴더
├── config/                     # 통합 설정 디렉토리
│   ├── config.yaml            # 메인 설정 파일
│   ├── accounts.yaml          # 계좌 매핑 설정
│   └── env.example            # 환경 변수 예시
├── logs/                       # 로그 파일
├── requirements.txt            # Python 의존성
└── README.md                   # 프로젝트 설명
```

주요 업데이트 내용:

1. **ManualProvider 추가**: 수동 입력을 위한 Excel 템플릿 지원 기능 추가
2. **데이터 스키마 통일**: CashSchema, PositionSchema, TransactionSchema로 통일된 데이터 구조
3. **날짜별 폴더 구조**: `data/input/YYYY-MM-DD/` 형태의 폴더 구조 지원
4. **코드 정리 반영**: 불필요한 메서드 제거, 중복 코드 정리
5. **CLI 명령어 업데이트**: `template` 명령어 추가
6. **Provider 패턴 개선**: BaseProvider의 추상 메서드 구조 개선

문서의 구조는 그대로 유지하면서 현재 코드 변경사항을 반영하여 업데이트했습니다.
