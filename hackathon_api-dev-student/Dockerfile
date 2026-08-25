# GPU 지원 PyTorch 베이스 이미지
FROM pytorch/pytorch:2.8.0-cuda12.8-cudnn9-runtime

# 작업 디렉토리 설정
WORKDIR /workspace

# 시스템 패키지 업데이트 및 필수 도구 설치
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    nginx \
    supervisor \
    vim \
    git \
    && rm -rf /var/lib/apt/lists/*

# code-server 설치 (최신 버전)
RUN curl -fsSL https://code-server.dev/install.sh | sh

# Python 의존성 복사 및 설치
COPY requirements.txt /workspace/
RUN pip install --no-cache-dir -r requirements.txt

# gdown 설치 (Google Drive 다운로드용)
RUN pip install --no-cache-dir gdown

# 참가자 사용자 생성
RUN useradd -ms /bin/bash participant

USER participant
RUN code-server --install-extension ms-python.python
RUN code-server --install-extension ms-toolsai.jupyter
USER root

# 프로젝트 파일 복사
# COPY . /workspace/
# RUN chown -R participant:participant /workspace

# 2. 대신, 덮어씌워지지 않을 임시 경로(/app-src)에 코드를 복사
RUN mkdir -p /app-src
COPY . /app-src/
RUN chown -R root:root /app-src/app && chmod -R 700 /app-src/app

# RUN chown -R root:root /workspace/app && chmod -R 700 /workspace/app

# Supervisor 설정 파일 복사
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Nginx 설정 파일 복사
COPY nginx.conf /etc/nginx/nginx.conf

# 필요한 디렉토리 생성
RUN mkdir -p /workspace/models \
    /workspace/public \
    /var/log/supervisor \
    /var/log/nginx \
    /run

# Nginx 기본 사이트 설정 제거
RUN rm -f /etc/nginx/sites-enabled/default

# 포트 노출
# 80: Nginx (메인 진입점)
# 8000: FastAPI (내부)
# 8080: code-server (내부)
EXPOSE 80 8000 8080

RUN apt-get update && apt-get install -y dos2unix && rm -rf /var/lib/apt/lists/*
# entrypoint 스크립트 복사 및 실행 권한 부여
COPY entrypoint.sh /app-init/entrypoint.sh
RUN dos2unix /app-init/entrypoint.sh
RUN chmod +x /app-init/entrypoint.sh

# 환경변수 설정
ENV PYTHONUNBUFFERED=1

# Entrypoint 설정 (데이터 다운로드 후 서비스 시작)
ENTRYPOINT ["/app-init/entrypoint.sh"]
