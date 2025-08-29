# Donmoa - 개인 자산 관리 도구

Donmoa는 여러 증권사, 은행, 암호화폐 거래소의 데이터를 한 곳으로 모아 개인이 손쉽게 관리할 수 있도록 돕는 개인 자산 관리 도구입니다.

## 🚀 주요 기능

- **기관별 계정 연동**: 증권사, 은행, 거래소 계정을 한 번 등록하면 자동 연동
- **데이터 자동 수집**: 잔고, 거래내역, 포지션 정보를 주기적으로 자동 수집
- **표준화된 CSV 출력**: 모든 기관의 데이터를 공통 포맷으로 변환하여 CSV 파일로 제공
- **자동화된 스케줄링**: 사용자가 설정한 주기에 따라 자동으로 데이터 수집 및 CSV 갱신

## 📊 지원 데이터 항목

### 증권사
- 잔고 현황
- 체결 내역
- 현금 입출금
- 배당 내역

### 은행
- 계좌 잔액
- 입출금 내역

### 거래소
- 코인 잔고
- 매수·매도 체결 내역
- 입출금 기록

## 🛠️ 설치 방법

```bash
# 저장소 클론
git clone https://github.com/yourusername/donmoa.git
cd donmoa

# 의존성 설치
pip install -r requirements.txt

# 환경 설정
cp .env.example .env
# .env 파일에 API 키 및 인증 정보 입력
```

## ⚙️ 설정 방법

1. `.env` 파일에 각 기관의 API 키 및 인증 정보를 입력합니다:

```env
# 증권사 설정
SECURITIES_API_KEY=your_api_key
SECURITIES_SECRET=your_secret

# 은행 설정
BANK_API_KEY=your_api_key
BANK_SECRET=your_secret

# 거래소 설정
EXCHANGE_API_KEY=your_api_key
EXCHANGE_SECRET=your_secret
```

2. `config.yaml` 파일에서 데이터 수집 주기 및 기타 설정을 조정합니다.

## 🚀 사용 방법

### CLI 명령어

```bash
# 모든 기관의 데이터를 수집하고 CSV 파일 생성
python -m donmoa collect

# 특정 기관의 데이터만 수집
python -m donmoa collect --provider securities

# 스케줄러 시작 (백그라운드에서 자동 실행)
python -m donmoa scheduler start

# 스케줄러 중지
python -m donmoa scheduler stop

# 설정된 스케줄 확인
python -m donmoa scheduler status
```

### Python API

```python
from donmoa.core import Donmoa

# Donmoa 인스턴스 생성
donmoa = Donmoa()

# 모든 데이터 수집
data = donmoa.collect_all_data()

# CSV 파일로 내보내기
donmoa.export_to_csv(data, output_dir="./export")
```

## 📁 출력 파일 구조

```
export/
├── transactions.csv    # 거래내역 (매수/매도/입출금/배당 등)
├── balances.csv       # 잔액 현황
└── positions.csv      # 보유 종목, 수량, 평균 단가
```

## 🔧 개발 환경 설정

```bash
# 개발 의존성 설치
pip install -r requirements-dev.txt

# 테스트 실행
pytest

# 코드 포맷팅
black donmoa/
isort donmoa/

# 린팅
flake8 donmoa/
mypy donmoa/
```

## 📈 로드맵

- [x] 1단계: API 연동 및 CSV 자동 다운로드 구축
- [ ] 2단계: 다운로드된 CSV → 로컬 데이터베이스 저장
- [ ] 3단계: REST API 제공 (개인 서버·로컬 PC)
- [ ] 4단계: 모바일 앱(대시보드)로 조회 및 시각화

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 [Issues](https://github.com/yourusername/donmoa/issues)를 통해 연락해 주세요.
