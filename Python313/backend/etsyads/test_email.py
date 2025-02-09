from email_utils import send_email  # Import hàm send_email từ file email_utils.py

# Thử gửi email test
try:
    send_email(
        to_email="test_email@gmail.com",  # Thay bằng địa chỉ email bạn muốn kiểm tra
        subject="Test Email",
        body="Đây là email test để kiểm tra hệ thống gửi email."
    )
    print("Email test đã được gửi thành công!")
except Exception as e:
    print(f"Lỗi khi gửi email test: {e}")
