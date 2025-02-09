from typing import Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request, Query, Form, Body
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from backend.etsyads.database import get_db
from backend.etsyads.schemas import (UserCreate, UserOut, HistoryCreate, HistoryResponse, UserResponse, ForgotPasswordRequest, ResetPasswordRequest, UserLogin, LoginRequest)
from backend.etsyads.models import User, History
from backend.etsyads.crud import get_user_by_username, create_user, verify_password, get_user_by_email
from backend.etsyads.utils import send_verification_email, generate_reset_token, verify_token, hash_password
from backend.etsyads.email_utils import send_email

import bcrypt

router = APIRouter()
templates = Jinja2Templates(directory="templates")  # Ensure templates directory exists

# --------------------------------------
# 📌 User Registration
# --------------------------------------
@router.post("/register/")
def register(user: UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Check if username or email exists
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email đã tồn tại.")
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại.")

    db_user = create_user(db, user)

    # Send confirmation email
    subject = "Chào mừng bạn đến với LeLifeAI!"
    body = f"Xin chào {user.username},\n\nCảm ơn bạn đã đăng ký tại LeLifeAI. Vui lòng xác nhận email của bạn."
    background_tasks.add_task(send_email, user.email, subject, body)

    return {"message": "Đăng ký thành công! Kiểm tra email của bạn."}

# --------------------------------------
# 📌 Email Verification
# --------------------------------------
@router.get("/verify-email/{user_id}")
def verify_email(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    
    user.is_verified = True
    db.commit()
    return {"message": "Email đã được xác nhận thành công!"}

# --------------------------------------
# 📌 User Login
# --------------------------------------
@router.post("/login/")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if not db_user:
        raise HTTPException(status_code=404, detail="Email không tồn tại.")
    
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Sai mật khẩu.")

    return {"message": "Đăng nhập thành công!", "user_id": db_user.id}


# --------------------------------------
# 📌 Forgot Password (Send Reset Email)
# --------------------------------------
@router.post("/forgot-password/")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == request.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Email không tồn tại")

    reset_token = generate_reset_token(db_user.email)
    reset_link = f"http://127.0.0.1:8000/etsyads/reset-password?token={reset_token}"

    send_email(
        to_email=request.email,
        subject="Khôi phục mật khẩu",
        body=f"Nhấn vào link sau để đặt lại mật khẩu: {reset_link}"
    )
    return {"message": "Email khôi phục đã được gửi"}

# --------------------------------------
# 📌 Reset Password Page (GET - Show Form)
# --------------------------------------
@router.get("/reset-password/", response_class=HTMLResponse)
def get_reset_password_page(token: str = Query(...)):
    html_content = f"""
    <html>
        <head><title>Đặt lại mật khẩu</title></head>
        <body>
            <h2>Nhập mật khẩu mới</h2>
            <form action="/etsyads/reset-password/" method="post">
                <input type="hidden" name="token" value="{token}">
                <label for="new_password">Mật khẩu mới:</label>
                <input type="password" name="new_password" required>
                <button type="submit">Đặt lại mật khẩu</button>
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)
# --------------------------------------
# 📌 Reset Password (POST)
# --------------------------------------
@router.post("/reset-password/")
async def reset_password(
    token: str = Form(...),  
    new_password: str = Form(...),
    db: Session = Depends(get_db)
):
    print(f"📩 Debug - Token: {token}, Mật khẩu mới: {new_password}")  

    email = verify_token(token)  
    if not email:
        raise HTTPException(status_code=400, detail="Token không hợp lệ hoặc đã hết hạn")

    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")

    # Cập nhật mật khẩu mới
    hashed_password = hash_password(new_password)
    db_user.hashed_password = hashed_password

    db.commit()
    print("✅ Mật khẩu đã được đặt lại thành công! 🔄 Đang chuyển hướng...")

    # 🔥 Chuyển hướng đến trang đăng nhập
    return RedirectResponse(url="/static/etsyadsAI.html", status_code=303)
# --------------------------------------
# 📌 History Management
# --------------------------------------
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
def get_history(db: Session = Depends(get_db)):
    return db.query(History).order_by(History.timestamp.desc()).all()

@router.delete("/history/")
def delete_history(db: Session = Depends(get_db)):
    db.query(History).delete()
    db.commit()
    return {"message": "Lịch sử đã được xóa thành công!"}
