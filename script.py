import sys
import subprocess

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


# ── 설정 ──────────────────────────────────────────────
SERVER_URL  = "https://script.google.com/macros/s/AKfycby_fdRaY0Br2Znjp-V3PHNLf0xYcmaTf5KIIm7lb8tDwciE6oOw200GjTVBa-55SPgp/exec"
TIMEOUT     = 10
AUTO_REPORT = True
# ──────────────────────────────────────────────────────


_BASE    = pathlib.Path(__file__).parent
_ID_FILE = _BASE / ".client_id"


def _get_id() -> str:
    if _ID_FILE.exists():
        return _ID_FILE.read_text().strip()
    cid = str(uuid.uuid4())
    _ID_FILE.write_text(cid)
    return cid


def _get_add() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        add = s.getsockname()[0]
        s.close()
        return add
    except Exception:
        return "unknown"


def _get_mac_serial() -> str:
    try:
        result = subprocess.run(
            ["system_profiler", "SPHardwareDataType"],
            capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.split("\n"):
            if "Serial Number" in line:
                return line.split(":")[-1].strip()
    except Exception:
        pass
    return "unknown"


def _get_mac_fullname(username: str) -> str:
    try:
        result = subprocess.run(
            ["dscl", ".", "-read", f"/Users/{username}", "RealName"],
            capture_output=True, text=True, timeout=3
        )
        lines = result.stdout.strip().split("\n")
        if len(lines) > 1:
            return lines[1].strip()
    except Exception:
        pass
    return "unknown"


def _get_platform_info() -> dict:
    info = {
        "usr":      os.environ.get("USERNAME") or os.environ.get("USER") or "unknown",
        "domain":   "unknown",
        "serial":   "unknown",
        "fullname": "unknown",
    }

    if platform.system() == "Windows":
        info["domain"] = os.environ.get("USERDOMAIN") or "unknown"

    elif platform.system() == "Darwin":
        info["fullname"] = _get_mac_fullname(info["usr"])
        info["serial"]   = _get_mac_serial()  # Jamf 자산 대장과 수동 대조용

    return info


def _collect_info() -> dict:
    platform_info = _get_platform_info()
    return {
        "id":        _get_id(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "hst":       socket.gethostname(),
        "add":       _get_add(),
        "ops":       f"{platform.system()} {platform.release()} ({platform.machine()})",
        **platform_info,
    }


def _send(payload: dict):
    try:
        res  = requests.post(SERVER_URL, json=payload, timeout=TIMEOUT)
        data = res.json()
        if data.get("status") == "duplicate":
            return
    except Exception:
        pass


def _show_training_message():
    msg = (
        "[보안 훈련 알림]\n\n"
        "방금 실행하신 파일은 사내 모의 훈련용입니다.\n"
        "출처 불명의 파일은 절대 실행하지 마세요.\n\n"
        "문의: 정보보호팀"
    )
    if platform.system() == "Windows":
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, msg, "정보보호팀 보안 훈련 알림", 0x40)
            return
        except Exception:
            pass
    elif platform.system() == "Darwin":
        try:
            subprocess.run(
                ["osascript", "-e", f'display dialog "{msg}" with title "정보보호팀 보안 훈련 알림" buttons {{"확인"}} default button "확인"'],
                timeout=60
            )
            return
        except Exception:
            pass
    # fallback
    print(msg)


def report(blocking: bool = False):
    payload = _collect_info()
    if blocking:
        _send(payload)
    else:
        t = threading.Thread(target=_send, args=(payload,), daemon=True)
        t.start()


if AUTO_REPORT:
    report(blocking=True)
    _show_training_message()
