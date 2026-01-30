import ssl
import logging
from logging.handlers import RotatingFileHandler
from flask import request
from app import create_app

app = create_app()

# Cấu hình xoay vòng log
import os

# Ensure logs directory exists
if not os.path.exists('logs'):
    os.makedirs('logs')

# Cấu hình xoay vòng log
log_handler = RotatingFileHandler(
    'logs/access.log',  # File log
    maxBytes=5 * 1024 * 1024,  # Giới hạn kích thước file log (5MB)
    backupCount=3,  # Số lượng file log sao lưu
    encoding='utf-8' # Encoding
)
log_handler.setLevel(logging.INFO)  # Mức độ log (INFO)
log_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(message)s',  # Định dạng log
    datefmt='%Y-%m-%d %H:%M:%S'  # Định dạng thời gian
))
app.logger.addHandler(log_handler)  # Thêm handler vào logger của Flask

@app.before_request
def log_request_info():
    """Ghi log mỗi yêu cầu HTTP, ngoại trừ các yêu cầu vào /static/ và /system_stats."""
    if not (request.path.startswith('/static/') or request.path.startswith('/api/system_stats')):
        app.logger.info(
            f"{request.remote_addr} - {request.method} {request.path} - {request.user_agent}"
        )


if __name__ == '__main__':
    # Đường dẫn đến các tệp SSL của bạn
    cert_file = 'deltavn.pem'  # Đảm bảo đây là đường dẫn chính xác đến chứng chỉ của bạn
    key_file = 'deltavn.key'   # Đảm bảo đây là đường dẫn chính xác đến khóa riêng của bạn

    # Tạo SSLContext cho TLS 1.2 và cipher suite chuẩn A
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.set_ciphers('ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:HIGH:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!3DES')

    # Tắt TLS 1.0 và 1.1 (vẫn giữ TLS 1.2)
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1  # Tắt TLS 1.0 và 1.1

    # Chạy ứng dụng Flask với HTTPS
    #app.run(host='0.0.0.0', port=5000, debug=False)
    app.run(host='0.0.0.0', port=5001, debug=True, ssl_context=(cert_file, key_file))
