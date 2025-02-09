import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from passlib.context import CryptContext

# Load biến môi trường từ file .env
load_dotenv(dotenv_path="C:/Users/QUANG LE/AppData/Local/Programs/Python/Python313/backend/etsyads/.env")

# Lấy cấu hình SMTP từ biến môi trường
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "your-email@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your-email-password")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")

# Cấu hình bảo mật mật khẩu
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Kiểm tra xem biến môi trường đã được load chưa
if not SMTP_SERVER or not SMTP_PORT or not SMTP_USERNAME or not SMTP_PASSWORD:
    raise ValueError("❌ Thiếu thông tin cấu hình SMTP. Vui lòng kiểm tra file .env!")

# 👉 **Hàm băm mật khẩu**
def hash_password(password: str) -> str:
    """Băm mật khẩu trước khi lưu vào database."""
    return pwd_context.hash(password)

# 👉 **Hàm tạo reset token**
def generate_reset_token(email: str) -> str:
    """Tạo token khôi phục mật khẩu."""
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps(email, salt="password-reset-salt")

# 👉 **Hàm xác thực token**
def verify_token(token: str) -> str | None:
    """
    Giải mã token khôi phục mật khẩu.
    Args:
        token (str): Token cần giải mã.
    Returns:
        str: Email nếu hợp lệ, None nếu không hợp lệ.
    """
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    try:
        email = serializer.loads(token, salt="password-reset-salt", max_age=3600)  # Token hợp lệ trong 1 giờ
        return email
    except (SignatureExpired, BadSignature):
        return None

# 👉 **Hàm gửi email**
def send_email(to_email: str, subject: str, body: str):
    """
    Gửi email sử dụng SMTP.
    Args:
        to_email (str): Địa chỉ email nhận.
        subject (str): Tiêu đề email.
        body (str): Nội dung email.
    """
    try:
        # Thiết lập nội dung email
        msg = MIMEMultipart()
        msg["From"] = SMTP_USERNAME
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Kết nối SMTP và gửi email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Bắt đầu kết nối TLS
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, to_email, msg.as_string())

        print(f"✅ Email đã được gửi thành công đến {to_email}")
    except Exception as e:
        print(f"❌ Lỗi khi gửi email: {e}")
        raise  # Raise lại lỗi để hệ thống có thể xử lý
