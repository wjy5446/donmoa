# Donmoa 개발자 가이드

## 🚀 개발 환경 설정

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
│   └── csv_exporter.py    # CSV 내보내기
├── providers/              # Provider 구현
│   ├── base.py            # 기본 Provider 클래스
│   ├── banksalad.py       # 뱅크샐러드 Provider
│   ├── domino.py          # 도미노 Provider
│   └── securities.py      # 증권사 Provider
├── utils/                  # 유틸리티
│   ├── config.py          # 설정 관리
│   └── logger.py          # 로깅
└── cli/                    # CLI 인터페이스
    └── main.py            # CLI 메인
```

### 아키텍처 패턴

1. **Provider 패턴**: 각 금융 기관별로 독립적인 Provider 구현
2. **Strategy 패턴**: 데이터 파싱 전략을 Provider별로 구현
3. **Factory 패턴**: Provider 인스턴스 생성 관리
4. **Observer 패턴**: 데이터 수집 진행 상황 모니터링

## 🔧 개발 가이드라인

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
        self.supported_formats = ['.xlsx', '.csv']

    def collect_data(self, file_path: Path) -> Dict[str, pd.DataFrame]:
        """데이터 수집 메서드

        Args:
            file_path: 입력 파일 경로

        Returns:
            데이터 타입별 DataFrame 딕셔너리

        Raises:
            ValueError: 지원하지 않는 파일 형식
        """
        if not self._is_supported_format(file_path):
            raise ValueError(f"지원하지 않는 파일 형식: {file_path.suffix}")

        # 데이터 수집 로직 구현
        return self._parse_file(file_path)
```

## 🧪 테스트 작성

### 테스트 구조

```
tests/
├── test_file_parsing.py    # 파일 파싱 테스트
├── test_deployment.py      # 배포 기능 테스트
├── conftest.py             # pytest 설정
└── fixtures/               # 테스트 데이터
    ├── sample_banksalad.xlsx
    └── sample_domino.mhtml
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

    def test_collect_data_success(self, provider, sample_file):
        """데이터 수집 성공 테스트"""
        result = provider.collect_data(sample_file)

        assert result['status'] == 'success'
        assert 'accounts' in result['data']
        assert len(result['data']['accounts']) > 0

    def test_collect_data_invalid_format(self, provider, tmp_path):
        """잘못된 파일 형식 테스트"""
        invalid_file = tmp_path / "test.txt"
        invalid_file.write_text("invalid content")

        with pytest.raises(ValueError, match="지원하지 않는 파일 형식"):
            provider.collect_data(invalid_file)
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
from typing import Dict, Any
from pathlib import Path
import pandas as pd
from .base import BaseProvider

class NewProvider(BaseProvider):
    """새로운 금융 기관 Provider"""

    def __init__(self, name: str, credentials: Dict[str, str] = None):
        super().__init__(name, "bank", credentials)

    def get_file_patterns(self) -> Dict[str, str]:
        """지원하는 파일 패턴 반환"""
        return {
            "balances": "*.xlsx",
            "transactions": "*.csv"
        }

    def parse_raw_data(self, file_paths: Dict[str, Path]) -> Dict[str, pd.DataFrame]:
        """raw 데이터 파일을 pandas DataFrame으로 변환"""
        dataframes = {}

        # 잔고 데이터 파싱
        if "balances" in file_paths:
            balances_df = self._parse_balances_to_dataframe(file_paths["balances"])
            if not balances_df.empty:
                dataframes["balances"] = balances_df

        # 거래 내역 파싱
        if "transactions" in file_paths:
            transactions_df = self._parse_transactions_to_dataframe(file_paths["transactions"])
            if not transactions_df.empty:
                dataframes["transactions"] = transactions_df

        return dataframes

    def _parse_balances_to_dataframe(self, file_path: Path) -> pd.DataFrame:
        """잔고 데이터를 DataFrame으로 파싱"""
        # 실제 파싱 로직 구현
        # return pd.DataFrame(data)
        pass

    def _parse_transactions_to_dataframe(self, file_path: Path) -> pd.DataFrame:
        """거래 내역을 DataFrame으로 파싱"""
        # 실제 파싱 로직 구현
        # return pd.DataFrame(data)
        pass
```

### 2. Provider 설정 파일 생성

```yaml
# config/providers/new_provider.yaml
name: "NewProvider"
description: "새로운 금융 기관 데이터 수집기"
version: "1.0.0"

supported_formats:
  - ".xlsx"
  - ".csv"
  - ".pdf"

data_types:
  - "accounts"
  - "transactions"
  - "balances"

account_mapping:
  "통합계좌1": "원본계좌1"
  "통합계좌2": "원본계좌2"

parsing_rules:
  excel:
    sheet_name: "Sheet1"
    header_row: 1
  csv:
    encoding: "utf-8"
    delimiter: ","

validation:
  required_columns:
    - "계좌번호"
    - "잔액"
    - "날짜"
```

### 3. Provider 등록

```python
# donmoa/core/donmoa.py에 추가
from ..providers.new_provider import NewProvider
from ..core.data_collector import DataCollector

def register_default_providers(self):
    """기본 Provider 등록"""
    # DataCollector 생성
    self.data_collector = DataCollector()

    # 기존 Provider들...

    # 새로운 Provider 추가
    new_provider = NewProvider("NewFinancial")
    self.data_collector.add_provider(new_provider)

    # 데이터 수집 및 통합
    input_dir = Path("data/input")
    collected_dataframes = self.data_collector.collect_all_dataframes(input_dir)
    integrated_dataframes = self.data_collector.integrate_dataframes()
```

## 🐛 디버깅 가이드

### 로깅 활용

```python
import logging
from donmoa.utils.logger import get_logger

logger = get_logger(__name__)

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

## 📊 성능 최적화

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

## 📞 개발 지원

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
