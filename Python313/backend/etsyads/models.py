import sys
import os
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean
from datetime import datetime
from backend.etsyads.database import Base

# Thêm thư mục cha của backend vào sys.path để tránh lỗi import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Model Lịch Sử Phân Tích

class History(Base):
    __tablename__ = "history"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    ctr = Column(Float, nullable=False)
    cr = Column(Float, nullable=False)
    cpp = Column(Float, nullable=False)
    fee_ads = Column(Float, nullable=False)
    roi = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Model Dữ Liệu Phân Tích
class AnalysisData(Base):
    __tablename__ = "analysis_data"
    __table_args__ = {'extend_existing': True}  # Thêm dòng này để tránh lỗi

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    price = Column(Float)
    views = Column(Integer)
    clicks = Column(Integer)
    orders = Column(Integer)
    revenue = Column(Float)
    spend = Column(Float)
    sales = Column(Float)
    marketing = Column(Float)
    fees = Column(Float)
    avg_ctr = Column(Float, default=2.0)
    avg_cr = Column(Float, default=2.5)
    avg_cpp = Column(Float, default=10.0)
    avg_fee_ads = Column(Float, default=20.0)

# Model Người Dùng
class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}  # Thêm dòng này để tránh lỗi

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, nullable=False, unique=True)  # Đảm bảo không null
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)

# Tránh import vòng lặp bằng cách sử dụng hàm khi cần thiết
def get_history_model():
    return History
