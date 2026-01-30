# Bandwidth History Tracking - Implementation Summary

## 📋 Tổng quan
Đã thêm tính năng theo dõi và hiển thị lịch sử băng thông (bandwidth) vào Dashboard với các đặc điểm:
- ✅ Capture bandwidth tự động mỗi 5 phút
- ✅ Lưu trữ dữ liệu dạng JSON trong folder `db/`
- ✅ Tự động cleanup data cũ hơn 7 ngày
- ✅ Hiển thị line chart trên dashboard
- ✅ Cho phép xem theo 6h, 12h, hoặc 24h
- ✅ Tự động refresh chart mỗi 5 phút

## 📁 Files đã tạo/sửa đổi

### 1. **app/services/bandwidth_history_service.py** (MỚI)
Service quản lý bandwidth history:
- `capture_bandwidth()`: Đo và lưu bandwidth hiện tại
- `get_history(hours)`: Lấy history trong X giờ
- `get_chart_data(hours)`: Format dữ liệu cho Chart.js
- Tự động tạo file `db/bandwidth_history.json` nếu chưa tồn tại
- Tự động xóa records cũ hơn 7 ngày

### 2. **app/__init__.py** (CẬP NHẬT)
Thêm APScheduler job:
```python
# Bandwidth tracking job - chạy mỗi 5 phút
scheduler.add_job(
    id='bandwidth_capture',
    func=BandwidthHistoryService.capture_bandwidth,
    trigger='interval',
    minutes=5
)
```

### 3. **app/blueprints/dashboard/routes.py** (CẬP NHẬT)
Thêm API endpoint mới:
```python
@dashboard_bp.route('/api/bandwidth_history', methods=['GET'])
def bandwidth_history():
    hours = request.args.get('hours', default=24, type=int)
    chart_data = BandwidthHistoryService.get_chart_data(hours)
    return jsonify(chart_data)
```

### 4. **app/templates/dashboard.html** (CẬP NHẬT)
Thêm bandwidth chart section:
- HTML: Canvas element với 3 nút filter (6h, 12h, 24h)
- JavaScript: Chart.js line chart với auto-refresh
- Vị trí: Giữa CPU/RAM blocks và Summary Numbers

## 🔄 Workflow

### Capture Flow
```
App Start → Capture ngay lập tức
    ↓
APScheduler → Capture mỗi 5 phút
    ↓
BandwidthHistoryService.capture_bandwidth()
    ↓
Đo bandwidth trong 1 giây (psutil)
    ↓
Lưu vào db/bandwidth_history.json
    ↓
Cleanup records > 7 ngày
```

### Display Flow
```
Dashboard Load → loadBandwidthChart(24)
    ↓
Fetch /api/bandwidth_history?hours=24
    ↓
BandwidthHistoryService.get_chart_data(24)
    ↓
Filter records theo thời gian
    ↓
Format: {labels: [...], data: [...]}
    ↓
Chart.js render line chart
    ↓
Auto refresh mỗi 5 phút
```

## 📊 Data Structure

### bandwidth_history.json
```json
{
  "records": [
    {
      "timestamp": "2026-01-30T12:55:00.123456",
      "bandwidth_in": 1.23,
      "bandwidth_out": 0.45,
      "total": 1.68
    },
    ...
  ]
}
```

### API Response (/api/bandwidth_history?hours=24)
```json
{
  "labels": ["12:00", "12:05", "12:10", ...],
  "data": [1.68, 2.34, 1.89, ...]
}
```

## 🎨 UI Features

### Chart Controls
- **6h button**: Hiển thị 6 giờ gần nhất
- **12h button**: Hiển thị 12 giờ gần nhất
- **24h button**: Hiển thị 24 giờ gần nhất (mặc định)

### Chart Properties
- Type: Line chart
- Color: Blue (#3b82f6)
- Fill: Semi-transparent
- Tension: 0.4 (smooth curves)
- Auto-refresh: Every 5 minutes
- Responsive: Yes

## 🔧 Configuration

### Capture Interval
Trong `app/__init__.py`:
```python
minutes=5  # Thay đổi để điều chỉnh tần suất capture
```

### Data Retention
Trong `app/services/bandwidth_history_service.py`:
```python
MAX_DAYS = 7  # Thay đổi để lưu lâu hơn/ngắn hơn
```

### Chart Refresh
Trong `dashboard.html`:
```javascript
setInterval(() => loadBandwidthChart(currentHours), 300000);  // 5 phút = 300000ms
```

## 🚀 Testing

### 1. Khởi động app
```bash
python run.py
```

### 2. Kiểm tra console log
Sẽ thấy message khi capture bandwidth:
```
✅ Bandwidth tracking scheduler started (captures every 5 minutes)
```

### 3. Truy cập dashboard
```
https://127.0.0.1:5001/dashboard
```

### 4. Kiểm tra file JSON
```
db/bandwidth_history.json
```

### 5. Test API endpoint
```
https://127.0.0.1:5001/api/bandwidth_history?hours=24
```

## ⚠️ Notes

1. **Lần đầu chạy**: Chart có thể trống vì chưa có data. Đợi 5 phút để có data point đầu tiên.

2. **Performance**: Capture bandwidth sử dụng `time.sleep(1)` để đo chính xác, nhưng chạy trong background job nên không ảnh hưởng UI.

3. **Storage**: File JSON sẽ tự động cleanup, không lo về disk space.

4. **Timezone**: Timestamps sử dụng ISO format với timezone local.

## 🔍 Troubleshooting

### Chart không hiển thị
- Kiểm tra console browser có lỗi không
- Kiểm tra `/api/bandwidth_history` có trả data không
- Kiểm tra file `db/bandwidth_history.json` có tồn tại không

### Không capture bandwidth
- Kiểm tra APScheduler có start không
- Kiểm tra console log có lỗi không
- Restart app để force capture ngay lập tức

### Data không cleanup
- Kiểm tra `MAX_DAYS` setting
- Kiểm tra timestamp format trong JSON
