import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

# Tải biến môi trường từ file .env
load_dotenv()

# Cấu hình SMTP
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SMTP_USERNAME", "your-email@gmail.com")
SENDER_PASSWORD = os.getenv("SMTP_PASSWORD", "your-email-password")

# Secret key cho token
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
serializer = URLSafeTimedSerializer(SECRET_KEY)

# Mã hóa mật khẩu
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Băm mật khẩu."""
    return pwd_context.hash(password)

def generate_reset_token(email: str) -> str:
    """
    Tạo token khôi phục mật khẩu.
    Args:
        email (str): Email của người dùng.
    Returns:
        str: Token đã mã hóa.
    """
    return serializer.dumps(email, salt="password-reset")

def verify_token(token: str, expiration: int = 3600) -> str:
    try:
        email = serializer.loads(token, salt="password-reset", max_age=expiration)
        return email
    except SignatureExpired:
        print("⚠️ Token đã hết hạn.")
        return None
    except BadSignature:
        print("⚠️ Token không hợp lệ.")
        return None

def send_email(to_email: str, subject: str, body: str):
    """
    Hàm gửi email sử dụng SMTP.
    Args:
        to_email (str): Địa chỉ email nhận.
        subject (str): Tiêu đề email.
        body (str): Nội dung email.
    """
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())

        print(f"✅ Email đã được gửi thành công đến {to_email}")
    except Exception as e:
        print(f"❌ Lỗi khi gửi email: {e}")

def send_verification_email(email: str, verification_link: str):
    """
    Gửi email xác minh tài khoản.
    Args:
        email (str): Địa chỉ email.
        verification_link (str): Link xác minh.
    """
    subject = "Verify Your Account"
    body = f"Click the link to verify your account: {verification_link}"
    send_email(email, subject, body)
