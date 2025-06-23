# 📚 Device API Documentation

🚀 Overview
The Device API project provides a RESTful interface for connecting to ZKTeco-compatible biometric devices, retrieving user data, and accessing attendance logs.
It is designed to simplify device integration for attendance and access control systems.litate interaction with the device through a RESTful API.

## 🗂️ Project Structure

```
device-api
├── src
│   ├── core.py          # Core functionality for device connectivity
│   ├── api
│   │   ├── __init__.py  # Initializes the API module
│   │   └── endpoints.py  # Defines API endpoints for user data and attendance logs
│   ├── main.py          # Entry point for the application
│   └── utils
│       └── device.py    # Utility functions related to device operations
├── requirements.txt      # Lists project dependencies
└── README.md             # Project documentation
```

## 🛠️ Prerequisites

🐍 Python 3.8+
Download: python.org/downloads

💻 pip (Python package manager)
Usually included with Python.

🪟 Windows Users:
Some libraries (like uvicorn) require Microsoft C++ Build Tools.
👉 Download Build Tools
`npm install --global windows-build-tools`

Or install via terminal:

## Setup Instructions

1. Clone the repository:

   ```
   git clone <repository-url>
   cd device-api
   ```

2. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Configure the device settings in `src/core.py`:
   - Update `device_ip`, `device_port`, and `comm_key` with your device's configuration.

## Usage

1. Start the application:

   ```
   python src/main.py
   ```

2. Access the API endpoints:
   - Retrieve user data: `GET /api/users`
   - Retrieve attendance logs: `GET /api/attendance`

## ⚙️ Configuration

Device connection settings are provided as query parameters in each API request:

ip: Device IP address
port: Device port (default: 4370)
comm_key: Communication key (default: 0 or as set on your device)
Example:
`GET /users?ip=192.168.1.201&port=4370&comm_key=454545`
▶️ Running the Application
🧪 Development (with auto-reload)
`uvicorn src.main:app --reload --host 0.0.0.0 --port 8000`
--reload: Auto-reloads on code changes.
--host 0.0.0.0: Accessible from your network.
--port 8000: Change as needed (e.g., --port 8080).

## 🏁 Production

For production, use a process manager like systemd, Supervisor, or pm2 to keep your app running.
Example: systemd service (Linux)
Create /etc/systemd/system/device-api.service:

`
[Unit]
Description=Device API FastAPI Service
After=network.target

[Service]
User=yourusername
WorkingDirectory=/path/to/device-api
ExecStart=/usr/bin/env uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target `
Enable and start

`sudo systemctl daemon-reload
sudo systemctl enable device-api
sudo systemctl start device-api `

## 🌐 Accessing the API

Swagger UI:
http://localhost:8000/users
(Replace localhost with your server IP if remote)

Example Endpoints:

Get users:
GET /users?ip=192.168.1.201&port=4370&comm_key=454545
Get attendance:
GET /attendance/1?ip=192.168.1.201&port=4370&comm_key=454545&day=2024-06-01

## 🛡️Firewall & Port

Open your chosen port (e.g., 8000) in your firewall
`sudo ufw allow 8000`
Access from other devices using:
http://<your-server-ip>:8000/docs

## 🧩 Contributing

Contributions are welcome!
Please submit a pull request or open an issue for any enhancements or bug fixes.

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for more details.
