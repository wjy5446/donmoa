# Donmoa - 개인 자산 관리 도구

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

Donmoa는 다양한 금융 기관의 데이터를 통합하여 개인이 손쉽게 관리할 수 있도록 돕는 개인 자산 관리 도구입니다.

## ✨ 주요 기능

- **다양한 데이터 소스 지원**: Excel, MHTML, CSV 등 다양한 형식의 금융 데이터 파싱
- **Provider 기반 아키텍처**: 뱅크샐러드, 도미노 등 기관별 데이터 수집기
- **통합 데이터 관리**: 여러 계좌의 데이터를 하나의 시스템에서 통합 관리
- **CLI 인터페이스**: 명령줄에서 쉽게 사용할 수 있는 인터페이스
- **Docker 지원**: 컨테이너화된 배포 환경 지원
- **자동화된 워크플로우**: 데이터 수집부터 CSV 내보내기까지 자동화

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
# 데이터 수집 및 CSV 내보내기
python -m donmoa collect

# 특정 Provider만 수집
python -m donmoa collect --provider banksalad

# 시스템 상태 확인
python -m donmoa status

# 도움말 보기
python -m donmoa --help
```

## 📁 프로젝트 구조

```
📁 donmoa/                    # 메인 패키지
├── 📁 core/                  # 핵심 로직
├── 📁 providers/             # Provider 구현
├── 📁 utils/                 # 유틸리티
└── 📁 cli/                   # CLI 인터페이스

📁 config/                    # 통합 설정 디렉토리
├── 📄 config.yaml            # 기본 설정
├── 📄 deployment.yaml        # 배포 환경 설정
├── 📄 env.example            # 환경 변수 예제
└── 📁 providers/             # Provider별 설정
    ├── banksalad.yaml
    └── domino.yaml

📁 data/                      # 데이터 디렉토리
├── 📁 input/                 # 입력 파일 (Excel, MHTML 등)
└── 📁 export/                # 출력 CSV 파일

📁 tests/                     # 테스트 코드
📁 logs/                      # 로그 파일
📁 backups/                   # 백업 파일

📄 requirements.txt            # Python 의존성
📄 Dockerfile                 # Docker 이미지 정의
📄 docker-compose.yml         # Docker Compose 설정
📄 deploy.sh                  # 배포 스크립트
```

## 🔧 설정

### 설정 파일 구조

프로젝트는 `config/` 폴더에 모든 설정을 통합 관리합니다:

- **`config/config.yaml`**: 기본 설정
- **`config/deployment.yaml`**: 배포 환경 설정
- **`config/env.example`**: 환경 변수 예제
- **`config/providers/`**: Provider별 상세 설정

### 환경 변수 설정

```bash
# 환경 변수 파일 생성
cp config/env.example config/.env

# .env 파일 편집
vim config/.env
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

## 🧪 테스트

### 파일 파싱 테스트

```bash
python tests/test_file_parsing.py
```

### 배포 환경 기능 테스트

```bash
python tests/test_deployment.py
```

## 🐳 Docker 배포

### Docker Compose로 실행

```bash
# 빌드 및 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

### 배포 스크립트 사용

```bash
# 배포 스크립트 실행
./deploy.sh
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

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

**Donmoa** - 개인 자산 관리의 새로운 시작 🚀
