# Device API Documentation

## Overview
The Device API project provides a simple interface for connecting to a device, retrieving user data, and accessing attendance logs. It is designed to facilitate interaction with the device through a RESTful API.

## Project Structure
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

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.