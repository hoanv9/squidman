import logging

# Cấu hình logging
logging.basicConfig(
    filename='logs/auto_tasks.log',  # Đường dẫn file log
    level=logging.INFO,             # Mức độ log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s'  # Định dạng log
)

def auto_generate_and_apply_config(app):
    """
    Hàm tự động Generate Config, Apply Config, và Reload Squid.
    Được gọi bởi APScheduler vào thời gian cấu hình.
    """
    from app.services.configuration_service import ConfigurationService

    # Sử dụng Flask application context
    with app.app_context():
        # Tạo request context giả lập
        with app.test_request_context():
            try:
                # Generate Config
                logging.info("Starting to generate configuration files...")
                success, res = ConfigurationService.generate_config()
                if not success:
                    logging.error(f"Generate failed: {res}")
                    return
                logging.info("Configuration files generated.")

                # Apply Config
                logging.info("Starting to apply configuration...")
                success, res = ConfigurationService.apply_config()
                if not success:
                    logging.error(f"Apply failed: {res}")
                    return
                logging.info("Configuration applied.")

                # Reload Squid
                logging.info("Starting to reload Squid...")
                success, res = ConfigurationService.reload_squid()
                if not success:
                    logging.error(f"Reload failed: {res}")
                else:
                    logging.info("Squid reloaded successfully.")

            except Exception as e:
                logging.error(f"Error during auto configuration: {e}")