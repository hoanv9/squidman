import subprocess
import os

class LogService:
    @staticmethod
    def get_logs(ip_filter=None, status_filter="ANY"):
        """
        Fetch Squid access logs filtered by IP and Status.
        Mocked on Windows.
        """
        if os.name == 'nt':
            return "Dev Mode: No real logs on Windows.\n[TIMESTAMP] TCP_TUNNEL 192.168.1.1 google.com\n[TIMESTAMP] TCP_DENIED 192.168.1.2 facebook.com"

        try:
            base_command = "tail -n 500 /var/log/squid/access.log"
            if ip_filter:
                # Sanitize ip_filter to prevent injection (basic check)
                if not all(c.isalnum() or c in '.:' for c in ip_filter):
                     return "Invalid IP Filter"
                base_command += f" | grep {ip_filter}"
            
            if status_filter == "SUCCESS":
                base_command += " | grep TCP_TUNNEL"
            elif status_filter == "DENIED":
                base_command += " | grep TCP_DENIED"

            # Use subprocess securely? grep injection is possible if not careful.
            # Using shell=True with user input is bad practice.
            # Ideally use python filtering or list args.
            # But adhering to original logic but safer:
            
            # Better implementation: read file in python 
            # But file might be huge. tail is efficient.
            # Let's keep subprocess but validate input strictly.
            
            logs = subprocess.check_output(base_command, shell=True, text=True)
            return logs
        except subprocess.CalledProcessError as e:
            return f"Error fetching logs: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"
