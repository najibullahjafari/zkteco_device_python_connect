from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import date, timedelta, datetime
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
from zk import ZK
import logging
import time

logging.basicConfig(level=logging.DEBUG)

router = APIRouter()


@contextmanager
def zk_conn(ip: str, port: int, comm_key: int, timeout: int = 50, force_udp: bool = False, ommit_ping: bool = False):
    zk = ZK(ip, port=port, timeout=timeout, password=comm_key,
            force_udp=force_udp, ommit_ping=ommit_ping)
    conn = zk.connect()
    try:
        yield conn
    finally:
        conn.disconnect()


class UserUpdate(BaseModel):
    name: Optional[str] = None
    privilege: Optional[int] = None
    password: Optional[str] = None
    group_id: Optional[int] = None
    user_id: Optional[str] = None
    card: Optional[int] = None


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
    comm_key: int = Query(454545, description="Device Communication Key"),
):
    try:
        with zk_conn(ip, port, comm_key) as conn:
            users = conn.get_users()
            return [{"uid": u.uid, "name": u.name, "privilege": u.privilege, "user_id": u.user_id} for u in users]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users")
def api_insert_user(
    user: UserCreate,
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key"),
):
    try:
        with zk_conn(ip, port, comm_key) as conn:
            uid = user.uid
            user_id = user.user_id if user.user_id else str(uid)
            group_id = str(user.group_id) if user.group_id is not None else ""
            card = 0
            conn.set_user(
                uid=uid,
                name=user.name,
                privilege=user.privilege,
                password=user.password,
                group_id=group_id,
                user_id=user_id,
                card=card,
            )
            return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/users/{uid}")
