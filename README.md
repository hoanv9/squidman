# Squid_Manager

## Overview
**Squid_Manager** is a Flask-based web application designed for managing Squid Proxy configurations. It provides a user-friendly interface for managing clients, configuring access times, defining allowed domains, and applying configurations to the Squid Proxy server.

## Features
- **Web Interface**: Accessible externally at `0.0.0.0:5000` with a clean, modern, and responsive design.
- **Client Configuration Management**: Supports CRUD operations for clients, including IP address, allowed domains, and expiration dates.
- **Automatic Configuration Generation**: Generates Squid configuration files for access times and allowed domains.
- **Expiration Control**: Manages client access based on expiration dates.
- **Input Validation and Sanitization**: Ensures secure and valid input for IP addresses, URLs, and expiration dates.

## Application Structure
- **Dashboard**: Displays client statistics and a list of clients expiring in the next 7 days.
- **Manage Clients**: Allows users to add, edit, and delete client configurations.
- **Apply Configuration**: Enables the application and backup of Squid configurations.

## Installation
sudo dnf install python3-pip  # hoặc dùng yum nếu dnf không có
sudo useradd -g squid-man -m -s /sbin/nologin squid-man
sudo groupadd squid-man
sudo useradd -g squid-man -m -s /sbin/nologin squid-man
sudo usermod -aG squid-man squid-man


1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd Squid_Manager
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
To run the application, execute:
```
python run.py
```
Visit `http://0.0.0.0:5000` in your web browser to access the application.

## Environment Variables
- `SQUID_CONF_DIR`: Path to Squid configuration directory (default: `/etc/squid/conf.d/`).
- `SQUID_DOMAINS_DIR`: Path to Squid domains directory (default: `/etc/squid/domains/`).
- `OUTPUT_DIR`: Path to output directory for generated configurations (default: `output/`).

## Logging
Logs are stored in the `logs/squid_manager.log` file. Ensure that the application has the necessary permissions to write to this file.

## Testing
Unit tests are located in the `tests` directory. To run the tests, use:
```
pytest
```

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.# squidman
