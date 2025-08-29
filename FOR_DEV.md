# Donmoa 개발자 문서

## 🎯 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [아키텍처](#아키텍처)
3. [개발 환경 설정](#개발-환경-설정)
4. [코드 구조](#코드-구조)
5. [API 참조](#api-참조)
6. [확장 가이드](#확장-가이드)
7. [테스트](#테스트)
8. [배포](#배포)
9. [문제 해결](#문제-해결)

## 🎯 프로젝트 개요

**Donmoa**는 여러 금융 기관(증권사, 은행, 암호화폐 거래소)의 데이터를 통합하여 개인 자산을 관리할 수 있는 Python 기반 도구입니다.

### 핵심 기능
- **데이터 통합**: 여러 기관의 API를 통해 잔고, 거래내역, 포지션 정보 수집
- **자동화**: 스케줄링을 통한 정기적인 데이터 수집
- **표준화**: 모든 기관의 데이터를 공통 CSV 형식으로 변환
- **확장성**: 새로운 기관 추가를 위한 Provider 패턴 구현

### 기술 스택
- **언어**: Python 3.8+
- **주요 라이브러리**: pandas, requests, schedule, click, rich, pydantic
- **아키텍처**: 모듈형 구조, Provider 패턴, CLI 인터페이스

## 🏗️ 아키텍처

### 전체 구조
```
donmoa/
├── core/           # 핵심 비즈니스 로직
├── providers/      # 기관별 API 연동 모듈
├── utils/          # 유틸리티 함수들
├── cli/            # 명령행 인터페이스
└── __main__.py     # 모듈 실행 진입점
```

### 핵심 컴포넌트

#### 1. Donmoa (Core)
- 전체 워크플로우 관리
- Provider 관리 및 데이터 수집 조율
- CSV 내보내기 및 결과 저장

#### 2. DataCollector
- 각 Provider로부터 데이터 수집
- 비동기/동기 수집 지원
- 에러 처리 및 재시도 로직

#### 3. CSVExporter
- 수집된 데이터를 표준 CSV 형식으로 변환
- 파일명 자동 생성 (타임스탬프 포함)
- 인코딩 및 형식 관리

#### 4. BaseProvider (Abstract)
- 모든 기관별 Provider의 기본 인터페이스
- 공통 메서드 정의 (인증, 데이터 수집 등)
- HTTP 요청 처리 및 에러 핸들링

#### 5. Scheduler
- 정기적인 데이터 수집 작업 스케줄링
- 백그라운드 작업 관리
- 작업 상태 모니터링

## 🛠️ 개발 환경 설정

### 필수 요구사항
- Python 3.8 이상
- pip 또는 conda

### 설치 단계

```bash
# 1. 저장소 클론
git clone https://github.com/yourusername/donmoa.git
cd donmoa

# 2. 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 개발 의존성 설치 (선택사항)
pip install -r requirements-dev.txt
```

### 환경 변수 설정

```bash
# .env 파일 생성
cp config/env.example .env

# 필요한 API 키 및 인증 정보 입력
SECURITIES_API_KEY=your_api_key
SECURITIES_SECRET=your_secret
BANK_API_KEY=your_api_key
BANK_SECRET=your_secret
EXCHANGE_API_KEY=your_api_key
EXCHANGE_SECRET=your_secret
```

### 설정 파일

`config/config.yaml`에서 다음 설정을 조정할 수 있습니다:

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

# 로깅 설정
logging:
  level: "INFO"
  file: "./logs/donmoa.log"
  console: true
```

## 🔍 코드 구조

### 핵심 모듈 상세

#### `donmoa/core/donmoa.py`
메인 클래스로, 전체 워크플로우를 관리합니다.

```python
class Donmoa(LoggerMixin):
    def __init__(self, config_path: Optional[Path] = None):
        # 설정 및 로깅 초기화
        # 핵심 컴포넌트 초기화

    def add_provider(self, provider: BaseProvider) -> None:
        # Provider 추가

    def run_full_workflow(self, output_dir: Optional[Path] = None,
                         use_async: bool = True) -> Dict[str, Any]:
        # 전체 워크플로우 실행

    def collect_data(self, provider_names: Optional[List[str]] = None,
                    use_async: bool = True) -> Dict[str, Any]:
        # 데이터 수집

    def export_to_csv(self, data: Dict[str, Any],
                     output_dir: Optional[Path] = None) -> Dict[str, Path]:
        # CSV 내보내기
```

#### `donmoa/providers/base.py`
모든 Provider의 기본 인터페이스를 정의합니다.

```python
class BaseProvider(ABC):
    @abstractmethod
    def authenticate(self) -> bool:
        """인증을 수행합니다."""
        pass

    @abstractmethod
    def get_balances(self) -> List[Dict[str, Any]]:
        """잔고 정보를 가져옵니다."""
        pass

    @abstractmethod
    def get_transactions(self, start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """거래 내역을 가져옵니다."""
        pass

    @abstractmethod
    def get_positions(self) -> List[Dict[str, Any]]:
        """보유 포지션을 가져옵니다."""
        pass
```

#### `donmoa/cli/main.py`
명령행 인터페이스를 제공합니다.

```python
@cli.command()
def collect(ctx, provider, output_dir, async, save_result):
    """데이터를 수집하고 CSV 파일로 내보냅니다."""

@cli.command()
def scheduler(ctx, action, name, time, interval):
    """스케줄러를 관리합니다."""

@cli.command()
def status(ctx):
    """현재 상태를 확인합니다."""
```

## 📚 API 참조

### Donmoa 클래스

#### 초기화
```python
from donmoa.core import Donmoa

# 기본 설정으로 초기화
donmoa = Donmoa()

# 사용자 정의 설정 파일로 초기화
donmoa = Donmoa(config_path=Path("./custom_config.yaml"))
```

#### Provider 관리
```python
# Provider 추가
provider = CustomProvider("provider_name", credentials, endpoints)
donmoa.add_provider(provider)

# Provider 제거
donmoa.remove_provider("provider_name")

# Provider 목록 조회
providers = donmoa.list_providers()
```

#### 데이터 수집
```python
# 전체 데이터 수집
result = donmoa.run_full_workflow()

# 특정 Provider만 수집
data = donmoa.collect_data(["securities", "bank"])

# 비동기 수집
data = donmoa.collect_data(use_async=True)
```

#### CSV 내보내기
```python
# 기본 출력 디렉토리로 내보내기
exported_files = donmoa.export_to_csv(collected_data)

# 사용자 정의 디렉토리로 내보내기
exported_files = donmoa.export_to_csv(collected_data, "./custom_export")
```

### BaseProvider 클래스

#### 필수 구현 메서드
```python
class CustomProvider(BaseProvider):
    def authenticate(self) -> bool:
        """인증 로직 구현"""
        # API 키 검증, 토큰 발급 등
        return True

    def get_balances(self) -> List[Dict[str, Any]]:
        """잔고 정보 수집"""
        # API 호출 및 데이터 파싱
        return [{"account": "main", "balance": 1000000}]

    def get_transactions(self, start_date=None, end_date=None) -> List[Dict[str, Any]]:
        """거래 내역 수집"""
        # 날짜 범위 기반 거래내역 조회
        return [{"date": "2024-01-01", "amount": 10000, "type": "deposit"}]

    def get_positions(self) -> List[Dict[str, Any]]:
        """포지션 정보 수집"""
        # 보유 자산 정보 조회
        return [{"symbol": "AAPL", "quantity": 10, "avg_price": 150.0}]
```

#### 유틸리티 메서드
```python
# HTTP 요청 수행
response = self._make_request("GET", "https://api.example.com/balances")

# 날짜 형식 변환
date_str = self._format_date(datetime.now())
date_obj = self._parse_date("2024-01-01")
```

## 🔧 확장 가이드

### 새로운 Provider 추가하기

#### 1. Provider 클래스 생성
```python
# donmoa/providers/new_bank.py
from .base import BaseProvider
from typing import Dict, List, Any, Optional
from datetime import datetime

class NewBankProvider(BaseProvider):
    def __init__(self, name: str, credentials: Dict[str, str]):
        endpoints = {
            "auth": "https://api.newbank.com/auth",
            "balances": "https://api.newbank.com/accounts/balances",
            "transactions": "https://api.newbank.com/accounts/transactions"
        }

        super().__init__(name, "bank", credentials, endpoints)

    def authenticate(self) -> bool:
        """NewBank API 인증"""
        auth_data = {
            "api_key": self.credentials["api_key"],
            "api_secret": self.credentials["api_secret"]
        }

        response = self._make_request("POST", self.endpoints["auth"], json=auth_data)
        if response and "access_token" in response:
            self.session.headers["Authorization"] = f"Bearer {response['access_token']}"
            return True
        return False

    def get_balances(self) -> List[Dict[str, Any]]:
        """계좌 잔액 조회"""
        response = self._make_request("GET", self.endpoints["balances"])
        if not response:
            return []

        balances = []
        for account in response.get("accounts", []):
            balances.append({
                "account_id": account["id"],
                "account_name": account["name"],
                "balance": account["balance"],
                "currency": account["currency"],
                "provider": self.name,
                "provider_type": self.provider_type,
                "timestamp": datetime.now().isoformat()
            })

        return balances

    def get_transactions(self, start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """거래내역 조회"""
        params = {}
        if start_date:
            params["from_date"] = self._format_date(start_date)
        if end_date:
            params["to_date"] = self._format_date(end_date)

        response = self._make_request("GET", self.endpoints["transactions"], params=params)
        if not response:
            return []

        transactions = []
        for tx in response.get("transactions", []):
            transactions.append({
                "transaction_id": tx["id"],
                "date": self._parse_date(tx["date"]).isoformat(),
                "amount": tx["amount"],
                "type": tx["type"],
                "description": tx.get("description", ""),
                "account_id": tx["account_id"],
                "provider": self.name,
                "provider_type": self.provider_type
            })

        return transactions

    def get_positions(self) -> List[Dict[str, Any]]:
        """은행은 포지션이 없으므로 빈 리스트 반환"""
        return []
```

#### 2. Provider 등록
```python
from donmoa.providers.new_bank import NewBankProvider

# Provider 인스턴스 생성
new_bank = NewBankProvider("NewBank", {
    "api_key": "your_api_key",
    "api_secret": "your_api_secret"
})

# Donmoa에 추가
donmoa.add_provider(new_bank)
```

### 새로운 데이터 형식 추가하기

#### 1. Exporter 확장
```python
# donmoa/core/json_exporter.py
from .base_exporter import BaseExporter
from typing import Dict, Any, Path
import json

class JSONExporter(BaseExporter):
    def export(self, data: Dict[str, Any], output_dir: Path) -> Dict[str, Path]:
        """JSON 형식으로 데이터 내보내기"""
        exported_files = {}

        for data_type, records in data.items():
            if not records:
                continue

            filename = f"{data_type}_{self._generate_timestamp()}.json"
            filepath = output_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)

            exported_files[data_type] = filepath

        return exported_files
```

#### 2. Exporter 등록
```python
from donmoa.core.json_exporter import JSONExporter

# JSON Exporter 추가
donmoa.json_exporter = JSONExporter()

# JSON 형식으로 내보내기
json_files = donmoa.json_exporter.export(collected_data, output_dir)
```

## 🧪 테스트

### 테스트 실행
```bash
# 전체 테스트 실행
pytest

# 특정 테스트 파일 실행
pytest test_donmoa.py

# 커버리지와 함께 실행
pytest --cov=donmoa

# 상세 출력
pytest -v
```

### 테스트 작성 가이드

#### Provider 테스트
```python
# test_providers.py
import pytest
from unittest.mock import Mock, patch
from donmoa.providers.new_bank import NewBankProvider

class TestNewBankProvider:
    @pytest.fixture
    def provider(self):
        credentials = {"api_key": "test_key", "api_secret": "test_secret"}
        return NewBankProvider("TestBank", credentials)

    def test_authentication_success(self, provider):
        with patch.object(provider, '_make_request') as mock_request:
            mock_request.return_value = {"access_token": "test_token"}

            result = provider.authenticate()

            assert result is True
            assert provider.session.headers["Authorization"] == "Bearer test_token"

    def test_get_balances(self, provider):
        with patch.object(provider, '_make_request') as mock_request:
            mock_request.return_value = {
                "accounts": [
                    {"id": "1", "name": "Main", "balance": 1000, "currency": "KRW"}
                ]
            }

            balances = provider.get_balances()

            assert len(balances) == 1
            assert balances[0]["balance"] == 1000
            assert balances[0]["provider"] == "TestBank"
```

#### 통합 테스트
```python
# test_integration.py
import pytest
from pathlib import Path
from donmoa.core import Donmoa
from donmoa.providers.securities import MockSecuritiesProvider

class TestDonmoaIntegration:
    @pytest.fixture
    def donmoa(self, tmp_path):
        donmoa = Donmoa()
        mock_provider = MockSecuritiesProvider("TestSecurities")
        donmoa.add_provider(mock_provider)
        return donmoa

    def test_full_workflow(self, donmoa, tmp_path):
        result = donmoa.run_full_workflow(output_dir=tmp_path)

        assert result["status"] == "success"
        assert "exported_files" in result
        assert len(result["exported_files"]) > 0
```

## 🚀 배포

### 패키지 빌드
```bash
# 개발 버전 설치
pip install -e .

# 배포용 패키지 빌드
python setup.py sdist bdist_wheel

# PyPI 업로드 (선택사항)
twine upload dist/*
```

### Docker 배포
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "-m", "donmoa", "scheduler", "start"]
```

```bash
# Docker 이미지 빌드
docker build -t donmoa .

# 컨테이너 실행
docker run -d --name donmoa-container donmoa
```

## 🔍 문제 해결

### 일반적인 문제들

#### 1. Provider 인증 실패
```python
# 로그 확인
donmoa.logger.setLevel("DEBUG")

# Provider 연결 테스트
test_result = donmoa.test_provider_connection("provider_name")
print(test_result)
```

#### 2. 데이터 수집 실패
```python
# 개별 Provider 테스트
provider = donmoa.get_provider("provider_name")
if provider:
    # 인증 테스트
    auth_result = provider.authenticate()
    print(f"인증 결과: {auth_result}")

    # 데이터 수집 테스트
    balances = provider.get_balances()
    print(f"잔고 데이터: {len(balances)}건")
```

#### 3. CSV 내보내기 오류
```python
# 출력 디렉토리 권한 확인
output_dir = Path("./export")
output_dir.mkdir(exist_ok=True)

# 데이터 형식 확인
for data_type, records in collected_data.items():
    print(f"{data_type}: {len(records)}건")
    if records:
        print(f"첫 번째 레코드: {records[0]}")
```

### 디버깅 팁

#### 로깅 레벨 조정
```python
# DEBUG 레벨로 설정
import logging
logging.getLogger("donmoa").setLevel(logging.DEBUG)

# 파일 로깅 활성화
from donmoa.utils.logger import setup_logger
setup_logger(level=10, log_file=Path("./debug.log"))
```

#### Provider 모킹
```python
# 테스트용 모의 Provider 사용
from donmoa.providers.securities import MockSecuritiesProvider

mock_provider = MockSecuritiesProvider("TestProvider")
donmoa.add_provider(mock_provider)

# 실제 API 호출 없이 테스트
result = donmoa.run_full_workflow()
```

## 📚 추가 리소스

### 코드 예시
- `example_usage.py`: 기본 사용법 및 고급 예시
- `test_donmoa.py`: 테스트 코드 참조

### 설정 파일
- `config/config.yaml`: 기본 설정
- `config/env.example`: 환경 변수 템플릿

### 문서
- `README.md`: 사용자 가이드
- `INSTALL.md`: 설치 가이드

### 개발 도구
```bash
# 코드 포맷팅
black donmoa/
isort donmoa/

# 린팅
flake8 donmoa/
mypy donmoa/

# 타입 체크
mypy donmoa/ --ignore-missing-imports
```

---

이 문서를 통해 Donmoa 프로젝트의 개발 환경을 설정하고, 코드를 이해하며, 새로운 기능을 추가할 수 있습니다. 추가 질문이나 도움이 필요한 부분이 있다면 언제든지 문의해 주세요!
