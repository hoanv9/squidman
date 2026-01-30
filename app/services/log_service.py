import subprocess
import os

from flask import current_app

class LogService:
    @staticmethod
    def get_logs(ip_filter=None, status_filter="ANY"):
        """
        Fetch Squid access logs filtered by IP and Status.
        Mocked on Windows.
        """
        if os.name == 'nt':
            return "Dev Mode: No real logs on Windows.\n[TIMESTAMP] TCP_TUNNEL 192.168.1.1 google.com\n[TIMESTAMP] TCP_DENIED 192.168.1.2 facebook.com"

        log_file_path = current_app.config.get('SQUID_ACCESS_LOG', '/var/log/squid/access.log')

        if not os.path.exists(log_file_path):
            return f"Log file not found at: {log_file_path}"
            
        try:
            # Use 'sudo' if necessary, but requires sudoers config. 
            # Assuming the app user has read access log file.
            base_command = f"tail -n 500 {log_file_path}"
            
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
            
            logs = subprocess.check_output(base_command, shell=True, text=True)
            return logs
        except subprocess.CalledProcessError as e:
            # grep returns exit code 1 if no matches found, which check_output treats as error
            if e.returncode == 1:
                return "No matching logs found."
            return f"Error fetching logs: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"
