import logging
from fastapi import FastAPI
from backend.amazontrend.amazontrend_main import amazontrend_app
from backend.etsyads.etsyads_main import etsyads_app
from fastapi.middleware.cors import CORSMiddleware

# ✅ Cấu hình logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# ✅ Khởi tạo FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Mount AmazonTrend API đúng
app.mount("/amazontrend", amazontrend_app)

# ✅ Mount EtsyAds API đúng
app.mount("/etsyads", etsyads_app)

# ✅ API kiểm tra hoạt động
@app.get("/")
async def root():
    return {"message": "AmazonTrend & EtsyAds APIs are running!"}

# ✅ Chạy server đúng cổng Render
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))  # Render sẽ cung cấp biến PORT
    uvicorn.run(app, host="0.0.0.0", port=port)
