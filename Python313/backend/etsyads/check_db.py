from backend.etsyads.database import engine
import sqlite3

conn = sqlite3.connect("backend/etsyads/database.db")
cursor = conn.cursor()

# Lấy danh sách các bảng
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables in database:", tables)

conn.close()

from backend.etsyads.database import SessionLocal
from backend.etsyads.models import History

db = SessionLocal()
new_entry = History(ctr=2.5, cr=3.0, cpp=15.0, fee_ads=20.0, roi=80.0)
db.add(new_entry)
db.commit()
db.close()

print("New entry added successfully.")
