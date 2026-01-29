from ipaddress import ip_address, AddressValueError
import validators
from datetime import datetime
import os
import subprocess

def validate_ip(ip):
    try:
        ip_address(ip)
        return True
    except AddressValueError:
        return False

def validate_url(url):
    return validators.url(url)

def validate_expiration_date(expiration_date):
    try:
        date = datetime.strptime(expiration_date, '%Y-%m-%d')
        return date > datetime.now()
    except ValueError:
        return False

def validate_squid_configs(config_dir='output/'):
    """
    Validate the generated Squid configuration files.

    Args:
        config_dir (str): The directory containing the Squid configuration files to validate.

    Returns:
        bool: True if all configuration files are valid, False otherwise.
    """
    for file_name in os.listdir(config_dir):
        config_path = os.path.join(config_dir, file_name)
        try:
            # Use the squid -k parse command to validate the configuration file
            result = subprocess.run(
                ['squid', '-k', 'parse', '-f', config_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode != 0:
                print(f"Validation failed for {config_path}: {result.stderr}")
                return False
        except FileNotFoundError:
            print("Squid is not installed or not in the system PATH.")
            return False
    return True