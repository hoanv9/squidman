# Hướng Dẫn Triển Khai Squid Manager trên Linux

Tài liệu này hướng dẫn cài đặt và cấu hình **Squid Manager** trên môi trường Linux (Ubuntu/Debian/CentOS) và thiết lập service `squidman` để tự động khởi chạy cùng hệ thống.

## 1. Yêu cầu hệ thống

- **Hệ điều hành**: Linux (Ubuntu 20.04+, Debian 10+, CentOS 7+)
- **Python**: Phiên bản 3.8 trở lên
- **Squid**: Đã cài đặt (`apt install squid` hoặc `yum install squid`)

## 2. Cài đặt ứng dụng

Lấy mã nguồn về thư mục `/opt/squid-manager` (hoặc thư mục tùy chọn).

```bash
# 1. Chuyển sang quyền root
sudo -i

# 2. Tạo thư mục chứa ứng dụng
mkdir -p /opt/squid-manager
cd /opt/squid-manager

# 3. Copy source code vào thư mục này
# (Ví dụ: git clone hoặc upload file)
# Đảm bảo bạn đang đứng ở thư mục gốc của dự án (/opt/squid-manager)

# 4. Cài đặt các gói phụ thuộc hệ thống (nếu cần cho Python build)
# Ubuntu/Debian
apt-get update && apt-get install -y python3-venv python3-dev build-essential
# CentOS/RHEL
yum install -y python3-devel gcc

# 5. Tạo môi trường ảo (Virtual Environment)
python3 -m venv venv

# 6. Kích hoạt môi trường ảo và cài đặt thư viện
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Cấu hình môi trường (.env)

Tạo file `.env` từ file mẫu và chỉnh sửa các tham số cho phù hợp với môi trường Linux.

```bash
# Copy file cấu hình mẫu
cp .env.example .env

# Chỉnh sửa file .env
nano .env
```

**Lưu ý các tham số quan trọng trong `.env`:**

```ini
# Đổi lại đường dẫn phù hợp với Linux (thường là /etc/squid/...)
SQUID_CONF_DIR=/etc/squid/conf.d/
SQUID_DOMAINS_DIR=/etc/squid/domains/
BACKUP_DIR=/etc/squid/backups/

# Cấu hình bảo mật
SECRET_KEY=chuoi-ngau-nhien-bao-mat-cua-ban
DEBUG=False
```

## 4. Kiểm tra chạy thử

Trước khi tạo service, hãy chạy thử để đảm bảo ứng dụng hoạt động.

```bash
# Đảm bảo đang trong venv
source venv/bin/activate

# Chạy app
python run.py
```
Nếu thấy thông báo `Running on https://0.0.0.0:5000` (hoặc http), ứng dụng đã khởi động thành công. Nhấn `Ctrl+C` để dừng.

## 5. Tạo Service Systemd (squidman)

Tạo file service để quản lý tiến trình bằng `systemd`.

**Bước 1: Tạo file service**

```bash
nano /etc/systemd/system/squidman.service
```

**Bước 2: Dán nội dung sau vào file**

_Lưu ý: Thay đổi đường dẫn `/opt/squid-manager` nếu bạn cài đặt ở nơi khác._

```ini
[Unit]
Description=Squid Manager Web Service
After=network.target

[Service]
# Chạy với quyền root để có thể reload Squid Service và ghi vào /etc/squid
User=root
Group=root

# Thư mục làm việc
WorkingDirectory=/opt/squid-manager

# Đường dẫn đến Python trong venv
ExecStart=/opt/squid-manager/venv/bin/python run.py

# Tự động khởi động lại nếu crash
Restart=always
RestartSec=5

# Log output
StandardOutput=append:/var/log/squidman.log
StandardError=append:/var/log/squidman.err

[Install]
WantedBy=multi-user.target
```

**Bước 3: Kích hoạt và khởi chạy service**

```bash
# Reload daemon để nhận service mới
systemctl daemon-reload

# Bật service khởi động cùng hệ thống
systemctl enable squidman

# Khởi chạy service ngay lập tức
systemctl start squidman

# Kiểm tra trạng thái
systemctl status squidman
```

## 6. Các lệnh quản lý thường dùng

- **Xem trạng thái**: `systemctl status squidman`
- **Khởi động lại**: `systemctl restart squidman`
- **Dừng service**: `systemctl stop squidman`
- **Xem log ứng dụng**: `tail -f /var/log/squidman.log`
