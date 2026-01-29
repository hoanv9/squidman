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

### 1. System Requirements (CentOS/RHEL/AlmaLinux)
```bash
# Install Python 3 and Git
sudo dnf install python3 python3-pip git -y
```

### 2. User & Group Setup (For Linux Permission)
Create the `squid-man` group and user to handle permissions securely.
```bash
sudo groupadd squid-man
sudo useradd -g squid-man -m -s /sbin/nologin squid-man
```

### 3. Get the Code (Git Clone)
Download code from your repository (replace URL with your actual repo):
```bash
cd /opt
sudo git clone https://github.com/hoanv9/squid-manager.git
# Or if you already have it, just update:
# cd squid-manager && git pull
cd squid-manager
```

### 4. Install Dependencies
It is highly recommended to use a Python Virtual Environment to isolate dependencies.

**Option A: Quick Setup (System-wide)**
```bash
sudo pip3 install -r requirements.txt
```

**Option B: Virtual Environment (Recommended)**
```bash
# 1. Install virtualenv
sudo dnf install python3-virtualenv -y  # CentOS/RHEL
# apt install python3-venv -y           # Ubuntu/Debian

# 2. Create venv
python3 -m venv venv

# 3. Activate venv
source venv/bin/activate

# 4. Install requirements
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configuration (.env)
You must create a `.env` file since it's not included in Git for security.
```bash
# Copy the example file
cp .env.example .env

# Edit the file to set your Admin Password
nano .env
```
Inside `.env`, verify or change:
```ini
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password  <-- CHANGE THIS
SQUID_CONF_DIR=/etc/squid/conf.d/
SQUID_DOMAINS_DIR=/etc/squid/domains/
DATABASE_URL=sqlite:///squid_manager.db
```

### 6. Deployment: Create Systemd Service
To keep the application running in the background and start on boot, create a systemd service.

**1. Create the service file:**
```bash
sudo nano /etc/systemd/system/squidman.service
```

**2. Paste the following configuration:**
*(Adjust paths if you installed somewhere other than `/opt/squid-manager`)*

```ini
[Unit]
Description=Squid Manager Web Service
After=network.target

[Service]
# Run as root to allow managing Squid services and files
User=root
Group=root

# Working Directory
WorkingDirectory=/opt/squid-manager

# Python Path (Point to your venv python if using one, or /usr/bin/python3)
ExecStart=/opt/squid-manager/venv/bin/python run.py

# Restart policy
Restart=always
RestartSec=5

# Logging
StandardOutput=append:/var/log/squidman.log
StandardError=append:/var/log/squidman.err

[Install]
WantedBy=multi-user.target
```

**3. Enable and Start the Service:**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service on boot
sudo systemctl enable squidman

# Start service now
sudo systemctl start squidman

# Check status
sudo systemctl status squidman
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
