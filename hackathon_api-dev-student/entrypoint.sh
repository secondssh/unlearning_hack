#!/bin/bash

# Docker 컨테이너 시작 시 실행되는 entrypoint 스크립트

set -e

# === 이 블록을 스크립트 맨 위에 추가 ===
# /workspace (볼륨)이 비어있는지 확인 (예: train.py 파일이 있는지 체크)
if [ ! -f "/workspace/train.py" ]; then
    echo "=========================================="
    echo "⚠️  /workspace (볼륨)이 비어있습니다."
    echo "    이미지의 /app-src에서 코드를 복사합니다..."
    
    # /app-src의 모든 파일(숨김 파일 포함)을 /workspace로 복사
    shopt -s dotglob
    cp -r /app-src/* /workspace/

    # 필요 없는 파일 제거
    rm /workspace/entrypoint.sh
    rm /workspace/nginx.conf
    rm /workspace/supervisord.conf
    
    echo "✅ 코드 복사 완료."
    echo "=========================================="
else
    echo "✓ /workspace (볼륨)에 코드가 이미 존재합니다. (복사 건너뜀)"
fi
# === 추가 블록 끝 ===

# 데이터 디렉토리 생성
mkdir -p /workspace/data

# === 권한 설정 ===
echo "🔐 권한 설정 중..."

chown -R participant:participant /workspace && chmod -R 755 /workspace
chown -R root:root /workspace/app && chmod -R 700 /workspace/app

echo "✅ 권한 설정 완료"
echo ""
# === 권한 설정 끝 ===

echo "=========================================="
echo "🚀 Hackathon API Server 시작"
echo "=========================================="


# 데이터셋 Google Drive URL 설정 (필요 시 아래 URL을 실제 URL로 변경)
# Google Drive 공유 링크에서 파일 ID만 추출하여 사용
# 예시: https://drive.google.com/file/d/1ABC123xyz/view?usp=sharing
#      -> 파일 ID는 "1ABC123xyz"
DATASET_1_FILE_ID="1H0kqx3I9Qr9arvJV4_V--6UUU6NGqDvR"
DATASET_2_FILE_ID="1_xKhqgbuSg7vhHcXH2QaJI_SI2og8rOw"
DATASET_3_FILE_ID="1a7_HN6YJdYPsRJLQMN0yp8o6T7egc5m8"

# 데이터셋 다운로드
echo ""
echo "📥 데이터셋 다운로드 중 (Google Drive)..."

if [ ! -f "/workspace/data/dataset_1.csv" ]; then
    echo "⏳ dataset_1.csv 다운로드 중..."
    if gdown --id "$DATASET_1_FILE_ID" -O /workspace/data/dataset_1.csv --quiet; then
        echo "✅ dataset_1.csv 다운로드 완료"
    else
        echo "⚠️  dataset_1.csv 다운로드 실패 (Google Drive ID 확인 필요)"
    fi
else
    echo "✓ dataset_1.csv 이미 존재함"
fi

if [ ! -f "/workspace/data/dataset_2.csv" ]; then
    echo "⏳ dataset_2.csv 다운로드 중..."
    if gdown --id "$DATASET_2_FILE_ID" -O /workspace/data/dataset_2.csv --quiet; then
        echo "✅ dataset_2.csv 다운로드 완료"
    else
        echo "⚠️  dataset_2.csv 다운로드 실패 (Google Drive ID 확인 필요)"
    fi
else
    echo "✓ dataset_2.csv 이미 존재함"
fi

if [ ! -f "/workspace/data/dataset_3.csv" ]; then
    echo "⏳ dataset_3.csv 다운로드 중..."
    if gdown --id "$DATASET_3_FILE_ID" -O /workspace/data/dataset_3.csv --quiet; then
        echo "✅ dataset_3.csv 다운로드 완료"
    else
        echo "⚠️  dataset_3.csv 다운로드 실패 (Google Drive ID 확인 필요)"
    fi
else
    echo "✓ dataset_3.csv 이미 존재함"
fi

# 다운로드된 파일 확인
echo ""
echo "📊 데이터 파일 확인:"
ls -lh /workspace/data/*.csv 2>/dev/null || echo "  (데이터 파일이 없습니다)"

echo ""
echo "=========================================="
echo "🎯 서비스 시작"
echo "=========================================="
echo ""

# Supervisor로 모든 서비스 실행
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf

