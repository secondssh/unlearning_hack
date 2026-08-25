from pathlib import Path

# 프로젝트 루트 경로
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 모델 파일 경로
MODEL_PATH = BASE_DIR / "models" / "best.pt"

# Validation 데이터 경로
VALIDATION_DATA_PATH = BASE_DIR / "data" / "validation.csv"

# 레이블 매핑 (데이터셋: 1=fake, 0=real)
LABEL_MAP = {
    1: "fake",
    0: "real"
}

