from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.etsyads.database import SessionLocal
from backend.etsyads.models import History
from backend.etsyads.schemas import HistoryCreate, HistoryResponse
from typing import List  # ✅ Import List đúng cách
from typing import Any


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

@router.get("/history/", response_model=list[HistoryResponse])
def get_history(db: Session = Depends(SessionLocal)):
    return db.query(History).order_by(History.timestamp.desc()).all()
