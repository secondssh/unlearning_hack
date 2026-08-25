import os
from pathlib import Path

# 프로젝트 루트 경로
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 모델 파일 경로
MODEL_PATH = BASE_DIR / "models" / "best.pt"

# Validation 데이터 경로
VALIDATION_DATA_PATH = BASE_DIR / "data" / "validation.csv"

# 레이블 매핑 (utils.constants에서 import)
from utils.constants import LABEL_TO_IDX, IDX_TO_LABEL

# API 인증 설정
API_KEY = os.getenv("HACKATHON_API_KEY")
API_KEY_HEADER_NAME = os.getenv("API_KEY_HEADER_NAME", "X-API-Key")
