import sys
import subprocess

# requests 없으면 자동 설치
try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

import socket
import os
import uuid
import pathlib
import platform
import threading
from datetime import datetime

# ──────────────────────────────────────────────────────────────
# 설정
# ──────────────────────────────────────────────────────────────
SERVER_URL  = "https://script.google.com/macros/s/AKfycby_fdRaY0Br2Znjp-V3PHNLf0xYcmaTf5KIIm7lb8tDwciE6oOw200GjTVBa-55SPgp/exec"
TIMEOUT     = 10
AUTO_REPORT = True
# ──────────────────────────────────────────────────────────────

_BASE    = pathlib.Path(__file__).parent
_ID_FILE = _BASE / ".client_id"

def _get_client_id() -> str:
    if _ID_FILE.exists():
        return _ID_FILE.read_text().strip()
    cid = str(uuid.uuid4())
    _ID_FILE.write_text(cid)
    return cid


def _get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "unknown"


def _collect_info() -> dict:
    return {
        "client_id": _get_client_id(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "host":      socket.gethostname(),
        "user":      os.environ.get("USERNAME") or os.environ.get("USER") or "unknown",
        "ip":        _get_local_ip(),
        "os":        f"{platform.system()} {platform.release()} ({platform.machine()})",
    }


def _send(payload: dict):
    try:
        res  = requests.post(SERVER_URL, json=payload, timeout=TIMEOUT)
        data = res.json()
        if data.get("status") == "ok":
            print("[OK] 전송 성공")
        else:
            print(f"[FAIL] 서버 오류: {data}")
    except Exception as e:
        print(f"[FAIL] 전송 실패: {e}")


def report(blocking: bool = False):
    payload = _collect_info()
    if blocking:
        _send(payload)
    else:
        t = threading.Thread(target=_send, args=(payload,), daemon=True)
        t.start()


if AUTO_REPORT:
    report(blocking=True)
import sys
import subprocess

# requests 없으면 자동 설치
try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

import socket
import os
import uuid
import pathlib
import platform
import threading
from datetime import datetime

# ──────────────────────────────────────────────────────────────
# 설정
# ──────────────────────────────────────────────────────────────
SERVER_URL  = "https://script.google.com/macros/s/AKfycby_fdRaY0Br2Znjp-V3PHNLf0xYcmaTf5KIIm7lb8tDwciE6oOw200GjTVBa-55SPgp/exec"
TIMEOUT     = 10
AUTO_REPORT = True
# ──────────────────────────────────────────────────────────────

_BASE    = pathlib.Path(__file__).parent
_ID_FILE = _BASE / ".client_id"

def _get_client_id() -> str:
    if _ID_FILE.exists():
        return _ID_FILE.read_text().strip()
    cid = str(uuid.uuid4())
    _ID_FILE.write_text(cid)
    return cid


def _get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "unknown"


def _collect_info() -> dict:
    return {
        "client_id": _get_client_id(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "host":      socket.gethostname(),
        "user":      os.environ.get("USERNAME") or os.environ.get("USER") or "unknown",
        "ip":        _get_local_ip(),
        "os":        f"{platform.system()} {platform.release()} ({platform.machine()})",
    }


def _send(payload: dict):
    try:
        res  = requests.post(SERVER_URL, json=payload, timeout=TIMEOUT)
        data = res.json()
        if data.get("status") == "ok":
            print("[OK] 전송 성공")
        else:
            print(f"[FAIL] 서버 오류: {data}")
    except Exception as e:
        print(f"[FAIL] 전송 실패: {e}")


def report(blocking: bool = False):
    payload = _collect_info()
    if blocking:
        _send(payload)
    else:
        t = threading.Thread(target=_send, args=(payload,), daemon=True)
        t.start()


if AUTO_REPORT:
    report(blocking=True)
