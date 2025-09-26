# 📚 Documentation

## 🚀 Overview

The Device API project provides a RESTful interface for connecting ZKTeco-compatible biometric devices to your applications—such as MIS, LMS, HR systems, and more—for retrieving user data and accessing attendance logs.

No matter which programming language you use! With this package, you can interact with your attendance machine via API endpoints—whether you're using PHP (Laravel), Python, Ruby, Next.js, NestJS, React, or others.

It is designed to simplify device integration for attendance and access control systems and to facilitate seamless interaction with the device through a RESTful API.
But after using this as api in server I realized that it could be a good and easy way to use the python code inside the php code. The key is to install the python in server and use php to run the python code in terminal to get data from attendance machine.

## 🗂️ Project Structure

```
device-api
├── src
│   ├── core.py          
│   ├── api
│   │   ├── __init__.py  
│   │   └── endpoints.py 
│   ├── main.py          
│   └── utils
│       └── device.py    
├── requirements.txt     
└── README.md          
```

## 🛠️ Prerequisites

- **Python 3.8+**  
   [Download Python](https://www.python.org/downloads/)

- **pip (Python package manager)**  
   Usually included with Python.

- **Windows Users:**  
   Some libraries (like `uvicorn`) require Microsoft C++ Build Tools.  
   Download Build Tools:
  ```sh
  npm install --global windows-build-tools
  ```
  Or install via terminal.

## ⚙️ Setup Instructions

1. **Clone the repository:**

   ```sh
   git clone <repository-url>
   cd device-api
   ```

2. **Install the required dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

3. **Configure the device settings in `src/core.py`:**
   - Update `device_ip`, `device_port`, and `comm_key` with your device's configuration.

## 🚦 Usage

1. **Start the application:**

   ```sh
   python src/main.py
   ```

2. **Access the API endpoints:**
   - Retrieve user data: `GET /api/users` it will retrive all users of zkteco device.
   - Retrieve attendance logs: `GET /api/attendance`

## ⚙️ Configuration

Device connection settings are provided as query parameters in each API request:

- `ip`: Device IP address
- `port`: Device port (default: 4370)
- `comm_key`: Communication key (default: 0 or as set on your device)

**Example:**

```
GET /users?ip=192.168.1.201&port=4370&comm_key=454545
```

### ▶️ Running the Application

**Development (with auto-reload):**

```sh
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

- `--reload`: Auto-reloads on code changes.
- `--host 0.0.0.0`: Accessible from your network.
- `--port 8000`: Change as needed (e.g., `--port 8080`).

## 🏁 Production

For production, use a process manager like `systemd`, `Supervisor`, or `pm2` to keep your app running.

**Example: systemd service (Linux)**  
Create `/etc/systemd/system/device-api.service`:

```ini
[Unit]
Description=Device API FastAPI Service
After=network.target

[Service]
User=yourusername
WorkingDirectory=/path/to/device-api
ExecStart=/usr/bin/env uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```sh
sudo systemctl daemon-reload
sudo systemctl enable device-api
sudo systemctl start device-api
```

## 🌐 Accessing the API

- **Swagger UI:**  
   [http://localhost:8000/docs](http://localhost:8000/docs)  
   (Replace `localhost` with your server IP if remote)

**Example Endpoints:**

- Get users:
  ```
  GET /users?ip=192.168.1.201&port=4370&comm_key=454545
  ```
- Get attendance:
  ```
  GET /attendance/1?ip=192.168.1.201&port=4370&comm_key=454545&day=2024-06-01
  ```

## 🛡️ Firewall & Port

Open your chosen port (e.g., 8000) in your firewall:

```sh
sudo ufw allow 8000
```

Access from other devices using:  
`http://<your-server-ip>:8000/docs`

## 🧩 Contributing

Contributions are welcome!  
Please submit a pull request or open an issue for any enhancements or bug fixes.

## ⭐️ Support

If you find this project helpful, please consider giving it a **star** on [GitHub](https://github.com/najibullahjafari/zkteco_device_python_connect)!  
Your support helps others discover this project and motivates further development. Thank you! 🌟

## 📄 License

This project is licensed under the [MIT License](../LICENSE). See the LICENSE file for more details.
