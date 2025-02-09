from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Định nghĩa URL cho database SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///C:/Users/QUANG LE/AppData/Local/Programs/Python/Python313/backend/etsyads/database.db"

# Tạo engine cho SQLite
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Tạo session cho database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Khởi tạo base cho ORM models
Base = declarative_base()

# Hàm tạo session cho FastAPI dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
