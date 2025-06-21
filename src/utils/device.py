from datetime import datetime

def format_user_data(user):
    return {
        "uid": user.uid,
        "name": user.name,
        "privilege": user.privilege
    }

def format_attendance_data(att):
    return {
        "user_id": att.user_id,
        "timestamp": att.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "status": att.status
    }

def parse_device_response(response):
    # Implement any device-specific response parsing logic here
    return response