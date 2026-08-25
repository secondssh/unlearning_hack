import torch
import pandas as pd
from pathlib import Path
from typing import Tuple
from io import StringIO
from sklearn.metrics import precision_score, recall_score, f1_score
from app.core.config import IDX_TO_LABEL, VALIDATION_DATA_PATH
from utils.vocab import Vocab, WhitespaceTokenizer, pad_sequences, PAD_TOKEN


class InferenceService:
    """추론 서비스 클래스"""
    
    def __init__(self, model: torch.nn.Module, vocab: Vocab, max_len: int = 256, device: str = "cpu"):
        """
        Args:
            model: 학습된 PyTorch 모델
            vocab: Vocabulary 객체
            max_len: 최대 시퀀스 길이
            device: 디바이스 ("cpu" or "cuda")
        """
        self.model = model
        self.vocab = vocab
        self.tokenizer = WhitespaceTokenizer()
        self.max_len = max_len
        self.device = device
        
    def preprocess_text(self, title: str, text: str) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        텍스트를 모델 입력 형태로 전처리
        
        Args:
            title: 뉴스 제목
            text: 뉴스 본문
            
        Returns:
            (input_ids, lengths) 튜플
        """
        # title과 text를 결합
        combined_text = f"<title> {title} </title> <text> {text} </text>"
        
        # 텍스트 인코딩
        token_ids = self.vocab.encode(combined_text, self.tokenizer)
        
        # 패딩
        pad_idx = self.vocab.token_to_idx.get(PAD_TOKEN, 0)
        padded = pad_sequences([token_ids], max_len=self.max_len, pad_idx=pad_idx)
        lengths = torch.tensor([min(len(token_ids), self.max_len)], dtype=torch.long)
        
        return padded.to(self.device), lengths.to(self.device)
    
    def predict_single(self, title: str, text: str) -> str:
        """
        단일 텍스트에 대한 예측
        
        Args:
            title: 뉴스 제목
            text: 뉴스 본문
            
        Returns:
            예측 레이블 ('real' or 'fake')
        """
        # 전처리
        input_ids, lengths = self.preprocess_text(title, text)
        
        # 추론
        with torch.no_grad():
            output = self.model(input_ids, lengths)
            pred_idx = torch.argmax(output, dim=1).item()
        
        return IDX_TO_LABEL[pred_idx]
    
    def predict_batch(self, titles: list[str], texts: list[str]) -> list[str]:
        """
        여러 텍스트에 대한 배치 예측
        
        Args:
            titles: 뉴스 제목 리스트
            texts: 뉴스 본문 리스트
            
        Returns:
            예측 레이블 리스트
        """
        predictions = []
        
        # 배치 처리
        for title, text in zip(titles, texts):
            pred = self.predict_single(title, text)
            predictions.append(pred)
        
        return predictions
    
    def predict_csv(self, csv_content: bytes) -> str:
        """
        CSV 파일에 대한 배치 예측
        
        Args:
            csv_content: CSV 파일 내용 (bytes)
            
        Returns:
            예측 결과가 포함된 CSV 형식 문자열
        """
        # CSV 파일 읽기
        df = pd.read_csv(StringIO(csv_content.decode('utf-8')), sep=None, engine='python')
        
        # 필수 컬럼 확인
        if 'title' not in df.columns or 'text' not in df.columns:
            raise ValueError("CSV file must contain 'title' and 'text' columns.")
        
        # 예측 수행
        titles = df['title'].fillna("").tolist()
        texts = df['text'].fillna("").tolist()
        predictions = self.predict_batch(titles, texts)
        
        # 예측 결과를 데이터프레임에 추가
        df['prediction'] = predictions
        
        csv_output = df.to_csv(index=False)
        return csv_output
    
    def validate(self, validation_path: Path = VALIDATION_DATA_PATH) -> Tuple[float, int, int]:
        """
        Validation 데이터셋으로 모델 성능 평가
        
        Args:
            validation_path: validation CSV 파일 경로
            
        Returns:
            (accuracy, total, correct) 튜플
        """
        if not validation_path.exists():
            raise FileNotFoundError(f"Validation file not found: {validation_path}")
        
        # CSV 파일 읽기 (구분자 자동 감지)
        df = pd.read_csv(validation_path, sep=None, engine='python')
        
        # 필수 컬럼 확인
        if 'title' not in df.columns or 'text' not in df.columns or 'label' not in df.columns:
            raise ValueError("Validation CSV must contain 'title', 'text' and 'label' columns.")
        
        # 예측 수행
        titles = df['title'].fillna("").tolist()
        texts = df['text'].fillna("").tolist()
        predictions = self.predict_batch(titles, texts)
        
        # 레이블은 이미 문자열 형태 ('real', 'fake')
        true_labels = df['label'].tolist()
        
        # 정확도 계산
        correct = sum(1 for pred, true in zip(predictions, true_labels) if pred == true)
        total = len(predictions)
        accuracy = correct / total if total > 0 else 0.0
        precision = precision_score(true_labels, predictions, average='macro')
        recall = recall_score(true_labels, predictions, average='macro')
        f1 = f1_score(true_labels, predictions, average='macro')
        
        return accuracy, total, correct, precision, recall, f1
