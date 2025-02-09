from typing import List
from pydantic import BaseModel, EmailStr
from datetime import datetime

# Schema cho lịch sử phân tích
class HistoryBase(BaseModel):
    ctr: float
    cr: float
    cpp: float
    fee_ads: float
    roi: float

class HistoryCreate(HistoryBase):
    pass

class HistoryResponse(HistoryCreate):
    id: int
    timestamp: datetime

    model_config = {
        "from_attributes": True  # Pydantic v2 chuẩn
    }

# ✅ Định nghĩa AnalyzeData để sử dụng trong API /analyze/
class AnalyzeData(BaseModel):
    views: int
    clicks: int
    orders: int
    revenue: float
    spend: float
    sales: float
    marketing: float
    fees: float

# Schema cho dữ liệu phân tích
class AnalysisBase(BaseModel):
    product_name: str
    price: float
    views: int
    clicks: int
    orders: int
    revenue: float
    spend: float
    sales: float
    marketing: float
    fees: float

class AnalysisCreate(AnalysisBase):
    pass

class AnalysisResponse(AnalysisBase):
    id: int

    model_config = {
        "from_attributes": True  # Pydantic v2 chuẩn
    }

# Schema cho người dùng
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr  # ✅ Make sure this field is "email"
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_verified: bool

    model_config = {
        "from_attributes": True  # Pydantic v2 chuẩn
    }

class UserResponse(UserOut):
    created_at: datetime

# Hỗ trợ đăng nhập bằng cả username hoặc email
class LoginRequest(BaseModel):
    identifier: str  # Có thể là tên đăng nhập hoặc email
    password: str

# Quên mật khẩu
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

# Đặt lại mật khẩu
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
