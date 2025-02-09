from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.etsyads.database import get_db
from backend.etsyads.models import History
from backend.etsyads.schemas import HistoryCreate, HistoryResponse

router = APIRouter()

# API để thêm dữ liệu lịch sử
@router.post("/history/", response_model=HistoryResponse)
def create_history(entry: HistoryCreate, db: Session = Depends(get_db)):
    try:
        db_entry = History(**entry.dict())
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        return db_entry
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# API lấy danh sách lịch sử
@router.get("/history/", response_model=list[HistoryResponse])
def get_history(db: Session = Depends(get_db)):
    try:
        return db.query(History).order_by(History.timestamp.desc()).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# API xóa toàn bộ lịch sử
@router.delete("/history/")
def delete_history(db: Session = Depends(get_db)):
    try:
        db.query(History).delete()
        db.commit()
        return {"message": "Lịch sử đã được xóa thành công!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
