#!/bin/bash

# Donmoa 배포 스크립트

set -e

echo "🚀 Donmoa 배포 시작..."

# 환경 확인
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되지 않았습니다."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose가 설치되지 않았습니다."
    exit 1
fi

# 필요한 디렉토리 생성
echo "📁 필요한 디렉토리 생성..."
mkdir -p data/input data/export data/logs backups

# Docker 이미지 빌드
echo "🔨 Docker 이미지 빌드 중..."
docker-compose build

# 기존 컨테이너 중지 및 제거
echo "🛑 기존 컨테이너 정리..."
docker-compose down

# 새 컨테이너 시작
echo "▶️ 새 컨테이너 시작..."
docker-compose up -d

# 상태 확인
echo "📊 컨테이너 상태 확인..."
docker-compose ps

echo "✅ 배포 완료!"
echo ""
echo "📋 사용 가능한 명령어:"
echo "  - 로그 확인: docker-compose logs -f donmoa"
echo "  - 컨테이너 중지: docker-compose down"
echo "  - 컨테이너 재시작: docker-compose restart"
echo ""
echo "🌐 애플리케이션 실행:"
echo "  docker exec -it donmoa-app python -m donmoa --deployment --help"
