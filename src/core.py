from fastapi import Depends, APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import date, timedelta
from typing import List, Dict, Any
from zk import ZK
from datetime import datetime
import logging
logging.basicConfig(level=logging.DEBUG)

router = APIRouter()


def connect(
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key")
):
    zk = ZK(ip, port=port, timeout=5, password=comm_key,
            force_udp=False, ommit_ping=False)  # Updated values
    conn = zk.connect()
    try:
        yield conn
    finally:
        conn.disconnect()


class UserCreate(BaseModel):
    uid: int
    name: str
    privilege: int = 0
    password: str = ""
    group_id: int = 1
    user_id: str


@router.get("/users")
def api_get_users(
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key")
):
    try:
        zk = ZK(ip, port=port, timeout=5, password=comm_key,
                force_udp=False, ommit_ping=False)  # Updated values
        conn = zk.connect()
        try:
            users = conn.get_users()
            return [{"uid": u.uid, "name": u.name, "privilege": u.privilege, "user_id": u.user_id} for u in users]
        finally:
            conn.disconnect()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users")
def api_insert_user(
    user: UserCreate,
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key")
):
    try:
        zk = ZK(ip, port=port, timeout=5, password=comm_key,
                force_udp=False, ommit_ping=False)
        conn = zk.connect()
        try:
            uid = user.uid
            # prefer explicit user_id if provided, otherwise fall back to uid
            user_id = user.user_id if user.user_id else str(uid)
            # set_user expects group_id as string for some firmwares, and int for others;
            # sending it as string is safe (the method handles conversion where needed)
            group_id = str(user.group_id) if user.group_id is not None else ""
            card = 0

            result = conn.set_user(
                uid=uid,
                name=user.name,
                privilege=user.privilege,
                password=user.password,
                group_id=group_id,
                user_id=user_id,
                card=card
            )
            return {"status": "success" if result else "failed"}
        finally:
            conn.disconnect()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/users/{uid}")
def api_delete_user(
    uid: int,
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key")
):
    try:
        zk = ZK(ip, port=port, timeout=5, password=comm_key,
                force_udp=False, ommit_ping=False)  # Updated values
        conn = zk.connect()
        try:
            conn.delete_user(uid)
            return {"status": "deleted"}
        finally:
            conn.disconnect()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/attendance")
def api_get_all_attendance(
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key")
):
    try:
        zk = ZK(ip, port=port, timeout=5, password=comm_key,
                force_udp=False, ommit_ping=False)  # Updated values
        conn = zk.connect()
        try:
            attendance = conn.get_attendance()
            result = []
            for att in attendance:
                result.append({
                    "user_id": att.user_id,
                    "timestamp": att.timestamp,
                    "status": att.status
                })
            return result
        finally:
            conn.disconnect()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/device/memory/size")
def get_memory_size(
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key")
):
    try:
        zk = ZK(ip, port=port, timeout=5, password=comm_key,
                force_udp=False, ommit_ping=False)  # Updated values
        conn = zk.connect()
        try:
            memory_size = conn.read_sizes()
            return {"memory_size": memory_size}
        finally:
            conn.disconnect()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/device/info")
def api_get_device_info(
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key")
):
    try:
        zk = ZK(ip, port=port, timeout=5, password=comm_key,
                force_udp=False, ommit_ping=False)  # Updated values
        conn = zk.connect()
        try:
            info = {}
            # list of (key, method_name) to call on the connection
            methods = [
                ("device_name", "get_device_name"),
                ("firmware_version", "get_firmware_version"),
                ("serial_number", "get_serialnumber"),
                ("platform", "get_platform"),
                ("mac", "get_mac"),
                ("face_version", "get_face_version"),
                ("fp_version", "get_fp_version"),
            ]

            for key, method_name in methods:
                fn = getattr(conn, method_name, None)
                if callable(fn):
                    try:
                        info[key] = fn()
                    except Exception:
                        info[key] = None
                else:
                    info[key] = None
            return info
        finally:
            conn.disconnect()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/device/restart")
def restart_device(
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key")
):
    """
    Restart the device.
    """
    try:
        zk = ZK(ip, port=port, timeout=5, password=comm_key,
                force_udp=False, ommit_ping=False)
        conn = zk.connect()
        try:
            result = conn.restart()
            return {"status": "success" if result else "failed"}
        finally:
            conn.disconnect()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/device/time")
def get_device_time(
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key")
):
    """
    Get the current time of the device.
    """
    try:
        zk = ZK(ip, port=port, timeout=5, password=comm_key,
                force_udp=False, ommit_ping=False)
        conn = zk.connect()
        try:
            device_time = conn.get_time()
            return {"device_time": device_time}
        finally:
            conn.disconnect()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/device/time")
def set_device_time(
    timestamp: datetime,
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key")
):
    """
    Set the current time of the device.
    """
    try:
        zk = ZK(ip, port=port, timeout=5, password=comm_key,
                force_udp=False, ommit_ping=False)
        conn = zk.connect()
        try:
            result = conn.set_time(timestamp)
            return {"status": "success" if result else "failed"}
        finally:
            conn.disconnect()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/device/network")
def get_network_params(
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key")
):
    """
    Get the network parameters of the device.
    """
    try:
        zk = ZK(ip, port=port, timeout=5, password=comm_key,
                force_udp=False, ommit_ping=False)
        conn = zk.connect()
        try:
            network_params = conn.get_network_params()
            return network_params
        finally:
            conn.disconnect()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/device/memory")
def get_memory_usage(
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key")
):
    """
    Get memory usage details of the device.
    """
    try:
        zk = ZK(ip, port=port, timeout=5, password=comm_key,
                force_udp=False, ommit_ping=False)
        conn = zk.connect()
        try:
            conn.read_sizes()
            return {
                "users": conn.users,
                "fingers": conn.fingers,
                "records": conn.records,
                "faces": conn.faces,
                "users_capacity": conn.users_cap,
                "fingers_capacity": conn.fingers_cap,
                "records_capacity": conn.rec_cap,
                "faces_capacity": conn.faces_cap,
            }
        finally:
            conn.disconnect()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/device/unlock")
def unlock_door(
    time: int = Query(3, description="Unlock duration in seconds"),
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key")
):
    """
    Unlock the door for a specified duration.
    """
    try:
        zk = ZK(ip, port=port, timeout=5, password=comm_key,
                force_udp=False, ommit_ping=False)
        conn = zk.connect()
        try:
            result = conn.unlock(time)
            return {"status": "success" if result else "failed"}
        finally:
            conn.disconnect()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/device/test-voice")
def api_test_voice(
    voice_id: int = Query(1, description="Voice index/ID to play"),
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key")
):
    """
    Play a test voice on the device.
    Example: /device/test-voice?voice_id=0
    """
    try:
        zk = ZK(ip, port=port, timeout=5, password=comm_key,
                force_udp=False, ommit_ping=False)
        conn = zk.connect()
        try:
            result = conn.test_voice(voice_id)
            return {"status": "success" if result else "failed", "voice_id": voice_id}
        finally:
            conn.disconnect()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
