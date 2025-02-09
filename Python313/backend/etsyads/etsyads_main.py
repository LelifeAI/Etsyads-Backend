from fastapi import FastAPI, Depends, HTTPException
from backend.etsyads.routers import router as etsyads_router
from backend.etsyads.history.endpoints import router as history_router
from backend.database import engine, SessionLocal
from backend import models
from backend.etsyads.ml_model import predict_action
from backend.etsyads.schemas import HistoryCreate, HistoryResponse, AnalyzeData
from backend.etsyads.database import SessionLocal
from sqlalchemy.orm import Session

# ✅ Khởi tạo FastAPI
etsyads_app = FastAPI(
    title="Etsy Ads AI",
    description="API for Etsy Ads Analysis",
    version="1.0",
    docs_url="/etsyads/docs",
    redoc_url="/etsyads/redoc"
)

# ✅ Đăng ký router chính xác
etsyads_app.include_router(etsyads_router, prefix="/etsyads", tags=["EtsyAds"])
etsyads_app.include_router(history_router, prefix="/history", tags=["History"])  # `/etsyads/history/`

# ✅ API kiểm tra `/etsyads/history/`
@etsyads_app.get("/history/")
async def get_etsyads_history():
    return {"message": "EtsyAds history endpoint is working!"}

@etsyads_app.post("/history/")
async def create_etsyads_history(entry: HistoryCreate, db: Session = Depends(lambda: SessionLocal())):
    try:
        db_entry = models.History(**entry.dict())
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        return db_entry
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ✅ Middleware CORS
from fastapi.middleware.cors import CORSMiddleware
etsyads_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ API kiểm tra `/etsyads/`
@etsyads_app.get("/")
def read_root():
    return {"message": "Welcome to EtsyAds-AI"}

# ✅ Thêm API `/etsyads/analyze/` để xử lý lỗi `404 Not Found`
@etsyads_app.post("/analyze/")
async def analyze_data(data: AnalyzeData):
    try:
        ctr = (data.clicks / data.views * 100) if data.views > 0 else 0
        cr = (data.orders / data.clicks * 100) if data.clicks > 0 else 0
        cpp = (data.spend / data.orders) if data.orders > 0 else 0
        fee_ads = (data.marketing / data.sales * 100) if data.sales > 0 else 0
        roi = ((data.revenue - data.spend) / data.spend * 100) if data.spend > 0 else 0

        recommendation = predict_action({
            "ctr": ctr,
            "cr": cr,
            "cpp": cpp,
            "fee_ads": fee_ads,
            "roi": roi
        })

        return {
            "analysis": {
                "ctr": ctr,
                "cr": cr,
                "cpp": cpp,
                "fee_ads": fee_ads,
                "roi": roi
            },
            "recommendation": recommendation
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error in analysis: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(etsyads_app, host="127.0.0.1", port=8000)
