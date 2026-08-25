from fastapi import APIRouter, UploadFile, File, HTTPException
import torch
from pathlib import Path

from app.schemas.schemas import InferRequest, InferResponse, ValidationResponse
from app.services.inference import InferenceService
from app.core.config import MODEL_PATH
from utils.vocab import Vocab


router = APIRouter()

model = None
vocab = None
inference_service = None


def initialize_model():
    """모델 초기화 (전체 모델 객체 로드)"""
    global model, vocab, inference_service
    
    try:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
        
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # 전체 모델 객체 로드
        checkpoint = torch.load(MODEL_PATH, map_location=device, weights_only=False)
        
        # 모델 로드
        model = checkpoint['model']
        model.to(device)
        model.eval()
        
        # Vocab 복원
        vocab = Vocab(
            max_size=checkpoint['vocab']['max_size'],
            min_freq=checkpoint['vocab']['min_freq']
        )
        vocab.token_to_idx = checkpoint['vocab']['token_to_idx']
        vocab.idx_to_token = checkpoint['vocab']['idx_to_token']
        vocab._frozen = True
        
        # 학습 설정 로드
        train_config = checkpoint.get('train_config', {})
        max_len = train_config.get('max_len', 256)
        
        # InferenceService 초기화
        inference_service = InferenceService(
            model=model,
            vocab=vocab,
            max_len=max_len,
            device=device
        )
        
        print(f"✓ Model loaded successfully from {MODEL_PATH}")
        print(f"  - Model: {checkpoint.get('model_name', 'unknown')}")
        print(f"  - Vocab size: {len(vocab)}")
        print(f"  - Max length: {max_len}")
        print(f"  - Device: {device}")
        
    except Exception as e:
        print(f"Failed to load model: {e}")
        raise


@router.post("/infer", response_model=InferResponse)
async def infer_single_text(request: InferRequest):
    """
    단일 텍스트에 대한 추론
    
    Args:
        request: 추론 요청 (title, text 포함)
        
    Returns:
        예측 결과 (real/fake)
    """
    if inference_service is None:
        raise HTTPException(status_code=503, detail="Model not loaded.")
    
    try:
        prediction = inference_service.predict_single(request.title, request.text)
        return InferResponse(prediction=prediction)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during inference: {str(e)}")


@router.post("/infer_csv")
async def infer_csv_dataset(file: UploadFile = File(...)):
    """
    CSV 파일 전체에 대한 추론
    
    Args:
        file: CSV 파일 (데이터셋 전체)
        
    Returns:
        예측 결과가 포함된 CSV 텍스트
    """
    if inference_service is None:
        raise HTTPException(status_code=503, detail="Model not loaded.")
    
    # CSV 파일인지 확인
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")
    
    try:
        # 파일 내용 읽기
        csv_content = await file.read()
        
        # 추론 수행
        csv_output = inference_service.predict_csv(csv_content)
        
        # CSV 텍스트 반환
        return {
            "filename": file.filename,
            "csv_result": csv_output
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during inference: {str(e)}")


@router.post("/validate", response_model=ValidationResponse)
async def validate_model():
    """
    Validation 데이터셋으로 모델 성능 평가
    
    Returns:
        정확도 및 평가 지표
    """
    if inference_service is None:
        raise HTTPException(status_code=503, detail="Model not loaded.")
    
    try:
        accuracy, total, correct = inference_service.validate()
        return ValidationResponse(
            accuracy=accuracy,
            total=total,
            correct=correct
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during validation: {str(e)}")
