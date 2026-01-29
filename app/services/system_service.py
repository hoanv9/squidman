import os
import psutil
import time
from datetime import datetime

class SystemService:
    @staticmethod
    def get_server_uptime():
        """Calculate server uptime."""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            if uptime.total_seconds() < 3600:
                return f"{int(uptime.total_seconds() // 60)} minutes"
            else:
                days = uptime.days
                hours, _ = divmod(uptime.seconds, 3600)
                return f"{days} day{'s' if days > 1 else ''} {hours}h" if days > 0 else f"{hours}h"
        except Exception:
            return "Unknown"

    @staticmethod
    def get_squid_status():
        """Check Squid service status. Mocks on Windows."""
        if os.name == 'nt':
            return True, "Running (Dev)"
        
        # Linux implementation
        squid_status = os.system("systemctl is-active --quiet squid") == 0
        squid_status_text = "Running" if squid_status else "Stopped"
        return squid_status, squid_status_text

    @staticmethod
    def get_squid_log_time(log_keyword):
        """Get timestamp from Squid logs using journalctl. Mocks on Windows."""
        if os.name == 'nt':
            return "Jan 01 00:00:00"

        try:
            log_entry = os.popen(f"journalctl -u squid -g '{log_keyword}' --no-pager | tail -1").read().strip()
            if log_entry:
                # Extract first 3 parts (Month Day Time)
                log_time_parts = log_entry.split(None, 3)[:3]
                return " ".join(log_time_parts)
        except Exception:
            pass
        return None

    @staticmethod
    def get_system_stats():
        """Get CPU, RAM, and Bandwidth stats."""
        cpu_percent = psutil.cpu_percent(interval=0)
        ram_percent = psutil.virtual_memory().percent
        
        # Calculate bandwidth (1 second block)
        # Note: In production, this blocking call might be better in a background job or cached
        net_io_start = psutil.net_io_counters()
        time.sleep(1)
        net_io_end = psutil.net_io_counters()
        
        bandwidth_in = (net_io_end.bytes_recv - net_io_start.bytes_recv) * 8 / 1_000_000  # Mbps
        bandwidth_out = (net_io_end.bytes_sent - net_io_start.bytes_sent) * 8 / 1_000_000  # Mbps
        bandwidth = f"{bandwidth_in + bandwidth_out:.2f} Mbps"

        return {
            'cpu_percent': cpu_percent,
            'ram_percent': ram_percent,
            'bandwidth': bandwidth
        }
