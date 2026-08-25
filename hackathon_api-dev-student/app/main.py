"""
FastAPI 메인 애플리케이션
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router, initialize_model

# FastAPI 앱 생성
app = FastAPI(
    title="뉴스 진위 판별 API",
    description="PyTorch 기반 뉴스 진위 판별 추론 API",
    version="1.0.0"
)

# CORS 설정 (필요시)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """서버 시작 시 모델 로드"""
    print("서버 시작 - 모델 로드 중...")
    try:
        initialize_model()
        print("모델 로드 완료!")
    except Exception as e:
        print(f"모델 로드 실패: {e}")
        print("서버는 시작되지만 추론 API는 사용할 수 없습니다.")


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "뉴스 진위 판별 API 서버",
        "endpoints": {
            "POST /infer": "단일 텍스트 추론",
            "POST /infer_csv": "CSV 파일 배치 추론",
            "POST /validate": "Validation 성능 평가",
            "POST /reload_model": "모델 재시작"
        }
    }


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

