
import os
import shutil
import logging
import time
from datetime import datetime
from app.services.configuration_service import ConfigurationService
from flask import current_app

class BackupService:
    @staticmethod
    def get_backup_dir():
        """Lấy đường dẫn thư mục backup database."""
        # Sử dụng db/backups cho database backups
        return os.path.join(os.getcwd(), 'db', 'backups')
    
    @staticmethod
    def get_db_path():
        """
        Lấy đường dẫn database hiện tại.
        Ưu tiên đường dẫn từ Config. Nếu file đó không tồn tại, kiểm tra fallback 'db/squid_manager.db'.
        """
        try:
            from flask import current_app
            uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
            
            # Default known location
            fallback_path = os.path.join(os.getcwd(), 'db', 'squid_manager.db')
            
            if uri.startswith('sqlite:///'):
                config_path = uri.replace('sqlite:///', '')
                if not os.path.isabs(config_path):
                    config_path = os.path.abspath(config_path)
                
                # 1. Nếu file config tồn tại -> Dùng nó
                if os.path.exists(config_path):
                    logging.debug(f"Resolved DB Path (Config): {config_path}")
                    return config_path
                
                # 2. Nếu không, kiểm tra trong folder app/ (thường gặp khi chạy package)
                app_db_path = os.path.join(os.getcwd(), 'app', 'squid_manager.db')
                if os.path.exists(app_db_path):
                    logging.debug(f"Resolved DB Path (App dir): {app_db_path}")
                    return app_db_path
                
                # 3. Kiểm tra fallback location db/
                logging.warning(f"DB at Config Path {config_path} not found. Checking fallback: {fallback_path}")
                if os.path.exists(fallback_path):
                    return fallback_path
                
                # 4. Nếu không thấy đâu cả, trả về config path
                return config_path
                
            logging.debug(f"Resolved DB Path: {fallback_path}")
            return fallback_path
        except Exception as e:
            logging.error(f"Error resolving DB path: {e}")
            return os.path.join(os.getcwd(), 'db', 'squid_manager.db')

    # ... (other methods)

    @staticmethod
    def restore_backup(filename):
        """Restore database từ backup."""
        try:
            # 1. Validate
            if '..' in filename or not filename.endswith('.db'):
                return False, "Invalid filename"
                
            backup_dir = BackupService.get_backup_dir()
            backup_path = os.path.join(backup_dir, filename)
            db_path = BackupService.get_db_path()
            
            if not os.path.exists(backup_path):
                return False, "Backup file not found"

            logging.info(f"Starting restore. Source: {backup_path} -> Target: {db_path}")

            # 2. Safety Backup
            s_success, s_msg = BackupService.create_database_backup('auto_restore_safety')
            if not s_success:
                return False, f"Failed to create safety backup: {s_msg}"

            # 3. Close Connections
            from app import db
            try:
                db.session.remove()
                if hasattr(db.engine, 'dispose'):
                    db.engine.dispose()
            except Exception as e:
                logging.warning(f"Error closing DB connections: {e}")
                
            time.sleep(1) # Wait for file lock release

            # 4. Restore
            try:
                # Check sizes for debug
                if os.path.exists(db_path):
                    current_size = os.path.getsize(db_path)
                    backup_size = os.path.getsize(backup_path)
                    logging.info(f"Overwriting DB ({current_size} bytes) with Backup ({backup_size} bytes)")
                
                shutil.copy2(backup_path, db_path)
                logging.info(f"Database restored successfully from {filename}")
                
                return True, "Database restored successfully. Please refresh the page."
            except PermissionError:
                return False, "Permission denied. Database file is locked by another process."
                
        except Exception as e:
            logging.error(f"Restore failed: {e}")
            return False, f"Restore failed: {e}"
    
    @staticmethod
    def create_database_backup(prefix='manual'):
        """
        Tạo backup database.
        Args:
            prefix: 'manual' hoặc 'auto'
        Returns:
            tuple(bool, str): (Success, Message/Filename)
        """
        try:
            backup_dir = BackupService.get_backup_dir()
            db_path = BackupService.get_db_path()
            
            if not os.path.exists(db_path):
                return False, f"Database not found at {db_path}"

            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{prefix}_{timestamp}.db"
            backup_path = os.path.join(backup_dir, filename)
            
            shutil.copy2(db_path, backup_path)
            logging.info(f"Database backup created: {backup_path}")
            
            # Xóa bớt auto backups cũ nếu > 10
            if prefix == 'auto':
                BackupService._cleanup_old_backups(backup_dir, 'auto_')
                
            if prefix == 'auto_restore_safety':
                BackupService._cleanup_old_backups(backup_dir, 'auto_restore_safety_')
                
            return True, filename
        except Exception as e:
            logging.error(f"Backup creation failed: {e}")
            return False, str(e)

    @staticmethod
    def create_manual_backup():
        return BackupService.create_database_backup('manual')

    @staticmethod
    def create_auto_backup():
        return BackupService.create_database_backup('auto')

    @staticmethod
    def list_backups():
        """Liệt kê tất cả backup files."""
        try:
            backup_dir = BackupService.get_backup_dir()
            if not os.path.exists(backup_dir):
                return []
                
            backups = []
            for filename in os.listdir(backup_dir):
                if filename.endswith('.db'):
                    file_path = os.path.join(backup_dir, filename)
                    stats = os.stat(file_path)
                    
                    # Determine type
                    b_type = 'manual'
                    if filename.startswith('auto_restore_safety_'):
                        b_type = 'safety'
                    elif filename.startswith('auto_'):
                        b_type = 'auto'
                        
                    backups.append({
                        'filename': filename,
                        'size': stats.st_size,
                        'created': datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                        'timestamp': stats.st_ctime, # For sorting
                        'type': b_type
                    })
            
            # Sort by created desc
            backups.sort(key=lambda x: x['timestamp'], reverse=True)
            return backups
        except Exception as e:
            logging.error(f"Error listing backups: {e}")
            return []

    @staticmethod
    def delete_backup(filename):
        """Xóa backup file."""
        try:
            # Basic validation to prevent path traversal
            if '..' in filename or '/' in filename or '\\' in filename:
                return False, "Invalid filename"
                
            backup_dir = BackupService.get_backup_dir()
            file_path = os.path.join(backup_dir, filename)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                return True, "Backup deleted successfully"
            return False, "File not found"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def restore_backup(filename):
        """Restore database từ backup."""
        try:
            # 1. Validate
            if '..' in filename or not filename.endswith('.db'):
                return False, "Invalid filename"
                
            backup_dir = BackupService.get_backup_dir()
            backup_path = os.path.join(backup_dir, filename)
            db_path = BackupService.get_db_path()
            
            if not os.path.exists(backup_path):
                return False, "Backup file not found"

            # 2. Safety Backup
            s_success, s_msg = BackupService.create_database_backup('auto_restore_safety')
            if not s_success:
                return False, f"Failed to create safety backup: {s_msg}"

            # 3. Close Connections
            # Trong ngữ cảnh Flask/SQLAlchemy, chúng ta không dễ dàng "đóng" hết connection pool global một cách thủ công 
            # mà không access vào object `db`.
            # Tuy nhiên, trên SQLite windows, file có thể bị lock.
            # Ta sẽ cố gắng copy đè. Nếu fail do lock thì cần user stop app.
            # Với mô hình hiện tại, ta implement simple copy.
            
            # Import db để close session
            from app import db
            db.session.remove()
            if hasattr(db.engine, 'dispose'):
                db.engine.dispose()
                
            # Wait a bit
            time.sleep(0.5)

            # 4. Restore
            shutil.copy2(backup_path, db_path)
            logging.info(f"Database restored from {filename}")
            
            return True, "Database restored successfully. Please refresh the page."
        except Exception as e:
            logging.error(f"Restore failed: {e}")
            return False, f"Restore failed: {e}. If file is locked, try stopping the app first."

    @staticmethod
    def _cleanup_old_backups(directory, prefix, keep=10):
        """Giữ lại N backup mới nhất, xóa cũ hơn."""
        try:
            files = []
            for f in os.listdir(directory):
                if f.startswith(prefix) and f.endswith('.db'):
                    full_path = os.path.join(directory, f)
                    files.append((full_path, os.path.getctime(full_path)))
            
            # Sort by time desc
            files.sort(key=lambda x: x[1], reverse=True)
            
            # Delete old
            if len(files) > keep:
                for f_path, _ in files[keep:]:
                    os.remove(f_path)
                    logging.info(f"Auto-cleanup: deleted {f_path}")
        except Exception as e:
            logging.warning(f"Backup cleanup warning: {e}")
