# Fake News Detection API

FastAPI 기반 가짜 뉴스 탐지 추론 서버입니다.

## 프로젝트 구조

```
hacakthon_api/
├── app/                     # FastAPI 서버 (추론 전용)
│   ├── main.py              # FastAPI 앱
│   ├── api/
│   │   └── routes.py        # API 엔드포인트
│   ├── core/
│   │   └── config.py        # 설정 파일
│   ├── schemas/
│   │   └── schemas.py       # Pydantic 스키마
│   └── services/
│       └── inference.py     # 추론 로직
├── model_definitions/       # 모델 클래스 정의 (학습 전용)
│   ├── bilstm.py
│   ├── bow_mlp.py
│   ├── cnn_text.py
│   └── tiny_transformer.py
├── configs/                 # 모델별 학습 설정 파일
│   ├── bow_mlp.yaml
│   ├── cnn_text.yaml
│   ├── bilstm.yaml
│   └── tiny_transformer.yaml
├── models/                  # 학습된 .pt 파일 저장
│   └── best.pt              # 학습된 모델
├── data/                    # 데이터셋
│   ├── train.csv
│   └── validation.csv
├── utils/                   # 유틸리티
│   ├── vocab.py
│   └── dataset.py
├── train.py                 # 모델 학습 스크립트
└── requirements.txt
```

## 설치

```bash
# Conda 환경 생성 및 활성화
conda create -n hackathon_api python=3.10
conda activate hackathon_api

# 의존성 패키지 설치
pip install -r requirements.txt
```

## 모델 학습

### 사용 가능한 모델

1. **bow_mlp**: Bag-of-Words + MLP
2. **cnn_text**: CNN 기반 텍스트 분류
3. **bilstm**: BiLSTM 기반 텍스트 분류
4. **tiny_transformer**: Transformer 기반 텍스트 분류

### 기본 학습 (모델별 설정 파일 자동 사용)

```bash
# 각 모델은 configs/{모델명}.yaml 설정 파일을 자동으로 사용합니다
python train.py --model bow_mlp
python train.py --model cnn_text
python train.py --model bilstm
python train.py --model tiny_transformer
```

### 사용자 정의 설정 파일 사용

```bash
python train.py --model bow_mlp --config configs/custom_config.yaml
```

### 설정 파일 형식 (YAML)

```yaml
# 학습 하이퍼파라미터
epochs: 10
batch_size: 32
lr: 0.001
max_len: 256
patience: 3
num_workers: 0

# Vocabulary 설정
max_vocab_size: 20000
min_freq: 1

# 모델 하이퍼파라미터 (모델별로 다름)
model:
  embedding_dim: 128
  hidden_dim: 128
  dropout: 0.2

# 데이터 경로
data:
  train_path: "data/train.csv"
  val_path: "data/validation.csv"
  text_fields: ["title", "text"]

# 출력 설정
output:
  model_dir: "models"
  log_dir: "logs"
```

### 학습 결과

- 학습된 모델은 `models/{모델명}_best.pt` 형태로 저장됩니다.
- 모델 파일에는 다음이 포함됩니다:
  - 전체 모델 객체 (`model`)
  - 어휘 사전 (`vocab`)
  - 모델 설정 (`model_config`)
  - 학습 설정 (`train_config`)
  - 검증 정확도 (`accuracy`)

### best.pt 심볼릭 링크 설정

API가 사용할 모델을 지정하려면 심볼릭 링크를 생성하세요:

```bash
# 예: bow_mlp 모델을 API에서 사용
ln -sf bow_mlp_best.pt models/best.pt

# 예: cnn_text 모델을 API에서 사용
ln -sf cnn_text_best.pt models/best.pt
```

## API 서버 실행

```bash
# 기본 실행
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 개발 모드 (자동 재시작)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

서버가 시작되면 다음 URL에서 API 문서를 확인할 수 있습니다:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 엔드포인트

### 1. POST /infer - 단일 텍스트 추론

**Request:**
```json
{
  "title": "뉴스 제목",
  "text": "뉴스 본문"
}
```

**Response:**
```json
{
  "prediction": "real"  // or "fake"
}
```

**cURL 예시:**
```bash
curl -X POST "http://localhost:8000/infer" \
  -H "Content-Type: application/json" \
  -d '{"title": "Breaking News", "text": "This is a test article."}'
```

### 2. POST /infer_csv - CSV 데이터셋 추론

**Request:**
- CSV 파일 업로드 (필수 컬럼: `title`, `text`)

**Response:**
```json
{
  "filename": "uploaded_file.csv",
  "csv_result": "title,text,prediction\n..."
}
```

**cURL 예시:**
```bash
curl -X POST "http://localhost:8000/infer_csv" \
  -F "file=@test_input.csv"
```

### 3. POST /validate - 모델 성능 평가

**Request:** 없음

**Response:**
```json
{
  "accuracy": 0.9856,
  "total": 8117,
  "correct": 8000
}
```

**cURL 예시:**
```bash
curl -X POST "http://localhost:8000/validate"
```

## 데이터 형식

### 학습/검증 데이터 (CSV)

필수 컬럼:
- `title`: 뉴스 제목
- `text`: 뉴스 본문
- `label`: 레이블 (0=real, 1=fake)

### 추론 데이터 (CSV)

필수 컬럼:
- `title`: 뉴스 제목
- `text`: 뉴스 본문

## 주의사항

### 모델 저장 및 로드

- **전체 모델 객체 저장**: 학생들이 모델 구조를 변형할 수 있으므로, `state_dict`만 저장하지 않고 전체 모델 객체를 저장합니다.
- **Vocab 포함**: 모델 파일에 vocab이 함께 저장되어 있어 별도 파일이 필요하지 않습니다.
- **학습 설정 포함**: `max_len`, `text_fields` 등 추론에 필요한 설정이 모델 파일에 포함되어 있습니다.

### GPU/CUDA 사용

- 학습 및 추론은 CUDA가 가능하면 자동으로 GPU를 사용합니다.
- CUDA가 없으면 자동으로 CPU로 전환됩니다.
- 모델 로드 시 `map_location`을 통해 디바이스를 자동 설정합니다.

### CSV 구분자

- API는 CSV 파일의 구분자를 자동으로 감지합니다 (쉼표, 세미콜론 등).
- `pd.read_csv(..., sep=None, engine='python')` 사용

## 라이선스

MIT License
