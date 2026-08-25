from pydantic import BaseModel
from typing import List


class InferRequest(BaseModel):
    """단일 텍스트 추론 요청"""
    title: str
    text: str


class InferResponse(BaseModel):
    """단일 텍스트 추론 응답"""
    prediction: str


class ValidationResponse(BaseModel):
    """Validation 평가 응답"""
    accuracy: float
    total: int
    correct: int

