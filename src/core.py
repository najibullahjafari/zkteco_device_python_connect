from fastapi import Depends, APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import date, timedelta
from typing import List
from zk import ZK
from datetime import datetime

router = APIRouter()


def connect(
    ip: str = Query(None, description="Device IP"),
    port: int = Query(None, description="Device Port"),
    comm_key: int = Query(None, description="Device Communication Key")
):
    # Set default values if not provided
    ip = ip or "192.168.1.201"
    port = port or 4370
    comm_key = comm_key or 454545

    zk = ZK(ip, port=port, timeout=5, password=comm_key,
            force_udp=True, ommit_ping=True)
    conn = zk.connect()
    try:
        yield conn
    finally:
        conn.disconnect()


def get_users(conn):
    return conn.get_users()


def get_attendance(conn):
    return conn.get_attendance()


class UserCreate(BaseModel):
    uid: int
    name: str
    privilege: int = 0
    password: str = ""
    group_id: int = 1
    user_id: str


@router.get("/users")
def api_get_users(conn=Depends(connect)):
    try:
        users = get_users(conn)
        return [{"uid": u.uid, "name": u.name, "privilege": u.privilege, "user_id": u.user_id} for u in users]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users")
def api_insert_user(user: UserCreate, conn=Depends(connect)):
    try:
        result = conn.set_user(
            uid=user.uid,
            name=user.name,
            privilege=user.privilege,
            password=user.password,
            group_id=user.group_id,
            user_id=str(user.uid),
            card=None
        )
        return {"status": "success" if result else "failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/users/{uid}")
def api_delete_user(uid: int, conn=Depends(connect)):
    try:
        conn.delete_user(uid)
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/users/{uid}")
def api_edit_user(uid: int, user: UserCreate, conn=Depends(connect)):
    try:
        result = conn.set_user(
            uid=uid,
            name=user.name,
            privilege=user.privilege,
            password=user.password,
            group_id=user.group_id,
            user_id=str(uid),
            card=None
        )
        return {"status": "success" if result else "failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/attendance/{user_id}")
def api_get_attendance(
    user_id: str,
    day: date = Query(None, description="Date in YYYY-MM-DD format"),
    conn=Depends(connect)
):
    """
    Get attendance logs for a specific user and time.
    Example: /attendance/1?day=2024-06-20
    """
    try:
        result = []
        for att in conn.get_attendance():
            if att.user_id == user_id:
                if day is None or getattr(att.timestamp, "date", lambda: None)() == day:
                    result.append({
                        "user_id": att.user_id,
                        "timestamp": att.timestamp,
                        "status": att.status
                    })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/attendance")
def api_get_all_attendance(conn=Depends(connect)):
    """
    Get all attendance logs for all users.
    """
    try:
        attendance = conn.get_attendance()
        return [
            {
                "user_id": att.user_id,
                "timestamp": att.timestamp,
                "status": att.status
            }
            for att in attendance
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/attendance/today")
def api_get_today_attendance(conn=Depends(connect)):
    """
    Get all attendance logs for today.
    """
    try:
        today = datetime.now().date()
        result = []
        for att in conn.get_attendance():
            if getattr(att.timestamp, "date", lambda: None)() == today:
                result.append({
                    "user_id": att.user_id,
                    "timestamp": att.timestamp,
                    "status": att.status
                })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/attendance/month")
def api_get_past_month_attendance(conn=Depends(connect)):
    """
    Get all attendance logs for the past month.
    """
    try:
        today = datetime.now().date()
        first_day_last_month = (today.replace(
            day=1) - timedelta(days=1)).replace(day=1)
        result = []
        for att in conn.get_attendance():
            att_date = getattr(att.timestamp, "date", lambda: None)()
            if att_date and first_day_last_month <= att_date <= today:
                result.append({
                    "user_id": att.user_id,
                    "timestamp": att.timestamp,
                    "status": att.status
                })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/device/time")
def api_get_device_time(conn=Depends(connect)):
    try:
        device_time = conn.get_time()
        return {"device_time": device_time}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/device/info")
def api_get_device_info(conn=Depends(connect)):
    try:
        info = conn.get_device_info()
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/photo/{user_id}")
def api_get_user_photo(user_id: str, conn=Depends(connect)):
    try:
        photo = conn.get_user_photo(user_id)
        if photo:
            return {"user_id": user_id, "photo": photo}
        else:
            raise HTTPException(status_code=404, detail="Photo not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/device/voice_test")
def api_test_voice(conn=Depends(connect)):
    try:
        conn.test_voice()
        return {"status": "voice test triggered"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/device/users_count")
def api_get_users_count(conn=Depends(connect)):
    try:
        users = conn.get_users()
        return {"users_count": len(users)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/device/logs_count")
def api_get_logs_count(conn=Depends(connect)):
    try:
        logs = conn.get_attendance()
        return {"logs_count": len(logs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class UnlockRequest(BaseModel):
    time: int = 3


@router.post("/device/unlock")
def api_unlock(request: UnlockRequest, conn=Depends(connect)):
    """
    Unlock the door for a specified time (seconds).
    """
    try:
        result = conn.unlock(request.time)
        return {"status": "success" if result else "failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/device/unlock")
def api_unlock_get(time: int = 3, conn=Depends(connect)):
    """
    Unlock the door for a specified time (seconds) via GET request.
    """
    try:
        result = conn.unlock(time)
        return {"status": "success" if result else "failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/device/verify_user")
def api_verify_user(conn=Depends(connect)):
    """
    Start verify finger mode (after capture).
    """
    try:
        result = conn.verify_user()
        return {"status": "success" if result else "failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
