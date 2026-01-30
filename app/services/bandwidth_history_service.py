import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import psutil
import time

class BandwidthHistoryService:
    """Service để quản lý bandwidth history data."""
    
    HISTORY_FILE = Path('db/bandwidth_history.json')
    MAX_DAYS = 7  # Lưu tối đa 7 ngày
    
    @classmethod
    def ensure_file_exists(cls):
        """Tạo file history nếu chưa tồn tại."""
        cls.HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not cls.HISTORY_FILE.exists():
            cls.HISTORY_FILE.write_text(json.dumps({'records': []}))
    
    @classmethod
    def capture_bandwidth(cls):
        """Capture bandwidth hiện tại và lưu vào history."""
        try:
            # Đo bandwidth trong 1 giây
            net_io_start = psutil.net_io_counters()
            time.sleep(1)
            net_io_end = psutil.net_io_counters()
            
            bandwidth_in = (net_io_end.bytes_recv - net_io_start.bytes_recv) * 8 / 1_000_000  # Mbps
            bandwidth_out = (net_io_end.bytes_sent - net_io_start.bytes_sent) * 8 / 1_000_000  # Mbps
            total_bandwidth = bandwidth_in + bandwidth_out
            
            # Tạo record mới
            record = {
                'timestamp': datetime.now().isoformat(),
                'bandwidth_in': round(bandwidth_in, 2),
                'bandwidth_out': round(bandwidth_out, 2),
                'total': round(total_bandwidth, 2)
            }
            
            # Lưu vào file
            cls.ensure_file_exists()
            data = json.loads(cls.HISTORY_FILE.read_text())
            data['records'].append(record)
            
            # Cleanup: Xóa records cũ hơn 7 ngày
            cutoff_time = datetime.now() - timedelta(days=cls.MAX_DAYS)
            data['records'] = [
                r for r in data['records']
                if datetime.fromisoformat(r['timestamp']) > cutoff_time
            ]
            
            # Ghi lại file
            cls.HISTORY_FILE.write_text(json.dumps(data, indent=2))
            
            return record
        except Exception as e:
            print(f"Error capturing bandwidth: {e}")
            return None
    
    @classmethod
    def get_history(cls, hours=24):
        """Lấy bandwidth history trong X giờ gần nhất."""
        try:
            cls.ensure_file_exists()
            data = json.loads(cls.HISTORY_FILE.read_text())
            
            # Filter theo thời gian
            cutoff_time = datetime.now() - timedelta(hours=hours)
            filtered_records = [
                r for r in data['records']
                if datetime.fromisoformat(r['timestamp']) > cutoff_time
            ]
            
            return filtered_records
        except Exception as e:
            print(f"Error reading bandwidth history: {e}")
            return []
    
    @classmethod
    def get_chart_data(cls, hours=24):
        """Lấy dữ liệu đã format cho Chart.js."""
        records = cls.get_history(hours)
        
        labels = []
        bandwidth_data = []
        
        for record in records:
            # Format timestamp
            dt = datetime.fromisoformat(record['timestamp'])
            labels.append(dt.strftime('%H:%M'))
            bandwidth_data.append(record['total'])
        
        return {
            'labels': labels,
            'data': bandwidth_data
        }