def api_update_user(
    uid: int,
    payload: UserUpdate,
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key"),
):
    """
    Update an existing user by uid using ZK.set_user. If the user does not exist, return 404.
    """
    try:
        with zk_conn(ip, port, comm_key) as conn:
            users = conn.get_users()
            current = next((u for u in users if u.uid == uid), None)
            if not current:
                raise HTTPException(
                    status_code=404, detail=f"user uid {uid} not found")

            name = payload.name if payload.name is not None else current.name
            privilege = payload.privilege if payload.privilege is not None else current.privilege
            password = payload.password if payload.password is not None else current.password
            # group_id handling: base.set_user accepts int/str depending on model; pass str if provided
            group_id_val = payload.group_id if payload.group_id is not None else current.group_id
            user_id = payload.user_id if payload.user_id is not None else current.user_id
            card = payload.card if payload.card is not None else current.card

            # set_user raises on failure; no return value on success
            conn.set_user(
                uid=uid,
                name=name,
                privilege=privilege,
                password=password,
                group_id=str(group_id_val) if group_id_val is not None else "",
                user_id=user_id,
                card=card if card is not None else 0,
            )
            return {
                "status": "success",
                "user": {
                    "uid": uid,
                    "name": name,
                    "privilege": privilege,
                    "user_id": user_id,
                    "group_id": str(group_id_val) if group_id_val is not None else "",
                    "card": card if card is not None else 0,
                },
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/users/by_user_id/{user_id}")
def api_delete_user_by_user_id(
    user_id: str,
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key"),
):
    """
    Delete a user by user_id using ZK.delete_user.
    """
    try:
        with zk_conn(ip, port, comm_key) as conn:
            # delete_user raises on failure
            conn.delete_user(user_id=user_id)
            return {"status": "deleted", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/attendance")
def api_get_all_attendance(
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key"),
):
    try:
        with zk_conn(ip, port, comm_key) as conn:
            attendance = conn.get_attendance()
            # Filter attendance after 2024
            filtered_attendance = [
                a for a in attendance if a.timestamp.year > 2024]
            return [{"user_id": a.user_id, "timestamp": a.timestamp, "status": a.status} for a in filtered_attendance]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/device/memory/size")
def get_memory_size(
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key"),
):
    try:
        with zk_conn(ip, port, comm_key) as conn:
            ok = conn.read_sizes()
            return {"memory_size": ok}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/device/info")
def api_get_device_info(
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key"),
):
    try:
        with zk_conn(ip, port, comm_key) as conn:
            info = {}
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/device/restart")
def restart_device(
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key"),
):
    try:
        with zk_conn(ip, port, comm_key) as conn:
            result = conn.restart()
            return {"status": "success" if result else "failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/device/time")
def get_device_time(
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key"),
):
    try:
        with zk_conn(ip, port, comm_key) as conn:
            device_time = conn.get_time()
            return {"device_time": device_time}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/device/time")
def set_device_time(
    timestamp: datetime,
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key"),
):
    try:
        with zk_conn(ip, port, comm_key) as conn:
            result = conn.set_time(timestamp)
            return {"status": "success" if result else "failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/device/network")
def get_network_params(
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key"),
):
    try:
        with zk_conn(ip, port, comm_key) as conn:
            return conn.get_network_params()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/device/memory")
def get_memory_usage(
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key"),
):
    try:
        with zk_conn(ip, port, comm_key) as conn:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/device/unlock")
def unlock_door(
    time: int = Query(3, description="Unlock duration in seconds"),
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key"),
):
    try:
        with zk_conn(ip, port, comm_key) as conn:
            result = conn.unlock(time)
            return {"status": "success" if result else "failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/device/health")
def device_health(
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key"),
):
    # Try TCP, then UDP
    try:
        with zk_conn(ip, port, comm_key, timeout=50, force_udp=False, ommit_ping=False) as conn:
            ts = conn.get_time()
            return {"ok": True, "transport": "tcp", "time": ts}
    except Exception as e1:
        try:
            with zk_conn(ip, port, comm_key, timeout=50, force_udp=True, ommit_ping=False) as conn:
                ts = conn.get_time()
                return {"ok": True, "transport": "udp", "time": ts}
        except Exception as e2:
            return {"ok": False, "error": str(e1), "udp_error": str(e2)}


@router.post("/device/test-voice")
def api_test_voice(
    voice_id: int = Query(1, description="Voice index/ID to play"),
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key"),
):
    last_err = None
    for force_udp in (False, True):
        try:
            with zk_conn(ip, port, comm_key, timeout=50, force_udp=force_udp, ommit_ping=False) as conn:
                result = conn.test_voice(voice_id)
                return {
                    "status": "success" if result else "failed",
                    "voice_id": voice_id,
                    "transport": "udp" if force_udp else "tcp",
                }
        except Exception as e:
            last_err = str(e)
            continue
    raise HTTPException(
        status_code=500, detail=last_err or "test_voice failed")


@router.get("/device/status")
def device_status(
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key"),
):
    """
    Returns connection status of the device.
    """
    last_err = None
    for force_udp in (False, True):
        try:
            start = time.monotonic()
            zk = ZK(ip, port=port, timeout=50, password=comm_key,
                    force_udp=force_udp, ommit_ping=False)
            conn = zk.connect()
            try:
                elapsed_ms = int((time.monotonic() - start) * 1000)
                return {
                    "connected": True,
                    "transport": "udp" if force_udp else "tcp",
                    "latency_ms": elapsed_ms,
                }
            finally:
                conn.disconnect()
        except Exception as e:
            last_err = str(e)
            continue
    return {"connected": False, "error": last_err or "unable to connect"}


@router.post("/device/toggle")
def toggle_device_status(
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key"),
):
    try:
        with zk_conn(ip, port, comm_key) as conn:
            # Attempt to get current status; assume library supports enable/disable
            try:
                # Check if device is enabled (this may vary by library)
                status = conn.get_device_status()  # Hypothetical method
                if status and status.get('enabled', True):
                    conn.disconnect()
                    return {"status": "disabled"}
                else:
                    conn.connect()
                    return {"status": "enabled"}
            except AttributeError:
                # Fallback if methods don't exist
                raise HTTPException(
                    status_code=501, detail="Toggle not supported by device")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/device/connect")
def connect_device(
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key"),
):
    try:
        zk = ZK(ip, port=port, timeout=50, password=comm_key,
                force_udp=False, ommit_ping=False)
        conn = zk.connect()
        return {"status": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/device/disconnect")
def disconnect_device(
    ip: str = Query("103.227.17.70", description="Device IP"),
    port: int = Query(4370, description="Device Port"),
    comm_key: int = Query(454545, description="Device Communication Key"),
):
    try:
        zk = ZK(ip, port=port, timeout=50, password=comm_key,
                force_udp=False, ommit_ping=False)
        conn = zk.connect()
        result = conn.disconnect()
        return {"status": "disconnected" if result else "failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
