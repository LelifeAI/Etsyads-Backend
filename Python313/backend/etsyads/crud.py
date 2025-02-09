from sqlalchemy.orm import Session
from backend.etsyads import models, schemas
from backend.etsyads.models import User
from backend.etsyads.schemas import UserCreate
import bcrypt

# Hàm tạo người dùng mới
from fastapi import HTTPException

def create_user(db: Session, user: UserCreate):
    existing_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()

    if existing_user:
        if existing_user.email == user.email:
            raise HTTPException(status_code=400, detail="Email đã tồn tại.")
        if existing_user.username == user.username:
            raise HTTPException(status_code=400, detail="Username đã tồn tại.")
    
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password.decode('utf-8'),
        is_admin=False,
        is_verified=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Hàm lấy người dùng theo username
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

# Hàm xác minh mật khẩu
def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()
