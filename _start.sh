#!/bin/bash

LOGFILE="startup.log"

# Tạo log directory nếu chưa có
mkdir -p "$(dirname "$LOGFILE")"

# Ghi log với timestamp
echo "$(date '+%Y-%m-%d %H:%M:%S') - Kiểm tra ứng dụng..." >> "$LOGFILE"

if pgrep -f "python run.py" > /dev/null; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Ứng dụng đang chạy, không khởi động lại." >> "$LOGFILE"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Khởi động ứng dụng..." >> "$LOGFILE"
    nohup python run.py >> "$LOGFILE" 2>&1 &
fi

